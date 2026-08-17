# 08_dhs_coverage.py
# Takes in: data/processed/dhs_inventory.csv  (built by 02_parse_dhs_inventory.py)
#           data/processed/country_panel.csv
# Does: characterizes what the approved DHS holdings can and cannot support.
# DHS is the intended source of the within-country spatial component
# of this project, GPS cluster coordinates give distance to care, 
# so this script establishes which countries have GPS files, how the
# survey program is distributed across WHO regions, and where DHS
# coverage overlaps the countries for which WHO capacity data exists.
# Outputs: output/fig10_dhs_coverage.png
#          output/table6_dhs_coverage.csv

import os
import sys

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import style_axis, caption

os.makedirs("output", exist_ok=True)

dhs = pd.read_csv("data/processed/dhs_inventory.csv")
panel = pd.read_csv("data/processed/country_panel.csv")
CAP = "neurologists_per100k"

FILE_TYPES = {
    "IR": "Individual recode (women 15-49)", "KR": "Children's recode",
    "HR": "Household recode", "BR": "Births recode",
    "PR": "Household member recode", "GE": "Geographic / GPS clusters",
    "MR": "Men's recode", "CR": "Couples recode", "HW": "Height and weight",
    "WI": "Wealth index", "HH": "Household (legacy)", "SQ": "Service provision",
    "IQ": "Interview questionnaire", "VR": "Verbatim responses",
    "OD": "Other documentation", "VA": "Verbal autopsy", "ML": "Malaria",
}

n_countries = dhs["dhs_cc"].nunique()
n_surveys = dhs.groupby(["dhs_cc", "surv_id"]).ngroups
gps_countries = set(dhs.loc[dhs["file_type"] == "GE", "dhs_cc"])

print("datasets in manifest:", len(dhs))
print("countries:", n_countries, " surveys:", n_surveys)
print("countries with GPS (GE) files:", len(gps_countries))

## surveys per country, and whether GPS is available
per_country = dhs.groupby("dhs_cc").agg(
    n_datasets=("file_type", "size"),
    n_surveys=("surv_id", "nunique"),
).reset_index()
per_country["has_gps"] = per_country["dhs_cc"].isin(gps_countries)

# ---------------------------------------------------------------
# Figure 10: three panels describing the DHS holdings
# ---------------------------------------------------------------

fig, axes = plt.subplots(1, 3, figsize=(16, 5.6))

# panel A: dataset counts by file type
ax = axes[0]
counts = dhs["file_type"].value_counts()
counts = counts[counts >= 10].sort_values()
cols = ["#c05621" if k == "GE" else "#b7c9de" for k in counts.index]
ax.barh([FILE_TYPES.get(k, k) for k in counts.index], counts.values,
        color=cols, zorder=3)
for i, v in enumerate(counts.values):
    ax.text(v + 5, i, str(v), va="center", fontsize=8.5)
ax.set_xlabel("Number of datasets in the approved manifest")
ax.set_xlim(0, counts.max() * 1.18)
ax.set_title("A. What the manifest contains\n%d datasets across %d surveys"
             % (len(dhs), n_surveys), fontsize=10.5)
ax.tick_params(axis="y", labelsize=8)
style_axis(ax, axis="x")

# panel B: how many surveys each country has, split by GPS availability
ax = axes[1]
bins = np.arange(0.5, per_country["n_surveys"].max() + 1.5, 1)
ax.hist([per_country.loc[per_country["has_gps"], "n_surveys"],
         per_country.loc[~per_country["has_gps"], "n_surveys"]],
        bins=bins, stacked=True, color=["#c05621", "#b7c9de"],
        label=["GPS files available", "No GPS files"], zorder=3)
ax.set_xlabel("Number of DHS surveys held for the country")
ax.set_ylabel("Number of countries")
ax.legend(fontsize=8.5, frameon=False)
ax.set_title("B. Repeat coverage by country\n%d of %d countries have GPS clusters"
             % (len(gps_countries), n_countries), fontsize=10.5)
style_axis(ax)

# panel C: overlap between DHS coverage and WHO capacity data
ax = axes[2]
who_cap = set(panel.loc[panel[CAP].notna(), "iso3"])
who_acc = set(panel.loc[panel["accessibility_level"].notna(), "iso3"])
overlap = pd.Series({
    "DHS\nany survey": n_countries,
    "DHS\nwith GPS": len(gps_countries),
    "WHO\nservice reach": len(who_acc),
    "WHO\nneurologist\ndensity": len(who_cap),
})
ax.bar(range(len(overlap)), overlap.values,
       color=["#b7c9de", "#c05621", "#7aa6cf", "#2b6cb0"], zorder=3, width=0.62)
for i, v in enumerate(overlap.values):
    ax.text(i, v + 1.5, str(v), ha="center", fontsize=10.5, fontweight="bold")
ax.set_xticks(range(len(overlap)))
ax.set_xticklabels(overlap.index, fontsize=8.5)
ax.set_ylabel("Number of countries")
ax.set_ylim(0, max(overlap.values) * 1.2)
ax.set_title("C. The binding constraint is WHO, not DHS\ncountry counts by data source",
             fontsize=10.5)
style_axis(ax)

fig.suptitle("Figure 10. The approved DHS holdings are broad; the WHO capacity data are the limiting factor",
             fontsize=13, y=0.985)
caption(fig,
        "Derived from the filenames in the approved DHS Program download manifest. No survey data were downloaded or read; the DHS filename convention CCTTVVFL.zip encodes country (CC), file type (TT)\n"
        "and survey phase (VV), which is sufficient to build a coverage inventory. GE files carry displaced GPS cluster coordinates and are the input for the planned distance-to-care measure. Panel C is the\n"
        "reason the country-level analysis in Figures 1-3 is small: DHS covers %d countries, but only %d have a WHO neurologist-density value to link them to."
        % (n_countries, len(who_cap)))
plt.tight_layout(rect=[0, 0.065, 1, 0.965])
plt.savefig("output/fig10_dhs_coverage.png", dpi=200)
plt.close()

# ---------------------------------------------------------------
# Table 6
# ---------------------------------------------------------------

t6 = pd.DataFrame({
    "metric": ["Datasets in manifest", "Distinct countries", "Distinct surveys",
               "Countries with GPS (GE) files", "Countries with 1 survey only",
               "Countries with 5+ surveys", "Median surveys per country",
               "WHO countries with neurologist density",
               "WHO countries with service-reach level"],
    "value": [len(dhs), n_countries, n_surveys, len(gps_countries),
              int((per_country["n_surveys"] == 1).sum()),
              int((per_country["n_surveys"] >= 5).sum()),
              float(per_country["n_surveys"].median()),
              len(who_cap), len(who_acc)],
})
t6.to_csv("output/table6_dhs_coverage.csv", index=False)
print()
print(t6.to_string(index=False))
print()
print("figure 10 and table 6 written to output/")
