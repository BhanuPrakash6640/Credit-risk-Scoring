"""
Generate Presentation Visual Artifacts for the Credit Risk Scoring Pipeline.

Outputs high-definition presentation figures to presentation_artifacts/.
Safely loads the trained champion model without overwriting production artifacts.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    auc,
    confusion_matrix,
    precision_recall_curve,
    roc_curve,
)

# Project paths
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import config
from src import cleaning, data_loader, features, models, quality, risk

# Professional presentation styling tokens
PRIMARY = "#1E3A8A"        # Deep Navy
CHAMPION = "#0D9488"       # Teal
SECONDARY = "#3B82F6"      # Royal Blue
ACCENT = "#F59E0B"         # Amber
DANGER = "#EF4444"         # Coral Red
SUCCESS = "#10B981"        # Emerald
NEUTRAL_DARK = "#1F2937"   # Charcoal
BORDER_COLOR = "#E5E7EB"   # Slate border

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.edgecolor": "#9CA3AF",
    "axes.linewidth": 1.2,
    "axes.labelcolor": NEUTRAL_DARK,
    "text.color": NEUTRAL_DARK,
    "xtick.color": "#4B5563",
    "ytick.color": "#4B5563",
    "figure.facecolor": "white",
    "axes.facecolor": "#FCFCFD",
    "axes.grid": True,
    "grid.color": "#E5E7EB",
    "grid.linestyle": "--",
    "grid.alpha": 0.7,
    "figure.dpi": 200,
    "savefig.dpi": 200,
})


def save_fig(fig, filename: str, out_dir: Path):
    path = out_dir / filename
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight", dpi=200)
    plt.close(fig)
    print(f"  [Saved] {path.name}")


def main():
    out_dir = ROOT / "presentation_artifacts"
    out_dir.mkdir(parents=True, exist_ok=True)
    print("=" * 70)
    print(f"GENERATING PRESENTATION ASSETS -> {out_dir}")
    print("=" * 70)

    # 1. Load Data
    print("\n[1/6] Loading data...")
    raw_df = data_loader.load_raw()
    print(f"Loaded {len(raw_df):,} rows x {raw_df.shape[1]} columns")

    # 2. Quality Assessment Before & After
    print("\n[2/6] Auditing data quality...")
    q_before = quality.assess(raw_df)
    clean_df, cleaning_log = cleaning.clean(raw_df, verbose=False)
    q_after = quality.assess(clean_df)

    # Chart 1: Quality Dimensions
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    dims = ["completeness", "validity", "consistency", "uniqueness", "overall_score"]
    dim_labels = ["Completeness", "Validity", "Consistency", "Uniqueness", "OVERALL SCORE"]
    before_vals = [q_before[d] for d in dims]
    after_vals = [q_after[d] for d in dims]

    x = np.arange(len(dims))
    width = 0.35
    ax.bar(x - width / 2, before_vals, width, label="Before Cleaning (Raw)", color="#94A3B8")
    ax.bar(x + width / 2, after_vals, width, label="After Cleaning (Repaired)", color=PRIMARY)
    ax.set_ylabel("Quality Score (0 - 100)")
    ax.set_title("Step 1: End-to-End Data Quality Audit & Sanitization", fontsize=13, fontweight="bold", pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(dim_labels, fontweight="semibold")
    ax.set_ylim(0, 115)
    ax.legend(frameon=True, facecolor="white", edgecolor=BORDER_COLOR)
    save_fig(fig, "step1_data_quality_assessment.png", out_dir)

    # Chart 2: Missingness & Cleaning Impact
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    missing_before = (raw_df.isna().mean() * 100).sort_values(ascending=False).head(10)
    ax1.barh(missing_before.index[::-1], missing_before.values[::-1], color="#E11D48", alpha=0.85)
    ax1.set_xlabel("% Missing in Raw File")
    ax1.set_title("Top 10 Incomplete Columns (Raw)", fontweight="bold")

    steps = [a["step"] for a in cleaning_log if "step" in a]
    step_counts = pd.Series(steps).value_counts()
    ax2.bar(step_counts.index, step_counts.values, color=SECONDARY)
    ax2.set_ylabel("Number of Actions")
    ax2.set_title("Data Cleaning Interventions Executed", fontweight="bold")
    ax2.tick_params(axis="x", rotation=30)
    fig.suptitle("Step 2: Missingness Resolution & Sanitization", fontsize=13, fontweight="bold")
    save_fig(fig, "step2_missingness_and_cleaning.png", out_dir)

    # 3. Feature Engineering & Risk Drivers
    print("\n[3/6] Engineering financial features...")
    feat_df = features.build_features(clean_df, verbose=False)

    # Chart 3: Correlation with Default
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    num_cols = [c for c in config.NUMERIC_FEATURES if c in feat_df.columns]
    corrs = feat_df[num_cols + [config.TARGET]].corr()[config.TARGET].drop(config.TARGET).sort_values()
    top_corrs = pd.concat([corrs.head(7), corrs.tail(7)])
    colors = [DANGER if v > 0 else SUCCESS for v in top_corrs.values]
    ax.barh(top_corrs.index, top_corrs.values, color=colors)
    ax.axvline(0, color=NEUTRAL_DARK, linestyle="-", linewidth=0.8)
    ax.set_xlabel("Pearson Correlation with Loan Default (1 = Default)")
    ax.set_title("Step 3: Key Financial Risk Drivers & Interaction Signals", fontsize=13, fontweight="bold")
    save_fig(fig, "step3_feature_correlations.png", out_dir)

    # Chart 4: Portfolio Structure & Vintages
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.8))
    target_counts = feat_df[config.TARGET].value_counts().sort_index()
    labels = ["Fully Paid (0)", "Default / Charged Off (1)"]
    ax1.pie(target_counts, labels=labels, autopct="%1.1f%%", colors=[SUCCESS, DANGER],
            startangle=140, explode=(0, 0.08), wedgeprops=dict(width=0.6, edgecolor="w"))
    ax1.set_title(f"Target Distribution\n(Default Rate: {feat_df[config.TARGET].mean():.1%})", fontweight="bold")

    if "issue_year" in feat_df.columns:
        vintages = feat_df.groupby("issue_year")[config.TARGET].agg(["count", "mean"])
        ax2.bar(vintages.index, vintages["count"], color=PRIMARY, alpha=0.85, label="Loan Volume")
        ax2_twin = ax2.twinx()
        ax2_twin.plot(vintages.index, vintages["mean"] * 100, color=DANGER, marker="o", linewidth=2.2)
        ax2.set_xlabel("Issue Vintage Year")
        ax2.set_ylabel("Loan Count")
        ax2_twin.set_ylabel("Default Rate (%)", color=DANGER)
        ax2_twin.grid(False)
        ax2.set_title("Loan Volume & Default Rate by Vintage", fontweight="bold")
    fig.suptitle("Step 4: Chronological Portfolio Structure & Class Balance", fontsize=13, fontweight="bold")
    save_fig(fig, "step4_class_distribution_and_vintages.png", out_dir)

    # 4. Model Inference & Evaluation
    print("\n[4/6] Evaluating champion model on test set...")
    import joblib
    model_dict = joblib.load(config.MODEL_PATH)
    pipeline = model_dict["pipeline"]
    model_name = model_dict.get("model_name", "XGBoost (Champion)")
    model_features = model_dict["numeric_features"] + model_dict["categorical_features"]

    # Test split
    _, _, test_df = features.time_split(feat_df, return_cal=True)
    X_test = test_df[model_features]
    y_test = test_df[config.TARGET].values

    probs = pipeline.predict_proba(X_test)[:, 1]

    # Chart 6: Champion ROC Curve
    fig, ax = plt.subplots(figsize=(8.5, 6))
    fpr, tpr, _ = roc_curve(y_test, probs)
    roc_val = auc(fpr, tpr)
    ax.plot(fpr, tpr, label=f"{model_name} (AUC = {roc_val:.4f})", linewidth=2.8, color=CHAMPION)
    ax.plot([0, 1], [0, 1], "k:", alpha=0.6, label="Random Guess (AUC = 0.50)")
    ax.set_xlabel("False Positive Rate (1 - Specificity)")
    ax.set_ylabel("True Positive Rate (Sensitivity / Recall)")
    ax.set_title(f"Receiver Operating Characteristic (ROC) — {model_name}", fontsize=13, fontweight="bold")
    ax.legend(loc="lower right", frameon=True, facecolor="white", edgecolor=BORDER_COLOR)
    save_fig(fig, "step6_roc_curves_all_models.png", out_dir)

    # Chart 7: Precision-Recall Curve
    fig, ax = plt.subplots(figsize=(8.5, 6))
    p, r, _ = precision_recall_curve(y_test, probs)
    pr_val = auc(r, p)
    baseline_rate = y_test.mean()
    ax.plot(r, p, label=f"{model_name} (PR-AUC = {pr_val:.4f})", linewidth=2.8, color=CHAMPION)
    ax.axhline(baseline_rate, color="k", linestyle=":", label=f"Baseline Prior ({baseline_rate:.1%})")
    ax.set_xlabel("Recall (Borrowers Correctly Flagged as Default)")
    ax.set_ylabel("Precision (Identified Defaults Truly Bad)")
    ax.set_title("Precision-Recall Trade-offs on Default Minority Class", fontsize=13, fontweight="bold")
    ax.legend(loc="upper right", frameon=True, facecolor="white", edgecolor=BORDER_COLOR)
    save_fig(fig, "step7_precision_recall_curves.png", out_dir)

    # Chart 8: Confusion Matrix
    tuned_thr = 0.17
    y_pred = (probs >= tuned_thr).astype(int)
    cm = confusion_matrix(y_test, y_pred)
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(cm, cmap="YlGnBu", interpolation="nearest")
    for i in range(2):
        for j in range(2):
            ax.text(j, i, f"{cm[i, j]:,}", ha="center", va="center",
                    color="white" if cm[i, j] > cm.max() / 2 else "black", fontweight="bold")
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(["Repaid", "Default"])
    ax.set_yticklabels(["Repaid", "Default"])
    ax.set_xlabel("Predicted Label")
    ax.set_ylabel("Actual Label")
    ax.set_title(f"Confusion Matrix ({model_name}, Threshold = {tuned_thr:.2f})", fontweight="bold")
    save_fig(fig, "step8_confusion_matrix_comparison.png", out_dir)

    # 5. Risk Segmentation & Scorecard
    print("\n[5/6] Risk segmentation & scorecard distribution...")
    scored_test = risk.score_dataframe(test_df, pipeline)

    # Chart 11: Risk Bands & Score Distribution
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    band_counts = scored_test["risk_band"].value_counts().reindex(config.RISK_LABELS, fill_value=0)
    band_colors = [SUCCESS, ACCENT, DANGER]
    ax1.bar(band_counts.index, band_counts.values, color=band_colors)
    for i, v in enumerate(band_counts.values):
        ax1.text(i, v + len(scored_test) * 0.01, f"{v:,}\n({v / len(scored_test):.1%})",
                 ha="center", fontweight="semibold")
    ax1.set_ylabel("Borrowers")
    ax1.set_title("Portfolio Risk Segmentation", fontweight="bold")

    ax2.hist(scored_test["credit_score"], bins=35, color=PRIMARY, alpha=0.85, edgecolor="white")
    ax2.axvline(660, color=ACCENT, linestyle="--", linewidth=2, label="Anchor Score 660 (Book Avg 20% PD)")
    ax2.set_xlabel("FICO-Scale Scorecard Rating (300 - 850)")
    ax2.set_ylabel("Frequency")
    ax2.set_title("Credit Score Distribution", fontweight="bold")
    ax2.legend(frameon=True, facecolor="white", edgecolor=BORDER_COLOR)
    fig.suptitle("Step 11: FICO-Scale Credit Scorecard & Risk Band Allocation", fontsize=13, fontweight="bold")
    save_fig(fig, "step11_credit_score_distribution.png", out_dir)

    # Chart 12: Decile Lift
    gains = risk.gains_table(scored_test)
    if not gains.empty:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        ax1.plot(range(1, 11), gains["cumulative_defaults_pct"], marker="o", color=PRIMARY, linewidth=2.5, label="Model Gains")
        ax1.plot([1, 10], [10, 100], "k--", label="Baseline (Random)")
        ax1.set_xlabel("Decile (1 = Highest Risk)")
        ax1.set_ylabel("% of All Defaults Captured")
        ax1.set_title("Cumulative Gains Curve", fontweight="bold")
        ax1.legend(frameon=True, facecolor="white", edgecolor=BORDER_COLOR)

        ax2.bar(range(1, 11), gains["lift"], color=CHAMPION)
        ax2.axhline(1.0, color="k", linestyle="--")
        ax2.set_xlabel("Decile (1 = Highest Risk)")
        ax2.set_ylabel("Lift Multiplier vs Book Average")
        ax2.set_title("Decile Lift Multiplier", fontweight="bold")
        fig.suptitle("Step 12: Decile Lift & Cumulative Default Separation", fontsize=13, fontweight="bold")
        save_fig(fig, "step12_decile_lift_gains.png", out_dir)

    print("\n[6/6] Done. Presentation assets refreshed without modifying production artifacts.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
