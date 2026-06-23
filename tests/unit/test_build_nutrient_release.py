from food_kg.services.nutrient_release import build_release


def test_build_release_includes_source_without_redundant_external_code_alias() -> None:
    candidates = [{"label": "Nutrient", "id": "NUTRIENT:SODIUM", "properties": {
        "name": "Sodium", "name_vi": "Natri", "external_code": "NA",
        "source": "SOURCE:FAO_INFOODS_TAGNAMES", "source_url": "https://example.test",
        "reviewed_at": "2026-06-22", "status": "draft",
    }}]
    nodes, relationships, approved = build_release(candidates, "2026-06-22")
    assert nodes[0]["id"] == "SOURCE:FAO_INFOODS_TAGNAMES"
    assert approved[0]["properties"]["status"] == "active"
    assert not [item for item in nodes if item["label"] == "Alias"]
    assert len(relationships) == 1
    assert any(item["type"] == "SUPPORTED_BY" for item in relationships)
