"""Build a provenance-complete additive release from Vietnam's official regulation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

SOURCE_ID = "SOURCE:VN_VBHN_09_2024"
SOURCE_URL = "https://datafiles.chinhphu.vn/cpp/files/vbpq/2024/9/09-vbhn-byt.pdf"
REGULATION_ID = "REGULATION:VN_VBHN_09_2024"


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def stable_id(prefix: str, value: str) -> str:
    return prefix + hashlib.sha256(value.casefold().encode("utf-8")).hexdigest()[:16].upper()


def build_release(candidates: list[dict], reviewed_at: str) -> tuple[list[dict], list[dict], list[dict]]:
    source = {"label": "Source", "id": SOURCE_ID, "properties": {
        "name": "Văn bản hợp nhất 09/VBHN-BYT (2024)", "source_type": "government_regulation",
        "url": SOURCE_URL, "source": SOURCE_ID, "source_url": SOURCE_URL,
        "reviewed_at": reviewed_at, "status": "active",
    }}
    regulation = {"label": "Regulation", "id": REGULATION_ID, "properties": {
        "name": "Quy định về quản lý và sử dụng phụ gia thực phẩm", "document_number": "09/VBHN-BYT",
        "issued_on": "2024-09-06", "source": SOURCE_ID, "source_url": SOURCE_URL,
        "reviewed_at": reviewed_at, "status": "active",
    }}
    nodes, relationships, approved = [source, regulation], [{"start_id": REGULATION_ID, "end_id": SOURCE_ID, "type": "SUPPORTED_BY", "properties": {"context": "official-consolidated-text"}}], []
    functional_classes: dict[str, dict] = {}
    alias_target: dict[str, str] = {}
    alias_ids: set[str] = set()
    for candidate in candidates:
        additive = {**candidate, "properties": {**candidate["properties"], "status": "active", "reviewed_at": reviewed_at}}
        approved.append(additive)
        nodes.append(additive)
        properties = additive["properties"]
        relationships.extend([
            {"start_id": additive["id"], "end_id": SOURCE_ID, "type": "SUPPORTED_BY", "properties": {"context": "appendix-1", "source_ins": properties["ins"]}},
            {"start_id": REGULATION_ID, "end_id": additive["id"], "type": "GOVERNS", "properties": {"appendix": "1", "ins": properties["ins"]}},
        ])
        for class_name in properties["functional_classes"]:
            class_id = stable_id("FUNCTION:", class_name)
            functional_classes.setdefault(class_id, {"label": "FunctionalClass", "id": class_id, "properties": {
                "name": class_name, "language": "vi", "source": SOURCE_ID, "source_url": SOURCE_URL,
                "reviewed_at": reviewed_at, "status": "active",
            }})
            relationships.append({"start_id": additive["id"], "end_id": class_id, "type": "HAS_FUNCTION", "properties": {"source": SOURCE_ID}})
        # ins is a canonical Additive property.  Keep only the E-number form
        # because it is a distinct token commonly observed on product labels.
        aliases = []
        if not properties["ins"].upper().startswith("E"):
            aliases.append(("E" + properties["ins"], "e-number", "und"))
        for name, alias_type, language in aliases:
            normalized = " ".join(name.casefold().split())
            previous_target = alias_target.setdefault(normalized, additive["id"])
            if previous_target != additive["id"]:
                raise ValueError(f"Ambiguous additive alias in regulation: {name}")
            alias_id = stable_id("ALIAS:ADDITIVE_", normalized)
            if alias_id in alias_ids:
                continue
            alias_ids.add(alias_id)
            nodes.append({"label": "Alias", "id": alias_id, "properties": {
                "name": name, "normalized_name": normalized, "language": language, "alias_type": alias_type,
                "source": SOURCE_ID, "source_url": SOURCE_URL, "reviewed_at": reviewed_at, "status": "active",
            }})
            relationships.append({"start_id": alias_id, "end_id": additive["id"], "type": "REFERS_TO", "properties": {"source": SOURCE_ID}})
    nodes.extend(functional_classes.values())
    return nodes, relationships, approved
