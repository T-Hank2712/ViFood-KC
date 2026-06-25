"""Promote FoodOn Ingredient candidates into a curated release."""

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


def normalized(value: str) -> str:
    return " ".join(value.casefold().split())


def apply_translation_seed(ingredients: list[dict], seed: dict | None) -> tuple[list[dict], list[dict], list[dict]]:
    if not seed:
        return ingredients, [], []
    by_foodon_id = {ingredient["properties"]["foodon_id"]: ingredient["id"] for ingredient in ingredients}
    unknown = sorted({item["foodon_id"] for item in seed.get("translations", [])} - by_foodon_id.keys())
    if unknown:
        raise ValueError(f"Translation seed targets unknown ingredients: {', '.join(unknown)}")
    patches = {item["foodon_id"]: item for item in seed.get("translations", [])}
    translated: list[dict] = []
    aliases: list[dict] = []
    relationships: list[dict] = []
    alias_index = 0
    for ingredient in ingredients:
        foodon_id = ingredient["properties"]["foodon_id"]
        patch = patches.get(foodon_id)
        if patch:
            ingredient = {**ingredient, "properties": {**ingredient["properties"], "name_vi": patch["name_vi"]}}
            canonical_names = {normalized(ingredient["properties"]["name"]), normalized(patch["name_vi"])}
            for alias_name in patch.get("aliases", []):
                if normalized(alias_name) in canonical_names:
                    continue
                alias_index += 1
                alias_id = f"ALIAS:INGREDIENT_VI_{alias_index:04d}"
                aliases.append({
                    "label": "Alias", "id": alias_id,
                    "properties": {
                        "name": alias_name, "normalized_name": normalized(alias_name),
                        "language": "vi", "alias_type": "translation_alias",
                        "source": TRANSLATION_SOURCE_ID, "source_url": TRANSLATION_SOURCE_URL,
                    },
                })
                relationships.append({"start_id": alias_id, "end_id": ingredient["id"], "type": "REFERS_TO", "properties": {"source": TRANSLATION_SOURCE_ID}})
        translated.append(ingredient)
    return translated, aliases, relationships


def remove_canonical_aliases(ingredients: list[dict], aliases: list[dict], relationships: list[dict]) -> tuple[list[dict], list[dict]]:
    names_by_ingredient = {
        ingredient["id"]: {normalized(str(value)) for value in (ingredient["properties"].get("name"), ingredient["properties"].get("name_vi")) if value}
        for ingredient in ingredients
    }
    targets_by_alias: dict[str, set[str]] = {}
    for relationship in relationships:
        if relationship["type"] == "REFERS_TO":
            targets_by_alias.setdefault(relationship["start_id"], set()).add(relationship["end_id"])
    removed_ids = {
        alias["id"] for alias in aliases
        if any(normalized(alias["properties"].get("name", "")) in names_by_ingredient.get(target, set()) for target in targets_by_alias.get(alias["id"], set()))
    }
    return ([alias for alias in aliases if alias["id"] not in removed_ids], [relationship for relationship in relationships if relationship["start_id"] not in removed_ids])


def build_release(ingredients: list[dict], aliases: list[dict], relationships: list[dict], reviewed_at: str, translation_seed: dict | None = None) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    source = {"label": "Source", "id": SOURCE_ID, "properties": {"name": "FoodOn Food Ontology", "source_type": "standard", "url": SOURCE_URL, "source": SOURCE_ID, "source_url": SOURCE_URL, "reviewed_at": reviewed_at, "status": "active"}}
    translation_source = {"label": "Source", "id": TRANSLATION_SOURCE_ID, "properties": {"name": "ViFood-KG Vietnamese translation seed", "source_type": "internal-curation", "url": TRANSLATION_SOURCE_URL, "source": TRANSLATION_SOURCE_ID, "source_url": TRANSLATION_SOURCE_URL, "reviewed_at": reviewed_at, "status": "active"}}
    ingredient_nodes = [node for node in ingredients if node["label"] == "Ingredient"]
    other_nodes = [node for node in ingredients if node["label"] != "Ingredient"]
    ingredient_nodes, translation_aliases, translation_relationships = apply_translation_seed(ingredient_nodes, translation_seed)
    ingredients = [*other_nodes, *ingredient_nodes]
    aliases = [*aliases, *translation_aliases]
    relationships = [*relationships, *translation_relationships]
    aliases, relationships = remove_canonical_aliases(ingredients, aliases, relationships)
    approved_ingredients, approved_aliases = activate(ingredients, reviewed_at), activate(aliases, reviewed_at)
    support_relationships = []
    for node in approved_ingredients:
        context = "packaged-food-ingredient" if node["label"] == "Ingredient" else "packaged-food-ingredient-group"
        properties = {"context": context}
        if node["label"] == "Ingredient":
            properties["foodon_id"] = node["properties"]["foodon_id"]
        if node["label"] == "IngredientGroup":
            properties["code"] = node["properties"]["code"]
        support_relationships.append({"start_id": node["id"], "end_id": SOURCE_ID, "type": "SUPPORTED_BY", "properties": properties})
    return [source, translation_source, *approved_ingredients, *approved_aliases], [*relationships, *support_relationships], approved_ingredients, approved_aliases
