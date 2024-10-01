from typing import TypedDict, List
from math import log, sqrt, atan, inf, exp
from numpy import logaddexp

NumericOutcome = TypedDict("NumericOutcome", {"p": float, "value": float})


class _Part():
    def __init__(
            self, logp: float,
            mean: float,
            square: float,
            min: float,
            max: float):
        """
        p = probability
        mean = (partial expected_value) / p
        square = (partial second_moment) / p
        min = minimum value possible
        max = maximum value possible
        """
        self._logp = logp
        self._mean = mean
        self._square = square
        self._min = min
        self._max = max

        # consistensy check
        assert(self._mean >= self._min)
        assert(self._mean <= self._max)
        assert(self._square >= self._mean**2)
        assert(self._square <= self._mean**2 + (self._mean - self._min) * (self._max - self._mean))

    def partial_logcdf(self, value: float) -> tuple[float, float]:
        """
        returns lower and upper bound on the (partial) log cdf of the part
        """
        if value < self._min:
            return (-inf, -inf)

        d = self._square - self._mean**2
        if d <= 0 or value >= self._max:
            # d == 0 is a corner case where there is no variance
            # should imply _min = _mean = _max
            return (self._logp, self._logp)

        # as d > 0, _max - _mean > 0 and _mean - _min > 0
        dmaxmean = self._max - self._mean
        bound1 = self._mean - d / dmaxmean
        dmeanvalue = self._mean - value
        if value <= bound1:
            return (-inf, self._logp - log(1 + dmeanvalue**2 / d))

        dmeanmin = self._mean - self._min
        bound2 = self._mean + d / dmeanmin
        if value <= bound2:
            dmaxmin = self._max - self._min
            dmaxvalue = self._max - value
            dvaluemin = value - self._min
            com = (d - dmaxmean*dmeanvalue)/dmaxmin
            return (self._logp+log(com/dvaluemin), self._logp+log((dmaxmean - com)/dmaxvalue))

        return (self._logp - log(1 + d / dmeanvalue**2), self._logp)

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
        if d <= 0 or dmaxmin <= 0:
            return 0.

        # as d > 0, _max - _mean > 0 and _mean - _min > 0
        dmaxmean = self._max - self._mean
        dmeanmin = self._mean - self._min
        dupper = dmaxmean * dmeanmin

        if d >= dupper:
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
        return f"_Part(logp={self._logp}, mean={self._mean}, square={self._square}, min={self._min}, max={self._max})"

    def __eq__(self, other: object) -> bool:
        # FIXME: use isclose
        if isinstance(other, _Part):
            return self._logp == other._logp \
                and self._mean == other._mean \
                and self._square == other._square \
                and self._min == other._min \
                and self._max == other._max

        return False

    def __add__(self, other):
        if not isinstance(other, _Part):
            return NotImplemented

        logp = self._logp + other._logp
        mean = self._mean + other._mean
        square = self._square + other._square + 2 * self._mean * other._mean
        min_value = self._min + other._min
        max_value = self._max + other._max

        # make sure that the rounding does not make probles with the numbers
        # TODO: Make check in constructor, if error is small, the correct
        # if error is big, then print warning
        mean = max(mean, min_value)
        mean = min(mean, max_value)
        square = max(square, mean**2)
        square = min(square, mean**2 + (max_value - mean)*(mean - min_value))

        return _Part(logp, mean, square, min_value, max_value)

    def __mul__(self, other):
        if not isinstance(other, _Part):
            return NotImplemented

        p = self._logp + other._logp
        mean = self._mean * other._mean
        square = self._square * other._square
        # FIXME: min and max are only correct for positive values
        min = self._min * other._min
        max = self._max * other._max

        return _Part(p, mean, square, min, max)

    def outcomes(self) -> List[NumericOutcome]:
        if self._min == self._mean or self._max == self._mean:
            # only one point has all the probability
            return [{
                "p": exp(self._logp),
                "value": self._mean
            }]

        diff = (self._square - self._mean**2) / (self._max - self._min)
        p = exp(self._logp)
        p_min = p * diff / (self._mean - self._min)
        p_max = diff / (self._max - self._mean)
        p_mean = p - p_min - p_max

        outcomes = []
        if p_min > 0:
            outcomes.append({
                "p": p_min,
                "value": self._min
            })
        if p_mean > 0:
            outcomes.append({
                "p": p_mean,
                "value": self._mean
            })
        if p_max > 0:
            outcomes.append({
                "p": p_max,
                "value": self._max
            })

        return outcomes

    @staticmethod
    def merge(part1, part2):
        min_value = min(part1._min, part2._min)
        max_value = max(part1._max, part2._max)
        logp = logaddexp(part1._logp, part2._logp)
        factor1 = exp(part1._logp - logp)
        factor2 = exp(part2._logp - logp)
        ex = factor1 * part1._mean + factor2 * part2._mean
        exx = factor1 * part1._square + factor2 * part2._square

        # make sure that the rounding does not make problems with the numbers
        ex = max(ex, min_value)
        ex = min(ex, max_value)
        exx = max(exx, ex**2)
        exx = min(exx, ex**2 + (max_value - ex)*(ex - min_value))

        return _Part(
            logp,
            ex,
            exx,
            min_value,
            max_value
        )
