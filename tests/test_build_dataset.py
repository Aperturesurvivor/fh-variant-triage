from scripts.build_dataset import cdna_region_type, normalize_label, protein_effect_type, variant_type
from scripts.score_unlabeled import triage_band
from scripts.score_variants_csv import ensure_columns
from scripts.score_variants_vcf import parse_info, vcf_to_dataframe
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


def test_protein_effect_type_from_hgvs_like_name() -> None:
    assert protein_effect_type("NM_000527.5(LDLR):c.1292C>G (p.Ala431Gly)") == "missense"
    assert protein_effect_type("NM_000384.3(APOB):c.7734A>G (p.Lys2578=)") == "synonymous"
    assert protein_effect_type("NM_000527.5(LDLR):c.1365del (p.Gln455fs)") == "frameshift"
    assert protein_effect_type("NM_000527.5(LDLR):c.2259_2264del (p.Gly754_Ala755del)") == "inframe_protein_deletion"


def test_cdna_region_type_from_hgvs_like_name() -> None:
    assert cdna_region_type("NM_000527.5(LDLR):c.1292C>G (p.Ala431Gly)") == "single_base_substitution"
    assert cdna_region_type("NM_174936.4(PCSK9):c.207+209C>T") == "splice_region_or_intronic"
    assert cdna_region_type("NM_174936.4(PCSK9):c.*75C>T") == "three_prime_utr"
    assert cdna_region_type("NM_000527.5(LDLR):c.2259_2264del (p.Gly754_Ala755del)") == "multi_base_or_range"


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
    assert normalized.loc[0, "protein_effect_type"] == "no_protein_change_listed"
    assert normalized.loc[0, "cdna_region_type"] == "multi_base_or_range"
    assert normalized.loc[0, "name_length"] > 0


def test_parse_vcf_info_flags_and_values() -> None:
    parsed = parse_info("GENE=LDLR;Consequence=missense_variant;SOMATIC")
    assert parsed["GENE"] == "LDLR"
    assert parsed["Consequence"] == "missense_variant"
    assert parsed["SOMATIC"] is True


def test_vcf_to_dataframe_reads_vep_csq_annotations(tmp_path) -> None:
    vcf = tmp_path / "input.vcf"
    vcf.write_text(
        "\n".join(
            [
                "##fileformat=VCFv4.2",
                '##INFO=<ID=CSQ,Number=.,Type=String,Description="Format: Allele|Consequence|IMPACT|SYMBOL|Gene|Feature_type|Feature|BIOTYPE|EXON|INTRON|HGVSc|HGVSp">',
                "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO",
                "19\t11216138\t.\tC\tT\t.\tPASS\tCSQ=T|missense_variant|MODERATE|LDLR|ENSG|Transcript|NM_000527.5|protein_coding|9/18||NM_000527.5:c.1292C>T|NP_000518.1:p.Ala431Val",
                "1\t1\t.\tA\tG\t.\tPASS\tCSQ=G|missense_variant|MODERATE|NOTFH|ENSG|Transcript|NM_1|protein_coding||||",
            ]
        )
        + "\n"
    )
    df = vcf_to_dataframe(vcf)
    assert len(df) == 1
    assert df.loc[0, "GeneSymbol"] == "LDLR"
    assert df.loc[0, "MolecularConsequence"] == "missense_variant"
    assert "p.Ala431Val" in df.loc[0, "Name"]


def test_vcf_to_dataframe_reads_snpeff_ann_annotations(tmp_path) -> None:
    vcf = tmp_path / "input.vcf"
    vcf.write_text(
        "\n".join(
            [
                "##fileformat=VCFv4.2",
                '##INFO=<ID=ANN,Number=.,Type=String,Description="Functional annotations: Format: Allele|Annotation|Annotation_Impact|Gene_Name|Gene_ID|Feature_Type|Feature_ID|Transcript_BioType|Rank|HGVS.c|HGVS.p">',
                "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO",
                "1\t55039974\t.\tG\tA\t.\tPASS\tANN=A|stop_gained|HIGH|PCSK9|ENSG|transcript|NM_174936.4|protein_coding|4/12|c.654G>A|p.Trp218Ter",
            ]
        )
        + "\n"
    )
    df = vcf_to_dataframe(vcf)
    assert len(df) == 1
    assert df.loc[0, "GeneSymbol"] == "PCSK9"
    assert df.loc[0, "MolecularConsequence"] == "stop_gained"
    assert df.loc[0, "Name"] == "c.654G>A (p.Trp218Ter)"
