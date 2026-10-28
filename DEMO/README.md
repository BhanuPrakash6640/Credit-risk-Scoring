# 🎯 Demonstration Portfolio Files (`DEMO/`)

This directory contains **3 specialized sample datasets** engineered for the live demonstration in front of examiners, industry practitioners, and conference audiences (1,000+ attendees).

---

## 📂 The 3 Demonstration Files

| File | Rows | Purpose & Key Takeaways | What Happens On Screen |
| :--- | :---: | :--- | :--- |
| [01_Institutional_Portfolio_Batch_100.csv](file:///c:/Users/bobby/Downloads/credit-risk-scoring/DEMO/01_Institutional_Portfolio_Batch_100.csv) | **100** | **Institutional Macro Portfolio Scoring**<br>Demonstrates full pipeline throughput, executive KPI rollups, exposure sizing, and decision mix. | • **32 Approved** (32.0%)<br>• **39 Manual Review**<br>• **29 Declined**<br>• Total Exposure: **$1,377,600**<br>• Expected Loss: **$128,740.51**<br>• Mean FICO: **685.2**, Mean PD: **15.54%** |
| [02_Partial_Acceptance_Dirty_Data_25.csv](file:///c:/Users/bobby/Downloads/credit-risk-scoring/DEMO/02_Partial_Acceptance_Dirty_Data_25.csv) | **25** | **Fault-Tolerant Partial Acceptance & Imputation**<br>Demonstrates real-world dirty data resilience. 2 malformed rows are quarantined into an amber audit drawer while 23 valid rows score smoothly. | • **23 Scored** (8 Approve, 10 Review, 5 Decline)<br>• **2 Quarantined** (Row 6: `ERR_AMOUNT_9999`, Row 16: `-$75,000` income)<br>• Automated imputation tags displayed for missing optional features |
| [03_Executive_VIP_Case_Studies_5.csv](file:///c:/Users/bobby/Downloads/credit-risk-scoring/DEMO/03_Executive_VIP_Case_Studies_5.csv) | **5** | **The Grand Finale: All 5 System Outcomes**<br>A compact 5-applicant dossier showcasing every decision path and governance gate. | • **Row 1**: **APPROVE** (Score 850, PD 0.47%, Tier 1 Super-Prime)<br>• **Row 2**: **APPROVE** (Score 746, PD 5.33%, Tier 2 Prime)<br>• **Row 3**: **REVIEW** (Score 674, PD 16.34%, Tier 3 Referral)<br>• **Row 4**: **DECLINE** (Score 589, PD 46.03%, FCRA Adverse Action reasons)<br>• **Row 5**: **INELIGIBLE** (Policy Gate: 60-month loan excluded) |

---

## 🎤 Presenter Stage Walkthrough (Step-by-Step Script)

### Step 1: Open the Institutional Underwriting Console
1. Ensure the web application is running:
   ```bash
   python -m uvicorn app:app --host 127.0.0.1 --port 8000
   ```
2. Open `http://127.0.0.1:8000` in Google Chrome or Edge (Press `F11` for full-screen stage mode).

---

### Step 2: Upload File 1 — `01_Institutional_Portfolio_Batch_100.csv`
- **Action**: Drag and drop [01_Institutional_Portfolio_Batch_100.csv](file:///c:/Users/bobby/Downloads/credit-risk-scoring/DEMO/01_Institutional_Portfolio_Batch_100.csv) into the upload dropzone (or click Browse and select it).
- **What to say**:
  > *"Here we are feeding a live batch of 100 heterogeneous consumer loan applications into our production underwriting engine. The pipeline validates the schema, computes the engineered credit features, scores through the calibrated champion model, and applies our dual-cutoff threshold matrix ($\tau_{\text{low}}=10\%$, $\tau_{\text{high}}=20\%$)."*
- **Showcase to the audience**:
  1. **Top KPI Bar**: Point out **$1.38M Total Exposure**, **$128.7K Expected Loss**, and the exact portfolio default probability (**15.54%**).
  2. **Filter Pills**: Click **"Approve (32)"**, **"Review (39)"**, and **"Decline (29)"** to demonstrate instantaneous reactive filtering.
  3. **Export**: Point out the "Export Decided Portfolio (CSV)" button for core banking integration.

---

### Step 3: Upload File 2 — `02_Partial_Acceptance_Dirty_Data_25.csv`
- **Action**: Drag and drop [02_Partial_Acceptance_Dirty_Data_25.csv](file:///c:/Users/bobby/Downloads/credit-risk-scoring/DEMO/02_Partial_Acceptance_Dirty_Data_25.csv).
- **What to say**:
  > *"In legacy underwriting systems, a single corrupted cell in a 1,000-row file causes an unhandled HTTP 500 server crash, aborting the entire batch. Watch how our enterprise pipeline handles real-world dirty data."*
- **Showcase to the audience**:
  1. The scoring completes with **HTTP 200 OK**.
  2. Highlight the amber **"Could Not Score (2 Records Quarantined)"** alert banner.
  3. Click to expand the quarantine table: show **Row 6** (corrupted non-numeric loan amount `ERR_AMOUNT_9999`) and **Row 16** (invalid negative income `-$75,000`).
  4. Point out that the remaining **23 valid rows scored cleanly** without data leakage, and optional missing fields were median-imputed with full transparency badges.

---

### Step 4: Upload File 3 — `03_Executive_VIP_Case_Studies_5.csv`
- **Action**: Drag and drop [03_Executive_VIP_Case_Studies_5.csv](file:///c:/Users/bobby/Downloads/credit-risk-scoring/DEMO/03_Executive_VIP_Case_Studies_5.csv).
- **What to say**:
  > *"To demonstrate our governance, explainability, and policy gates, we have curated 5 distinct executive case studies that cover every branch of the decision engine."*
- **Showcase to the audience**:
  1. **Row 1 (Prime Approve)**: Click to open the **Applicant Dossier Modal**. Show the 850 credit score, near-zero default probability (0.47%), and prime underwriting rationale.
  2. **Row 3 (Manual Review)**: Click row 3. Explain that between $\tau_{\text{low}}$ (10%) and $\tau_{\text{high}}$ (20%), the algorithm routes the file to senior credit officers rather than blindly approving or rejecting.
  3. **Row 4 (Decline & TreeSHAP)**: Click row 4. Show the **Adverse Action Notice (FCRA Compliant)**:
     - Top Reason 1: High revolving utilization (84.5%)
     - Top Reason 2: Low FICO score (635)
     - Top Reason 3: Elevated debt-to-income ratio (28.5%)
     - Emphasize that these are dynamically computed from TreeSHAP negative log-odds contributions.
  4. **Row 5 (Policy Eligibility Gate)**: Show the **Ineligible** badge. Point out that before machine learning even touches the file, our institutional policy gate flags 60-month terms to restrict collateral duration risk.

---

## 🏆 Summary Checklist for Tomorrow
- [x] Web server tested and active on `http://127.0.0.1:8000`
- [x] Full-screen presentation mode (`F11`) verified
- [x] All 3 files present in `DEMO/` directory
- [x] Dark mode toggle tested and functioning
- [x] Modal `Esc` key and close button verified
- [x] Camera-ready IEEE Paper and Presentation PDF synced
