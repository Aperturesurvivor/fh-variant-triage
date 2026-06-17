# FH Variant Triage Impact Estimate

This is a planning estimate, not a clinical outcome claim. It combines public FH burden assumptions with this repository's current validation and triage outputs.

## Current Model Throughput Signal

- Uncertain/conflicting/excluded ClinVar FH records scored: 5,364
- High-priority review band: 1,269 (23.7%)
- Moderate-or-high review band: 1,690 (31.5%)
- Lower-priority/watchlist records: 3,674

If a clinic had a backlog of 500 annotated FH-gene variants of uncertain or conflicting significance, the current band distribution would put about 118 into high-priority review and about 158 into moderate-or-high review.

## Current Accuracy Boundary

- Random hidden ClinVar split: 94.9% accuracy and 95.2% balanced accuracy on 1,538 held-out variants.
- Temporal LastEvaluated split: 94.8% accuracy and 93.6% balanced accuracy on 1,506 newer-evaluation variants.
- At the default 0.5 threshold: 62 benign-labeled variants were flagged and 17 pathogenic-labeled variants were missed in the hidden test set.

The random split is the optimistic operating signal. The harder split and gene-held-out validations in `reports/validation_splits.json` are better evidence for deployment risk.

## Population-Scale Planning Math

For a planning population of 342,000,000 people:

- Using FH prevalence assumptions of 1 in 311 to 1 in 250, expected FH cases are roughly 1,099,678 to 1,368,000.
- If only 10.0% to 20.0% are diagnosed, potentially undiagnosed FH cases are roughly 879,743 to 1,231,200.

For every 1,000,000 people sequenced or otherwise genetically screened, the same prevalence range implies roughly 3,215 to 4,000 people with FH before accounting for test sensitivity, phenotype filters, or uptake.

## How This Could Multiply Expert Capacity

The practical value is prioritization. The tool does not replace a lipid specialist, genetic counselor, clinical laboratory director, or ACMG/ClinGen review. It can reduce the first-pass reading burden by moving the most suspicious FH-gene variants to the top of a review queue.

Useful near-term deployment shapes:

- research registry triage for variants of uncertain significance
- clinical-lab quality improvement dashboards after standard variant calling and annotation
- cascade-screening support after a known family variant is identified
- prioritization of variants for functional assay follow-up
- education and reproducible benchmarking against CADD, REVEL, AlphaMissense, SpliceAI, ClinGen, and ACMG/AMP calls

## Data That Would Make The Estimate Stronger

- real clinic/lab counts of FH-gene VUS and conflicting variants per month
- expert review time per variant before and after triage
- fraction of model high-priority variants later upgraded to pathogenic/likely pathogenic
- downstream treatment changes after variant reclassification
- LDL-C reduction and cardiovascular-event outcomes after earlier identification
- ancestry-stratified validation cohorts

## Sources

- [CDC FH overview](https://www.cdc.gov/heart-disease-family-history/about/about-familial-hypercholesterolemia.html): FH signs, symptoms, and LDL threshold context.
- [CDC Genomics blog: How common is FH?](https://blogs.cdc.gov/genomics/2021/01/25/how-common-is-fh/): FH prevalence range: about 1 in 250 historically; meta-analysis closer to 1 in 311.
- [World Heart Federation FH page](https://world-heart-federation.org/what-we-do/cholesterol/familial-hypercholesterolemia/): Order-of-magnitude underdiagnosis framing; only about 10% diagnosed worldwide.
- [American Heart Association FH overview](https://www.heart.org/en/health-topics/cholesterol/genetic-conditions/familial-hypercholesterolemia-fh): Early identification and treatment context.
