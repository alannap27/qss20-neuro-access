# 07_regional_and_cadre.py
# Takes in: data/raw/atlas_workforce_by_region.csv
#           data/raw/atlas_workforce_by_income.csv
#           data/processed/country_panel.csv
# Does: two cuts the income-group analysis cannot make. First, the same
# gradient by WHO region, with the country-level GDO values overlaid
# on the Atlas regional medians. Second, the gradient broken out by
# team (adult neurologists, neurosurgeons, child neurologists),
# which shows the shortage deepening as subspecialization increases.
# Outputs: output/fig8_regional_gradient.png
#          output/fig9__gradient.png
#          output/table5_regional_comparison.csv

import os
import sys

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import INCOME_COLORS, REGION_NAMES, style_axis, caption

os.makedirs("output", exist_ok=True)
CAP = "neurologists_per100k"

by_region = pd.read_csv("data/raw/atlas_workforce_by_region.csv")
by_income = pd.read_csv("data/raw/atlas_workforce_by_income.csv")
panel = pd.read_csv("data/processed/country_panel.csv")

# ---------------------------------------------------------------
# Figure 8: regional gradient, Atlas medians with GDO countries overlaid
# ---------------------------------------------------------------

reg = by_region[by_region["region_code"] != "Global"].copy()
reg = reg.sort_values("total_workforce_per100k")
global_med = by_region.loc[by_region["region_code"] == "Global",
                           "total_workforce_per100k"].values[0]

gdo_reg = panel[panel[CAP].notna() & panel["who_region"].notna()].copy()

fig, ax = plt.subplots(figsize=(11.5, 6.6))
xs = np.arange(len(reg))
ax.bar(xs, reg["total_workforce_per100k"], width=0.62, color="#b7c9de",
       edgecolor="#7aa6cf", zorder=2, label="WHO Atlas regional median (all cadres)")

# the bar value sits at the left edge rather than the center, because the
# jittered country dots occupy the middle of each bar
for i, (_, r) in enumerate(reg.iterrows()):
    ax.text(i - 0.33, r["total_workforce_per100k"] + 0.22, "%.1f" % r["total_workforce_per100k"],
            ha="left", fontsize=9.5, fontweight="bold")
    ax.text(i, -0.72, "Atlas n = %d" % r["n_total"], ha="center", fontsize=7.5, color="#555555")

# overlay the individual GDO countries that sit in each region
rng = np.random.default_rng(20260803)
plotted = False
for i, (_, r) in enumerate(reg.iterrows()):
    sub = gdo_reg[gdo_reg["who_region"] == r["region_code"]]
    if not len(sub):
        continue
    x = i + rng.uniform(-0.16, 0.16, len(sub))
    ax.scatter(x, sub[CAP], s=52, color="#c05621", zorder=4, alpha=0.92,
               edgecolor="white", linewidth=0.7,
               label="Individual country, WHO GDO (neurologists only)" if not plotted else None)
    plotted = True
    ax.text(i, -1.28, "GDO n = %d" % len(sub), ha="center", fontsize=7.5, color="#c05621")

ax.axhline(global_med, linestyle="--", color="black", linewidth=1.1, zorder=3)
ax.text(-0.44, global_med + 0.2, "global median %.1f" % global_med, fontsize=8.5)

ax.set_xticks(xs)
ax.set_xticklabels(["%s\n%s" % (c, REGION_NAMES[c].replace(" Region", "").replace("Region of the ", ""))
                    for c in reg["region_code"]], fontsize=8.5)
ax.set_ylim(-1.8, 15)
ax.set_ylabel("Workforce per 100 000 population")
ax.set_xlabel("WHO region")
ax.legend(fontsize=8.5, loc="upper left", frameon=False)
ax.set_title("Figure 8. The workforce gradient by WHO region: the African and South-East Asia\n"
             "Regions sit an order of magnitude below the global median", fontsize=12)
style_axis(ax)
caption(fig,
        "Bars are the WHO/WFN Neurology Atlas median of the total neurological workforce (adult neurologists + neurosurgeons + child neurologists) per 100 000 population within each WHO region\n"
        "(2017, Fig. 11); the count under each bar is the number of countries answering that item. Orange dots are individual countries from the WHO Global Dementia Observatory (2017), which counts\n"
        "adult neurologists only and therefore sits systematically below the Atlas bar. Dots are jittered horizontally to avoid overplotting. Regions are ordered by Atlas median, not alphabetically.")
plt.tight_layout(rect=[0, 0.062, 1, 1])
plt.savefig("output/fig8_regional_gradient.png", dpi=200)
plt.close()

# ---------------------------------------------------------------
# Figure 9: the gradient deepens with subspecialization
# ---------------------------------------------------------------

inc = by_income[by_income["income_group"] != "Global"].copy()
cadres = [("adult_neurologists_per100k", "Adult neurologists"),
          ("neurosurgeons_per100k", "Neurosurgeons"),
          ("child_neurologists_per100k", "Child neurologists")]

fig, ax = plt.subplots(figsize=(11, 6.4))
w = 0.26
for j, (col, lab) in enumerate(cadres):
    off = (j - 1) * w
    ax.bar(np.arange(len(inc)) + off, inc[col], width=w, zorder=3,
           color=["#2b6cb0", "#dd9a4e", "#c05621"][j], label=lab)
    for i, v in enumerate(inc[col]):
        ax.text(i + off, v * 1.16 if v > 0 else 0.0012, "%.3g" % v,
                ha="center", fontsize=8)

ax.set_yscale("log")
ax.set_ylim(0.001, 20)
ax.set_xticks(range(len(inc)))
ax.set_xticklabels(["Low-income", "Lower-middle-income", "Upper-middle-income", "High-income"],
                   fontsize=9)
ax.set_ylabel("Median per 100 000 population (log scale)")
ax.set_xlabel("World Bank income group")
ax.legend(fontsize=9, loc="upper left", frameon=False)

# annotate the ratio for each group
ratios = []
for col, lab in cadres:
    lo = inc.loc[inc["income_group"] == "Low-income", col].values[0]
    hi = inc.loc[inc["income_group"] == "High-income", col].values[0]
    ratios.append((lab, lo, hi, hi / lo))
# on a log-scale bar chart every bar runs to the axis floor, so the only
# is high above the two left-hand groups; the box is placed there
# in axes coordinates and clears the legend at upper left
txt = "\n".join("%-20s %4.0fx" % (lab, r) for lab, _, _, r in ratios)
ax.text(0.31, 0.975, "high- vs low-income ratio\n" + txt,
        transform=ax.transAxes, fontsize=8.5, family="monospace",
        va="top", ha="left",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#f4f4f4", edgecolor="#bbbbbb"))

ax.set_title("Figure 9. The scarcity gradient steepens with subspecialization: 62-fold for\n"
             "neurosurgeons, 158-fold for adult neurologists, 195-fold for child neurologists",
             fontsize=12)
style_axis(ax)
caption(fig,
        "Median number of each group per 100,000 population by World Bank income group, on a logarithmic vertical axis because the values span four orders of magnitude (0.002 to 4.75). A log axis\n"
        "makes equal ratios equal distances, so the widening spacing between the three series from left to right is the finding: the rarer the specialism, the steeper the income gradient. Source:\n"
        "WHO/WFN Atlas: Country Resources for Neurological Disorders, 2nd ed. (2017), Table 3. Response counts differ by group (93 to 114 countries) and are reported in table3_atlas_gradients.csv.")
plt.tight_layout(rect=[0, 0.062, 1, 1])
plt.savefig("output/fig9_cadre_gradient.png", dpi=200)
plt.close()

# ---------------------------------------------------------------
# Table 5: regional comparison of the two instruments
# ---------------------------------------------------------------

rows = []
for _, r in by_region.iterrows():
    sub = gdo_reg[gdo_reg["who_region"] == r["region_code"]]
    rows.append({
        "region_code": r["region_code"],
        "region": REGION_NAMES.get(r["region_code"], "Global"),
        "atlas_total_workforce_per100k": r["total_workforce_per100k"],
        "atlas_n": r["n_total"],
        "atlas_adult_neurologists_per100k": r["adult_neurologists_per100k"],
        "gdo_n_countries": len(sub),
        "gdo_median_neurologists_per100k": round(sub[CAP].median(), 3) if len(sub) else np.nan,
        "gdo_min": round(sub[CAP].min(), 3) if len(sub) else np.nan,
        "gdo_max": round(sub[CAP].max(), 3) if len(sub) else np.nan,
    })
t5 = pd.DataFrame(rows)
t5.to_csv("output/table5_regional_comparison.csv", index=False)

print(t5.to_string(index=False))
print()
print("Group ratios (high-income / low-income):")
for lab, lo, hi, r in ratios:
    print("  %-20s %.3f -> %.3f  = %.0fx" % (lab, lo, hi, r))
print()
print("figures 8-9 and table 5 written to output/")
