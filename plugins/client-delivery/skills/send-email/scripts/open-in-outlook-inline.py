#!/usr/bin/env python3
"""
Open a Markdown email draft in Outlook on macOS with INLINE images.

The sibling script open-in-outlook.py builds the message through AppleScript,
where images can only ride along as plain attachments. Outlook's AppleScript
dictionary has no way to give an attachment a Content-ID, so an image can never
land inside the body that way.

This script takes the other route: it assembles a real MIME message
(multipart/related with cid: references) and hands the .eml to Outlook's
`import eml` command, which files it in the Drafts folder. Images referenced in
the Markdown as ![alt](path) end up embedded in the body, so they render in
Outlook on Windows, Outlook Web and Gmail alike — unlike base64 data: URIs,
which Outlook on Windows refuses to display.

Usage:
    python open-in-outlook-inline.py email-draft.md
    python open-in-outlook-inline.py email-draft.md --max-width 720
    python open-in-outlook-inline.py email-draft.md --eml-only out.eml

Frontmatter is the same as open-in-outlook.py (to, cc, subject, from,
signature, attachments). Images come from the body, not from `attachments:` —
anything listed there is attached as a regular file, as before.
"""
from __future__ import annotations

import argparse
import importlib.util
import mimetypes
import os
import re
import subprocess
import sys
from email.message import EmailMessage
from email.utils import formatdate, make_msgid

# Reuse the Markdown/frontmatter/signature machinery from the sibling script.
_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "open_in_outlook", os.path.join(_HERE, "open-in-outlook.py")
)
base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)

if not hasattr(base, "parse_recipients"):
    # Older sibling versions only parsed a single recipient.
    def _parse_recipients(raw: str) -> list[tuple[str, str]]:
        out = []
        for kus in re.split(r"[;\n]", raw or ""):
            kus = kus.strip().rstrip(",")
            if not kus:
                continue
            jmeno, email = base.parse_recipient(kus)
            if email:
                out.append((jmeno, email))
        return out

    base.parse_recipients = _parse_recipients

# Drafts folder is localised; Outlook exposes it under the display name.
DRAFTS_NAMES = ["Koncepty", "Drafts", "Entwürfe", "Brouillons", "Borradores", "Bozze"]

IMAGE_LINE = re.compile(r"^!\[([^\]]*)\]\(([^)]+)\)$")


def split_body(body: str) -> list[tuple[str, str]]:
    """Split the Markdown body into ('text'|'image', payload) segments.

    A standalone ![alt](path) line becomes its own image segment; everything
    else accumulates into text segments that go through md_to_html untouched.
    """
    segments: list[tuple[str, str]] = []
    buffer: list[str] = []
    for line in body.split("\n"):
        m = IMAGE_LINE.match(line.strip())
        if m:
            if buffer:
                segments.append(("text", "\n".join(buffer)))
                buffer = []
            segments.append(("image", m.group(2).strip()))
        else:
            buffer.append(line)
    if buffer:
        segments.append(("text", "\n".join(buffer)))
    return segments


def build_html(segments, md_dir: str, max_width: int):
    """Render segments to HTML, returning (html, [(cid, path), ...])."""
    parts: list[str] = []
    images: list[tuple[str, str]] = []
    for kind, payload in segments:
        if kind == "text":
            html = base.md_to_html(payload.strip())
            if html:
                parts.append(html)
            continue

        path = payload if os.path.isabs(payload) else os.path.join(md_dir, payload)
        if not os.path.isfile(path):
            print(f"Chyba: obrázek nenalezen: {path}", file=sys.stderr)
            sys.exit(1)
        cid = make_msgid(domain="email-draft.local")
        images.append((cid, path))
        parts.append(
            f'<p style="margin:0 0 14px 0;">'
            f'<img src="cid:{cid[1:-1]}" width="{max_width}" '
            f'style="max-width:100%;height:auto;border:1px solid #d9d9d9;">'
            f"</p>"
        )
    return "\n".join(parts), images


def plain_text(segments) -> str:
    """A text/plain alternative so the message is not HTML-only."""
    out = []
    for kind, payload in segments:
        if kind == "text":
            txt = re.sub(r"\*\*(.+?)\*\*", r"\1", payload)
            txt = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", txt)
            out.append(txt.strip())
        else:
            out.append("[obrázek]")
    return "\n\n".join(p for p in out if p)


def build_eml(meta, segments, md_dir, max_width, attachments) -> bytes:
    body_html, images = build_html(segments, md_dir, max_width)
    profile = base.load_sender_profile(meta.get("signature", "datawizard"))
    full_html = base.wrap_html(body_html + base.signature_html(profile))

    msg = EmailMessage()
    msg["Subject"] = meta.get("subject", "")
    if meta.get("from"):
        msg["From"] = meta["from"]
    to_list = base.parse_recipients(meta.get("to", ""))
    cc_list = base.parse_recipients(meta.get("cc", ""))
    msg["To"] = ", ".join(f"{n} <{e}>" if n else e for n, e in to_list)
    if cc_list:
        msg["Cc"] = ", ".join(f"{n} <{e}>" if n else e for n, e in cc_list)
    msg["Date"] = formatdate(localtime=True)
    # Tells Outlook this is an unsent message rather than a received one.
    msg["X-Unsent"] = "1"

    msg.set_content(plain_text(segments) + base.signature_text(profile))
    msg.add_alternative(f"<html><body>{full_html}</body></html>", subtype="html")

    html_part = msg.get_payload()[1]
    for cid, path in images:
        ctype, _ = mimetypes.guess_type(path)
        maintype, subtype = (ctype or "image/png").split("/", 1)
        with open(path, "rb") as f:
            html_part.add_related(
                f.read(), maintype=maintype, subtype=subtype,
                cid=cid, filename=os.path.basename(path),
            )

    for path in attachments:
        ctype, _ = mimetypes.guess_type(path)
        maintype, subtype = (ctype or "application/octet-stream").split("/", 1)
        with open(path, "rb") as f:
            msg.add_attachment(
                f.read(), maintype=maintype, subtype=subtype,
                filename=os.path.basename(path),
            )

    return msg.as_bytes(), len(images)


def import_to_drafts(eml_path: str) -> str:
    """Import the .eml into Outlook's Drafts folder, return the folder name."""
    names = " , ".join(f'"{n}"' for n in DRAFTS_NAMES)
    script = f'''\
tell application "Microsoft Outlook"
    set target to missing value
    repeat with n in {{{names}}}
        try
            set target to mail folder (n as text)
            exit repeat
        end try
    end repeat
    if target is missing value then error "Nenasel jsem slozku Koncepty/Drafts."
    set m to import eml POSIX file "{base.as_escape(os.path.abspath(eml_path))}" to target
    activate
    open m
    return name of target
end tell
'''
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if result.returncode != 0:
        print("Chyba pri importu do Outlooku:", file=sys.stderr)
        print(result.stderr.strip(), file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Open a Markdown email draft in Outlook with inline images"
    )
    parser.add_argument("file", help="Path to Markdown file with YAML frontmatter")
    parser.add_argument("--attachment", action="append", default=[],
                        help="Extra file to attach as a regular attachment (repeatable)")
    parser.add_argument("--max-width", type=int, default=720,
                        help="Display width of inline images in px (default: 720)")
    parser.add_argument("--eml-only", metavar="PATH",
                        help="Only write the .eml to PATH, do not touch Outlook")
    args = parser.parse_args()

    path = os.path.expanduser(args.file)
    if not os.path.isfile(path):
        print(f"Soubor nenalezen: {path}", file=sys.stderr)
        sys.exit(1)

    with open(path, encoding="utf-8") as f:
        meta, body = base.parse_frontmatter(f.read())

    # Same body cleanup as the sibling script: drop the title and the draft-note
    # blockquote that never belongs in the sent mail.
    body = re.sub(r"^#\s+.*\n*", "", body, count=1).strip()
    kept: list[str] = []
    in_meta = True
    for line in body.split("\n"):
        if in_meta and (not line.strip() or line.strip().startswith(">")):
            continue
        if in_meta and line.strip() == "---":
            in_meta = False
            continue
        in_meta = False
        kept.append(line)
    body = "\n".join(kept).strip()

    if not meta.get("subject"):
        print("Chybí pole 'subject' ve frontmatter.", file=sys.stderr)
        sys.exit(1)
    if not base.parse_recipients(meta.get("to", "")):
        print("Chybí pole 'to' ve frontmatter.", file=sys.stderr)
        sys.exit(1)

    md_dir = os.path.dirname(os.path.abspath(path))
    segments = split_body(body)

    fm_att = meta.get("attachments", [])
    if isinstance(fm_att, str):
        fm_att = [fm_att]
    attachments = []
    for att in list(args.attachment) + list(fm_att or []):
        att = att.strip()
        if not att:
            continue
        full = att if os.path.isabs(att) else os.path.join(md_dir, att)
        if not os.path.isfile(full):
            print(f"Varování: příloha nenalezena: {full}", file=sys.stderr)
            continue
        attachments.append(full)

    raw, n_images = build_eml(meta, segments, md_dir, args.max_width, attachments)

    if args.eml_only:
        with open(args.eml_only, "wb") as f:
            f.write(raw)
        print(f"Zapsano: {args.eml_only} ({len(raw)} B, {n_images} inline obrazku)")
        return

    eml_path = os.path.join(md_dir, ".draft.eml")
    with open(eml_path, "wb") as f:
        f.write(raw)
    folder = import_to_drafts(eml_path)
    os.remove(eml_path)

    kdo = ", ".join(n or e for n, e in base.parse_recipients(meta.get("to", "")))
    print(f"Hotovo — koncept pro {kdo} je ve slozce {folder}.")
    print(f"Inline obrazku: {n_images}, priloh: {len(attachments)}, velikost: {len(raw)//1024} kB")


if __name__ == "__main__":
    main()
