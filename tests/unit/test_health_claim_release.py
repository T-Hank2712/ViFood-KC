import json

from food_kg.services.health_claim_release import build_release


def test_builds_evidence_complete_health_claim_release(tmp_path) -> None:
    staging = tmp_path / "claims.jsonl"
    staging.write_text(json.dumps({
        "id": "CLAIM:SODIUM_HIGH_INTAKE_BP", "subject_external_codes": ["NA"],
        "outcome_id": "OUTCOME:HIGH_BLOOD_PRESSURE", "outcome_name": "Raised blood pressure",
        "claim_text": "High sodium intake is associated with increased blood pressure.",
        "evidence_excerpt": "high intake of sodium (salt) is associated with increased blood pressure",
        "evidence_level": "authoritative public-health guidance", "conditions_of_use": "Population-level guidance.",
        "effect_direction": "increase",
    }) + "\n", encoding="utf-8")
    nutrients = tmp_path / "nutrients.json"
    nutrients.write_text(json.dumps([
        {"label": "Source", "id": "SOURCE:FAO_INFOODS_TAGNAMES", "properties": {"source": "SOURCE:FAO_INFOODS_TAGNAMES"}},
        {"label": "Nutrient", "id": "NUTRIENT:INFOODS_NA", "properties": {"external_code": "NA", "source": "SOURCE:FAO_INFOODS_TAGNAMES"}},
    ]), encoding="utf-8")
    nodes, relationships = build_release(staging, nutrients, "2026-06-24")
    assert {node["label"] for node in nodes} == {"Source", "Nutrient", "HealthClaim", "HealthOutcome"}
    assert {relationship["type"] for relationship in relationships} == {"SUBJECT_OF", "OUTCOME", "EVIDENCED_BY"}


def test_builds_one_claim_with_multiple_nutrient_subjects(tmp_path) -> None:
    staging = tmp_path / "claims.jsonl"
    staging.write_text(json.dumps({
        "id": "CLAIM:MICRONUTRIENTS", "subject_external_codes": ["CA", "FE"],
        "outcome_id": "OUTCOME:GROWTH", "outcome_name": "Growth", "claim_text": "Micronutrients support growth.",
        "evidence_excerpt": "micronutrients are essential", "evidence_level": "guidance",
        "conditions_of_use": "Population-level guidance.", "effect_direction": "supports",
    }) + "\n", encoding="utf-8")
    nutrients = tmp_path / "nutrients.json"
    nutrients.write_text(json.dumps([
        {"label": "Source", "id": "SOURCE:FAO_INFOODS_TAGNAMES", "properties": {"source": "SOURCE:FAO_INFOODS_TAGNAMES"}},
        {"label": "Nutrient", "id": "NUTRIENT:INFOODS_CA", "properties": {"external_code": "CA", "source": "SOURCE:FAO_INFOODS_TAGNAMES"}},
        {"label": "Nutrient", "id": "NUTRIENT:INFOODS_FE", "properties": {"external_code": "FE", "source": "SOURCE:FAO_INFOODS_TAGNAMES"}},
    ]), encoding="utf-8")
    _, relationships = build_release(staging, nutrients, "2026-06-24")
    assert sum(relationship["type"] == "SUBJECT_OF" for relationship in relationships) == 2
