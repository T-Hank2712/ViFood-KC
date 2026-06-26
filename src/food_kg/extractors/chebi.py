"""Extract scoped ChEBI HTML snapshots into staging records."""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

import yaml

SOURCE_ID = "SOURCE:CHEBI"
SOURCE_URL = "https://www.ebi.ac.uk/chebi/"


def snapshot_filename(chebi_id: str) -> str:
    return chebi_id.replace(":", "_") + ".html"


def _ld_json(html_text: str) -> dict:
    match = re.search(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', html_text, flags=re.S)
    if not match:
        raise ValueError("ChEBI page has no application/ld+json molecular entity block")
    return json.loads(html.unescape(match.group(1)))


def extract_record(html_file: Path, chebi_id: str, retrieved_at: str) -> dict:
    html_text = html_file.read_text(encoding="utf-8")
    data = _ld_json(html_text)
    if data.get("identifier") != chebi_id:
        raise ValueError(f"{html_file}: expected {chebi_id}, found {data.get('identifier')}")
    return {
        "chebi_id": chebi_id,
        "name": data["name"],
        "molecular_formula": data.get("molecularFormula"),
        "source_url": data.get("url") or f"https://www.ebi.ac.uk/chebi/{chebi_id}",
        "raw_file": str(html_file),
        "retrieved_at": retrieved_at,
        "source_id": SOURCE_ID,
    }


def extract(scope_file: Path, snapshot_dir: Path, output_file: Path) -> int:
    scope = yaml.safe_load(scope_file.read_text(encoding="utf-8"))
    retrieved_at = str(scope.get("snapshot_date", ""))
    output_file.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with output_file.open("w", encoding="utf-8") as output:
        for item in scope["chemicals"]:
            record = extract_record(snapshot_dir / snapshot_filename(item["chebi_id"]), item["chebi_id"], retrieved_at)
            expected = item.get("expected_name")
            if expected and record["name"].casefold() != expected.casefold():
                raise ValueError(f'{item["chebi_id"]}: expected ChEBI name "{expected}", found "{record["name"]}"')
            output.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract scoped ChEBI HTML snapshots into staging JSONL")
    parser.add_argument("--scope", type=Path, required=True)
    parser.add_argument("--snapshot-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    count = extract(args.scope, args.snapshot_dir, args.output)
    print(f"Extracted {count} ChEBI chemical records to {args.output}")


if __name__ == "__main__":
    main()
