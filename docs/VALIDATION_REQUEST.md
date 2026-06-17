# Validation Request

## Short Version

I am an independent developer building an open-source research prototype for
familial hypercholesterolemia variant triage. It is not intended for diagnosis
or clinical decision-making. It trains on public ClinVar FH-gene variants and
can score annotated VCF or CSV variant records for `LDLR`, `APOB`, and `PCSK9`.

I am looking for expert criticism and independent validation, especially against
FH variants of uncertain significance, conflicting variants, ClinGen/ACMG
classifications, functional assay data, or de-identified lab/registry datasets.

If it is not useful, I would like to know why. If it is useful, I would like to
improve it in the direction the field actually needs.

## What The Tool Does

- Prioritizes FH-gene variants for expert review.
- Scores variants by resemblance to ClinVar benign/likely benign versus
  pathogenic/likely pathogenic buckets.
- Supports public ClinVar reproduction, bring-your-own CSV scoring, and
  annotated VCF scoring after standard variant calling and annotation.
- Generates validation splits, calibration summaries, ablations, an impact
  estimate, and a run manifest.

## What The Tool Does Not Do

- It does not diagnose FH.
- It does not classify variants under ACMG/AMP rules.
- It does not estimate person-level disease probability.
- It does not replace a clinical laboratory, clinician, genetic counselor, or
  ClinGen/ACMG review.

## What I Am Asking Reviewers To Test

1. Does the pipeline run reproducibly?
2. Are the claims and limitations accurate?
3. Does the model rank known/pathogenic FH variants near the top in independent
   data?
4. Does it behave reasonably on VUS/conflicting variants?
5. Where does it fail by gene, variant class, ancestry context, annotation
   source, or clinical setting?
6. Does the VCF interface fit real sequencing/annotation workflows?
7. What data or validation would make it genuinely useful?

## Useful Validation Inputs

- Annotated VCF or CSV variant tables for `LDLR`, `APOB`, and `PCSK9`.
- Independent expert classifications.
- ClinGen/ACMG-reviewed variant labels not used during model training.
- Functional assay outcomes.
- VUS resolution history.
- Ancestry-stratified frequency annotations.
- De-identified phenotype-linked cohorts if legally and ethically shareable.

Please do not share private health information in GitHub issues.

## Suggested Minimal Validation Run

```bash
git clone <repo-url>
cd fh-variant-triage
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python scripts/run_pipeline.py
python -m pytest
python scripts/score_variants_vcf.py your_annotated.vcf reports/your_scored_variants.csv
```

Or for CSV:

```bash
python scripts/score_variants_csv.py your_variants.csv reports/your_scored_variants.csv
```

## Best Feedback Format

- GitHub issue for scientific concerns, data-source suggestions, or validation
  results.
- Pull request for code, docs, parser, or benchmark improvements.
- Private email only if the validation involves data that cannot be discussed
  publicly.

## Authorship / Credit

External validators and domain experts who contribute substantial review,
benchmarking, data access, or scientific design should be credited in project
docs and considered for collaboration on any future preprint or manuscript.
