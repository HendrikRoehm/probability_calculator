from typing import TypedDict, List, Union
from fractions import Fraction
from math import log, sqrt, atan

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

        # consistensy check
        assert(self._mean >= self._min)
        assert(self._mean <= self._max)
        assert(self._square >= self._mean**2)
        assert(self._square <= self._mean**2 + (self._mean - self._min) * (self._max - self._mean))

#    def get_partial_expected(self):
#        return self._mean * self._p
#
#    def get_partial_second_moment(self):
#        return self._square * self._p

    def partial_cdf(self, value: Union[Fraction, int]) -> tuple[Fraction, Fraction]:
        """
        returns lower and upper bound on the (partial) cdf of the part
        """
        if value < self._min:
            return (Fraction(0), Fraction(0))

        d = self._square - self._mean**2
        if d == 0 or value >= self._max:
            # d == 0 is a corner case where there is no variance
            # should imply _min = _mean = _max
            return (self._p, self._p)

        # as d > 0, _max - _mean > 0 and _mean - _min > 0
        dmaxmean = self._max - self._mean
        bound1 = self._mean - d / dmaxmean
        dmeanvalue = self._mean - value
        if value <= bound1:
            return (Fraction(0), self._p /(1 + dmeanvalue**2 / d))

        dmeanmin = self._mean - self._min
        bound2 = self._mean + d / dmeanmin
        if value <= bound2:
            dmaxmin = self._max - self._min
            dmaxvalue = self._max - value
            dvaluemin = value - self._min
            com = (d - dmaxmean*dmeanvalue)/dmaxmin
            return (self._p*com/dvaluemin, self._p*(dmaxmean - com)/dmaxvalue)

        return (self._p / (1 + d / dmeanvalue**2), self._p)

    def cdf_uncertainty(self, exact_upper = True) -> float:
        """
        Computes the scaled integral between the upper and lower bound of the partial_cdf.
        For the real integral, one has to multiply by p.
        
        When the variance is maxed out and all probability is at the bounds,
        the theoretic integral would be 0. However, as we are using this as a
        heuristic, we give it a positive value if exact_upper is false.
        """
        d = self._square - self._mean**2
        dmaxmin = self._max - self._min
        if d == 0 or dmaxmin == 0:
            return 0.

        # as d > 0, _max - _mean > 0 and _mean - _min > 0
        dmaxmean = self._max - self._mean
        dmeanmin = self._mean - self._min
        dupper = dmaxmean * dmeanmin

        if d == dupper:
            # no variance as all probability is at the bounds
            if exact_upper:
                return 0.
            
            # as heuristic use a lower d
            d = d / 2

        # difference between bound1 and bound2
        I = log(float((dupper**2 + d**2  + d * (dmaxmean**2 + dmeanmin**2))/(dupper - d)**2))
        ret = I * float((dupper - d) / dmaxmin)
        
        # difference between bound2 and t_max
        fsqrtd = sqrt(float(d))
        ret += fsqrtd * (atan(-fsqrtd / float(dmeanmin)) - atan(float(-dmaxmean)/fsqrtd))

        # difference between t_min and bound1
        ret += fsqrtd * (atan(-fsqrtd / float(dmaxmean)) - atan(-float(dmeanmin)/fsqrtd))

        return ret

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

        # denominator limiting is required for a fast enough computation
        # however, the big denominator should result in a very small derivation
        # make sure that the rounding does not make probles with the numbers
        new_p = p.limit_denominator(max_denominator=1000_000_000_000_000_000_000_000_000)
        new_ex = (ex / p).limit_denominator(max_denominator=1000_000)
        new_ex = max(new_ex, min_value)
        new_ex = min(new_ex, max_value)
        new_exx = (exx / p).limit_denominator(max_denominator=1000_000)
        new_exx = max(new_exx, new_ex**2)
        new_exx = min(new_exx, new_ex**2 + (max_value - new_ex)*(new_ex - min_value))

        return _Part(
            new_p,
            new_ex,
            new_exx,
            min_value,
            max_value
        )
