from __future__ import annotations

import argparse
import json
import pathlib


UNLABELED = pathlib.Path("reports/unlabeled_triage_summary.json")
VALIDATION = pathlib.Path("reports/validation_splits.json")
MODEL_ANALYSIS = pathlib.Path("reports/model_analysis.json")
OUT = pathlib.Path("reports/impact_estimate.md")

SOURCES = [
    {
        "name": "CDC FH overview",
        "url": "https://www.cdc.gov/heart-disease-family-history/about/about-familial-hypercholesterolemia.html",
        "used_for": "FH signs, symptoms, and LDL threshold context.",
    },
    {
        "name": "CDC Genomics blog: How common is FH?",
        "url": "https://blogs.cdc.gov/genomics/2021/01/25/how-common-is-fh/",
        "used_for": "FH prevalence range: about 1 in 250 historically; meta-analysis closer to 1 in 311.",
    },
    {
        "name": "World Heart Federation FH page",
        "url": "https://world-heart-federation.org/what-we-do/cholesterol/familial-hypercholesterolemia/",
        "used_for": "Order-of-magnitude underdiagnosis framing; only about 10% diagnosed worldwide.",
    },
    {
        "name": "American Heart Association FH overview",
        "url": "https://www.heart.org/en/health-topics/cholesterol/genetic-conditions/familial-hypercholesterolemia-fh",
        "used_for": "Early identification and treatment context.",
    },
]


def load(path: pathlib.Path) -> dict:
    if not path.exists():
        raise SystemExit(f"Missing {path}; run scripts/run_pipeline.py first")
    return json.loads(path.read_text())


def fmt_int(x: float) -> str:
    return f"{round(x):,}"


def pct(x: float) -> str:
    return f"{x * 100:.1f}%"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a transparent impact estimate for FH variant triage.")
    parser.add_argument("--population", type=int, default=342_000_000, help="Planning population size.")
    parser.add_argument("--prevalence-high", type=float, default=1 / 250, help="Higher FH prevalence assumption.")
    parser.add_argument("--prevalence-low", type=float, default=1 / 311, help="Lower FH prevalence assumption.")
    parser.add_argument("--diagnosed-rate-low", type=float, default=0.10, help="Lower diagnosed-rate assumption.")
    parser.add_argument("--diagnosed-rate-high", type=float, default=0.20, help="Higher diagnosed-rate assumption.")
    parser.add_argument("--clinic-uncertain-variants", type=int, default=500, help="Example clinic backlog size.")
    parser.add_argument("--sequenced-people", type=int, default=1_000_000, help="Example sequenced cohort size.")
    args = parser.parse_args()

    unlabeled = load(UNLABELED)
    validation = load(VALIDATION)
    analysis = load(MODEL_ANALYSIS)

    band_counts = unlabeled["triage_band_counts"]
    unlabeled_total = unlabeled["unlabeled_rows_scored"]
    high_share = band_counts.get("high_priority_review", 0) / unlabeled_total
    moderate_share = band_counts.get("moderate_priority_review", 0) / unlabeled_total
    review_share = high_share + moderate_share

    fh_people_low = args.population * args.prevalence_low
    fh_people_high = args.population * args.prevalence_high
    undiagnosed_low = fh_people_low * (1 - args.diagnosed_rate_high)
    undiagnosed_high = fh_people_high * (1 - args.diagnosed_rate_low)
    cohort_fh_low = args.sequenced_people * args.prevalence_low
    cohort_fh_high = args.sequenced_people * args.prevalence_high
    clinic_high = args.clinic_uncertain_variants * high_share
    clinic_review = args.clinic_uncertain_variants * review_share

    random_holdout = next(s for s in validation["splits"] if s["name"] == "random_holdout")
    temporal = next(s for s in validation["splits"] if s["name"] == "temporal_last_evaluated")
    threshold_05 = next(row for row in analysis["operating_points"] if row["threshold"] == 0.5)

    lines = [
        "# FH Variant Triage Impact Estimate",
        "",
        "This is a planning estimate, not a clinical outcome claim. It combines public FH burden assumptions with this repository's current validation and triage outputs.",
        "",
        "## Current Model Throughput Signal",
        "",
        f"- Uncertain/conflicting/excluded ClinVar FH records scored: {unlabeled_total:,}",
        f"- High-priority review band: {band_counts.get('high_priority_review', 0):,} ({pct(high_share)})",
        f"- Moderate-or-high review band: {band_counts.get('high_priority_review', 0) + band_counts.get('moderate_priority_review', 0):,} ({pct(review_share)})",
        f"- Lower-priority/watchlist records: {band_counts.get('lower_priority', 0) + band_counts.get('watchlist', 0):,}",
        "",
        "If a clinic had a backlog of "
        f"{args.clinic_uncertain_variants:,} annotated FH-gene variants of uncertain or conflicting significance, "
        f"the current band distribution would put about {fmt_int(clinic_high)} into high-priority review and "
        f"about {fmt_int(clinic_review)} into moderate-or-high review.",
        "",
        "## Current Accuracy Boundary",
        "",
        f"- Random hidden ClinVar split: {pct(random_holdout['accuracy'])} accuracy and {pct(random_holdout['balanced_accuracy'])} balanced accuracy on {random_holdout['test_rows']:,} held-out variants.",
        f"- Temporal LastEvaluated split: {pct(temporal['accuracy'])} accuracy and {pct(temporal['balanced_accuracy'])} balanced accuracy on {temporal['test_rows']:,} newer-evaluation variants.",
        f"- At the default 0.5 threshold: {threshold_05['false_alarm_count']:,} benign-labeled variants were flagged and {threshold_05['missed_pathogenic_count']:,} pathogenic-labeled variants were missed in the hidden test set.",
        "",
        "The random split is the optimistic operating signal. The harder split and gene-held-out validations in `reports/validation_splits.json` are better evidence for deployment risk.",
        "",
        "## Population-Scale Planning Math",
        "",
        f"For a planning population of {args.population:,} people:",
        "",
        f"- Using FH prevalence assumptions of 1 in 311 to 1 in 250, expected FH cases are roughly {fmt_int(fh_people_low)} to {fmt_int(fh_people_high)}.",
        f"- If only {pct(args.diagnosed_rate_low)} to {pct(args.diagnosed_rate_high)} are diagnosed, potentially undiagnosed FH cases are roughly {fmt_int(undiagnosed_low)} to {fmt_int(undiagnosed_high)}.",
        "",
        f"For every {args.sequenced_people:,} people sequenced or otherwise genetically screened, the same prevalence range implies roughly {fmt_int(cohort_fh_low)} to {fmt_int(cohort_fh_high)} people with FH before accounting for test sensitivity, phenotype filters, or uptake.",
        "",
        "## How This Could Multiply Expert Capacity",
        "",
        "The practical value is prioritization. The tool does not replace a lipid specialist, genetic counselor, clinical laboratory director, or ACMG/ClinGen review. It can reduce the first-pass reading burden by moving the most suspicious FH-gene variants to the top of a review queue.",
        "",
        "Useful near-term deployment shapes:",
        "",
        "- research registry triage for variants of uncertain significance",
        "- clinical-lab quality improvement dashboards after standard variant calling and annotation",
        "- cascade-screening support after a known family variant is identified",
        "- prioritization of variants for functional assay follow-up",
        "- education and reproducible benchmarking against CADD, REVEL, AlphaMissense, SpliceAI, ClinGen, and ACMG/AMP calls",
        "",
        "## Data That Would Make The Estimate Stronger",
        "",
        "- real clinic/lab counts of FH-gene VUS and conflicting variants per month",
        "- expert review time per variant before and after triage",
        "- fraction of model high-priority variants later upgraded to pathogenic/likely pathogenic",
        "- downstream treatment changes after variant reclassification",
        "- LDL-C reduction and cardiovascular-event outcomes after earlier identification",
        "- ancestry-stratified validation cohorts",
        "",
        "## Sources",
        "",
    ]
    for source in SOURCES:
        lines.append(f"- [{source['name']}]({source['url']}): {source['used_for']}")
    lines.append("")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines))
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
