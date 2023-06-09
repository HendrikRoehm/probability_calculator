from typing import TypedDict, List, Union
from fractions import Fraction

Outcome = TypedDict("Outcome", {"p": Union[Fraction, int], "value": Union[Fraction, int]})


class _Part():
    def __init__(
            self, p: Union[Fraction, int],
            mean: Union[Fraction, int],
            square: Union[Fraction, int],
            min: Union[Fraction, int],
            max: Union[Fraction, int]):
        """
        p = probability
        mean = (partial expected_value) / p
        square = (partial second_moment) / p
        min = minimum value possible
        max = maximum value possible
        """
        self._p = Fraction(p)
        self._mean = Fraction(mean)
        self._square = Fraction(square)
        self._min = Fraction(min)
        self._max = Fraction(max)

#    def get_partial_expected(self):
#        return self._mean * self._p
#
#    def get_partial_second_moment(self):
#        return self._square * self._p

    def partial_cdf(self, value: Union[Fraction, int]) -> tuple[Fraction, Fraction]:
        """
        returns lower and upper bound on the (partial) cdf of the part
        """
        # TODO: Check correctness of formulas
        if value < self._min:
            return (Fraction(0), Fraction(0))
        elif value > self._max:
            return (self._p, self._p)
        elif self._min == self._max:
            return (self._p, self._p)
        elif value <= self._mean:
            return (Fraction(0), self._p * (self._max - self._mean) / (self._max - value))
        elif value <= self._max:
            return (self._p * (value - self._mean) / (value - self._min), self._p)
        else:
            raise Exception("something impossible occurred")

    def __str__(self) -> str:
        return f"_Part(p={self._p}, mean={self._mean}, square={self._square}, min={self._min}, max={self._max})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, _Part):
            return self._p == other._p \
                and self._mean == other._mean \
                and self._square == other._square \
                and self._min == other._min \
                and self._max == other._max

        return False

    def __add__(self, other):
        if not isinstance(other, _Part):
            return NotImplemented

        p = self._p * other._p
        mean = self._mean + other._mean
        square = self._square + other._square + 2 * self._mean * other._mean
        min = self._min + other._min
        max = self._max + other._max

        return _Part(p, mean, square, min, max)

    def __mul__(self, other):
        if not isinstance(other, _Part):
            return NotImplemented

        p = self._p * other._p
        mean = self._mean * other._mean
        square = self._square * other._square
        # FIXME: min and max are only correct for positive values
        min = self._min * other._min
        max = self._max * other._max

        return _Part(p, mean, square, min, max)

    def outcomes(self) -> List[Outcome]:
        if self._min == self._mean or self._max == self._mean:
            # only one point has all the probability
            return [{
                "p": self._p,
                "value": self._mean
            }]

        diff = (self._square - self._mean**2) / (self._max - self._min) * self._p
        p_min = diff / (self._mean - self._min)
        p_max = diff / (self._max - self._mean)
        p_mean = self._p - p_min - p_max

        outcomes = []
        if p_min != 0:
            outcomes.append({
                "p": p_min,
                "value": self._min
            })
        if p_mean != 0:
            outcomes.append({
                "p": p_mean,
                "value": self._mean
            })
        if p_max != 0:
            outcomes.append({
                "p": p_max,
                "value": self._max
            })

        return outcomes

    @staticmethod
    def merge(l: List['_Part']):
        if len(l) == 0:
            raise Exception("list needs elements to be merged")

        p = Fraction(0)
        ex = Fraction(0)
        exx = Fraction(0)
        min_value = l[0]._min
        max_value = l[0]._max
        for el in l:
            p += el._p
            ex += el._p * el._mean
            exx += el._p * el._square
            min_value = min(min_value, el._min)
            max_value = max(max_value, el._max)

        return _Part(
            p,
            ex / p,
            exx / p,
            min_value,
            max_value
        )
