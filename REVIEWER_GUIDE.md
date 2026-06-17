# Reviewer Guide

## Fast Reproduction

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python scripts/run_pipeline.py
python -m pytest
```

`scripts/run_pipeline.py` downloads ClinVar data and regenerates all local
analysis artifacts. Raw and generated data files are intentionally ignored by
Git.

## First Files To Read

1. `reports/research_report.md` — generated quantitative report.
2. `PEER_REVIEW_NOTES.md` — supported claims, unsupported claims, and known
   concerns.
3. `MODEL_CARD.md` — intended-use boundaries.
4. `METHODS.md` — data processing and validation design.

## What To Check Critically

- Random holdout performance versus hard validation splits.
- Gene-specific performance, especially sparse `PCSK9` labels.
- Ablation table: performance drops when `name_length` and `gene` are removed.
- VUS/conflicting triage output: useful for expert-review prioritization, not
  variant reclassification.
- Absence of external biological annotations in v0.1: no gnomAD, CADD, REVEL,
  AlphaMissense, SpliceAI, or functional assay data yet.

## Expected Generated Artifacts

- `reports/dataset_profile.json`
- `reports/baseline_metrics.json`
- `reports/gene_models.json`
- `reports/model_analysis.json`
- `reports/learning_curve.json`
- `reports/validation_splits.json`
- `reports/unlabeled_triage_summary.json`
- `reports/unlabeled_triage_top.csv`
- `reports/research_report.md`
- `models/fh_cautious_random_forest.joblib`

Run `python scripts/audit_artifacts.py` to check these quickly.

