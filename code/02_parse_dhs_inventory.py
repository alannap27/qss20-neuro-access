## 02_parse_dhs_inventory.py
## Takes in : the DHS Program download manifest (urlslist_*.txt) issued to an
##            approved DHS account. The manifest is a list of authenticated
##            download URLs; this script reads the FILENAMES only and does not
##            download anything.
## Does     : decodes the DHS filename convention CCTTVVFL.zip into country,
##            file type and survey phase, and summarises coverage -- in
##            particular which countries have GE (GPS cluster) files
## Outputs  : data/processed/dhs_inventory.csv

import csv
import os
import re
import sys
from collections import Counter

PATTERN = re.compile(
    r"Filename=([A-Z]{2})([A-Z]{2})(\w{2})FL\.zip.*?Ctry_Code=(\w+).*?surv_id=(\d+)")

FILE_TYPES = {
    "IR": "Individual recode (women 15-49)", "MR": "Men's recode",
    "HR": "Household recode", "PR": "Household member recode",
    "BR": "Births recode", "KR": "Children's recode", "CR": "Couples recode",
    "GE": "Geographic / GPS cluster coordinates", "HW": "Height and weight",
    "WI": "Wealth index", "SQ": "Service provision", "IQ": "Interview questionnaire",
}


def main(path):
    rows = []
    for line in open(path):
        m = PATTERN.search(line.strip())
        if m:
            cc, ftype, phase, ctry, surv = m.groups()
            rows.append(dict(dhs_cc=cc, ctry_code=ctry, surv_id=surv,
                             file_type=ftype, phase=phase, url=line.strip()))

    print("datasets in manifest:", len(rows))
    print("distinct countries:", len({r["dhs_cc"] for r in rows}))
    print("distinct surveys:", len({(r["dhs_cc"], r["surv_id"]) for r in rows}))
    print()
    print("file types:")
    for k, v in Counter(r["file_type"] for r in rows).most_common():
        print("  %-4s %-45s %d" % (k, FILE_TYPES.get(k, ""), v))
    gps = {r["dhs_cc"] for r in rows if r["file_type"] == "GE"}
    print()
    print("countries with GPS (GE) files:", len(gps))

    os.makedirs("data/processed", exist_ok=True)
    with open("data/processed/dhs_inventory.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["dhs_cc", "ctry_code", "surv_id",
                                          "file_type", "phase", "url"])
        w.writeheader(); w.writerows(rows)
    print("written data/processed/dhs_inventory.csv")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/raw/urlslist.txt")
