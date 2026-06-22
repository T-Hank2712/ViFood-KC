import json

from food_kg.transformers.nutrient_master import build_candidates


def test_builds_draft_candidate_from_staging(tmp_path) -> None:
    staging = tmp_path / "staging.jsonl"
    staging.write_text(json.dumps({
        "source_tagname": "NA", "source_name": "sodium", "comments": None,
        "source_id": "SOURCE:FAO_INFOODS_TAGNAMES", "source_url": "https://example.test",
    }) + "\n")
    mapping = tmp_path / "mapping.yaml"
    mapping.write_text("candidates:\n  - {id: NUTRIENT:SODIUM, tagname: NA, name: Sodium, name_vi: Natri, nutrient_type: mineral, default_unit: mg}\n")
    records = build_candidates(staging, mapping, "2026-06-22")
    assert records[0]["id"] == "NUTRIENT:SODIUM"
    assert records[0]["properties"]["status"] == "draft"
    assert records[0]["properties"]["external_code"] == "NA"
