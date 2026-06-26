from food_kg.extractors.codex_allergens import extract_records
from food_kg.transformers.codex_allergens import build_release


def test_extracts_codex_allergen_records() -> None:
    config = {
        "source": {"id": "SOURCE:CODEX_CXS_1_1985", "name": "Codex", "url": "https://example.test", "standard_code": "CXS 1-1985", "section": "4.2.1.4"},
        "allergens": [{"code": "MILK", "name": "Milk", "name_vi": "Sữa", "category_type": "allergen_group", "codex_text": "Milk and milk products.", "aliases": ["milk", "sữa"]}],
    }
    records = extract_records(config, "2026-06-25")
    assert records[0]["allergen_code"] == "MILK"
    assert records[0]["source_section"] == "4.2.1.4"


def test_builds_codex_allergen_release() -> None:
    records = [{
        "source_id": "SOURCE:CODEX_CXS_1_1985",
        "source_name": "Codex",
        "source_url": "https://example.test",
        "standard_code": "CXS 1-1985",
        "source_section": "4.2.1.4",
        "allergen_code": "MILK",
        "name": "Milk and milk products",
        "name_vi": "Sữa và sản phẩm từ sữa",
        "category_type": "allergen_group",
        "codex_text": "Milk and milk products, lactose included.",
        "examples": ["milk"],
        "examples_vi": ["sữa"],
        "threshold": None,
        "aliases": ["milk", "sữa", "lactose"],
    }]
    nodes, relationships = build_release(records, "2026-06-25")
    assert any(node["label"] == "Allergen" and node["id"] == "ALLERGEN:MILK" for node in nodes)
    assert any(node["label"] == "Alias" and node["properties"]["name"] == "lactose" for node in nodes)
    assert any(relationship["type"] == "SUPPORTED_BY" and relationship["start_id"] == "ALLERGEN:MILK" for relationship in relationships)
