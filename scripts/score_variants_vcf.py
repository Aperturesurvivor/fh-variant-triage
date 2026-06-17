from __future__ import annotations

import argparse
import gzip
import pathlib
import re
from collections.abc import Iterable

import pandas as pd

try:
    from score_variants_csv import FH_GENES, score_dataframe
except ModuleNotFoundError:
    from scripts.score_variants_csv import FH_GENES, score_dataframe


DEFAULT_OUTPUT_COLUMNS = [
    "GeneSymbol",
    "Name",
    "Type",
    "MolecularConsequence",
    "VariationID",
    "Chromosome",
    "Start",
    "ReferenceAllele",
    "AlternateAllele",
]


def open_text(path: pathlib.Path):
    if path.suffix == ".gz":
        return gzip.open(path, "rt")
    return path.open("rt")


def parse_info(info_text: str) -> dict[str, str | bool]:
    info: dict[str, str | bool] = {}
    if not info_text or info_text == ".":
        return info
    for item in info_text.split(";"):
        if not item:
            continue
        if "=" not in item:
            info[item] = True
            continue
        key, value = item.split("=", 1)
        info[key] = value
    return info


def parse_format_fields(description: str) -> list[str]:
    match = re.search(r"Format: ([^\">]+)", description)
    if not match:
        return []
    return [field.strip() for field in match.group(1).split("|")]


def parse_info_header(line: str) -> tuple[str, list[str]] | None:
    match = re.match(r"##INFO=<ID=([^,>]+),.*Description=\"(.*)\">$", line)
    if not match:
        return None
    info_id, description = match.groups()
    if info_id not in {"ANN", "CSQ"}:
        return None
    return info_id, parse_format_fields(description)


def consequence_to_type(ref: str, alt: str) -> str:
    if len(ref) == 1 and len(alt) == 1:
        return "single nucleotide variant"
    if len(ref) > len(alt):
        return "Deletion"
    if len(ref) < len(alt):
        return "Insertion"
    return "complex sequence alteration"


def first_present(row: dict[str, str], names: Iterable[str]) -> str:
    for name in names:
        value = row.get(name, "")
        if value:
            return value
    return ""


def annotation_rows(
    info: dict[str, str | bool],
    annotation_fields: dict[str, list[str]],
    chrom: str,
    pos: str,
    record_id: str,
    ref: str,
    alts: list[str],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for key in ("CSQ", "ANN"):
        value = info.get(key)
        fields = annotation_fields.get(key, [])
        if not isinstance(value, str) or not fields:
            continue
        for annotation in value.split(","):
            parts = annotation.split("|")
            parsed = dict(zip(fields, parts, strict=False))
            alt = first_present(parsed, ["Allele"]).strip() or alts[0]
            gene = first_present(parsed, ["SYMBOL", "Gene_Name", "Gene"]).strip()
            if gene not in FH_GENES:
                continue
            consequence = first_present(parsed, ["Consequence", "Annotation"]).strip()
            hgvsc = first_present(parsed, ["HGVSc", "HGVS.c"]).strip()
            hgvsp = first_present(parsed, ["HGVSp", "HGVS.p"]).strip()
            name = hgvsc or f"{chrom}:{pos}{ref}>{alt}"
            if hgvsp:
                name = f"{name} ({hgvsp.split(':')[-1]})"
            rows.append(
                {
                    "GeneSymbol": gene,
                    "Name": name,
                    "Type": consequence_to_type(ref, alt),
                    "MolecularConsequence": consequence,
                    "VariationID": "" if record_id == "." else record_id,
                    "Chromosome": chrom,
                    "Start": pos,
                    "ReferenceAllele": ref,
                    "AlternateAllele": alt,
                }
            )
    return rows


def fallback_row(
    info: dict[str, str | bool],
    chrom: str,
    pos: str,
    record_id: str,
    ref: str,
    alt: str,
) -> dict[str, str] | None:
    gene = str(
        info.get("GeneSymbol")
        or info.get("GENE")
        or info.get("Gene")
        or info.get("SYMBOL")
        or ""
    ).strip()
    if gene not in FH_GENES:
        return None
    name = str(info.get("HGVS") or info.get("HGVSc") or info.get("Name") or f"{chrom}:{pos}{ref}>{alt}")
    hgvsp = str(info.get("HGVSp") or "")
    if hgvsp and hgvsp not in name:
        name = f"{name} ({hgvsp.split(':')[-1]})"
    return {
        "GeneSymbol": gene,
        "Name": name,
        "Type": str(info.get("Type") or consequence_to_type(ref, alt)),
        "MolecularConsequence": str(info.get("Consequence") or info.get("MolecularConsequence") or ""),
        "VariationID": "" if record_id == "." else record_id,
        "Chromosome": chrom,
        "Start": pos,
        "ReferenceAllele": ref,
        "AlternateAllele": alt,
    }


def vcf_to_dataframe(vcf_path: pathlib.Path) -> pd.DataFrame:
    annotation_fields: dict[str, list[str]] = {}
    rows: list[dict[str, str]] = []
    with open_text(vcf_path) as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("##INFO="):
                parsed_header = parse_info_header(line)
                if parsed_header:
                    key, fields = parsed_header
                    annotation_fields[key] = fields
                continue
            if line.startswith("#"):
                continue
            fields = line.split("\t")
            if len(fields) < 8:
                raise SystemExit(f"Malformed VCF row with fewer than 8 columns: {line[:120]}")
            chrom, pos, record_id, ref, alt_text, _qual, _filter, info_text = fields[:8]
            alts = alt_text.split(",")
            info = parse_info(info_text)
            annotated = annotation_rows(info, annotation_fields, chrom, pos, record_id, ref, alts)
            if annotated:
                rows.extend(annotated)
                continue
            for alt in alts:
                row = fallback_row(info, chrom, pos, record_id, ref, alt)
                if row:
                    rows.append(row)
    return pd.DataFrame(rows, columns=DEFAULT_OUTPUT_COLUMNS)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Score FH-gene variants from an annotated VCF with the cautious prototype model."
    )
    parser.add_argument("input_vcf", help="Annotated VCF or VCF.GZ from a sequencing/variant-calling pipeline.")
    parser.add_argument("output_csv", help="Output CSV path for ranked FH triage scores.")
    args = parser.parse_args()

    df = vcf_to_dataframe(pathlib.Path(args.input_vcf))
    output = pathlib.Path(args.output_csv)
    output.parent.mkdir(parents=True, exist_ok=True)
    if df.empty:
        df.to_csv(output, index=False)
        print(f"No annotated FH-gene variants found -> {output}")
        return
    scored = score_dataframe(df)
    scored.to_csv(output, index=False)
    print(f"Scored {len(scored)} FH-gene variants from VCF -> {output}")


if __name__ == "__main__":
    main()
