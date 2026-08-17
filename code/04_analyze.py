## 04_analyze.py
## Takes in : data/processed/country_panel.csv
## Does     : answers the three research questions -- (RQ1) how far capacity is
##            aligned with burden, measured as a share ratio; (RQ2) how unequally
##            capacity is distributed across and within countries, measured with a
##            Gini coefficient and the service-reach gradient; (RQ3) whether the
##            gap differs between binned country types, tested with Welch t-tests,
##            one-way ANOVA and a chi-square rather than a country-level regression
## Outputs  : output/fig1_alignment_ratio.png
##            output/fig2_lorenz_gini.png
##            output/fig3_service_reach_by_income.png
##            output/table1_analysis_sample.csv
##            output/table2_hypothesis_tests.csv

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

os.makedirs("output", exist_ok=True)
df = pd.read_csv("data/processed/country_panel.csv")

BURDEN = "stroke_dalys_per100k_agestd_2004"
CAP = "neurologists_per100k"

## ---------------------------------------------------------------
## Table 1: what the analysis sample actually contains
## ---------------------------------------------------------------

t1 = pd.DataFrame({
    "measure": ["Countries in panel",
                "With neurologist density (WHO GDO, 2017)",
                "With service-reach level (WHO GDO, 2017)",
                "With stroke DALY rate (WHO GHE, 2004)",
                "With World Bank income group (WHO Atlas, 2017)",
                "With capacity AND burden (RQ1 sample)",
                "With service reach AND income group (RQ3 sample)"],
    "n": [len(df), df[CAP].notna().sum(), df["accessibility_level"].notna().sum(),
          df[BURDEN].notna().sum(), df["wb_income_group"].notna().sum(),
          (df[CAP].notna() & df[BURDEN].notna()).sum(),
          (df["accessibility_level"].notna() & df["wb_income_group"].notna()).sum()],
})
t1.to_csv("output/table1_analysis_sample.csv", index=False)
print(t1.to_string(index=False))

## ===============================================================
## RQ1. Is neurological workforce capacity aligned with burden?
## ===============================================================
## Metric: the burden-to-capacity SHARE RATIO.
##   share of sample burden held by a country, divided by
##   share of sample neurologists held by that country.
## A ratio of 1.0 means the country carries exactly as large a share of the
## sample's stroke burden as it holds of the sample's neurological workforce.
## A ratio of 2.0 means it carries twice as large a share of the burden as it
## holds of the workforce -- i.e. its workforce is spread half as thinly as
## an evenly-matched country's would be.

rq1 = df[df[CAP].notna() & df[BURDEN].notna()].copy()

## countries reporting zero neurologists cannot be placed on a ratio scale at
## all; they are reported separately rather than silently dropped or set to inf
zero_cap = rq1[rq1[CAP] == 0]
rq1 = rq1[rq1[CAP] > 0].copy()

rq1["burden_share"] = rq1[BURDEN] / rq1[BURDEN].sum()
rq1["capacity_share"] = rq1[CAP] / rq1[CAP].sum()
rq1["alignment_ratio"] = rq1["burden_share"] / rq1["capacity_share"]
rq1 = rq1.sort_values("alignment_ratio")

print()
print("=== RQ1: burden-to-capacity share ratio ===")
print("countries on the ratio scale:", len(rq1))
print("countries reporting ZERO neurologists (off-scale):",
      list(zero_cap["iso3"]), "- burden per 100k:",
      list(zero_cap[BURDEN]))
print()
print(rq1[["iso3", "wb_income_group", CAP, BURDEN, "alignment_ratio"]].to_string(index=False))
print()
print("median ratio, high-income:",
      round(rq1.loc[rq1["income_bin2"] == "High-income", "alignment_ratio"].median(), 2))
print("median ratio, low/middle-income:",
      round(rq1.loc[rq1["income_bin2"] == "Low / middle", "alignment_ratio"].median(), 2))

## Figure 1 -- annotated so it stands alone
## The ratio spans three orders of magnitude (0.07 to 70), so it is drawn on a
## log scale: there the reference value of 1.0 sits mid-axis, and "twice as much
## burden as workforce" is the same visual distance as "half as much".
LABEL = {"High-income": "High-income", "Low / middle": "Low / middle-income"}
rq1["grp"] = rq1["income_bin2"].map(LABEL).fillna("Not classified")
PALETTE = {"High-income": "#2b6cb0", "Low / middle-income": "#c05621",
           "Not classified": "#9aa0a6"}

fig, ax = plt.subplots(figsize=(10, 6.8))
ax.barh(rq1["iso3"], rq1["alignment_ratio"],
        color=rq1["grp"].map(PALETTE), height=0.72, zorder=3)

ax.set_xscale("log")
ax.set_xlim(0.04, 300)
ax.set_xticks([0.1, 1, 10, 100])
ax.set_xticklabels(["0.1x", "1x", "10x", "100x"])
ax.xaxis.grid(True, which="major", color="#dddddd", linewidth=0.8, zorder=0)
ax.set_axisbelow(True)
ax.axvline(1.0, color="black", linestyle="--", linewidth=1.3, zorder=4)

## labels sit outside the bar tip, but bars just below parity would run their
## label straight through the dashed 1.0 line, so those are set inside instead
for y, v in enumerate(rq1["alignment_ratio"]):
    txt = ("%.2f" % v) if v < 1 else ("%.1f" % v)
    if 0.45 < v < 1.0:
        ax.text(v * 0.93, y, txt, va="center", ha="right",
                fontsize=8.5, color="white", zorder=5)
    else:
        ax.text(v * 1.14, y, txt, va="center", fontsize=8.5, zorder=5)

ax.text(0.052, len(rq1) - 0.4, "more workforce than burden",
        fontsize=8.5, style="italic", color="#2b6cb0", va="center")
ax.text(1.5, len(rq1) - 0.4, "more burden than workforce",
        fontsize=8.5, style="italic", color="#c05621", va="center")
ax.annotate("parity: share of burden\nequals share of workforce",
            xy=(1.0, 2.4), xytext=(3.0, 1.0), fontsize=8,
            arrowprops=dict(arrowstyle="->", lw=0.9, color="black"))

ax.set_ylim(-0.9, len(rq1) - 0.1)
ax.set_xlabel("Share of sample stroke burden ÷ share of sample neurologists  (log scale)")
ax.set_title("RQ1. The countries carrying the largest share of stroke burden hold the\n"
             "smallest share of the neurological workforce (n = %d countries)" % len(rq1),
             fontsize=11.5)
handles = [plt.Rectangle((0, 0), 1, 1, color=PALETTE[k])
           for k in ["High-income", "Low / middle-income", "Not classified"]]
ax.legend(handles, ["High-income", "Low / middle-income", "Income group not in WHO Atlas"],
          fontsize=8, loc="lower right", framealpha=0.95)
plt.figtext(0.01, 0.005,
            "Ratio above 1.0 means the country holds a larger share of the sample's stroke burden than of its neurologists; below 1.0 the reverse. "
            "Capacity is WHO Global\nDementia Observatory neurologist density per 100 000 (2017); burden is WHO Global Health Estimates age-standardised stroke DALYs per 100 000 (2004).\n"
            "Eswatini and Fiji report zero neurologists and cannot be placed on a ratio scale; their stroke DALY rates are 994 and 1 536 per 100 000.",
            fontsize=7, ha="left")
plt.tight_layout(rect=[0, 0.075, 1, 1])
plt.savefig("output/fig1_alignment_ratio.png", dpi=200)
plt.close()

## ===============================================================
## RQ2. How unequally is capacity distributed?
## ===============================================================
## Gini of neurologist density across countries. 0 = every country has the
## same density; 1 = one country holds the entire workforce.

def gini(x):
    x = np.sort(np.asarray(x, dtype=float))
    n = len(x)
    if n == 0 or x.sum() == 0:
        return np.nan
    idx = np.arange(1, n + 1)
    return (2.0 * np.sum(idx * x) / (n * x.sum())) - (n + 1.0) / n

cap_all = df.loc[df[CAP].notna(), CAP].values
g_all = gini(cap_all)

print()
print("=== RQ2: inequality in capacity ===")
print("Gini of neurologist density across %d countries: %.3f" % (len(cap_all), g_all))
for b in ["High-income", "Low / middle"]:
    sub = df.loc[df[CAP].notna() & (df["income_bin2"] == b), CAP].values
    if len(sub) >= 3:
        print("  within %-14s (n=%d): Gini = %.3f" % (b, len(sub), gini(sub)))

## focal contrast, highest against lowest reported density
hi = df.loc[df[CAP].notna()].nlargest(1, CAP).iloc[0]
lo = df.loc[df[CAP].notna() & (df[CAP] > 0)].nsmallest(1, CAP).iloc[0]
print("  focal contrast: %s %.2f vs %s %.2f per 100k = %.0f-fold"
      % (hi["iso3"], hi[CAP], lo["iso3"], lo[CAP], hi[CAP] / lo[CAP]))

## Lorenz curve
xs = np.sort(cap_all)
cum_c = np.arange(1, len(xs) + 1) / len(xs)
cum_w = np.cumsum(xs) / xs.sum()
cum_c = np.insert(cum_c, 0, 0); cum_w = np.insert(cum_w, 0, 0)

plt.figure(figsize=(7.2, 6))
plt.plot([0, 1], [0, 1], "--", color="black", linewidth=1.2)
plt.plot(cum_c, cum_w, marker="o", markersize=4, color="#2b6cb0")
plt.fill_between(cum_c, cum_w, cum_c, alpha=0.18, color="#2b6cb0")
plt.text(0.52, 0.30, "Gini = %.2f" % g_all, fontsize=13, fontweight="bold")
plt.text(0.30, 0.72, "line of perfect equality\n(every country the same density)",
         fontsize=8, rotation=32)
## annotation placed in the empty area below the curve, with a leader to the
## 50th percentile, so it never prints on top of the Lorenz line itself
half = float(np.interp(0.5, cum_c, cum_w))
plt.annotate("the poorer half of countries\nholds %.0f%% of the workforce" % (100 * half),
             xy=(0.5, half), xytext=(0.72, 0.13), fontsize=8.5, ha="left",
             arrowprops=dict(arrowstyle="->", lw=0.9, color="#555555",
                             connectionstyle="arc3,rad=0.25"))
plt.xlabel("Cumulative share of countries, ranked from lowest density")
plt.ylabel("Cumulative share of neurologists per 100 000")
plt.title("RQ2. Neurological workforce is distributed across countries about as\n"
          "unequally as income within a highly unequal economy (n = %d countries)" % len(cap_all),
          fontsize=11)
plt.figtext(0.01, 0.005,
            "Lorenz curve of WHO GDO neurologist density per 100 000 population (2017). "
            "A Gini of 0 would place the curve on the dashed diagonal;\n"
            "a Gini of 1 would push it into the bottom-right corner. "
            "Highest: %s at %.1f per 100k. Lowest non-zero: %s at %.2f."
            % (hi["iso3"], hi[CAP], lo["iso3"], lo[CAP]),
            fontsize=7, ha="left")
plt.tight_layout(rect=[0, 0.05, 1, 1])
plt.savefig("output/fig2_lorenz_gini.png", dpi=200)
plt.close()

## ===============================================================
## RQ3. Does the gap differ systematically between country types?
## ===============================================================

rq3 = df[df["accessibility_level"].notna() & df["wb_income_group"].notna()].copy()

print()
print("=== RQ3: binned comparisons ===")
print("service-reach sample:", len(rq3), "countries")
ct = pd.crosstab(rq3["income_bin3"], rq3["accessibility_level"])
ct.columns = ["Capital only", "Capital + main cities", "Reaches rural areas"]
print()
print(ct)

tests = []

## (a) Welch t-test on capacity, high-income vs low/middle
a = df.loc[df[CAP].notna() & (df["income_bin2"] == "High-income"), CAP]
b = df.loc[df[CAP].notna() & (df["income_bin2"] == "Low / middle"), CAP]
if len(a) >= 2 and len(b) >= 2:
    t, p = stats.ttest_ind(a, b, equal_var=False)
    u, pu = stats.mannwhitneyu(a, b, alternative="two-sided")
    tests.append(["Neurologist density, high-income vs low/middle",
                  "Welch t-test", f"t = {t:.2f}", f"p = {p:.4f}",
                  f"n = {len(a)} vs {len(b)}; means {a.mean():.2f} vs {b.mean():.2f}"])
    tests.append(["Neurologist density, high-income vs low/middle",
                  "Mann-Whitney U", f"U = {u:.1f}", f"p = {pu:.4f}",
                  f"medians {a.median():.2f} vs {b.median():.2f}"])

## (b) one-way ANOVA on service reach across three income bins
groups = [g["accessibility_level"].values for _, g in rq3.groupby("income_bin3") if len(g) >= 2]
if len(groups) >= 2:
    f, p = stats.f_oneway(*groups)
    h, ph = stats.kruskal(*groups)
    tests.append(["Service reach across three income bins", "One-way ANOVA",
                  f"F = {f:.2f}", f"p = {p:.4f}",
                  "; ".join(f"{k}: mean {g['accessibility_level'].mean():.2f} (n={len(g)})"
                            for k, g in rq3.groupby("income_bin3"))])
    tests.append(["Service reach across three income bins", "Kruskal-Wallis",
                  f"H = {h:.2f}", f"p = {ph:.4f}", "rank-based check on the ANOVA"])

## (c) chi-square on the contingency table
chi2, pchi, dof, _ = stats.chi2_contingency(ct.values)
tests.append(["Service reach by income bin (contingency)", "Chi-square",
              f"chi2 = {chi2:.2f}, df = {dof}", f"p = {pchi:.4f}",
              f"expected counts below 5 in {(stats.chi2_contingency(ct.values)[3] < 5).sum()} of {ct.size} cells"])

t2 = pd.DataFrame(tests, columns=["comparison", "test", "statistic", "p_value", "detail"])
t2.to_csv("output/table2_hypothesis_tests.csv", index=False)
print()
print(t2.to_string(index=False))

## Figure 3
props = (ct.T / ct.sum(axis=1)).T * 100
order = ["Low / lower-middle", "Upper-middle", "High-income"]
props = props.reindex([o for o in order if o in props.index])
ct_o = ct.reindex(props.index)

plt.figure(figsize=(9, 5.8))
bottom = np.zeros(len(props))
shades = ["#c05621", "#dd9a4e", "#2b6cb0"]
for j, col in enumerate(props.columns):
    plt.bar(props.index, props[col], bottom=bottom, color=shades[j], label=col)
    for i, v in enumerate(props[col]):
        if v > 6:
            plt.text(i, bottom[i] + v / 2, "%.0f%%\n(n=%d)" % (v, ct_o[col].iloc[i]),
                     ha="center", va="center", fontsize=8,
                     color="white" if j != 1 else "black")
    bottom += props[col].values
plt.ylabel("% of countries in the income bin")
plt.ylim(0, 108)
plt.title("RQ3. Dementia diagnostic services reach rural areas in most high-income\n"
          "countries and in none of the low or lower-middle income countries sampled",
          fontsize=11)
plt.legend(fontsize=8, loc="upper center", ncol=3, frameon=False)
plt.figtext(0.01, 0.005,
            "WHO Global Dementia Observatory (2017), question 8.3.1, cross-tabulated with World Bank income group from the WHO Neurology Atlas. "
            "n = %d countries with\nboth fields. Chi-square = %.2f, df = %d, p = %.4f. Cell counts are small, so this is a descriptive comparison, not a precise test."
            % (len(rq3), chi2, dof, pchi),
            fontsize=7, ha="left")
plt.tight_layout(rect=[0, 0.05, 1, 1])
plt.savefig("output/fig3_service_reach_by_income.png", dpi=200)
plt.close()

print()
print("figures and tables written to output/")
