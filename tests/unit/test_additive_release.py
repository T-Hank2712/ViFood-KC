import pytest

from food_kg.services.additive_release import build_release


def test_build_release_creates_functions_and_aliases() -> None:
    candidates = [{"label": "Additive", "id": "ADDITIVE:INS_621", "functional_classes": ["Chất điều vị"], "properties": {
        "name": "Monosodium L-glutamate", "name_vi": "Bột ngọt", "ins": "621",
    }}]
    nodes, relationships, approved = build_release(candidates, "2026-06-22")
    assert approved[0]["properties"]["status"] == "active"
    assert "functional_classes" not in approved[0]["properties"]
    assert "functional_classes" not in approved[0]
    additive_nodes = [node for node in nodes if node["label"] == "Additive"]
    assert "functional_classes" not in additive_nodes[0]["properties"]
    assert "functional_classes" not in additive_nodes[0]
    assert {node["id"] for node in nodes} >= {"SOURCE:VN_VBHN_09_2024", "REGULATION:VN_VBHN_09_2024"}
    assert {rel["type"] for rel in relationships} >= {"SUPPORTED_BY", "HAS_FUNCTION", "REFERS_TO", "GOVERNS"}
    aliases = [node for node in nodes if node["label"] == "Alias"]
    assert [alias["properties"]["name"] for alias in aliases] == ["E621"]


def test_rejects_ambiguous_aliases() -> None:
    candidate = {"label": "Additive", "id": "ADDITIVE:INS_621", "functional_classes": [], "properties": {"name": "x", "name_vi": "x", "ins": "621"}}
    with pytest.raises(ValueError, match="Ambiguous"):
        build_release([candidate, {"label": "Additive", "id": "ADDITIVE:INS_621_DUPLICATE", "functional_classes": [], "properties": {"name": "y", "name_vi": "y", "ins": "621"}}], "2026-06-22")
