# Peer Review Notes

This repository is intended as an openly inspectable research prototype, not as
a clinical product.

## Claims The Current Evidence Supports

- Public ClinVar labels for `LDLR`, `APOB`, and `PCSK9` contain enough signal
  to train a first-pass variant triage model.
- Random holdout and temporal-style validation perform strongly.
- Cross-gene transfer is weak enough that gene-aware modeling is preferred.
- Uncertain/conflicting ClinVar variants can be ranked for expert-review
  prioritization.

## Claims The Current Evidence Does Not Support

- Person-level probability of familial hypercholesterolemia.
- Clinical diagnosis or treatment decisions.
- Ethnicity-agnostic validity.
- True functional pathogenicity independent of ClinVar curation patterns.

## Known Reviewer Concerns

- The top feature in the current cautious random forest is variant-name length,
  which is likely an annotation artifact or complexity proxy, not direct
  biology. The repository now includes ablations that remove this feature and
  report how much performance changes.
- Current features are too weak: no population frequency, protein-domain
  context, family segregation, functional assay data, or external pathogenicity
  scores yet.
- ClinVar labels are an imperfect target because they are themselves curated
  interpretations with ascertainment, ancestry, submitter, and publication
  biases.
- Some high-scoring uncertain variants are deletions/frameshifts in `LDLR`;
  this is plausible for FH but must be independently checked with ClinGen/ACMG
  criteria.

## Highest-Value Next Experiments

1. Add gnomAD allele frequencies and population-stratified frequencies.
2. Add CADD, REVEL, AlphaMissense, and SpliceAI scores where access/licensing
   permits.
3. Create an explicit ACMG/ClinGen rules baseline for `LDLR`.
4. Compare the model against published FH-specific tools and ClinGen expert
   panel classifications.
5. Build a small manual-review set from the generated VUS candidate CSV.

## Reproducibility Check

Run:

```bash
python scripts/run_pipeline.py
python -m pytest
```

The pipeline ends with `scripts/audit_artifacts.py`, which checks that expected
reports, model files, validation splits, ablation outputs, and uncertain-variant
triage artifacts were generated.
