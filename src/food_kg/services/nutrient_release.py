"""Build an importable nutrient release from reviewed INFOODS candidates."""

from __future__ import annotations

import json
from pathlib import Path

SOURCE_ID = "SOURCE:FAO_INFOODS_TAGNAMES"
SOURCE_URL = "https://www.fao.org/infoods/infoods/standards-guidelines/food-component-identifiers-tagnames/en/"
VIETNAM_FCT_SOURCE_ID = "SOURCE:VN_SMILING_FCT_2013"
VIETNAM_FCT_SOURCE_URL = "https://www.fao.org/fileadmin/templates/food_composition/documents/FCT_SMILING_PROJECT_ASIA/D3_5a_SMILING_FCT_Vietnam_180713_protected.xlsx"
VIETNAM_LABELING_SOURCE_ID = "SOURCE:VN_TT29_2023"
VIETNAM_LABELING_SOURCE_URL = "https://vfa.gov.vn/van-ban/tai-tep-158f3069a435b314a80bdcb024f8e422.html"


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
    includes_vietnam_fct = any(
        candidate["properties"].get("vietnam_presence_source") == VIETNAM_FCT_SOURCE_ID
        for candidate in candidates
    )
    vietnam_fct_source = {
        "label": "Source", "id": VIETNAM_FCT_SOURCE_ID,
        "properties": {
            "name": "SMILING Food Composition Table for Vietnam (2013)",
            "source_type": "food-composition-table", "url": VIETNAM_FCT_SOURCE_URL,
            "source": VIETNAM_FCT_SOURCE_ID, "source_url": VIETNAM_FCT_SOURCE_URL,
            "reviewed_at": reviewed_at, "status": "active",
        },
    }
    includes_vietnam_labeling = any(
        candidate["properties"].get("vietnam_labeling_source") == VIETNAM_LABELING_SOURCE_ID
        for candidate in candidates
    )
    vietnam_labeling_source = {
        "label": "Source", "id": VIETNAM_LABELING_SOURCE_ID,
        "properties": {
            "name": "Thông tư 29/2023/TT-BYT về ghi thành phần, giá trị dinh dưỡng trên nhãn thực phẩm",
            "source_type": "regulation", "url": VIETNAM_LABELING_SOURCE_URL,
            "source": VIETNAM_LABELING_SOURCE_ID, "source_url": VIETNAM_LABELING_SOURCE_URL,
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
        if properties.get("vietnam_presence_source") == VIETNAM_FCT_SOURCE_ID:
            relationships.append({
                "start_id": nutrient["id"], "end_id": VIETNAM_FCT_SOURCE_ID, "type": "SUPPORTED_BY",
                "properties": {
                    "context": "vietnam-food-composition-presence",
                    "source_columns": properties["vietnam_fct_columns"],
                    "food_records_with_value": properties["vietnam_fct_value_count"],
                },
            })
        if properties.get("vietnam_labeling_source") == VIETNAM_LABELING_SOURCE_ID:
            relationships.append({
                "start_id": nutrient["id"], "end_id": VIETNAM_LABELING_SOURCE_ID, "type": "SUPPORTED_BY",
                "properties": {
                    "context": "vietnam-nutrition-labelling",
                    "requirement": properties["vietnam_label_requirement"],
                    "legal_reference": properties["vietnam_legal_reference"],
                    "source_page": properties["vietnam_labeling_source_page"],
                },
            })
    sources = [
        source,
        *([vietnam_fct_source] if includes_vietnam_fct else []),
        *([vietnam_labeling_source] if includes_vietnam_labeling else []),
    ]
    return [*sources, *approved], relationships, approved
