import contextlib
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from pmap import main
from tests.helpers import EXAMPLE


def run(argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = main(argv)
    return rc, out.getvalue(), err.getvalue()


class CliOutputs(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.spec = self.dir / "faktury-to-be.process.toml"
        shutil.copy(EXAMPLE, self.spec)

    def tearDown(self):
        self.tmp.cleanup()

    def test_default_names_follow_spec_file(self):
        for cmd, suffix in (("layout", ".layout.json"), ("mermaid", ".mermaid.md"), ("html", ".html"), ("svg", ".svg")):
            rc, out, err = run([cmd, str(self.spec)])
            self.assertEqual(rc, 0, err)
            self.assertTrue((self.dir / f"faktury-to-be{suffix}").exists(), cmd)
        self.assertEqual(json.loads((self.dir / "faktury-to-be.layout.json").read_text(encoding="utf-8"))["width"], 1520)

    def test_out_into_missing_folder(self):
        target = self.dir / "nova" / "slozka" / "x.html"
        rc, _, _ = run(["html", str(self.spec), "-o", str(target)])
        self.assertEqual(rc, 0)
        self.assertTrue(target.exists())

    def test_out_is_a_folder_is_a_clear_error(self):
        rc, _, err = run(["html", str(self.spec), "-o", str(self.dir)])
        self.assertEqual(rc, 1)
        self.assertIn("CHYBA", err)

    def test_links_are_validated(self):
        ok = self.dir / "ok.html"
        rc, _, _ = run(["html", str(self.spec), "-o", str(ok), "--link", "Dokument=proces.md",
                        "--link", "Web=https://example.com", "--link", "Kotva=#top"])
        self.assertEqual(rc, 0)
        self.assertIn('<a href="proces.md">Dokument</a>', ok.read_text(encoding="utf-8"))
        for bad in ("X=javascript:alert(1)", "X=data:text/html,x", "bez-rovnitka"):
            rc, _, err = run(["html", str(self.spec), "-o", str(self.dir / "bad.html"), "--link", bad])
            self.assertEqual(rc, 1, bad)
            self.assertIn("--link", err)
