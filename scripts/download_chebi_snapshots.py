"""Download small, scoped ChEBI HTML snapshots by CHEBI ID."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

import yaml


def filename(chebi_id: str) -> str:
    return chebi_id.replace(":", "_") + ".html"


def download(scope_file: Path, output_dir: Path) -> int:
    scope = yaml.safe_load(scope_file.read_text(encoding="utf-8"))
    output_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for item in scope["chemicals"]:
        chebi_id = item["chebi_id"]
        url = f"https://www.ebi.ac.uk/chebi/searchId.do?chebiId={chebi_id}"
        target = output_dir / filename(chebi_id)
        subprocess.run(["curl", "-L", "--fail", "--silent", "--show-error", "--output", str(target), url], check=True)
        count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description="Download ChEBI HTML snapshots for scoped chemical ingredients")
    parser.add_argument("--scope", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    count = download(args.scope, args.output_dir)
    print(f"Downloaded {count} ChEBI snapshots to {args.output_dir}")


if __name__ == "__main__":
    main()
