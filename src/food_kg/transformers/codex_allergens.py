"""Build Codex-backed Allergen master release records."""

from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path

import yaml

CODEX_SOURCE_ID = "SOURCE:CODEX_CXS_1_1985"
SOURCE_URL = "https://www.fao.org/fao-who-codexalimentarius/sh-proxy/en/?lnk=1&url=https%253A%252F%252Fworkspace.fao.org%252Fsites%252Fcodex%252FStandards%252FCXS%2B1-1985%252FCXS_001e.pdf"


def normalized(value: str) -> str:
    return " ".join(value.casefold().split())


def allergen_id(code: str) -> str:
    return "ALLERGEN:" + re.sub(r"[^A-Z0-9_]", "_", code.upper())


def alias_id(code: str, index: int) -> str:
    return f"ALIAS:ALLERGEN_{re.sub(r'[^A-Z0-9_]', '_', code.upper())}_{index:02d}"


def detect_language(value: str) -> str:
    return "vi" if re.search(r"[àáạảãăằắặẳẵâầấậẩẫđèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]", value.casefold()) else "en"


def load_staging(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def build_release(records: list[dict], reviewed_at: str) -> tuple[list[dict], list[dict]]:
    source = {
        "label": "Source",
        "id": CODEX_SOURCE_ID,
        "properties": {
            "name": "Codex General Standard for the Labelling of Prepackaged Foods",
            "source_type": "standard",
            "url": SOURCE_URL,
            "source": CODEX_SOURCE_ID,
            "source_url": SOURCE_URL,
            "reviewed_at": reviewed_at,
            "status": "active",
        },
    }
    nodes: list[dict] = [source]
    relationships: list[dict] = []
    alias_targets: dict[str, str] = {}
    seen_allergens: set[str] = set()
    for record in sorted(records, key=lambda item: item["allergen_code"]):
        node_id = allergen_id(record["allergen_code"])
        if node_id in seen_allergens:
            raise ValueError(f"Duplicate Codex allergen code: {record['allergen_code']}")
        seen_allergens.add(node_id)
        properties = {
            "name": record["name"],
            "name_vi": record["name_vi"],
            "external_code": record["allergen_code"],
            "category_type": record["category_type"],
            "codex_standard": record["standard_code"],
            "codex_section": record["source_section"],
            "codex_text": record["codex_text"],
            "examples": record.get("examples", []),
            "examples_vi": record.get("examples_vi", []),
            "source": CODEX_SOURCE_ID,
            "source_url": record["source_url"],
            "reviewed_at": reviewed_at,
            "status": "active",
        }
        if record.get("threshold"):
            properties["threshold"] = record["threshold"]
        nodes.append({"label": "Allergen", "id": node_id, "properties": properties})
        relationships.append({
            "start_id": node_id,
            "end_id": CODEX_SOURCE_ID,
            "type": "SUPPORTED_BY",
            "properties": {"context": "codex-allergen-master", "codex_section": record["source_section"]},
        })
        canonical = {normalized(record["name"]), normalized(record["name_vi"]), normalized(record["allergen_code"])}
        alias_index = 1
        for alias in record.get("aliases", []):
            alias_key = normalized(alias)
            if alias_key in canonical:
                continue
            previous_target = alias_targets.setdefault(alias_key, node_id)
            if previous_target != node_id:
                raise ValueError(f"Ambiguous allergen alias: {alias}")
            aid = alias_id(record["allergen_code"], alias_index)
            alias_index += 1
            nodes.append({
                "label": "Alias",
                "id": aid,
                "properties": {
                    "name": alias,
                    "normalized_name": alias_key,
                    "language": detect_language(alias),
                    "alias_type": "allergen_alias",
                    "source": CODEX_SOURCE_ID,
                    "source_url": record["source_url"],
                    "reviewed_at": reviewed_at,
                    "status": "active",
                },
            })
            relationships.append({"start_id": aid, "end_id": node_id, "type": "REFERS_TO", "properties": {"source": CODEX_SOURCE_ID}})
    return nodes, relationships


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Codex allergen curated release")
    parser.add_argument("--staging", type=Path, required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--reviewed-at", default=datetime.now(UTC).date().isoformat())
    parser.add_argument("--nodes-output", type=Path, required=True)
    parser.add_argument("--relationships-output", type=Path, required=True)
    parser.add_argument("--release-output", type=Path, required=True)
    args = parser.parse_args()
    nodes, relationships = build_release(load_staging(args.staging), args.reviewed_at)
    write_json(args.nodes_output, nodes)
    write_json(args.relationships_output, relationships)
    args.release_output.parent.mkdir(parents=True, exist_ok=True)
    args.release_output.write_text(yaml.safe_dump({
        "version": args.version,
        "released_at": args.reviewed_at,
        "source_ids": [CODEX_SOURCE_ID],
        "node_count": len(nodes),
        "relationship_count": len(relationships),
        "notes": "Codex CXS 1-1985 allergen master for prepackaged-food label interpretation.",
    }, allow_unicode=True, sort_keys=False), encoding="utf-8")
    print(f"Built {args.version}: {len(nodes)} nodes, {len(relationships)} relationships")


if __name__ == "__main__":
    main()
