"""
03_generate_figures.py
=======================
PROJECT: Global Banking Sector Stability Around Systemic Crises (2000-2023)

PURPOSE OF THIS SCRIPT:
Takes the same clean panel used in 02_generate_results_document.py and turns
the key results into publication-quality figures (300 DPI PNGs). This is
kept as a separate script on purpose - the results document (tables) is the
"raw evidence," and these figures are the polished visual layer built on
top of it, exactly like a real paper separates its Results and Figures.

FIGURES PRODUCED:

  FIG 1 - Global average Bank Z-score, 2000-2023, with both crisis years
          marked. This is the visual companion to the Chow structural
          break test in Table 2 of the results document.

  FIG 2 - Event study line chart (2008 GFC): average Z-score for
          High income vs Emerging market countries, years -3 to +3
          relative to 2008. Lets a reader see the divergence pattern
          directly, not just the DiD coefficient.

  FIG 3 - Event study line chart (2020 COVID): same idea, for the 2020
          shock.

  FIG 4 - Difference-in-Differences bar chart: pre- vs post-crisis
          average Z-score for each group, for both crises side by side.
          This is the classic "DiD in a bar chart" visual.

  FIG 5 - Distribution comparison (box plot): spread of Bank Z-score by
          income group, so a reader can see the full distribution, not
          just the group means.

HOW TO RUN:
    pip install pandas matplotlib seaborn
    python 03_generate_figures.py

INPUT:
    data/global_banking_panel.csv   (produced by 01_fetch_data.py)

OUTPUT (all 300 DPI PNGs):
    outputs/figures/fig1_global_zscore_trend.png
    outputs/figures/fig2_event_study_gfc.png
    outputs/figures/fig3_event_study_covid.png
    outputs/figures/fig4_did_bar_comparison.png
    outputs/figures/fig5_zscore_distribution.png
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

INPUT_FILE = "data/global_banking_panel.csv"
FIG_DIR = "outputs/figures"

NAVY = "#1F3864"
GOLD = "#C9A24B"
GREY = "#8C8C8C"
LIGHT_GREY = "#D9D9D9"

CRISIS_YEARS = {"GFC (2008)": 2008, "COVID (2020)": 2020}

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.edgecolor": "#444444",
    "axes.labelcolor": "#222222",
    "text.color": "#222222",
    "xtick.color": "#444444",
    "ytick.color": "#444444",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 100,
})


def load_panel():
    df = pd.read_csv(INPUT_FILE)
    df["treatment_group"] = np.where(
        df["income_group"] == "High income", "High income", "Emerging market"
    )
    return df


# ---------------------------------------------------------------------------
# FIG 1 - Global average Z-score trend with crisis markers
# ---------------------------------------------------------------------------

def fig1_global_trend(df):
    world_avg = df.groupby("year")["bank_zscore"].mean()

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(world_avg.index, world_avg.values, color=NAVY, linewidth=2.2, marker="o", markersize=4)

    for label, yr in CRISIS_YEARS.items():
        if yr in world_avg.index:
            ax.axvline(yr, color=GOLD, linestyle="--", linewidth=1.4, alpha=0.9)
            ax.text(yr, ax.get_ylim()[1], label, color=GOLD, fontsize=9,
                    ha="center", va="bottom", fontweight="bold")

    ax.set_title("Global Average Bank Z-score, 2000-2023", fontsize=14, fontweight="bold", color=NAVY, pad=28)
    ax.set_xlabel("Year")
    ax.set_ylabel("Bank Z-score (higher = more stable)")
    ax.xaxis.set_major_locator(mticker.MultipleLocator(4))
    ax.grid(axis="y", color=LIGHT_GREY, linewidth=0.7)

    fig.tight_layout()
    path = os.path.join(FIG_DIR, "fig1_global_zscore_trend.png")
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {path}")


# ---------------------------------------------------------------------------
# FIG 2 / FIG 3 - Event study line charts
# ---------------------------------------------------------------------------

def event_study_series(df, crisis_year, window=3):
    d = df.copy()
    d["rel_year"] = d["year"] - crisis_year
    d = d[(d["rel_year"] >= -window) & (d["rel_year"] <= window)]
    pivot = d.groupby(["rel_year", "treatment_group"])["bank_zscore"].mean().unstack("treatment_group")
    return pivot


def fig_event_study(df, crisis_year, label, filename):
    pivot = event_study_series(df, crisis_year)

    fig, ax = plt.subplots(figsize=(8, 5))
    if "High income" in pivot.columns:
        ax.plot(pivot.index, pivot["High income"], color=NAVY, marker="o",
                linewidth=2.2, label="High income")
    if "Emerging market" in pivot.columns:
        ax.plot(pivot.index, pivot["Emerging market"], color=GOLD, marker="o",
                linewidth=2.2, label="Emerging market")

    ax.axvline(0, color=GREY, linestyle=":", linewidth=1.4)
    ax.text(0, ax.get_ylim()[1], "Crisis year", color=GREY, fontsize=9,
            ha="center", va="bottom", style="italic")

    ax.set_title(f"Event Study: Bank Z-score Around {label}", fontsize=14,
                 fontweight="bold", color=NAVY, pad=28)
    ax.set_xlabel("Years relative to crisis")
    ax.set_ylabel("Average Bank Z-score")
    ax.legend(frameon=False, loc="lower left")
    ax.grid(axis="y", color=LIGHT_GREY, linewidth=0.7)

    fig.tight_layout()
    path = os.path.join(FIG_DIR, filename)
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {path}")


# ---------------------------------------------------------------------------
# FIG 4 - DiD bar chart (pre vs post, both crises)
# ---------------------------------------------------------------------------

def did_pre_post_means(df, crisis_year):
    d = df.copy()
    d["period"] = np.where(d["year"] < crisis_year, "Pre-crisis", "Post-crisis")
    return d.groupby(["treatment_group", "period"])["bank_zscore"].mean()


def fig4_did_bars(df):
    fig, axes = plt.subplots(1, 2, figsize=(11, 5.5), sharey=True)

    bar_handles = None
    for ax, (label, yr) in zip(axes, CRISIS_YEARS.items()):
        means = did_pre_post_means(df, yr)
        groups = ["High income", "Emerging market"]
        x = np.arange(len(groups))
        width = 0.35

        pre_vals = [means.get((g, "Pre-crisis"), np.nan) for g in groups]
        post_vals = [means.get((g, "Post-crisis"), np.nan) for g in groups]

        b1 = ax.bar(x - width / 2, pre_vals, width, label="Pre-crisis", color=LIGHT_GREY, edgecolor="#444444")
        b2 = ax.bar(x + width / 2, post_vals, width, label="Post-crisis", color=NAVY)
        bar_handles = [b1, b2]

        ax.set_xticks(x)
        ax.set_xticklabels(groups)
        ax.set_title(label, fontsize=12, fontweight="bold", color=NAVY)
        ax.grid(axis="y", color=LIGHT_GREY, linewidth=0.7)
        # headroom so bars never collide with the legend/title above
        ax.set_ylim(0, ax.get_ylim()[1] * 1.15)

    axes[0].set_ylabel("Average Bank Z-score")
    fig.suptitle("Difference-in-Differences: Pre- vs Post-Crisis Bank Z-score",
                 fontsize=14, fontweight="bold", color=NAVY, y=1.02)
    # Legend placed outside the plotting area entirely (above both panels)
    # so it can never overlap a bar, regardless of the data's scale.
    fig.legend(bar_handles, ["Pre-crisis", "Post-crisis"], loc="upper center",
               bbox_to_anchor=(0.5, 0.96), ncol=2, frameon=False, fontsize=10)
    fig.tight_layout(rect=[0, 0, 1, 0.90])

    path = os.path.join(FIG_DIR, "fig4_did_bar_comparison.png")
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {path}")


# ---------------------------------------------------------------------------
# FIG 5 - Distribution box plot
# ---------------------------------------------------------------------------

def fig5_distribution(df):
    fig, ax = plt.subplots(figsize=(7, 5.5))
    groups = ["High income", "Emerging market"]
    data = [df.loc[df["treatment_group"] == g, "bank_zscore"].dropna().values for g in groups]

    # Real-world Z-score data has many outlier countries; drawing them as
    # solid default "fliers" makes them pile up into a single black blob.
    # Instead: hide the built-in fliers and redraw outliers ourselves as
    # small, semi-transparent, horizontally-jittered points so individual
    # countries stay visible instead of merging together.
    bp = ax.boxplot(data, tick_labels=groups, patch_artist=True, widths=0.5,
                     showfliers=False,
                     medianprops={"color": "#222222", "linewidth": 1.6})
    colors = [NAVY, GOLD]
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.75)

    rng = np.random.default_rng(42)
    for i, values in enumerate(data, start=1):
        q1, q3 = np.percentile(values, [25, 75])
        iqr = q3 - q1
        lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        outliers = values[(values < lo) | (values > hi)]
        if len(outliers) == 0:
            continue
        jitter = rng.uniform(-0.10, 0.10, size=len(outliers))
        ax.scatter(np.full(len(outliers), i) + jitter, outliers,
                    s=14, color=GREY, alpha=0.45, edgecolors="none", zorder=3)

    ax.set_title("Distribution of Bank Z-score by Income Group", fontsize=14,
                 fontweight="bold", color=NAVY, pad=16)
    ax.set_ylabel("Bank Z-score")
    ax.grid(axis="y", color=LIGHT_GREY, linewidth=0.7)

    fig.tight_layout()
    path = os.path.join(FIG_DIR, "fig5_zscore_distribution.png")
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {path}")


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    os.makedirs(FIG_DIR, exist_ok=True)
    df = load_panel()

    fig1_global_trend(df)
    fig_event_study(df, CRISIS_YEARS["GFC (2008)"], "2008 GFC", "fig2_event_study_gfc.png")
    fig_event_study(df, CRISIS_YEARS["COVID (2020)"], "2020 COVID", "fig3_event_study_covid.png")
    fig4_did_bars(df)
    fig5_distribution(df)

    print("\nAll figures saved to:", FIG_DIR)


if __name__ == "__main__":
    main()