"""Build an importable nutrient release from reviewed INFOODS candidates."""

from __future__ import annotations

import json
import re
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
    approved, aliases, relationships = [], [], []
    for candidate in candidates:
        nutrient = {**candidate, "properties": {**candidate["properties"], "status": "active", "reviewed_at": reviewed_at}}
        approved.append(nutrient)
        properties = nutrient["properties"]
        relationships.append({
            "start_id": nutrient["id"], "end_id": SOURCE_ID, "type": "SUPPORTED_BY",
            "properties": {"context": "nutrient-master", "source_tagname": properties["external_code"]},
        })
        alias_specs = [("INFOODS_" + properties["external_code"], properties["external_code"], "abbreviation", "en")]
        if properties["name_vi"].casefold() != properties["name"].casefold():
            alias_specs.append((nutrient["id"].split(":", 1)[1] + "_VI", properties["name_vi"], "common-name", "vi"))
        for suffix, name, alias_type, language in alias_specs:
            alias_id = "ALIAS:" + re.sub(r"[^A-Z0-9_]", "_", suffix.upper())
            aliases.append({
                "label": "Alias", "id": alias_id,
                "properties": {
                    "name": name, "normalized_name": " ".join(name.lower().split()),
                    "language": language, "alias_type": alias_type,
                    "source": SOURCE_ID, "source_url": SOURCE_URL,
                    "reviewed_at": reviewed_at, "status": "active",
                },
            })
            relationships.append({
                "start_id": alias_id, "end_id": nutrient["id"], "type": "REFERS_TO",
                "properties": {"source": SOURCE_ID},
            })
    return [source, *approved, *aliases], relationships, approved
