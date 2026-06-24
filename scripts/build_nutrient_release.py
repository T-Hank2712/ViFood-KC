"""Promote reviewed INFOODS nutrient candidates into an importable curated release."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import yaml

from food_kg.services.nutrient_release import SOURCE_ID, VIETNAM_FCT_SOURCE_ID, VIETNAM_LABELING_SOURCE_ID, build_release, write_json


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--reviewed-at", default=date.today().isoformat())
    parser.add_argument("--approved-output", type=Path, required=True)
    parser.add_argument("--nodes-output", type=Path, required=True)
    parser.add_argument("--relationships-output", type=Path, required=True)
    parser.add_argument("--release-output", type=Path, required=True)
    args = parser.parse_args()
    candidates = json.loads(args.candidates.read_text(encoding="utf-8"))
    nodes, relationships, approved = build_release(candidates, args.reviewed_at)
    write_json(args.approved_output, approved)
    write_json(args.nodes_output, nodes)
    write_json(args.relationships_output, relationships)
    args.release_output.parent.mkdir(parents=True, exist_ok=True)
    args.release_output.write_text(yaml.safe_dump({
        "version": args.version, "released_at": args.reviewed_at,
        "source_ids": [SOURCE_ID,
            *([VIETNAM_FCT_SOURCE_ID] if any(candidate["properties"].get("vietnam_presence_source") == VIETNAM_FCT_SOURCE_ID for candidate in candidates) else []),
            *([VIETNAM_LABELING_SOURCE_ID] if any(candidate["properties"].get("vietnam_labeling_source") == VIETNAM_LABELING_SOURCE_ID for candidate in candidates) else []),
        ], "node_count": len(nodes),
        "relationship_count": len(relationships),
        "notes": "Nutrient master derived from FAO/INFOODS Tagnames; Vietnam relevance is selected by exact tagname intersection with the FAO SMILING Vietnam FCT when present.",
    }, allow_unicode=True, sort_keys=False), encoding="utf-8")
    print(f"Built {args.version}: {len(nodes)} nodes, {len(relationships)} relationships")


if __name__ == "__main__":
    main()
