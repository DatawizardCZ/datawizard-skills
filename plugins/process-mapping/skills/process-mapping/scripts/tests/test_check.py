import unittest

from pmaplib.check import check
from pmaplib.model import from_dict, load
from tests.helpers import EXAMPLE, base_spec


def errors(d):
    return [i.msg for i in check(from_dict(d)) if i.level == "error"]


def warnings(d):
    return [i.msg for i in check(from_dict(d)) if i.level == "warning"]


class CheckReferences(unittest.TestCase):
    def test_example_is_clean(self):
        self.assertEqual(check(load(EXAMPLE)), [])

    def test_unknown_lane(self):
        d = base_spec()
        d["step"][0]["lane"] = "neni"
        self.assertTrue(any("role 'neni' neexistuje" in m for m in errors(d)))

    def test_duplicate_id(self):
        d = base_spec()
        d["step"][1]["id"] = "x1"
        self.assertTrue(any("dvakrát" in m for m in errors(d)))

    def test_id_shapes(self):
        d = base_spec()
        d["process"]["id"] = "../Venku"
        d["step"][0]["id"] = "krok č.1"
        msgs = " | ".join(errors(d))
        self.assertIn("kebab-case", msgs)
        self.assertIn("smí obsahovat", msgs)

    def test_flow_to_unknown_step(self):
        d = base_spec()
        d["flow"] = [{"from": "x1", "to": "nikam", "kind": "loop"}]
        self.assertTrue(any("'nikam' neexistuje" in m for m in errors(d)))

    def test_bad_enums(self):
        d = base_spec()
        d["process"]["kind"] = "budoucnost"
        d["step"][0]["type"] = "ukol"
        d["flow"] = [{"from": "x3", "to": "x1", "kind": "zpet", "route": "xy"}]
        msgs = " | ".join(errors(d))
        for word in ("budoucnost", "ukol", "zpet", "xy"):
            self.assertIn(word, msgs)

    def test_question_refs_and_status(self):
        d = base_spec()
        d["question"] = [{"ref": "neni", "text": "Co s tím?"}, {"ref": "x1", "text": "Hotovo?", "status": "resolved"}]
        self.assertTrue(any("není krok, role ani stav" in m for m in errors(d)))
        self.assertTrue(any("nemá answer" in m for m in warnings(d)))

    def test_state_at_unknown_step(self):
        d = base_spec()
        d["state"] = [{"name": "Hotovo", "at": "neni"}]
        self.assertTrue(any("(at) neexistuje" in m for m in errors(d)))

    def test_dangling_steps_warn(self):
        d = base_spec()
        d["process"]["auto_flow"] = False
        w = warnings(d)
        self.assertTrue(any("'x2' nemá žádný vstup" in m for m in w))
        self.assertTrue(any("'x1' nemá žádný výstup" in m for m in w))

    def test_lane_without_steps_warns(self):
        d = base_spec()
        d["lane"].append({"id": "c", "name": "Prázdná"})
        self.assertTrue(any("'c' nemá žádný krok" in m for m in warnings(d)))

    def test_load_notes_become_warnings(self):
        d = base_spec()
        d["step"][0]["detial"] = "x"
        self.assertTrue(any("'detial'" in m for m in warnings(d)))
