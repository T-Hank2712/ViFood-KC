"""Build Vietnamese name patches and non-canonical aliases for FoodOn categories."""

from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path

import yaml


def build_candidates(categories: list[dict], translations: dict, reviewed_at: str) -> tuple[list[dict], list[dict], list[dict]]:
    by_foodon_id = {row["properties"]["foodon_id"]: row for row in categories}
    patches, aliases, relationships = [], [], []
    for item in translations["translations"]:
        category = by_foodon_id.get(item["foodon_id"])
        if not category:
            raise ValueError(f"Translation target is absent from FoodOn scope: {item['foodon_id']}")
        category_id = category["id"]
        patches.append({
            "label": "FoodCategory", "id": category_id,
            "properties": {
                "name": category["properties"]["name"], "name_vi": item["name_vi"],
                "foodon_id": item["foodon_id"], "source": category["properties"]["source"],
                "source_url": category["properties"]["source_url"],
                "translation_source": translations["source_id"], "translation_status": "draft",
                "reviewed_at": reviewed_at, "status": "draft",
            },
        })
        # name_vi is the canonical Vietnamese display/search name on the
        # FoodCategory node, so do not duplicate it as an Alias node.
        for index, alias_name in enumerate(item.get("aliases", []), start=1):
            alias_id = "ALIAS:" + re.sub(r"[^A-Z0-9_]", "_", f"{category_id.split(':', 1)[1]}_VI_{index}".upper())
            aliases.append({
                "label": "Alias", "id": alias_id,
                "properties": {
                    "name": alias_name, "normalized_name": " ".join(alias_name.casefold().split()),
                    "language": "vi", "alias_type": "common-name",
                    "source": translations["source_id"], "source_url": translations["source_url"],
                    "reviewed_at": reviewed_at, "status": "draft",
                },
            })
            relationships.append({"start_id": alias_id, "end_id": category_id, "type": "REFERS_TO", "properties": {"source": translations["source_id"]}})
    return patches, aliases, relationships


def write_json(path: Path, content: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(content, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--categories", type=Path, required=True)
    parser.add_argument("--translations", type=Path, required=True)
    parser.add_argument("--patches-output", type=Path, required=True)
    parser.add_argument("--aliases-output", type=Path, required=True)
    parser.add_argument("--relationships-output", type=Path, required=True)
    parser.add_argument("--reviewed-at", default=datetime.now(UTC).date().isoformat())
    args = parser.parse_args()
    categories = json.loads(args.categories.read_text(encoding="utf-8"))
    translations = yaml.safe_load(args.translations.read_text(encoding="utf-8"))
    patches, aliases, relationships = build_candidates(categories, translations, args.reviewed_at)
    write_json(args.patches_output, patches)
    write_json(args.aliases_output, aliases)
    write_json(args.relationships_output, relationships)
    print(f"Created {len(patches)} Vietnamese name patches, {len(aliases)} non-canonical aliases and {len(relationships)} relationships for review.")


if __name__ == "__main__":
    main()
