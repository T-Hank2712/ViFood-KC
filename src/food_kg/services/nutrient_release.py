"""Build an importable nutrient release from reviewed INFOODS candidates."""

from __future__ import annotations

import json
from pathlib import Path

SOURCE_ID = "SOURCE:FAO_INFOODS_TAGNAMES"
SOURCE_URL = "https://www.fao.org/infoods/infoods/standards-guidelines/food-component-identifiers-tagnames/en/"


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_release(candidates: list[dict], reviewed_at: str) -> tuple[list[dict], list[dict], list[dict]]:
    source = {
        "label": "Source", "id": SOURCE_ID,
        "properties": {
            "name": "FAO/INFOODS Food Component Identifiers (Tagnames)",
            "source_type": "standard", "url": SOURCE_URL,
            "source": SOURCE_ID, "source_url": SOURCE_URL,
            "reviewed_at": reviewed_at, "status": "active",
        },
    }
    approved, relationships = [], []
    for candidate in candidates:
        nutrient = {**candidate, "properties": {**candidate["properties"], "status": "active", "reviewed_at": reviewed_at}}
        approved.append(nutrient)
        properties = nutrient["properties"]
        relationships.append({
            "start_id": nutrient["id"], "end_id": SOURCE_ID, "type": "SUPPORTED_BY",
            "properties": {"context": "nutrient-master", "source_tagname": properties["external_code"]},
        })
    return [source, *approved], relationships, approved
