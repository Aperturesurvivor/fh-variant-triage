from __future__ import annotations

import json
import pathlib

import joblib
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
OUT = pathlib.Path("reports/gene_models.json")
MODEL_DIR = pathlib.Path("models/gene_specific")


def main() -> None:
    if not DATA.exists():
        raise SystemExit(f"Missing {DATA}; run scripts/build_dataset.py first")

    write_status("train_gene_models", "Training gene-specific models")
    df = pd.read_csv(DATA)
    df = df[df["label"].isin(["benign", "pathogenic"])].copy()

    results = []
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    for gene in sorted(df["GeneSymbol"].dropna().unique()):
        gene_df = df[df["GeneSymbol"] == gene].copy()
        if len(gene_df) < 200 or gene_df["label"].nunique() != 2:
            results.append(
                {
                    "gene": gene,
                    "skipped": True,
                    "reason": "Not enough rows or only one label class.",
                    "rows": int(len(gene_df)),
                    "label_counts": gene_df["label"].value_counts().to_dict(),
                }
            )
            continue
        train_df, test_df = train_test_split(
            gene_df,
            test_size=0.25,
            random_state=42,
            stratify=gene_df["label"],
        )
        x_train = build_features(train_df).drop(columns=["gene", "review_status", "number_submitters"])
        x_test = build_features(test_df).drop(columns=["gene", "review_status", "number_submitters"])
        y_train = (train_df["label"] == "pathogenic").astype(int).to_numpy()
        y_test = (test_df["label"] == "pathogenic").astype(int).to_numpy()

        model = Pipeline(
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
        model.fit(x_train, y_train)
        pred = model.predict(x_test)
        score = model.predict_proba(x_test)[:, 1]
        model_path = MODEL_DIR / f"{gene.lower()}_random_forest.joblib"
        joblib.dump(model, model_path)
        results.append(
            {
                "gene": gene,
                "skipped": False,
                "rows": int(len(gene_df)),
                "train_rows": int(len(train_df)),
                "test_rows": int(len(test_df)),
                "label_counts": gene_df["label"].value_counts().to_dict(),
                "accuracy": float(accuracy_score(y_test, pred)),
                "balanced_accuracy": float(balanced_accuracy_score(y_test, pred)),
                "roc_auc": float(roc_auc_score(y_test, score)),
                "confusion_matrix": confusion_matrix(y_test, pred).tolist(),
                "model_path": str(model_path),
            }
        )

    payload = {"models": results}
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2, sort_keys=True))
    write_status("gene_models_complete", f"Wrote {len(results)} gene-specific model summaries")


if __name__ == "__main__":
    main()
