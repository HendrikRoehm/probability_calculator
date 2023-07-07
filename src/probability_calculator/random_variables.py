import itertools
from fractions import Fraction
from typing import List, Literal
from .part import Outcome, _Part
import matplotlib.pyplot as plt


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
                return self + self * (other - 1)
        elif not isinstance(other, RandomVariable):
            raise NotImplemented

        parts = []
        for part1 in self._parts:
            for part2 in other._parts:
                parts.append(part1 * part2)
        return RandomVariable(_parts=parts)

    def plot_outcomes(
            self,
            xscale: Literal["linear", "log"] = "linear",
            yscale: Literal["linear", "log"] = "linear"):
        outcomes = self.outcomes()
        x = [o["value"] for o in outcomes]
        y = [o["p"] for o in outcomes]
        fig, ax = plt.subplots()
        ax.set_xscale(xscale)
        ax.set_yscale(yscale)
        ax.plot(x, y, "o", ms=4, alpha=0.7)
        if yscale == "linear":
            ax.set_ylim(bottom=0)
        plt.show()
        plt.close()
        return fig, ax

    @staticmethod
    def _simplifyParts(parts: List[_Part]):
        sortedParts = sorted(parts, key=lambda part: part._min)
        simplifiedParts = []

        i = 0
        while i < len(sortedParts):
            part = sortedParts[i]
            j = i + 1
            while j < len(sortedParts):
                nextPart = sortedParts[j]
                if nextPart._min != part._min or nextPart._max != part._max:
                    break

                j += 1

            selectedParts = sortedParts[i:j]
            simplifiedParts.append(_Part.merge(selectedParts))
            i = j

        return simplifiedParts


class FairDie(RandomVariable):
    def __init__(self, n):
        """
        Generates a fair die with n sides
        """
        p = Fraction(1, n)
        outcomes = [Outcome(p=p, value=i) for i in range(1, n + 1)]

        super().__init__(outcomes)
