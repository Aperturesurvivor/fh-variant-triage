from __future__ import annotations

import json
import pathlib

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    confusion_matrix,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

try:
    from train_baseline import build_features, make_preprocessor, write_status
except ModuleNotFoundError:
    from scripts.train_baseline import build_features, make_preprocessor, write_status


DATA = pathlib.Path("data/processed/fh_clinvar_variants.csv")
OUT = pathlib.Path("reports/model_analysis.json")


def make_cautious_model(x_train: pd.DataFrame) -> Pipeline:
    return Pipeline(
        [
            ("pre", make_preprocessor(x_train)),
            (
                "clf",
                RandomForestClassifier(
                    n_estimators=400,
                    random_state=42,
                    class_weight="balanced_subsample",
                    min_samples_leaf=2,
                ),
            ),
        ]
    )


def metric_row(y_true: np.ndarray, scores: np.ndarray, threshold: float) -> dict:
    pred = (scores >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, pred, labels=[0, 1]).ravel()
    return {
        "threshold": threshold,
        "accuracy": float(accuracy_score(y_true, pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, pred)),
        "precision_pathogenic": float(precision_score(y_true, pred, zero_division=0)),
        "recall_pathogenic": float(recall_score(y_true, pred, zero_division=0)),
        "false_alarm_count": int(fp),
        "missed_pathogenic_count": int(fn),
        "true_benign_count": int(tn),
        "true_pathogenic_count": int(tp),
    }


def calibration_bins(y_true: np.ndarray, scores: np.ndarray, bins: int = 10) -> list[dict]:
    edges = np.linspace(0, 1, bins + 1)
    rows = []
    for i in range(bins):
        lo = edges[i]
        hi = edges[i + 1]
        if i == bins - 1:
            mask = (scores >= lo) & (scores <= hi)
        else:
            mask = (scores >= lo) & (scores < hi)
        if not mask.any():
            continue
        rows.append(
            {
                "bin_min": float(lo),
                "bin_max": float(hi),
                "count": int(mask.sum()),
                "mean_predicted_probability": float(scores[mask].mean()),
                "observed_pathogenic_rate": float(y_true[mask].mean()),
            }
        )
    return rows


def bootstrap_ci(y_true: np.ndarray, scores: np.ndarray, threshold: float = 0.5, repeats: int = 500) -> dict:
    rng = np.random.default_rng(42)
    rows = []
    n = len(y_true)
    for _ in range(repeats):
        idx = rng.integers(0, n, size=n)
        y_b = y_true[idx]
        s_b = scores[idx]
        if len(np.unique(y_b)) < 2:
            continue
        pred_b = (s_b >= threshold).astype(int)
        rows.append(
            {
                "accuracy": accuracy_score(y_b, pred_b),
                "balanced_accuracy": balanced_accuracy_score(y_b, pred_b),
                "roc_auc": roc_auc_score(y_b, s_b),
                "average_precision": average_precision_score(y_b, s_b),
            }
        )
    out = {}
    for key in rows[0]:
        values = np.array([row[key] for row in rows])
        out[key] = {
            "mean": float(values.mean()),
            "ci95_low": float(np.quantile(values, 0.025)),
            "ci95_high": float(np.quantile(values, 0.975)),
        }
    return out


def feature_importance(model: Pipeline, top_n: int = 20) -> list[dict]:
    pre = model.named_steps["pre"]
    clf = model.named_steps["clf"]
    names = pre.get_feature_names_out()
    importances = clf.feature_importances_
    order = np.argsort(importances)[::-1][:top_n]
    return [
        {"feature": str(names[i]), "importance": float(importances[i])}
        for i in order
    ]


def main() -> None:
    if not DATA.exists():
        raise SystemExit(f"Missing {DATA}; run scripts/build_dataset.py first")

    write_status("analyze_model", "Computing calibration, thresholds, and feature importance")
    df = pd.read_csv(DATA)
    df = df[df["label"].isin(["benign", "pathogenic"])].copy()
    y = (df["label"] == "pathogenic").astype(int).to_numpy()
    x = build_features(df).drop(columns=["review_status", "number_submitters"])
    stratify = df["label"] + "_" + df["GeneSymbol"].fillna("unknown")

    x_train, x_test, y_train, y_test, train_df, test_df = train_test_split(
        x,
        y,
        df,
        test_size=0.25,
        random_state=42,
        stratify=stratify,
    )

    model = make_cautious_model(x_train)
    model.fit(x_train, y_train)
    scores = model.predict_proba(x_test)[:, 1]
    pred = (scores >= 0.5).astype(int)
    payload = {
        "model": "cautious_random_forest_no_review_metadata",
        "split": "random holdout stratified by label and gene",
        "train_rows": int(len(x_train)),
        "test_rows": int(len(x_test)),
        "test_gene_counts": test_df["GeneSymbol"].value_counts().to_dict(),
        "test_label_counts": test_df["label"].value_counts().to_dict(),
        "summary_metrics": {
            "accuracy": float(accuracy_score(y_test, pred)),
            "balanced_accuracy": float(balanced_accuracy_score(y_test, pred)),
            "roc_auc": float(roc_auc_score(y_test, scores)),
            "average_precision": float(average_precision_score(y_test, scores)),
            "brier_score": float(brier_score_loss(y_test, scores)),
        },
        "confidence_intervals": bootstrap_ci(y_test, scores),
        "calibration_bins": calibration_bins(y_test, scores),
        "operating_points": [metric_row(y_test, scores, threshold) for threshold in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]],
        "top_feature_importances": feature_importance(model),
    }
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2, sort_keys=True))
    write_status("model_analysis_complete", "Wrote calibration, threshold, and feature-importance analysis")


if __name__ == "__main__":
    main()
