"""Extract Codex allergen records from a reviewed source snapshot config."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

import yaml


def extract_records(config: dict, retrieved_at: str) -> list[dict]:
    source = config["source"]
    records: list[dict] = []
    for item in config["allergens"]:
        records.append({
            "source_id": source["id"],
            "source_name": source["name"],
            "source_url": source["url"],
            "standard_code": source["standard_code"],
            "source_section": source["section"],
            "allergen_code": item["code"],
            "name": item["name"],
            "name_vi": item["name_vi"],
            "category_type": item["category_type"],
            "codex_text": item["codex_text"],
            "examples": item.get("examples", []),
            "examples_vi": item.get("examples_vi", []),
            "threshold": item.get("threshold"),
            "aliases": item.get("aliases", []),
            "retrieved_at": retrieved_at,
        })
    return records


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract Codex CXS 1-1985 allergen records to staging JSONL")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--retrieved-at", default=datetime.now(UTC).date().isoformat())
    args = parser.parse_args()
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    records = extract_records(config, args.retrieved_at)
    write_jsonl(args.output, records)
    print(f"Extracted {len(records)} Codex allergen records")


if __name__ == "__main__":
    main()
