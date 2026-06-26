from food_kg.transformers.chebi_chemical_ingredients import build_release


def test_builds_chebi_chemical_ingredient_release() -> None:
    records = {"CHEBI:1": {"chebi_id": "CHEBI:1", "name": "glucose", "molecular_formula": "C6H12O6", "source_url": "https://example.test/CHEBI:1"}}
    scope = {
        "groups": {"chemical_sugar": {"name": "Chemical sugar ingredients", "name_vi": "Nguyên liệu đường dạng hóa chất"}},
        "chemicals": [{"chebi_id": "CHEBI:1", "name_vi": "Glucose", "group": "chemical_sugar", "aliases": ["đường glucose", "glucose"]}],
    }
    nodes, relationships = build_release(records, scope, "2026-06-25")
    assert any(node["label"] == "Ingredient" and node["properties"]["chebi_id"] == "CHEBI:1" for node in nodes)
    assert any(node["label"] == "IngredientGroup" and node["id"] == "INGREDIENT_GROUP:CHEMICAL_SUGAR" for node in nodes)
    assert any(relationship["type"] == "IN_GROUP" for relationship in relationships)
    assert not any(node["label"] == "Alias" and node["properties"]["name"] == "glucose" for node in nodes)
