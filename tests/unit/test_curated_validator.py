from food_kg.models import NodeRecord, RelationshipRecord
from food_kg.validators import validate_curated_graph

def node(label: str, identifier: str, **properties: object) -> NodeRecord:
    return NodeRecord(label=label, id=identifier, properties={
        "name": identifier, "source": "SOURCE:TEST", "source_url": "https://example.test", "reviewed_at": "2026-01-01", **properties,
    })

def test_health_claim_with_required_context_is_valid() -> None:
    nodes = [
        node("HealthClaim", "CLAIM:TEST", conditions_of_use="population context", evidence_level="high"),
        node("Nutrient", "NUTRIENT:SODIUM"), node("HealthOutcome", "OUTCOME:BP"), node("Source", "SOURCE:TEST"),
    ]
    relationships = [
        RelationshipRecord(start_id="CLAIM:TEST", end_id="NUTRIENT:SODIUM", type="SUBJECT_OF"),
        RelationshipRecord(start_id="CLAIM:TEST", end_id="OUTCOME:BP", type="OUTCOME"),
        RelationshipRecord(start_id="CLAIM:TEST", end_id="SOURCE:TEST", type="EVIDENCED_BY"),
    ]
    assert validate_curated_graph(nodes, relationships) == []

def test_rejects_invalid_endpoint_and_missing_provenance() -> None:
    nodes = [node("Nutrient", "NUTRIENT:SODIUM"), NodeRecord(label="Ingredient", id="INGREDIENT:SALT", properties={"name": "salt"})]
    relationship = RelationshipRecord(start_id="NUTRIENT:SODIUM", end_id="INGREDIENT:SALT", type="HAS_NUTRIENT")
    errors = validate_curated_graph(nodes, [relationship])
    assert any("missing provenance" in error for error in errors)
    assert any("invalid endpoints" in error for error in errors)

def test_allowlists_reject_cypher_injection_values() -> None:
    import pytest
    with pytest.raises(ValueError):
        NodeRecord(label="Nutrient) DELETE n //", id="NUTRIENT:SODIUM")
    with pytest.raises(ValueError):
        RelationshipRecord(start_id="NUTRIENT:SODIUM", end_id="NUTRIENT:SALT", type="X] DELETE r //")
