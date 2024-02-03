import unittest

from utils.backdoors import get_all_units_from_backdoor, get_all_biunits_from_backdoor


class TestBackdoors(unittest.TestCase):
    def test_get_all_units_from_backdoor(self):
        self.assertEqual([-1, -2].sort(), get_all_units_from_backdoor([[1, 2, 3], [1, 2, -3]]).sort())

    def test_get_all_units_from_backdoor_empty(self):
        self.assertEqual(get_all_units_from_backdoor([]), [])

    def test_get_all_units_from_backdoor_hard(self):
        self.assertEqual([2].sort(), get_all_units_from_backdoor([[-1, 2, 3, 4], [1, 2, -3, 4], [-1, 2, -3, -4]]).sort())

    def test_get_all_biunits_from_backdoor(self):
        self.assertEqual([(-1, -2), (-1, 2), (1, -2)].sort(), get_all_biunits_from_backdoor([[1, 2, 3], [1, 2, -3]]).sort())

    def test_get_all_biunits_from_backdoor_empty(self):
        self.assertEqual(get_all_biunits_from_backdoor([]), [])

    def test_get_all_biunits_from_backdoor_hard(self):
        self.assertEqual([(-1, 2), (1, -2)].sort(), get_all_biunits_from_backdoor([[-1, 2, 3, 4], [1, 2, -3, 4], [-1, 2, -3, -4]]).sort())
