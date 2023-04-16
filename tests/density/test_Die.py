import unittest
from probability_calculator.density import Die


class TestDie(unittest.TestCase):
    def test_die3(self):
        d = Die(3)
        expected = [
            {"value": 1, "p": 1. / 3},
            {"value": 2, "p": 1. / 3},
            {"value": 3, "p": 1. / 3}
        ]
        assert d.export_outcomes() == expected

    def test_die6(self):
        d = Die(6)
        expected = [
            {"value": 1, "p": 1. / 6},
            {"value": 2, "p": 1. / 6},
            {"value": 3, "p": 1. / 6},
            {"value": 4, "p": 1. / 6},
            {"value": 5, "p": 1. / 6},
            {"value": 6, "p": 1. / 6}
        ]
        assert d.export_outcomes() == expected

    def test_die2_sum(self):
        d = Die(2)
        expected = [
            {"value": 3, "p": 1. / 8},
            {"value": 4, "p": 3. / 8},
            {"value": 5, "p": 3. / 8},
            {"value": 6, "p": 1. / 8}
        ]
        assert (d**3).export_outcomes() == expected

    def test_die3_sum(self):
        d = Die(3)
        expected = [
            {"value": 2, "p": 1. / 9},
            {"value": 3, "p": 2. / 9},
            {"value": 4, "p": 3. / 9},
            {"value": 5, "p": 2. / 9},
            {"value": 6, "p": 1. / 9}
        ]
        assert (d*d).export_outcomes() == expected