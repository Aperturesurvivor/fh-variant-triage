.PHONY: install test pipeline audit manifest dashboard score-example clean

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

dashboard:
	$(PYTHON) -m http.server 8765

score-example:
	$(PYTHON) scripts/score_variants_csv.py examples/example_variants.csv reports/example_scored_variants.csv

clean:
	rm -rf .pytest_cache scripts/__pycache__ tests/__pycache__
