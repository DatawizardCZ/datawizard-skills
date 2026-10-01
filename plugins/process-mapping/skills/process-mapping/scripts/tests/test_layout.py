import unittest

from pmaplib.layout import TIP_GAP, assign_columns, compute_layout, path_hits, rect_of, rects_overlap
from pmaplib.model import from_dict, load
from tests.helpers import EXAMPLE, base_spec, big_spec


def wire(L, src, dst):
    return next(w for w in L["wires"] if w["src"] == src and w["dst"] == dst)


def on_border(pt, c, tol=0.6):
    x, y = pt
    x0, y0, x1, y1 = rect_of(c)
    in_x = x0 - tol <= x <= x1 + tol
    in_y = y0 - tol <= y <= y1 + tol
    return ((abs(x - x0) <= tol or abs(x - x1) <= tol) and in_y) or ((abs(y - y0) <= tol or abs(y - y1) <= tol) and in_x)


def dist_outside(pt, c):
    x, y = pt
    x0, y0, x1, y1 = rect_of(c)
    dx = max(x0 - x, 0, x - x1)
    dy = max(y0 - y, 0, y - y1)
    return (dx * dx + dy * dy) ** 0.5


def assert_sound(tc, L):
    """Vlastnosti, které musí platit pro každé rozložení."""
    cards = {c["id"]: c for c in L["cards"]}
    cs = L["cards"]
    for i, a in enumerate(cs):
        for b in cs[i + 1:]:
            tc.assertFalse(rects_overlap(rect_of(a), rect_of(b)), (a["id"], b["id"]))
    for w in L["wires"]:
        if w["kind"] == "state":
            continue
        tc.assertTrue(on_border(w["points"][0], cards[w["src"]]), w)
        tc.assertAlmostEqual(dist_outside(w["points"][-1], cards[w["dst"]]), TIP_GAP, delta=0.6, msg=w)
        tc.assertEqual(len(w["tip"]), 3)


class ExampleLayout(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proc = load(EXAMPLE)
        cls.L = compute_layout(cls.proc)
        cls.cards = {c["id"]: c for c in cls.L["cards"]}

    def test_columns_follow_rule(self):
        self.assertEqual(assign_columns(self.proc),
                         {"s1": 0, "s2": 0, "s3": 1, "k": 2, "s5": 4, "s6": 5, "s7": 6, "s8": 7, "s9": 8})

    def test_lane_heights_and_size(self):
        self.assertEqual([l["h"] for l in self.L["lanes"]], [180, 244, 180, 180, 106])
        self.assertEqual(self.L["lanes_bottom"], 890)
        self.assertEqual((self.L["width"], self.L["height"]), (1520, 996))
        self.assertEqual(self.L["schema"], 1)
        self.assertEqual(self.L["meta"]["subtitle"], "to-be · v0.2 · 2026-10-01 · fiktivní vzor pluginu process-mapping")

    def test_sound(self):
        assert_sound(self, self.L)

    def test_wires_avoid_other_cards(self):
        for w in self.L["wires"]:
            if w["kind"] == "state":
                continue
            others = [rect_of(c) for c in self.L["cards"] if c["id"] not in (w["src"], w["dst"])]
            self.assertFalse(path_hits(w["points"], others), w)

    def test_routes(self):
        self.assertEqual(wire(self.L, "s1", "s2")["route"], "v")
        self.assertEqual(wire(self.L, "s2", "s3")["points"], [[172, 282], [262, 282], [262, 159]])
        self.assertEqual(wire(self.L, "s3", "k")["route"], "hv")      # vh by ležela na čáře s2 → s3
        self.assertEqual(wire(self.L, "k", "s5")["points"], [[511, 396], [511, 526], [677, 526]])
        self.assertEqual(wire(self.L, "s7", "s8")["route"], "hv")     # vh by ležela na alternativě do limitu
        self.assertEqual(wire(self.L, "s8", "s9")["route"], "hv")

    def test_loop_alt_and_labels(self):
        loop = wire(self.L, "k", "s3")
        self.assertEqual(loop["points"], [[630, 232], [630, 34], [262, 34], [262, 45]])
        self.assertEqual((loop["label_pos"], loop["label_anchor"]), ([446, 28], "middle"))
        alt = wire(self.L, "s6", "s8")
        self.assertEqual((alt["kind"], alt["points"]), ("alt", [[926, 232], [926, 102], [1175, 102]]))
        main = wire(self.L, "s6", "s7")
        self.assertEqual((main["label"], main["label_anchor"], main["label_pos"]), ("nad limit", "start", [934, 523]))

    def test_timing(self):
        self.assertEqual(self.L["pace"], 1.0)
        self.assertEqual([self.cards[s.id]["t"] for s in self.proc.steps],
                         [0.5, 1.3, 2.1, 2.9, 5.6, 6.4, 7.2, 8.0, 8.8])
        self.assertEqual(wire(self.L, "s1", "s2")["t"], 0.8)
        self.assertEqual(wire(self.L, "s1", "s2")["tip_t"], 1.35)
        self.assertEqual(wire(self.L, "k", "s3")["t"], 4.1)
        self.assertEqual([it["t"] for it in self.cards["k"]["items"]], [3.3, 3.45, 3.6, 3.75])
        self.assertEqual(self.L["duration"], 9.9)

    def test_states(self):
        st = self.L["states"]
        self.assertEqual([p["lit_t"] for p in st["pills"]], [0.5, 5.6, 8.0, 8.8, 9.3])
        self.assertEqual([s["dx"] for s in st["ring"]["steps"]], [0, 302, 604, 906, 1208])
        self.assertTrue(st["in_order"])

    def test_labels_and_questions(self):
        labels = [self.cards[s.id]["label"] for s in self.proc.steps]
        self.assertEqual(labels, ["START", "KROK 1", "KROK 2", "KROK 3", "KROK 4", "KROK 5", "KROK 6", "KROK 7", "KONEC"])
        self.assertTrue(self.cards["s2"]["question"])
        self.assertFalse(self.cards["s7"]["question"])   # jen vyřešená otázka

    def test_span(self):
        sp = self.L["spans"][0]
        self.assertEqual((sp["x"], sp["y"], sp["w"]), (684, 814, 650))


class EdgeLayouts(unittest.TestCase):
    def test_base_spec_shares_column_and_falls_back(self):
        L = compute_layout(from_dict(base_spec()))
        self.assertEqual({c["id"]: c["col"] for c in L["cards"]}, {"x1": 0, "x2": 0, "x3": 1})
        self.assertEqual(wire(L, "x2", "x3")["route"], "hv")

    def test_empty_and_span_only_lanes(self):
        d = base_spec()
        d["lane"] += [{"id": "c", "name": "Dohled"}, {"id": "e", "name": "Prázdná"}]
        d["span"] = [{"lane": "c", "from": "x1", "to": "x3", "text": "dohled"}]
        L = compute_layout(from_dict(d))
        self.assertEqual([l["h"] for l in L["lanes"]], [180, 180, 106, 90])
        self.assertEqual((L["spans"][0]["x"], L["spans"][0]["w"]), (20, 318))
        self.assertIsNone(L["states"])
        self.assertEqual(L["height"], L["lanes_bottom"] + 16)

    def test_manual_col_is_respected(self):
        d = base_spec()
        d["step"][2]["col"] = 4
        L = compute_layout(from_dict(d))
        self.assertEqual(next(c for c in L["cards"] if c["id"] == "x3")["col"], 4)

    def test_out_of_order_states_are_flagged_but_ring_moves_forward(self):
        d = base_spec()
        d["state"] = [{"name": "B", "at": "x3"}, {"name": "A", "at": "x1"}]
        st = compute_layout(from_dict(d))["states"]
        self.assertFalse(st["in_order"])
        lits = [p["lit_t"] for p in st["pills"]]
        self.assertEqual(lits, sorted(lits))


class BigProcess(unittest.TestCase):
    def test_big_process_layout_is_sound_and_paced(self):
        L = compute_layout(from_dict(big_spec()))
        assert_sound(self, L)
        self.assertLess(L["pace"], 1.0)
        self.assertLessEqual(L["duration"], 15.0)
        self.assertEqual(len(L["cards"]), 32)
