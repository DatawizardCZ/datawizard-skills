import contextlib
import io
import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path

from pmaplib.figma import FIGMA_DIR, MAX_CODE, figma_code
from pmaplib.layout import compute_layout
from pmaplib.model import SpecError, from_dict, load
from pmap import main
from tests.helpers import EXAMPLE, base_spec


def run(argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = main(argv)
    return rc, out.getvalue(), err.getvalue()


def embedded(code, marker):
    return json.loads(re.search(r"const " + marker + r" = (.*?);\n", code).group(1))


class Figma(unittest.TestCase):
    def test_build_embeds_layout_as_ascii_json(self):
        L = compute_layout(load(EXAMPLE))
        code = figma_code(L, "build")
        self.assertNotIn("/*LAYOUT*/", code)
        literal = re.search(r"const L = (.*?);\n", code).group(1)
        self.assertTrue(literal.isascii())
        self.assertEqual(json.loads(literal), L)
        self.assertLess(len(code), MAX_CODE)

    def test_hostile_text_stays_inside_the_literal(self):
        d = base_spec()
        d["process"]["title"] = 'X"; figma.root.remove(); // '
        code = figma_code(compute_layout(from_dict(d)), "build")
        template = (FIGMA_DIR / "build-swimlane.js").read_text(encoding="utf-8")
        self.assertEqual(embedded(code, "L")["meta"]["title"], 'X"; figma.root.remove(); //')
        self.assertEqual(code.count("\n"), template.count("\n"))   # žádný nový řádek ani kód navíc
        self.assertIn('X\\"; figma.root.remove(); //', code)

    def test_marker_text_does_not_break_motion_code(self):
        d = base_spec()
        d["process"]["title"] = "Proces /*IDS*/null /*LAYOUT*/null konec"
        L = compute_layout(from_dict(d))
        code = figma_code(L, "motion", {"root": "1:1"})
        self.assertEqual(embedded(code, "L"), json.loads(json.dumps(L)))
        self.assertEqual(embedded(code, "IDS"), {"root": "1:1"})

    def test_motion_needs_ids(self):
        L = compute_layout(load(EXAMPLE))
        with self.assertRaisesRegex(SpecError, "--ids"):
            figma_code(L, "motion")
        code = figma_code(L, "motion", {"root": "1:1"})
        self.assertEqual(embedded(code, "IDS"), {"root": "1:1"})

    def test_too_big_is_refused(self):
        L = compute_layout(load(EXAMPLE))
        L = dict(L, padding="x" * MAX_CODE)
        with self.assertRaisesRegex(SpecError, "podprocesy"):
            figma_code(L, "build")


class FigmaCli(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.spec = self.dir / "faktury-to-be.process.toml"
        shutil.copy(EXAMPLE, self.spec)

    def tearDown(self):
        self.tmp.cleanup()

    def test_figma_build_and_motion(self):
        rc, _, _ = run(["figma", str(self.spec), "--part", "build"])
        self.assertEqual(rc, 0)
        self.assertTrue((self.dir / "faktury-to-be.figma-build.js").exists())
        rc, _, err = run(["figma", str(self.spec), "--part", "motion"])
        self.assertEqual((rc, "--ids" in err), (1, True))
        ids = self.dir / "ids.json"
        ids.write_text('{"root": "1:1"}', encoding="utf-8")
        rc, _, _ = run(["figma", str(self.spec), "--part", "motion", "--ids", str(ids)])
        self.assertEqual(rc, 0)
