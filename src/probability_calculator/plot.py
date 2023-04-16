from typing import Optional, Tuple, List, Literal
import math
import matplotlib.pyplot as plt
import numpy as np
import scipy as sp
from .outcome import ExportedOutcome


def plot_density(
        density,
        xscale: Literal["linear", "log"] = "linear",
        yscale: Literal["linear", "log"] = "linear",
        kde=False,
        gridsize: int = 1000,
        **args):
    outcomes = density.export_outcomes()
    x, y = get_plot_data(outcomes, **args)

    if kde:
        x, y = kernel_density_estimation(
            x, y, gridsize=gridsize)

    fig, ax = plt.subplots()
    ax.set_xscale(xscale)
    ax.set_yscale(yscale)
    ax.plot(x, y, "o" if not kde else "-")
    if yscale == "linear":
        ax.set_ylim(bottom=0)
    plt.show()
    plt.close()
    return fig, ax


def get_plot_data(outcomes: List[ExportedOutcome], merge_tol=1e-6) -> Tuple[List[float], List[float]]:
    points = [(o["value"], o["p"]) for o in outcomes]

    x: List[float] = []
    y: List[float] = []
    last_value = None
    for value, p in sorted(points):
        if last_value is not None and math.isclose(value, last_value, abs_tol=merge_tol):
            # multiple times the same point -> add probabilities together
            y[-1] += p
        else:
            x.append(value)
            y.append(p)
            last_value = value

    return x, y


def kernel_density_estimation(
        X: List[float],
        Y: List[float],
        gridsize: int = 1000) -> Tuple[List[float], List[float]]:
    """
    estimates the density by using a trapez-like kernel
    """

    delta_x = (X[-1] - X[0]) / gridsize
    kde_x = np.linspace(X[0] - delta_x, X[-1] + delta_x, gridsize + 3)

    # bw_method parameter optimized for the evenly spaced case
    kernel = sp.stats.gaussian_kde(
        X, weights=Y, bw_method=(X[-1] - X[0]) / max(1000, 5 * len(X))
    )
    kde_y = kernel(kde_x)

    return kde_x.tolist(), kde_y.tolist()
