import json

from food_kg.extractors.vietnam_nutrition_labeling import extract_requirements
from food_kg.transformers.vietnam_nutrient_presence import build_candidates


def test_adds_legal_nutrients_even_when_absent_from_food_composition_table(tmp_path):
    infoods = tmp_path / "infoods.jsonl"
    tags = ["ENERC", "PROCNT", "CHOCDF", "FAT", "NA", "SUGAR", "FASAT"]
    infoods.write_text("".join(json.dumps({
        "source_tagname": tag, "source_name": tag.lower(), "default_unit": "g",
        "source_id": "SOURCE:FAO_INFOODS_TAGNAMES", "source_url": "https://example.test",
    }) + "\n" for tag in tags), encoding="utf-8")
    requirements = tmp_path / "requirements.jsonl"
    assert extract_requirements(infoods, tmp_path / "tt29.pdf", requirements, "2026-06-24") == 7
    components = tmp_path / "components.jsonl"
    components.write_text("", encoding="utf-8")

    candidates = build_candidates(infoods, components, "2026-06-24", requirements)

    sodium = next(candidate for candidate in candidates if candidate["properties"]["external_code"] == "NA")
    assert sodium["properties"]["name_vi"] == "Natri"
    assert sodium["properties"]["vietnam_label_requirement"] == "required"
