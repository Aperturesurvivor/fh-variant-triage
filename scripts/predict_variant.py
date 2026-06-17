from __future__ import annotations

import argparse
import json
import pathlib

import joblib
import pandas as pd


MODEL = pathlib.Path("models/fh_cautious_random_forest.joblib")
FEATURES = pathlib.Path("models/fh_cautious_features.json")


def main() -> None:
    parser = argparse.ArgumentParser(description="Score a single FH-gene variant with the cautious prototype model.")
    parser.add_argument("--gene", required=True, choices=["LDLR", "APOB", "PCSK9"])
    parser.add_argument("--type", default="single nucleotide variant")
    parser.add_argument("--variant-type", default="substitution", choices=["substitution", "deletion", "duplication", "insertion", "delins", "other"])
    parser.add_argument("--molecular-consequence", default="unknown")
    parser.add_argument("--lof-like", action="store_true")
    parser.add_argument("--name-length", type=int, default=40)
    args = parser.parse_args()

    if not MODEL.exists() or not FEATURES.exists():
        raise SystemExit("Missing trained model; run scripts/train_baseline.py first")

    model = joblib.load(MODEL)
    features = json.loads(FEATURES.read_text())
    row = {
        "gene": args.gene,
        "type": args.type,
        "variant_type_simple": args.variant_type,
        "molecular_consequence": args.molecular_consequence,
        "is_lof_like": str(bool(args.lof_like)),
        "name_length": args.name_length,
    }
    x = pd.DataFrame([{key: row.get(key, "unknown") for key in features}])
    probability = float(model.predict_proba(x)[0, 1])
    label = "review as potentially pathogenic" if probability >= 0.5 else "likely lower priority"
    print(json.dumps({"pathogenic_bucket_probability": probability, "triage_label": label, "input": row}, indent=2))


if __name__ == "__main__":
    main()

