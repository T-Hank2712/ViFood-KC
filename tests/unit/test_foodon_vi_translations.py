from food_kg.transformers.foodon_vi_translations import build_candidates


def test_builds_vietnamese_name_patch_and_alias() -> None:
    categories = [{"label": "FoodCategory", "id": "CATEGORY:FOODON_1", "properties": {"name": "instant noodle", "foodon_id": "FOODON:1", "source": "SOURCE:FOODON", "source_url": "https://example.test"}}]
    translations = {"source_id": "SOURCE:VIFOOD_TRANSLATION_SEED", "source_url": "internal://test", "translations": [{"foodon_id": "FOODON:1", "name_vi": "Mì ăn liền", "aliases": ["mì gói"]}]}
    patches, aliases, relationships = build_candidates(categories, translations, "2026-06-22")
    assert patches[0]["properties"]["name_vi"] == "Mì ăn liền"
    assert [item["properties"]["name"] for item in aliases] == ["Mì ăn liền", "mì gói"]
    assert len(relationships) == 2
