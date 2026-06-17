from __future__ import annotations

import json
import pathlib

import joblib
import pandas as pd

try:
    from train_baseline import build_features, write_status
except ModuleNotFoundError:
    from scripts.train_baseline import build_features, write_status


DATA = pathlib.Path("data/processed/fh_clinvar_variants.csv")
MODEL = pathlib.Path("models/fh_cautious_random_forest.joblib")
FEATURES = pathlib.Path("models/fh_cautious_features.json")
OUT_CSV = pathlib.Path("reports/unlabeled_triage_top.csv")
OUT_JSON = pathlib.Path("reports/unlabeled_triage_summary.json")


def triage_band(score: float) -> str:
    if score >= 0.8:
        return "high_priority_review"
    if score >= 0.5:
        return "moderate_priority_review"
    if score >= 0.2:
        return "watchlist"
    return "lower_priority"


def main() -> None:
    if not DATA.exists():
        raise SystemExit(f"Missing {DATA}; run scripts/build_dataset.py first")
    if not MODEL.exists() or not FEATURES.exists():
        raise SystemExit("Missing cautious model; run scripts/train_baseline.py first")

    write_status("score_unlabeled", "Scoring VUS/conflicting/unlabeled variants for research triage")
    df = pd.read_csv(DATA)
    unlabeled = df[df["label"].isna()].copy()
    if unlabeled.empty:
        raise SystemExit("No unlabeled variants available to score")

    model = joblib.load(MODEL)
    features = json.loads(FEATURES.read_text())
    x = build_features(unlabeled).drop(columns=["review_status", "number_submitters"])
    x = x[features]
    unlabeled["pathogenic_bucket_score"] = model.predict_proba(x)[:, 1]
    unlabeled["triage_band"] = unlabeled["pathogenic_bucket_score"].map(triage_band)

    keep = [
        "VariationID",
        "GeneSymbol",
        "Name",
        "Type",
        "ClinicalSignificance",
        "ReviewStatus",
        "NumberSubmitters",
        "PhenotypeList",
        "variant_type_simple",
        "is_lof_like",
        "pathogenic_bucket_score",
        "triage_band",
    ]
    ranked = unlabeled.sort_values("pathogenic_bucket_score", ascending=False)[keep]
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    ranked.head(500).to_csv(OUT_CSV, index=False)

    summary = {
        "unlabeled_rows_scored": int(len(unlabeled)),
        "top_csv": str(OUT_CSV),
        "triage_band_counts": unlabeled["triage_band"].value_counts().to_dict(),
        "clinical_significance_counts": unlabeled["ClinicalSignificance"].fillna("").value_counts().head(20).to_dict(),
        "gene_counts": unlabeled["GeneSymbol"].value_counts().to_dict(),
        "top_20": ranked.head(20).to_dict(orient="records"),
    }
    OUT_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))
    write_status("unlabeled_scoring_complete", f"Scored {len(unlabeled)} unlabeled/VUS/conflicting variants")


if __name__ == "__main__":
    main()
