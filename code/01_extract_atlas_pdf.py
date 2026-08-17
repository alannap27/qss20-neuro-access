## 01_extract_atlas_pdf.py
## Takes in : the WHO/WFN Neurology Atlas 2nd edition PDF (ISBN 978-92-4-156550-9),
##            downloaded separately -- see the data note in README.md
## Does     : parses Annex 1 (pages 67-70 of the PDF) into a country ->
##            WHO region -> World Bank income group crosswalk, repairing the two
##            rows whose country name wraps across a line break
## Outputs  : data/raw/atlas_country_crosswalk.csv

import csv
import os
import sys

import pdfplumber

REGIONS = ["African Region", "Region of the Americas", "Eastern Mediterranean Region",
           "European Region", "South-East Asia Region", "Western Pacific Region"]
INCOMES = ["Low-income", "Lower-middle income", "Upper-middle income", "High-income"]
ANNEX_PAGES = range(66, 70)


def parse(pdf_path):
    rows = []
    with pdfplumber.open(pdf_path) as pdf:
        for i in ANNEX_PAGES:
            for line in (pdf.pages[i].extract_text() or "").split("\n"):
                for reg in REGIONS:
                    if reg in line:
                        country = line.split(reg)[0].strip()
                        rest = line.split(reg)[1].strip()
                        inc = next((x for x in INCOMES if rest.startswith(x)), None)
                        if country and inc:
                            rows.append([country, reg, inc])
                        break
    ## one country name wraps onto a second line in the source PDF
    for r in rows:
        if r[0] == "United Kingdom of Great Britain and":
            r[0] = "United Kingdom of Great Britain and Northern Ireland"
    seen, out = set(), []
    for r in rows:
        if r[0] not in seen:
            seen.add(r[0]); out.append(r)
    return sorted(out)


if __name__ == "__main__":
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else "data/raw/neurology_atlas_2017.pdf"
    if not os.path.exists(pdf_path):
        sys.exit("Atlas PDF not found at %s -- see the data note in README.md" % pdf_path)
    rows = parse(pdf_path)
    print("countries parsed from Annex 1:", len(rows))
    os.makedirs("data/raw", exist_ok=True)
    with open("data/raw/atlas_country_crosswalk_full.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["country", "who_region", "wb_income_group"])
        w.writerows(rows)
    print("written data/raw/atlas_country_crosswalk_full.csv")
    print("NOTE: atlas_country_crosswalk.csv adds ISO3 codes for the subset of")
    print("countries that also appear in the WHO GHO extracts.")
