from __future__ import annotations

import gzip
import json
import pathlib
import re
from collections import Counter

import pandas as pd


RAW = pathlib.Path("data/raw/variant_summary.txt.gz")
OUT = pathlib.Path("data/processed/fh_clinvar_variants.csv")
PROFILE = pathlib.Path("reports/dataset_profile.json")
STATUS = pathlib.Path("reports/status.json")
FH_GENES = {"LDLR", "APOB", "PCSK9"}


def normalize_label(sig: str) -> str | None:
    s = (sig or "").lower()
    if "conflicting" in s or "uncertain" in s or "not provided" in s:
        return None
    if "pathogenic" in s and "benign" not in s:
        return "pathogenic"
    if "benign" in s and "pathogenic" not in s:
        return "benign"
    return None


def variant_type(name: str) -> str:
    n = (name or "").lower()
    if "delins" in n:
        return "delins"
    if "del" in n:
        return "deletion"
    if "dup" in n:
        return "duplication"
    if "ins" in n:
        return "insertion"
    if ">" in n:
        return "substitution"
    return "other"


def protein_effect_type(name: str) -> str:
    n = str(name or "")
    p_match = re.search(r"\(p\.([^)]+)\)", n)
    if not p_match:
        return "no_protein_change_listed"
    p = p_match.group(1)
    p_lower = p.lower()
    if "=" in p:
        return "synonymous"
    if "fs" in p_lower:
        return "frameshift"
    if "ter" in p_lower or "*" in p:
        return "stop_gained"
    if "delins" in p_lower:
        return "protein_delins"
    if "del" in p_lower:
        return "inframe_protein_deletion"
    if "dup" in p_lower:
        return "inframe_protein_duplication"
    if re.search(r"^[A-Z][a-z]{2}\d+[A-Z][a-z]{2}$", p):
        return "missense"
    return "other_protein_change"


def cdna_region_type(name: str) -> str:
    n = str(name or "")
    c_match = re.search(r":c\.([^ ]+)", n)
    if not c_match:
        return "no_cdna_change_listed"
    c = c_match.group(1)
    if c.startswith("*"):
        return "three_prime_utr"
    if c.startswith("-"):
        return "five_prime_utr"
    if "+" in c or "-" in c:
        return "splice_region_or_intronic"
    if "_" in c:
        return "multi_base_or_range"
    if ">" in c:
        return "single_base_substitution"
    if any(token in c for token in ["del", "dup", "ins"]):
        return "small_indel"
    return "other_cdna_change"


def is_loss_of_function(row: pd.Series) -> bool:
    fields = " ".join(
        str(row.get(col, "")).lower()
        for col in ["Name", "MolecularConsequence", "Type"]
    )
    lof_terms = [
        "frameshift",
        "fs",
        "ter",
        "stop_gained",
        "nonsense",
        "splice_acceptor",
        "splice_donor",
        "canonical splice",
        "start_lost",
    ]
    return any(term in fields for term in lof_terms)


def write_status(stage: str, message: str) -> None:
    STATUS.parent.mkdir(parents=True, exist_ok=True)
    STATUS.write_text(json.dumps({"stage": stage, "message": message}, indent=2) + "\n")


def existing_usecols(path: pathlib.Path, desired: list[str]) -> list[str]:
    with gzip.open(path, "rt") as f:
        header = f.readline().rstrip("\n").split("\t")
    return [col for col in desired if col in header]


def main() -> None:
    if not RAW.exists():
        raise SystemExit(f"Missing {RAW}; run scripts/download_clinvar.py first")

    write_status("build_dataset", "Filtering ClinVar to FH genes")
    rows = []
    desired_usecols = [
        "GeneSymbol",
        "Name",
        "Type",
        "ClinicalSignificance",
        "LastEvaluated",
        "ReviewStatus",
        "NumberSubmitters",
        "Assembly",
        "Chromosome",
        "Start",
        "Stop",
        "ReferenceAllele",
        "AlternateAllele",
        "MolecularConsequence",
        "VariationID",
        "PhenotypeList",
        "Origin",
    ]
    usecols = existing_usecols(RAW, desired_usecols)

    with gzip.open(RAW, "rt") as f:
        for chunk in pd.read_csv(f, sep="\t", usecols=usecols, chunksize=100_000, low_memory=False):
            chunk = chunk[chunk["GeneSymbol"].isin(FH_GENES)].copy()
            if chunk.empty:
                continue
            for col in desired_usecols:
                if col not in chunk.columns:
                    chunk[col] = ""
            chunk["label"] = chunk["ClinicalSignificance"].map(normalize_label)
            chunk["variant_type_simple"] = chunk["Name"].map(variant_type)
            chunk["protein_effect_type"] = chunk["Name"].map(protein_effect_type)
            chunk["cdna_region_type"] = chunk["Name"].map(cdna_region_type)
            chunk["is_lof_like"] = chunk.apply(is_loss_of_function, axis=1)
            chunk["name_length"] = chunk["Name"].fillna("").astype(str).str.len()
            rows.append(chunk)

    if not rows:
        raise SystemExit("No FH gene variants found in ClinVar summary")

    df = pd.concat(rows, ignore_index=True).drop_duplicates(subset=["VariationID"])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)

    labeled = df[df["label"].notna()].copy()
    profile = {
        "rows_total": int(len(df)),
        "rows_labeled": int(len(labeled)),
        "genes_total": dict(Counter(df["GeneSymbol"])),
        "genes_labeled": dict(Counter(labeled["GeneSymbol"])),
        "labels": dict(Counter(labeled["label"])),
        "clinical_significance_top": Counter(df["ClinicalSignificance"].fillna("")).most_common(20),
        "review_status_top": Counter(df["ReviewStatus"].fillna("")).most_common(20),
        "variant_type_simple": dict(Counter(df["variant_type_simple"])),
        "protein_effect_type": dict(Counter(df["protein_effect_type"])),
        "cdna_region_type": dict(Counter(df["cdna_region_type"])),
        "last_evaluated_nonempty": int(df["LastEvaluated"].fillna("").astype(str).str.len().gt(0).sum()),
    }
    PROFILE.parent.mkdir(parents=True, exist_ok=True)
    PROFILE.write_text(json.dumps(profile, indent=2, sort_keys=True) + "\n")
    print(json.dumps(profile, indent=2, sort_keys=True))
    print(f"Wrote {OUT}")
    print(f"Wrote {PROFILE}")
    write_status("dataset_ready", f"Built FH ClinVar dataset with {len(df)} rows and {len(labeled)} labeled rows")


if __name__ == "__main__":
    main()
