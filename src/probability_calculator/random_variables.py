import itertools
from fractions import Fraction
from typing import List, Literal, Union
from . import part
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import time

class RandomVariable:
    def __init__(self, outcomes: List[part.Outcome] = [], _parts: List[part._Part] = []):
        parts = []
        for p in _parts:
            parts.append(p)
        for outcome in outcomes:
            p = outcome["p"]
            value = outcome["value"]
            parts.append(part._Part(
                p,
                value,
                value**2,
                value,
                value
            ))

        self._parts = RandomVariable._simplifyParts(parts)

    def outcomes(self):
        outcomes: List[part.Outcome] = list(
            itertools.chain(*[part.outcomes() for part in self._parts]))
        return outcomes

    def mean(self) -> Fraction:
        mean = Fraction(0)
        for part in self._parts:
            mean += part._mean * part._p
        return mean
    
    def square(self) -> Fraction:
        square = Fraction(0)
        for part in self._parts:
            square += part._square * part._p
        return square

    def cdf(self, value: Union[Fraction, int]) -> tuple[Fraction, Fraction]:
        """
        returns lower and upper bounds on the cumulative distribution function of the random variable
        """
        lower = Fraction(0)
        upper = Fraction(0)
        for part in self._parts:
            if part._min > value:
                break

            (l, u) = part.partial_cdf(value)
            lower += l
            upper += u

        return (lower, upper)

    def quantil(self, q: Fraction):
        # TODO: use lower and upper bound, this is not really correct
        sum = Fraction(0, 1)
        for part in self._parts:
            sum += part._p
            if sum > q:
                return part._min

        return self._minmax()[1]

    def __add__(self, other):
        start = time.time()
        parts = []
        for part1 in self._parts:
            for part2 in other._parts:
                parts.append(part1 + part2)
        ret = RandomVariable(_parts=parts)
        print("add %s" % (time.time() - start))
        return ret

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
                res = self + self * (other - 1)
                print("mul", other, len(res._parts))
                return res
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
            steps=101,
            upper_value: Union[Fraction, None] = None):

        fig, ax = plt.subplots()
        ax.set_xscale(xscale)
        ax.set_yscale(yscale)

        min_value, max_value = self._minmax()
        if upper_value is not None:
            max_value = upper_value
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
            ax.set_ylim(bottom=0, top=1)
        plt.show()
        plt.close()
        return fig, ax

    def plot_quantils(
            self,
            steps=101,
            upper_value: Union[Fraction, None] = None,
            lower_value: Union[Fraction, None] = None,
            fixed_pscale=True):

        fig, ax = plt.subplots()
        min_value, max_value = self._minmax()
        if upper_value is not None:
            max_value = upper_value
        if lower_value is not None:
            min_value = lower_value
        delta = (max_value - min_value) / steps
        delta_float = float(delta)

        last_value = min_value
        x = []
        y = []
        lx = []
        ly = []
        ux = []
        uy = []
        while last_value < max_value:
            current_value = last_value + delta
            (current_lower, current_upper) = self.cdf(current_value)

            value_float = float(current_value)
            current_p = float(current_lower / 2 + current_upper / 2)
            x.append(value_float)
            y.append(current_p)
            
            lower_float = float(current_lower)
            lx.append(lower_float)
            ly.append(value_float)
            lx.append(lower_float)
            ly.append(value_float + delta_float)

            upper_float = float(current_upper)
            ux.append(upper_float)
            uy.append(value_float - delta_float)
            ux.append(upper_float)
            uy.append(value_float)
            #ax.vlines(
            #    float(current_lower),
            #    value_float,
            #    value_float + delta_float,
            #    color="red"
            #)
            #ax.vlines(
            #    float(current_upper),
            #    value_float - delta_float,
            #    value_float,
            #    color="black"
            #)

            last_value = current_value

        ax.margins(0.01)
        ax.autoscale()
        if fixed_pscale:
            ax.set_xlim(left=0, right=1)
        plt.plot(lx, ly, color="blue", alpha=0.2)
        plt.plot(ux, uy, color="blue", alpha=0.2)
        plt.plot(y, x, color="blue")
        plt.show()
        plt.close()

        if lower_value is not None:
            print(f"P(value < {lower_value}) ∈ [{lx[0]:.8f}, {ux[0]:.8f}]")
        if upper_value is not None:
            print(f"P(value > {upper_value}) ∈ [{1-ux[-1]:.8f}, {1-lx[-1]:.8f}]")

        return fig, ax

    @ staticmethod
    def _simplifyParts(parts: List[part._Part]) -> List[part._Part]:
        def heuristic(part1: part._Part, part2: part._Part, merged: part._Part):
            value = merged.cdf_uncertainty(exact_upper=False)
            value -= float(part1._p / mergedPart._p) * part1.cdf_uncertainty()
            value -= float(part2._p / mergedPart._p) * part2.cdf_uncertainty()
            return float(merged._p) * value

        goalPartCount = 800
        if len(parts) > goalPartCount:
            sortedParts = sorted(parts, key=lambda part: part._mean)
            mergeBounds = []
            i = 1
            currentPart = sortedParts[0]
            while i < len(sortedParts):
                nextPart = sortedParts[i]
                mergedPart = part._Part.merge([currentPart, nextPart])

                mergeBounds.append(heuristic(currentPart, nextPart, mergedPart))
                currentPart = nextPart
                i += 1

            # we want to merge the parts with a small heuristic value to change the least amount possible
            sortedBounds = sorted(mergeBounds)
            bound = sortedBounds[-goalPartCount]

            simplifiedParts = []
            i = 1
            currentPart = sortedParts[0]
            while i < len(sortedParts):
                nextPart = sortedParts[i]
                mergedPart = part._Part.merge([currentPart, nextPart])

                isMerge = heuristic(currentPart, nextPart, mergedPart) <= bound
                if isMerge:
                    currentPart = mergedPart
                else:
                    simplifiedParts.append(currentPart)
                    currentPart = nextPart

                i += 1

            simplifiedParts.append(currentPart)

            if len(simplifiedParts) > 1.1 * goalPartCount:
                return RandomVariable._simplifyParts(simplifiedParts)

        else:
            simplifiedParts = parts[:]

        return sorted(simplifiedParts, key=lambda p: p._min)


class FairDie(RandomVariable):
    def __init__(self, n):
        """
        Generates a fair die with n sides
        """
        p = Fraction(1, n)
        outcomes = [part.Outcome(p=p, value=i) for i in range(1, n + 1)]

        super().__init__(outcomes)
