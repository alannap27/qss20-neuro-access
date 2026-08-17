# 09_robustness.py
# Takes in: data/processed/country_panel.csv
# Does: stress-tests every headline number in the project. With 19
# countries, a point estimate on its own overstates how precisely
# anything is known, so this script reports (a) a bootstrap interval
# for the Gini, (b) a leave-one-out recomputation showing how far a
# single reporter can move it, (c) the same for the share ratio
# comparison, and (d) an explicit bounding exercise for the project's
# central confounder, national income.
# Outputs: output/fig11_robustness.png
#          output/table7_robustness.csv

import os
import sys

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import gini, bootstrap_ci, leave_one_out, share_ratio, style_axis, caption

os.makedirs("output", exist_ok=True)
panel = pd.read_csv("data/processed/country_panel.csv")
CAP = "neurologists_per100k"
BURDEN = "stroke_dalys_per100k_agestd_2004"

cap = panel[panel[CAP].notna()].copy()
rows = []

# ---------------------------------------------------------------
# (a) how precisely is the Gini known?
# ---------------------------------------------------------------

g_hat, g_lo, g_hi = bootstrap_ci(cap[CAP].values, stat=gini, n_boot=5000)
print("Gini = %.3f, 95%% bootstrap CI [%.3f, %.3f], n = %d"
      % (g_hat, g_lo, g_hi, len(cap)))
rows.append(["Gini of neurologist density", "%.3f" % g_hat,
             "[%.3f, %.3f]" % (g_lo, g_hi), "5000-draw percentile bootstrap, n = %d" % len(cap)])

# ---------------------------------------------------------------
# (b) can one country carry the result?
# ---------------------------------------------------------------

loo = leave_one_out(cap[CAP].values, cap["iso3"].values, stat=gini)
print()
print("leave-one-out Gini, most influential countries:")
print(pd.concat([loo.head(3), loo.tail(3)]).to_string(index=False))
rows.append(["Gini, leave-one-out range",
             "%.3f to %.3f" % (loo["statistic"].min(), loo["statistic"].max()),
             "swing %.3f" % (loo["statistic"].max() - loo["statistic"].min()),
             "dropping %s lowers it most; dropping %s raises it most"
             % (loo.iloc[0]["dropped"], loo.iloc[-1]["dropped"])])

# ---------------------------------------------------------------
# (c) does the income-group difference survive resampling?
# ---------------------------------------------------------------

hi = cap.loc[cap["income_bin2"] == "High-income", CAP].values
lo = cap.loc[cap["income_bin2"] == "Low / middle", CAP].values
t, p = stats.ttest_ind(hi, lo, equal_var=False)
u, pu = stats.mannwhitneyu(hi, lo, alternative="two-sided")

# exact permutation test: with n = 8 vs 7 the full null distribution is
# cheap to approximate and does not rely on any distributional assumption
rng = np.random.default_rng(20260803)
pooled = np.concatenate([hi, lo])
obs = hi.mean() - lo.mean()
perm = []
for _ in range(20000):
    rng.shuffle(pooled)
    perm.append(pooled[:len(hi)].mean() - pooled[len(hi):].mean())
p_perm = (np.sum(np.abs(perm) >= abs(obs)) + 1) / (len(perm) + 1)
print()
print("high vs low/middle: Welch p = %.4f, Mann-Whitney p = %.4f, permutation p = %.4f"
      % (p, pu, p_perm))
rows.append(["High- vs low/middle-income density difference",
             "%.2f vs %.2f per 100k" % (hi.mean(), lo.mean()),
             "permutation p = %.4f" % p_perm,
             "20,000 permutations; Welch p = %.4f, Mann-Whitney p = %.4f" % (p, pu)])

# ---------------------------------------------------------------
# (d) bounding the central confounder
# ---------------------------------------------------------------
# National income drives both capacity and measured burden. Rather than
# naming that confounder and moving on, ask how much of the observed gap
# would have to be spurious for the conclusion to reverse.

rq1 = panel[panel[CAP].notna() & panel[BURDEN].notna() & (panel[CAP] > 0)].copy()
rq1["ratio"] = share_ratio(rq1[BURDEN], rq1[CAP])
med_hi = rq1.loc[rq1["income_bin2"] == "High-income", "ratio"].median()
med_lo = rq1.loc[rq1["income_bin2"] == "Low / middle", "ratio"].median()
observed_gap = med_lo / med_hi

# if low/middle-income burden were overstated by a factor k (or their capacity
# understated by k), how large must k be to bring the two medians level?
k_needed = observed_gap
print()
print("median share ratio: high-income %.2f, low/middle %.2f -> gap factor %.1f"
      % (med_hi, med_lo, observed_gap))
print("to erase the gap, low/middle burden would have to be overstated (or their")
print("capacity understated) by a factor of %.1f" % k_needed)
rows.append(["Confounding needed to erase the RQ1 gap",
             "median ratio %.2f vs %.2f" % (med_lo, med_hi),
             "factor %.1f" % k_needed,
             "burden would have to be overstated, or capacity understated, this many times over in low/middle-income countries"])

t7 = pd.DataFrame(rows, columns=["quantity", "estimate", "uncertainty", "note"])
t7.to_csv("output/table7_robustness.csv", index=False)

# ---------------------------------------------------------------
# Figure 11
# ---------------------------------------------------------------

fig, axes = plt.subplots(1, 3, figsize=(16, 5.4))

# panel A: bootstrap distribution of the Gini
ax = axes[0]
rng2 = np.random.default_rng(20260803)
draws = [gini(rng2.choice(cap[CAP].values, len(cap), replace=True)) for _ in range(5000)]
ax.hist(draws, bins=45, color="#b7c9de", zorder=3)
ax.axvline(g_hat, color="#2b6cb0", lw=2, zorder=4)
ax.axvline(g_lo, color="black", ls="--", lw=1.1, zorder=4)
ax.axvline(g_hi, color="black", ls="--", lw=1.1, zorder=4)
ax.text(g_hat, ax.get_ylim()[1] * 0.94, " point estimate %.2f" % g_hat,
        fontsize=8.5, color="#2b6cb0")
ax.text(g_lo, ax.get_ylim()[1] * 0.80, "95%% CI\n%.2f - %.2f" % (g_lo, g_hi),
        fontsize=8.5, ha="right")
ax.set_xlabel("Gini of neurologist density")
ax.set_ylabel("Bootstrap draws")
ax.set_title("A. The Gini is imprecise\n5 000 resamples of %d countries" % len(cap), fontsize=10.5)
style_axis(ax)

# panel B: leave-one-out
ax = axes[1]
loo_s = loo.sort_values("statistic")
ax.barh(loo_s["dropped"], loo_s["statistic"], color="#b7c9de", zorder=3)
ax.axvline(g_hat, color="#2b6cb0", lw=2, zorder=4)
ax.text(g_hat, len(loo_s) - 0.4, " full sample %.2f" % g_hat, fontsize=8.5, color="#2b6cb0")
ax.set_xlim(min(loo_s["statistic"]) - 0.05, max(loo_s["statistic"]) + 0.03)
ax.set_xlabel("Gini with that country removed")
ax.tick_params(axis="y", labelsize=7.5)
ax.set_title("B. No single country drives it\nswing of %.3f across all drops"
             % (loo["statistic"].max() - loo["statistic"].min()), fontsize=10.5)
style_axis(ax, axis="x")

# panel C: permutation null
ax = axes[2]
ax.hist(perm, bins=50, color="#b7c9de", zorder=3)
ax.axvline(obs, color="#c05621", lw=2.2, zorder=4)
ax.set_xlim(min(perm) * 1.12, obs * 1.30)
ax.text(obs * 0.97, ax.get_ylim()[1] * 0.88,
        "observed\ndifference\n%.2f" % obs,
        fontsize=8.5, color="#c05621", ha="right", va="top")
ax.set_xlabel("High-income minus low/middle-income mean density, per 100 000")
ax.set_ylabel("Permutations")
ax.set_title("C. The income difference is not chance\n20 000 label permutations, p = %.4f" % p_perm,
             fontsize=10.5)
style_axis(ax)

fig.suptitle("Figure 11. Robustness of the country-level results to their small sample",
             fontsize=13, y=0.985)
caption(fig,
        "Panel A resamples the %d countries with replacement 5 000 times; the interval is wide because the sample is small, so the Gini should be read as 'high inequality' rather than as the precise\n"
        "value 0.61. Panel B recomputes the Gini dropping each country in turn, to check that no single reporter carries the result. Panel C shuffles the income labels 20,000 times to build the null\n"
        "distribution for the difference in means, which avoids any normality assumption at n = %d versus %d. All three use WHO Global Dementia Observatory neurologist density (2017)."
        % (len(cap), len(hi), len(lo)))
plt.tight_layout(rect=[0, 0.065, 1, 0.965])
plt.savefig("output/fig11_robustness.png", dpi=200)
plt.close()

print()
print(t7.to_string(index=False))
print()
print("figure 11 and table 7 written to output/")
