# FH Variant Triage Research Report

Generated from the local reproducible pipeline.

## Plain-English Summary

This project asks whether open ClinVar data contains enough signal to build a first-pass triage model for familial hypercholesterolemia variants in `LDLR`, `APOB`, and `PCSK9`.

The current model does not estimate a person's chance of having FH. It estimates whether a variant resembles ClinVar variants labeled benign/likely benign or pathogenic/likely pathogenic.

A final run manifest is generated after this report at `reports/run_manifest.json`; it records artifact hashes, runtime details, git state, and the ClinVar source URL.

A separate planning report at `reports/impact_estimate.md` translates the current triage output into rough review-backlog and population-scale impact estimates.

## Dataset

- Total FH-gene ClinVar variants: 11,514
- Binary-labeled training candidates: 6,150
- Benign / likely benign: 3,600
- Pathogenic / likely pathogenic: 2,550
- Labeled by gene: {'APOB': 2250, 'LDLR': 3290, 'PCSK9': 610}

## Main Held-Out Result

The cautious random-forest model, excluding review status and submitter count, reached 94.9% ordinary accuracy and 95.2% balanced accuracy on 1,538 hidden variants.

Confusion matrix [[true benign, false alarm], [missed pathogenic, true pathogenic]]: `[[838, 62], [17, 621]]`.

## Learning Curve

| Model | Training examples | Accuracy | Balanced accuracy | ROC-AUC |
| --- | ---: | ---: | ---: | ---: |
| logistic_regression | 230 | 82.2% | 79.0% | 0.948 |
| random_forest | 230 | 91.7% | 92.1% | 0.977 |
| logistic_regression | 461 | 85.4% | 86.0% | 0.951 |
| random_forest | 461 | 93.9% | 93.0% | 0.977 |
| logistic_regression | 922 | 85.4% | 86.1% | 0.948 |
| random_forest | 922 | 93.4% | 93.1% | 0.976 |
| logistic_regression | 1,844 | 85.4% | 86.0% | 0.950 |
| random_forest | 1,844 | 93.5% | 92.8% | 0.978 |
| logistic_regression | 3,228 | 85.4% | 86.1% | 0.949 |
| random_forest | 3,228 | 93.8% | 92.9% | 0.979 |
| logistic_regression | 4,612 | 85.5% | 86.2% | 0.950 |
| random_forest | 4,612 | 93.0% | 92.7% | 0.981 |

## Gene-Specific Models

| Gene | Rows | Accuracy | Balanced accuracy | ROC-AUC | Confusion matrix |
| --- | ---: | ---: | ---: | ---: | --- |
| APOB | 2,250 | 94.8% | 93.7% | 0.989 | `[[475, 24], [5, 59]]` |
| LDLR | 3,290 | 93.7% | 94.0% | 0.980 | `[[241, 13], [39, 530]]` |
| PCSK9 | 610 | 95.4% | 78.3% | 0.766 | `[[143, 5], [2, 3]]` |

## Calibration And Operating Thresholds

Brier score: `0.0309`. Lower is better; 0 is perfect probability calibration.

Bootstrap 95% confidence intervals on the hidden test set:

| Metric | Mean | 95% CI |
| --- | ---: | ---: |
| accuracy | 94.9% | 93.8% - 95.9% |
| average_precision | 98.8% | 98.3% - 99.3% |
| balanced_accuracy | 95.2% | 94.1% - 96.3% |
| roc_auc | 99.3% | 98.9% - 99.5% |

Operating points show the review tradeoff. Lower thresholds catch more pathogenic variants but create more false alarms.

| Threshold | Accuracy | Pathogenic recall | Pathogenic precision | False alarms | Missed pathogenic |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0.1 | 91.2% | 99.5% | 82.8% | 132 | 3 |
| 0.2 | 92.9% | 99.4% | 85.8% | 105 | 4 |
| 0.3 | 94.0% | 98.4% | 88.5% | 82 | 10 |
| 0.4 | 94.7% | 97.3% | 90.7% | 64 | 17 |
| 0.5 | 94.9% | 97.3% | 90.9% | 62 | 17 |
| 0.6 | 96.3% | 93.1% | 97.9% | 13 | 44 |
| 0.7 | 95.8% | 91.5% | 98.2% | 11 | 54 |
| 0.8 | 95.8% | 91.2% | 98.6% | 8 | 56 |
| 0.9 | 94.7% | 88.4% | 98.8% | 7 | 74 |

Top model features by random-forest importance:

| Feature | Importance |
| --- | ---: |
| `cat__protein_effect_type_synonymous` | 0.1918 |
| `cat__gene_LDLR` | 0.1715 |
| `num__name_length` | 0.1034 |
| `cat__gene_APOB` | 0.0745 |
| `cat__type_single nucleotide variant` | 0.0699 |
| `cat__variant_type_simple_substitution` | 0.0584 |
| `cat__is_lof_like_False` | 0.0573 |
| `cat__protein_effect_type_missense` | 0.0559 |
| `cat__is_lof_like_True` | 0.0502 |
| `cat__gene_PCSK9` | 0.0322 |
| `cat__protein_effect_type_stop_gained` | 0.0197 |
| `cat__type_Deletion` | 0.0185 |

## Ablation And Rule Baselines

Ablations ask whether the model survives when suspect or high-level features are removed.

| Model variant | Accuracy | Balanced accuracy | ROC-AUC | Brier score |
| --- | ---: | ---: | ---: | ---: |
| cautious_no_review_metadata | 94.9% | 95.2% | 0.993 | 0.0309 |
| no_name_length | 96.0% | 95.6% | 0.990 | 0.0348 |
| no_gene | 93.3% | 93.5% | 0.979 | 0.0505 |
| parsed_hgvs_without_name_length | 96.0% | 95.6% | 0.990 | 0.0350 |
| coarse_gene_and_variant_class_only | 96.0% | 95.6% | 0.990 | 0.0347 |
| transparent_rule_baseline | 81.0% | 77.7% | 0.910 | 0.1202 |

## Uncertain Variant Triage Output

The trained cautious model scored 5,364 unlabeled, uncertain, conflicting, or otherwise excluded ClinVar records for research triage.

Triage band counts: `{'high_priority_review': 1269, 'lower_priority': 3121, 'moderate_priority_review': 421, 'watchlist': 553}`.

Top-ranked uncertain/conflicting candidates are written to `reports/unlabeled_triage_top.csv` locally after running the pipeline. The CSV is not committed because it is generated data.

Top 10 generated candidates:

| Rank | Gene | VariationID | Score | Current ClinVar label | Name |
| ---: | --- | ---: | ---: | --- | --- |
| 1 | LDLR | 264664 | 1.000 | no classification for the single variant | `NM_000527.5(LDLR):c.657_661del (p.Pro220fs)` |
| 2 | LDLR | 375839 | 1.000 | Uncertain significance | `NM_000527.5(LDLR):c.2402_2403del (p.Phe801fs)` |
| 3 | LDLR | 237871 | 1.000 | Conflicting classifications of pathogenicity | `NM_000527.5(LDLR):c.2551_2554del (p.Gln851fs)` |
| 4 | LDLR | 2635536 | 0.999 | Uncertain significance | `NM_000527.5(LDLR):c.2583_*4del (p.Ter861CysextTer?)` |
| 5 | LDLR | 4530599 | 0.999 | Uncertain significance | `NM_000527.5(LDLR):c.2487del (p.Lys830fs)` |
| 6 | LDLR | 440700 | 0.999 | Conflicting classifications of pathogenicity | `NM_000527.5(LDLR):c.2500del (p.Asp834fs)` |
| 7 | LDLR | 431520 | 0.998 | Uncertain significance | `NM_000527.5(LDLR):c.1009_1014del (p.Glu337_Cys338del)` |
| 8 | LDLR | 3070615 | 0.998 | Uncertain significance | `NM_000527.5(LDLR):c.2259_2264del (p.Gly754_Ala755del)` |
| 9 | LDLR | 1677867 | 0.998 | Conflicting classifications of pathogenicity | `NM_000527.5(LDLR):c.1162_1173del (p.His388_Ala391del)` |
| 10 | LDLR | 252287 | 0.998 | Uncertain significance | `NM_000527.5(LDLR):c.2322_2342del (p.Asp774_Asn780del)` |

## Harder Validation Splits

| Split | Test rows | Accuracy | Balanced accuracy | ROC-AUC | Interpretation |
| --- | ---: | ---: | ---: | ---: | --- |
| random_holdout | 1,538 | 94.9% | 95.2% | 0.9925496342737723 | Standard hidden test set, stratified by label and gene. |
| hold_out_gene_APOB | 2,250 | 81.7% | 84.2% | 0.8174455005641925 | Train on the other FH genes, then test only on APOB; this probes cross-gene generalization. |
| hold_out_gene_LDLR | 3,290 | 74.8% | 81.1% | 0.9206164672765659 | Train on the other FH genes, then test only on LDLR; this probes cross-gene generalization. |
| hold_out_gene_PCSK9 | 610 | 86.7% | 49.8% | 0.8441980585982723 | Train on the other FH genes, then test only on PCSK9; this probes cross-gene generalization. |
| temporal_last_evaluated | 1,506 | 94.8% | 93.6% | 0.9896892396413214 | Train on older ClinVar evaluations, test on newer evaluations; useful but imperfect because LastEvaluated is not discovery date. |
| train_non_substitution_test_substitution | 4,708 | 81.9% | 82.2% | 0.8634873123399092 | Train on insertions/deletions/duplications/other, then test substitutions; intentionally harsh variant-class shift. |

## Current Interpretation

The random holdout and temporal split suggest useful signal in the open ClinVar-derived features. The gene holdout tests show limited cross-gene portability, especially when the held-out gene has a different pathogenic/benign balance or different variant mechanisms. That means the project should move toward gene-aware models and external biological annotations rather than a single generic FH classifier.

The parsed HGVS/protein-effect features reduce the earlier dependence on raw variant-name length: the no-name-length and parsed-HGVS ablations remain strong. The model still relies on coarse public annotation patterns, gene identity, and ClinVar-derived labels, so high-scoring uncertain variants should be read as expert-review candidates, not reclassifications.

## Next Research Steps

1. Add gnomAD allele frequency features, including ancestry-stratified frequencies.
2. Add external pathogenicity predictors such as CADD, REVEL, AlphaMissense, and SpliceAI where licensing/access allows.
3. Add ClinGen/ACMG rule features for FH-specific interpretation.
4. Report per-gene and per-variant-class performance by default.
5. Treat person-level FH probability as a later model that combines variant evidence with LDL cholesterol, age, sex, family history, and clinical criteria.
