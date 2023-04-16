import math
import itertools
from typing import Optional, List
from .outcome import Outcome, ExportedOutcome, DiscreteOutcome
from .plot import plot_density


class DiscreteDensity:
    def __init__(self, outcomes: List[ExportedOutcome] = [], _outcomes: Optional[List[Outcome]] = None):
        self._outcomes: List[Outcome] = _outcomes if _outcomes is not None else [
        ]

        self._outcomes: List[Outcome] = self._outcomes + [DiscreteOutcome(
            value=o["value"], p=o["p"]) for o in outcomes]

        # TODO: this _outcomes-parameter in the constructor is really strange...
        self.simplify()

    def plot(self, **kwargs):
        """
        plots the density with matplotlib
        """
        return plot_density(self, **kwargs)

    def simplify(self):
        """
        simplifies the list of outcomes by combining elements
        """
        outcomes = sorted(self._outcomes, key=lambda o: o.get_value())
        new_outcomes: List[Outcome] = []
        last_outcome: Optional[Outcome] = None
        for o in outcomes:
            if last_outcome is not None and \
                isinstance(last_outcome, DiscreteOutcome) and \
                isinstance(o, DiscreteOutcome) and \
                math.isclose(last_outcome.get_value(),
                             o.get_value()):
                # two DiscreteOutcomes with the same value -> join together
                p = last_outcome.get_p() + o.get_p()
                last_outcome = DiscreteOutcome(value=last_outcome.get_value(), p=p)
                new_outcomes[-1] = last_outcome
            else:
                new_outcomes.append(o)
                last_outcome = o

        self._outcomes = new_outcomes

    def export_outcomes(self):
        outcomes: List[ExportedOutcome] = list(
            itertools.chain(*[o.export() for o in self._outcomes]))
        return outcomes

    def __mul__(self, other):
        outcomes = [o1 + o2 for o1 in self._outcomes for o2 in other._outcomes]
        return DiscreteDensity(_outcomes=outcomes)

    def __pow__(self, other):
        if isinstance(other, int):
            if other == 1:
                return self
            elif other > 1:
                return self * (self**(other - 1))

        return NotImplemented


class Die(DiscreteDensity):
    def __init__(self, n):
        """
        Generates a fair die with n sides
        """
        p = 1. / n  # TODO: rather use sympy?
        outcomes = [ExportedOutcome(value=i, p=p) for i in range(1, n + 1)]

        super().__init__(outcomes)
