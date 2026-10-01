import json
import re
import unittest

from pmaplib.html import render_html, render_svg
from pmaplib.layout import compute_layout
from pmaplib.model import from_dict, load
from tests.helpers import EXAMPLE, base_spec


def render(proc, links=None):
    return render_html(proc, compute_layout(proc), links, generated="2026-10-01")


def js_object(html, name):
    """Hodnota vložená do skriptu: var <name> = <JSON>;"""
    return json.loads(re.search(r"var " + name + r" = (.*?);(?: *//[^\n]*)?\n", html).group(1))


class ExampleHtml(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proc = load(EXAMPLE)
        cls.html = render(cls.proc)

    def test_complete_and_self_contained(self):
        for s in self.proc.steps:
            for word in s.title.split():
                self.assertIn(word, self.html)
        self.assertIsNone(re.search(r"__[A-Z][A-Z_]*__", self.html))
        self.assertNotIn("marker-end", self.html)
        # žádné externí zdroje (xmlns SVG není požadavek)
        self.assertIsNone(re.search(r'(src|href)="https?:|url\(\s*["\']?https?:|@import', self.html))
        self.assertEqual(self.html.count("</script>"), 2)
        self.assertIn("vygenerováno 2026-10-01", self.html)
        self.assertIn("upraveno 2026-10-01", self.html)

    def test_csp_hashes_match_scripts(self):
        import base64
        import hashlib
        scripts = re.findall(r"<script>(.*?)</script>", self.html, re.S)
        csp = re.search(r"script-src ([^;]+);", self.html).group(1)
        for sc in scripts:
            h = base64.b64encode(hashlib.sha256(sc.encode()).digest()).decode()
            self.assertIn(f"'sha256-{h}'", csp)

    def test_one_tip_per_wire(self):
        self.assertEqual(len(re.findall(r'class="mk(?:-a)? tip"', self.html)), 14)

    def test_details_overview_and_steps(self):
        d = js_object(self.html, "nodeData")
        self.assertEqual(d["step:s2"]["q"], ["Kolik faktur přichází jen v papíru? (odpoví: účetní)"])
        self.assertEqual(d["step:s7"]["done"], ["Může ředitel schválení delegovat? → Ano, na finančního manažera."])
        self.assertEqual(d["step:k"]["label"], "Krok 3 · Kontroly faktury")
        self.assertEqual(len(d["step:k"]["items"]), 4)
        self.assertIn(["Systémy", "e-mail, skener"], d["step:s1"]["rows"])
        self.assertEqual(d["step:s5"]["pain"], ["Při dovolené vedoucího faktury stojí."])
        self.assertEqual(len(d["lane:vedouci"]["q"]), 1)
        self.assertIn("span:0", d)
        self.assertIn("state:st3", d)
        self.assertIn("Otevřené otázky (4)", self.html)
        self.assertIn("Bolesti (2)", self.html)
        self.assertIn("<td>Vlastník</td><td>finanční manažer</td>", self.html)
        steps = js_object(self.html, "steps")
        self.assertEqual([s["id"] for s in steps], [s.id for s in self.proc.steps])
        self.assertEqual(steps[0]["until"], 0.75)

    def test_states_ring_and_print(self):
        self.assertEqual(self.html.count('class="st hit"'), 5)
        self.assertIn("translateX(1208px)", self.html)
        self.assertIn("STAVY FAKTURY", self.html)
        self.assertIn("@media print", self.html)
        self.assertIn("min-width: 1292px", self.html)

    def test_links(self):
        html = render(self.proc, [("Dokument", "proces.md")])
        self.assertIn('<a href="proces.md">Dokument</a>', html)


class EdgeHtml(unittest.TestCase):
    def test_escaping(self):
        d = base_spec()
        d["process"]["title"] = 'Test <b>&"x"</b>'
        d["step"][0]["detail"] = "konec </script> a <!--<script> tady"
        html = render(from_dict(d))
        self.assertIn("Test &lt;b&gt;&amp;&quot;x&quot;&lt;/b&gt;", html)
        self.assertNotIn("<b>&", html)
        self.assertEqual(html.count("</script>"), 2)
        self.assertEqual(html.count("<!--"), 0)
        self.assertEqual(js_object(html, "nodeData")["step:x1"]["desc"], "konec </script> a <!--<script> tady")

    def test_placeholder_markers_in_text_stay_literal(self):
        d = base_spec()
        marker = "a /*DETAILS*/null b /*STEPS*/null c /*RING*/null d /*DURATION*/0 e"
        d["step"][0]["detail"] = marker
        html = render(from_dict(d))
        self.assertEqual(js_object(html, "nodeData")["step:x1"]["desc"], marker)
        self.assertIsInstance(js_object(html, "steps"), list)
        self.assertIsInstance(js_object(html, "duration"), (int, float))

    def test_without_states_and_questions(self):
        html = render(from_dict(base_spec()))
        self.assertNotIn('class="st hit"', html)
        self.assertIn("Žádné otevřené otázky.", html)
        self.assertNotIn("Rámec", html)


class StaticSvg(unittest.TestCase):
    def test_static_svg_is_final_and_light(self):
        import xml.etree.ElementTree as ET
        proc = load(EXAMPLE)
        svg = render_svg(proc, compute_layout(proc))
        root = ET.fromstring(svg.split("\n", 1)[1])
        self.assertTrue(root.tag.endswith("svg"))
        self.assertNotIn("var(--", svg)
        self.assertNotIn("pathLength", svg)
        self.assertNotIn("mask=", svg)
        self.assertIn('transform="translate(1208,0)"', svg)
        self.assertIn("#1168bd", svg)
