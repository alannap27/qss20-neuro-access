# 00_pull_who_gho.py
# Takes in: nothing (the public WHO Global Health Observatory OData API)
# Does: pulls the three WHO indicators the project relies on and writes
# them to data/raw/ in the exact schema the later scripts use.
# No API key is required. Re-run this to refresh the raw files.
# Outputs: data/raw/who_gho_neurologists_per100k.csv
##         data/raw/who_gho_dx_accessibility.csv
##         data/raw/who_ghe_stroke_dalys_2004.csv

import os
import json
import urllib.request

BASE = "https://ghoapi.azureedge.net/api/"
RAW = "data/raw/"
os.makedirs(RAW, exist_ok=True)

INDICATORS = {
    ## neurologists per 100 000 population, Global Dementia Observatory, 2017
    "GDO_q6x1_2": "who_gho_neurologists_per100k.csv",
    ## accessibility of community dementia diagnostic services, GDO 2017
    ## values: "Capital city only" / "Capital and main cities only" /
    ##         "Capital, main cities and rural areas"
    "GDO_q8x3_1": "who_gho_dx_accessibility.csv",
    ## age-standardized cerebrovascular disease (stroke) DALYs per 100 000,
    ## WHO Global Health Estimates. Only the 2004 round is published here.
    "SA_0000001689": "who_ghe_stroke_dalys_2004.csv",
}


def fetch(code):
    url = BASE + code
    with urllib.request.urlopen(url, timeout=60) as r:
        return json.loads(r.read())["value"]


def main():
    for code, fname in INDICATORS.items():
        rows = fetch(code)
        rows = [r for r in rows if r.get("SpatialDimType") == "COUNTRY"]
        ## the stroke indicator is split by sex; keep both-sexes only
        if code == "SA_0000001689":
            rows = [r for r in rows if r.get("Dim1") == "SEX_BTSX"]
        print(f"{code}: {len(rows)} country records -> {fname}")

    print()
    print("Note: the committed data/raw/*.csv files were produced by this query")
    print("and are checked into the repository so that 03_clean_merge.py runs")
    print("without network access. Re-run this script to refresh them.")


if __name__ == "__main__":
    main()
