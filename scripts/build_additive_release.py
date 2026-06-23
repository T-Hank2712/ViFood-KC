"""Build an importable additive release from automatic regulation candidates."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import yaml

from food_kg.services.additive_release import SOURCE_ID, build_release, write_json
from food_kg.transformers.additive_master import build_candidates


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--staging", type=Path, required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--reviewed-at", default=date.today().isoformat())
    parser.add_argument("--approved-output", type=Path, required=True)
    parser.add_argument("--nodes-output", type=Path, required=True)
    parser.add_argument("--relationships-output", type=Path, required=True)
    parser.add_argument("--release-output", type=Path, required=True)
    args = parser.parse_args()
    candidates = build_candidates(args.staging, args.reviewed_at)
    nodes, relationships, approved = build_release(candidates, args.reviewed_at)
    write_json(args.approved_output, approved)
    write_json(args.nodes_output, nodes)
    write_json(args.relationships_output, relationships)
    args.release_output.parent.mkdir(parents=True, exist_ok=True)
    args.release_output.write_text(yaml.safe_dump({"version": args.version, "released_at": args.reviewed_at, "source_ids": [SOURCE_ID], "node_count": len(nodes), "relationship_count": len(relationships), "notes": "Automatic release from Appendix 1 of Vietnam's consolidated additive regulation."}, allow_unicode=True, sort_keys=False), encoding="utf-8")
    print(f"Built {args.version}: {len(nodes)} nodes, {len(relationships)} relationships")


if __name__ == "__main__":
    main()
