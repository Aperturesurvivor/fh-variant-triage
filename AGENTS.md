# Agent Handoff

This repository is the durable project hub for the FH variant triage project.
Future Codex sessions should start here.

## First Read

1. `docs/FUTURE_SESSION_HANDOFF.md`
2. `docs/PROJECT_BRIEF.md`
3. `README.md`
4. `MODEL_CARD.md`
5. `PEER_REVIEW_NOTES.md`
6. `REVIEWER_GUIDE.md`

## Project Boundary

This is a familial hypercholesterolemia variant-triage research prototype. It
does not diagnose people, does not estimate a person's probability of FH, and
does not replace ACMG/ClinGen review.

The practical goal is to help prioritize `LDLR`, `APOB`, and `PCSK9` variants
for expert review after standard variant calling and annotation.

## Local Verification

Use:

```bash
make install
make pipeline
make test
make score-example
make score-vcf-example
```

Generated data/model artifacts are ignored by Git except selected Markdown
reports.

## Current Publishing State

The repo is local. GitHub CLI is installed, but GitHub auth was not completed
from the earlier phone/remote-control session. See `docs/GITHUB_PUBLISHING.md`.

Do not claim clinical validity. Ask experts to test and critique the tool.
