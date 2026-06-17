from __future__ import annotations

import hashlib
import pathlib
import urllib.request


URL = "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt.gz"
OUT = pathlib.Path("data/raw/variant_summary.txt.gz")


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    if OUT.exists() and OUT.stat().st_size > 0:
        print(f"Already exists: {OUT} ({OUT.stat().st_size:,} bytes)")
    else:
        print(f"Downloading {URL}")
        urllib.request.urlretrieve(URL, OUT)
    print(f"sha256={sha256(OUT)}")


if __name__ == "__main__":
    main()

