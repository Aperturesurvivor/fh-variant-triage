# Roadmap

## v0.1: Public ClinVar Triage Prototype

Status: current.

- Public ClinVar FH-gene filtering.
- Binary ClinVar-label training target.
- Cautious model excluding review status and submitter count.
- Gene-specific models.
- Hard validation splits.
- Calibration, thresholds, ablations, and rule baseline.
- VUS/conflicting variant triage output.
- Bring-your-own CSV scoring.
- Annotated VCF scoring after standard variant calling and annotation.
- Generated impact-estimate report for review-backlog and population-scale
  planning discussions.
- Dashboard and reviewer audit workflow.

## v0.2: External Annotation Layer

Goal: reduce dependence on ClinVar naming/curation artifacts.

- Add gnomAD allele frequencies.
- Add ancestry-stratified frequency features where available.
- Add CADD, REVEL, AlphaMissense, and SpliceAI where licensing/access permits.
- Add protein-domain position features for `LDLR`.
- Re-run ablations to quantify whether external biological evidence improves
  hard-split performance.

## v0.3: Rule-Based Expert Baselines

Goal: compare machine-learning triage against explicit domain rules.

- Implement LDLR-specific ClinGen/ACMG rule features where feasible.
- Add a transparent ACMG-inspired baseline.
- Compare model-ranked VUS candidates against expert-panel classifications.
- Add a manual-review worksheet for top uncertain variants.

## v0.4: Person-Level Prototype Boundary

Goal: define what would be required for disease probability, without pretending
open variant data is enough.

- Specify a cohort-data schema: genotype, LDL-C, treatment status, age, sex,
  family history, clinical criteria, ancestry/frequency context.
- Build a synthetic/mock person-level interface for research design only.
- Document controlled-access datasets that could support real person-level
  modeling.
