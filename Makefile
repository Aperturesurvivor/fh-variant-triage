.PHONY: install test pipeline audit manifest impact dashboard score-example score-vcf-example clean

PYTHON ?= $(shell if [ -x .venv/bin/python ]; then echo .venv/bin/python; else echo python3; fi)

install:
	$(PYTHON) -m pip install -e ".[dev]"

test:
	$(PYTHON) -m pytest

pipeline:
	$(PYTHON) scripts/run_pipeline.py

audit:
	$(PYTHON) scripts/audit_artifacts.py

manifest:
	$(PYTHON) scripts/generate_manifest.py

impact:
	$(PYTHON) scripts/estimate_impact.py

dashboard:
	$(PYTHON) -m http.server 8765

score-example:
	$(PYTHON) scripts/score_variants_csv.py examples/example_variants.csv reports/example_scored_variants.csv

score-vcf-example:
	$(PYTHON) scripts/score_variants_vcf.py examples/example_annotated.vcf reports/example_vcf_scored_variants.csv

clean:
	rm -rf .pytest_cache scripts/__pycache__ tests/__pycache__
