# Global Banking Sector Stability Around Systemic Crises (2000-2023)

A cross-country empirical econometrics pipeline investigating whether financial development level buffered banks against two systemic shocks — the 2008 Global Financial Crisis and the 2020 COVID-19 shock — using real World Bank panel data.

**This project is implemented independently in both Python and R**, using the identical research design and econometric methodology in each language, then cross-checked against each other. The goal was not just to build the pipeline twice, but to test a real research question: *if you run the same empirical design through two completely different toolchains, do you get the same answer?*

## Research Question

Did high-income economies' banking sectors remain more stable than emerging market economies' banking sectors after the 2008 and 2020 systemic shocks?

Tested using **Bank Z-score** — the standard academic measure of banking sector stability, which combines a banking system's capital buffer and profitability with return volatility into a single "distance to insolvency" score.

## Data Source

- **World Bank Global Financial Development Database (GFDD)** — bank-level stability, capital, liquidity, and profitability indicators
- **World Bank World Development Indicators (WDI)** — macroeconomic controls (GDP growth, inflation)
- Coverage: ~150 countries, 2000-2023
- Accessed via the free, public World Bank API — Python via `wbgapi`, R via `wbstats`

## Two Implementations, One Design

| | Python | R |
|---|---|---|
| **Location** | repo root (`01_fetch_data.py`, etc.) | [`/r`](./r) |
| Data collection | `wbgapi` | `wbstats` |
| Data wrangling | `pandas` | `dplyr` / `tidyr` |
| Panel econometrics | `linearmodels` | `plm` |
| Clustered standard errors | `linearmodels` cov_type | `sandwich` + `lmtest` |
| Word document + tables | `python-docx` | `officer` + `flextable` |
| Figures | `matplotlib` | `ggplot2` |

Both versions pull data from the same World Bank source, run the same seven-table empirical pipeline, and produce the same five figures — built independently in each language's idiomatic style, not translated line-by-line.

---

## Python vs R: Do the Results Agree?

**Short answer: yes, on every substantive conclusion — with one genuine, explainable exception.**

### 1. Sample sizes are close but not identical

| | Python (Emerging) | R (Emerging) | Python (High income) | R (High income) |
|---|---|---|---|---|
| Bank Z-score N | 1,964 | 1,909 | 1,242 | 1,225 |
| Bank Z-score Mean | 16.242 | 16.337 | 16.202 | 16.282 |

Row counts differ by roughly 1-3%. This is expected, not a bug: `wbgapi` and `wbstats` are two independent wrappers around the same World Bank API, pulled on different dates, and can return marginally different snapshots of the database as the World Bank periodically revises historical figures. The means themselves are nearly identical (within ~0.1 points on a ~16-point scale).

### 2. Structural break test — same conclusion, close statistics

| Crisis | Python F-stat | Python p-value | R F-stat | R p-value | Conclusion |
|---|---|---|---|---|---|
| GFC (2008) | 3.976 | 0.037 | 4.509 | 0.026 | **Both: significant break** |
| COVID (2020) | — (too few post obs.) | — | — (too few post obs.) | — | **Both: inconclusive** — GFDD data only extends to ~2021 |

### 3. Panel Fixed Effects regression — same signs, same significance pattern

| Variable | Python FE coef. | Python p | R FE coef. | R p | Agreement |
|---|---|---|---|---|---|
| capital_to_assets | -0.045 | 0.195 | -0.043 | 0.205 | Same sign, both insignificant |
| npl_ratio | -0.003 | 0.675 | -0.004 | 0.590 | Same sign, both insignificant |
| **roa** | **0.226** | **0.026** | **0.216** | **0.021** | **Same sign, both significant** |
| liquid_to_deposits | -0.022 | 0.072 | -0.021 | 0.065 | Same sign, both borderline |
| **gdp_growth** | **0.092** | **0.007** | **0.092** | **0.005** | **Same sign, both significant, near-identical coefficient** |
| inflation | 0.028 | 0.219 | 0.033 | 0.115 | Same sign, both insignificant |

Every coefficient has the same sign in both languages, and the two variables that matter statistically (ROA and GDP growth) are significant in both — with the GDP growth coefficient essentially identical (0.092 in both).

### 4. Difference-in-Differences — same sign, same (in)significance, close magnitude

| Crisis | Python coef. | Python p | R coef. | R p |
|---|---|---|---|---|
| GFC (2008) | 0.177 | 0.811 | 0.150 | 0.837 |
| COVID (2020) | -0.289 | 0.643 | -0.224 | 0.711 |

Both languages agree: **neither crisis produces a statistically significant DiD effect** in this specification, and the sign pattern is identical (slightly positive for 2008, negative for 2020) in both.

### 5. Robustness checks — same story, both languages

| Check | Python coef. / p | R coef. / p |
|---|---|---|
| Main DiD | 0.177 / 0.811 | 0.150 / 0.837 |
| Placebo test (2004) | 0.294 / 0.752 | 0.281 / 0.759 |
| Winsorized | 0.143 / 0.835 | 0.114 / 0.867 |

Both versions show the placebo test finding no effect either — exactly what you want to see, since it means the main result isn't a statistical artifact of the modeling approach.

### 6. The one real difference: the Hausman test

| | Python | R |
|---|---|---|
| Hausman result | **Inconclusive** — variance-difference matrix not positive definite | **Valid** — chi-sq = 94.932, p < 0.001, favors Fixed Effects |

This is a genuine, worth-explaining discrepancy rather than a mistake in either script. The Python version computes the Hausman statistic manually from the raw FE/RE coefficient and covariance matrices; in finite samples, especially with clustered standard errors, that variance-difference matrix can fail to be positive semi-definite, which makes the test numerically invalid — and the script is designed to report "Inconclusive" rather than output a misleading number in that case. R's `plm::phtest()` uses a more numerically robust internal implementation that produced a valid statistic here. **Both point toward the same practical conclusion** (Fixed Effects is the more defensible choice given the panel structure), but only R's test could say so with a formal p-value in this run.

### 7. A shared data-quality note (present in both languages identically)

The `npl_ratio` and `liquid_to_deposits` variables have implausible values in both Python and R output (NPL ratio means over 100%, max values above 800%). This isn't a coding bug — it's a known artifact in the raw World Bank GFDD series for a handful of countries with irregular reporting. Since it appears identically in both independent pulls, it confirms the two pipelines are reading the same underlying data correctly; it's a data-cleaning caveat worth flagging in any write-up rather than a pipeline error.

---

## What This Comparison Demonstrates

Running the identical research design through two independent toolchains and getting matching signs, matching significance patterns, and near-identical coefficients on every substantive test is a real (informal) robustness check — it shows the empirical result isn't an artifact of one specific software implementation. The one place the two disagreed (the Hausman test) has a clear, technical explanation rooted in how each language's statistics library handles a known small-sample edge case, not a methodological error.

## Project Structure

```
├── 01_fetch_data.py                  # Python
├── 02_generate_results_document.py
├── 03_generate_figures.py
├── data/global_banking_panel.csv
├── outputs/
│   ├── Global_Banking_Stability_Results.docx
│   └── figures/
├── README.md
└── r/                                 # R implementation
    ├── 01_fetch_data.R
    ├── 02_generate_results_document.R
    ├── 03_generate_figures.R
    ├── data/global_banking_panel.csv
    └── outputs/
        ├── Global_Banking_Stability_Results.docx
        └── figures/
```

## How to Run

**Python (run from repo root):**
```bash
pip install wbgapi pandas numpy statsmodels linearmodels python-docx scipy matplotlib
python 01_fetch_data.py
python 02_generate_results_document.py
python 03_generate_figures.py
```

**R (run from inside the `r/` folder):**
```r
setwd("r")
install.packages(c("wbstats", "dplyr", "tidyr", "plm", "lmtest",
                    "sandwich", "officer", "flextable", "ggplot2", "patchwork"))
source("01_fetch_data.R")
source("02_generate_results_document.R")
source("03_generate_figures.R")
```

