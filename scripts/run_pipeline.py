from __future__ import annotations

import subprocess
import sys


STEPS = [
    ["scripts/download_clinvar.py"],
    ["scripts/build_dataset.py"],
    ["scripts/train_baseline.py"],
    ["scripts/score_unlabeled.py"],
    ["scripts/train_gene_models.py"],
    ["scripts/analyze_model.py"],
    ["scripts/learning_curve.py"],
    ["scripts/validate_splits.py"],
    ["scripts/generate_report.py"],
    ["scripts/generate_manifest.py"],
    ["scripts/audit_artifacts.py"],
]


def main() -> None:
    for step in STEPS:
        print(f"\n=== python {' '.join(step)} ===", flush=True)
        subprocess.run([sys.executable, *step], check=True)


if __name__ == "__main__":
    main()
