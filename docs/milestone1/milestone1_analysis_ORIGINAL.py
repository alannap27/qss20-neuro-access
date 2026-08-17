## QSS 20 Final Project -- Milestone 1
## Country-level neurological workforce vs. neurological disease burden
## Starter analysis and visualizations

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

## ---------------------------------------------------------------
## 1. Read in the data extracted from the WHO Neurology Atlas (2017)
## ---------------------------------------------------------------

countries = pd.read_csv("data/atlas_countries.csv")
by_income = pd.read_csv("data/atlas_workforce_by_income.csv")
by_region = pd.read_csv("data/atlas_workforce_by_region.csv")

print("countries:", countries.shape)
print(countries.head())
print()
print(by_income[["income_group", "total_workforce_per100k",
                 "adult_neurologists_per100k", "pct_countries_rural"]])

## ---------------------------------------------------------------
## 2. Descriptive: how the 133 Atlas countries distribute across strata
## ---------------------------------------------------------------

## normalize the income labels in the country crosswalk so they merge
## onto the aggregate tables (the Annex writes "Lower-middle income",
## the results tables write "Lower-middle-income")
label_map = {"Low-income": "Low-income",
             "Lower-middle income": "Lower-middle-income",
             "Upper-middle income": "Upper-middle-income",
             "High-income": "High-income"}
countries["income_group"] = countries["wb_income_group"].map(label_map)

counts = countries.groupby("income_group").size().reset_index(name="n_countries")
merged = counts.merge(by_income, on="income_group", how="left")
merged = merged.sort_values("total_workforce_per100k")
print()
print(merged[["income_group", "n_countries", "total_workforce_per100k",
              "adult_neurologists_per100k", "pct_countries_rural"]])

## the headline gap the project is built around
low = by_income.loc[by_income["income_group"] == "Low-income",
                    "adult_neurologists_per100k"].values[0]
high = by_income.loc[by_income["income_group"] == "High-income",
                     "adult_neurologists_per100k"].values[0]
print()
print("adult neurologist density ratio, high- vs low-income:", round(high / low, 1))

## cross-tab of WHO region by income group, which is the stratification
## the burden merge will eventually be checked against
xtab = pd.crosstab(countries["who_region"], countries["income_group"])
print()
print(xtab)

## ---------------------------------------------------------------
## 3. Figure 1: neurological workforce density by income group
## ---------------------------------------------------------------

plot_inc = by_income[by_income["income_group"] != "Global"]

plt.bar(plot_inc["income_group"], plot_inc["total_workforce_per100k"])
plt.axhline(3.1, linestyle="--", linewidth=1, color="gray")
plt.text(-0.42, 3.3, "global median 3.1", fontsize=8, color="gray", ha="left")
for i, v in enumerate(plot_inc["total_workforce_per100k"]):
    plt.text(i, v + 0.15, str(v), ha="center", fontsize=9)
plt.ylabel("Median workforce per 100 000 population")
plt.xlabel("World Bank income group")
plt.title("Neurological workforce density by income group")
plt.xticks(rotation=20, ha="right", fontsize=8)
plt.tight_layout()
plt.savefig("figures/fig1_workforce_by_income.png", dpi=200)
plt.close()

## ---------------------------------------------------------------
## 4. Figure 2: where those providers actually practise
## ---------------------------------------------------------------

positions = range(len(plot_inc))
width = 0.27
offsets = [-width, 0, width]
cols = ["pct_countries_capital", "pct_countries_other_urban", "pct_countries_rural"]
labels = ["Capital city", "Other urban areas", "Rural areas"]

for off, col, lab in zip(offsets, cols, labels):
    plt.bar([p + off for p in positions], plot_inc[col], width=width, label=lab)
for off, col in zip(offsets, cols):
    for p, v in zip(positions, plot_inc[col]):
        plt.text(p + off, v + 1.5, str(v), ha="center", fontsize=7)
plt.xticks(list(positions), plot_inc["income_group"], rotation=20, ha="right", fontsize=8)
plt.ylabel("% of responding countries")
plt.xlabel("World Bank income group")
plt.title("Where neurologists practise, by income group")
plt.ylim(0, 132)
plt.legend(fontsize=8, loc="upper center", ncol=3, frameon=False)
plt.tight_layout()
plt.savefig("figures/fig2_where_neurologists_practise.png", dpi=200)
plt.close()

print()
print("figures written")
