"""Create a FoodOn curated release from reviewed candidate files."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import yaml

from food_kg.services.foodon_release import SOURCE_ID, TRANSLATION_SOURCE_ID, build_release, write_json


def load(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--categories", type=Path, required=True)
    parser.add_argument("--aliases", type=Path, action="append", required=True)
    parser.add_argument("--relationships", type=Path, action="append", required=True)
    parser.add_argument("--category-patches", type=Path, action="append", default=[])
    parser.add_argument("--version", required=True)
    parser.add_argument("--reviewed-at", default=date.today().isoformat())
    parser.add_argument("--approved-categories-output", type=Path, required=True)
    parser.add_argument("--approved-aliases-output", type=Path, required=True)
    parser.add_argument("--nodes-output", type=Path, required=True)
    parser.add_argument("--relationships-output", type=Path, required=True)
    parser.add_argument("--release-output", type=Path, required=True)
    args = parser.parse_args()
    patches = [patch for path in args.category_patches for patch in load(path)]
    aliases_input = [alias for path in args.aliases for alias in load(path)]
    relationships_input = [relationship for path in args.relationships for relationship in load(path)]
    nodes, rels, categories, aliases = build_release(load(args.categories), aliases_input, relationships_input, args.reviewed_at, patches)
    write_json(args.approved_categories_output, categories)
    write_json(args.approved_aliases_output, aliases)
    write_json(args.nodes_output, nodes)
    write_json(args.relationships_output, rels)
    args.release_output.parent.mkdir(parents=True, exist_ok=True)
    args.release_output.write_text(yaml.safe_dump({"version": args.version, "released_at": args.reviewed_at, "source_ids": [SOURCE_ID, TRANSLATION_SOURCE_ID], "node_count": len(nodes), "relationship_count": len(rels), "notes": "FoodOn knowledge taxonomy; ambiguous aliases are held back for review."}, allow_unicode=True, sort_keys=False), encoding="utf-8")
    print(f"Built {args.version}: {len(nodes)} nodes, {len(rels)} relationships")


if __name__ == "__main__":
    main()
