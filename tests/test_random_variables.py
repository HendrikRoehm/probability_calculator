import unittest
from fractions import Fraction
from probability_calculator.random_variables import RandomVariable, FairDie


class TestRandomVariables(unittest.TestCase):
    def test_outcomes(self):
        var = RandomVariable(outcomes=[
            {"p": Fraction(1, 6), "value": 1},
            {"p": Fraction(1, 3), "value": 2},
            {"p": Fraction(1, 6), "value": 1},
            {"p": Fraction(1, 3), "value": 3}
        ])
        expected = [
            {"p": Fraction(1, 3), "value": 1},
            {"p": Fraction(1, 3), "value": 2},
            {"p": Fraction(1, 3), "value": 3}
        ]
        self.assertEqual(var.outcomes(), expected)

    def test_add(self):
        var1 = RandomVariable(outcomes=[
            {"p": Fraction(1, 10), "value": 1},
            {"p": Fraction(3, 10), "value": 2}]
        )
        var2 = RandomVariable(outcomes=[
            {"p": Fraction(4, 10), "value": 4},
            {"p": Fraction(8, 10), "value": 8}]
        )
        var = var1 + var2
        outcomes = var.outcomes()
        expected = [
            {"p": Fraction(4, 100), "value": 5},
            {"p": Fraction(12, 100), "value": 6},
            {"p": Fraction(8, 100), "value": 9},
            {"p": Fraction(24, 100), "value": 10}
        ]

        self.assertEqual(outcomes, expected)

    def test_mul(self):
        var1 = RandomVariable(outcomes=[
            {"p": Fraction(1, 10), "value": 1},
            {"p": Fraction(3, 10), "value": 2}]
        )
        var2 = RandomVariable(outcomes=[
            {"p": Fraction(4, 10), "value": 4},
            {"p": Fraction(8, 10), "value": 8}]
        )
        var = var1 * var2
        outcomes = var.outcomes()
        expected = [
            {"p": Fraction(4, 100), "value": 4},
            {"p": Fraction(20, 100), "value": 8},
            {"p": Fraction(24, 100), "value": 16}
        ]

        self.assertEqual(outcomes, expected)

    def test_mul2(self):
        var1 = RandomVariable(outcomes=[
            {"p": Fraction(1, 10), "value": 1},
            {"p": Fraction(3, 10), "value": 2}]
        )
        self.assertEqual((var1 * 2).outcomes(), (var1 + var1).outcomes())

    def test_mul3(self):
        var1 = RandomVariable(outcomes=[
            {"p": Fraction(1, 10), "value": 1},
            {"p": Fraction(3, 10), "value": 2}]
        )
        self.assertEqual((3 * var1).outcomes(), (var1 + var1 + var1).outcomes())

    def test_fairdie(self):
        var = FairDie(3)
        expected = [
            {"p": Fraction(1, 3), "value": 1},
            {"p": Fraction(1, 3), "value": 2},
            {"p": Fraction(1, 3), "value": 3}
        ]
        self.assertEqual(var.outcomes(), expected)
