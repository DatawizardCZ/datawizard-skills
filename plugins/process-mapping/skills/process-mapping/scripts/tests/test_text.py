import unittest

from pmaplib.text import SUB_PX, TITLE_PX, WARN_PX, chars_for, wrap


class Wrap(unittest.TestCase):
    def test_widths_match_card(self):
        self.assertEqual(chars_for(128, TITLE_PX), 17)
        self.assertEqual(chars_for(128, SUB_PX), 21)
        self.assertEqual(chars_for(294, WARN_PX), 47)

    def test_wraps_on_words(self):
        self.assertEqual(wrap("dodavatel, částka, splatnost", 21), ["dodavatel, částka,", "splatnost"])

    def test_empty(self):
        self.assertEqual(wrap("", 10), [])

    def test_long_word_stays_whole_and_terminates(self):
        lines = wrap("https://example.com/velmi/dlouha/adresa/bez/mezer krok", 12)
        self.assertEqual(lines, ["https://example.com/velmi/dlouha/adresa/bez/mezer", "krok"])
