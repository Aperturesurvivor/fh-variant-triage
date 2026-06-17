# FH Variant Triage Project Brief

## One-Sentence Summary

Open-source research prototype that prioritizes familial hypercholesterolemia
variants in `LDLR`, `APOB`, and `PCSK9` for expert review using public ClinVar
labels and transparent validation.

## What It Does

- Downloads public ClinVar `variant_summary.txt.gz`.
- Filters to FH genes: `LDLR`, `APOB`, `PCSK9`.
- Normalizes ClinVar labels into benign/likely benign versus
  pathogenic/likely pathogenic research buckets.
- Trains baseline and cautious models.
- Scores uncertain/conflicting/excluded FH variants into review-priority bands.
- Accepts bring-your-own CSV variant tables.
- Accepts annotated VCF files after standard variant calling and annotation.
- Generates research, impact, validation, audit, and reproducibility artifacts.

## What It Does Not Do

- It does not diagnose FH.
- It does not estimate a person's probability of having FH.
- It does not call variants from raw FASTQ/BAM/CRAM sequencing data.
- It does not replace ACMG/AMP, ClinGen, laboratory director, genetic counselor,
  lipid specialist, or clinician review.
- It is not a regulated clinical device.

## Current Best Result

The cautious random-forest model, excluding review status and submitter count,
reached about `94.9%` ordinary accuracy and `95.2%` balanced accuracy on the
random hidden ClinVar split. Harder splits are less favorable and should be read
before making any deployment claims.

Read:

- `reports/research_report.md`
- `reports/impact_estimate.md`
- `reports/validation_splits.json` after running the pipeline
- `PEER_REVIEW_NOTES.md`

## Why It Might Matter

FH is common, underdiagnosed, and treatable. Earlier identification can lead to
earlier LDL-lowering therapy and cascade screening of relatives. The tool's
near-term value is not autonomous diagnosis; it is queue prioritization:
surfacing variants that deserve expert attention sooner.

## Current Impact Framing

The current generated impact estimate says:

- `5,364` uncertain/conflicting/excluded ClinVar FH records scored.
- `1,269` landed in high-priority review.
- In a hypothetical `500`-variant uncertain FH backlog, roughly `118` would
  land in high-priority review and `158` in moderate-or-high review.
- In a US-sized population, public prevalence/diagnosis assumptions imply
  hundreds of thousands to over a million potentially undiagnosed FH cases.

These are planning numbers, not clinical-outcome claims.

## Target Users

- Bioinformaticians
- Variant scientists
- FH researchers
- Lipid clinics and registries
- Clinical genomics labs doing research or quality improvement
- ClinGen/ClinVar-oriented curators
- Open-source genomics contributors

## Current Ask To The Field

Test it. Break it. Validate it externally. Tell us where it fails.

Useful external validation data:

- independent FH variant labels
- expert ACMG/AMP or ClinGen-reviewed calls not used in training
- functional assays
- ancestry-stratified frequency annotations
- phenotype-linked cohorts with LDL-C and treatment/family history context
- clinic/lab VUS resolution outcomes
