# Data Sources

## ClinVar

- Source: `https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt.gz`
- Use: public variant-level clinical-significance labels and metadata.
- Local raw file: `data/raw/variant_summary.txt.gz` after download.
- Git policy: raw data is not committed.

## Planned External Annotations

These are not yet integrated into the pipeline, but they are the next data
sources needed for a stronger research tool:

- gnomAD allele frequencies, including population-stratified frequencies.
- CADD scores.
- REVEL missense scores.
- AlphaMissense scores.
- SpliceAI scores for splice-relevant variants.
- ClinGen/ACMG FH-specific rule criteria and expert-panel evidence.

## Why More Data Matters

The current model can learn ClinVar label patterns. External annotations help
test whether the same variants also look suspicious by independent biological
evidence: rarity in population data, predicted protein impact, splice impact,
domain position, and expert-curated rule criteria.

## Generated Research Outputs

The pipeline generates a ranked local CSV of uncertain/conflicting ClinVar
records scored by the cautious model:

- `reports/unlabeled_triage_top.csv`
- `reports/unlabeled_triage_summary.json`

These are generated artifacts and are not committed by default.
