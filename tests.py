import unittest
import bi

from utils.backdoors import get_all_units_from_backdoor, get_all_biunits_from_backdoor


class TestBackdoors(unittest.TestCase):
    def test_get_all_units_from_backdoor(self):
        self.assertEqual([-1, -2].sort(), get_all_units_from_backdoor([[1, 2, 3], [1, 2, -3]]).sort())

    def test_get_all_units_from_backdoor_empty(self):
        self.assertEqual(get_all_units_from_backdoor([]), [])

    def test_get_all_units_from_backdoor_hard(self):
        self.assertEqual([2].sort(), get_all_units_from_backdoor([[-1, 2, 3, 4], [1, 2, -3, 4], [-1, 2, -3, -4]]).sort())

    def test_get_all_biunits_from_backdoor(self):
        bi_units = get_all_biunits_from_backdoor([[1, 2, 3], [1, 2, -3]])
        cnfs = bi.all_sets_of_clauses(2)
        mapb = bi.get_map_to_dnf()
        for biunit in bi_units.values():
            bis = list(biunit)
            var_a = abs(bis[0][0])
            var_b = abs(bis[0][1])
            mapped = bi.map_values_from_cnf(var_a, var_b, bis)
            id_in_cnfs = -1
            mapped.sort()
            for i in range(len(cnfs)):
                cnfs[i].sort()
                if cnfs[i] == mapped:
                    id_in_cnfs = i
                    break
            direct_cnf = cnfs[mapb[id_in_cnfs]]
            direct_cnf = bi.map_values_to_cnf(var_a, var_b, direct_cnf)
            print(direct_cnf)
        # self.assertEqual([(-1, -2), (-1, 2), (1, -2)].sort(), get_all_biunits_from_backdoor([[1, 2, 3], [1, 2, -3]]).sort())

    def test_get_all_biunits_from_backdoor_empty(self):
        self.assertEqual(get_all_biunits_from_backdoor([]), [])

    def test_get_all_biunits_from_backdoor_hard(self):
        self.assertEqual([(-1, 2), (1, -2)].sort(), get_all_biunits_from_backdoor([[-1, 2, 3, 4], [1, 2, -3, 4], [-1, 2, -3, -4]]).sort())
