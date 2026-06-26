"""Build ChEBI-backed chemical Ingredient release records."""

from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path

import yaml

CHEBI_SOURCE_ID = "SOURCE:CHEBI"
CHEBI_SOURCE_URL = "https://www.ebi.ac.uk/chebi/"
INTERNAL_SOURCE_ID = "SOURCE:VIFOOD_TRANSLATION_SEED"
INTERNAL_SOURCE_URL = "internal://vi-food-translation-seed"


def normalized(value: str) -> str:
    return " ".join(value.casefold().split())


def ingredient_id(chebi_id: str) -> str:
    return "INGREDIENT:" + chebi_id.replace(":", "_")


def group_id(group: str) -> str:
    return "INGREDIENT_GROUP:" + re.sub(r"[^A-Z0-9_]", "_", group.upper())


def alias_id(chebi_id: str, index: int) -> str:
    return f"ALIAS:{chebi_id.replace(':', '_')}_{index:02d}"


def load_staging(path: Path) -> dict[str, dict]:
    return {record["chebi_id"]: record for line in path.read_text(encoding="utf-8").splitlines() if (record := json.loads(line))}


def build_release(records: dict[str, dict], scope: dict, reviewed_at: str) -> tuple[list[dict], list[dict]]:
    missing = sorted({item["chebi_id"] for item in scope["chemicals"]} - records.keys())
    if missing:
        raise ValueError(f"Scope chemicals missing from ChEBI staging: {', '.join(missing)}")
    source = {"label": "Source", "id": CHEBI_SOURCE_ID, "properties": {"name": "ChEBI", "source_type": "standard", "url": CHEBI_SOURCE_URL, "source": CHEBI_SOURCE_ID, "source_url": CHEBI_SOURCE_URL, "reviewed_at": reviewed_at, "status": "active"}}
    internal_source = {"label": "Source", "id": INTERNAL_SOURCE_ID, "properties": {"name": "ViFood-KG Vietnamese translation seed", "source_type": "internal-curation", "url": INTERNAL_SOURCE_URL, "source": INTERNAL_SOURCE_ID, "source_url": INTERNAL_SOURCE_URL, "reviewed_at": reviewed_at, "status": "active"}}
    nodes: list[dict] = [source, internal_source]
    relationships: list[dict] = []
    for code, group in sorted(scope.get("groups", {}).items()):
        nodes.append({
            "label": "IngredientGroup", "id": group_id(code),
            "properties": {
                "name": group["name"], "name_vi": group["name_vi"], "code": code,
                "source": INTERNAL_SOURCE_ID, "source_url": INTERNAL_SOURCE_URL,
                "reviewed_at": reviewed_at, "status": "active",
            },
        })
        relationships.append({"start_id": group_id(code), "end_id": INTERNAL_SOURCE_ID, "type": "SUPPORTED_BY", "properties": {"context": "chemical-ingredient-group", "code": code}})
    alias_targets: dict[str, str] = {}
    for item in scope["chemicals"]:
        record = records[item["chebi_id"]]
        node_id = ingredient_id(record["chebi_id"])
        nodes.append({
            "label": "Ingredient", "id": node_id,
            "properties": {
                "name": record["name"], "name_vi": item["name_vi"],
                "chebi_id": record["chebi_id"], "external_code": record["chebi_id"],
                "molecular_formula": record.get("molecular_formula"),
                "source": CHEBI_SOURCE_ID, "source_url": record["source_url"],
                "reviewed_at": reviewed_at, "status": "active",
            },
        })
        relationships.extend([
            {"start_id": node_id, "end_id": CHEBI_SOURCE_ID, "type": "SUPPORTED_BY", "properties": {"context": "chemical-ingredient", "chebi_id": record["chebi_id"]}},
            {"start_id": node_id, "end_id": group_id(item["group"]), "type": "IN_GROUP", "properties": {"source": INTERNAL_SOURCE_ID, "scope_file": "config/chebi_chemical_ingredient_scope.yaml"}},
        ])
        canonical = {normalized(record["name"]), normalized(item["name_vi"]), normalized(record["chebi_id"])}
        alias_index = 1
        for alias_name in item.get("aliases", []):
            alias_key = normalized(alias_name)
            if alias_key in canonical:
                continue
            previous_target = alias_targets.setdefault(alias_key, node_id)
            if previous_target != node_id:
                raise ValueError(f"Ambiguous ChEBI chemical alias: {alias_name}")
            aid = alias_id(record["chebi_id"], alias_index)
            alias_index += 1
            nodes.append({
                "label": "Alias", "id": aid,
                "properties": {
                    "name": alias_name, "normalized_name": alias_key,
                    "language": "vi" if re.search(r"[àáạảãăằắặẳẵâầấậẩẫđèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹ]", alias_key) else "en",
                    "alias_type": "chemical_ingredient_alias",
                    "source": INTERNAL_SOURCE_ID, "source_url": INTERNAL_SOURCE_URL,
                    "reviewed_at": reviewed_at, "status": "active",
                },
            })
            relationships.append({"start_id": aid, "end_id": node_id, "type": "REFERS_TO", "properties": {"source": INTERNAL_SOURCE_ID}})
    return nodes, relationships


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build ChEBI chemical Ingredient curated release")
    parser.add_argument("--staging", type=Path, required=True)
    parser.add_argument("--scope", type=Path, required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--reviewed-at", default=datetime.now(UTC).date().isoformat())
    parser.add_argument("--nodes-output", type=Path, required=True)
    parser.add_argument("--relationships-output", type=Path, required=True)
    parser.add_argument("--release-output", type=Path, required=True)
    args = parser.parse_args()
    nodes, relationships = build_release(load_staging(args.staging), yaml.safe_load(args.scope.read_text(encoding="utf-8")), args.reviewed_at)
    write_json(args.nodes_output, nodes)
    write_json(args.relationships_output, relationships)
    args.release_output.parent.mkdir(parents=True, exist_ok=True)
    args.release_output.write_text(yaml.safe_dump({"version": args.version, "released_at": args.reviewed_at, "source_ids": [CHEBI_SOURCE_ID, INTERNAL_SOURCE_ID], "node_count": len(nodes), "relationship_count": len(relationships), "notes": "ChEBI-backed chemical Ingredient master for scoped packaged-food label terms."}, allow_unicode=True, sort_keys=False), encoding="utf-8")
    print(f"Built {args.version}: {len(nodes)} nodes, {len(relationships)} relationships")


if __name__ == "__main__":
    main()
