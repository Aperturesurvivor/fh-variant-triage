# Outreach Targets

The goal is not to ask people to trust the tool. The goal is to ask qualified
people to test it, criticize it, and identify what would make it useful.

## Highest-Priority Scientific Targets

### ClinGen FH Variant Curation Expert Panel

Why:

- They work directly on FH variant curation for `LDLR`, `APOB`, and `PCSK9`.
- They are the closest match for expert feedback on variant interpretation
  claims and ACMG/ClinGen boundaries.

Ask:

- Are the claims appropriately limited?
- Could this be useful as a triage or benchmarking tool?
- What validation would matter to the panel?

### Family Heart Foundation / CASCADE FH Registry

Why:

- FH-specific patient/clinical registry network.
- Potential path toward real-world validation questions and clinical-site
  feedback.

Ask:

- Would a variant-priority tool be useful for registry/research workflows?
- What outcomes or validation would make this worth studying?
- Are there public or permissible datasets to benchmark against?

### National Lipid Association

Why:

- Lipid specialists and FH clinical guidance.
- Useful for clinical workflow feedback, even if they are not the first group to
  validate the model technically.

Ask:

- Does the framing align with current FH diagnosis/management guidance?
- What would make this useful or unsafe in clinic-adjacent workflows?

### Clinical Genomics / Variant Interpretation Labs

Examples:

- academic molecular pathology labs
- cardiovascular genetics labs
- clinical genomics cores
- variant interpretation teams

Ask:

- Can they run the VCF/CSV scorer on de-identified/internal benchmark sets?
- Does the ranking help prioritize VUS/conflicting variants?
- What annotation formats need better support?

## Technical Review Targets

- bioinformatics researchers
- computational genomics groups
- variant annotation tool users
- VEP/SnpEff users
- open-source genomics communities
- statistical genetics researchers

Ask:

- Is the validation design fair?
- Are the features too artifact-prone?
- What hard splits or baselines are missing?
- Is the VCF parser acceptable for real-world annotation formats?

## Outreach Message

```text
Hi,

I am an independent developer building an open-source research prototype for
familial hypercholesterolemia variant triage. It is not intended for diagnosis
or clinical decision-making.

The tool trains on public ClinVar FH-gene variants and can score annotated VCF
or CSV records for LDLR, APOB, and PCSK9. The goal is to prioritize variants
for expert review, especially VUS/conflicting variants, not to replace
ACMG/ClinGen interpretation.

I am looking for expert criticism and independent validation. If this is not
useful, I would like to understand why. If it is useful, I would like to improve
it toward the field's actual needs.

Repository: <GitHub URL>
Validation request: <GitHub URL>/blob/main/docs/VALIDATION_REQUEST.md

Thank you for any feedback or pointers.
```

## Outreach Rules

- Be humble and precise.
- Do not imply clinical validity.
- Do not ask for private health information.
- Invite criticism before collaboration.
- Ask for validation on de-identified or already-public data only.
- Track responses and requested changes in GitHub issues when appropriate.
