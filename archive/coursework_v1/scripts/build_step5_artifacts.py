"""
Step 5 Implementation Script:
1. Trains and saves Champion XGBoost (Option A True No-LC) and Challenger Logistic Regression.
2. Analyzes risk band distribution on the test set under ~15% default rate.
3. Computes real PSI (train vs test) for predicted score and top 10 features, saving to artifacts/psi.json.
4. Generates SHAP TreeExplainer, top-4 plain English reason code generator, and global SHAP summary plot.
"""

import sys
import time
from pathlib import Path
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import joblib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

import config
from src import data_loader, cleaning, features, models, risk

def calculate_psi(expected, actual, num_buckets=10, epsilon=1e-4):
    exp = pd.Series(expected).dropna().to_numpy()
    act = pd.Series(actual).dropna().to_numpy()
    if len(exp) == 0 or len(act) == 0:
        return {"psi": 0.0, "status": "Stable"}

    percentiles = np.linspace(0, 100, num_buckets + 1)
    bins = np.percentile(exp, percentiles)
    bins = np.unique(bins)
    if len(bins) < 2:
        return {"psi": 0.0, "status": "Stable"}

    bins[0] = -np.inf
    bins[-1] = np.inf

    exp_counts, _ = np.histogram(exp, bins=bins)
    act_counts, _ = np.histogram(act, bins=bins)

    exp_pct = exp_counts / len(exp)
    act_pct = act_counts / len(act)

    exp_pct = np.where(exp_pct == 0, epsilon, exp_pct)
    act_pct = np.where(act_pct == 0, epsilon, act_pct)

    psi_vals = (act_pct - exp_pct) * np.log(act_pct / exp_pct)
    total_psi = float(np.sum(psi_vals))

    if total_psi < 0.10:
        status = "Stable (PSI < 0.10)"
    elif total_psi < 0.25:
        status = "Moderate Drift (0.10 <= PSI < 0.25)"
    else:
        status = "Significant Drift (PSI >= 0.25)"

    return {
        "psi": round(total_psi, 4),
        "status": status,
        "n_expected": len(exp),
        "n_actual": len(act),
    }

FEATURE_HUMAN_NAMES = {
    "dti": "Debt-to-income ratio",
    "annual_inc_log": "Annual income level",
    "revol_bal": "Revolving credit balance",
    "acc_open_past_24mths": "Recent accounts opened (past 24 months)",
    "credit_history_months": "Length of credit history",
    "bc_util": "Bankcard credit utilization",
    "fico_avg": "FICO credit bureau score",
    "credit_utilisation": "Total credit utilization",
    "credit_limit_util": "Credit limit utilization ratio",
    "open_acc_ratio": "Proportion of active credit lines",
    "revol_util": "Revolving balance utilization",
    "loan_to_income": "Loan amount relative to annual income",
    "inq_velocity": "Velocity of credit inquiries",
    "inq_last_6mths": "Recent credit inquiries (past 6 months)",
    "mort_acc": "Number of mortgage accounts",
    "pub_rec_bankruptcies": "Public bankruptcy records",
    "delinq_2yrs": "Recent delinquencies (past 2 years)",
    "has_delinq_history": "Historical delinquency flag",
}

def generate_reason_codes(feature_names, shap_values, original_row, top_k=4):
    """
    Generate plain-English adverse action / risk explanation reason codes.
    Positive SHAP value -> Increases default risk (risk driver).
    Negative SHAP value -> Decreases default risk (protective factor).
    """
    items = []
    for name, val in zip(feature_names, shap_values):
        clean_name = name.replace("num__", "").replace("cat__", "")
        # base name before onehot
        base_name = clean_name.split("_")[0] if "_" in clean_name and clean_name not in FEATURE_HUMAN_NAMES else clean_name
        label = FEATURE_HUMAN_NAMES.get(clean_name, FEATURE_HUMAN_NAMES.get(base_name, clean_name.replace("_", " ").title()))
        
        orig_val = original_row.get(clean_name, original_row.get(base_name, "N/A")) if original_row is not None else "N/A"
        
        # Build plain-English description
        if val > 0:
            direction = "increased risk"
            if "dti" in clean_name.lower():
                desc = f"Elevated debt-to-income ratio ({orig_val}%) increased risk"
            elif "fico" in clean_name.lower():
                desc = f"Below-average credit score ({orig_val}) increased risk"
            elif "inq" in clean_name.lower():
                desc = f"Recent credit inquiry activity increased risk"
            elif "loan_to_income" in clean_name.lower():
                desc = f"High loan amount relative to stated income increased risk"
            elif "annual_inc" in clean_name.lower():
                desc = f"Stated annual income level increased risk"
            elif "acc_open" in clean_name.lower():
                desc = f"High number of recent accounts opened ({orig_val}) increased risk"
            elif "bc_util" in clean_name.lower() or "revol_util" in clean_name.lower():
                desc = f"High revolving credit line utilization ({orig_val}%) increased risk"
            else:
                desc = f"High {label.lower()} increased default risk"
        else:
            direction = "decreased risk"
            if "fico" in clean_name.lower():
                desc = f"Strong credit bureau score ({orig_val}) reduced risk"
            elif "credit_history" in clean_name.lower():
                desc = f"Established credit history ({orig_val} months) reduced risk"
            elif "annual_inc" in clean_name.lower():
                desc = f"Strong verified annual income reduced risk"
            elif "mort_acc" in clean_name.lower():
                desc = f"Home mortgage account presence reduced risk"
            elif "dti" in clean_name.lower():
                desc = f"Manageable debt-to-income ratio ({orig_val}%) reduced risk"
            else:
                desc = f"Favorable {label.lower()} reduced risk"

        items.append({
            "feature": clean_name,
            "label": label,
            "shap_value": round(float(val), 4),
            "abs_impact": float(abs(val)),
            "impact": direction,
            "description": desc,
            "value": orig_val
        })

    # Sort by absolute impact
    items.sort(key=lambda x: x["abs_impact"], reverse=True)
    return items[:top_k]

def main():
    print("=" * 68)
    print("STEP 5: REAL PSI, SHAP TREEEXPLAINER, AND RISK BAND AUDIT")
    print("=" * 68)

    config.EXCLUDE_LC_RISK_SIGNALS = True
    config.LOAN_TERM_MONTHS = 36

    print("\n[1/5] Ingesting and splitting data...")
    raw = data_loader.load_raw()
    clean_df, _ = cleaning.clean(raw, verbose=False)
    feat_df = features.build_features(clean_df, verbose=False)
    train_df, cal_df, test_df = features.time_split(feat_df, return_cal=True)

    X_train, y_train, num, cat = features.prepare_xy(train_df)
    X_cal, y_cal, _, _ = features.prepare_xy(cal_df)
    X_test, y_test, _, _ = features.prepare_xy(test_df)

    print("\n[2/5] Training Champion XGBoost & Challenger Logistic Regression...")
    from xgboost import XGBClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline

    pos_weight = float((y_train == 0).sum() / max((y_train == 1).sum(), 1))

    xgb_clf = XGBClassifier(
        n_estimators=250,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=30,
        gamma=0.3,
        reg_lambda=4.0,
        reg_alpha=0.5,
        scale_pos_weight=pos_weight,
        eval_metric="auc",
        random_state=config.RANDOM_STATE,
        n_jobs=-1,
        tree_method="hist",
    )

    logreg_clf = LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=config.RANDOM_STATE,
    )

    prep = features.build_preprocessor(num, cat)
    champion_pipe = Pipeline([("prep", prep), ("model", xgb_clf)])
    champion_pipe.fit(X_train, y_train)

    # Calibrate on calibration set
    champion_calibrated = models._calibrate(champion_pipe, X_cal, y_cal)

    # Threshold on cal set
    prob_cal = champion_calibrated.predict_proba(X_cal)[:, 1]
    tuned_threshold = models.find_best_threshold(y_cal, prob_cal)

    # Predict on test
    prob_test = champion_calibrated.predict_proba(X_test)[:, 1]
    eval_metrics = models.evaluate(y_test, prob_test, threshold=tuned_threshold)
    eval_metrics["tuned_threshold"] = round(float(tuned_threshold), 4)

    # Challenger evaluation
    prep_lr = features.build_preprocessor(num, cat)
    challenger_pipe = Pipeline([("prep", prep_lr), ("model", logreg_clf)])
    challenger_pipe.fit(X_train, y_train)
    challenger_cal = models._calibrate(challenger_pipe, X_cal, y_cal)
    prob_test_lr = challenger_cal.predict_proba(X_test)[:, 1]
    eval_metrics_lr = models.evaluate(y_test, prob_test_lr, threshold=tuned_threshold)

    print(f"  Champion XGBoost Test ROC-AUC: {eval_metrics['roc_auc']:.4f} | PR-AUC: {eval_metrics['pr_auc']:.4f} | KS: {eval_metrics['ks']:.4f} | Brier: {eval_metrics['brier']:.4f} | Tuned Thr: {tuned_threshold:.2f}")
    print(f"  Challenger LogReg Test ROC-AUC: {eval_metrics_lr['roc_auc']:.4f} | PR-AUC: {eval_metrics_lr['pr_auc']:.4f} | KS: {eval_metrics_lr['ks']:.4f}")

    print("\n[3/5] AUDITING RISK BANDS & SCORECARD AT ~15% DEFAULT RATE...")
    scored_test = risk.score_dataframe(test_df, champion_calibrated)
    band_summary = risk.portfolio_summary(scored_test)
    print("\nPortfolio Distribution by Risk Band on Test Set:")
    print(band_summary.to_string())

    print("\n[4/5] COMPUTING REAL POPULATION STABILITY INDEX (PSI)...")
    prob_train = champion_calibrated.predict_proba(X_train)[:, 1]
    score_train = risk.probability_to_score(prob_train)
    score_test = scored_test["credit_score"].to_numpy()

    psi_results = {}
    psi_score = calculate_psi(score_train, score_test)
    psi_pd = calculate_psi(prob_train, prob_test)
    psi_results["credit_score_psi"] = psi_score
    psi_results["default_probability_psi"] = psi_pd

    print(f"  Credit Score PSI (Train vs Test): {psi_score['psi']:.4f} -> {psi_score['status']}")
    print(f"  Default Probability PSI:          {psi_pd['psi']:.4f} -> {psi_pd['status']}")

    # Top features PSI
    top_features = ["dti", "annual_inc_log", "revol_bal", "acc_open_past_24mths",
                    "credit_history_months", "bc_util", "fico_avg", "credit_utilisation",
                    "loan_to_income", "revol_util"]
    feature_psi = {}
    for feat in top_features:
        if feat in X_train.columns:
            f_res = calculate_psi(X_train[feat], X_test[feat])
            feature_psi[feat] = f_res
            print(f"  PSI · {feat:<28}: {f_res['psi']:.4f} ({f_res['status']})")
    psi_results["features_psi"] = feature_psi

    with open(config.ARTIFACT_DIR / "psi.json", "w") as f:
        json.dump(psi_results, f, indent=2)
    print(f"  Saved real PSI calculations -> {config.ARTIFACT_DIR / 'psi.json'}")

    print("\n[5/5] SHAP TREEEXPLAINER & REASON CODE GENERATION...")
    import xgboost as xgb
    import shap
    unwrapped = models.unwrap_pipeline(champion_calibrated)
    xgb_model = unwrapped.named_steps["model"]
    prep_step = unwrapped.named_steps["prep"]

    # Sample 5000 test cases for SHAP background and global summary plot
    sample_X_test = X_test.sample(min(5000, len(X_test)), random_state=42)
    X_test_proc = prep_step.transform(sample_X_test)
    feat_names = list(prep_step.get_feature_names_out())
    clean_names = [f.replace("num__", "").replace("cat__", "") for f in feat_names]

    # Native XGBoost TreeSHAP computation
    # XGBoost prohibits '<', '[', ']' in DMatrix feature_names
    xgb_feat_names = [
        f.replace("<", "lt_").replace(">", "gt_").replace("[", "").replace("]", "")
        for f in clean_names
    ]
    dmat = xgb.DMatrix(X_test_proc, feature_names=xgb_feat_names)
    contribs = xgb_model.get_booster().predict(dmat, pred_contribs=True)
    shap_vals = contribs[:, :-1]

    # Save SHAP summary plot
    fig_dir = config.ARTIFACT_DIR / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(10, 6))
    shap.summary_plot(shap_vals, X_test_proc, feature_names=clean_names, show=False)
    plt.tight_layout()
    shap_plot_path = fig_dir / "shap_summary.png"
    plt.savefig(shap_plot_path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"  Saved SHAP summary plot -> {shap_plot_path}")

    # Test individual applicant reason codes on 2 distinct test borrowers
    print("\nSample Adverse Action Reason Codes for Applicants:")
    for idx in [0, 10]:
        applicant_raw = sample_X_test.iloc[idx].to_dict()
        app_shap = shap_vals[idx]
        reasons = generate_reason_codes(clean_names, app_shap, applicant_raw, top_k=4)
        pd_val = prob_test[idx]
        print(f"\n  Applicant #{idx} (Predicted PD: {pd_val:.2%}, Score: {risk.probability_to_score(pd_val)}):")
        for r_i, r in enumerate(reasons, 1):
            print(f"    {r_i}. {r['description']} [SHAP impact: {r['shap_value']:+.4f}]")

    # Save best_model.joblib with Champion XGBoost
    print("\nSaving Champion Model (Option A XGBoost) -> best_model.joblib...")
    models.save(champion_calibrated, {"XGBoost (Champion)": eval_metrics, "Logistic Regression (Challenger)": eval_metrics_lr}, "XGBoost (Champion)", num, cat)

    print("\nStep 5 Completed Successfully.")

if __name__ == "__main__":
    main()
