#!/usr/bin/env bash
# Rebuild every figure and table from the committed raw data.
# Scripts 00-02 are not run here: 00 and 01 refresh inputs from the network /
# the Atlas PDF, and 02 needs your own DHS manifest. Everything else is offline.
set -e
cd "$(dirname "$0")"
for s in 03_clean_merge 04_analyze 05_atlas_descriptives 06_paired_comparison \
         07_regional_and_cadre 08_dhs_coverage 09_robustness; do
  echo "=== running code/${s}.py ==="
  python3 "code/${s}.py" > "output/log_${s}.txt" 2>&1
done
echo
echo "done. figures and tables in output/"
ls -1 output/*.png output/*.csv
