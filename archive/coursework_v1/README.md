# Coursework v1 deliverables (superseded)

These files are kept for the record. **Do not quote their numbers.**

Their headline results (ROC-AUC 0.7488 for XGBoost, 0.7524 for the "Hybrid Neuro-GBDT"
ensemble, KS 0.36) came from an earlier 100k-row run that used Lending Club's own pricing
signals (`int_rate`, `grade`, `installment`), a different split, and no maturity filter.
They **cannot be reproduced**: on the full matured 2013-2015 cohort the champion scores
0.688 ROC-AUC without the pricing signals and 0.703 with them. See
`artifacts/model_comparison.csv` and `docs/research_paper.md` for the current numbers.

- `presentation_artifacts/terminal_step*.png` are **rendered illustrations** drawn by
  `scripts/render_terminal_screenshots.py`, not real terminal captures.
- `scripts/` holds the generators for the PDF, DOCX, presentation and cards. They
  hardcode the old numbers.
- `scripts/build_step5_artifacts.py` used to train the shipped model separately from
  `run_pipeline.py`. `run_pipeline.py` now produces every artifact itself.
