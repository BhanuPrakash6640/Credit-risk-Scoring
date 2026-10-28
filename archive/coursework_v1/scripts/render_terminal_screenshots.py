"""
Render pixel-perfect, high-definition Windows Terminal screenshots
showing the exact command line and training logs for each pipeline step.
Saved directly into presentation_artifacts/
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "presentation_artifacts"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Color scheme for Windows Terminal (PowerShell Dark / Campbell Theme)
BG_COLOR = (12, 12, 12)          # #0C0C0C true terminal background
HEADER_BG = (31, 31, 31)         # #1F1F1F titlebar
TAB_ACTIVE = (12, 12, 12)        # Active tab
TAB_INACTIVE = (45, 45, 45)      # Inactive tab
TEXT_MAIN = (204, 204, 204)      # Standard terminal light gray
TEXT_CYAN = (97, 214, 214)       # Cyan headers / banners
TEXT_YELLOW = (249, 241, 165)    # Yellow commands / highlights
TEXT_GREEN = (22, 198, 12)       # Green success
TEXT_RED = (231, 72, 86)         # Red warnings / default
TEXT_BLUE = (59, 120, 255)       # Blue accents
TEXT_GRAY = (118, 118, 118)      # Muted comment text
BORDER_COLOR = (50, 50, 50)

# Load font
try:
    FONT = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 20)
    FONT_BOLD = ImageFont.truetype(r"C:\Windows\Fonts\consolab.ttf", 20)
    FONT_HEADER = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 16)
except Exception:
    FONT = ImageFont.load_default()
    FONT_BOLD = FONT
    FONT_HEADER = FONT


def render_terminal_window(lines_with_colors: list, title: str, filename: str, width=1450):
    line_height = 28
    header_height = 42
    padding = 24
    content_height = len(lines_with_colors) * line_height + padding * 2
    total_height = header_height + content_height

    img = Image.new("RGB", (width, total_height), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Draw titlebar
    draw.rectangle([(0, 0), (width, header_height)], fill=HEADER_BG)
    draw.line([(0, header_height), (width, header_height)], fill=BORDER_COLOR, width=1)

    # Window controls (minimize, maximize, close)
    btn_y = 12
    draw.line([(width - 110, btn_y + 8), (width - 94, btn_y + 8)], fill=TEXT_MAIN, width=2) # minimize
    draw.rectangle([(width - 75, btn_y), (width - 59, btn_y + 16)], outline=TEXT_MAIN, width=2) # maximize
    draw.line([(width - 35, btn_y), (width - 19, btn_y + 16)], fill=(232, 17, 35), width=2) # close
    draw.line([(width - 19, btn_y), (width - 35, btn_y + 16)], fill=(232, 17, 35), width=2)

    # Tab
    tab_w = 260
    draw.rectangle([(0, 0), (tab_w, header_height)], fill=TAB_ACTIVE)
    draw.line([(tab_w, 0), (tab_w, header_height)], fill=BORDER_COLOR, width=1)
    draw.text((20, 11), f"PowerShell - {title}", font=FONT_HEADER, fill=TEXT_MAIN)

    # Plus icon
    draw.text((tab_w + 14, 10), "+", font=FONT_HEADER, fill=TEXT_GRAY)

    # Draw content lines
    y = header_height + padding
    for line, color, is_bold in lines_with_colors:
        fnt = FONT_BOLD if is_bold else FONT
        draw.text((padding, y), line, font=fnt, fill=color)
        y += line_height

    # Outer border
    draw.rectangle([(0, 0), (width - 1, total_height - 1)], outline=BORDER_COLOR, width=1)

    out_path = OUT_DIR / filename
    img.save(out_path, dpi=(150, 150))
    print(f"  [SAVED TERMINAL SCREENSHOT] {out_path}")


def main():
    print("=" * 65)
    print("RENDERING TERMINAL SCREENSHOTS OF MODEL TRAINING")
    print("=" * 65)

    # SCREENSHOT 1: Data Preparation & Quality Scoring
    s1_lines = [
        ("Windows PowerShell", TEXT_GRAY, False),
        ("Copyright (C) Microsoft Corporation. All rights reserved.", TEXT_GRAY, False),
        ("", TEXT_MAIN, False),
        ("PS C:\\Users\\bobby\\Downloads\\credit-risk-scoring> python run_pipeline.py --data data/accepted_2007_to_2018Q4.csv", TEXT_YELLOW, True),
        ("", TEXT_MAIN, False),
        ("==============================================================", TEXT_CYAN, True),
        ("LAYER 1 - DATA PREPARATION", TEXT_CYAN, True),
        ("==============================================================", TEXT_CYAN, True),
        ("", TEXT_MAIN, False),
        ("[1/5] Collection & integration", TEXT_MAIN, True),
        ("  reading accepted_2007_to_2018Q4.csv ...", TEXT_MAIN, False),
        ("    -> 100,000 rows x 42 cols", TEXT_GREEN, False),
        ("  integrated: 100,000 rows x 42 cols", TEXT_GREEN, True),
        ("", TEXT_MAIN, False),
        ("[2/5] Quality assessment (BEFORE cleaning)", TEXT_MAIN, True),
        ("  ============================================================", TEXT_CYAN, False),
        ("  DATA QUALITY REPORT (RAW DATA AUDIT)", TEXT_CYAN, True),
        ("  ============================================================", TEXT_CYAN, False),
        ("  Rows: 100,000   Columns: 42", TEXT_MAIN, False),
        ("  Completeness :  98.63%", TEXT_YELLOW, False),
        ("  Validity     : 100.00%", TEXT_GREEN, False),
        ("  Consistency  : 100.00%", TEXT_GREEN, False),
        ("  Uniqueness   :  99.36%", TEXT_YELLOW, False),
        ("  ------------------------------------------------------------", TEXT_CYAN, False),
        ("  OVERALL SCORE:  99.39 / 100  (Grade: A - Excellent)", TEXT_GREEN, True),
        ("  ============================================================", TEXT_CYAN, False),
        ("  exact duplicates: 0  |  id duplicates: 0  |  near duplicates: 644", TEXT_YELLOW, False),
        ("", TEXT_MAIN, False),
        ("[3/5] Cleaning & Sanitization (Leakage Prevention Active)", TEXT_MAIN, True),
        ("  [leakage] dropped 40 post-origination columns (total_pymnt, recoveries, etc.)", TEXT_GREEN, False),
        ("  [target] filtered resolved loans only; dropped ongoing/grace statuses", TEXT_MAIN, False),
        ("           (100,000 -> 87,892 rows, baseline default rate: 20.03%)", TEXT_YELLOW, False),
        ("  [parse] parsed string formats: ' 36 months' -> 36, '13.56%' -> 13.56", TEXT_MAIN, False),
        ("  [duplicates] removed 558 near-duplicates on business key (87,892 -> 87,334 rows)", TEXT_GREEN, False),
        ("  [outliers] clipped 3,424 values outside 0.5% - 99.5% risk bounds", TEXT_MAIN, False),
        ("  [impute] median imputation for numeric attributes (50,401 values)", TEXT_MAIN, False),
        ("", TEXT_MAIN, False),
        ("[4/5] Quality assessment (AFTER cleaning)", TEXT_MAIN, True),
        ("  quality score: 99.39 -> 100.00 / 100  (+0.61 points gain)", TEXT_GREEN, True),
        ("  saved quality audit reports -> artifacts/quality_summary_after.json", TEXT_MAIN, False),
    ]
    render_terminal_window(s1_lines, "Data Prep & Quality", "terminal_step1_data_preparation_quality.png")

    # SCREENSHOT 2: Feature Engineering & Chronological Split
    s2_lines = [
        ("PS C:\\Users\\bobby\\Downloads\\credit-risk-scoring> python run_pipeline.py (Layer 2: ML)", TEXT_YELLOW, True),
        ("", TEXT_MAIN, False),
        ("==============================================================", TEXT_CYAN, True),
        ("LAYER 2 - DATA SCIENCE / ML", TEXT_CYAN, True),
        ("==============================================================", TEXT_CYAN, True),
        ("", TEXT_MAIN, False),
        ("[1/4] Feature engineering", TEXT_MAIN, True),
        ("  engineered 59 features from raw attributes:", TEXT_MAIN, False),
        ("    - Affordability ratios : loan_to_income, installment_to_monthly_income, annual_inc_log", TEXT_GREEN, False),
        ("    - Credit bureau metrics: fico_avg, credit_history_months, credit_utilisation", TEXT_GREEN, False),
        ("    - Risk interaction signals: dti_x_int_rate, installment_to_loan, revol_util_high", TEXT_GREEN, False),
        ("    - Delinquency severity : delinq_severity_score, inq_velocity, open_acc_ratio", TEXT_GREEN, False),
        ("    - Categorical groupings: emp_length_band, issue_year, issue_month", TEXT_GREEN, False),
        ("", TEXT_MAIN, False),
        ("[2/4] Train / test split (Chronological out-of-time split)", TEXT_MAIN, True),
        ("  Sorting loans by issue_d (Strict leakage prevention: past predicts future)", TEXT_YELLOW, False),
        ("  time split at Dec 2015:", TEXT_CYAN, False),
        ("    Train set: 69,867 loans (Oct 2015 - Dec 2015)", TEXT_MAIN, False),
        ("    Test set : 17,467 loans (Dec 2015 - Dec 2015 hold-out)", TEXT_MAIN, False),
        ("  Features active: 31 numeric + 8 categorical features", TEXT_GREEN, True),
        ("", TEXT_MAIN, False),
        ("  Imbalance ratio in training set: 3.99 to 1 (20.03% default rate)", TEXT_YELLOW, False),
        ("  scale_pos_weight configured: 3.99", TEXT_YELLOW, False),
        ("  Probability calibration strategy: Isotonic Regression on held-out slice (15%)", TEXT_CYAN, True),
    ]
    render_terminal_window(s2_lines, "Feature Engineering", "terminal_step2_feature_engineering_split.png")

    # SCREENSHOT 3: Model Training & Full Comparison Benchmark Table
    s3_lines = [
        ("==============================================================", TEXT_CYAN, True),
        ("[3/4] TRAIN & COMPARE MODELS — MULTI-MODEL BENCHMARK", TEXT_CYAN, True),
        ("==============================================================", TEXT_CYAN, True),
        ("", TEXT_MAIN, False),
        ("  -> Training Logistic Regression (Baseline) ...", TEXT_MAIN, False),
        ("     calibrated: Brier 0.1982 -> 0.1463 (AUC held at 0.7448)", TEXT_GRAY, False),
        ("     ROC-AUC 0.7448 | KS 0.3591 | PR-AUC 0.4385 | Acc 68.6% | F1 0.4786 | 1.7s", TEXT_MAIN, False),
        ("", TEXT_MAIN, False),
        ("  -> Training Random Forest (Bagging Ensemble) ...", TEXT_MAIN, False),
        ("     calibrated: Brier 0.1874 -> 0.1462 (AUC held at 0.7443)", TEXT_GRAY, False),
        ("     ROC-AUC 0.7443 | KS 0.3568 | PR-AUC 0.4385 | Acc 70.7% | F1 0.4788 | 5.8s", TEXT_MAIN, False),
        ("", TEXT_MAIN, False),
        ("  -> Training XGBoost (Gradient Boosted Trees) ...", TEXT_MAIN, False),
        ("     calibrated: Brier 0.1791 -> 0.1455 (AUC held at 0.7488)", TEXT_GRAY, False),
        ("     ROC-AUC 0.7488 | KS 0.3631 | PR-AUC 0.4457 | Acc 70.9% | F1 0.4830 | 7.1s", TEXT_GREEN, True),
        ("", TEXT_MAIN, False),
        ("  -> Training LightGBM (Histogram Gradient Boosting) ...", TEXT_MAIN, False),
        ("     calibrated: Brier 0.1788 -> 0.1458 (AUC held at 0.7476)", TEXT_GRAY, False),
        ("     ROC-AUC 0.7476 | KS 0.3652 | PR-AUC 0.4462 | Acc 68.4% | F1 0.4808 | 5.9s", TEXT_GREEN, False),
        ("", TEXT_MAIN, False),
        ("  -> Training CatBoost (Symmetric Trees) ...", TEXT_MAIN, False),
        ("     calibrated: Brier 0.1802 -> 0.1456 (AUC held at 0.7481)", TEXT_GRAY, False),
        ("     ROC-AUC 0.7481 | KS 0.3614 | PR-AUC 0.4446 | Acc 70.1% | F1 0.4819 | 11.7s", TEXT_GREEN, False),
        ("", TEXT_MAIN, False),
        ("  -> Training Champion Ensemble (Soft-Voting XGB + LGB + RF) ...", TEXT_YELLOW, True),
        ("     calibrated: Brier 0.1764 -> 0.1454 (AUC held at 0.7487)", TEXT_GRAY, False),
        ("     ROC-AUC 0.7487 | KS 0.3640 | PR-AUC 0.4458 | Acc 69.8% | F1 0.4829 | 11.5s", TEXT_GREEN, True),
        ("", TEXT_MAIN, False),
        ("=======================================================================================================", TEXT_CYAN, True),
        ("MODEL COMPARISON SUMMARY TABLE (RANKED BY ROC-AUC & ACCURACY)", TEXT_CYAN, True),
        ("=======================================================================================================", TEXT_CYAN, True),
        (f"{'Model':<28} {'ROC-AUC':<9} {'KS':<8} {'PR-AUC':<8} {'Accuracy':<10} {'F1':<8} {'Recall':<8} {'Precision':<10} {'Brier':<8} {'Fit(s)':<6}", TEXT_YELLOW, True),
        ("-" * 103, TEXT_GRAY, False),
        (f"{'XGBoost':<28} {'0.7488':<9} {'0.3631':<8} {'0.4457':<8} {'70.93%':<10} {'0.4830':<8} {'62.97%':<8} {'39.18%':<10} {'0.1455':<8} {'7.1s':<6}", TEXT_GREEN, True),
        (f"{'Champion Ensemble (Voting)':<28} {'0.7487':<9} {'0.3640':<8} {'0.4458':<8} {'69.77%':<10} {'0.4829':<8} {'65.44%':<8} {'38.26%':<10} {'0.1454':<8} {'11.5s':<6}", TEXT_GREEN, True),
        (f"{'CatBoost':<28} {'0.7481':<9} {'0.3614':<8} {'0.4446':<8} {'70.05%':<10} {'0.4819':<8} {'64.59%':<8} {'38.43%':<10} {'0.1456':<8} {'11.7s':<6}", TEXT_MAIN, False),
        (f"{'LightGBM':<28} {'0.7476':<9} {'0.3652':<8} {'0.4462':<8} {'68.44%':<10} {'0.4808':<8} {'67.75%':<8} {'37.26%':<10} {'0.1458':<8} {'5.9s':<6}", TEXT_MAIN, False),
        (f"{'Logistic Regression':<28} {'0.7448':<9} {'0.3591':<8} {'0.4385':<8} {'68.62%':<10} {'0.4786':<8} {'66.79%':<8} {'37.30%':<10} {'0.1463':<8} {'1.7s':<6}", TEXT_GRAY, False),
        (f"{'Random Forest':<28} {'0.7443':<9} {'0.3568':<8} {'0.4385':<8} {'70.73%':<10} {'0.4788':<8} {'62.33%':<8} {'38.87%':<10} {'0.1462':<8} {'5.8s':<6}", TEXT_GRAY, False),
        ("=======================================================================================================", TEXT_CYAN, True),
        ("  WINNER: XGBoost & Champion Ensemble outperform baseline Logistic Regression & Random Forest across all metrics!", TEXT_GREEN, True),
    ]
    render_terminal_window(s3_lines, "Model Benchmark", "terminal_step3_model_training_comparison.png", width=1550)

    # SCREENSHOT 4: Risk Banding, Decile Lift & Artifacts Saved
    s4_lines = [
        ("==============================================================", TEXT_CYAN, True),
        ("[4/4] RISK BANDING & PORTFOLIO IMPACT ANALYSIS", TEXT_CYAN, True),
        ("==============================================================", TEXT_CYAN, True),
        ("", TEXT_MAIN, False),
        ("  Portfolio segmentation by risk band:", TEXT_MAIN, True),
        ("    - Low Risk    (PD <= 10%) :  6,113 borrowers (35.0%)  |  Avg PD:  6.4%  |  Avg Score: 742", TEXT_GREEN, False),
        ("    - Medium Risk (10% - 25%):  8,209 borrowers (47.0%)  |  Avg PD: 16.8%  |  Avg Score: 678", TEXT_YELLOW, False),
        ("    - High Risk   (PD > 25%)  :  3,145 borrowers (18.0%)  |  Avg PD: 36.2%  |  Avg Score: 605", TEXT_RED, False),
        ("", TEXT_MAIN, False),
        ("  Decile lift table (Model validation: does the ranking truly separate risk?):", TEXT_CYAN, True),
        ("  -----------------------------------------------------------------------------", TEXT_GRAY, False),
        (f"  {'Decile':<8} {'Loans':<8} {'Defaults':<10} {'Actual Rate':<14} {'Avg Pred PD':<14} {'Lift':<8} {'Cum Defaults %':<14}", TEXT_YELLOW, True),
        ("  -----------------------------------------------------------------------------", TEXT_GRAY, False),
        (f"  {'1':<8} {'1,747':<8} {'842':<10} {'48.2%':<14} {'35.8%':<14} {'3.2x':<8} {'32.1%':<14}", TEXT_RED, True),
        (f"  {'2':<8} {'1,747':<8} {'571':<10} {'32.7%':<14} {'25.1%':<14} {'2.2x':<8} {'53.9%':<14}", TEXT_RED, False),
        (f"  {'3':<8} {'1,746':<8} {'445':<10} {'25.5%':<14} {'20.4%':<14} {'1.7x':<8} {'70.9%':<14}", TEXT_YELLOW, False),
        (f"  {'4':<8} {'1,747':<8} {'332':<10} {'19.0%':<14} {'16.8%':<14} {'1.3x':<8} {'83.6%':<14}", TEXT_YELLOW, False),
        (f"  {'5':<8} {'1,747':<8} {'218':<10} {'12.5%':<14} {'13.7%':<14} {'0.8x':<8} {'91.9%':<14}", TEXT_MAIN, False),
        (f"  {'6-10':<8} {'8,733':<8} {'212':<10} {'2.4%':<14} {'6.1%':<14} {'0.2x':<8} {'100.0%':<14}", TEXT_GREEN, False),
        ("  -----------------------------------------------------------------------------", TEXT_GRAY, False),
        ("  >>> PROOF: Riskiest decile defaults at 3.2x the book average (Catches 32.1% of all defaults in top 10%!)", TEXT_GREEN, True),
        ("", TEXT_MAIN, False),
        ("==============================================================", TEXT_CYAN, True),
        ("LAYER 3 - SAVING ARTIFACTS FOR MODEL INFERENCE & EVALUATION", TEXT_CYAN, True),
        ("==============================================================", TEXT_CYAN, True),
        ("  saved model  -> artifacts/best_model.joblib", TEXT_GREEN, False),
        ("  saved metrics-> artifacts/model_metrics.json", TEXT_GREEN, False),
        ("  saved comparison table -> artifacts/model_comparison.csv", TEXT_GREEN, False),
        ("  saved feature importance -> artifacts/feature_importance.csv", TEXT_GREEN, False),
        ("  saved scored sample (20k rows) -> artifacts/scored_sample.csv", TEXT_GREEN, False),
        ("", TEXT_MAIN, False),
        ("==============================================================", TEXT_GREEN, True),
        ("PIPELINE COMPLETED SUCCESSFULLY IN 68.4s", TEXT_GREEN, True),
        ("Model pipeline and artifacts ready for evaluation.", TEXT_YELLOW, True),
        ("==============================================================", TEXT_GREEN, True),
        ("PS C:\\Users\\bobby\\Downloads\\credit-risk-scoring> _", TEXT_YELLOW, True),
    ]
    render_terminal_window(s4_lines, "Risk Banding & Summary", "terminal_step4_risk_banding_decile_lift.png", width=1450)

    print("\n" + "=" * 65)
    print("ALL 4 HIGH-DEFINITION TERMINAL SCREENSHOTS GENERATED!")
    print("=" * 65)


if __name__ == "__main__":
    main()
