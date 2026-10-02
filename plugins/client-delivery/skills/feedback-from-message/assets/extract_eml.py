#!/usr/bin/env python3
"""Extract .eml into text + html body + inline images, numbered by HTML order.

Usage:
    python3 extract_eml.py <path-to-eml> <output-folder>

Creates inside <output-folder>/attachments/:
    body.txt        — plain text body
    body.html       — HTML body
    img-01.png …    — inline images, numbered by appearance in HTML
    cid-map.txt     — CID → filename mapping
"""

import email
import os
import re
import sys
from email import policy


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    eml_path = sys.argv[1]
    out_dir = sys.argv[2]
    attachments_dir = os.path.join(out_dir, "attachments")
    os.makedirs(attachments_dir, exist_ok=True)

    with open(eml_path, "rb") as f:
        msg = email.message_from_binary_file(f, policy=policy.default)

    print(f"Subject: {msg['Subject']}")
    print(f"From:    {msg['From']}")
    print(f"To:      {msg['To']}")
    print(f"Date:    {msg['Date']}")
    print("---")

    body_text = None
    body_html = None
    for part in msg.walk():
        ctype = part.get_content_type()
        cdisp = str(part.get("Content-Disposition") or "")
        if "attachment" in cdisp:
            continue
        if ctype == "text/plain" and body_text is None:
            body_text = part.get_content()
        elif ctype == "text/html" and body_html is None:
            body_html = part.get_content()

    if body_text:
        with open(os.path.join(attachments_dir, "body.txt"), "w") as f:
            f.write(body_text)
        print(f"Saved body.txt ({len(body_text)} chars)")

    if body_html:
        with open(os.path.join(attachments_dir, "body.html"), "w") as f:
            f.write(body_html)
        print(f"Saved body.html ({len(body_html)} chars)")

    # Order CIDs by their first appearance in HTML body
    cid_order = []
    seen = set()
    for m in re.finditer(r"cid:([^\"'>\s]+)", body_html or ""):
        cid = m.group(1)
        if cid not in seen:
            seen.add(cid)
            cid_order.append(cid)

    print(f"\nFound {len(cid_order)} inline CIDs in HTML order:")
    for i, cid in enumerate(cid_order, 1):
        print(f"  {i:02d}. {cid}")

    cid_to_filename = {}
    extra_idx = 99
    for part in msg.walk():
        ctype = part.get_content_type()
        if not ctype.startswith("image/"):
            continue
        cid = (part.get("Content-ID") or "").strip("<>")
        ext = ctype.split("/")[-1].lower()
        if ext == "jpeg":
            ext = "jpg"

        if cid in cid_order:
            order = cid_order.index(cid) + 1
        else:
            extra_idx += 1
            order = extra_idx

        filename = f"img-{order:02d}.{ext}"
        cid_to_filename[cid] = filename

        payload = part.get_payload(decode=True)
        if payload:
            with open(os.path.join(attachments_dir, filename), "wb") as f:
                f.write(payload)
            print(f"  saved {filename} (cid={cid[:8]}…, {len(payload)} B)")

    with open(os.path.join(attachments_dir, "cid-map.txt"), "w") as f:
        for cid, fn in cid_to_filename.items():
            f.write(f"{cid}\t{fn}\n")

    print(f"\nDone. Output in: {attachments_dir}")


if __name__ == "__main__":
    main()
