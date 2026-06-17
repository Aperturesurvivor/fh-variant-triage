# Repository Map

## Public Entry Points

- `README.md`: project overview and commands.
- `MODEL_CARD.md`: intended use and misuse boundaries.
- `METHODS.md`: research design.
- `PEER_REVIEW_NOTES.md`: supported and unsupported claims.
- `REVIEWER_GUIDE.md`: reproduction and review checklist.

## Context / Coordination

- `AGENTS.md`: first-read instructions for future Codex sessions.
- `docs/FUTURE_SESSION_HANDOFF.md`: durable session handoff.
- `docs/PROJECT_BRIEF.md`: concise project explanation.
- `docs/GITHUB_PUBLISHING.md`: public publishing checklist.
- `docs/OUTREACH_TARGETS.md`: who to contact and how.
- `docs/VALIDATION_REQUEST.md`: short external validation request.
- `docs/EXTERNAL_VALIDATION_PROTOCOL.md`: concrete validation protocol.

## Code

- `scripts/run_pipeline.py`: full pipeline driver.
- `scripts/download_clinvar.py`: ClinVar download.
- `scripts/build_dataset.py`: FH ClinVar filtering and feature derivation.
- `scripts/train_baseline.py`: baseline/cautious model training.
- `scripts/score_unlabeled.py`: uncertain/conflicting ClinVar triage.
- `scripts/score_variants_csv.py`: bring-your-own CSV scoring.
- `scripts/score_variants_vcf.py`: annotated VCF scoring.
- `scripts/analyze_model.py`: calibration, thresholds, ablations.
- `scripts/validate_splits.py`: hard validation splits.
- `scripts/estimate_impact.py`: generated impact estimate.
- `scripts/generate_report.py`: generated research report.
- `scripts/generate_manifest.py`: artifact provenance manifest.
- `scripts/audit_artifacts.py`: local artifact audit.

## Examples

- `examples/example_variants.csv`
- `examples/example_annotated.vcf`

## Generated Artifacts

Most generated outputs are ignored by Git:

- `data/raw/variant_summary.txt.gz`
- `data/processed/fh_clinvar_variants.csv`
- `models/*.joblib`
- JSON reports in `reports/`
- scored example CSVs in `reports/`

Tracked generated Markdown reports:

- `reports/research_report.md`
- `reports/impact_estimate.md`
- `reports/run_summary.md`

## GitHub Collaboration

- `.github/ISSUE_TEMPLATE/validation_report.md`
- `.github/ISSUE_TEMPLATE/dataset_or_collaboration.md`
- `.github/ISSUE_TEMPLATE/scientific_concern.md`
- `.github/ISSUE_TEMPLATE/feature_request.md`
- `.github/pull_request_template.md`
