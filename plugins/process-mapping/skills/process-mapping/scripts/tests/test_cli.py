import contextlib
import io
import tempfile
import unittest
from pathlib import Path

import pmaplib.model as model
from pmap import main
from tests.helpers import EXAMPLE


def run(argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = main(argv)
    return rc, out.getvalue(), err.getvalue()


class CliCheck(unittest.TestCase):
    def test_example_ok(self):
        rc, out, _ = run(["check", str(EXAMPLE)])
        self.assertEqual(rc, 0)
        self.assertEqual(out.strip(), "OK: schvalovani-faktur · 9 kroků, 5 rolí")

    def test_broken_reference_returns_1(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.process.toml"
            p.write_text('[process]\nid = "x"\ntitle = "X"\n[[lane]]\nid = "a"\nname = "A"\n'
                         '[[step]]\nid = "s1"\nlane = "neni"\ntitle = "Krok"\n', encoding="utf-8")
            rc, _, err = run(["check", str(p)])
        self.assertEqual(rc, 1)
        self.assertIn("CHYBA", err)

    def test_missing_file_and_bad_toml_return_2(self):
        rc, _, err = run(["check", "/neexistuje/x.process.toml"])
        self.assertEqual((rc, "neexistuje" in err), (2, True))
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.process.toml"
            p.write_text("[process\n", encoding="utf-8")
            rc, _, err = run(["check", str(p)])
        self.assertEqual((rc, "neplatné TOML" in err), (2, True))

    def test_missing_toml_parser_returns_2_with_uv_hint(self):
        saved = model.tomllib
        model.tomllib = None
        try:
            rc, _, err = run(["check", str(EXAMPLE)])
        finally:
            model.tomllib = saved
        self.assertEqual(rc, 2)
        self.assertIn("uv run", err)
