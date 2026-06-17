from __future__ import annotations

import json
import pathlib

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_curve,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


DATA = pathlib.Path("data/processed/fh_clinvar_variants.csv")
REPORT = pathlib.Path("reports/baseline_metrics.json")
MODEL = pathlib.Path("models/fh_baseline_random_forest.joblib")
CAUTIOUS_MODEL = pathlib.Path("models/fh_cautious_random_forest.joblib")
CAUTIOUS_FEATURES = pathlib.Path("models/fh_cautious_features.json")
STATUS = pathlib.Path("reports/status.json")


def write_status(stage: str, message: str) -> None:
    STATUS.parent.mkdir(parents=True, exist_ok=True)
    STATUS.write_text(json.dumps({"stage": stage, "message": message}, indent=2) + "\n")


def clean_number_submitters(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce").fillna(0).clip(lower=0)


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    x = pd.DataFrame()
    x["gene"] = df["GeneSymbol"].fillna("unknown")
    x["type"] = df["Type"].fillna("unknown")
    x["variant_type_simple"] = df["variant_type_simple"].fillna("unknown")
    if "MolecularConsequence" in df.columns:
        x["molecular_consequence"] = df["MolecularConsequence"].fillna("unknown")
    else:
        x["molecular_consequence"] = "unknown"
    x["review_status"] = df["ReviewStatus"].fillna("unknown")
    x["is_lof_like"] = df["is_lof_like"].astype(str)
    x["number_submitters"] = clean_number_submitters(df["NumberSubmitters"])
    x["name_length"] = pd.to_numeric(df["name_length"], errors="coerce").fillna(0)
    return x


def evaluate(name: str, model: Pipeline, x_test: pd.DataFrame, y_test: np.ndarray) -> dict:
    y_pred = model.predict(x_test)
    if hasattr(model, "predict_proba"):
        y_score = model.predict_proba(x_test)[:, 1]
    else:
        y_score = y_pred
    return {
        "name": name,
        "balanced_accuracy": float(balanced_accuracy_score(y_test, y_pred)),
        "roc_auc": float(roc_auc_score(y_test, y_score)),
        "average_precision": float(average_precision_score(y_test, y_score)),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "classification_report": classification_report(y_test, y_pred, target_names=["benign", "pathogenic"], output_dict=True),
    }


def make_preprocessor(x: pd.DataFrame) -> ColumnTransformer:
    categorical = [
        col
        for col in ["gene", "type", "variant_type_simple", "molecular_consequence", "review_status", "is_lof_like"]
        if col in x.columns
    ]
    numeric = [col for col in ["number_submitters", "name_length"] if col in x.columns]
    return ColumnTransformer(
        [
            ("cat", OneHotEncoder(handle_unknown="ignore", min_frequency=2), categorical),
            ("num", StandardScaler(), numeric),
        ]
    )


def make_models(pre: ColumnTransformer) -> dict[str, Pipeline]:
    return {
        "majority_dummy": Pipeline([("pre", pre), ("clf", DummyClassifier(strategy="most_frequent"))]),
        "logistic_regression": Pipeline(
            [
                ("pre", pre),
                ("clf", LogisticRegression(max_iter=2_000, class_weight="balanced")),
            ]
        ),
        "random_forest": Pipeline(
            [
                ("pre", pre),
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
        ),
    }


def main() -> None:
    if not DATA.exists():
        raise SystemExit(f"Missing {DATA}; run scripts/build_dataset.py first")

    write_status("train_baseline", "Training baseline models")
    df = pd.read_csv(DATA)
    df = df[df["label"].isin(["benign", "pathogenic"])].copy()
    y = (df["label"] == "pathogenic").astype(int).to_numpy()
    x = build_features(df)

    stratify = df["label"] + "_" + df["GeneSymbol"].fillna("unknown")
    usable_stratify = stratify if stratify.value_counts().min() >= 2 else df["label"]
    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.25,
        random_state=42,
        stratify=usable_stratify,
    )

    metrics = {
        "n_total_labeled": int(len(df)),
        "n_train": int(len(x_train)),
        "n_test": int(len(x_test)),
        "label_counts": df["label"].value_counts().to_dict(),
        "gene_counts": df["GeneSymbol"].value_counts().to_dict(),
        "models": [],
    }
    fitted = {}
    full_models = make_models(make_preprocessor(x_train))
    for name, model in full_models.items():
        model.fit(x_train, y_train)
        fitted[name] = model
        result = evaluate(name, model, x_test, y_test)
        result["feature_set"] = "full_metadata"
        metrics["models"].append(result)

    artifact_columns = ["review_status", "number_submitters"]
    x_train_reduced = x_train.drop(columns=artifact_columns)
    x_test_reduced = x_test.drop(columns=artifact_columns)
    reduced_models = make_models(make_preprocessor(x_train_reduced))
    for name, model in reduced_models.items():
        if name == "majority_dummy":
            continue
        model.fit(x_train_reduced, y_train)
        result = evaluate(f"{name}_no_review_metadata", model, x_test_reduced, y_test)
        result["feature_set"] = "no_review_status_or_submitter_count"
        metrics["models"].append(result)

    MODEL.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(fitted["random_forest"], MODEL)
    cautious = reduced_models["random_forest"]
    joblib.dump(cautious, CAUTIOUS_MODEL)
    CAUTIOUS_FEATURES.write_text(json.dumps(list(x_train_reduced.columns), indent=2) + "\n")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n")
    print(json.dumps(metrics, indent=2, sort_keys=True))
    print(f"Wrote {MODEL}")
    print(f"Wrote {CAUTIOUS_MODEL}")
    print(f"Wrote {REPORT}")
    write_status("training_complete", f"Trained {len(metrics['models'])} baseline runs on {len(x_train)} rows; tested on {len(x_test)} rows")


if __name__ == "__main__":
    main()
