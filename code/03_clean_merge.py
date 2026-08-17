## 03_clean_merge.py
## Takes in : data/raw/who_gho_neurologists_per100k.csv
##            data/raw/who_gho_dx_accessibility.csv
##            data/raw/who_ghe_stroke_dalys_2004.csv
##            data/raw/atlas_country_crosswalk.csv
## Does     : harmonises WHO placeholder strings to missing, converts the
##            accessibility question to an ordered scale, left joins burden and
##            income group onto the capacity records, and reports row counts
##            before and after every join
## Outputs  : data/processed/country_panel.csv

import os
import pandas as pd

RAW = "data/raw/"
OUT = "data/processed/"
os.makedirs(OUT, exist_ok=True)

## WHO encodes non-responses as literal strings inside a numeric field
MISSING_STRINGS = ["Not available", "Not applicable", "No data", ""]

## ---------------------------------------------------------------
## 1. Capacity: neurologists per 100 000 population
## ---------------------------------------------------------------

neuro = pd.read_csv(RAW + "who_gho_neurologists_per100k.csv")
print("neurologist records pulled:", len(neuro))

neuro["neurologists_per100k"] = pd.to_numeric(
    neuro["value_raw"].where(~neuro["value_raw"].isin(MISSING_STRINGS)), errors="coerce")
n_usable = neuro["neurologists_per100k"].notna().sum()
print("  with a usable numeric value:", n_usable)
print("  dropped as Not available/Not applicable:", len(neuro) - n_usable)
neuro = neuro[neuro["neurologists_per100k"].notna()].copy()

## ---------------------------------------------------------------
## 2. Distribution: where dementia diagnostic services reach
## ---------------------------------------------------------------

acc = pd.read_csv(RAW + "who_gho_dx_accessibility.csv")
print()
print("accessibility records pulled:", len(acc))

## the question is ordered: services reaching rural areas strictly dominate
## services confined to the capital
ACC_SCALE = {
    "Capital city only": 1,
    "Capital and main cities only": 2,
    "Capital, main cities and rural areas": 3,
}
acc["accessibility_level"] = acc["accessibility_raw"].map(ACC_SCALE)
n_acc = acc["accessibility_level"].notna().sum()
print("  with a usable ordered value:", n_acc)
print("  dropped as Not available/Not applicable:", len(acc) - n_acc)
acc = acc[acc["accessibility_level"].notna()].copy()

## ---------------------------------------------------------------
## 3. Burden and income group
## ---------------------------------------------------------------

burden = pd.read_csv(RAW + "who_ghe_stroke_dalys_2004.csv")
cross = pd.read_csv(RAW + "atlas_country_crosswalk.csv")
print()
print("burden records:", len(burden), " crosswalk records:", len(cross))

## ---------------------------------------------------------------
## 4. Assemble the country panel
## ---------------------------------------------------------------

panel = pd.merge(neuro[["iso3", "who_region", "neurologists_per100k"]],
                 acc[["iso3", "accessibility_level", "accessibility_raw"]],
                 on="iso3", how="outer")
print()
print("rows after outer join of capacity and accessibility:", len(panel))

before = len(panel)
panel = panel.merge(burden, on="iso3", how="left")
print("rows after left join of burden:", len(panel), "(was", before, ")")
print("  matched a burden value:", panel["stroke_dalys_per100k_agestd_2004"].notna().sum())

before = len(panel)
panel = panel.merge(cross[["iso3", "country", "wb_income_group"]], on="iso3", how="left")
print("rows after left join of crosswalk:", len(panel), "(was", before, ")")
print("  matched an income group:", panel["wb_income_group"].notna().sum())
print("  no income group (country absent from the WHO Atlas 133):",
      panel["wb_income_group"].isna().sum())

## two-level and three-level bins. Country-level regressions on this many
## observations are underpowered, so the analysis compares binned groups
## rather than fitting a slope across countries.
THREE = {"Low-income": "Low / lower-middle",
         "Lower-middle income": "Low / lower-middle",
         "Upper-middle income": "Upper-middle",
         "High-income": "High-income"}
panel["income_bin3"] = panel["wb_income_group"].map(THREE)
panel["income_bin2"] = panel["wb_income_group"].map(
    lambda x: "High-income" if x == "High-income" else ("Low / middle" if pd.notna(x) else None))

panel = panel.sort_values("iso3")
panel.to_csv(OUT + "country_panel.csv", index=False)

print()
print("=== country_panel.csv ===")
print("rows:", len(panel))
print("with capacity (neurologist density):", panel["neurologists_per100k"].notna().sum())
print("with distribution (accessibility):", panel["accessibility_level"].notna().sum())
print("with both capacity and burden:",
      (panel["neurologists_per100k"].notna() & panel["stroke_dalys_per100k_agestd_2004"].notna()).sum())
print()
print(panel["income_bin3"].value_counts(dropna=False))
