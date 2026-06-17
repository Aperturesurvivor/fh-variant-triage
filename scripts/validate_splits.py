from __future__ import annotations

import json
import pathlib

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

try:
    from train_baseline import build_features, make_preprocessor, write_status
except ModuleNotFoundError:
    from scripts.train_baseline import build_features, make_preprocessor, write_status


DATA = pathlib.Path("data/processed/fh_clinvar_variants.csv")
OUT = pathlib.Path("reports/validation_splits.json")


def make_model(x_train: pd.DataFrame) -> Pipeline:
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


def y_from(df: pd.DataFrame) -> np.ndarray:
    return (df["label"] == "pathogenic").astype(int).to_numpy()


def score_split(name: str, train_df: pd.DataFrame, test_df: pd.DataFrame, notes: str) -> dict:
    x_train = build_features(train_df).drop(columns=["review_status", "number_submitters"])
    x_test = build_features(test_df).drop(columns=["review_status", "number_submitters"])
    y_train = y_from(train_df)
    y_test = y_from(test_df)
    model = make_model(x_train)
    model.fit(x_train, y_train)
    pred = model.predict(x_test)
    score = model.predict_proba(x_test)[:, 1]
    has_two_test_classes = len(set(y_test.tolist())) == 2
    return {
        "name": name,
        "notes": notes,
        "train_rows": int(len(train_df)),
        "test_rows": int(len(test_df)),
        "train_label_counts": train_df["label"].value_counts().to_dict(),
        "test_label_counts": test_df["label"].value_counts().to_dict(),
        "accuracy": float(accuracy_score(y_test, pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_test, pred)) if has_two_test_classes else None,
        "roc_auc": float(roc_auc_score(y_test, score)) if has_two_test_classes else None,
        "confusion_matrix": confusion_matrix(y_test, pred).tolist(),
    }


def main() -> None:
    if not DATA.exists():
        raise SystemExit(f"Missing {DATA}; run scripts/build_dataset.py first")

    write_status("validate_splits", "Running harder validation splits")
    df = pd.read_csv(DATA)
    df = df[df["label"].isin(["benign", "pathogenic"])].copy()

    results = []
    train_df, test_df = train_test_split(
        df,
        test_size=0.25,
        random_state=42,
        stratify=df["label"] + "_" + df["GeneSymbol"],
    )
    results.append(score_split("random_holdout", train_df, test_df, "Standard hidden test set, stratified by label and gene."))

    for gene in sorted(df["GeneSymbol"].dropna().unique()):
        test_gene = df[df["GeneSymbol"] == gene]
        train_gene = df[df["GeneSymbol"] != gene]
        if len(test_gene) >= 100 and test_gene["label"].nunique() == 2 and train_gene["label"].nunique() == 2:
            results.append(
                score_split(
                    f"hold_out_gene_{gene}",
                    train_gene,
                    test_gene,
                    f"Train on the other FH genes, then test only on {gene}; this probes cross-gene generalization.",
                )
            )

    if "LastEvaluated" in df.columns:
        dated = df.copy()
        dated["last_evaluated_dt"] = pd.to_datetime(dated["LastEvaluated"], errors="coerce")
        dated = dated[dated["last_evaluated_dt"].notna()].sort_values("last_evaluated_dt")
        if len(dated) >= 1000:
            cutoff_idx = int(len(dated) * 0.75)
            train_time = dated.iloc[:cutoff_idx].drop(columns=["last_evaluated_dt"])
            test_time = dated.iloc[cutoff_idx:].drop(columns=["last_evaluated_dt"])
            if train_time["label"].nunique() == 2 and test_time["label"].nunique() == 2:
                results.append(
                    score_split(
                        "temporal_last_evaluated",
                        train_time,
                        test_time,
                        "Train on older ClinVar evaluations, test on newer evaluations; useful but imperfect because LastEvaluated is not discovery date.",
                    )
                )

    substitutions = df[df["variant_type_simple"] == "substitution"]
    non_substitutions = df[df["variant_type_simple"] != "substitution"]
    if len(substitutions) >= 500 and len(non_substitutions) >= 500 and non_substitutions["label"].nunique() == 2:
        results.append(
            score_split(
                "train_non_substitution_test_substitution",
                non_substitutions,
                substitutions,
                "Train on insertions/deletions/duplications/other, then test substitutions; intentionally harsh variant-class shift.",
            )
        )

    payload = {"splits": results}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2, sort_keys=True))
    write_status("validation_splits_complete", f"Wrote {len(results)} validation split results")


if __name__ == "__main__":
    main()
