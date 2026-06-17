from __future__ import annotations

import argparse
import json
import pathlib

import joblib
import pandas as pd

try:
    from train_baseline import build_features
    from build_dataset import is_loss_of_function, variant_type
    from score_unlabeled import triage_band
except ModuleNotFoundError:
    from scripts.train_baseline import build_features
    from scripts.build_dataset import is_loss_of_function, variant_type
    from scripts.score_unlabeled import triage_band


MODEL = pathlib.Path("models/fh_cautious_random_forest.joblib")
FEATURES = pathlib.Path("models/fh_cautious_features.json")
FH_GENES = {"LDLR", "APOB", "PCSK9"}


def ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    aliases = {
        "gene": "GeneSymbol",
        "variant_name": "Name",
        "variant_type": "variant_type_simple",
        "molecular_consequence": "MolecularConsequence",
    }
    for old, new in aliases.items():
        if new not in out.columns and old in out.columns:
            out[new] = out[old]

    defaults = {
        "GeneSymbol": "unknown",
        "Name": "",
        "Type": "unknown",
        "ClinicalSignificance": "",
        "ReviewStatus": "",
        "NumberSubmitters": 0,
        "MolecularConsequence": "unknown",
        "VariationID": "",
        "PhenotypeList": "",
        "Origin": "",
    }
    for col, default in defaults.items():
        if col not in out.columns:
            out[col] = default

    if "variant_type_simple" not in out.columns:
        out["variant_type_simple"] = out["Name"].map(variant_type)
    if "is_lof_like" not in out.columns:
        out["is_lof_like"] = out.apply(is_loss_of_function, axis=1)
    if "name_length" not in out.columns:
        out["name_length"] = out["Name"].fillna("").astype(str).str.len()
    return out


def score_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    if not MODEL.exists() or not FEATURES.exists():
        raise SystemExit("Missing cautious model; run scripts/train_baseline.py or scripts/run_pipeline.py first")

    model = joblib.load(MODEL)
    features = json.loads(FEATURES.read_text())
    normalized = ensure_columns(df)
    unknown_genes = sorted(set(normalized["GeneSymbol"].dropna().astype(str)) - FH_GENES)
    if unknown_genes:
        raise SystemExit(f"Only FH genes {sorted(FH_GENES)} are supported; found unsupported genes: {unknown_genes}")

    x = build_features(normalized).drop(columns=["review_status", "number_submitters"])
    x = x[features]
    scored = normalized.copy()
    scored["pathogenic_bucket_score"] = model.predict_proba(x)[:, 1]
    scored["triage_band"] = scored["pathogenic_bucket_score"].map(triage_band)
    return scored.sort_values("pathogenic_bucket_score", ascending=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Score a CSV of FH-gene variants with the cautious prototype model.")
    parser.add_argument("input_csv", help="Input CSV with ClinVar-like columns or normalized gene/name/type columns.")
    parser.add_argument("output_csv", help="Output CSV path for ranked triage scores.")
    args = parser.parse_args()

    df = pd.read_csv(args.input_csv)
    scored = score_dataframe(df)
    output = pathlib.Path(args.output_csv)
    output.parent.mkdir(parents=True, exist_ok=True)
    scored.to_csv(output, index=False)
    print(f"Scored {len(scored)} variants -> {output}")


if __name__ == "__main__":
    main()

