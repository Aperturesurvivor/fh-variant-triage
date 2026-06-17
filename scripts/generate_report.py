from __future__ import annotations

import json
import pathlib


PROFILE = pathlib.Path("reports/dataset_profile.json")
BASELINE = pathlib.Path("reports/baseline_metrics.json")
CURVE = pathlib.Path("reports/learning_curve.json")
VALIDATION = pathlib.Path("reports/validation_splits.json")
GENE_MODELS = pathlib.Path("reports/gene_models.json")
MODEL_ANALYSIS = pathlib.Path("reports/model_analysis.json")
UNLABELED = pathlib.Path("reports/unlabeled_triage_summary.json")
OUT = pathlib.Path("reports/research_report.md")


def load(path: pathlib.Path) -> dict:
    if not path.exists():
        raise SystemExit(f"Missing {path}; run the full pipeline first")
    return json.loads(path.read_text())


def pct(x: float | None) -> str:
    if x is None:
        return "-"
    return f"{x * 100:.1f}%"


def main() -> None:
    profile = load(PROFILE)
    baseline = load(BASELINE)
    curve = load(CURVE)
    validation = load(VALIDATION)
    gene_models = load(GENE_MODELS)
    analysis = load(MODEL_ANALYSIS)
    unlabeled = load(UNLABELED)

    cautious = next(m for m in baseline["models"] if m["name"] == "random_forest_no_review_metadata")
    best_curve = {}
    for point in curve["points"]:
        best_curve.setdefault(point["model"], []).append(point)

    lines = [
        "# FH Variant Triage Research Report",
        "",
        "Generated from the local reproducible pipeline.",
        "",
        "## Plain-English Summary",
        "",
        "This project asks whether open ClinVar data contains enough signal to build a first-pass triage model for familial hypercholesterolemia variants in `LDLR`, `APOB`, and `PCSK9`.",
        "",
        "The current model does not estimate a person's chance of having FH. It estimates whether a variant resembles ClinVar variants labeled benign/likely benign or pathogenic/likely pathogenic.",
        "",
        "## Dataset",
        "",
        f"- Total FH-gene ClinVar variants: {profile['rows_total']:,}",
        f"- Binary-labeled training candidates: {profile['rows_labeled']:,}",
        f"- Benign / likely benign: {profile['labels'].get('benign', 0):,}",
        f"- Pathogenic / likely pathogenic: {profile['labels'].get('pathogenic', 0):,}",
        f"- Labeled by gene: {profile['genes_labeled']}",
        "",
        "## Main Held-Out Result",
        "",
        f"The cautious random-forest model, excluding review status and submitter count, reached {pct(cautious['classification_report']['accuracy'])} ordinary accuracy and {pct(cautious['balanced_accuracy'])} balanced accuracy on {baseline['n_test']:,} hidden variants.",
        "",
        f"Confusion matrix [[true benign, false alarm], [missed pathogenic, true pathogenic]]: `{cautious['confusion_matrix']}`.",
        "",
        "## Learning Curve",
        "",
        "| Model | Training examples | Accuracy | Balanced accuracy | ROC-AUC |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for point in curve["points"]:
        lines.append(
            f"| {point['model']} | {point['training_examples']:,} | {pct(point['accuracy'])} | {pct(point['balanced_accuracy'])} | {point['roc_auc']:.3f} |"
        )

    lines.extend(
        [
            "",
            "## Gene-Specific Models",
            "",
            "| Gene | Rows | Accuracy | Balanced accuracy | ROC-AUC | Confusion matrix |",
            "| --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for model in gene_models["models"]:
        if model.get("skipped"):
            lines.append(f"| {model['gene']} | {model['rows']:,} | skipped | skipped | skipped | {model['reason']} |")
        else:
            lines.append(
                f"| {model['gene']} | {model['rows']:,} | {pct(model['accuracy'])} | {pct(model['balanced_accuracy'])} | {model['roc_auc']:.3f} | `{model['confusion_matrix']}` |"
            )

    lines.extend(
        [
            "",
            "## Calibration And Operating Thresholds",
            "",
            f"Brier score: `{analysis['summary_metrics']['brier_score']:.4f}`. Lower is better; 0 is perfect probability calibration.",
            "",
            "Bootstrap 95% confidence intervals on the hidden test set:",
            "",
            "| Metric | Mean | 95% CI |",
            "| --- | ---: | ---: |",
        ]
    )
    for name, row in analysis["confidence_intervals"].items():
        lines.append(f"| {name} | {pct(row['mean'])} | {pct(row['ci95_low'])} - {pct(row['ci95_high'])} |")

    lines.extend(
        [
            "",
            "Operating points show the review tradeoff. Lower thresholds catch more pathogenic variants but create more false alarms.",
            "",
            "| Threshold | Accuracy | Pathogenic recall | Pathogenic precision | False alarms | Missed pathogenic |",
            "| ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in analysis["operating_points"]:
        lines.append(
            f"| {row['threshold']:.1f} | {pct(row['accuracy'])} | {pct(row['recall_pathogenic'])} | {pct(row['precision_pathogenic'])} | {row['false_alarm_count']:,} | {row['missed_pathogenic_count']:,} |"
        )

    lines.extend(
        [
            "",
            "Top model features by random-forest importance:",
            "",
            "| Feature | Importance |",
            "| --- | ---: |",
        ]
    )
    for row in analysis["top_feature_importances"][:12]:
        lines.append(f"| `{row['feature']}` | {row['importance']:.4f} |")

    lines.extend(
        [
            "",
            "## Ablation And Rule Baselines",
            "",
            "Ablations ask whether the model survives when suspect or high-level features are removed.",
            "",
            "| Model variant | Accuracy | Balanced accuracy | ROC-AUC | Brier score |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in analysis["ablation_models"]:
        metrics = row["summary_metrics"]
        lines.append(
            f"| {row['name']} | {pct(metrics['accuracy'])} | {pct(metrics['balanced_accuracy'])} | {metrics['roc_auc']:.3f} | {metrics['brier_score']:.4f} |"
        )
    rule = analysis["rule_baseline"]
    rule_metrics = rule["summary_metrics"]
    lines.append(
        f"| {rule['name']} | {pct(rule_metrics['accuracy'])} | {pct(rule_metrics['balanced_accuracy'])} | {rule_metrics['roc_auc']:.3f} | {rule_metrics['brier_score']:.4f} |"
    )

    lines.extend(
        [
            "",
            "## Uncertain Variant Triage Output",
            "",
            f"The trained cautious model scored {unlabeled['unlabeled_rows_scored']:,} unlabeled, uncertain, conflicting, or otherwise excluded ClinVar records for research triage.",
            "",
            f"Triage band counts: `{unlabeled['triage_band_counts']}`.",
            "",
            "Top-ranked uncertain/conflicting candidates are written to `reports/unlabeled_triage_top.csv` locally after running the pipeline. The CSV is not committed because it is generated data.",
            "",
            "Top 10 generated candidates:",
            "",
            "| Rank | Gene | VariationID | Score | Current ClinVar label | Name |",
            "| ---: | --- | ---: | ---: | --- | --- |",
        ]
    )
    for i, row in enumerate(unlabeled["top_20"][:10], start=1):
        name = str(row["Name"]).replace("|", "\\|")
        if len(name) > 90:
            name = name[:87] + "..."
        lines.append(
            f"| {i} | {row['GeneSymbol']} | {row['VariationID']} | {row['pathogenic_bucket_score']:.3f} | {row['ClinicalSignificance']} | `{name}` |"
        )

    lines.extend(
        [
            "",
            "## Harder Validation Splits",
            "",
            "| Split | Test rows | Accuracy | Balanced accuracy | ROC-AUC | Interpretation |",
            "| --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for split in validation["splits"]:
        lines.append(
            f"| {split['name']} | {split['test_rows']:,} | {pct(split['accuracy'])} | {pct(split['balanced_accuracy'])} | {split['roc_auc'] if split['roc_auc'] is not None else '-'} | {split['notes']} |"
        )

    lines.extend(
        [
            "",
            "## Current Interpretation",
            "",
            "The random holdout and temporal split suggest useful signal in the open ClinVar-derived features. The gene holdout tests show limited cross-gene portability, especially when the held-out gene has a different pathogenic/benign balance or different variant mechanisms. That means the project should move toward gene-aware models and external biological annotations rather than a single generic FH classifier.",
            "",
            "The parsed HGVS/protein-effect features reduce the earlier dependence on raw variant-name length: the no-name-length and parsed-HGVS ablations remain strong. The model still relies on coarse public annotation patterns, gene identity, and ClinVar-derived labels, so high-scoring uncertain variants should be read as expert-review candidates, not reclassifications.",
            "",
            "## Next Research Steps",
            "",
            "1. Add gnomAD allele frequency features, including ancestry-stratified frequencies.",
            "2. Add external pathogenicity predictors such as CADD, REVEL, AlphaMissense, and SpliceAI where licensing/access allows.",
            "3. Add ClinGen/ACMG rule features for FH-specific interpretation.",
            "4. Report per-gene and per-variant-class performance by default.",
            "5. Treat person-level FH probability as a later model that combines variant evidence with LDL cholesterol, age, sex, family history, and clinical criteria.",
            "",
        ]
    )
    OUT.write_text("\n".join(lines))
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
