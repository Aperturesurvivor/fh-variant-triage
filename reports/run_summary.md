# FH Variant Triage Run Summary

Generated: 2026-06-17

## Current Dataset

Source: ClinVar `variant_summary.txt.gz`, filtered to `LDLR`, `APOB`, and
`PCSK9`.

- Total FH-gene variants: 11,514
- Binary-labeled variants usable for first training pass: 6,150
- Labels:
  - Benign / likely benign: 3,600
  - Pathogenic / likely pathogenic: 2,550
- Labeled variants by gene:
  - LDLR: 3,290
  - APOB: 2,250
  - PCSK9: 610
- Held-out test split: 1,538 variants

This is enough for a first supervised train/test split, but not enough to trust
fine-grained subgroup behavior without more validation.

## Baseline Results

The first models use coarse ClinVar-derived features: gene, variant type,
loss-of-function-like string flags, name length, review status, and submitter
count. A second pass removes review status and submitter count to reduce obvious
curation-artifact leakage.

| Model | Feature Set | Balanced Accuracy | ROC-AUC | Avg Precision | Confusion Matrix |
| --- | --- | ---: | ---: | ---: | --- |
| Majority dummy | full metadata | 0.500 | 0.500 | 0.415 | [[900, 0], [638, 0]] |
| Logistic regression | full metadata | 0.868 | 0.941 | 0.928 | [[736, 164], [52, 586]] |
| Random forest | full metadata | 0.937 | 0.977 | 0.969 | [[858, 42], [51, 587]] |
| Logistic regression | no review metadata | 0.863 | 0.947 | 0.939 | [[739, 161], [61, 577]] |
| Random forest | no review metadata | 0.915 | 0.974 | 0.964 | [[840, 60], [66, 572]] |

## Interpretation

The dataset is large enough for a real first model. The high scores are
encouraging but should be treated as provisional, because ClinVar labels and
variant annotations can contain curation artifacts and duplicated knowledge
patterns. The reduced-feature run suggests the model is not relying only on
review status or submitter count, but it may still exploit label-correlated
structure in variant naming and variant type.

## Next Validation Steps

1. Add external annotations:
   - gnomAD allele frequency, ideally overall and ancestry-specific frequencies.
   - CADD, REVEL, AlphaMissense, and SpliceAI where available.
   - LDLR protein/domain position features.
2. Add harder splits:
   - Train on older ClinVar entries, test on newer entries if dates are usable.
   - Train on two FH genes, test on the third as a stress test.
   - For LDLR, hold out protein domains or variant classes.
3. Compare against existing predictors:
   - CADD
   - REVEL
   - AlphaMissense
   - SpliceAI for splice-relevant variants
   - FH-specific published tools such as MLb-LDLr / OptiMo-LDLr if scores or
     reproducible implementations are accessible.
4. Examine ancestry robustness:
   - ClinVar summary itself does not provide ethnicity labels.
   - Use gnomAD population allele frequencies as a proxy for whether variants
     are common/rare across continental-ancestry reference groups.
   - Report performance and uncertainty by gene, variant class, and frequency
     bins before making any ethnicity-agnostic claim.

