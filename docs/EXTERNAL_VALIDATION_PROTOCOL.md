# External Validation Protocol

## Purpose

Define a simple, repeatable way for outside researchers, labs, or curators to
test whether the FH variant triage model is useful on data not used to build
the model.

## Preferred Validation Dataset

An independent dataset should contain FH-gene variants in at least one of:

- `LDLR`
- `APOB`
- `PCSK9`

Preferred columns or annotations:

- gene
- HGVS cDNA/protein name if available
- variant type or consequence
- existing expert/lab classification
- classification date or review stage if available
- source of label, such as ACMG/AMP, ClinGen, lab curation, functional assay,
  or later VUS resolution

Do not share patient identifiers or private health information.

## Data Formats

Supported:

- annotated VCF/VCF.GZ with VEP `CSQ`
- annotated VCF/VCF.GZ with SnpEff `ANN`
- simple INFO-key VCF annotations
- CSV with ClinVar-like or normalized columns

See `docs/INPUT_SCHEMA.md`.

## Run Steps

1. Reproduce the public model:

   ```bash
   make install
   make pipeline
   make test
   ```

2. Score external VCF data:

   ```bash
   python scripts/score_variants_vcf.py external_annotated.vcf reports/external_scored.csv
   ```

3. Or score external CSV data:

   ```bash
   python scripts/score_variants_csv.py external_variants.csv reports/external_scored.csv
   ```

4. Compare `pathogenic_bucket_score` and `triage_band` against the independent
   labels.

## Metrics To Report

For binary benign/pathogenic external labels:

- number of variants tested
- label counts
- accuracy
- balanced accuracy
- ROC-AUC if both classes are present
- precision/recall for pathogenic labels
- confusion matrix at thresholds `0.1`, `0.3`, `0.5`, `0.7`, `0.9`

For VUS/conflicting resolution datasets:

- number of VUS/conflicting variants scored
- number later resolved
- share of upgraded pathogenic/likely pathogenic variants in each triage band
- share of downgraded benign/likely benign variants in each triage band
- variants the model ranked highly that experts disagree with
- variants experts consider important that the model ranked low

For workflow usefulness:

- average expert review time per variant before triage
- average expert review time per variant after triage
- number of variants that needed immediate expert review
- reviewer comments on false alarms and misses

## Failure Analysis

Please stratify failures where possible by:

- gene
- variant class
- missense versus loss-of-function-like
- splice-region variants
- annotation source
- ancestry/frequency context
- ClinVar absent versus ClinVar present
- old versus new classifications

## Interpreting Results

Good random-split performance is not enough. The most valuable validation is
independent, time-separated, lab-separated, ancestry-diverse, or expert-curated
data. A negative result is useful if it identifies where the model should not be
used.

## Reporting Template

```markdown
### Dataset
- Source:
- Public/private:
- Number of variants:
- Genes:
- Label source:
- Annotation method:

### Results
- Accuracy:
- Balanced accuracy:
- Pathogenic recall:
- Pathogenic precision:
- Notes on high-priority band:

### Failures
- Main failure modes:
- Examples:
- Possible causes:

### Recommendation
- Not useful / research-only / promising with changes / worth deeper validation
```
