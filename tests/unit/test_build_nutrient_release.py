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


def test_build_release_adds_vietnam_fct_provenance_for_exactly_matched_candidates() -> None:
    candidates = [{"label": "Nutrient", "id": "NUTRIENT:INFOODS_PROCNT", "properties": {
        "name": "protein", "external_code": "PROCNT", "source": "SOURCE:FAO_INFOODS_TAGNAMES",
        "source_url": "https://example.test", "vietnam_presence_source": "SOURCE:VN_SMILING_FCT_2013",
        "vietnam_fct_columns": ["PROTCNT(g)"], "vietnam_fct_value_count": 165,
        "reviewed_at": "2026-06-24", "status": "draft",
    }}]
    nodes, relationships, _ = build_release(candidates, "2026-06-24")
    assert {node["id"] for node in nodes if node["label"] == "Source"} == {
        "SOURCE:FAO_INFOODS_TAGNAMES", "SOURCE:VN_SMILING_FCT_2013",
    }
    assert {relation["end_id"] for relation in relationships} == {
        "SOURCE:FAO_INFOODS_TAGNAMES", "SOURCE:VN_SMILING_FCT_2013",
    }


def test_build_release_adds_vietnam_labelling_provenance() -> None:
    candidates = [{"label": "Nutrient", "id": "NUTRIENT:INFOODS_NA", "properties": {
        "name": "sodium", "name_vi": "Natri", "external_code": "NA", "source": "SOURCE:FAO_INFOODS_TAGNAMES",
        "source_url": "https://example.test", "vietnam_labeling_source": "SOURCE:VN_TT29_2023",
        "vietnam_label_requirement": "required", "vietnam_legal_reference": "Điều 5 khoản 1 điểm đ",
        "vietnam_labeling_source_page": 4, "reviewed_at": "2026-06-24", "status": "draft",
    }}]
    nodes, relationships, _ = build_release(candidates, "2026-06-24")
    assert any(node["id"] == "SOURCE:VN_TT29_2023" for node in nodes)
    assert relationships[-1]["end_id"] == "SOURCE:VN_TT29_2023"
