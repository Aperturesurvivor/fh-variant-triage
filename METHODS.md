# Methods

## Research Question

Can public variant-interpretation data support a transparent first-pass triage
model for familial hypercholesterolemia variants in `LDLR`, `APOB`, and
`PCSK9`?

The current model estimates whether a variant belongs in the same bucket as
ClinVar variants labeled pathogenic/likely pathogenic versus benign/likely
benign. It does not estimate a person's probability of having FH.

## Data

The first dataset is derived from NCBI ClinVar's public tab-delimited
`variant_summary.txt.gz`. The pipeline filters variants to `LDLR`, `APOB`, and
`PCSK9`, then normalizes ClinVar clinical-significance strings into binary
research labels:

- pathogenic: `Pathogenic`, `Likely pathogenic`, `Pathogenic/Likely pathogenic`
- benign: `Benign`, `Likely benign`, `Benign/Likely benign`

Uncertain, conflicting, missing, and non-classification labels are excluded from
supervised training.

## Current Features

The cautious model avoids review status and submitter count. It uses:

- gene symbol
- ClinVar variant type
- simple variant class parsed from the variant name
- parsed cDNA-region and protein-effect classes from HGVS-like names
- molecular consequence when present in the source file
- a string-derived loss-of-function-like flag
- variant-name length as a crude complexity proxy

These are intentionally weak features. The next research-grade version should
add external annotations such as gnomAD population allele frequency, CADD,
REVEL, AlphaMissense, SpliceAI, protein-domain position, and ClinGen rule
features.

## Validation

The project reports several validation settings:

- random holdout: standard hidden test set
- gene-specific within-gene holdouts
- gene holdout: train on two FH genes and test on the third
- temporal LastEvaluated holdout where available
- variant-class shift: train on non-substitution variants and test substitutions
- threshold operating points, calibration bins, Brier score, and bootstrap
  confidence intervals on the cautious random-holdout model
- ablations that remove artifact-prone features such as variant-name length and
  high-level gene identity
- a transparent hand-built rule baseline for sanity comparison

The hard splits are more important than the random split for judging whether the
model learned portable signal rather than ClinVar curation artifacts.

## Limitations

- This is not a diagnostic device.
- ClinVar labels are not a perfect ground truth.
- ClinVar is affected by ascertainment, ancestry, lab-submission, and literature
  biases.
- Current features are not yet sufficient for clinical-grade variant
  interpretation.
- Person-level FH probability requires genotype plus LDL cholesterol, age, sex,
  family history, ancestry/frequency context, treatment history, and clinical
  diagnosis criteria.

## Pipeline Integration Boundary

The VCF scorer starts after variant calling and annotation. It does not inspect
FASTQ/BAM/CRAM reads, align sequencing data, or decide whether a variant exists.
Instead, it reads annotated VCF records from upstream tools and converts
FH-gene annotations into the same feature schema used by the CSV scorer.

Supported VCF annotation paths currently include VEP `CSQ`, SnpEff `ANN`, and a
small fallback set of gene/HGVS INFO keys. Unannotated VCFs should be annotated
before triage scoring.
