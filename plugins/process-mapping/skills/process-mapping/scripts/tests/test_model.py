import unittest

from pmaplib.model import SpecError, from_dict, load
from tests.helpers import EXAMPLE, base_spec
import tempfile
from pathlib import Path


def load_bytes(data: bytes):
    with tempfile.TemporaryDirectory() as td:
        p = Path(td, "x.process.toml")
        p.write_bytes(data)
        return load(p)


class BadInput(unittest.TestCase):
    def test_cp1250_file_is_a_clear_error(self):
        src = '[process]\nid = "x"\ntitle = "Účetní proces"\n'.encode("cp1250")
        with self.assertRaisesRegex(SpecError, "UTF-8"):
            load_bytes(src)

    def test_bom_is_accepted(self):
        self.assertEqual(load_bytes(b"\xef\xbb\xbf" + Path(EXAMPLE).read_bytes()).id, "schvalovani-faktur")

    def test_wrong_types_are_spec_errors(self):
        cases = [("pain", 5), ("tools", 5), ("items", ["subtitle check"]), ("items", {"title": "x"}), ("next", "false")]
        for key, val in cases:
            with self.subTest(key=key, val=val):
                d = base_spec()
                d["step"][0][key] = val
                if key == "items":
                    d["step"][0]["type"] = "checks"
                with self.assertRaises(SpecError):
                    from_dict(d)
        d = base_spec()
        d["process"]["auto_flow"] = "false"
        with self.assertRaisesRegex(SpecError, "true nebo false"):
            from_dict(d)
        d = base_spec()
        d["lane"] = ["ucetni"]
        with self.assertRaises(SpecError):
            from_dict(d)

    def test_list_in_single_line_field_is_joined(self):
        d = base_spec()
        d["step"][0]["today"] = ["e-mail", "papír"]
        self.assertEqual(from_dict(d).steps[0].today, "e-mail, papír")



class LoadExample(unittest.TestCase):
    def test_example_loads(self):
        p = load(EXAMPLE)
        self.assertEqual(p.id, "schvalovani-faktur")
        self.assertEqual([l.id for l in p.lanes], ["ucetni", "system", "vedouci", "reditel", "controlling"])
        self.assertEqual(len(p.steps), 9)
        self.assertEqual(p.steps[3].type, "checks")
        self.assertEqual(len(p.steps[3].items), 4)
        self.assertEqual(p.states_label, "Stavy faktury")
        self.assertEqual(p.owner, "finanční manažer")
        self.assertEqual(p.steps[0].tools, ["e-mail", "skener"])
        self.assertEqual(p.steps[4].pain, ["Při dovolené vedoucího faktury stojí."])
        self.assertEqual(len(p.open_questions()), 4)
        self.assertEqual(len(p.open_questions("vedouci")), 1)
        self.assertEqual(p.resolved_questions()[0].answer, "Ano, na finančního manažera.")
        self.assertEqual(p.notes, [])

    def test_auto_flow_and_explicit_flows(self):
        p = load(EXAMPLE)
        pairs = [(f.src, f.dst, f.kind) for f in p.all_flows()]
        self.assertEqual(pairs[:3], [("k", "s3", "loop"), ("s6", "s7", "main"), ("s6", "s8", "alt")])
        self.assertIn(("s1", "s2", "main"), pairs)
        self.assertIn(("s7", "s8", "main"), pairs)
        self.assertNotIn(("s9", "s1", "main"), pairs)
        self.assertEqual(len(pairs), 10)

    def test_auto_flow_off(self):
        d = base_spec()
        d["process"]["auto_flow"] = False
        self.assertEqual(from_dict(d).all_flows(), [])

    def test_explicit_main_replaces_auto(self):
        d = base_spec()
        d["flow"] = [{"from": "x1", "to": "x3"}]
        self.assertEqual([(f.src, f.dst) for f in from_dict(d).all_flows()], [("x1", "x3"), ("x2", "x3")])

    def test_next_false_stops_auto_flow(self):
        d = base_spec()
        d["step"][1]["next"] = False
        self.assertEqual([(f.src, f.dst) for f in from_dict(d).all_flows()], [("x1", "x2")])


class Coercion(unittest.TestCase):
    def test_single_line_fields_are_collapsed(self):
        d = base_spec()
        d["step"][0]["title"] = "Řádek\njedna   a\tdvě"
        self.assertEqual(from_dict(d).steps[0].title, "Řádek jedna a dvě")

    def test_non_string_values_become_text(self):
        d = base_spec()
        d["step"][0]["title"] = 123
        self.assertEqual(from_dict(d).steps[0].title, "123")

    def test_today_as_string(self):
        d = base_spec()
        d["process"]["today"] = "jedna věta"
        self.assertEqual(from_dict(d).today, ["jedna věta"])

    def test_question_accepts_step_key(self):
        d = base_spec()
        d["question"] = [{"step": "x1", "text": "Co?"}]
        self.assertEqual(from_dict(d).questions[0].ref, "x1")

    def test_unknown_keys_and_numeric_version_are_noted(self):
        d = base_spec()
        d["process"]["version"] = 0.1
        d["step"][0]["detial"] = "překlep"
        d["flow"] = [{"from": "x1", "to": "x2", "type": "loop"}]
        notes = " | ".join(from_dict(d).notes)
        self.assertIn("'detial'", notes)
        self.assertIn("'type'", notes)
        self.assertIn("uvozovkách", notes)


class Errors(unittest.TestCase):
    def test_missing_process_block(self):
        with self.assertRaisesRegex(SpecError, r"\[process\]"):
            from_dict({"step": []})

    def test_missing_required_field(self):
        d = base_spec()
        del d["step"][0]["lane"]
        with self.assertRaisesRegex(SpecError, r"\[\[step\]\] č\. 1.*lane"):
            from_dict(d)

    def test_bad_col(self):
        d = base_spec()
        d["step"][0]["col"] = "druhý"
        with self.assertRaisesRegex(SpecError, "col musí být celé číslo"):
            from_dict(d)

    def test_no_steps(self):
        d = base_spec()
        d["step"] = []
        with self.assertRaisesRegex(SpecError, "žádný"):
            from_dict(d)

    def test_missing_file_and_directory(self):
        with self.assertRaisesRegex(SpecError, "neexistuje"):
            load("/neexistuje/proces.process.toml")
        with self.assertRaisesRegex(SpecError, "nejde přečíst"):
            load(EXAMPLE.parent)
