# Model Card

## Model Name

FH cautious random forest prototype.

## Intended Use

Research-only triage of variants in familial hypercholesterolemia genes
(`LDLR`, `APOB`, `PCSK9`). The model estimates whether a variant resembles
ClinVar variants labeled benign/likely benign or pathogenic/likely pathogenic.

## Not Intended For

- Diagnosing familial hypercholesterolemia.
- Estimating a person's probability of having FH.
- Replacing ACMG/ClinGen expert variant interpretation.
- Making treatment, screening, insurance, or reproductive decisions.

## Training Data

NCBI ClinVar public `variant_summary.txt.gz`, filtered to `LDLR`, `APOB`, and
`PCSK9`.

Binary labels are derived from ClinVar clinical-significance text:

- pathogenic bucket: pathogenic / likely pathogenic
- benign bucket: benign / likely benign

Uncertain, conflicting, missing, and non-classification records are excluded
from supervised training.

## Features

The cautious model excludes review status and submitter count. Current features:

- gene
- ClinVar variant type
- simple variant class parsed from the variant name
- parsed cDNA-region and protein-effect classes from HGVS-like names
- molecular consequence when available
- string-derived loss-of-function-like flag
- variant-name length

These features are intentionally limited. They do not yet include population
frequency, protein-domain context, computational pathogenicity predictors, or
FH-specific ACMG/ClinGen rule evidence.

## Current Performance Snapshot

See `reports/research_report.md` after running the pipeline. The current random
holdout is strong, while whole-gene holdouts are substantially weaker. The
whole-gene weakness is a central limitation, not an incidental detail.

The report also includes threshold operating points. For research triage, the
threshold is not a purely technical choice: lower thresholds catch more
pathogenic variants while increasing false alarms for expert review.

## Ethical And Scientific Caveats

ClinVar is a clinical-interpretation database, not a clean ground-truth cohort.
Its labels reflect literature, submitter, ancestry, ascertainment, and curation
biases. A high score should mean "prioritize for expert review," not "this
person has disease."

Person-level FH probability requires clinical context, especially LDL
cholesterol, family history, age, sex, treatment status, ancestry/frequency
context, and formal diagnostic criteria.
