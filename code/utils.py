## utils.py
## Shared helpers imported by every numbered script in this repository.
## Nothing here reads or writes files; each numbered script owns its own I/O.

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

## ---------------------------------------------------------------
## House style, so every figure in output/ looks like it belongs to
## the same project
## ---------------------------------------------------------------

PALETTE = {
    "High-income": "#2b6cb0",
    "Upper-middle": "#7aa6cf",
    "Low / middle-income": "#c05621",
    "Low / lower-middle": "#c05621",
    "Not classified": "#9aa0a6",
}
INCOME_COLORS = ["#c05621", "#dd9a4e", "#7aa6cf", "#2b6cb0"]
SETTING_COLORS = {"capital": "#2b6cb0", "urban": "#dd9a4e", "rural": "#c05621"}
GRID = "#e6e6e6"

INCOME_ORDER = ["Low-income", "Lower-middle-income", "Upper-middle-income", "High-income"]
BIN3_ORDER = ["Low / lower-middle", "Upper-middle", "High-income"]

REGION_NAMES = {
    "AFR": "African Region", "AMR": "Region of the Americas",
    "EMR": "Eastern Mediterranean Region", "EUR": "European Region",
    "SEAR": "South-East Asia Region", "WPR": "Western Pacific Region",
}


def style_axis(ax, axis="y"):
    """Apply the shared grid / spine treatment to an axis."""
    if axis in ("y", "both"):
        ax.yaxis.grid(True, color=GRID, linewidth=0.8, zorder=0)
    if axis in ("x", "both"):
        ax.xaxis.grid(True, color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    return ax


def caption(fig, text, size=7):
    """Attach a self-contained source note under a figure.

    Every figure in this project carries its own source, sample size and a
    plain-language reading of any reference line, so that a reader skimming
    only the figures can follow the argument.
    """
    fig.text(0.01, 0.005, text, fontsize=size, ha="left", va="bottom")


## ---------------------------------------------------------------
## WHO data cleaning
## ---------------------------------------------------------------

## WHO stores non-responses as literal strings inside otherwise numeric fields
MISSING_STRINGS = ["Not available", "Not applicable", "No data", "Not reported", ""]

## the service-accessibility question is ordered, not merely categorical
ACC_SCALE = {
    "Capital city only": 1,
    "Capital and main cities only": 2,
    "Capital, main cities and rural areas": 3,
}
ACC_LABELS = {1: "Capital only", 2: "Capital + main cities", 3: "Reaches rural areas"}


def clean_who_numeric(series):
    """Convert a WHO value column to float, mapping placeholder strings to NaN."""
    return pd.to_numeric(series.where(~series.isin(MISSING_STRINGS)), errors="coerce")


def bin_income(income_group, n_bins=3):
    """Collapse the four World Bank groups into 2 or 3 comparison bins.

    Country-level regressions on 19-35 observations are underpowered, so the
    analysis compares binned groups instead. Returns None for unclassified.
    """
    if pd.isna(income_group):
        return None
    if n_bins == 2:
        return "High-income" if income_group == "High-income" else "Low / middle"
    return {"Low-income": "Low / lower-middle",
            "Lower-middle income": "Low / lower-middle",
            "Lower-middle-income": "Low / lower-middle",
            "Upper-middle income": "Upper-middle",
            "Upper-middle-income": "Upper-middle",
            "High-income": "High-income"}.get(income_group)


## ---------------------------------------------------------------
## The gap metrics
## ---------------------------------------------------------------

def share_ratio(burden, capacity):
    """Burden-to-capacity SHARE RATIO.

    Each country's share of the sample's total burden, divided by its share of
    the sample's total capacity.

      1.0  the country holds exactly as large a share of the sample's burden as
           it holds of the sample's workforce
      1.2  it carries 20% more of the burden than its share of the workforce
     13.1  it carries thirteen times as large a share of the burden as of the
           workforce, i.e. the same workforce stretched over thirteen times the need
     <1.0  it holds more of the workforce than of the burden

    Scale-free, so it does not depend on the units of either input. Undefined
    where capacity is zero; those countries are returned as NaN and must be
    reported separately rather than dropped silently.
    """
    burden = np.asarray(burden, dtype=float)
    capacity = np.asarray(capacity, dtype=float)
    b_share = burden / np.nansum(burden)
    c_share = capacity / np.nansum(capacity)
    with np.errstate(divide="ignore", invalid="ignore"):
        out = np.where(c_share > 0, b_share / c_share, np.nan)
    return out


def gini(x):
    """Gini coefficient of a non-negative array.

    0 = every unit identical; 1 = one unit holds everything. Computed on the
    sorted array with the standard covariance formula.
    """
    x = np.sort(np.asarray(x, dtype=float))
    x = x[~np.isnan(x)]
    n = len(x)
    if n == 0 or x.sum() == 0:
        return np.nan
    idx = np.arange(1, n + 1)
    return (2.0 * np.sum(idx * x) / (n * x.sum())) - (n + 1.0) / n


def lorenz_points(x):
    """Return (cumulative share of units, cumulative share of total) for a Lorenz curve."""
    xs = np.sort(np.asarray(x, dtype=float))
    xs = xs[~np.isnan(xs)]
    cum_units = np.arange(1, len(xs) + 1) / len(xs)
    cum_total = np.cumsum(xs) / xs.sum()
    return np.insert(cum_units, 0, 0), np.insert(cum_total, 0, 0)


def bootstrap_ci(x, stat=gini, n_boot=5000, alpha=0.05, seed=20260803):
    """Percentile bootstrap interval for a statistic of a small sample.

    Used because the country-level samples here are small enough (n = 19) that a
    point estimate on its own would overstate how precisely the inequality is known.
    """
    rng = np.random.default_rng(seed)
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    draws = [stat(rng.choice(x, size=len(x), replace=True)) for _ in range(n_boot)]
    lo, hi = np.percentile(draws, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return stat(x), lo, hi


def leave_one_out(x, labels, stat=gini):
    """Recompute a statistic dropping each observation in turn.

    With 19 countries, a single extreme reporter can move a Gini materially;
    this shows how much.
    """
    x = np.asarray(x, dtype=float)
    rows = []
    for i, lab in enumerate(labels):
        keep = np.delete(x, i)
        rows.append({"dropped": lab, "statistic": stat(keep)})
    return pd.DataFrame(rows).sort_values("statistic")
