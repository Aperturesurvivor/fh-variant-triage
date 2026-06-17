from scripts.build_dataset import normalize_label, variant_type
from scripts.score_unlabeled import triage_band
from scripts.score_variants_csv import ensure_columns
import pandas as pd


def test_normalize_label_pathogenic_family() -> None:
    assert normalize_label("Pathogenic") == "pathogenic"
    assert normalize_label("Likely pathogenic") == "pathogenic"
    assert normalize_label("Pathogenic/Likely pathogenic") == "pathogenic"


def test_normalize_label_benign_family() -> None:
    assert normalize_label("Benign") == "benign"
    assert normalize_label("Likely benign") == "benign"
    assert normalize_label("Benign/Likely benign") == "benign"


def test_normalize_label_excludes_uncertain_and_conflicting() -> None:
    assert normalize_label("Uncertain significance") is None
    assert normalize_label("Conflicting classifications of pathogenicity") is None
    assert normalize_label("not provided") is None


def test_variant_type_simple_from_hgvs_like_name() -> None:
    assert variant_type("NM_000527.5(LDLR):c.1A>G") == "substitution"
    assert variant_type("LDLR:c.1_3del") == "deletion"
    assert variant_type("LDLR:c.1_3dup") == "duplication"
    assert variant_type("LDLR:c.1_2delinsAA") == "delins"


def test_triage_band_thresholds() -> None:
    assert triage_band(0.81) == "high_priority_review"
    assert triage_band(0.5) == "moderate_priority_review"
    assert triage_band(0.2) == "watchlist"
    assert triage_band(0.19) == "lower_priority"


def test_score_csv_column_normalization() -> None:
    df = pd.DataFrame([{"gene": "LDLR", "variant_name": "LDLR:c.1_3del", "Type": "Deletion"}])
    normalized = ensure_columns(df)
    assert normalized.loc[0, "GeneSymbol"] == "LDLR"
    assert normalized.loc[0, "variant_type_simple"] == "deletion"
    assert normalized.loc[0, "name_length"] > 0
