# Neurological care capacity vs. neurological disease burden

QSS 20 final project, Milestone 2. Alanna Polyak, Dartmouth College.

Does the world's neurological workforce sit where the neurological disease
burden is? This repository assembles four public sources to measure that gap,
characterise how unequally capacity is distributed, and test whether the pattern
differs systematically between country types.

The analysis is **descriptive throughout**. National income drives both workforce
capacity and *measured* burden, and measured burden itself depends on the
diagnostic capacity that is the exposure of interest. No causal effect is
estimated or implied. Section [Bounding the confounder](#bounding-the-confounder)
states how large that confounding would have to be to overturn the main result.

---

## Contents

- [Two levels of evidence](#two-levels-of-evidence)
- [Research questions and headline findings](#research-questions-and-headline-findings)
- [The gap metric, defined](#the-gap-metric-defined)
- [Bounding the confounder](#bounding-the-confounder)
- [Figure index](#figure-index)
- [Table index](#table-index)
- [Scripts](#scripts)
- [Data](#data)
- [Known limitations](#known-limitations)

---

## Two levels of evidence

The project works at two scales, and every substantive claim is checked at both.

**Aggregate.** The WHO/WFN Neurology Atlas reports medians by income group and
WHO region across **114 responding countries**. Six times the country-level
sample, so it establishes the gradient securely — but it cannot identify
individual countries or be linked to burden.

**Country level.** The WHO Global Dementia Observatory reports country-by-country
values, which is what makes the burden-to-capacity ratio and the Gini possible,
but only **19 countries** report neurologist density.

Figures 6 and 7 set the two instruments side by side. They disagree on level, for
a documented reason — the Atlas counts neurologists, neurosurgeons and child
neurologists, the GDO counts neurologists only — and agree on direction and
steepness. Figure 8 shows the regional medians converging: the GDO median for the
European Region is 6.01 per 100,000 against the Atlas adult-neurologist median of
6.60, and for South-East Asia 0.08 against 0.10. That agreement is the main
defence against the small-*n* objection the country-level work would otherwise
face.

---

## Research questions and headline findings

### RQ1. Is neurological workforce capacity aligned with neurological disease burden?

No, and the misalignment is large. On the burden-to-capacity **share ratio**
(defined below), the median high-income country sits at **0.38** and the median
low- or middle-income country at **13.1** — a 34-fold difference in how thinly
the same workforce is spread. Myanmar (69.7), Bangladesh (49.1) and Togo (43.9)
are the extremes; Switzerland (0.07) and the Netherlands (0.25) the other end.
Eswatini and Fiji report **zero** neurologists and cannot be placed on the scale
at all, while carrying stroke DALY rates of 994 and 1,536 per 100,000.

→ `output/fig1_alignment_ratio.png`

### RQ2. How unequally is that capacity distributed?

The Gini coefficient of neurologist density across the 19 reporting countries is
**0.61**, with a 95% bootstrap interval of **[0.43, 0.73]** — high inequality,
imprecisely estimated. The lower half of countries holds about **6%** of the
sampled workforce. Inequality is far greater between income groups than within
them: Gini 0.27 within high-income countries, 0.49 within low- and middle-income
countries. Focal contrast: Switzerland 13.10 per 100,000 against Myanmar 0.07, a
**187-fold** difference. Dropping any single country moves the Gini by at most
0.06, so no one reporter carries the result.

→ `output/fig2_lorenz_gini.png`, `output/fig11_robustness.png`

### RQ3. Does the gap differ systematically between country types?

Yes. Country-level regressions on 19 to 35 observations would be underpowered, so
countries are binned and compared directly.

| Comparison | Test | Result |
|---|---|---|
| Neurologist density, high-income vs low/middle | Welch *t* | *t* = 4.29, **p = 0.0031** |
| same | Mann-Whitney *U* | **p = 0.0003** |
| same | 20,000-draw permutation | **p = 0.0002** |
| Service reach across three income bins | One-way ANOVA | *F* = 5.74, **p = 0.0074** |
| same | Kruskal-Wallis | *H* = 9.44, **p = 0.0089** |
| Service reach × income bin | Chi-square | χ² = 11.81, df = 4, **p = 0.0188** |

Dementia diagnostic services reach rural areas in **77%** of high-income
countries and in **none** of the four low or lower-middle income countries
sampled. The chi-square has six of nine cells with expected counts below 5, which
is why the rank-based and permutation tests are reported alongside it.

→ `output/fig3_service_reach_by_income.png`, `output/fig7_paired_rural_access.png`

### Supporting finding: the gradient steepens with subspecialisation

| Cadre | Low-income | High-income | Ratio |
|---|---|---|---|
| Total neurological workforce | 0.100 | 7.10 | **71×** |
| Neurosurgeons | 0.020 | 1.24 | **62×** |
| Adult neurologists | 0.030 | 4.75 | **158×** |
| Child neurologists | 0.002 | 0.39 | **195×** |

The rarer the specialism, the steeper the income gradient.
→ `output/fig9_cadre_gradient.png`, `output/table3_atlas_gradients.csv`

---

## The gap metric, defined

The **burden-to-capacity share ratio** for a country is

```
(that country's share of the sample's total stroke DALY rate)
-------------------------------------------------------------
(that country's share of the sample's total neurologist density)
```

Read it like this:

- **1.0** — the country holds exactly as large a share of the sample's stroke
  burden as it holds of the sample's neurological workforce. Burden and capacity
  are matched.
- **1.2** — it carries 20% more of the burden than its share of the workforce.
- **13.1** — it carries thirteen times as large a share of the burden as of the
  workforce; the same workforce stretched over thirteen times the need.
- **below 1.0** — it holds more of the workforce than of the burden.

The ratio is scale-free, so it does not depend on the units of either input, and
is directly comparable across countries. It is undefined where capacity is zero;
those countries are reported separately rather than dropped. Implemented in
`code/utils.py::share_ratio`.

---

## Bounding the confounder

Naming a confounder in a limitations section is not the same as accounting for
it. National income drives both capacity and measured burden, so the question is
how much of the observed gap would have to be spurious for the conclusion to
reverse.

The median share ratio is 0.38 in high-income countries and 13.12 in low- and
middle-income countries — a factor of **34.3**. For those two medians to level,
burden in low- and middle-income countries would have to be **overstated by a
factor of 34**, or their capacity **understated by a factor of 34**. Measurement
error of that magnitude is not plausible in either direction: under-diagnosis in
low-capacity settings would push measured burden *down*, not up, which widens the
true gap rather than narrowing it.

→ `output/table7_robustness.csv`

---

## Figure index

| # | File | Shows | n |
|---|---|---|---|
| 1 | `fig1_alignment_ratio.png` | burden-to-capacity share ratio per country, log scale | 17 |
| 2 | `fig2_lorenz_gini.png` | Lorenz curve and Gini of neurologist density | 19 |
| 3 | `fig3_service_reach_by_income.png` | where dementia diagnostic services reach, by income bin | 35 |
| 4 | `fig4_atlas_workforce_by_income.png` | Atlas median workforce density by income group | 114 |
| 5 | `fig5_atlas_where_neurologists_practise.png` | Atlas capital / urban / rural practice shares | 114 |
| 6 | `fig6_paired_workforce_gradient.png` | **paired** — Atlas medians beside GDO country values | 114 / 15 |
| 7 | `fig7_paired_rural_access.png` | **paired** — Atlas rural practice beside GDO service reach | 114 / 35 |
| 8 | `fig8_regional_gradient.png` | workforce by WHO region, Atlas bars with GDO countries overlaid | 114 / 19 |
| 9 | `fig9_cadre_gradient.png` | gradient by cadre on a log axis | 93–114 |
| 10 | `fig10_dhs_coverage.png` | DHS holdings, GPS availability, and the binding constraint | 106 |
| 11 | `fig11_robustness.png` | bootstrap, leave-one-out, and permutation checks | 19 |

Every figure carries its own source note, sample size, and a plain-language
reading of any reference line, so a reader skimming only the figures can follow
the argument.

## Table index

| # | File | Contents |
|---|---|---|
| 1 | `table1_analysis_sample.csv` | what the analysis sample contains, source by source |
| 2 | `table2_hypothesis_tests.csv` | all RQ3 test statistics with detail |
| 3 | `table3_atlas_gradients.csv` | per-cadre absolute gap and high-to-low ratio |
| 4 | `table4_paired_instruments.csv` | what each instrument contributes and where it fails |
| 5 | `table5_regional_comparison.csv` | Atlas vs GDO by WHO region |
| 6 | `table6_dhs_coverage.csv` | DHS coverage metrics |
| 7 | `table7_robustness.csv` | bootstrap intervals, leave-one-out swing, confounding bound |

---

## Scripts

`code/utils.py` holds every shared function — the house plotting style, the WHO
placeholder-string cleaner, the income binner, and the three metrics
(`share_ratio`, `gini`, `bootstrap_ci`). Numbered scripts import from it and own
their own file I/O.

| Script | Takes in | Does | Outputs |
|---|---|---|---|
| [`utils.py`](code/utils.py) | — | shared metrics, cleaning helpers, plot style | imported, writes nothing |
| [`00_pull_who_gho.py`](code/00_pull_who_gho.py) | public WHO GHO OData API, no key | pulls the three WHO indicators | `data/raw/who_*.csv` |
| [`01_extract_atlas_pdf.py`](code/01_extract_atlas_pdf.py) | Neurology Atlas PDF | parses Annex 1 into a country → region → income crosswalk, repairing wrapped rows | `data/raw/atlas_country_crosswalk_full.csv` |
| [`02_parse_dhs_inventory.py`](code/02_parse_dhs_inventory.py) | DHS manifest `urlslist_*.txt` | decodes filenames into country / type / phase; downloads nothing | `data/processed/dhs_inventory.csv` |
| [`03_clean_merge.py`](code/03_clean_merge.py) | the `data/raw/` files | cleans placeholders, orders the service-reach scale, joins burden and income group, prints row counts before and after every join | `data/processed/country_panel.csv` |
| [`04_analyze.py`](code/04_analyze.py) | the country panel | share ratio, Gini and Lorenz, binned t-test / ANOVA / chi-square | figs 1–3, tables 1–2 |
| [`05_atlas_descriptives.py`](code/05_atlas_descriptives.py) | Atlas aggregate tables | the two 114-country gradients and per-cadre ratios | figs 4–5, table 3 |
| [`06_paired_comparison.py`](code/06_paired_comparison.py) | panel + Atlas | sets each aggregate descriptive beside its country-level counterpart | figs 6–7, table 4 |
| [`07_regional_and_cadre.py`](code/07_regional_and_cadre.py) | Atlas regional + panel | regional gradient with countries overlaid; cadre gradient on a log axis | figs 8–9, table 5 |
| [`08_dhs_coverage.py`](code/08_dhs_coverage.py) | DHS inventory + panel | what the approved DHS holdings can support, and why WHO is the binding constraint | fig 10, table 6 |
| [`09_robustness.py`](code/09_robustness.py) | the country panel | bootstrap CI, leave-one-out, permutation test, confounding bound | fig 11, table 7 |

### Repository layout

```
code/                 numbered scripts plus the shared utils.py
data/raw/             inputs as pulled, unmodified
data/processed/       merged analysis file and DHS inventory
output/               11 figures, 7 tables, run logs
docs/milestone1/      the Milestone 1 writeup (.tex and .pdf) and the
                      original standalone script that produced its two
                      figures, kept for provenance
run_all.sh            rebuilds every figure and table offline
```

`docs/milestone1/milestone1_analysis_ORIGINAL.py` is superseded by
`code/05_atlas_descriptives.py`, which produces the same two figures with
response counts, ratio annotations and full source captions added. It is kept so
the Milestone 1 PDF remains reproducible as submitted.

### Running it

```bash
pip install pandas numpy matplotlib scipy pdfplumber
bash run_all.sh
```

or individually:

```bash
python code/03_clean_merge.py
python code/04_analyze.py
python code/05_atlas_descriptives.py
python code/06_paired_comparison.py
python code/07_regional_and_cadre.py
python code/08_dhs_coverage.py
python code/09_robustness.py
```

Scripts `03`–`09` run **offline** from the committed raw files. `00` and `01`
only need re-running to refresh inputs, and `02` needs your own DHS manifest.

---

## Data

All raw inputs are committed to `data/raw/` — small, public, aggregate. Nothing
here is restricted or individual-level.

| Source | Gives | Coverage | Year |
|---|---|---|---|
| WHO Global Dementia Observatory `GDO_q6x1_2` | neurologists per 100,000 | 21 records, **19 usable** | 2017 |
| WHO Global Dementia Observatory `GDO_q8x3_1` | where dementia diagnostic services reach | 61 records, **47 usable** | 2017 |
| WHO Global Health Estimates `SA_0000001689` | age-standardised stroke DALYs per 100,000 | 62 countries | **2004** |
| WHO/WFN Neurology Atlas, Annex 1 | WHO region and World Bank income group | 133 countries; 45 matched to ISO3 | 2017 |
| WHO/WFN Neurology Atlas, Tables 2–3, Figs 11–12, 15–16 | median density and practice location by income group and region | 114 responding countries | 2017 |
| DHS Program manifest | survey and GPS-file coverage inventory | 106 countries, 443 surveys, **62 with GPS** | various |

**Atlas PDF.** Not committed (5.5 MB WHO publication). Download and place at
`data/raw/neurology_atlas_2017.pdf` before running `01`.

**DHS microdata.** Not committed and not downloadable from here. DHS data require
a per-project application; the manifest contains authenticated URLs tied to an
approved account and is gitignored. Only the derived coverage inventory is
included, and it contains no survey responses.

---

## Known limitations

1. **Temporal mismatch.** Capacity is 2017, burden is 2004 — the only round of
   the WHO stroke DALY series available through this API. Thirteen years is long
   enough for both to move. Country *rankings* are likely more stable than
   levels, but this is the weakest joint in the analysis and the reason RQ1 is
   framed as describing a gap rather than estimating one. Replacing this with an
   IHME GBD extract is the single highest-value next step; `03_clean_merge.py`
   needs only a burden file with an `iso3` column.
2. **Small, self-selected samples.** 19 countries report neurologist density; 35
   have both service reach and an income group. Countries answering the WHO
   questionnaire plausibly have stronger health information systems, biasing the
   sample toward better-resourced countries and *understating* the true gap.
3. **Stroke stands in for neurological burden.** Cerebrovascular disease is one
   neurological cause among many.
4. **Small cell counts.** Six of nine cells in the RQ3 contingency table have
   expected counts below 5, so the chi-square is indicative; rank-based and
   permutation tests are reported alongside.
5. **Self-reported and unaudited.** Both WHO instruments are questionnaires
   completed by ministry focal points, with no independent verification and no
   full-time-equivalent adjustment.
6. **Coverage gap in the crosswalk.** 17 of the 62 WHO-extract countries are
   absent from the Atlas 133 and therefore have no income group; they appear in
   figures as "not classified" rather than being dropped.
