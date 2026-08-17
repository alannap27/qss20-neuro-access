## 05_atlas_descriptives.py
## Takes in : data/raw/atlas_workforce_by_income.csv
##            data/raw/atlas_workforce_by_region.csv
##            data/raw/atlas_country_crosswalk.csv
## Does     : reproduces the two aggregate descriptives from the WHO/WFN Neurology
##            Atlas that provide the backdrop for the country-level analysis in
##            04_analyze.py. These rest on 114 responding countries -- roughly six
##            times the country-level sample -- so they establish the gradient at
##            a scale the GDO extract cannot reach.
## Outputs  : output/fig4_atlas_workforce_by_income.png
##            output/fig5_atlas_where_neurologists_practise.png
##            output/table3_atlas_gradients.csv

import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

os.makedirs("output", exist_ok=True)
RAW = "data/raw/"

by_income = pd.read_csv(RAW + "atlas_workforce_by_income.csv")
by_region = pd.read_csv(RAW + "atlas_workforce_by_region.csv")
cross = pd.read_csv(RAW + "atlas_country_crosswalk.csv")

print("income-group rows:", len(by_income), " region rows:", len(by_region))
print("crosswalk countries with an ISO3 match:", len(cross))

## ---------------------------------------------------------------
## The two headline gradients, reported as ratios so that they are
## directly comparable with the share ratio used in 04_analyze.py
## ---------------------------------------------------------------

def val(df, grp, col):
    return df.loc[df["income_group"] == grp, col].values[0]

rows = []
for col, label in [("total_workforce_per100k", "Total neurological workforce"),
                   ("adult_neurologists_per100k", "Adult neurologists"),
                   ("neurosurgeons_per100k", "Neurosurgeons"),
                   ("child_neurologists_per100k", "Child neurologists")]:
    lo, hi = val(by_income, "Low-income", col), val(by_income, "High-income", col)
    rows.append([label, lo, hi, round(hi - lo, 3), round(hi / lo, 1)])

t3 = pd.DataFrame(rows, columns=["cadre", "low_income_per100k", "high_income_per100k",
                                 "absolute_gap", "ratio_high_to_low"])
t3.to_csv("output/table3_atlas_gradients.csv", index=False)
print()
print(t3.to_string(index=False))
print()
print("Read the ratio column as: a value of 158.3 means a high-income country has")
print("158 times as many adult neurologists per head as a low-income country.")

## ---------------------------------------------------------------
## Figure 4: the aggregate scarcity gradient
## ---------------------------------------------------------------

plot_inc = by_income[by_income["income_group"] != "Global"].copy()
global_med = val(by_income, "Global", "total_workforce_per100k")

fig, ax = plt.subplots(figsize=(9, 6))
bars = ax.bar(plot_inc["income_group"], plot_inc["total_workforce_per100k"],
              color=["#c05621", "#dd9a4e", "#7aa6cf", "#2b6cb0"], zorder=3)
ax.axhline(global_med, linestyle="--", linewidth=1.2, color="black", zorder=4)
ax.text(-0.45, global_med + 0.14, "global median %.1f per 100 000" % global_med,
        fontsize=8.5, va="bottom")

for b, v, n in zip(bars, plot_inc["total_workforce_per100k"], plot_inc["n_total"]):
    ax.text(b.get_x() + b.get_width() / 2, v + 0.12, "%.1f" % v,
            ha="center", fontsize=10, fontweight="bold")
    ax.text(b.get_x() + b.get_width() / 2, v + 0.42, "n = %d countries" % n,
            ha="center", fontsize=7.5, color="#444444")

## the headline contrast, stated in open space rather than drawn across the bars
ratio_hi_lo = val(by_income, "High-income", "total_workforce_per100k") / \
              val(by_income, "Low-income", "total_workforce_per100k")
ax.text(0.55, 6.35,
        "%.0fx\nhigh-income median (%.1f)\nvs low-income median (%.1f)"
        % (ratio_hi_lo, val(by_income, "High-income", "total_workforce_per100k"),
           val(by_income, "Low-income", "total_workforce_per100k")),
        fontsize=9.5, ha="center", va="center", color="#333333",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#f4f4f4",
                  edgecolor="#bbbbbb", linewidth=0.8))

ax.set_ylabel("Median neurological workforce per 100 000 population")
ax.set_xlabel("World Bank income group")
ax.set_ylim(0, 8.4)
ax.yaxis.grid(True, color="#e6e6e6", linewidth=0.8, zorder=0)
ax.set_axisbelow(True)
ax.set_title("Context. Neurological workforce density rises 71-fold from low- to\n"
             "high-income countries (WHO Neurology Atlas, 114 responding countries)",
             fontsize=11.5)
plt.figtext(0.01, 0.005,
            "Median of the total neurological workforce (adult neurologists + neurosurgeons + child neurologists) per 100 000 population, by World Bank income\n"
            "group. Source: WHO/WFN Atlas: Country Resources for Neurological Disorders, 2nd ed. (2017), Figure 12. Counts under each bar are the number of\n"
            "countries answering that item; because these are medians of country values, they are not population-weighted.",
            fontsize=7, ha="left")
plt.tight_layout(rect=[0, 0.075, 1, 1])
plt.savefig("output/fig4_atlas_workforce_by_income.png", dpi=200)
plt.close()

## ---------------------------------------------------------------
## Figure 5: the same countries, disaggregated by where staff practise
## ---------------------------------------------------------------

cols = ["pct_countries_capital", "pct_countries_other_urban", "pct_countries_rural"]
labels = ["Capital city", "Other urban areas", "Rural areas"]
shades = ["#2b6cb0", "#dd9a4e", "#c05621"]
positions = range(len(plot_inc))
width = 0.27
offsets = [-width, 0, width]

fig, ax = plt.subplots(figsize=(9.5, 6))
for off, col, lab, sh in zip(offsets, cols, labels, shades):
    ax.bar([p + off for p in positions], plot_inc[col], width=width,
           label=lab, color=sh, zorder=3)
    for p, v in zip(positions, plot_inc[col]):
        ax.text(p + off, v + 1.8, "%d%%" % v, ha="center", fontsize=8.5, zorder=4)

ax.annotate("no low-income country reports\nany neurologist practising rurally",
            xy=(0 + width, 1.5), xytext=(-0.34, 40), fontsize=8.5, ha="left",
            arrowprops=dict(arrowstyle="->", lw=1.0, color="#c05621",
                            connectionstyle="arc3,rad=-0.2"), color="#c05621")

ax.set_xticks(list(positions))
ax.set_xticklabels(plot_inc["income_group"], fontsize=9)
ax.set_ylabel("% of responding countries")
ax.set_xlabel("World Bank income group")
ax.set_ylim(0, 132)
ax.yaxis.grid(True, color="#e6e6e6", linewidth=0.8, zorder=0)
ax.set_axisbelow(True)
ax.legend(fontsize=8.5, loc="upper center", ncol=3, frameon=False)
ax.set_title("Context. Capital-city coverage is near-universal at every income level;\n"
             "rural coverage collapses from 45% to 0% (WHO Neurology Atlas, n = 114)",
             fontsize=11.5)
plt.figtext(0.01, 0.005,
            "Share of responding countries reporting that neurologists practise in each setting, by World Bank income group. A country can report more than one\n"
            "setting, so bars within a group do not sum to 100%. Source: WHO/WFN Atlas: Country Resources for Neurological Disorders, 2nd ed. (2017), Figure 16;\n"
            "114 responding countries. This is the aggregate counterpart to Figure 3, which measures the same gradient country by country in the WHO GDO extract.",
            fontsize=7, ha="left")
plt.tight_layout(rect=[0, 0.075, 1, 1])
plt.savefig("output/fig5_atlas_where_neurologists_practise.png", dpi=200)
plt.close()

print()
print("figures 4-5 and table 3 written to output/")
