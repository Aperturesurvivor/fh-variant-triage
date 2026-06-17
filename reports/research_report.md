# FH Variant Triage Research Report

Generated from the local reproducible pipeline.

## Plain-English Summary

This project asks whether open ClinVar data contains enough signal to build a first-pass triage model for familial hypercholesterolemia variants in `LDLR`, `APOB`, and `PCSK9`.

The current model does not estimate a person's chance of having FH. It estimates whether a variant resembles ClinVar variants labeled benign/likely benign or pathogenic/likely pathogenic.

## Dataset

- Total FH-gene ClinVar variants: 11,514
- Binary-labeled training candidates: 6,150
- Benign / likely benign: 3,600
- Pathogenic / likely pathogenic: 2,550
- Labeled by gene: {'APOB': 2250, 'LDLR': 3290, 'PCSK9': 610}

## Main Held-Out Result

The cautious random-forest model, excluding review status and submitter count, reached 91.8% ordinary accuracy and 91.5% balanced accuracy on 1,538 hidden variants.

Confusion matrix [[true benign, false alarm], [missed pathogenic, true pathogenic]]: `[[840, 60], [66, 572]]`.

## Learning Curve

| Model | Training examples | Accuracy | Balanced accuracy | ROC-AUC |
| --- | ---: | ---: | ---: | ---: |
| logistic_regression | 230 | 84.6% | 85.1% | 0.939 |
| random_forest | 230 | 90.6% | 90.7% | 0.964 |
| logistic_regression | 461 | 84.7% | 85.1% | 0.943 |
| random_forest | 461 | 92.5% | 91.3% | 0.966 |
| logistic_regression | 922 | 84.5% | 84.9% | 0.940 |
| random_forest | 922 | 92.1% | 91.4% | 0.966 |
| logistic_regression | 1,844 | 84.7% | 85.2% | 0.942 |
| random_forest | 1,844 | 92.1% | 91.2% | 0.966 |
| logistic_regression | 3,228 | 84.6% | 85.1% | 0.941 |
| random_forest | 3,228 | 91.6% | 91.1% | 0.967 |
| logistic_regression | 4,612 | 84.6% | 85.1% | 0.942 |
| random_forest | 4,612 | 91.7% | 91.2% | 0.970 |

## Gene-Specific Models

| Gene | Rows | Accuracy | Balanced accuracy | ROC-AUC | Confusion matrix |
| --- | ---: | ---: | ---: | ---: | --- |
| APOB | 2,250 | 81.7% | 87.6% | 0.939 | `[[399, 100], [3, 61]]` |
| LDLR | 3,290 | 91.5% | 92.5% | 0.954 | `[[242, 12], [58, 511]]` |
| PCSK9 | 610 | 94.8% | 78.0% | 0.755 | `[[142, 6], [2, 3]]` |

## Calibration And Operating Thresholds

Brier score: `0.0572`. Lower is better; 0 is perfect probability calibration.

Bootstrap 95% confidence intervals on the hidden test set:

| Metric | Mean | 95% CI |
| --- | ---: | ---: |
| accuracy | 91.8% | 90.6% - 93.2% |
| average_precision | 96.4% | 95.3% - 97.4% |
| balanced_accuracy | 91.5% | 90.2% - 93.0% |
| roc_auc | 97.4% | 96.6% - 98.0% |

Operating points show the review tradeoff. Lower thresholds catch more pathogenic variants but create more false alarms.

| Threshold | Accuracy | Pathogenic recall | Pathogenic precision | False alarms | Missed pathogenic |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0.1 | 78.3% | 99.4% | 65.8% | 329 | 4 |
| 0.2 | 81.0% | 97.8% | 69.2% | 278 | 14 |
| 0.3 | 91.0% | 91.5% | 87.3% | 85 | 54 |
| 0.4 | 91.0% | 91.1% | 87.8% | 81 | 57 |
| 0.5 | 91.8% | 89.7% | 90.5% | 60 | 66 |
| 0.6 | 93.4% | 86.7% | 97.2% | 16 | 85 |
| 0.7 | 93.3% | 86.2% | 97.3% | 15 | 88 |
| 0.8 | 93.4% | 85.9% | 97.9% | 12 | 90 |
| 0.9 | 92.7% | 84.0% | 98.2% | 10 | 102 |

Top model features by random-forest importance:

| Feature | Importance |
| --- | ---: |
| `num__name_length` | 0.2800 |
| `cat__gene_LDLR` | 0.2512 |
| `cat__gene_APOB` | 0.1259 |
| `cat__type_single nucleotide variant` | 0.0886 |
| `cat__variant_type_simple_substitution` | 0.0873 |
| `cat__gene_PCSK9` | 0.0529 |
| `cat__type_Deletion` | 0.0470 |
| `cat__variant_type_simple_deletion` | 0.0406 |
| `cat__type_Duplication` | 0.0109 |
| `cat__variant_type_simple_duplication` | 0.0081 |
| `cat__variant_type_simple_delins` | 0.0017 |
| `cat__type_Microsatellite` | 0.0017 |

## Uncertain Variant Triage Output

The trained cautious model scored 5,364 unlabeled, uncertain, conflicting, or otherwise excluded ClinVar records for research triage.

Triage band counts: `{'high_priority_review': 1155, 'lower_priority': 1094, 'moderate_priority_review': 131, 'watchlist': 2984}`.

Top-ranked uncertain/conflicting candidates are written to `reports/unlabeled_triage_top.csv` locally after running the pipeline. The CSV is not committed because it is generated data.

Top 10 generated candidates:

| Rank | Gene | VariationID | Score | Current ClinVar label | Name |
| ---: | --- | ---: | ---: | --- | --- |
| 1 | LDLR | 4069769 | 0.999 | Uncertain significance | `NM_000527.5(LDLR):c.2341_2343del (p.Glu781del)` |
| 2 | LDLR | 251097 | 0.999 | Uncertain significance | `NM_000527.5(LDLR):c.257_265del (p.Phe86_Arg88del)` |
| 3 | LDLR | 251937 | 0.999 | Uncertain significance | `NM_000527.5(LDLR):c.1618_1620del (p.Ala540del)` |
| 4 | LDLR | 3290390 | 0.999 | Uncertain significance | `NM_000527.5(LDLR):c.38_58del (p.Ala13_Ala19del)` |
| 5 | LDLR | 375839 | 0.999 | Uncertain significance | `NM_000527.5(LDLR):c.2402_2403del (p.Phe801fs)` |
| 6 | LDLR | 226373 | 0.999 | Uncertain significance | `NM_000527.5(LDLR):c.1776_1778del (p.Gly593del)` |
| 7 | LDLR | 251854 | 0.999 | Uncertain significance | `NM_000527.5(LDLR):c.1460_1462del (p.Asn487del)` |
| 8 | LDLR | 1325734 | 0.999 | Uncertain significance | `NM_000527.5:c.(2311+1_2312-1)_(2389+1_2390-1)del` |
| 9 | LDLR | 2773530 | 0.999 | Uncertain significance | `NM_000527.5(LDLR):c.2536_2538del (p.Ser846del)` |
| 10 | LDLR | 440655 | 0.999 | Uncertain significance | `NM_000527.5(LDLR):c.1658_1660del (p.Tyr553del)` |

## Harder Validation Splits

| Split | Test rows | Accuracy | Balanced accuracy | ROC-AUC | Interpretation |
| --- | ---: | ---: | ---: | ---: | --- |
| random_holdout | 1,538 | 91.8% | 91.5% | 0.9735370950888191 | Standard hidden test set, stratified by label and gene. |
| hold_out_gene_APOB | 2,250 | 62.7% | 55.8% | 0.6289630610581745 | Train on the other FH genes, then test only on APOB; this probes cross-gene generalization. |
| hold_out_gene_LDLR | 3,290 | 56.8% | 68.1% | 0.8544595896714124 | Train on the other FH genes, then test only on LDLR; this probes cross-gene generalization. |
| hold_out_gene_PCSK9 | 610 | 86.2% | 82.7% | 0.8302164039540476 | Train on the other FH genes, then test only on PCSK9; this probes cross-gene generalization. |
| temporal_last_evaluated | 1,506 | 92.6% | 88.8% | 0.9650061252041735 | Train on older ClinVar evaluations, test on newer evaluations; useful but imperfect because LastEvaluated is not discovery date. |
| train_non_substitution_test_substitution | 4,708 | 67.0% | 73.8% | 0.8306520331180313 | Train on insertions/deletions/duplications/other, then test substitutions; intentionally harsh variant-class shift. |

## Current Interpretation

The random holdout and temporal split suggest useful signal in the open ClinVar-derived features. The gene holdout tests show limited cross-gene portability, especially when the held-out gene has a different pathogenic/benign balance or different variant mechanisms. That means the project should move toward gene-aware models and external biological annotations rather than a single generic FH classifier.

The feature-importance results also show that the current model relies heavily on variant-name length and coarse variant class. Those are useful triage proxies but not sufficient biological evidence. High-scoring uncertain variants should be read as expert-review candidates, not reclassifications.

## Next Research Steps

1. Add gnomAD allele frequency features, including ancestry-stratified frequencies.
2. Add external pathogenicity predictors such as CADD, REVEL, AlphaMissense, and SpliceAI where licensing/access allows.
3. Add ClinGen/ACMG rule features for FH-specific interpretation.
4. Report per-gene and per-variant-class performance by default.
5. Treat person-level FH probability as a later model that combines variant evidence with LDL cholesterol, age, sex, family history, and clinical criteria.
