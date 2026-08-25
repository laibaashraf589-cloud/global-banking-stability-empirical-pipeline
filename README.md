# Global Banking Sector Stability Around Systemic Crises (2000–2023)

A cross-country empirical econometrics pipeline investigating whether financial development level buffered banks against two systemic shocks — the 2008 Global Financial Crisis and the 2020 COVID-19 shock — using real World Bank panel data.

---

## Research Question

**Did high-income economies' banking sectors remain more stable than emerging market economies' banking sectors after the 2008 and 2020 systemic shocks?**

This is tested using **Bank Z-score** the standard academic measure of banking sector stability. It combines a banking system's capital buffer and profitability with the volatility of its returns into a single "distance to insolvency" score. A higher Z-score means a lower probability of the banking system defaulting; a falling Z-score signals rising fragility.

---

## Data Source

* **World Bank Global Financial Development Database (GFDD):** Bank-level stability, capital, liquidity, and profitability indicators
* **World Bank World Development Indicators (WDI):** Macroeconomic controls (GDP growth, inflation)
* **Coverage:** ~150 countries, 2000–2023
* **Access:** Free, public World Bank API (`wbgapi`) — no API key required

---

## Methodology

| Step | Method | What it tests |
| :--- | :--- | :--- |
| **1** | **Descriptive statistics by income group** | What does the raw data look like before any modeling? |
| **2** | **Structural break test (Chow Test)** | Did the global Z-score trend actually shift at 2008 and 2020, or could the apparent change be random noise? |
| **3** | **Panel Fixed Effects vs Random Effects + Hausman test** | Which panel model specification is econometrically correct for this data? |
| **4** | **Difference-in-Differences (two-way fixed effects)** | Did emerging markets' stability fall more than high-income countries' did, specifically because of each crisis? |
| **5** | **Event study (relative-year comparison)** | What does the year-by-year pattern around each crisis actually look like, not just the before/after average? |
| **6** | **Robustness checks** | Does the main result survive stricter tests, or could it be a statistical artifact? |

---

## Key Figures

### Figure 1 — Global Average Bank Z-score, 2000–2023
<img width="2658" height="1461" alt="fig1_global_zscore_trend" src="https://github.com/user-attachments/assets/9b0343a3-da40-4dd4-9a49-8c6d854d48dc" />
* **What it shows:** The average Bank Z-score across all ~150 countries, plotted year by year, with the 2008 and 2020 crisis years marked by dashed vertical lines.
* **What it answers:** The first, most basic question — did global banking stability actually change around these two events at all? This is the visual companion to the Chow structural break test (Table 2 in the results document): if the line visibly bends at 2008 and 2020, that's the pattern the formal statistical test is checking for significance.

---

### Figure 2 — Event Study: Bank Z-score Around the 2008 GFC
<img width="2358" height="1461" alt="fig2_event_study_gfc" src="https://github.com/user-attachments/assets/fe3f6933-8d39-41ca-b8f9-0a9f0d10f888" />
* **What it shows:** Two separate lines — High income and Emerging market — tracing the average Z-score from 3 years before to 3 years after 2008.
* **What it answers:** This is the core visual evidence for the research question. If the two lines run roughly parallel before the crisis (supporting the DiD design's key assumption) and then visibly diverge after 2008 — with emerging markets falling further — that is a direct, year-by-year picture of financial development acting as a buffer.

---

### Figure 3 — Event Study: Bank Z-score Around 2020 COVID-19
<img width="2357" height="1461" alt="fig3_event_study_covid" src="https://github.com/user-attachments/assets/ed102851-5cde-4975-9727-f9ec3f58bb98" />
* **What it shows:** The same relative-year comparison, applied to the 2020 shock instead.
* **What it answers:** Lets you compare whether the same buffering pattern shows up in a second, very different type of crisis (a health/liquidity shock rather than a financial-system-originated one) — strengthening or weakening confidence that the 2008 result reflects a general relationship, not a one-off coincidence.

---

### Figure 4 — Difference-in-Differences: Pre- vs Post-Crisis Bank Z-score
<img width="3259" height="1693" alt="fig4_did_bar_comparison" src="https://github.com/user-attachments/assets/d06462f1-6046-450f-89bb-6667450cd982" />
* **What it shows:** Bar chart comparing each group's average Z-score before vs after each crisis, side by side for 2008 and 2020.
* **What it answers:** This is the plain-language version of the DiD regression coefficient in Tables 4-5. The DiD estimate is essentially: *(how much the emerging-market bars drop) minus (how much the high-income bars drop)*. If the emerging-market post-crisis bar falls noticeably more than the high-income one, that visually is the causal effect the regression is quantifying.

---

### Figure 5 — Distribution of Bank Z-score by Income Group
<img width="2059" height="1611" alt="fig5_zscore_distribution" src="https://github.com/user-attachments/assets/672d6d63-befe-471d-8c5a-3b9b5b0443b4" />
* **What it shows:** A box plot of every country-year Z-score observation, split by income group, with individual outlier countries shown as scattered points.
* **What it answers:** The DiD and event study results are about averages — this figure checks whether those averages are representative or hide huge variation. It answers: is the emerging-market group uniformly less stable, or are a few very fragile countries dragging the average down? This matters for how confidently the main result can be generalized.

---

## How the Results Document Answers the Research Question
`outputs/Global_Banking_Stability_Results.docx`

| Table | What it contains | What it establishes |
| :--- | :--- | :--- |
| **1. Descriptive Statistics** | Mean/std/min/max of every variable, by income group | Confirms high-income countries do start with structurally different banking fundamentals (higher capital ratios, lower NPLs) — the baseline the rest of the analysis controls for |
| **2. Structural Break Test** | Chow test F-statistics and p-values for 2008 and 2020 | Formally confirms (or rejects) that the global trend actually broke at each crisis date, rather than just looking that way in Figure 1 |
| **3. Panel FE vs RE + Hausman** | Regression of Z-score on bank fundamentals and macro controls, both ways, plus the model-choice test | Establishes which controls matter for banking stability generally, and justifies using Fixed Effects (or Random Effects) for the causal analysis |
| **4. Difference-in-Differences** | The treat × post interaction coefficient — the core causal estimate — for each crisis | Directly answers the research question with a number: how many Z-score points more did emerging markets lose, specifically attributable to each crisis |
| **5. Event Study Table** | Year-by-year average Z-score per group, ±3 years around each crisis | The numeric backing for Figures 2 and 3 — lets you check the exact pre-trend and post-crisis values, not just read them off a chart |
| **6. Robustness Checks** | Clustered SEs, placebo test (fake crisis year), winsorized re-estimate | Stress-tests the DiD result: the placebo test should find no effect at a year with no real shock, and the winsorized version should give a similar coefficient — both support that the main result is real rather than driven by outliers or by a spurious trend |

---

## Project Structure

```text
├── 01_fetch_data.py                  # Pulls real panel data from the World Bank API
├── 02_generate_results_document.py   # Runs the full econometric pipeline, outputs tables to Word
├── 03_generate_figures.py            # Generates publication-quality figures from the same panel
├── data/
│   └── global_banking_panel.csv      # Clean country-year panel dataset
├── outputs/
│   ├── Global_Banking_Stability_Results.docx   # All regression/test tables
│   └── figures/                                # 300 DPI PNG figures
└── README.md
