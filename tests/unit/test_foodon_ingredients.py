from food_kg.transformers.foodon_ingredients import build_candidates


def record(identifier: str, label: str, parents=None, synonyms=None) -> dict:
    return {"source_foodon_id": identifier, "source_iri": "https://example.test/" + identifier,
            "label": label, "definition": None, "parent_foodon_ids": parents or [], "synonyms": synonyms or []}


def test_builds_ingredient_hierarchy_and_holds_ambiguous_aliases() -> None:
    records = {
        "FOODON:1": record("FOODON:1", "flour"),
        "FOODON:2": record("FOODON:2", "wheat flour", ["FOODON:1"], ["plain flour"]),
        "FOODON:3": record("FOODON:3", "rice flour", ["FOODON:1"], ["plain flour"]),
        "FOODON:4": record("FOODON:4", "obsolete: old flour", ["FOODON:1"]),
    }
    scope = {"include_descendants": True, "roots": [{"id": "FOODON:1", "ingredient_group": "flour"}], "exclude_label_regex": ["^obsolete:"]}
    nodes, relationships, aliases, ambiguous = build_candidates(records, scope, "2026-06-25")
    assert len([node for node in nodes if node["label"] == "Ingredient"]) == 3
    assert len([node for node in nodes if node["label"] == "IngredientGroup"]) == 1
    assert any(item["type"] == "IS_A" and item["start_id"] == "INGREDIENT:FOODON_2" and item["end_id"] == "INGREDIENT:FOODON_1" for item in relationships)
    assert any(item["type"] == "IN_GROUP" and item["start_id"] == "INGREDIENT:FOODON_2" and item["end_id"] == "INGREDIENT_GROUP:FLOUR" for item in relationships)
    assert aliases == []
    assert ambiguous == [{"normalized_name": "plain flour", "targets": ["INGREDIENT:FOODON_2", "INGREDIENT:FOODON_3"]}]
