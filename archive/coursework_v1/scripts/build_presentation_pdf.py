"""
Generate a professional, multi-page presentation PDF slide deck
strictly focused on Data Engineering, Model Training, Benchmark Results,
and Terminal Screenshots.
"""

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "presentation_artifacts"
PDF_PATH = ASSET_DIR / "Credit_Risk_Model_Training_Presentation.pdf"

# Design Tokens (Corporate Presentation Theme)
NAVY = "#0F172A"       # Slate 900
PRIMARY = "#1E3A8A"    # Deep Navy
SLATE = "#475569"      # Slate 600
LIGHT_BG = "#F8FAFC"   # Slate 50
ACCENT = "#2563EB"     # Royal Blue
BORDER = "#E2E8F0"

def create_slide_figure():
    """Create a 16:9 widescreen slide figure."""
    fig = plt.figure(figsize=(16, 9), dpi=150, facecolor="white")
    return fig

def add_header_footer(fig, title: str, category: str, page_num: int, total_pages: int = 15):
    # Top banner bar
    top_ax = fig.add_axes([0, 0.90, 1.0, 0.10])
    top_ax.axis("off")
    top_ax.set_facecolor(NAVY)
    top_ax.fill_between([0, 1], 0, 1, color=NAVY)
    top_ax.text(0.04, 0.60, category.upper(), color="#93C5FD", fontsize=11, fontweight="bold", transform=top_ax.transAxes)
    top_ax.text(0.04, 0.22, title, color="white", fontsize=18, fontweight="bold", transform=top_ax.transAxes)

    # Bottom footer bar
    bot_ax = fig.add_axes([0, 0, 1.0, 0.05])
    bot_ax.axis("off")
    bot_ax.set_facecolor(LIGHT_BG)
    bot_ax.fill_between([0, 1], 0, 1, color=LIGHT_BG)
    bot_ax.text(0.04, 0.35, "Credit Risk Scoring & Loan Default Prediction • Model Training & Validation Report",
                color=SLATE, fontsize=10, transform=bot_ax.transAxes)
    bot_ax.text(0.96, 0.35, f"{page_num} / {total_pages}",
                color=SLATE, fontsize=10, fontweight="bold", ha="right", transform=bot_ax.transAxes)

def load_img(name: str):
    p = ASSET_DIR / name
    if p.exists():
        return Image.open(p)
    p2 = ROOT / "docs" / "screenshots" / name
    if p2.exists():
        return Image.open(p2)
    return None

def main():
    print("=" * 65)
    print("GENERATING PRESENTATION PDF (MODEL & TRAINING ONLY)")
    print("=" * 65)

    with PdfPages(PDF_PATH) as pdf:
        total_pages = 15

        # =====================================================================
        # SLIDE 1: TITLE / EXECUTIVE COVER SLIDE
        # =====================================================================
        fig = create_slide_figure()
        ax = fig.add_axes([0, 0, 1, 1])
        ax.axis("off")
        ax.fill_between([0, 1], 0, 1, color=NAVY)

        ax.text(0.08, 0.76, "CREDIT RISK SCORING & LOAN DEFAULT PREDICTION",
                color="#60A5FA", fontsize=16, fontweight="bold")
        ax.text(0.08, 0.64, "Machine Learning Architecture,\nModel Training & Benchmark Results",
                color="white", fontsize=30, fontweight="bold", linespacing=1.2)
        ax.text(0.08, 0.50, "End-to-end training pipeline on real Lending Club portfolio (100,000+ loans)\nOut-of-time chronological validation with Isotonic probability calibration",
                color="#94A3B8", fontsize=14, linespacing=1.4)

        # Key metric pills on cover
        pills = [
            ("ROC-AUC", "0.7488", "Beats 0.68-0.72 baselines"),
            ("KS STATISTIC", "0.3640", "Industry deployable >0.30"),
            ("ACCURACY", "70.93%", "Tuned operating point"),
            ("DEFAULTER RECALL", "65.44%", "Catches ~2/3 of all defaults"),
            ("TOP DECILE LIFT", "3.2x", "48.2% default rate in top 10%"),
        ]
        px_start = 0.08
        for label, val, sub in pills:
            card = plt.Rectangle((px_start, 0.22), 0.155, 0.19, transform=ax.transAxes,
                                 color="#1E293B", ec="#334155", lw=1.5)
            ax.add_patch(card)
            ax.text(px_start + 0.0775, 0.35, val, color="#38BDF8", fontsize=20, fontweight="bold", ha="center")
            ax.text(px_start + 0.0775, 0.29, label, color="white", fontsize=10, fontweight="bold", ha="center")
            ax.text(px_start + 0.0775, 0.24, sub, color="#94A3B8", fontsize=7.5, ha="center")
            px_start += 0.17

        ax.text(0.08, 0.10, "Author: Machine Learning & Modeling Team • Lending Club Benchmark",
                color="#64748B", fontsize=11)
        pdf.savefig(fig)
        plt.close(fig)
        print("  [Page 1] Title cover added")

        # =====================================================================
        # SLIDE 2: KEY MODEL SUCCESS RATES & EXECUTIVE TALKING POINTS
        # =====================================================================
        fig = create_slide_figure()
        add_header_footer(fig, "Key Model Success Rates & Performance Highlights", "Executive Summary", 2, total_pages)
        ax = fig.add_axes([0.05, 0.08, 0.90, 0.78])
        ax.axis("off")
        img = load_img("model_success_rates_presentation_card.png")
        if img:
            ax.imshow(img)
        pdf.savefig(fig)
        plt.close(fig)
        print("  [Page 2] Model success rates card added")

        # =====================================================================
        # SLIDE 3: DATA PREPARATION & QUALITY AUDIT (TERMINAL OUTPUT)
        # =====================================================================
        fig = create_slide_figure()
        add_header_footer(fig, "Layer 1: Data Ingestion, Leakage Prevention & Quality Audit", "Data Engineering", 3, total_pages)
        # Left: Chart, Right: Terminal Screenshot
        ax1 = fig.add_axes([0.04, 0.08, 0.45, 0.78])
        ax1.axis("off")
        img1 = load_img("step1_data_quality_assessment.png")
        if img1:
            ax1.imshow(img1)

        ax2 = fig.add_axes([0.51, 0.08, 0.45, 0.78])
        ax2.axis("off")
        img2 = load_img("terminal_step1_data_preparation_quality.png")
        if img2:
            ax2.imshow(img2)

        pdf.savefig(fig)
        plt.close(fig)
        print("  [Page 3] Data preparation & quality audit added")

        # =====================================================================
        # SLIDE 4: DATA CLEANING, SANITIZATION & MISSINGNESS RESOLUTION
        # =====================================================================
        fig = create_slide_figure()
        add_header_footer(fig, "Data Cleaning: Outlier Clipping, Imputation & Leakage Dropping", "Data Sanitization", 4, total_pages)
        ax1 = fig.add_axes([0.04, 0.08, 0.50, 0.78])
        ax1.axis("off")
        img = load_img("step2_missingness_and_cleaning.png")
        if img:
            ax1.imshow(img)

        # Bullets card on right
        ax2 = fig.add_axes([0.56, 0.12, 0.40, 0.72])
        ax2.axis("off")
        card = plt.Rectangle((0, 0), 1, 1, transform=ax2.transAxes, color=LIGHT_BG, ec=BORDER, lw=1.5)
        ax2.add_patch(card)
        ax2.text(0.06, 0.90, "STRICT LEAKAGE PREVENTION & CLEANING PROTOCOL", color=PRIMARY, fontsize=12, fontweight="bold")
        bullets = [
            "• Dropped 40 post-origination leakage columns (total_pymnt, recoveries, next_pymnt_d).",
            "• Training on leakage columns yields fake 0.99 AUC. Our model is 100% leak-free.",
            "• Filtered resolved loans only: 100,000 -> 87,892 loans (dropped ongoing/grace period).",
            "• Standardized string formatting: parsed ' 36 months' to integer, '13.56%' to float.",
            "• Removed 558 near-duplicate applications on business keys (87,892 -> 87,334 loans).",
            "• Winsorized extreme outliers at 0.5% and 99.5% boundaries (3,424 records).",
            "• Median imputation applied to incomplete credit attributes (50,401 values).",
            "• Final Data Quality Score: 100.00 / 100 (Grade A - Production Ready).",
        ]
        by = 0.78
        for b in bullets:
            ax2.text(0.06, by, b, color=NAVY, fontsize=10.5)
            by -= 0.095

        pdf.savefig(fig)
        plt.close(fig)
        print("  [Page 4] Data cleaning & sanitization added")

        # =====================================================================
        # SLIDE 5: FEATURE ENGINEERING & CHRONOLOGICAL TIME SPLIT
        # =====================================================================
        fig = create_slide_figure()
        add_header_footer(fig, "Layer 2: Domain Feature Engineering & Chronological Train/Test Split", "Feature Engineering", 5, total_pages)
        ax1 = fig.add_axes([0.04, 0.08, 0.45, 0.78])
        ax1.axis("off")
        img1 = load_img("step3_feature_correlations.png")
        if img1:
            ax1.imshow(img1)

        ax2 = fig.add_axes([0.51, 0.08, 0.45, 0.78])
        ax2.axis("off")
        img2 = load_img("terminal_step2_feature_engineering_split.png")
        if img2:
            ax2.imshow(img2)

        pdf.savefig(fig)
        plt.close(fig)
        print("  [Page 5] Feature engineering & split added")

        # =====================================================================
        # SLIDE 6: MULTI-MODEL TRAINING TERMINAL BENCHMARK (REAL OUTPUT)
        # =====================================================================
        fig = create_slide_figure()
        add_header_footer(fig, "Live Terminal Execution: 6-Model Training & Benchmark Table", "Model Training", 6, total_pages)
        ax = fig.add_axes([0.04, 0.08, 0.92, 0.78])
        ax.axis("off")
        img = load_img("terminal_step3_model_training_comparison.png")
        if img:
            ax.imshow(img)
        pdf.savefig(fig)
        plt.close(fig)
        print("  [Page 6] Terminal model benchmark table added")

        # =====================================================================
        # SLIDE 7: MODEL ACCURACY & PERFORMANCE COMPARISON
        # =====================================================================
        fig = create_slide_figure()
        add_header_footer(fig, "Multi-Model Evaluation: Baseline vs. Champion Ensemble Benchmark", "Model Benchmarking", 7, total_pages)
        ax = fig.add_axes([0.05, 0.08, 0.90, 0.78])
        ax.axis("off")
        img = load_img("step5_model_accuracy_comparison.png")
        if img:
            ax.imshow(img)
        pdf.savefig(fig)
        plt.close(fig)
        print("  [Page 7] Model accuracy comparison added")

        # =====================================================================
        # SLIDE 8: ROC CURVES & PRECISION-RECALL FRONTIERS
        # =====================================================================
        fig = create_slide_figure()
        add_header_footer(fig, "Discrimination Power: Multi-Model ROC Curves & PR Curves", "Evaluation Metrics", 8, total_pages)
        ax1 = fig.add_axes([0.04, 0.08, 0.45, 0.78])
        ax1.axis("off")
        img1 = load_img("step6_roc_curves_all_models.png")
        if img1:
            ax1.imshow(img1)

        ax2 = fig.add_axes([0.51, 0.08, 0.45, 0.78])
        ax2.axis("off")
        img2 = load_img("step7_precision_recall_curves.png")
        if img2:
            ax2.imshow(img2)

        pdf.savefig(fig)
        plt.close(fig)
        print("  [Page 8] ROC & PR curves added")

        # =====================================================================
        # SLIDE 9: CONFUSION MATRIX & PROBABILITY CALIBRATION
        # =====================================================================
        fig = create_slide_figure()
        add_header_footer(fig, "Confusion Matrix Comparison & Isotonic Probability Calibration", "Calibration & Diagnostics", 9, total_pages)
        ax1 = fig.add_axes([0.04, 0.08, 0.48, 0.78])
        ax1.axis("off")
        img1 = load_img("step8_confusion_matrix_comparison.png")
        if img1:
            ax1.imshow(img1)

        ax2 = fig.add_axes([0.53, 0.08, 0.43, 0.78])
        ax2.axis("off")
        img2 = load_img("step9_probability_calibration.png")
        if img2:
            ax2.imshow(img2)

        pdf.savefig(fig)
        plt.close(fig)
        print("  [Page 9] Confusion matrix & calibration added")

        # =====================================================================
        # SLIDE 10: RISK DRIVERS & FICO SCORECARD DISTRIBUTION
        # =====================================================================
        fig = create_slide_figure()
        add_header_footer(fig, "Feature Importance (Top 15 Drivers) & Credit Scorecard Mapping", "Risk Explainability", 10, total_pages)
        ax1 = fig.add_axes([0.04, 0.08, 0.45, 0.78])
        ax1.axis("off")
        img1 = load_img("step10_feature_importance.png")
        if img1:
            ax1.imshow(img1)

        ax2 = fig.add_axes([0.51, 0.08, 0.45, 0.78])
        ax2.axis("off")
        img2 = load_img("step11_credit_score_distribution.png")
        if img2:
            ax2.imshow(img2)

        pdf.savefig(fig)
        plt.close(fig)
        print("  [Page 10] Feature importance & scorecard added")

        # =====================================================================
        # SLIDE 11: DECILE LIFT & TERMINAL COMPLETION
        # =====================================================================
        fig = create_slide_figure()
        add_header_footer(fig, "Decile Lift Validation & Terminal Pipeline Completion", "Business Validation", 11, total_pages)
        ax1 = fig.add_axes([0.04, 0.08, 0.46, 0.78])
        ax1.axis("off")
        img1 = load_img("step12_decile_lift_gains.png")
        if img1:
            ax1.imshow(img1)

        ax2 = fig.add_axes([0.51, 0.08, 0.45, 0.78])
        ax2.axis("off")
        img2 = load_img("terminal_step4_risk_banding_decile_lift.png")
        if img2:
            ax2.imshow(img2)

        pdf.savefig(fig)
        plt.close(fig)
        print("  [Page 11] Decile lift & terminal completion added")

        # =====================================================================
        # SLIDE 12: PRODUCTION UNDERWRITING CONSOLE: PORTFOLIO OVERVIEW
        # =====================================================================
        fig = create_slide_figure()
        add_header_footer(fig, "Production Underwriting Console: Portfolio Overview & Live Analytics", "Production Deployment", 12, total_pages)
        ax1 = fig.add_axes([0.04, 0.08, 0.50, 0.78])
        ax1.axis("off")
        img1 = load_img("02_portfolio_overview.png")
        if img1:
            ax1.imshow(img1)

        ax2 = fig.add_axes([0.56, 0.10, 0.40, 0.74])
        ax2.axis("off")
        card = plt.Rectangle((0, 0), 1, 1, transform=ax2.transAxes, color=LIGHT_BG, ec=BORDER, lw=1.5)
        ax2.add_patch(card)
        ax2.text(0.06, 0.91, "REAL-TIME AUTOMATED DECISION ENGINE", color=PRIMARY, fontsize=12, fontweight="bold")
        bullets_s12 = [
            "• Production web underwriting console powered by FastAPI & Chart.js.",
            "• Zero-PII disk footprint: in-memory stream scoring compliant with GLBA.",
            "• Instantaneous scoring: <45ms inference latency per loan applicant.",
            "• Executive 6-KPI strip: Scored volume, auto-approval rate, calibrated PD,",
            "  total exposure ($3.85M demo), Basel expected loss ($320k), policy gates.",
            "• 4 live interactive charts: Underwriting decision donut, PD distribution",
            "  histogram, capital exposure vs expected loss, and scorecard distribution.",
            "• Dual-cutoff decision protocol: Approve (PD <= 10%), Review (10%-20%),",
            "  and Decline (PD > 20%) calibrated against institutional risk appetite.",
        ]
        by = 0.81
        for b in bullets_s12:
            ax2.text(0.06, by, b, color=NAVY, fontsize=10.2)
            by -= 0.085

        pdf.savefig(fig)
        plt.close(fig)
        print("  [Page 12] Production underwriting console overview added")

        # =====================================================================
        # SLIDE 13: EXPERT APPLICANT DOSSIER & COMPLIANCE EXPLAINABILITY
        # =====================================================================
        fig = create_slide_figure()
        add_header_footer(fig, "Applicant Dossier: Calibrated Scorecard, Benchmarks & TreeSHAP", "Local Explainability", 13, total_pages)
        ax1 = fig.add_axes([0.04, 0.08, 0.50, 0.78])
        ax1.axis("off")
        img1 = load_img("04_applicant_detail_view.png")
        if img1:
            ax1.imshow(img1)

        ax2 = fig.add_axes([0.56, 0.10, 0.40, 0.74])
        ax2.axis("off")
        card = plt.Rectangle((0, 0), 1, 1, transform=ax2.transAxes, color=LIGHT_BG, ec=BORDER, lw=1.5)
        ax2.add_patch(card)
        ax2.text(0.06, 0.91, "AUDITABLE BORROWER DOSSIER & FCRA CODES", color=PRIMARY, fontsize=12, fontweight="bold")
        bullets_s13 = [
            "• Semicircle Scorecard Gauge converting continuous PD to 300-850 FICO",
            "  scale via Points-to-Double-the-Odds (PDO = 40, anchor 660 @ 20% odds).",
            "• Live applicant vs. portfolio benchmark comparisons (FICO, DTI, income).",
            "• Local TreeSHAP waterfall risk decomposition quantifying exact margin",
            "  contributions from portfolio baseline to individual calibrated PD.",
            "• Top-4 FCRA §615(a) statutory Adverse Action reason codes isolating",
            "  primary risk drivers and protective financial characteristics.",
            "• Plain-English explanations ensure full regulatory auditability before",
            "  extending credit or issuing institutional loan adverse notices.",
        ]
        by = 0.81
        for b in bullets_s13:
            ax2.text(0.06, by, b, color=NAVY, fontsize=10.2)
            by -= 0.095

        pdf.savefig(fig)
        plt.close(fig)
        print("  [Page 13] Applicant dossier & explainability added")

        # =====================================================================
        # SLIDE 14: FAULT-TOLERANT PARTIAL ACCEPTANCE & AUDITABILITY
        # =====================================================================
        fig = create_slide_figure()
        add_header_footer(fig, "Fault-Tolerant Partial Acceptance & Algorithmic Accountability", "Enterprise Engineering", 14, total_pages)
        ax1 = fig.add_axes([0.04, 0.08, 0.50, 0.78])
        ax1.axis("off")
        img1 = load_img("03_results_table.png")
        if img1:
            ax1.imshow(img1)

        ax2 = fig.add_axes([0.56, 0.10, 0.40, 0.74])
        ax2.axis("off")
        card = plt.Rectangle((0, 0), 1, 1, transform=ax2.transAxes, color=LIGHT_BG, ec=BORDER, lw=1.5)
        ax2.add_patch(card)
        ax2.text(0.06, 0.91, "ENTERPRISE INGESTION & POLICY SAFEGUARDS", color=PRIMARY, fontsize=12, fontweight="bold")
        bullets_s14 = [
            "• Fault-Tolerant Partial Acceptance (Requirement 1): dirty rows with",
            "  negative incomes or invalid scores are segregated into an auditable",
            "  'Could Not Score' quarantine table, while all valid rows are scored.",
            "• Automated Imputation Tracking (Requirement 2): blank attributes are",
            "  filled using training medians and flagged with '⚡ N' badges in table",
            "  and borrower dossiers for full algorithmic transparency.",
            "• Policy Eligibility Gating: 60-month term loans are intercepted as",
            "  INELIGIBLE, preventing uncalibrated out-of-domain model drift.",
            "• Temporal Stability: PSI < 0.10 across all top predictors and scorecards.",
        ]
        by = 0.81
        for b in bullets_s14:
            ax2.text(0.06, by, b, color=NAVY, fontsize=10.2)
            by -= 0.095

        pdf.savefig(fig)
        plt.close(fig)
        print("  [Page 14] Partial acceptance & policy safeguards added")

        # =====================================================================
        # SLIDE 15: LIVE DEMONSTRATION SUMMARY & STAGE ARCHITECTURE
        # =====================================================================
        fig = create_slide_figure()
        add_header_footer(fig, "System Summary & Live Demonstration Architecture (1,000 Attendees)", "Executive Conclusion", 15, total_pages)
        ax1 = fig.add_axes([0.04, 0.08, 0.46, 0.78])
        ax1.axis("off")
        img1 = load_img("step13_presentation_summary_card.png")
        if img1:
            ax1.imshow(img1)

        ax2 = fig.add_axes([0.52, 0.10, 0.44, 0.74])
        ax2.axis("off")
        card = plt.Rectangle((0, 0), 1, 1, transform=ax2.transAxes, color=NAVY, ec="#334155", lw=1.5)
        ax2.add_patch(card)
        ax2.text(0.06, 0.91, "PROJECT TEAM & KEY TAKEAWAYS", color="#60A5FA", fontsize=12, fontweight="bold")
        bullets_s15 = [
            ("100% Leak-Free Foundation", "Purged 40 post-issuance attributes; true Bayes error rate."),
            ("Champion Model Performance", "0.7488 ROC-AUC, 0.3640 KS statistic, 3.21x top-decile lift."),
            ("Calibrated Probabilities", "Isotonic regression matches empirical priors; Brier = 0.1455."),
            ("Institutional Decision Protocol", "Approve (<=10% PD: 7.05% def) vs. Decline (>20% PD: 25.87% def)."),
            ("Real-Time Underwriting Console", "FastAPI + Chart.js, sub-45ms scoring, 1-click demo presets."),
            ("Production Governance", "Partial acceptance, imputation audits, zero-PII in-memory streaming."),
        ]
        by = 0.80
        for title_b, sub_b in bullets_s15:
            ax2.text(0.06, by, f"• {title_b}:", color="white", fontsize=10.5, fontweight="bold")
            ax2.text(0.06, by - 0.038, f"   {sub_b}", color="#94A3B8", fontsize=9.5)
            by -= 0.095

        ax2.text(0.06, 0.08, "Project Team 7 • Bhanu Prakash (2420030209) · Krishita Myneni (2420030443) · Laasya Priya (2420030002)",
                 color="#38BDF8", fontsize=9, fontweight="bold")

        pdf.savefig(fig)
        plt.close(fig)
        print("  [Page 15] Executive conclusion & stage summary added")

    # Also sync copy to root for easy user presentation access
    import shutil
    shutil.copy2(PDF_PATH, ROOT / "Credit_Risk_Model_Training_Presentation.pdf")
    print(f"  [Copied] {ROOT / 'Credit_Risk_Model_Training_Presentation.pdf'}")

    print("\n" + "=" * 65)
    print(f"PRESENTATION PDF SUCCESSFULLY GENERATED -> {PDF_PATH}")
    print("=" * 65)


if __name__ == "__main__":
    main()
