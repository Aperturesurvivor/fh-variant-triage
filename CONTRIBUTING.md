# Contributing

This is a research prototype, not a clinical tool. Contributions should improve
scientific clarity, reproducibility, validation strength, or usability for
expert review.

## Good First Contributions

- Add external annotation features with clear provenance.
- Improve validation splits or add a new stress test.
- Add tests for data normalization or scoring behavior.
- Improve documentation around limitations and supported claims.
- Compare results against an interpretable baseline or published FH-specific
  method.

## Development Workflow

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python scripts/run_pipeline.py
python -m pytest
```

The full pipeline downloads public ClinVar data and generates local artifacts
under `data/`, `models/`, and `reports/`. These generated files are intentionally
ignored by Git, except for stable Markdown summaries.

## Scientific Standards

- Do not describe model scores as diagnoses.
- Distinguish variant triage, variant classification, and person-level disease
  probability.
- Add provenance for every external dataset.
- Prefer hard validation splits over only random holdouts.
- Report failure modes and ablations when adding new features.
- Keep claims narrower than the evidence.

## Data And Privacy

Do not commit private, identifiable, patient-level, or controlled-access data.
This repository currently uses public ClinVar data and generated local outputs.

