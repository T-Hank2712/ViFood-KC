from pathlib import Path

import pytest

from food_kg.extractors.who_health_claims import extract_claims


def test_stages_claim_only_when_evidence_excerpt_exists(tmp_path: Path) -> None:
    html = tmp_path / "who.html"
    html.write_text("<p>High intake of sodium (salt) is associated with increased blood pressure.</p>", encoding="utf-8")
    rules = tmp_path / "rules.yaml"
    rules.write_text("""
source_id: SOURCE:WHO_HEALTHY_DIET
source_url: https://example.test
claims:
  - id: CLAIM:SODIUM_HIGH_INTAKE_BP
    subject_external_code: NA
    outcome_id: OUTCOME:HIGH_BLOOD_PRESSURE
    outcome_name: Raised blood pressure
    claim_text: High sodium intake is associated with increased blood pressure.
    evidence_excerpt: high intake of sodium (salt) is associated with increased blood pressure
    evidence_level: authoritative public-health guidance
    conditions_of_use: Population-level dietary guidance.
    effect_direction: increase
""", encoding="utf-8")
    output = tmp_path / "claims.jsonl"
    assert extract_claims(html, rules, output, "2026-06-24") == 1


def test_rejects_claim_when_evidence_excerpt_is_missing(tmp_path: Path) -> None:
    html = tmp_path / "who.html"
    html.write_text("<p>Different statement.</p>", encoding="utf-8")
    rules = tmp_path / "rules.yaml"
    rules.write_text("source_id: SOURCE:WHO_HEALTHY_DIET\nsource_url: https://example.test\nclaims:\n  - id: CLAIM:TEST\n    evidence_excerpt: expected statement\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Evidence excerpt"):
        extract_claims(html, rules, tmp_path / "claims.jsonl", "2026-06-24")
