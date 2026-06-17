from __future__ import annotations

import json
import pathlib
import sys


REQUIRED_JSON = {
    "reports/dataset_profile.json": ["rows_total", "rows_labeled", "labels", "genes_labeled"],
    "reports/baseline_metrics.json": ["models", "n_train", "n_test"],
    "reports/gene_models.json": ["models"],
    "reports/model_analysis.json": ["summary_metrics", "ablation_models", "rule_baseline", "operating_points"],
    "reports/learning_curve.json": ["points"],
    "reports/validation_splits.json": ["splits"],
    "reports/unlabeled_triage_summary.json": ["unlabeled_rows_scored", "triage_band_counts", "top_20"],
    "reports/run_manifest.json": ["artifacts", "clinvar_source", "git", "python"],
}

REQUIRED_FILES = [
    "reports/research_report.md",
    "reports/unlabeled_triage_top.csv",
    "reports/run_manifest.json",
    "models/fh_cautious_random_forest.joblib",
    "models/fh_cautious_features.json",
]


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: pathlib.Path, keys: list[str]) -> dict:
    if not path.exists():
        fail(f"missing {path}")
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")
    for key in keys:
        if key not in data:
            fail(f"{path} missing key {key!r}")
    return data


def main() -> None:
    for file_name in REQUIRED_FILES:
        path = pathlib.Path(file_name)
        if not path.exists():
            fail(f"missing {path}")
        if path.stat().st_size == 0:
            fail(f"empty {path}")

    loaded = {
        file_name: load_json(pathlib.Path(file_name), keys)
        for file_name, keys in REQUIRED_JSON.items()
    }

    profile = loaded["reports/dataset_profile.json"]
    if profile["rows_labeled"] < 1_000:
        fail("too few labeled variants for current expected FH ClinVar dataset")
    if set(profile["genes_labeled"]) != {"APOB", "LDLR", "PCSK9"}:
        fail("expected labeled variants for APOB, LDLR, and PCSK9")

    baseline = loaded["reports/baseline_metrics.json"]
    model_names = {row["name"] for row in baseline["models"]}
    if "random_forest_no_review_metadata" not in model_names:
        fail("missing cautious random-forest baseline")

    analysis = loaded["reports/model_analysis.json"]
    if analysis["summary_metrics"]["balanced_accuracy"] < 0.75:
        fail("cautious model balanced accuracy unexpectedly low")
    ablation_names = {row["name"] for row in analysis["ablation_models"]}
    for expected in ["no_name_length", "no_gene", "parsed_hgvs_without_name_length", "coarse_gene_and_variant_class_only"]:
        if expected not in ablation_names:
            fail(f"missing ablation {expected}")

    validation = loaded["reports/validation_splits.json"]
    split_names = {row["name"] for row in validation["splits"]}
    for expected in ["random_holdout", "temporal_last_evaluated", "hold_out_gene_LDLR"]:
        if expected not in split_names:
            fail(f"missing validation split {expected}")

    unlabeled = loaded["reports/unlabeled_triage_summary.json"]
    if unlabeled["unlabeled_rows_scored"] < 1_000:
        fail("too few uncertain/conflicting variants scored")
    if not unlabeled["top_20"]:
        fail("missing top uncertain-variant candidates")

    manifest = loaded["reports/run_manifest.json"]
    manifest_paths = {row["path"]: row for row in manifest["artifacts"]}
    for expected in REQUIRED_FILES:
        if expected == "reports/run_manifest.json":
            continue
        if expected not in manifest_paths:
            fail(f"run manifest missing artifact record for {expected}")
        if not manifest_paths[expected].get("exists"):
            fail(f"run manifest says required artifact is missing: {expected}")
    raw = manifest_paths.get("data/raw/variant_summary.txt.gz", {})
    if raw.get("bytes", 0) < 1_000_000:
        fail("ClinVar raw artifact record is unexpectedly small or missing")

    report = pathlib.Path("reports/research_report.md").read_text()
    for heading in [
        "## Main Held-Out Result",
        "## Calibration And Operating Thresholds",
        "## Ablation And Rule Baselines",
        "## Uncertain Variant Triage Output",
        "## Harder Validation Splits",
    ]:
        if heading not in report:
            fail(f"research report missing heading {heading}")

    print("Artifact audit passed.")


if __name__ == "__main__":
    main()
