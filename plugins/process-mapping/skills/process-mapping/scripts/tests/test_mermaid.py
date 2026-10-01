import unittest

from pmaplib.mermaid import render_flowchart, render_markdown
from pmaplib.model import from_dict, load
from tests.helpers import EXAMPLE, base_spec


class Mermaid(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.md = render_markdown(load(EXAMPLE), "schvalovani-faktur.process.toml")

    def test_flowchart(self):
        md = self.md
        self.assertIn("flowchart LR", md)
        for sid in ("s1", "s2", "s3", "k", "s5", "s6", "s7", "s8", "s9"):
            self.assertIn(f"n_{sid}", md)
        self.assertIn('subgraph lane_ucetni["Účetní"]', md)
        self.assertIn('n_k -.->|"opravit údaje"| n_s3', md)
        self.assertIn('n_s6 -->|"nad limit"| n_s7', md)
        self.assertIn('n_s6 -.->|"do limitu"| n_s8', md)
        self.assertIn('n_s6{"Nad 50 000 Kč? ??"}', md)
        self.assertIn('n_s1(["Přijme fakturu"])', md)
        self.assertIn('n_k[["Kontroly faktury ??"]]', md)
        self.assertIn("class n_s2,n_k,n_s6 q", md)
        self.assertIn('span_0[/"Průběžně: sleduje čerpání rozpočtu střediska"/]', md)
        self.assertIn("`schvalovani-faktur.process.toml`", md)

    def test_states_and_questions(self):
        md = self.md
        self.assertIn("## Stavy faktury", md)
        self.assertIn('state "Ke schválení" as n_st2', md)
        self.assertIn("[*] --> n_st1", md)
        self.assertIn("n_st5 --> [*]", md)
        self.assertEqual(md.count("- `??` "), 4)
        self.assertIn("(role Vedoucí střediska, odpoví: finanční manažer)", md)
        self.assertIn("## Vyřešené otázky", md)

    def test_escaping_and_ids(self):
        d = base_spec()
        d["step"][0]["title"] = 'Řekne "ano" & <B> #1'
        d["step"][1]["id"] = "end"
        d["step"][2]["id"] = "a-b"
        d["lane"][0]["name"] = "A < B"
        out = render_flowchart(from_dict(d))
        self.assertIn('n_x1["Řekne #quot;ano#quot; #amp; #lt;B#gt; #35;1"]', out)
        self.assertIn('lane_a["A #lt; B"]', out)
        self.assertIn("n_end", out)
        self.assertIn("n_a_2d_b", out)
        d["process"]["title"] = "Test <x> & y"
        self.assertIn("# Test &lt;x&gt; &amp; y", render_markdown(from_dict(d)))

    def test_no_states_no_questions(self):
        md = render_markdown(from_dict(base_spec()))
        self.assertNotIn("stateDiagram", md)
        self.assertNotIn("Otevřené otázky", md)
