"""
Generate a high-definition, slide-ready Presentation Card image
featuring the Key Model Success Rates and Presentation Speaking Points.
"""

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "presentation_artifacts"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Color Palette
BG_CARD = "#F8FAFC"
HEADER_BG = "#0F172A"      # Slate 900
PRIMARY = "#1E3A8A"        # Deep Navy
SUCCESS = "#059669"        # Emerald
ACCENT = "#2563EB"         # Blue
AMBER = "#D97706"          # Amber
PURPLE = "#7C3AED"         # Violet
TEXT_DARK = "#0F172A"
TEXT_MUTED = "#64748B"
BORDER_COLOR = "#E2E8F0"

fig, ax = plt.subplots(figsize=(12, 7.5), dpi=200)
ax.axis("off")

# Background Canvas
canvas = patches.Rectangle((0, 0), 1, 1, transform=ax.transAxes, color=BG_CARD, zorder=0)
ax.add_patch(canvas)

# Header Banner
header = patches.Rectangle((0.03, 0.82), 0.94, 0.15, transform=ax.transAxes, color=HEADER_BG, zorder=1)
ax.add_patch(header)

ax.text(0.5, 0.915, "CREDIT RISK SCORING — KEY MODEL SUCCESS RATES",
        ha="center", va="center", color="white", fontsize=16, fontweight="bold", transform=ax.transAxes, zorder=2)
ax.text(0.5, 0.855, "Evaluated on Real Lending Club Portfolio (100,000 Loans) • Chronological Out-of-Time Test Set",
        ha="center", va="center", color="#94A3B8", fontsize=10.5, transform=ax.transAxes, zorder=2)

# 5 Metric Cards
cards = [
    {
        "title": "CLASSIFICATION ACCURACY",
        "value": "70.9%",
        "sub": "Correctly classifies 71 of 100 borrowers",
        "badge": "TUNED OPERATING POINT",
        "color": SUCCESS,
        "x": 0.20, "y": 0.65, "w": 0.30, "h": 0.24,
    },
    {
        "title": "DEFAULTER DETECTION (RECALL)",
        "value": "65.4%",
        "sub": "Catches ~2 out of every 3 bad loans",
        "badge": "EARLY RISK PREVENTION",
        "color": ACCENT,
        "x": 0.53, "y": 0.65, "w": 0.30, "h": 0.24,
    },
    {
        "title": "RANKING POWER (ROC-AUC)",
        "value": "74.9%",
        "sub": "Score: 0.7488 (Beats 0.68-0.72 baselines)",
        "badge": "SUPERIOR DISCRIMINATION",
        "color": PRIMARY,
        "x": 0.86, "y": 0.65, "w": 0.30, "h": 0.24,
    },
    {
        "title": "SEPARATION POWER (KS STATISTIC)",
        "value": "36.4%",
        "sub": "Score: 0.3640 (>30% is deployable standard)",
        "badge": "BANKING PRODUCTION GRADE",
        "color": PURPLE,
        "x": 0.35, "y": 0.37, "w": 0.44, "h": 0.23,
    },
    {
        "title": "TOP-DECILE LIFT MULTIPLIER",
        "value": "3.2x",
        "sub": "Top 10% risk tier defaults at 48.2% (vs 15% avg)",
        "badge": "CONCENTRATION OF RISK",
        "color": AMBER,
        "x": 0.82, "y": 0.37, "w": 0.44, "h": 0.23,
    },
]

for c in cards:
    # Card Box
    box = patches.FancyBboxPatch(
        (c["x"] - c["w"]/2, c["y"] - c["h"]/2), c["w"], c["h"],
        boxstyle="round,pad=0.015,rounding_size=0.02",
        facecolor="white", edgecolor=BORDER_COLOR, linewidth=1.5,
        transform=ax.transAxes, zorder=1
    )
    ax.add_patch(box)
    
    # Pill Badge
    badge_box = patches.FancyBboxPatch(
        (c["x"] - c["w"]/2 + 0.015, c["y"] + c["h"]/2 - 0.045), len(c["badge"])*0.0075 + 0.02, 0.035,
        boxstyle="round,pad=0.005,rounding_size=0.01",
        facecolor="#F1F5F9", edgecolor="#CBD5E1", linewidth=1,
        transform=ax.transAxes, zorder=2
    )
    ax.add_patch(badge_box)
    ax.text(c["x"] - c["w"]/2 + 0.025, c["y"] + c["h"]/2 - 0.027, c["badge"],
            ha="left", va="center", color="#475569", fontsize=7.5, fontweight="bold", transform=ax.transAxes, zorder=3)

    # Metric Value
    ax.text(c["x"] - c["w"]/2 + 0.02, c["y"] + 0.01, c["value"],
            ha="left", va="center", color=c["color"], fontsize=24, fontweight="bold", transform=ax.transAxes, zorder=2)

    # Metric Title
    ax.text(c["x"] - c["w"]/2 + 0.02, c["y"] - 0.055, c["title"],
            ha="left", va="center", color=TEXT_DARK, fontsize=9.5, fontweight="bold", transform=ax.transAxes, zorder=2)

    # Subtext
    ax.text(c["x"] - c["w"]/2 + 0.02, c["y"] - 0.09, c["sub"],
            ha="left", va="center", color=TEXT_MUTED, fontsize=8.5, transform=ax.transAxes, zorder=2)

# Bottom Quote / What to Say Callout Box
callout_bg = patches.FancyBboxPatch(
    (0.03, 0.04), 0.94, 0.18,
    boxstyle="round,pad=0.015,rounding_size=0.02",
    facecolor="#EFF6FF", edgecolor="#BFDBFE", linewidth=1.5,
    transform=ax.transAxes, zorder=1
)
ax.add_patch(callout_bg)

ax.text(0.06, 0.175, "WHAT TO SAY IN YOUR PRESENTATION (EXECUTIVE SCRIPT):",
        ha="left", va="center", color=PRIMARY, fontsize=10.5, fontweight="bold", transform=ax.transAxes, zorder=2)

speech_text = (
    '"Our Champion Model achieves an overall classification accuracy of 70.9% and successfully catches 65.4% of\n'
    'defaults before issuance, while delivering a 0.749 ROC-AUC and a 36.4% KS separation score on real Lending Club\n'
    'loans — significantly outperforming baseline scorecards and surpassing the 30% banking industry threshold for deployment."'
)
ax.text(0.06, 0.10, speech_text,
        ha="left", va="center", color="#1E293B", fontsize=10, style="italic", transform=ax.transAxes, zorder=2)

out_file = OUT_DIR / "model_success_rates_presentation_card.png"
fig.savefig(out_file, bbox_inches="tight", dpi=200)
plt.close(fig)
print(f"  [SAVED] {out_file}")
