"""Build a curated HealthClaim release from a verified WHO snapshot."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import yaml

from food_kg.extractors.who_health_claims import extract_claims
from food_kg.services.health_claim_release import build_release


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-html", type=Path, required=True)
    parser.add_argument("--rules", type=Path, required=True)
    parser.add_argument("--nutrient-nodes", type=Path, required=True)
    parser.add_argument("--staging-output", type=Path, required=True)
    parser.add_argument("--nodes-output", type=Path, required=True)
    parser.add_argument("--relationships-output", type=Path, required=True)
    parser.add_argument("--release-output", type=Path, required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--reviewed-at", default=date.today().isoformat())
    args = parser.parse_args()
    claim_count = extract_claims(args.raw_html, args.rules, args.staging_output, args.reviewed_at)
    nodes, relationships = build_release(args.staging_output, args.nutrient_nodes, args.reviewed_at)
    write_json(args.nodes_output, nodes)
    write_json(args.relationships_output, relationships)
    args.release_output.parent.mkdir(parents=True, exist_ok=True)
    args.release_output.write_text(yaml.safe_dump({
        "version": args.version, "released_at": args.reviewed_at,
        "source_ids": ["SOURCE:FAO_INFOODS_TAGNAMES", "SOURCE:WHO_HEALTHY_DIET"],
        "node_count": len(nodes), "relationship_count": len(relationships),
        "notes": "WHO Healthy Diet claims whose configured evidence excerpts were verified against the raw snapshot.",
    }, allow_unicode=True, sort_keys=False), encoding="utf-8")
    print(f"Built {args.version}: {claim_count} claims, {len(nodes)} nodes, {len(relationships)} relationships")


if __name__ == "__main__":
    main()
