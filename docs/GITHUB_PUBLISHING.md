# GitHub Publishing Checklist

## Current Blocker

GitHub CLI is installed, but authentication was not completed from the remote
phone session. Complete this from the computer:

```bash
cd /Users/josiahwilson/fh-variant-triage
gh auth login
```

Then publish:

```bash
gh repo create fh-variant-triage --public --source=. --remote=origin --push
```

## Before Publishing

Run:

```bash
git status -sb
make test
make pipeline
make score-example
make score-vcf-example
```

Confirm:

- `git status -sb` is clean except ignored generated artifacts.
- README says research prototype, not diagnostic tool.
- `MODEL_CARD.md` and `PEER_REVIEW_NOTES.md` are present.
- `docs/VALIDATION_REQUEST.md` and `docs/EXTERNAL_VALIDATION_PROTOCOL.md` are present.
- No private health information or private datasets are committed.

## After Publishing

Recommended GitHub settings:

- Enable Issues.
- Enable Discussions if available.
- Add repository topics:
  - `familial-hypercholesterolemia`
  - `clinvar`
  - `variant-interpretation`
  - `bioinformatics`
  - `machine-learning`
  - `genomics`
  - `vcf`
  - `open-science`
- Add a repository description:
  - `Open-source research prototype for FH variant triage from ClinVar, CSV, and annotated VCF data.`

## First Release

After publishing and verifying the public repo:

```bash
git tag v0.1.0
git push origin v0.1.0
```

Release title:

```text
v0.1.0 - ClinVar-trained FH variant triage prototype
```

Release notes:

```markdown
Initial open-source research prototype for familial hypercholesterolemia variant
triage. Includes:

- reproducible ClinVar pipeline
- cautious baseline model
- CSV and annotated VCF scoring
- validation splits and ablations
- research report and impact estimate
- model card and peer-review notes

This release is for research and expert review only. It is not a diagnostic
medical device and should not be used for clinical decision-making.
```

## Optional DOI

After the first GitHub release, connect the repository to Zenodo and archive
`v0.1.0` for a DOI. Add the DOI badge to `README.md` after Zenodo creates it.
