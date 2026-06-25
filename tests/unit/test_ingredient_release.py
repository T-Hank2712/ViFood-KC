from food_kg.services.ingredient_release import build_release


def test_build_release_adds_translation_and_removes_canonical_alias() -> None:
    ingredients = [{"label": "Ingredient", "id": "INGREDIENT:FOODON_1", "properties": {"name": "wheat flour", "foodon_id": "FOODON:1", "source": "SOURCE:FOODON", "source_url": "https://example.test", "reviewed_at": "2026-06-25", "status": "draft"}}]
    aliases = [{"label": "Alias", "id": "ALIAS:WHEAT_FLOUR", "properties": {"name": "wheat flour", "source": "SOURCE:FOODON", "source_url": "https://example.test"}}]
    relationships = [{"start_id": "ALIAS:WHEAT_FLOUR", "end_id": "INGREDIENT:FOODON_1", "type": "REFERS_TO", "properties": {}}]
    seed = {"translations": [{"foodon_id": "FOODON:1", "name_vi": "Bột mì", "aliases": ["bột lúa mì", "Bột mì"]}]}
    nodes, release_relationships, approved_ingredients, approved_aliases = build_release(ingredients, aliases, relationships, "2026-06-25", seed)
    assert nodes[0]["id"] == "SOURCE:FOODON"
    assert approved_ingredients[0]["properties"]["name_vi"] == "Bột mì"
    assert {alias["properties"]["name"] for alias in approved_aliases} == {"bột lúa mì"}
    assert any(item["type"] == "SUPPORTED_BY" for item in release_relationships)
