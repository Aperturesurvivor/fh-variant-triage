# FH Variant Triage

Research prototype for familial hypercholesterolemia variant triage.

This project is not a diagnostic medical tool. It explores whether public
ClinVar-style data can support a transparent model that prioritizes variants in
`LDLR`, `APOB`, and `PCSK9` for expert review.

## Current Status

This is an early research prototype with a reproducible local pipeline,
dashboard, model card, hard validation splits, and unit tests. The strongest
current use is variant-prioritization research, not clinical decision-making.

## First Target

- Download ClinVar `variant_summary.txt.gz`.
- Filter variants for FH genes: `LDLR`, `APOB`, `PCSK9`.
- Normalize ClinVar germline clinical significance into binary training labels:
  pathogenic/likely pathogenic vs benign/likely benign.
- Hold out variants for evaluation.
- Train simple tabular baselines and compare against non-ML rule baselines.

## Commands

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/download_clinvar.py
python scripts/build_dataset.py
python scripts/train_baseline.py
python scripts/score_unlabeled.py
python scripts/train_gene_models.py
python scripts/analyze_model.py
python scripts/learning_curve.py
python scripts/validate_splits.py
python scripts/generate_report.py
python scripts/generate_manifest.py
python scripts/audit_artifacts.py
python -m pytest
```

Or run the whole analysis pipeline:

```bash
python scripts/run_pipeline.py
```

This downloads public ClinVar data, rebuilds the processed dataset, trains
baseline and gene-specific models, scores uncertain/conflicting variants,
regenerates the research report, and audits that the expected artifacts exist.

For a reviewer, the shortest verification path is:

```bash
python -m pip install -e ".[dev]"
python scripts/run_pipeline.py
python -m pytest
```

Equivalent `make` shortcuts are available:

```bash
make install
make pipeline
make test
```

Then read:

- [reports/research_report.md](reports/research_report.md) for the generated results.
- `reports/run_manifest.json` for artifact hashes, raw ClinVar hash, Python
  version, and git commit after running the pipeline.
- [PEER_REVIEW_NOTES.md](PEER_REVIEW_NOTES.md) for supported and unsupported claims.
- [MODEL_CARD.md](MODEL_CARD.md) for intended-use boundaries.

Score your own small FH-gene variant CSV after training:

```bash
python scripts/score_variants_csv.py examples/example_variants.csv reports/example_scored_variants.csv
```

Input can use ClinVar-like columns such as `GeneSymbol`, `Name`, `Type`, and
`MolecularConsequence`, or normalized aliases such as `gene`, `variant_name`,
and `variant_type`.

See [docs/INPUT_SCHEMA.md](docs/INPUT_SCHEMA.md) for accepted columns and output
interpretation.

Open the local monitor:

```bash
python3 -m http.server 8765
```

Then visit <http://localhost:8765/dashboard/>.

## What The Score Means

The current model predicts whether a variant looks more like ClinVar variants
classified as pathogenic/likely pathogenic or benign/likely benign. It does not
predict a person's percent likelihood of having FH.

For a person-level FH probability model, this variant score would be one input
alongside LDL cholesterol, age, sex, family history, ancestry/frequency context,
and clinical diagnostic criteria.

## Research Notes

See [METHODS.md](METHODS.md) for the current design, validation approach, and
limitations.

See [MODEL_CARD.md](MODEL_CARD.md) for intended use and misuse boundaries.
See [DATA_SOURCES.md](DATA_SOURCES.md) for data provenance and planned external
annotations.
See [PEER_REVIEW_NOTES.md](PEER_REVIEW_NOTES.md) for supported claims, unsupported
claims, and known reviewer concerns.
See [REVIEWER_GUIDE.md](REVIEWER_GUIDE.md) for a peer-review checklist.
See [ROADMAP.md](ROADMAP.md) and [docs/MANUSCRIPT_DRAFT.md](docs/MANUSCRIPT_DRAFT.md)
for planned scientific extensions and manuscript framing.

## Data Collaboration

This project is intentionally limited to public, reproducible inputs. The next
major improvements require independent evidence beyond ClinVar labels.

Useful datasets or annotations would include:

- FH variant functional assay results for `LDLR`, `APOB`, or `PCSK9`
- expert ACMG/AMP or ClinGen-reviewed classifications not used during training
- population-frequency annotations across diverse ancestries
- phenotype-linked cohorts with LDL-C, age, treatment status, family history,
  ancestry context, and genotype
- segregation evidence from families
- splicing, protein-domain, conservation, or saturation-mutagenesis annotations
- independent validation sets from clinics, registries, or biobanks that can be
  shared ethically and legally

Researchers, clinicians, patient registries, or dataset maintainers with ideas
for additional public datasets or permissible validation data are encouraged to
open an issue or discussion. Please do not share private health information in
GitHub issues.

## License

MIT. See [LICENSE](LICENSE).
