# FH Variant Triage: Manuscript Draft

## Title

Public ClinVar Data Supports a Reproducible First-Pass Triage Prototype for
Familial Hypercholesterolemia Variants

## Abstract

Familial hypercholesterolemia (FH) is a genetically mediated lipid disorder
commonly associated with variants in `LDLR`, `APOB`, and `PCSK9`. This project
tests whether public ClinVar variant-interpretation data can support a
transparent research prototype for prioritizing FH-gene variants for expert
review. The pipeline downloads ClinVar, filters FH-gene variants, normalizes
clinical-significance labels into benign and pathogenic research buckets, trains
baseline and gene-specific models, scores uncertain/conflicting variants, and
generates reproducible validation reports.

The current cautious random-forest model excludes review status and submitter
count. It performs strongly on random holdout and temporal-style validation, but
whole-gene holdouts and feature ablations show important limitations. In
particular, performance drops when artifact-prone features such as variant-name
length or high-level gene identity are removed. These results support
variant-prioritization research but do not support clinical diagnosis,
variant reclassification, ethnicity-agnostic claims, or person-level FH
probability.

## Introduction

Variant interpretation remains a practical bottleneck in genetic screening for
FH. Public resources such as ClinVar provide valuable aggregate evidence, but
their labels are curated interpretations shaped by ascertainment, submitter,
publication, and ancestry biases. A useful research tool should therefore not
only report random holdout performance, but also quantify failure modes,
artifact dependence, and stress-test behavior.

## Methods

The pipeline uses ClinVar `variant_summary.txt.gz`, filtered to `LDLR`, `APOB`,
and `PCSK9`. Clinical-significance labels are normalized into two supervised
training buckets: benign/likely benign and pathogenic/likely pathogenic.
Uncertain, conflicting, missing, and non-classification records are excluded
from supervised training and later scored as triage candidates.

Models are trained on coarse public metadata and string-derived features:
gene, ClinVar type, simple variant class, molecular consequence when available,
loss-of-function-like string flags, and variant-name length. The cautious model
excludes review status and submitter count.

Validation includes random holdout, gene-specific within-gene splits, whole-gene
holdouts, temporal-style splits using `LastEvaluated`, variant-class shift,
threshold operating points, calibration bins, bootstrap confidence intervals,
feature importance, ablations, and a transparent rule baseline.

## Results

The generated report at `reports/research_report.md` is the source of record
for current numbers. As of v0.1, the cautious model reaches strong random
holdout performance, but hard splits reveal limited cross-gene portability.
Gene-specific models are more interpretable, with `PCSK9` limited by sparse
pathogenic labels. Ablations demonstrate that the model depends materially on
variant-name length and gene identity, motivating external biological
annotations as the next major step.

The pipeline also scores uncertain/conflicting ClinVar records and writes a
ranked local CSV for expert-review prioritization. These scores are triage
signals only and should not be interpreted as reclassifications.

## Discussion

The prototype shows that open ClinVar data contains usable signal for FH variant
triage research, but it also shows why random holdout performance is not enough.
The strongest immediate use is prioritizing variants for expert review and
identifying where external annotations should be added. A clinical-grade tool
would need population frequency, functional evidence, expert rule criteria,
segregation evidence, and clinical context.

## Limitations

- ClinVar labels are imperfect ground truth.
- The current feature set is coarse and artifact-prone.
- No gnomAD, CADD, REVEL, AlphaMissense, SpliceAI, functional assay, or ClinGen
  rule features are integrated yet.
- The tool does not estimate person-level disease probability.
- Ethnicity-agnostic validity has not been established.

## Reproducibility

```bash
python -m pip install -e ".[dev]"
python scripts/run_pipeline.py
python -m pytest
```

The pipeline ends with `scripts/audit_artifacts.py`, which verifies that the
expected generated artifacts exist and satisfy basic sanity checks.

