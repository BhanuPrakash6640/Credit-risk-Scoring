/**
 * Institutional Credit Risk Console - Frontend Logic
 * Rebuilt for Upload-and-Score Real-Time Underwriting Workflow with Chart.js analytics,
 * interactive sorting, filtering, pagination, and expert applicant dossier.
 */

let currentScoredData = null;
let currentFilteredApplicants = [];
let currentPage = 1;
let pageSize = 25;
let sortColumn = "id";
let sortDirection = "asc";

let filterDecision = "ALL";
let filterBand = "ALL";
let searchQuery = "";

// Chart.js instances
let decisionDonutChart = null;
let pdHistogramChart = null;
let exposureElChart = null;
let scoreDistributionChart = null;

// Color System Constants
const COLORS = {
  approve: "#10B981",
  approveBg: "#ECFDF5",
  review: "#F59E0B",
  reviewBg: "#FFFBEB",
  decline: "#EF4444",
  declineBg: "#FEF2F2",
  ineligible: "#64748B",
  ineligibleBg: "#F1F5F9",
  blue: "#2563EB",
  purple: "#8B5CF6",
};

// Drag & drop file upload initialization
document.addEventListener("DOMContentLoaded", () => {
  const dropZone = document.getElementById("dropZone");
  if (!dropZone) return;

  ["dragenter", "dragover"].forEach(eventName => {
    dropZone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropZone.classList.add("dragover");
    }, false);
  });

  ["dragleave", "drop"].forEach(eventName => {
    dropZone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropZone.classList.remove("dragover");
    }, false);
  });

  dropZone.addEventListener("drop", (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files.length > 0) {
      uploadFile(files[0]);
    }
  });
});

function handleFileSelected(event) {
  const file = event.target.files[0];
  if (file) {
    uploadFile(file);
  }
}

async function uploadFile(file) {
  if (!file.name.toLowerCase().endsWith(".csv")) {
    showError("Invalid file format. Please upload a CSV file (.csv).");
    return;
  }

  if (file.size > 5 * 1024 * 1024) {
    showError("File size exceeds 5MB limit. Please upload a smaller batch.");
    return;
  }

  hideError();
  showLoader(true);

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch("/api/score", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();
    showLoader(false);

    if (!response.ok) {
      showError(data.detail || "Failed to score applicants.");
      return;
    }

    renderResults(data);
  } catch (err) {
    showLoader(false);
    showError(`Network error communicating with scoring engine: ${err.message}`);
  }
}

async function scoreSampleApplicants() {
  hideError();
  showLoader(true);
  try {
    const res = await fetch("/api/example-batch");
    if (!res.ok) throw new Error("Could not fetch example batch file");
    const blob = await res.blob();
    const file = new File([blob], "example_applicants.csv", { type: "text/csv" });
    await uploadFile(file);
  } catch (err) {
    showLoader(false);
    showError(`Failed to load example batch: ${err.message}`);
  }
}

async function scoreDemoBatch() {
  hideError();
  showLoader(true);
  try {
    const res = await fetch("/api/demo-batch");
    if (!res.ok) throw new Error("Could not fetch demo batch file");
    const blob = await res.blob();
    const file = new File([blob], "demo_batch_300.csv", { type: "text/csv" });
    await uploadFile(file);
  } catch (err) {
    showLoader(false);
    showError(`Failed to load demo batch: ${err.message}`);
  }
}

async function scoreMixedBatch() {
  hideError();
  showLoader(true);
  try {
    const res = await fetch("/api/mixed-batch");
    if (!res.ok) throw new Error("Could not fetch mixed batch file");
    const blob = await res.blob();
    const file = new File([blob], "mixed_good_bad.csv", { type: "text/csv" });
    await uploadFile(file);
  } catch (err) {
    showLoader(false);
    showError(`Failed to load mixed batch: ${err.message}`);
  }
}

async function scoreIneligibleBatch() {
  hideError();
  showLoader(true);
  try {
    const res = await fetch("/api/ineligible-batch");
    if (!res.ok) throw new Error("Could not fetch ineligible batch file");
    const blob = await res.blob();
    const file = new File([blob], "all_60_month.csv", { type: "text/csv" });
    await uploadFile(file);
  } catch (err) {
    showLoader(false);
    showError(`Failed to load ineligible batch: ${err.message}`);
  }
}

// Global Escape key listener to close modal effortlessly during presentations
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    closeModalDirect();
  }
});

function showLoader(show) {
  const loader = document.getElementById("scoringLoader");
  if (loader) loader.style.display = show ? "block" : "none";
}

function showError(msg) {
  const errEl = document.getElementById("uploadError");
  if (errEl) {
    errEl.innerText = msg;
    errEl.style.display = "block";
  }
}

function hideError() {
  const errEl = document.getElementById("uploadError");
  if (errEl) errEl.style.display = "none";
}

function resetToUpload() {
  document.getElementById("resultsSection").style.display = "none";
  document.getElementById("uploadSection").style.display = "block";
  window.scrollTo({ top: 0, behavior: "smooth" });
}

/* ==========================================================================
   RESULTS VIEW RENDERING & PORTFOLIO CHARTS
   ========================================================================== */
function renderResults(data) {
  currentScoredData = data;
  currentPage = 1;

  document.getElementById("uploadSection").style.display = "none";
  const resultsSec = document.getElementById("resultsSection");
  resultsSec.style.display = "block";

  // Global warning for ineligible loans and invalid rows
  const warningBanner = document.getElementById("globalWarningBanner");
  const warningText = document.getElementById("globalWarningText");
  const summary = data.summary;

  if (data.global_warning) {
    warningText.innerText = data.global_warning;
    warningBanner.style.display = "flex";
  } else if (summary.ineligible_count > 0) {
    warningText.innerText = `Notice: ${summary.ineligible_count} applicant(s) requested a 60-month term. Under model governance, the champion model is calibrated strictly on 36-month cohorts. 60-month loans are flagged as INELIGIBLE ("Not scored") and excluded from portfolio performance metrics.`;
    warningBanner.style.display = "flex";
  } else {
    warningBanner.style.display = "none";
  }

  // Render Could Not Score (Invalid Records) Table if present (Point 1)
  const couldNotScoreSec = document.getElementById("couldNotScoreSection");
  const couldNotScoreTbody = document.getElementById("couldNotScoreTableBody");
  const couldNotScoreTitle = document.getElementById("couldNotScoreTitle");

  if (couldNotScoreSec && couldNotScoreTbody) {
    const invalidList = data.could_not_score || [];
    if (invalidList.length > 0) {
      if (couldNotScoreTitle) {
        couldNotScoreTitle.innerText = `Could Not Score (${invalidList.length} Record${invalidList.length > 1 ? "s" : ""})`;
      }
      couldNotScoreTbody.innerHTML = "";
      invalidList.forEach(inv => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td><strong style="color:var(--text-primary); font-family:var(--font-mono);">Row ${inv.row_number}</strong></td>
          <td><span style="color:#DC2626; font-weight:600; font-size:12.5px;">${escapeHtml(inv.reason_text)}</span></td>
          <td>${inv.loan_amnt !== "N/A" ? "$" + Number(inv.loan_amnt || 0).toLocaleString() : "—"}</td>
          <td>${inv.annual_inc !== "N/A" ? "$" + Number(inv.annual_inc || 0).toLocaleString() : "—"}</td>
          <td>${inv.dti !== "N/A" ? inv.dti + "%" : "—"}</td>
          <td>${inv.fico !== "N/A" ? inv.fico : "—"}</td>
          <td>${formatTitle(inv.purpose || "—")}</td>
        `;
        couldNotScoreTbody.appendChild(tr);
      });
      couldNotScoreSec.style.display = "block";
    } else {
      couldNotScoreSec.style.display = "none";
    }
  }

  // Populate Executive KPIs
  document.getElementById("metricTotal").innerText = Number(summary.eligible_count || 0).toLocaleString();
  document.getElementById("metricDecisionsSub").innerText = `${summary.approved_count} Approved · ${summary.review_count} Review · ${summary.declined_count} Declined`;

  document.getElementById("metricApprovalRate").innerText = summary.approval_rate_pct || "0.0%";
  document.getElementById("metricApprovalSub").innerText = `${summary.approved_count} of ${summary.eligible_count} auto-approved`;

  document.getElementById("metricAvgPd").innerText = summary.avg_default_probability_pct || "0.0%";
  document.getElementById("metricCutoffSub").innerText = `Cutoffs: ≤10% Appr, >20% Decl`;

  document.getElementById("metricExposure").innerText = formatCurrency(summary.total_exposure || 0);
  const avgExp = summary.eligible_count > 0 ? summary.total_exposure / summary.eligible_count : 0;
  document.getElementById("metricExposureSub").innerText = `Avg: ${formatCurrency(avgExp)} / loan`;

  document.getElementById("metricEl").innerText = formatCurrency(summary.total_expected_loss || 0);
  const lossRate = summary.total_exposure > 0 ? (summary.total_expected_loss / summary.total_exposure * 100) : 0;
  document.getElementById("metricElSub").innerText = `Expected Loss Rate: ${lossRate.toFixed(2)}% (LGD 60%)`;

  document.getElementById("metricIneligible").innerText = Number(summary.ineligible_count || 0).toLocaleString();

  // Render Charts
  renderPortfolioCharts(data);

  // Apply filters and render table
  applyFiltersAndSort();

  // Scroll to results top smoothly
  resultsSec.scrollIntoView({ behavior: "smooth" });
}

/* ==========================================================================
   PORTFOLIO CHARTS (Chart.js)
   ========================================================================== */
function isDarkMode() {
  return document.body.getAttribute("data-theme") === "dark";
}

function getChartThemeColors() {
  const dark = isDarkMode();
  return {
    textColor: dark ? "#D1D5DB" : "#475569",
    gridColor: dark ? "rgba(255, 255, 255, 0.08)" : "rgba(0, 0, 0, 0.06)",
    surfaceBg: dark ? "#111827" : "#FFFFFF",
  };
}

function renderPortfolioCharts(data) {
  if (typeof Chart === "undefined") {
    console.warn("Chart.js is not loaded.");
    return;
  }

  const tc = getChartThemeColors();
  const summary = data.summary;
  const eligibleApplicants = (data.applicants || []).filter(a => a.decision !== "INELIGIBLE");

  // 1. DONUT CHART: Decision Breakdown
  const ctxDonut = document.getElementById("decisionDonutChart");
  if (ctxDonut) {
    if (decisionDonutChart) decisionDonutChart.destroy();

    const counts = [
      summary.approved_count || 0,
      summary.review_count || 0,
      summary.declined_count || 0,
      summary.ineligible_count || 0,
    ];

    decisionDonutChart = new Chart(ctxDonut, {
      type: "doughnut",
      data: {
        labels: ["Approve", "Review", "Decline", "Ineligible"],
        datasets: [{
          data: counts,
          backgroundColor: [COLORS.approve, COLORS.review, COLORS.decline, COLORS.ineligible],
          borderWidth: 2,
          borderColor: tc.surfaceBg,
          hoverOffset: 6,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "bottom",
            labels: { color: tc.textColor, font: { family: "Inter", size: 12, weight: 600 } }
          },
          tooltip: {
            callbacks: {
              label: (ctx) => {
                const total = counts.reduce((a, b) => a + b, 0);
                const val = ctx.raw;
                const pct = total > 0 ? (val / total * 100).toFixed(1) : 0;
                return ` ${ctx.label}: ${val} (${pct}%)`;
              }
            }
          }
        },
        cutout: "65%",
      }
    });
  }

  // 2. PD HISTOGRAM: Frequency across PD ranges with shaded zones
  const ctxPd = document.getElementById("pdHistogramChart");
  if (ctxPd) {
    if (pdHistogramChart) pdHistogramChart.destroy();

    const bins = [
      { label: "0-5%", min: 0.00, max: 0.05, count: 0, color: "rgba(16, 185, 129, 0.85)" },
      { label: "5-10%", min: 0.05, max: 0.10, count: 0, color: "rgba(16, 185, 129, 0.85)" },
      { label: "10-15%", min: 0.10, max: 0.15, count: 0, color: "rgba(245, 158, 11, 0.85)" },
      { label: "15-20%", min: 0.15, max: 0.20, count: 0, color: "rgba(245, 158, 11, 0.85)" },
      { label: "20-25%", min: 0.20, max: 0.25, count: 0, color: "rgba(239, 68, 68, 0.85)" },
      { label: "25-30%", min: 0.25, max: 0.30, count: 0, color: "rgba(239, 68, 68, 0.85)" },
      { label: ">30%", min: 0.30, max: 1.00, count: 0, color: "rgba(185, 28, 28, 0.85)" },
    ];

    eligibleApplicants.forEach(a => {
      const p = a.default_probability;
      if (p !== null && p !== undefined) {
        for (let b of bins) {
          if (p >= b.min && (p < b.max || (b.max === 1.00 && p <= 1.00))) {
            b.count++;
            break;
          }
        }
      }
    });

    pdHistogramChart = new Chart(ctxPd, {
      type: "bar",
      data: {
        labels: bins.map(b => b.label),
        datasets: [{
          label: "Applicants",
          data: bins.map(b => b.count),
          backgroundColor: bins.map(b => b.color),
          borderRadius: 4,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              afterLabel: (ctx) => {
                const idx = ctx.dataIndex;
                if (idx <= 1) return " Zone: Low Risk (Approve ≤10%)";
                if (idx <= 3) return " Zone: Medium Risk (Review 10-20%)";
                return " Zone: High Risk (Decline >20%)";
              }
            }
          }
        },
        scales: {
          x: {
            grid: { color: tc.gridColor },
            ticks: { color: tc.textColor, font: { family: "Inter", size: 11 } }
          },
          y: {
            grid: { color: tc.gridColor },
            ticks: { color: tc.textColor, font: { family: "Inter", size: 11 } }
          }
        }
      }
    });
  }

  // 3. EXPOSURE & EXPECTED LOSS PER RISK BAND BAR CHART
  const ctxExposure = document.getElementById("exposureElChart");
  if (ctxExposure) {
    if (exposureElChart) exposureElChart.destroy();

    const bandStats = {
      "Low Risk": { exposure: 0, el: 0 },
      "Medium Risk": { exposure: 0, el: 0 },
      "High Risk": { exposure: 0, el: 0 },
    };

    eligibleApplicants.forEach(a => {
      const band = a.risk_band;
      if (bandStats[band]) {
        bandStats[band].exposure += (a.loan_amnt || 0);
        bandStats[band].el += (a.expected_loss || 0);
      }
    });

    exposureElChart = new Chart(ctxExposure, {
      type: "bar",
      data: {
        labels: ["Low Risk (Approve)", "Medium Risk (Review)", "High Risk (Decline)"],
        datasets: [
          {
            label: "Loan Exposure ($)",
            data: [bandStats["Low Risk"].exposure, bandStats["Medium Risk"].exposure, bandStats["High Risk"].exposure],
            backgroundColor: "rgba(37, 99, 235, 0.8)",
            borderRadius: 4,
          },
          {
            label: "Expected Loss ($)",
            data: [bandStats["Low Risk"].el, bandStats["Medium Risk"].el, bandStats["High Risk"].el],
            backgroundColor: "rgba(239, 68, 68, 0.8)",
            borderRadius: 4,
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "top",
            labels: { color: tc.textColor, font: { family: "Inter", size: 11.5, weight: 600 } }
          },
          tooltip: {
            callbacks: {
              label: (ctx) => ` ${ctx.dataset.label}: ${formatCurrency(ctx.raw)}`
            }
          }
        },
        scales: {
          x: {
            grid: { color: tc.gridColor },
            ticks: { color: tc.textColor, font: { family: "Inter", size: 11 } }
          },
          y: {
            grid: { color: tc.gridColor },
            ticks: {
              color: tc.textColor,
              font: { family: "Inter", size: 11 },
              callback: (v) => "$" + (v >= 1000 ? (v / 1000).toFixed(0) + "k" : v)
            }
          }
        }
      }
    });
  }

  // 4. SCORECARD CREDIT SCORE DISTRIBUTION (300-850)
  const ctxScore = document.getElementById("scoreDistributionChart");
  if (ctxScore) {
    if (scoreDistributionChart) scoreDistributionChart.destroy();

    const scoreBins = [
      { label: "<620 (Subprime)", min: 300, max: 620, count: 0, color: "rgba(239, 68, 68, 0.85)" },
      { label: "620-659 (Near-Prime)", min: 620, max: 660, count: 0, color: "rgba(245, 158, 11, 0.85)" },
      { label: "660-699 (Core)", min: 660, max: 700, count: 0, color: "rgba(59, 130, 246, 0.85)" },
      { label: "700-739 (Prime)", min: 700, max: 740, count: 0, color: "rgba(16, 185, 129, 0.85)" },
      { label: "740-779 (Prime+)", min: 740, max: 780, count: 0, color: "rgba(16, 185, 129, 0.85)" },
      { label: "780-850 (Super-Prime)", min: 780, max: 851, count: 0, color: "rgba(4, 120, 87, 0.9)" },
    ];

    eligibleApplicants.forEach(a => {
      const s = a.credit_score;
      if (s !== null && s !== undefined) {
        for (let b of scoreBins) {
          if (s >= b.min && s < b.max) {
            b.count++;
            break;
          }
        }
      }
    });

    scoreDistributionChart = new Chart(ctxScore, {
      type: "bar",
      data: {
        labels: scoreBins.map(b => b.label),
        datasets: [{
          label: "Applicants",
          data: scoreBins.map(b => b.count),
          backgroundColor: scoreBins.map(b => b.color),
          borderRadius: 4,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => ` Applicants: ${ctx.raw}`
            }
          }
        },
        scales: {
          x: {
            grid: { color: tc.gridColor },
            ticks: { color: tc.textColor, font: { family: "Inter", size: 10.5 } }
          },
          y: {
            grid: { color: tc.gridColor },
            ticks: { color: tc.textColor, font: { family: "Inter", size: 11 } }
          }
        }
      }
    });
  }
}

/* ==========================================================================
   TABLE FILTERING, SORTING & PAGINATION
   ========================================================================== */
function handleTableSearch(e) {
  searchQuery = e.target.value.toLowerCase().trim();
  currentPage = 1;
  applyFiltersAndSort();
}

function setDecisionFilter(val) {
  filterDecision = val;
  document.querySelectorAll('[data-filter="decision"]').forEach(btn => {
    btn.classList.toggle("active", btn.getAttribute("data-val") === val);
  });
  currentPage = 1;
  applyFiltersAndSort();
}

function setBandFilter(val) {
  filterBand = val;
  document.querySelectorAll('[data-filter="band"]').forEach(btn => {
    btn.classList.toggle("active", btn.getAttribute("data-val") === val);
  });
  currentPage = 1;
  applyFiltersAndSort();
}

function changePageSize(e) {
  pageSize = parseInt(e.target.value, 10);
  currentPage = 1;
  applyFiltersAndSort();
}

function sortTable(column) {
  if (sortColumn === column) {
    sortDirection = sortDirection === "asc" ? "desc" : "asc";
  } else {
    sortColumn = column;
    sortDirection = "asc";
  }
  updateSortArrows();
  applyFiltersAndSort();
}

function updateSortArrows() {
  const cols = ["id", "loan_amnt", "annual_inc", "fico", "dti", "default_probability", "credit_score", "expected_loss"];
  cols.forEach(c => {
    const el = document.getElementById("sort_" + c);
    if (!el) return;
    if (c === sortColumn) {
      el.innerText = sortDirection === "asc" ? "▲" : "▼";
      el.style.opacity = "1";
    } else {
      el.innerText = "↕";
      el.style.opacity = "0.5";
    }
  });
}

function applyFiltersAndSort() {
  if (!currentScoredData || !currentScoredData.applicants) return;

  let list = [...currentScoredData.applicants];

  // 1. Search filter
  if (searchQuery) {
    list = list.filter(a => {
      const idMatch = a.id.toString().includes(searchQuery);
      const purposeMatch = (a.purpose || "").toLowerCase().includes(searchQuery);
      return idMatch || purposeMatch;
    });
  }

  // 2. Decision filter
  if (filterDecision !== "ALL") {
    list = list.filter(a => a.decision === filterDecision);
  }

  // 3. Band filter
  if (filterBand !== "ALL") {
    list = list.filter(a => a.risk_band === filterBand);
  }

  // 4. Sort
  list.sort((a, b) => {
    let va = a[sortColumn];
    let vb = b[sortColumn];

    if (va === null || va === undefined) return 1;
    if (vb === null || vb === undefined) return -1;

    if (typeof va === "string") {
      return sortDirection === "asc" ? va.localeCompare(vb) : vb.localeCompare(va);
    }
    return sortDirection === "asc" ? va - vb : vb - va;
  });

  currentFilteredApplicants = list;
  renderTableRows();
}

function renderTableRows() {
  const tbody = document.getElementById("applicantTableBody");
  if (!tbody) return;

  tbody.innerHTML = "";

  const total = currentFilteredApplicants.length;
  const startIdx = (currentPage - 1) * pageSize;
  const endIdx = Math.min(startIdx + pageSize, total);
  const pageRows = currentFilteredApplicants.slice(startIdx, endIdx);

  if (pageRows.length === 0) {
    tbody.innerHTML = `<tr><td colspan="12" style="text-align:center; padding:32px; color:var(--text-tertiary);">No applicants match the current search & filters.</td></tr>`;
    updatePaginationControls(0, 0, 0);
    return;
  }

  pageRows.forEach(app => {
    const tr = document.createElement("tr");
    tr.onclick = () => openApplicantModal(app);

    // Decision badge
    let decBadgeClass = "badge-ineligible";
    if (app.decision === "APPROVE") decBadgeClass = "badge-approve";
    else if (app.decision === "REVIEW") decBadgeClass = "badge-review";
    else if (app.decision === "DECLINE") decBadgeClass = "badge-decline";

    // Risk band display
    let bandClass = "band-none";
    let bandText = app.risk_band;
    if (app.risk_band === "Low Risk") bandClass = "band-low";
    else if (app.risk_band === "Medium Risk") bandClass = "band-med";
    else if (app.risk_band === "High Risk") bandClass = "band-high";
    else if (app.decision === "INELIGIBLE") bandText = "Not scored";

    const pdDisplay = app.default_probability !== null ? (app.default_probability * 100).toFixed(2) + "%" : "Not scored";
    const scoreDisplay = app.credit_score !== null ? app.credit_score : "-";
    const elDisplay = app.expected_loss !== null ? formatCurrency(app.expected_loss) : "-";

    tr.innerHTML = `
      <td>#${app.id}${app.imputed_labels && app.imputed_labels.length > 0 ? ` <span title="Auto-imputed fields: ${app.imputed_labels.join(', ')}" style="display:inline-block; font-size:10px; color:#2563EB; background:rgba(37,99,235,0.1); padding:1px 5px; border-radius:4px; font-weight:700; cursor:help;">⚡ ${app.imputed_labels.length}</span>` : ''}</td>
      <td style="font-weight:600; font-family:var(--font-mono);">${formatCurrency(app.loan_amnt)}</td>
      <td>${app.term}</td>
      <td style="font-family:var(--font-mono);">${formatCurrency(app.annual_inc)}</td>
      <td style="font-family:var(--font-mono); font-weight:600;">${app.fico}</td>
      <td style="font-family:var(--font-mono);">${app.dti.toFixed(1)}%</td>
      <td style="font-family:var(--font-mono); font-weight:700;">${pdDisplay}</td>
      <td style="font-family:var(--font-mono); font-weight:700;">${scoreDisplay}</td>
      <td><span class="badge-band ${bandClass}">● ${bandText}</span></td>
      <td style="font-family:var(--font-mono);">${elDisplay}</td>
      <td><span class="badge-decision ${decBadgeClass}">${app.decision}</span></td>
      <td style="text-align:right;">
        <button class="btn btn-secondary" style="padding:4px 8px; font-size:11px;" onclick="event.stopPropagation(); openApplicantModalById(${app.id})">
          View Dossier →
        </button>
      </td>
    `;
    tbody.appendChild(tr);
  });

  updatePaginationControls(startIdx + 1, endIdx, total);
}

function updatePaginationControls(start, end, total) {
  const info = document.getElementById("paginationInfo");
  if (info) {
    info.innerText = total > 0 ? `Showing ${start} to ${end} of ${total} applicants` : `0 applicants`;
  }

  const prevBtn = document.getElementById("prevPageBtn");
  const nextBtn = document.getElementById("nextPageBtn");
  const pageSpan = document.getElementById("pageNumbersSpan");

  const totalPages = Math.ceil(total / pageSize) || 1;

  if (prevBtn) prevBtn.disabled = currentPage <= 1;
  if (nextBtn) nextBtn.disabled = currentPage >= totalPages;
  if (pageSpan) pageSpan.innerText = `Page ${currentPage} of ${totalPages}`;
}

function prevPage() {
  if (currentPage > 1) {
    currentPage--;
    renderTableRows();
  }
}

function nextPage() {
  const totalPages = Math.ceil(currentFilteredApplicants.length / pageSize) || 1;
  if (currentPage < totalPages) {
    currentPage++;
    renderTableRows();
  }
}

function openApplicantModalById(id) {
  if (!currentScoredData) return;
  const app = currentScoredData.applicants.find(a => a.id === id);
  if (app) openApplicantModal(app);
}

/* ==========================================================================
   APPLICANT DETAIL DOSSIER MODAL
   ========================================================================== */
function openApplicantModal(app) {
  const modal = document.getElementById("applicantModal");
  if (!modal) return;

  // Title and basic headers
  document.getElementById("modalApplicantTitle").innerText = `Applicant #${app.id} Dossier`;
  document.getElementById("modalApplicantSub").innerText = `${app.term} · Purpose: ${formatTitle(app.purpose)}`;

  // Decision Badge
  let decBadgeClass = "badge-ineligible";
  if (app.decision === "APPROVE") decBadgeClass = "badge-approve";
  else if (app.decision === "REVIEW") decBadgeClass = "badge-review";
  else if (app.decision === "DECLINE") decBadgeClass = "badge-decline";

  document.getElementById("modalDecisionBadge").innerHTML = `<span class="badge-decision ${decBadgeClass}" style="font-size:13px; padding:5px 14px;">${app.decision}</span>`;

  // Top 4 KPIs
  document.getElementById("modalLoanAmnt").innerText = formatCurrency(app.loan_amnt);
  document.getElementById("modalPd").innerText = app.default_probability !== null ? (app.default_probability * 100).toFixed(2) + "%" : "Not scored";
  document.getElementById("modalScore").innerText = app.credit_score !== null ? app.credit_score : "-";
  document.getElementById("modalEl").innerText = app.expected_loss !== null ? formatCurrency(app.expected_loss) : "Not scored";

  // Rationale and Warning
  document.getElementById("modalRationale").innerText = app.rationale || "Automated underwriting recommendation.";
  const warnEl = document.getElementById("modalWarning");
  if (app.warning) {
    warnEl.innerText = "⚠️ " + app.warning;
    warnEl.style.display = "block";
  } else {
    warnEl.style.display = "none";
  }

  // Filled-in / Imputed attributes notice (Point 2)
  const imputedNoteEl = document.getElementById("modalImputedNote");
  const imputedFieldsTextEl = document.getElementById("modalImputedFieldsText");
  if (imputedNoteEl && imputedFieldsTextEl) {
    if (app.imputed_labels && app.imputed_labels.length > 0) {
      imputedFieldsTextEl.innerHTML = `The following <strong>${app.imputed_labels.length}</strong> attribute(s) were blank or omitted in the uploaded application and were automatically filled in using cohort imputation defaults: <strong>${app.imputed_labels.join(", ")}</strong>.`;
      imputedNoteEl.style.display = "block";
    } else {
      imputedNoteEl.style.display = "none";
    }
  }

  // Draw Semicircle Credit Score Gauge
  drawScoreGauge(app.credit_score, app.risk_band, app.decision);

  // Render Benchmark Comparison Bars
  renderBenchmarkComparison(app);

  // Render SHAP Waterfall Decomposition
  renderShapWaterfall(app);

  // Render Adverse Action Reason Codes
  renderReasonCodes(app.reason_codes);

  // Render Stated Application Attributes Grid
  renderRawAttributes(app.raw_features);

  modal.style.display = "flex";
}

function closeModal(event) {
  if (event.target.id === "applicantModal") {
    closeModalDirect();
  }
}

function closeModalDirect() {
  const modal = document.getElementById("applicantModal");
  if (modal) modal.style.display = "none";
}

/* --- Semicircle Gauge Drawing --- */
function drawScoreGauge(score, band, decision) {
  const canvas = document.getElementById("scoreGaugeCanvas");
  if (!canvas) return;

  const ctx = canvas.getContext("2d");
  const width = canvas.width;
  const height = canvas.height;

  ctx.clearRect(0, 0, width, height);

  const cx = width / 2;
  const cy = height - 20;
  const radius = 100;
  const startAngle = Math.PI;
  const endAngle = 2 * Math.PI;

  // Background arc
  ctx.beginPath();
  ctx.arc(cx, cy, radius, startAngle, endAngle, false);
  ctx.lineWidth = 18;
  ctx.strokeStyle = isDarkMode() ? "#374151" : "#E2E8F0";
  ctx.stroke();

  const scoreNumEl = document.getElementById("gaugeScoreNumber");
  const scoreLblEl = document.getElementById("gaugeScoreLabel");
  const bandBadgeEl = document.getElementById("modalBandBadge");

  if (decision === "INELIGIBLE" || score === null) {
    scoreNumEl.innerText = "N/A";
    scoreLblEl.innerText = "Policy Ineligible (60m loan)";
    bandBadgeEl.className = "badge-band band-none";
    bandBadgeEl.innerText = "Not Scored";
    return;
  }

  // Score arc (300 to 850 range -> 0 to 1 fraction)
  const scoreClamped = Math.max(300, Math.min(850, score));
  const fraction = (scoreClamped - 300) / 550;
  const currentAngle = startAngle + fraction * Math.PI;

  let gaugeColor = COLORS.approve;
  if (band === "High Risk") gaugeColor = COLORS.decline;
  else if (band === "Medium Risk") gaugeColor = COLORS.review;

  ctx.beginPath();
  ctx.arc(cx, cy, radius, startAngle, currentAngle, false);
  ctx.lineWidth = 18;
  ctx.strokeStyle = gaugeColor;
  ctx.lineCap = "round";
  ctx.stroke();

  scoreNumEl.innerText = score;
  scoreLblEl.innerText = `Scorecard Scale 300–850 (Band: ${band})`;

  let bandClass = "band-low";
  if (band === "Medium Risk") bandClass = "band-med";
  else if (band === "High Risk") bandClass = "band-high";

  bandBadgeEl.className = `badge-band ${bandClass}`;
  bandBadgeEl.innerText = `● ${band}`;
}

/* --- Benchmark Comparison Bars --- */
function renderBenchmarkComparison(app) {
  const container = document.getElementById("benchmarkComparisonList");
  if (!container) return;

  const b = (currentScoredData && currentScoredData.benchmarks) || {
    fico_avg: 692,
    dti: 17.5,
    annual_inc: 65000,
    revol_util: 53.0
  };

  const raw = app.raw_features || {};
  const appFico = app.fico || 700;
  const appDti = app.dti || 0;
  const appInc = app.annual_inc || 0;
  const appRevolUtil = parseFloat(raw.revol_util) || 0;

  const items = [
    {
      name: "Credit Bureau Score (FICO)",
      val: appFico,
      bench: b.fico_avg,
      valStr: `${appFico}`,
      benchStr: `${b.fico_avg}`,
      pct: Math.min(100, Math.max(0, (appFico - 500) / (850 - 500) * 100)),
      higherBetter: true,
    },
    {
      name: "Debt-to-Income (DTI)",
      val: appDti,
      bench: b.dti,
      valStr: `${appDti.toFixed(1)}%`,
      benchStr: `${b.dti.toFixed(1)}%`,
      pct: Math.min(100, Math.max(0, (appDti / 45) * 100)),
      higherBetter: false,
    },
    {
      name: "Stated Annual Income",
      val: appInc,
      bench: b.annual_inc,
      valStr: formatCurrency(appInc),
      benchStr: formatCurrency(b.annual_inc),
      pct: Math.min(100, Math.max(0, (appInc / 150000) * 100)),
      higherBetter: true,
    },
    {
      name: "Revolving Utilization",
      val: appRevolUtil,
      bench: b.revol_util,
      valStr: `${appRevolUtil.toFixed(1)}%`,
      benchStr: `${b.revol_util.toFixed(1)}%`,
      pct: Math.min(100, Math.max(0, (appRevolUtil / 100) * 100)),
      higherBetter: false,
    },
  ];

  let html = "";
  items.forEach(it => {
    const isFavorable = it.higherBetter ? it.val >= it.bench : it.val <= it.bench;
    const barColor = isFavorable ? COLORS.approve : (it.higherBetter ? COLORS.decline : COLORS.review);

    html += `
      <div class="benchmark-row">
        <div class="benchmark-header">
          <span class="benchmark-name">${it.name}</span>
          <span class="benchmark-vals">${it.valStr} vs <span style="color:var(--text-tertiary);">${it.benchStr}</span></span>
        </div>
        <div class="benchmark-bar-track">
          <div class="benchmark-bar-fill" style="width:${it.pct}%; background:${barColor};"></div>
        </div>
      </div>
    `;
  });

  container.innerHTML = html;
}

/* --- SHAP Waterfall Risk Decomposition --- */
function renderShapWaterfall(app) {
  const container = document.getElementById("shapWaterfallContainer");
  if (!container) return;

  if (app.decision === "INELIGIBLE" || !app.reason_codes || app.reason_codes.length === 0) {
    container.innerHTML = `<div style="font-size:12.5px; color:var(--text-tertiary); padding:16px 0; text-align:center;">No SHAP explanation: Loan was flagged ineligible before model scoring.</div>`;
    return;
  }

  const basePd = ((currentScoredData && currentScoredData.benchmarks && currentScoredData.benchmarks.avg_pd) || 0.1456) * 100;
  const applicantPd = (app.default_probability || 0) * 100;

  let html = `
    <div class="waterfall-step" style="background:var(--bg-app); border-left:3px solid var(--brand-blue);">
      <span class="waterfall-feature">Portfolio Prior Baseline (Avg PD)</span>
      <span class="waterfall-impact impact-neutral">${basePd.toFixed(2)}% Base</span>
    </div>
  `;

  app.reason_codes.forEach((rc, i) => {
    const isRiskUp = rc.direction === "Risk Driver" || rc.shap_value > 0;
    const badgeClass = isRiskUp ? "impact-up" : "impact-down";
    const sign = isRiskUp ? "+" : "-";
    const impactPercent = Math.abs(rc.shap_value * 2.5).toFixed(2); // calibrated margin conversion

    html += `
      <div class="waterfall-step">
        <span class="waterfall-feature">#${i + 1} ${rc.description || rc.feature}</span>
        <span class="waterfall-impact ${badgeClass}">${sign}${impactPercent}% PD</span>
      </div>
    `;
  });

  html += `
    <div class="waterfall-step" style="background:var(--bg-subtle); border-left:3px solid var(--text-primary); font-weight:700;">
      <span class="waterfall-feature">Final Calibrated Probability of Default (PD)</span>
      <span class="waterfall-impact" style="background:var(--bg-surface); color:var(--text-primary); border:1px solid var(--border-medium); font-size:12.5px;">
        ${applicantPd.toFixed(2)}% PD
      </span>
    </div>
  `;

  container.innerHTML = html;
}

/* --- Adverse Action Reason Codes --- */
function renderReasonCodes(codes) {
  const container = document.getElementById("modalReasonCodesList");
  if (!container) return;

  if (!codes || codes.length === 0) {
    container.innerHTML = `<div style="font-size:12.5px; color:var(--text-tertiary); padding:16px 0; text-align:center;">No adverse action codes required for this decision tier.</div>`;
    return;
  }

  let html = "";
  codes.forEach((rc, idx) => {
    const isRiskUp = rc.direction === "Risk Driver" || rc.shap_value > 0;
    const badgeStyle = isRiskUp
      ? `background:var(--color-decline-bg); color:var(--color-decline-text); border:1px solid var(--color-decline-border);`
      : `background:var(--color-approve-bg); color:var(--color-approve-text); border:1px solid var(--color-approve-border);`;
    const label = isRiskUp ? `Risk Factor (+${Math.abs(rc.shap_value).toFixed(3)})` : `Protective Factor (-${Math.abs(rc.shap_value).toFixed(3)})`;

    html += `
      <div style="background:var(--bg-surface); border:1px solid var(--border-light); border-radius:var(--radius-sm); padding:10px 14px; display:flex; justify-content:space-between; align-items:center; gap:12px;">
        <div>
          <div style="font-weight:600; font-size:12.5px; color:var(--text-primary);">
            #${idx + 1} ${rc.description}
          </div>
          <div style="font-size:11px; color:var(--text-tertiary); margin-top:2px;">
            Feature attribute: <code style="font-family:var(--font-mono);">${rc.feature}</code>
          </div>
        </div>
        <span style="font-size:11px; font-weight:700; padding:3px 8px; border-radius:var(--radius-pill); white-space:nowrap; ${badgeStyle}">
          ${label}
        </span>
      </div>
    `;
  });

  container.innerHTML = html;
}

/* --- Stated Raw Attributes Grid --- */
function renderRawAttributes(features) {
  const container = document.getElementById("modalRawFeaturesGrid");
  if (!container) return;

  if (!features || Object.keys(features).length === 0) {
    container.innerHTML = `<div style="grid-column:1/-1; color:var(--text-tertiary); text-align:center;">No raw attributes present.</div>`;
    return;
  }

  const primaryKeys = [
    "loan_amnt", "term", "emp_length", "home_ownership", "annual_inc",
    "verification_status", "purpose", "dti", "fico_range_low", "inq_last_6mths",
    "open_acc", "pub_rec", "revol_bal", "revol_util", "total_acc", "mort_acc",
    "pub_rec_bankruptcies", "bc_util", "acc_open_past_24mths", "earliest_cr_line"
  ];

  let html = "";
  primaryKeys.forEach(k => {
    if (k in features) {
      const v = features[k];
      html += `
        <div class="attr-item">
          <div class="attr-label">${k.replace(/_/g, " ")}</div>
          <div class="attr-val">${v}</div>
        </div>
      `;
    }
  });

  container.innerHTML = html;
}

/* ==========================================================================
   EXPORT & UTILITIES
   ========================================================================== */
function exportResultsCSV() {
  if (!currentScoredData || !currentScoredData.applicants) return;

  const apps = currentScoredData.applicants;
  const headers = [
    "applicant_id", "loan_amnt", "term", "annual_inc", "fico", "dti",
    "default_probability", "credit_score", "risk_band", "expected_loss", "decision"
  ];

  const rows = [headers.join(",")];
  apps.forEach(a => {
    rows.push([
      a.id,
      a.loan_amnt,
      `"${a.term}"`,
      a.annual_inc,
      a.fico,
      a.dti,
      a.default_probability !== null ? a.default_probability : "",
      a.credit_score !== null ? a.credit_score : "",
      `"${a.risk_band}"`,
      a.expected_loss !== null ? a.expected_loss : "",
      `"${a.decision}"`
    ].join(","));
  });

  const blob = new Blob([rows.join("\n")], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.setAttribute("href", url);
  link.setAttribute("download", "underwriting_scored_batch.csv");
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

function toggleTheme() {
  const current = document.body.getAttribute("data-theme") || "light";
  const next = current === "dark" ? "light" : "dark";
  document.body.setAttribute("data-theme", next);

  const icon = document.getElementById("themeIcon");
  if (icon) icon.innerText = next === "dark" ? "☀️" : "🌙";

  if (currentScoredData) {
    renderPortfolioCharts(currentScoredData);
  }
}

function formatCurrency(val) {
  const n = Number(val) || 0;
  return "$" + n.toLocaleString("en-US", { minimumFractionDigits: 0, maximumFractionDigits: 0 });
}

function formatTitle(str) {
  if (!str) return "";
  return str.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());
}

function escapeHtml(text) {
  if (!text) return "";
  const div = document.createElement("div");
  div.innerText = String(text);
  return div.innerHTML;
}

// Champion badge reflects whatever model the API actually loaded
fetch("/api/health")
  .then((r) => r.json())
  .then((h) => {
    const el = document.getElementById("championLabel");
    if (el) el.textContent = `Champion: ${h.model} (calibrated) · test AUC ${h.test_roc_auc}`;
  })
  .catch(() => {});
