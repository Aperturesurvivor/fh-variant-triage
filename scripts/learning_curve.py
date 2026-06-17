from __future__ import annotations

import json
import pathlib
import time

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

try:
    from train_baseline import build_features, write_status
except ModuleNotFoundError:
    from scripts.train_baseline import build_features, write_status


DATA = pathlib.Path("data/processed/fh_clinvar_variants.csv")
OUT = pathlib.Path("reports/learning_curve.json")


def make_pipeline(kind: str, x: pd.DataFrame) -> Pipeline:
    categorical = [
        col
        for col in ["gene", "type", "variant_type_simple", "molecular_consequence", "is_lof_like"]
        if col in x.columns
    ]
    numeric = [col for col in ["name_length"] if col in x.columns]
    pre = ColumnTransformer(
        [
            ("cat", OneHotEncoder(handle_unknown="ignore", min_frequency=2), categorical),
            ("num", StandardScaler(), numeric),
        ]
    )
    if kind == "logistic_regression":
        clf = LogisticRegression(max_iter=2_000, class_weight="balanced")
    elif kind == "random_forest":
        clf = RandomForestClassifier(
            n_estimators=250,
            random_state=42,
            class_weight="balanced_subsample",
            min_samples_leaf=2,
        )
    else:
        raise ValueError(kind)
    return Pipeline([("pre", pre), ("clf", clf)])


def main() -> None:
    if not DATA.exists():
        raise SystemExit(f"Missing {DATA}; run scripts/build_dataset.py first")

    write_status("learning_curve", "Measuring accuracy as training examples increase")
    df = pd.read_csv(DATA)
    df = df[df["label"].isin(["benign", "pathogenic"])].copy()
    y = (df["label"] == "pathogenic").astype(int).to_numpy()
    x = build_features(df).drop(columns=["review_status", "number_submitters"])

    x_train_full, x_test, y_train_full, y_test = train_test_split(
        x,
        y,
        test_size=0.25,
        random_state=42,
        stratify=df["label"],
    )

    fractions = [0.05, 0.10, 0.20, 0.40, 0.70, 1.00]
    rows = []
    rng = np.random.default_rng(42)
    for fraction in fractions:
        n = max(40, int(len(x_train_full) * fraction))
        idx = rng.choice(len(x_train_full), size=n, replace=False)
        x_train = x_train_full.iloc[idx]
        y_train = y_train_full[idx]
        for kind in ["logistic_regression", "random_forest"]:
            start = time.perf_counter()
            model = make_pipeline(kind, x_train)
            model.fit(x_train, y_train)
            seconds = time.perf_counter() - start
            pred = model.predict(x_test)
            score = model.predict_proba(x_test)[:, 1]
            rows.append(
                {
                    "model": kind,
                    "training_examples": int(n),
                    "accuracy": float(accuracy_score(y_test, pred)),
                    "balanced_accuracy": float(balanced_accuracy_score(y_test, pred)),
                    "roc_auc": float(roc_auc_score(y_test, score)),
                    "train_seconds": float(seconds),
                }
            )

    payload = {
        "test_examples": int(len(x_test)),
        "explanation": "Accuracy measured on the same held-out examples while increasing the number of training examples.",
        "points": rows,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2, sort_keys=True))
    write_status("learning_curve_complete", f"Wrote learning curve with {len(rows)} points")


if __name__ == "__main__":
    main()
