from food_kg.services.foodon_release import build_release


def test_build_release_connects_category_to_source() -> None:
    categories = [{"label": "FoodCategory", "id": "CATEGORY:FOODON_1", "properties": {"name": "snack", "foodon_id": "FOODON:1", "source": "SOURCE:FOODON", "source_url": "https://example.test", "reviewed_at": "2026-06-22", "status": "draft"}}]
    aliases = [{"label": "Alias", "id": "ALIAS:SNACK", "properties": {"name": "snack", "source": "SOURCE:FOODON", "source_url": "https://example.test", "reviewed_at": "2026-06-22", "status": "draft"}}]
    relationships = [{"start_id": "ALIAS:SNACK", "end_id": "CATEGORY:FOODON_1", "type": "REFERS_TO", "properties": {}}]
    patches = [{"id": "CATEGORY:FOODON_1", "properties": {"name_vi": "Đồ ăn nhẹ"}}]
    nodes, release_relationships, approved_categories, approved_aliases = build_release(categories, aliases, relationships, "2026-06-22", patches)
    assert nodes[0]["id"] == "SOURCE:FOODON"
    assert approved_categories[0]["properties"]["status"] == "active"
    assert approved_categories[0]["properties"]["name_vi"] == "Đồ ăn nhẹ"
    assert approved_aliases[0]["properties"]["status"] == "active"
    assert any(item["type"] == "SUPPORTED_BY" for item in release_relationships)
