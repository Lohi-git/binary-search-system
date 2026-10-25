import math
import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from search import binary_search, first_occurrence, last_occurrence, linear_cost, record_steps

FUNCS = {"any": binary_search, "first": first_occurrence, "last": last_occurrence}


class SearchTests(unittest.TestCase):
    def setUp(self):
        self.rng = random.Random(77)

    def rand_case(self):
        a = sorted(self.rng.randint(1, 30) for _ in range(self.rng.randint(1, 25)))
        return a, self.rng.randint(0, 32)

    def test_against_brute_force(self):
        for _ in range(300):
            a, t = self.rand_case()
            if t in a:
                self.assertEqual(a[binary_search(a, t)], t)
                self.assertEqual(first_occurrence(a, t), a.index(t))
                self.assertEqual(last_occurrence(a, t), len(a) - 1 - a[::-1].index(t))
            else:
                self.assertEqual(binary_search(a, t), -1)

    def test_steps_match_functions_and_stay_logarithmic(self):
        for mode, fn in FUNCS.items():
            for _ in range(150):
                a, t = self.rand_case()
                end = record_steps(a, t, mode)[-1]
                self.assertEqual(end["res"], fn(a, t))
                self.assertLessEqual(end["c"], math.ceil(math.log2(len(a) + 1)))

    def test_linear_cost(self):
        self.assertEqual(linear_cost([1, 2, 3, 4], 3, "any"), 3)
        self.assertEqual(linear_cost([1, 2, 3, 4], 9, "any"), 4)
        self.assertEqual(linear_cost([1, 2, 3, 4], 1, "last"), 4)


if __name__ == "__main__":
    unittest.main()
