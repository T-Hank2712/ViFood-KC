"""Promote reviewed FoodOn category candidates into a curated release."""

from __future__ import annotations

import json
from pathlib import Path

SOURCE_ID = "SOURCE:FOODON"
SOURCE_URL = "https://github.com/FoodOntology/foodon"
TRANSLATION_SOURCE_ID = "SOURCE:VIFOOD_TRANSLATION_SEED"
TRANSLATION_SOURCE_URL = "internal://vi-food-translation-seed"


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def activate(records: list[dict], reviewed_at: str) -> list[dict]:
    return [{**record, "properties": {**record["properties"], "status": "active", "reviewed_at": reviewed_at}} for record in records]


def apply_patches(categories: list[dict], patches: list[dict]) -> list[dict]:
    patch_by_id = {patch["id"]: patch["properties"] for patch in patches}
    unknown = sorted(set(patch_by_id) - {category["id"] for category in categories})
    if unknown:
        raise ValueError(f"Translation patches target unknown categories: {', '.join(unknown)}")
    return [{**category, "properties": {**category["properties"], **patch_by_id.get(category["id"], {})}} for category in categories]


def build_release(categories: list[dict], aliases: list[dict], relationships: list[dict], reviewed_at: str, patches: list[dict] | None = None) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    source = {"label": "Source", "id": SOURCE_ID, "properties": {"name": "FoodOn Food Ontology", "source_type": "standard", "url": SOURCE_URL, "source": SOURCE_ID, "source_url": SOURCE_URL, "reviewed_at": reviewed_at, "status": "active"}}
    categories = apply_patches(categories, patches or [])
    translation_source = {"label": "Source", "id": TRANSLATION_SOURCE_ID, "properties": {"name": "ViFood-KG Vietnamese translation seed", "source_type": "internal-curation", "url": TRANSLATION_SOURCE_URL, "source": TRANSLATION_SOURCE_ID, "source_url": TRANSLATION_SOURCE_URL, "reviewed_at": reviewed_at, "status": "active"}}
    approved_categories, approved_aliases = activate(categories, reviewed_at), activate(aliases, reviewed_at)
    support_relationships = [{"start_id": category["id"], "end_id": SOURCE_ID, "type": "SUPPORTED_BY", "properties": {"context": "packaged-food-taxonomy", "foodon_id": category["properties"]["foodon_id"]}} for category in approved_categories]
    return [source, translation_source, *approved_categories, *approved_aliases], [*relationships, *support_relationships], approved_categories, approved_aliases
