import unittest

from pmaplib.layout import compute_layout
from pmaplib.lint import check_layout
from pmaplib.model import from_dict, load
from tests.helpers import EXAMPLE, base_spec, big_spec


def issues(d):
    return check_layout(compute_layout(from_dict(d)))


class Lint(unittest.TestCase):
    def test_example_is_clean(self):
        self.assertEqual(check_layout(compute_layout(load(EXAMPLE))), [])

    def test_manual_col_overlap_is_error(self):
        d = base_spec()
        d["step"][2]["col"] = 0
        msgs = [i.msg for i in issues(d) if i.level == "error"]
        self.assertTrue(any("překrývají" in m for m in msgs))

    def test_long_texts_warn(self):
        d = base_spec()
        d["step"][0]["title"] = "Velmi dlouhý titulek kroku, který se nevejde ani na dva řádky karty"
        d["step"][1]["title"] = "https://example.com/velmi/dlouha/adresa"
        d["step"][2]["sub"] = "viz https://example.com/velmi/dlouha/adresa"
        msgs = " | ".join(i.msg for i in issues(d))
        self.assertIn("titulek", msgs)
        self.assertEqual(msgs.count("slovo je delší"), 2)

    def test_states_out_of_order_warn(self):
        d = base_spec()
        d["state"] = [{"name": "B", "at": "x3"}, {"name": "A", "at": "x1"}]
        self.assertTrue(any("mimo pořadí" in i.msg for i in issues(d)))

    def test_forced_route_through_card_warns(self):
        d = base_spec()
        d["flow"] = [{"from": "x2", "to": "x3", "route": "vh"}]
        self.assertTrue(any("vede přes kartu" in i.msg and "route" in i.msg for i in issues(d)))

    def test_loop_through_its_own_target_warns(self):
        d = base_spec()
        d["step"] = d["step"][:2]
        d["flow"] = [{"from": "x2", "to": "x1", "kind": "loop"}]
        self.assertTrue(any("vede přes kartu" in i.msg and "col" in i.msg for i in issues(d)))

    def test_big_process_only_advises(self):
        found = issues(big_spec())
        self.assertFalse([i for i in found if i.level == "error"])
        for i in found:
            self.assertTrue("pomůže" in i.msg or "posuň" in i.msg or "zkrať" in i.msg, i.msg)
