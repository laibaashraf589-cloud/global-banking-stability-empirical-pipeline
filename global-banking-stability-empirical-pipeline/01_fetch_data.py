"""
01_fetch_data.py
=================
PROJECT: Global Banking Sector Stability Around Systemic Crises (2000-2023)

PURPOSE OF THIS SCRIPT:
This script pulls a real, large-scale cross-country panel dataset directly
from the World Bank API (free, no API key required) and prepares it for
econometric analysis. Nothing here is synthetic or simulated - every value
comes from the World Bank's live database.

WHAT IT DOES, STEP BY STEP:
1. Connects to the World Bank API using the 'wbgapi' package.
2. Downloads six indicators for every country the World Bank tracks,
   for the years 2000-2023:
      - Bank Z-score                              (GFDD.SI.01)  -> our DEPENDENT variable
      - Bank capital to assets ratio (%)           (GFDD.SI.02)
      - Bank nonperforming loans to gross loans (%)(GFDD.SI.04)
      - Bank return on assets (%, after tax)       (GFDD.EI.09)
      - Liquid assets to deposits & short-term
        funding (%)                                (GFDD.OI.02)
      - GDP growth (annual %)                      (NY.GDP.MKTP.KD.ZG)
      - Inflation, consumer prices (annual %)      (FP.CPI.TOTL.ZG)
3. Pulls each country's official World Bank income-group classification
   (High income / Upper-middle / Lower-middle / Low income) - this becomes
   our TREATMENT/CONTROL split for the DiD design later.
4. Drops aggregate/regional codes (e.g. "World", "Euro area") so only
   actual countries remain.
5. Reshapes everything into "long panel" format: one row per
   country-year, one column per variable - this is the standard shape
   required for panel econometrics (linearmodels, PanelOLS, etc.)
6. Drops country-years with too much missing data (keeps the panel usable
   without introducing fake numbers).
7. Saves the final clean panel to data/global_banking_panel.csv

WHY THIS MATTERS FOR THE PROJECT:
Bank Z-score is a widely used academic measure of bank stability -
it combines a bank's capital buffer and return volatility into a single
"distance to insolvency" score. Higher Z-score = more stable. Using it
across ~150 countries and 24 years lets us formally test whether
financial development level cushioned countries against the 2008 and
2020 shocks - a genuinely cross-country empirical question.

HOW TO RUN:
    pip install wbgapi pandas
    python 01_fetch_data.py

OUTPUT:
    data/global_banking_panel.csv
"""

import os
import pandas as pd
import wbgapi as wb

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

START_YEAR = 2000
END_YEAR = 2023
# Note: the GFDD indicators are only updated through 2021 as of the World
# Bank's last GFDD release (WDI indicators like GDP growth/inflation go
# further). Requesting through 2023 is fine - the extra years just come
# back empty for GFDD variables and skipBlanks=True drops them cleanly.

INDICATORS = {
    # code: (clean_name, database_id)
    # GFDD indicators live in the Global Financial Development Database (db=32)
    # WDI indicators live in the World Development Indicators database (db=2, wbgapi's default)
    "GFDD.SI.01": ("bank_zscore", 32),          # Bank Z-score (stability measure)
    "GFDD.SI.02": ("capital_to_assets", 32),    # Bank capital to assets ratio (%)
    "GFDD.SI.04": ("npl_ratio", 32),            # Nonperforming loans to gross loans (%)
    "GFDD.EI.09": ("roa", 32),                  # Return on assets (%, after tax)
    "GFDD.OI.02": ("liquid_to_deposits", 32),   # Liquid assets to deposits & short-term funding (%)
    "NY.GDP.MKTP.KD.ZG": ("gdp_growth", 2),     # GDP growth (annual %)
    "FP.CPI.TOTL.ZG": ("inflation", 2),         # Inflation, consumer prices (annual %)
}

OUTPUT_DIR = "data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "global_banking_panel.csv")

# Minimum share of core variables that must be non-missing for a
# country-year row to be kept (avoids a panel full of holes)
MIN_NON_MISSING_SHARE = 0.5


def fetch_indicator_panel() -> pd.DataFrame:
    """
    Downloads all indicators from the World Bank API and returns a
    long-format panel: one row per (country, year), one column per
    indicator.
    """
    print(f"Fetching {len(INDICATORS)} indicators for {START_YEAR}-{END_YEAR} "
          f"from the World Bank API...")

    frames = []
    for code, (clean_name, db) in INDICATORS.items():
        print(f"  -> downloading {code} ({clean_name}) from database {db}")
        # wb.data.DataFrame returns countries as rows, years as columns
        raw = wb.data.DataFrame(
            code,
            db=db,
            time=range(START_YEAR, END_YEAR + 1),
            labels=False,
            skipBlanks=True,
        )
        # Reshape wide (years as columns) -> long (one row per country-year)
        raw = raw.reset_index().rename(columns={"economy": "country_code"})
        long = raw.melt(
            id_vars="country_code", var_name="year", value_name=clean_name
        )
        # wbgapi returns year columns labelled like "YR2008" -> convert to int
        long["year"] = long["year"].str.replace("YR", "", regex=False).astype(int)
        frames.append(long.set_index(["country_code", "year"]))

    panel = pd.concat(frames, axis=1).reset_index()
    return panel


def fetch_country_metadata() -> pd.DataFrame:
    """
    Downloads country name + income-group classification for every
    economy code. This is what lets us split the sample into
    High income vs Emerging market (the DiD treatment/control groups).
    """
    print("Fetching country metadata (name, region, income group)...")
    # labels=True -> region/incomeLevel come back as readable text
    # skipAggs=True -> cleanly drops aggregate/regional codes (e.g. "World",
    # "Euro area") so only actual countries remain - no manual filtering needed
    meta = wb.economy.DataFrame(labels=True, skipAggs=True)

    # wbgapi names the DataFrame's index "id" (the 3-letter economy code),
    # not "economy" - that mismatch was the bug.
    meta = meta.reset_index().rename(columns={"id": "country_code"})
    meta = meta[["country_code", "name", "region", "incomeLevel"]]
    meta.columns = ["country_code", "country_name", "region", "income_group"]
    return meta


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    panel = fetch_indicator_panel()
    meta = fetch_country_metadata()

    # Keep only actual countries (inner join drops aggregate/regional codes)
    df = panel.merge(meta, on="country_code", how="inner")

    # Reorder columns for readability
    id_cols = ["country_code", "country_name", "region", "income_group", "year"]
    value_cols = [name for name, db in INDICATORS.values()]
    df = df[id_cols + value_cols]

    # Drop rows that are almost entirely missing on the core indicators
    non_missing_share = df[value_cols].notna().mean(axis=1)
    before = len(df)
    df = df[non_missing_share >= MIN_NON_MISSING_SHARE].reset_index(drop=True)
    after = len(df)
    print(f"Dropped {before - after} country-year rows with too much missing data "
          f"(kept {after} rows).")

    df = df.sort_values(["country_name", "year"]).reset_index(drop=True)

    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nSaved clean panel to: {OUTPUT_FILE}")
    print(f"Countries: {df['country_name'].nunique()}  |  "
          f"Years: {df['year'].min()}-{df['year'].max()}  |  "
          f"Rows: {len(df)}")
    print("\nIncome group breakdown (unique countries):")
    print(df.drop_duplicates("country_name")["income_group"].value_counts())


if __name__ == "__main__":
    main()
