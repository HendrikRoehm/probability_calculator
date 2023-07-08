import itertools
from fractions import Fraction
from typing import List, Literal, Union
from .part import Outcome, _Part
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


class RandomVariable:
    def __init__(self, outcomes: List[Outcome] = [], _parts: List[_Part] = []):
        parts = []
        for part in _parts:
            parts.append(part)
        for outcome in outcomes:
            p = outcome["p"]
            value = outcome["value"]
            parts.append(_Part(
                p,
                value,
                value**2,
                value,
                value
            ))

        self._parts = RandomVariable._simplifyParts(parts)

    def outcomes(self):
        outcomes: List[Outcome] = list(
            itertools.chain(*[part.outcomes() for part in self._parts]))
        return outcomes

    def cdf(self, value: Union[Fraction, int]) -> tuple[Fraction, Fraction]:
        """
        returns lower and upper bounds on the cumulative distribution function of the random variable
        """
        lower = Fraction(0)
        upper = Fraction(0)
        for part in self._parts:
            (l, u) = part.partial_cdf(value)
            lower += l
            upper += u

        return (lower, upper)

    def __add__(self, other):
        parts = []
        for part1 in self._parts:
            for part2 in other._parts:
                parts.append(part1 + part2)
        return RandomVariable(_parts=parts)

    def __rmul__(self, other):
        if not isinstance(other, int):
            raise NotImplementedError

        return self * other

    def __mul__(self, other):
        if isinstance(other, int):
            if other <= 0:
                raise NotImplementedError
            elif other == 1:
                return self
            else:
                # TODO: use logarithmic approach for solving
                return self + self * (other - 1)
        elif not isinstance(other, RandomVariable):
            raise NotImplemented

        parts = []
        for part1 in self._parts:
            for part2 in other._parts:
                parts.append(part1 * part2)
        return RandomVariable(_parts=parts)

    def _minmax(self) -> tuple[Fraction, Fraction]:
        min_value = self._parts[0]._min
        max_value = self._parts[0]._max
        for part in self._parts:
            min_value = min(part._min, min_value)
            max_value = max(part._max, max_value)
        return (min_value, max_value)

    def plot_outcomes(
            self,
            xscale: Literal["linear", "log"] = "linear",
            yscale: Literal["linear", "log"] = "linear",
            ignore_tails_p: Union[Fraction, int, float] = 0):
        outcomes = sorted(self.outcomes(), key=lambda o: o["value"])
        sum_p = Fraction(0)
        x = []
        y = []
        for o in outcomes:
            sum_p = o["p"]
            if sum_p <= ignore_tails_p or sum_p >= 1 - ignore_tails_p:
                continue

            x.append(o["value"])
            y.append(o["p"])

        fig, ax = plt.subplots()
        ax.set_xscale(xscale)
        ax.set_yscale(yscale)
        ax.plot(x, y, "o", ms=4, alpha=0.7)
        if yscale == "linear":
            ax.set_ylim(bottom=0)
        plt.show()
        plt.close()
        return fig, ax

    def plot_histogram(
            self,
            xscale: Literal["linear", "log"] = "linear",
            yscale: Literal["linear", "log"] = "linear",
            cumulative: bool = False,
            steps=101):

        fig, ax = plt.subplots()
        ax.set_xscale(xscale)
        ax.set_yscale(yscale)

        (min_value, max_value) = self._minmax()
        delta = (max_value - min_value) / steps
        delta_float = float(delta)
        last_value = min_value
        last_lower = Fraction(0)
        last_upper = Fraction(0)
        while last_value < max_value:
            current_value = last_value + delta
            (current_lower, current_upper) = self.cdf(current_value)

            xmin = float(last_value)
            xmax = xmin + delta_float
            value = float(current_lower / 2 + current_upper / 2) if cumulative else \
                float(current_lower / 2 + current_upper / 2 - last_lower / 2 - last_upper / 2)
            ax.add_patch(Rectangle((xmin, 0), delta_float, value))
            ax.hlines(
                float(current_lower) if cumulative else float(current_lower - last_upper),
                xmin,
                xmax,
                color="red"
            )
            ax.hlines(
                float(current_upper) if cumulative else max(0, float(current_upper - last_lower)),
                xmin,
                xmax,
                color="black"
            )

            last_value = current_value
            last_lower = current_lower
            last_upper = current_upper

        ax.margins(0.01)
        ax.autoscale()
        if yscale == "linear":
            ax.set_ylim(bottom=0)
        plt.show()
        plt.close()
        return fig, ax

    @ staticmethod
    def _simplifyParts(parts: List[_Part]) -> List[_Part]:
        sortedParts = sorted(parts, key=lambda part: part._min)
        simplifiedParts = []

        i = 1
        currentPart = sortedParts[0]
        while i < len(sortedParts):
            part = sortedParts[i]

            p = currentPart._p + part._p
            min_value = min(currentPart._min, part._min)
            max_value = max(currentPart._max, part._max)

            # isMerge = p * (max_value - min_value) < 1e-5
            isMerge = (max_value - min_value) <= 1
            if isMerge:
                currentPart = _Part.merge([currentPart, part])
            else:
                simplifiedParts.append(currentPart)
                currentPart = part

            i += 1

        simplifiedParts.append(currentPart)

        return simplifiedParts


class FairDie(RandomVariable):
    def __init__(self, n):
        """
        Generates a fair die with n sides
        """
        p = Fraction(1, n)
        outcomes = [Outcome(p=p, value=i) for i in range(1, n + 1)]

        super().__init__(outcomes)
