import unittest
from typing import List
import math
from probability_calculator.part import Outcome, _Part
from fractions import Fraction


class TestPart(unittest.TestCase):
    def test_str(self):
        part = _Part(0, 1, 2, 3, 4)
        self.assertEqual(str(part), "_Part(p=0, mean=1, square=2, min=3, max=4)")

    def test_eq(self):
        part1 = _Part(0, 1, 2, 3, 4)
        part2 = _Part(0, Fraction(5, 5), 2, 3, 4)
        self.assertEqual(part1, part2)

    def test_add(self):
        part1 = _Part(Fraction(1, 10), 3, 9, 2, 4)
        part2 = _Part(Fraction(2, 10), 8, 64, 7, 10)

        part = part1 + part2
        self.assertEqual(part._p, Fraction(2, 100))
        self.assertEqual(part._mean, 11)
        self.assertEqual(part._square, 121)
        self.assertEqual(part._min, 9)
        self.assertEqual(part._max, 14)

    def test_mul(self):
        part1 = _Part(Fraction(1, 10), 3, 9, 2, 4)
        part2 = _Part(Fraction(2, 10), 8, 64, 7, 10)

        part = part1 * part2
        self.assertEqual(part._p, Fraction(2, 100))
        self.assertEqual(part._mean, 24)
        self.assertEqual(part._square, 576)
        self.assertEqual(part._min, 14)
        self.assertEqual(part._max, 40)

    def test_outcomes(self):
        part = _Part(Fraction(1, 10), 1, Fraction(5, 3), 0, 2)
        outcomes = part.outcomes()
        self.assertEqual(outcomes, [{
            "p": Fraction(1, 30),
            "value": 0
        }, {
            "p": Fraction(1, 30),
            "value": 1
        }, {
            "p": Fraction(1, 30),
            "value": 2
        }])

    def test_outcomes2(self):
        part1 = _Part(Fraction(1, 10), 1, 1, 1, 1)
        part2 = _Part(Fraction(1, 5), 2, 4, 2, 2)
        part = _Part.merge([part1, part2])
        outcomes = part.outcomes()
        self.assertEqual(outcomes, [{
            "p": Fraction(1, 10),
            "value": 1
        }, {
            "p": Fraction(1, 5),
            "value": 2
        }])

    def test_merge(self):
        part1 = _Part(Fraction(1, 10), 1, 1, 1, 1)
        part2 = _Part(Fraction(1, 5), 2, 4, 2, 2)
        part = _Part.merge([part1, part2])

        self.assertEqual(part._p, Fraction(3, 10))
        self.assertEqual(part._mean, Fraction(5, 3))
        self.assertEqual(part._square, Fraction(3))
        self.assertEqual(part._min, Fraction(1))
        self.assertEqual(part._max, Fraction(2))

    def test_cdf(self):
        p0 = Fraction(0)
        p1 = Fraction(1, 5)
        part = _Part(p1, 1, 1, 1, 1)
        self.assertEqual(part.partial_cdf(0), (p0, p0))
        self.assertEqual(part.partial_cdf(1), (p1, p1))
        self.assertEqual(part.partial_cdf(2), (p1, p1))

    def test_cdf2(self):
        part = _Part(Fraction(1, 10), 3, 5, 1, 7)
        self.assertEqual(part.partial_cdf(0), (Fraction(0), Fraction(0)))
        self.assertEqual(part.partial_cdf(1), (Fraction(0), Fraction(4, 60)))
        self.assertEqual(part.partial_cdf(2), (Fraction(0), Fraction(4, 50)))
        self.assertEqual(part.partial_cdf(3), (Fraction(0), Fraction(1, 10)))
        self.assertEqual(part.partial_cdf(4), (Fraction(1, 30), Fraction(1, 10)))
        self.assertEqual(part.partial_cdf(7), (Fraction(4, 60), Fraction(1, 10)))
        self.assertEqual(part.partial_cdf(8), (Fraction(1, 10), Fraction(1, 10)))
