import unittest

from src.helpers import hms_to_s


class TestHelpers(unittest.TestCase):
    def test_hms_to_s(self):
        self.assertEqual(hms_to_s('0:10'), 10)
        self.assertEqual(hms_to_s('1:10'), 70)
        self.assertEqual(hms_to_s('70:00'), 4200)
        self.assertEqual(hms_to_s('1:10:00'), 4200)
