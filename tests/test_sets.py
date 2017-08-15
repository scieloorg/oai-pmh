import unittest

from oaipmh import sets


class VirtualOffsetTranslationTests(unittest.TestCase):
    def test_case_1(self):
        self.assertEqual(sets.translate_virtual_offset(10, 0), 0)

    def test_case_2(self):
        self.assertEqual(sets.translate_virtual_offset(10, 0), 0)

    def test_case_3(self):
        self.assertEqual(sets.translate_virtual_offset(150, 0), 0)

    def test_case_4(self):
        self.assertEqual(sets.translate_virtual_offset(150, 101), 0)

