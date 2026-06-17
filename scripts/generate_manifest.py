from __future__ import annotations

import hashlib
import json
import pathlib
import platform
import subprocess
import sys
from datetime import datetime, timezone


OUT = pathlib.Path("reports/run_manifest.json")
TRACKED_ARTIFACTS = [
    "data/raw/variant_summary.txt.gz",
    "data/processed/fh_clinvar_variants.csv",
    "reports/dataset_profile.json",
    "reports/baseline_metrics.json",
    "reports/gene_models.json",
    "reports/model_analysis.json",
    "reports/learning_curve.json",
    "reports/validation_splits.json",
    "reports/unlabeled_triage_summary.json",
    "reports/unlabeled_triage_top.csv",
    "reports/research_report.md",
    "models/fh_cautious_random_forest.joblib",
    "models/fh_cautious_features.json",
]


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_value(args: list[str]) -> str | None:
    try:
        return subprocess.check_output(["git", *args], text=True).strip()
    except Exception:
        return None


def file_record(path_text: str) -> dict:
    path = pathlib.Path(path_text)
    if not path.exists():
        return {"path": path_text, "exists": False}
    return {
        "path": path_text,
        "exists": True,
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def main() -> None:
    manifest = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": {
            "executable": sys.executable,
            "version": sys.version,
            "platform": platform.platform(),
        },
        "git": {
            "commit": git_value(["rev-parse", "HEAD"]),
            "branch": git_value(["branch", "--show-current"]),
            "dirty": bool(git_value(["status", "--short"])),
        },
        "clinvar_source": {
            "url": "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt.gz",
            "local_path": "data/raw/variant_summary.txt.gz",
        },
        "artifacts": [file_record(path) for path in TRACKED_ARTIFACTS],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()

