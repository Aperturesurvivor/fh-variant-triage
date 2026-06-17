# Future Session Handoff

## Start Here

Working directory:

```bash
cd /Users/josiahwilson/fh-variant-triage
```

This repo contains the project code, docs, validation plan, outreach plan,
publication framing, and GitHub publishing checklist.

## Current State

- Local Git repo on branch `main`.
- No GitHub remote configured yet.
- GitHub CLI `gh` has been installed by Homebrew.
- `gh auth login` still needs to be completed from the computer.
- Latest known commits include:
  - `3ddcfda Add VCF scoring and impact estimates`
  - `93a4325 Add data collaboration notes`
  - `52a621f Add reproducibility manifest`

## Core Commands

```bash
make install
make pipeline
make test
make score-example
make score-vcf-example
```

The full pipeline downloads/reuses ClinVar, rebuilds the dataset, trains models,
scores uncertain variants, validates splits, generates reports, generates a
manifest, and audits artifacts.

## Main Files

- `README.md`: public project entry point.
- `METHODS.md`: research design and limitations.
- `MODEL_CARD.md`: intended use and misuse boundaries.
- `PEER_REVIEW_NOTES.md`: supported and unsupported claims.
- `REVIEWER_GUIDE.md`: reviewer reproduction checklist.
- `ROADMAP.md`: staged future work.
- `docs/PROJECT_BRIEF.md`: concise project explanation.
- `docs/VALIDATION_REQUEST.md`: message/request for expert reviewers.
- `docs/EXTERNAL_VALIDATION_PROTOCOL.md`: how outsiders can test it.
- `docs/OUTREACH_TARGETS.md`: who to contact and why.
- `docs/GITHUB_PUBLISHING.md`: how to push publicly.
- `docs/MANUSCRIPT_DRAFT.md`: early paper/preprint framing.

## Current Technical Scope

Inputs:

- ClinVar tab-delimited `variant_summary.txt.gz`.
- FH variant CSVs via `scripts/score_variants_csv.py`.
- Annotated VCF/VCF.GZ via `scripts/score_variants_vcf.py`.

Outputs:

- `reports/research_report.md`
- `reports/impact_estimate.md`
- `reports/unlabeled_triage_top.csv`
- `reports/run_manifest.json`
- `models/fh_cautious_random_forest.joblib`

Most generated outputs are ignored by Git; selected Markdown reports are
tracked.

## Important Scientific Boundaries

Say:

- research triage tool
- variant-prioritization model
- estimates whether a variant resembles ClinVar benign/pathogenic buckets
- post-annotation VCF scoring
- not diagnostic
- requires independent validation

Do not say:

- predicts whether a person has FH
- clinically validated
- saves lives by itself
- replaces a doctor or ACMG/ClinGen curation

## Near-Term Next Moves

1. Publish to GitHub.
2. Create first release and optional Zenodo DOI.
3. Send validation request to bioinformatics and FH-specific experts.
4. Ask for independent validation on external FH VUS/conflicting datasets.
5. Add external annotations: gnomAD, CADD, REVEL, AlphaMissense, SpliceAI,
   ClinGen rule features where feasible.
6. Update the manuscript draft only after external validation exists.
