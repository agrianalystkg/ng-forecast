# -*- coding: utf-8 -*-
"""
plot_model_diagnostics.py
-------------------------
Build the three-panel exhibit for the Brent-anchored model from the shipped
derived diagnostics only:

    data/ffv_brent_model_diagnostics.csv  ->  images/ffv_brent_model.png

Run from the repo root:

    python forecasting/plot_model_diagnostics.py

No raw price data are required. The CSV contains one row per formation month
with a realised outcome, the one-step-ahead forecast, the monthly refit
coefficients and the expanding R².
"""

import os

import matplotlib
matplotlib.use("Agg")
from matplotlib.lines import Line2D
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(_REPO, "data", "ffv_brent_model_diagnostics.csv")
OUT = os.path.join(_REPO, "images", "ffv_brent_model.png")

BLUE = "#1f4e79"
GREEN = "#2e7d32"
ORANGE = "#e67e22"
RED = "#c62828"
GREY = "#666666"

plt.rcParams.update({
    "font.size": 11,
    "axes.titlesize": 12.5,
    "axes.titleweight": "bold",
    "axes.labelsize": 11,
    "xtick.labelsize": 10.5,
    "ytick.labelsize": 10.5,
    "legend.fontsize": 9,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})


def _year_axis(ax):
    ax.xaxis.set_major_locator(mdates.YearLocator(4))
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))


def _shade_2022(ax):
    ax.axvspan(pd.Timestamp("2022-01-01"), pd.Timestamp("2023-01-01"),
               color=GREY, alpha=0.10, linewidth=0)


def panel_storage(ax, df):
    x = df["storage_yoy"]
    y = df["actual_log_yoy"]
    ax.scatter(x, y, s=14, color=BLUE, alpha=0.45, linewidths=0)

    # raw univariate fit, shown only as a reference
    slope, intercept = np.polyfit(x, y, 1)
    xs = np.linspace(x.min(), x.max(), 100)
    ax.plot(xs, slope * xs + intercept, color=GREY, linestyle="--",
            linewidth=1.1, label=f"raw univariate slope {slope:+.2f}")

    # binned median of the raw relationship
    bins = pd.qcut(x, 10, duplicates="drop")
    med = (df.groupby(bins, observed=True)
             .agg(x=("storage_yoy", "median"), y=("actual_log_yoy", "median"),
                  n=("actual_log_yoy", "size")))
    med = med[med["n"] >= 5]
    ax.plot(med["x"], med["y"], color=ORANGE, linewidth=1.8,
            marker="o", markersize=4, label="binned median")

    ax.axhline(0, color="black", linewidth=0.6, alpha=0.5)
    ax.set_xlabel("Storage YoY (log change, 12 months)")
    ax.set_ylabel("Price YoY (log change, 12 months)")
    ax.set_title("Storage relationship", loc="left")
    ax.grid(True, alpha=0.3, linewidth=0.6)

    b = df["beta_storage"]
    note = (f"model $\\beta_{{storage}}$ {b.mean():+.2f} "
            f"(range {b.min():+.2f} to {b.max():+.2f})\n"
            "conditional on Brent and the lagged price")
    ax.text(0.03, 0.04, note, transform=ax.transAxes, va="bottom", ha="left",
            fontsize=8.8, color=GREY,
            bbox=dict(boxstyle="round,pad=0.35", facecolor="white",
                      edgecolor="#dddddd", alpha=0.9))
    ax.legend(loc="upper left", frameon=False)


def panel_stability(ax_coef, ax_r2, df):
    d = df.set_index("date")
    roll = d[["alpha", "beta_storage", "beta_brent", "beta_lag"]].rolling(12).mean()

    ax_coef.plot(roll.index, roll["alpha"], color=BLUE, linewidth=1.4, label="alpha")
    ax_coef.plot(roll.index, roll["beta_brent"], color=ORANGE, linewidth=1.4,
                 label="beta Brent")
    ax_coef.plot(roll.index, roll["beta_lag"], color=RED, linewidth=1.4,
                 label="beta lagged price")
    ax_coef.axhline(0, color="black", linewidth=0.6, alpha=0.5)
    ax_coef.set_ylabel("Coefficient (12m average)")
    ax_coef.set_title("Rolling coefficients and R²", loc="left")
    ax_coef.grid(True, alpha=0.3, linewidth=0.6)
    _shade_2022(ax_coef)

    ax_stor = ax_coef.twinx()
    ax_stor.plot(roll.index, roll["beta_storage"], color=GREEN, linewidth=1.6,
                 label="beta storage (right)")
    ax_stor.set_ylabel("Storage beta", color=GREEN)
    ax_stor.tick_params(axis="y", colors=GREEN)
    ax_stor.spines["right"].set_visible(True)
    ax_stor.spines["right"].set_color(GREEN)

    lines = [
        Line2D([0], [0], color=BLUE, linewidth=1.4, label="alpha"),
        Line2D([0], [0], color=ORANGE, linewidth=1.4, label="beta Brent"),
        Line2D([0], [0], color=RED, linewidth=1.4, label="beta lagged price"),
        Line2D([0], [0], color=GREEN, linewidth=1.6, label="beta storage (right)"),
    ]
    ax_coef.legend(handles=lines, loc="upper left", ncol=2, frameon=False)
    ax_coef.tick_params(labelbottom=False)

    r2 = d["r2_expanding"].dropna()
    ax_r2.plot(r2.index, r2.values, color=BLUE, linewidth=1.2)
    ax_r2.fill_between(r2.index, 0, r2.values, color=BLUE, alpha=0.10)
    ax_r2.axhline(0.5, color=GREY, linestyle=":", linewidth=0.9, alpha=0.7)
    ax_r2.set_ylim(0, 1)
    ax_r2.set_ylabel("Expanding R²")
    ax_r2.set_xlabel("Formation month")
    ax_r2.grid(True, alpha=0.3, linewidth=0.6)
    _shade_2022(ax_r2)
    _year_axis(ax_r2)
    ax_r2.text(0.98, 0.95, f"latest {r2.iloc[-1]:.2f}   range {r2.min():.2f}–{r2.max():.2f}",
               transform=ax_r2.transAxes, va="top", ha="right", fontsize=8.8, color=GREY)


def panel_fit(ax_fit, ax_res, df):
    d = df.set_index("date")
    ax_fit.plot(d.index, d["actual_log_yoy"], color="#333333", linewidth=1.3,
                label="actual")
    ax_fit.plot(d.index, d["fitted_log_yoy"], color=ORANGE, linewidth=1.5,
                label="one-step-ahead forecast")
    ax_fit.axhline(0, color="black", linewidth=0.6, alpha=0.5)
    ax_fit.set_ylabel("Log price YoY")
    ax_fit.set_title("One-step-ahead fit", loc="left")
    ax_fit.grid(True, alpha=0.3, linewidth=0.6)
    _shade_2022(ax_fit)
    ax_fit.legend(loc="lower left", frameon=False, ncol=2)

    a = d["actual_log_yoy"].values
    r = d["residual"].values
    r2 = 1 - np.sum(r ** 2) / np.sum((a - a.mean()) ** 2)
    rmse = np.sqrt(np.mean(r ** 2))
    hit = np.mean(np.sign(a) == np.sign(d["fitted_log_yoy"].values))
    note = f"R² {r2:.3f}   RMSE {rmse:.3f}\ndirectional {hit:.0%}   n {len(d)}"
    ax_fit.text(0.02, 0.96, note, transform=ax_fit.transAxes, va="top",
                ha="left", fontsize=9, color=GREY,
                bbox=dict(boxstyle="round,pad=0.35", facecolor="white",
                          edgecolor="#dddddd", alpha=0.9))

    colours = np.where(r >= 0, GREEN, RED)
    ax_res.bar(d.index, r, width=20, color=colours, alpha=0.65, linewidth=0)
    ax_res.axhline(0, color="black", linewidth=0.6, alpha=0.5)
    ax_res.set_ylabel("Residual")
    ax_res.set_xlabel("Formation month")
    ax_res.grid(True, alpha=0.25, linewidth=0.6, axis="y")
    _shade_2022(ax_res)
    _year_axis(ax_res)
    for ax in (ax_fit,):
        ax.tick_params(labelbottom=False)


def main():
    df = pd.read_csv(DATA, parse_dates=["date"]).sort_values("date")
    if df.empty:
        raise SystemExit("diagnostics CSV is empty")

    fig = plt.figure(figsize=(18, 5))
    outer = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.05, 1.18], wspace=0.42)

    ax1 = fig.add_subplot(outer[0, 0])
    mid = outer[0, 1].subgridspec(2, 1, height_ratios=[1.55, 1.0], hspace=0.12)
    right = outer[0, 2].subgridspec(2, 1, height_ratios=[3.1, 1.0], hspace=0.08)

    panel_storage(ax1, df)
    panel_stability(fig.add_subplot(mid[0, 0]), fig.add_subplot(mid[1, 0]), df)
    panel_fit(fig.add_subplot(right[0, 0]), fig.add_subplot(right[1, 0]), df)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    fig.savefig(OUT, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
