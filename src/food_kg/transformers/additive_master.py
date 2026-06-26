"""Promote every structurally valid Vietnamese-regulation staging row automatically."""

from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path


def identifier(ins: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "_", ins.upper()).strip("_")


def build_candidates(staging_file: Path, reviewed_at: str) -> list[dict]:
    candidates: list[dict] = []
    for line in staging_file.read_text(encoding="utf-8").splitlines():
        source = json.loads(line)
        candidates.append({
            "label": "Additive",
            "id": "ADDITIVE:INS_" + identifier(source["source_ins"]),
            "functional_classes": source["functional_classes"],
            "properties": {
                "name": source["source_name_en"], "name_vi": source["source_name_vi"],
                "ins": source["source_ins"],
                "source": source["source_id"], "source_url": source["source_url"],
                "raw_page_number": source["raw_page_number"], "raw_record_number": source["raw_record_number"],
                "reviewed_at": reviewed_at, "status": "draft",
            },
        })
    if not candidates:
        raise ValueError("Staging file contains no additive records")
    return candidates


def main() -> None:
    parser = argparse.ArgumentParser(description="Create automatic additive candidates from regulation staging data")
    parser.add_argument("--staging", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--reviewed-at", default=datetime.now(UTC).date().isoformat())
    args = parser.parse_args()
    candidates = build_candidates(args.staging, args.reviewed_at)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(candidates, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Created {len(candidates)} automatic additive candidates: {args.output}")


if __name__ == "__main__":
    main()
