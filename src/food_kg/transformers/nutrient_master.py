"""Build reviewable Nutrient node candidates from INFOODS staging data."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

import yaml


def build_candidates(staging_file: Path, mapping_file: Path, reviewed_at: str) -> list[dict]:
    staging = {
        record["source_tagname"]: record
        for line in staging_file.read_text(encoding="utf-8").splitlines()
        if (record := json.loads(line))
    }
    mapping = yaml.safe_load(mapping_file.read_text(encoding="utf-8"))["candidates"]
    records: list[dict] = []
    missing: list[str] = []
    for candidate in mapping:
        source = staging.get(candidate["tagname"])
        if not source:
            missing.append(candidate["tagname"])
            continue
        properties = {
            "name": candidate["name"],
            "name_vi": candidate["name_vi"],
            "nutrient_type": candidate["nutrient_type"],
            "default_unit": candidate["default_unit"],
            "external_code": source["source_tagname"],
            "source_name": source["source_name"],
            "source_comments": source["comments"],
            "source": source["source_id"],
            "source_url": source["source_url"],
            "source_version": "INFOODS Tagnames snapshot 2026-06-22",
            "reviewed_at": reviewed_at,
            "status": "draft",
        }
        records.append({"label": "Nutrient", "id": candidate["id"], "properties": properties})
    if missing:
        raise ValueError(f"Configured Tagnames missing from staging: {', '.join(missing)}")
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description="Create INFOODS nutrient-master candidates for manual review")
    parser.add_argument("--staging", type=Path, required=True)
    parser.add_argument("--mapping", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--reviewed-at", default=datetime.now(UTC).date().isoformat())
    args = parser.parse_args()
    candidates = build_candidates(args.staging, args.mapping, args.reviewed_at)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(candidates, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Created {len(candidates)} nutrient candidates for review: {args.output}")


if __name__ == "__main__":
    main()
