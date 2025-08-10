import itertools
from fractions import Fraction
from typing import List, Literal, Union
from . import numeric_part
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import time
from math import log, exp, inf
from numpy import logaddexp

class NumericRandomVariable:
    def __init__(self, outcomes: List[numeric_part.NumericOutcome] = [], _parts: List[numeric_part._Part] = []):
        parts = []
        for p in _parts:
            parts.append(p)
        for outcome in outcomes:
            p = outcome["p"]
            value = outcome["value"]
            parts.append(numeric_part._Part(
                log(p),
                value,
                value**2,
                value,
                value
            ))

        self._parts = NumericRandomVariable._simplifyParts(parts)

    def outcomes(self):
        outcomes: List[numeric_part.NumericOutcome] = list(
            itertools.chain(*[part.outcomes() for part in self._parts]))
        return outcomes

    def cdf(self, value: float) -> tuple[float, float]:
        """
        returns lower and upper bounds on the cumulative distribution function of the random variable
        """
        lower = -inf
        upper = -inf
        for part in self._parts:
            if part._min > value:
                break

            (l, u) = part.partial_logcdf(value)
            lower = logaddexp(lower, l)
            upper = logaddexp(upper, u)

        return (exp(lower), exp(upper))

    def __add__(self, other):
        start = time.time()
        parts = []
        for part1 in self._parts:
            for part2 in other._parts:
                parts.append(part1 + part2)
        #print("array generate %s" % (time.time() - start))
        start2 = time.time()
        ret = NumericRandomVariable(_parts=parts)
        #print("instantiate var %s" % (time.time() - start2))
        #print("add %s" % (time.time() - start))
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
        elif not isinstance(other, NumericRandomVariable):
            raise NotImplemented

        parts = []
        for part1 in self._parts:
            for part2 in other._parts:
                parts.append(part1 * part2)
        return NumericRandomVariable(_parts=parts)

    def _minmax(self) -> tuple[float, float]:
        min_value = self._parts[0]._min
        max_value = self._parts[0]._max
        for part in self._parts:
            min_value = min(part._min, min_value)
            max_value = max(part._max, max_value)
        return (min_value, max_value)

    def split(self, threshold: float) -> tuple["NumericRandomVariable", "NumericRandomVariable"]:
        """
        Splits the random variable into two parts, one with part means <= threshold and one with part means > threshold
        """
        lower_parts = []
        upper_parts = []
        for part in self._parts:
            if part._mean <= threshold:
                lower_parts.append(part)
            else:
                upper_parts.append(part)

        return (NumericRandomVariable(_parts=lower_parts), NumericRandomVariable(_parts=upper_parts))

    def pscale(self, pfactor: float) -> "NumericRandomVariable":
        logpfactor = log(pfactor)
        scaled_parts = []
        for part in self._parts:
            part._logp += logpfactor
            scaled_parts.append(part)
        return NumericRandomVariable(_parts=scaled_parts)

    def concat(self, other: "NumericRandomVariable") -> "NumericRandomVariable":
        """
        Concatenates two random variables, i.e. adds the parts of the other random variable to this one
        """
        parts = self._parts + other._parts
        return NumericRandomVariable(_parts=parts)

    def plot_outcomes(
            self,
            xscale: Literal["linear", "log"] = "linear",
            yscale: Literal["linear", "log"] = "linear",
            ignore_tails_p: Union[Fraction, int, float] = 0):
        outcomes = sorted(self.outcomes(), key=lambda o: o["value"])
        sum_p = 0.
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
            lower_value: Union[float, None] = None,
            upper_value: Union[float, None] = None):

        fig, ax = plt.subplots()
        ax.set_xscale(xscale)
        ax.set_yscale(yscale)

        min_value, max_value = self._minmax()
        if upper_value is not None:
            max_value = upper_value
        if lower_value is not None:
            min_value = lower_value
        delta = (max_value - min_value) / steps
        delta_float = float(delta)
        last_value = min_value
        last_lower = 0.
        last_upper = 0.
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
            upper_value: Union[float, None] = None,
            lower_value: Union[float, None] = None,
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
    def _simplifyParts(parts: List[numeric_part._Part]) -> List[numeric_part._Part]:
        def heuristic(part1: numeric_part._Part, part2: numeric_part._Part, merged: numeric_part._Part):
            value = merged.cdf_uncertainty(exact_upper=False)
            value -= exp(part1._logp - mergedPart._logp) * part1.cdf_uncertainty()
            value -= exp(part2._logp - mergedPart._logp) * part2.cdf_uncertainty()
            return exp(merged._logp) * value

        goalPartCount = 200
        if len(parts) > goalPartCount:
            sortedParts = sorted(parts, key=lambda part: part._mean)
            mergeBounds = []
            i = 1
            currentPart = sortedParts[0]
            while i < len(sortedParts):
                nextPart = sortedParts[i]
                mergedPart = numeric_part._Part.merge(currentPart, nextPart)

                mergeBounds.append(heuristic(currentPart, nextPart, mergedPart))
                currentPart = nextPart
                i += 1

            sortedBounds = sorted(mergeBounds)
            bound = sortedBounds[-goalPartCount]

            simplifiedParts = []
            i = 1
            currentPart = sortedParts[0]
            while i < len(sortedParts):
                nextPart = sortedParts[i]
                mergedPart = numeric_part._Part.merge(currentPart, nextPart)

                isMerge = heuristic(currentPart, nextPart, mergedPart) <= bound
                if isMerge:
                    currentPart = mergedPart
                else:
                    simplifiedParts.append(currentPart)
                    currentPart = nextPart

                i += 1

            simplifiedParts.append(currentPart)

            if len(simplifiedParts) > 1.1 * goalPartCount:
                return NumericRandomVariable._simplifyParts(simplifiedParts)

        else:
            simplifiedParts = parts[:]

        return sorted(simplifiedParts, key=lambda p: p._min)


class FairDie(NumericRandomVariable):
    def __init__(self, n):
        """
        Generates a fair die with n sides
        """
        p = 1./ n
        outcomes = [numeric_part.NumericOutcome(p=p, value=i) for i in range(1, n + 1)]

        super().__init__(outcomes)
