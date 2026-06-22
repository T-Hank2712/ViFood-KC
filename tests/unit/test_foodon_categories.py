from food_kg.transformers.foodon_categories import build_candidates


def record(identifier: str, label: str, parents=None, synonyms=None) -> dict:
    return {"source_foodon_id": identifier, "source_iri": "https://example.test/" + identifier,
            "label": label, "definition": None, "parent_foodon_ids": parents or [], "synonyms": synonyms or []}


def test_builds_categories_and_marks_ambiguous_aliases_for_review() -> None:
    records = {
        "FOODON:1": record("FOODON:1", "snack food"),
        "FOODON:2": record("FOODON:2", "potato snack", ["FOODON:1"], ["crisps"]),
        "FOODON:3": record("FOODON:3", "corn snack", ["FOODON:1"], ["crisps"]),
    }
    scope = {"include_descendants": True, "roots": [{"id": "FOODON:1"}]}
    nodes, relationships, aliases, ambiguous = build_candidates(records, scope, "2026-06-22")
    assert len(nodes) == 3
    assert any(item["type"] == "BROADER_THAN" and item["start_id"] == "CATEGORY:FOODON_1" for item in relationships)
    assert aliases == []
    assert ambiguous == [{"normalized_name": "crisps", "targets": ["CATEGORY:FOODON_2", "CATEGORY:FOODON_3"]}]
