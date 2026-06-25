"""Create Ingredient, hierarchy and alias candidates from FoodOn staging."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict, deque
from datetime import UTC, datetime
from pathlib import Path

import yaml

SOURCE_ID = "SOURCE:FOODON"
SOURCE_URL = "https://github.com/FoodOntology/foodon"
GROUP_LABELS = {
    "cacao": ("Cacao ingredients", "Nguyên liệu cacao"),
    "cereal_flour": ("Cereal flour ingredients", "Nguyên liệu bột ngũ cốc"),
    "cereal_grain": ("Cereal grain ingredients", "Nguyên liệu ngũ cốc"),
    "coffee_tea": ("Coffee and tea ingredients", "Nguyên liệu cà phê và trà"),
    "dairy": ("Dairy ingredients", "Nguyên liệu sữa"),
    "fruit_juice": ("Fruit juice ingredients", "Nguyên liệu nước trái cây"),
    "nut_seed_legume": ("Nut, seed and legume ingredients", "Nguyên liệu hạt và đậu"),
    "oil_fat": ("Oil and fat ingredients", "Nguyên liệu dầu và chất béo"),
    "starch": ("Starch ingredients", "Nguyên liệu tinh bột"),
    "sweetener": ("Sweetener ingredients", "Nguyên liệu tạo ngọt"),
    "water_mineral": ("Water and mineral ingredients", "Nguyên liệu nước và khoáng"),
}


def ingredient_id(foodon_id: str) -> str:
    return "INGREDIENT:" + foodon_id.replace(":", "_")


def group_id(group: str) -> str:
    return "INGREDIENT_GROUP:" + re.sub(r"[^A-Z0-9_]", "_", group.upper())


def normalized(value: str) -> str:
    return " ".join(value.casefold().split())


def load_records(path: Path) -> dict[str, dict]:
    return {record["source_foodon_id"]: record for line in path.read_text(encoding="utf-8").splitlines() if (record := json.loads(line))}


def _children(records: dict[str, dict]) -> dict[str, set[str]]:
    children: dict[str, set[str]] = defaultdict(set)
    for record in records.values():
        for parent in record["parent_foodon_ids"]:
            children[parent].add(record["source_foodon_id"])
    return children


def selected_ids(records: dict[str, dict], roots: list[dict], include_descendants: bool) -> set[str]:
    children = _children(records)
    selected: set[str] = set()
    queue = deque((root["id"], 0, root.get("max_depth")) for root in roots)
    while queue:
        identifier, depth, max_depth = queue.popleft()
        if identifier in selected:
            continue
        selected.add(identifier)
        if max_depth is None:
            max_depth = 999 if include_descendants else 0
        if depth >= max_depth:
            continue
        for child in sorted(children[identifier]):
            if child not in selected:
                queue.append((child, depth + 1, max_depth))
    return selected


def _root_groups(records: dict[str, dict], roots: list[dict], include_descendants: bool) -> dict[str, set[str]]:
    groups: dict[str, set[str]] = defaultdict(set)
    children = _children(records)
    for root in roots:
        group = root.get("ingredient_group", "general")
        queue = deque([(root["id"], 0, root.get("max_depth"))])
        while queue:
            identifier, depth, max_depth = queue.popleft()
            groups[identifier].add(group)
            if max_depth is None:
                max_depth = 999 if include_descendants else 0
            if depth >= max_depth:
                continue
            for child in sorted(children[identifier]):
                queue.append((child, depth + 1, max_depth))
    return groups


def _excluded(record: dict, patterns: list[re.Pattern[str]]) -> bool:
    label = record["label"]
    return any(pattern.search(label) for pattern in patterns)


def build_candidates(records: dict[str, dict], scope: dict, reviewed_at: str) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    roots = scope["roots"]
    missing = sorted({item["id"] for item in roots} - records.keys())
    if missing:
        raise ValueError(f"Scope roots missing from FoodOn staging: {', '.join(missing)}")
    patterns = [re.compile(pattern, re.IGNORECASE) for pattern in scope.get("exclude_label_regex", [])]
    selected = selected_ids(records, roots, scope.get("include_descendants", False))
    selected = {identifier for identifier in selected if not _excluded(records[identifier], patterns)}
    groups_by_id = _root_groups(records, roots, scope.get("include_descendants", False))
    nodes: list[dict] = []
    relationships: list[dict] = []
    alias_candidates: list[dict] = []
    alias_targets: dict[str, list[tuple[str, str]]] = defaultdict(list)
    all_groups = sorted({group for identifier in selected for group in groups_by_id.get(identifier, {"general"})})
    for group in all_groups:
        name, name_vi = GROUP_LABELS.get(group, (group.replace("_", " ").title(), group.replace("_", " ")))
        nodes.append({
            "label": "IngredientGroup", "id": group_id(group),
            "properties": {
                "name": name, "name_vi": name_vi, "code": group,
                "source": SOURCE_ID, "source_url": SOURCE_URL,
                "reviewed_at": reviewed_at, "status": "draft",
            },
        })
    for identifier in sorted(selected):
        record = records[identifier]
        node_id = ingredient_id(identifier)
        groups = sorted(groups_by_id.get(identifier, {"general"}))
        nodes.append({
            "label": "Ingredient", "id": node_id,
            "properties": {
                "name": record["label"], "foodon_id": identifier,
                "external_code": identifier, "source_iri": record["source_iri"],
                "description": record["definition"],
                "source": SOURCE_ID, "source_url": SOURCE_URL,
                "reviewed_at": reviewed_at, "status": "draft",
            },
        })
        for group in groups:
            relationships.append({
                "start_id": node_id, "end_id": group_id(group), "type": "IN_GROUP",
                "properties": {"source": SOURCE_ID, "scope_file": "config/foodon_ingredient_scope.yaml"},
            })
        for parent in record["parent_foodon_ids"]:
            if parent in selected:
                relationships.append({
                    "start_id": node_id, "end_id": ingredient_id(parent), "type": "IS_A",
                    "properties": {"source": SOURCE_ID, "source_relation": "rdfs:subClassOf"},
                })
        for synonym in record["synonyms"]:
            if normalized(synonym) != normalized(record["label"]):
                alias_targets[normalized(synonym)].append((synonym, node_id))
    ambiguous: list[dict] = []
    for alias_key, targets in sorted(alias_targets.items()):
        unique_targets = {target for _, target in targets}
        if len(unique_targets) > 1:
            ambiguous.append({"normalized_name": alias_key, "targets": sorted(unique_targets)})
            continue
        alias_name, target = targets[0]
        suffix = re.sub(r"[^A-Z0-9_]", "_", target.split(":", 1)[1] + "_" + str(len(alias_candidates) + 1))
        alias_id = "ALIAS:" + suffix
        alias_candidates.append({
            "label": "Alias", "id": alias_id,
            "properties": {
                "name": alias_name, "normalized_name": alias_key, "language": "en",
                "alias_type": "synonym", "source": SOURCE_ID, "source_url": SOURCE_URL,
                "reviewed_at": reviewed_at, "status": "draft",
            },
        })
        relationships.append({
            "start_id": alias_id, "end_id": target, "type": "REFERS_TO",
            "properties": {"source": SOURCE_ID},
        })
    return nodes, relationships, alias_candidates, ambiguous


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build FoodOn Ingredient candidates for packaged-food knowledge core")
    parser.add_argument("--staging", type=Path, required=True)
    parser.add_argument("--scope", type=Path, required=True)
    parser.add_argument("--nodes-output", type=Path, required=True)
    parser.add_argument("--relationships-output", type=Path, required=True)
    parser.add_argument("--aliases-output", type=Path, required=True)
    parser.add_argument("--ambiguous-output", type=Path, required=True)
    parser.add_argument("--reviewed-at", default=datetime.now(UTC).date().isoformat())
    args = parser.parse_args()
    records = load_records(args.staging)
    scope = yaml.safe_load(args.scope.read_text(encoding="utf-8"))
    nodes, relationships, aliases, ambiguous = build_candidates(records, scope, args.reviewed_at)
    write_json(args.nodes_output, nodes)
    write_json(args.relationships_output, relationships)
    write_json(args.aliases_output, aliases)
    write_json(args.ambiguous_output, ambiguous)
    print(f"Created {len(nodes)} Ingredient candidates, {len(aliases)} alias candidates, {len(relationships)} relationships; {len(ambiguous)} ambiguous aliases need review.")


if __name__ == "__main__":
    main()
