import json

from food_kg.transformers.vietnam_nutrient_presence import build_candidates


def test_selects_only_exact_infoods_tag_present_in_vietnam_table(tmp_path):
    infoods = tmp_path / "infoods.jsonl"
    infoods.write_text(
        json.dumps({"source_tagname": "NA", "source_name": "sodium", "default_unit": "mg", "source_id": "SOURCE:FAO_INFOODS_TAGNAMES", "source_url": "https://example.test"}) + "\n"
        + json.dumps({"source_tagname": "HISTN", "source_name": "histamine", "default_unit": "mg", "source_id": "SOURCE:FAO_INFOODS_TAGNAMES", "source_url": "https://example.test"}) + "\n",
        encoding="utf-8",
    )
    components = tmp_path / "components.jsonl"
    components.write_text(json.dumps({
        "source_tagname": "NA", "source_columns": ["NA(mg)"], "food_records_with_value": 123,
        "source_id": "SOURCE:VN_SMILING_FCT_2013", "source_url": "https://example.test",
    }) + "\n", encoding="utf-8")

    candidates = build_candidates(infoods, components, "2026-06-24")

    assert [candidate["id"] for candidate in candidates] == ["NUTRIENT:INFOODS_NA"]
    assert candidates[0]["properties"]["vietnam_fct_columns"] == ["NA(mg)"]
