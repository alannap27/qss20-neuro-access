# 06_paired_comparison.py
# Takes in: data/processed/country_panel.csv
#           data/raw/atlas_workforce_by_income.csv
# Does: sets each aggregate Atlas descriptive directly beside its
# country-level counterpart from the WHO GDO extract, so the two
# can be read against each other. The Atlas panels rest on 114
# responding countries and the GDO panels on 19-35, so agreement
# between them is the main defense against the small-n objection
# the country-level analysis would otherwise face.
# Outputs: output/fig6_paired_workforce_gradient.png
#          output/fig7_paired_rural_access.png
#          output/table4_paired_instruments.csv

import os
import sys

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import (INCOME_COLORS, SETTING_COLORS, ACC_LABELS, BIN3_ORDER,
                   style_axis, caption)

os.makedirs("output", exist_ok=True)
CAP = "neurologists_per100k"

panel = pd.read_csv("data/processed/country_panel.csv")
atlas = pd.read_csv("data/raw/atlas_workforce_by_income.csv")
atlas_plot = atlas[atlas["income_group"] != "Global"].copy()

# ---------------------------------------------------------------
# Figure 6: the workforce gradient, measured two ways
# left: Atlas medians by income group, 114 responding countries
# right: GDO country-level density, 19 countries, plotted individually
# ---------------------------------------------------------------

gdo = panel[panel[CAP].notna() & panel["income_bin3"].notna()].copy()

fig, axes = plt.subplots(1, 2, figsize=(14, 6.4))

# left panel: the aggregate
ax = axes[0]
bars = ax.bar(range(len(atlas_plot)), atlas_plot["total_workforce_per100k"],
              color=INCOME_COLORS, zorder=3, width=0.68)
for i, (v, n) in enumerate(zip(atlas_plot["total_workforce_per100k"], atlas_plot["n_total"])):
    ax.text(i, v + 0.12, "%.1f" % v, ha="center", fontsize=10, fontweight="bold")
    ax.text(i, v + 0.44, "n = %d" % n, ha="center", fontsize=7.5, color="#555555")
ax.axhline(3.1, linestyle="--", color="black", linewidth=1.1, zorder=4)
ax.text(-0.45, 3.22, "global median 3.1", fontsize=8)
ax.set_xticks(range(len(atlas_plot)))
ax.set_xticklabels(["Low", "Lower-\nmiddle", "Upper-\nmiddle", "High"], fontsize=9)
ax.set_ylim(0, 8.6)
ax.set_ylabel("Median workforce per 100 000 population")
ax.set_xlabel("World Bank income group")
ax.set_title("A. Aggregate instrument — WHO Neurology Atlas\n"
             "median of country values, 114 responding countries", fontsize=10.5)
style_axis(ax)

# right panel: the country-level, same construct
ax = axes[1]
jitter_rng = np.random.default_rng(20260803)
xpos = {b: i for i, b in enumerate(BIN3_ORDER)}
for b in BIN3_ORDER:
    sub = gdo[gdo["income_bin3"] == b]
    if not len(sub):
        continue
    x = xpos[b] + jitter_rng.uniform(-0.13, 0.13, len(sub))
    ax.scatter(x, sub[CAP], s=64, zorder=3, alpha=0.9,
               color=INCOME_COLORS[0] if b == "Low / lower-middle"
               else (INCOME_COLORS[2] if b == "Upper-middle" else INCOME_COLORS[3]),
               edgecolor="white", linewidth=0.8)
    med = sub[CAP].median()
    ax.plot([xpos[b] - 0.28, xpos[b] + 0.28], [med, med], color="black", lw=2, zorder=4)
    ax.text(xpos[b] + 0.32, med, "median %.2f" % med, fontsize=8, va="center")
    ax.text(xpos[b], -0.55, "n = %d" % len(sub), ha="center", fontsize=7.5, color="#555555")

# label the extremes, stepping the low-end labels apart so the three
# near-zero countries do not print on top of one another
for _, r in gdo.nlargest(2, CAP).iterrows():
    ax.annotate(r["iso3"], (xpos[r["income_bin3"]], r[CAP]),
                textcoords="offset points", xytext=(13, 2), fontsize=8.5)
for k, (_, r) in enumerate(gdo.nsmallest(3, CAP).iterrows()):
    ax.annotate("%s (%.2f)" % (r["iso3"], r[CAP]),
                (xpos[r["income_bin3"]], r[CAP]),
                textcoords="offset points", xytext=(16, -26 + 13 * k), fontsize=8,
                arrowprops=dict(arrowstyle="-", lw=0.6, color="#999999"))

ax.set_xticks(range(len(BIN3_ORDER)))
ax.set_xticklabels(["Low /\nlower-middle", "Upper-\nmiddle", "High"], fontsize=9)
ax.set_xlim(-0.6, 2.85)
ax.set_ylim(-1.6, 14.8)
ax.set_ylabel("Neurologists per 100 000 population (each dot = one country)")
ax.set_xlabel("World Bank income group")
ax.set_title("B. Country-level instrument — WHO Global Dementia Observatory\n"
             "one observation per country, %d countries with an income group" % len(gdo),
             fontsize=10.5)
style_axis(ax)

fig.suptitle("Figure 6. The same workforce gradient measured by two independent WHO instruments",
             fontsize=13, y=0.985)
caption(fig,
        "Panel A reports the median across countries within each income group and cannot identify individual countries; Panel B reports each country separately but covers far fewer of them.\n"
        "The two disagree on level (Panel A counts neurologists, neurosurgeons and child neurologists; Panel B counts neurologists only) and agree on direction and steepness, which is the point:\n"
        "The country-level finding is not an artifact of the 19-country sample. Sources: WHO/WFN Neurology Atlas 2nd ed. (2017) Fig. 12; WHO Global Dementia Observatory (2017) indicator GDO_q6x1_2.")
plt.tight_layout(rect=[0, 0.055, 1, 0.965])
plt.savefig("output/fig6_paired_workforce_gradient.png", dpi=200)
plt.close()

# ---------------------------------------------------------------
# Figure 7: rural access, measured two ways
# left: Atlas, share of countries reporting neurologists in each setting
# right: GDO, where dementia diagnostic services actually reach
# ---------------------------------------------------------------

rq3 = panel[panel["accessibility_level"].notna() & panel["income_bin3"].notna()].copy()
ct = pd.crosstab(rq3["income_bin3"], rq3["accessibility_level"])
for lvl in [1, 2, 3]:
    if lvl not in ct.columns:
        ct[lvl] = 0
ct = ct[[1, 2, 3]].reindex([b for b in BIN3_ORDER if b in ct.index])
props = (ct.T / ct.sum(axis=1)).T * 100

fig, axes = plt.subplots(1, 2, figsize=(14, 6.4))

# left panel
ax = axes[0]
cols = ["pct_countries_capital", "pct_countries_other_urban", "pct_countries_rural"]
labs = ["Capital city", "Other urban areas", "Rural areas"]
shades = [SETTING_COLORS["capital"], SETTING_COLORS["urban"], SETTING_COLORS["rural"]]
w = 0.26
for off, col, lab, sh in zip([-w, 0, w], cols, labs, shades):
    ax.bar([i + off for i in range(len(atlas_plot))], atlas_plot[col],
           width=w, color=sh, label=lab, zorder=3)
    for i, v in enumerate(atlas_plot[col]):
        ax.text(i + off, v + 2.0, "%d%%" % v, ha="center", fontsize=8)
ax.annotate("0% — no low-income country\nreports rural practice",
            xy=(w, 2.0), xytext=(0.30, 60), fontsize=8, ha="center",
            color=SETTING_COLORS["rural"],
            arrowprops=dict(arrowstyle="->", lw=1.0, color=SETTING_COLORS["rural"],
                            connectionstyle="arc3,rad=0.18"))
ax.set_xticks(range(len(atlas_plot)))
ax.set_xticklabels(["Low", "Lower-\nmiddle", "Upper-\nmiddle", "High"], fontsize=9)
ax.set_ylim(0, 128)
ax.set_ylabel("% of responding countries")
ax.set_xlabel("World Bank income group")
ax.legend(fontsize=8, loc="upper center", ncol=3, frameon=False)
ax.set_title("A. Where neurologists practice — WHO Neurology Atlas\n"
             "114 responding countries; a country may report several settings", fontsize=10.5)
style_axis(ax)

# right panel
ax = axes[1]
bottom = np.zeros(len(props))
for j, lvl in enumerate([1, 2, 3]):
    sh = [SETTING_COLORS["rural"], SETTING_COLORS["urban"], SETTING_COLORS["capital"]][j]
    ax.bar(range(len(props)), props[lvl], bottom=bottom, color=sh,
           label=ACC_LABELS[lvl], zorder=3, width=0.62)
    for i, v in enumerate(props[lvl]):
        if v > 6:
            ax.text(i, bottom[i] + v / 2, "%.0f%%\n(n=%d)" % (v, ct[lvl].iloc[i]),
                    ha="center", va="center", fontsize=8.5,
                    color="white" if j != 1 else "black")
    bottom += props[lvl].values
ax.set_xticks(range(len(props)))
ax.set_xticklabels(["Low /\nlower-middle", "Upper-\nmiddle", "High"], fontsize=9)
ax.set_ylim(0, 128)
ax.set_ylabel("% of countries in the income bin")
ax.set_xlabel("World Bank income group")
ax.legend(fontsize=8, loc="upper center", ncol=3, frameon=False)
ax.set_title("B. Where dementia diagnostic services reach — WHO GDO\n"
             "%d countries with both service reach and an income group" % len(rq3), fontsize=10.5)
style_axis(ax)

fig.suptitle("Figure 7. Two parts, one finding: specialist care thins out before it reaches rural populations",
             fontsize=13, y=0.985)
caption(fig,
        "Panel A asks whether neurologists practice in a setting at all; Panel B asks how far dementia diagnostic services extend. These are different questions about the same underlying\n"
        "constraint, asked of overlapping but not identical country sets, and they produce the same ordering. In Panel A rural coverage falls 45%% -> 0%% across income groups; in Panel B the share\n"
        "of countries whose services reach rural areas falls %.0f%% -> %.0f%%. Sources: WHO/WFN Neurology Atlas 2nd ed. (2017) Fig. 16; WHO Global Dementia Observatory (2017) indicator GDO_q8x3_1."
        % (props[3].get("High-income", 0), props[3].get("Low / lower-middle", 0)))
plt.tight_layout(rect=[0, 0.055, 1, 0.965])
plt.savefig("output/fig7_paired_rural_access.png", dpi=200)
plt.close()

# ---------------------------------------------------------------
# Table 4: what each instrument contributes
# ---------------------------------------------------------------

t4 = pd.DataFrame([
    ["Workforce gradient", "WHO Neurology Atlas (aggregate)", 114,
     "median per income group", "0.1 -> 7.1 per 100k (71x)",
     "cannot identify countries; not linkable to burden"],
    ["Workforce gradient", "WHO GDO (country level)", int(gdo[CAP].notna().sum()),
     "one value per country",
     "median %.2f -> %.2f per 100k (%.0fx)" % (
         gdo.loc[gdo["income_bin3"] == "Low / lower-middle", CAP].median(),
         gdo.loc[gdo["income_bin3"] == "High-income", CAP].median(),
         gdo.loc[gdo["income_bin3"] == "High-income", CAP].median() /
         max(gdo.loc[gdo["income_bin3"] == "Low / lower-middle", CAP].median(), 1e-9)),
     "small sample; neurologists only, no neurosurgeons"],
    ["Rural access", "WHO Neurology Atlas (aggregate)", 114,
     "% of countries reporting rural practice", "45% -> 0% across income groups",
     "binary presence, not intensity"],
    ["Rural access", "WHO GDO (country level)", len(rq3),
     "ordered service-reach level",
     "%.0f%% -> %.0f%% of countries reach rural areas" % (
         props[3].get("High-income", 0), props[3].get("Low / lower-middle", 0)),
     "dementia services specifically, not all neurology"],
], columns=["construct", "instrument", "n_countries", "unit", "finding", "limitation"])
t4.to_csv("output/table4_paired_instruments.csv", index=False)

print(t4.to_string(index=False))
print()
print("figures 6-7 and table 4 written to output/")
