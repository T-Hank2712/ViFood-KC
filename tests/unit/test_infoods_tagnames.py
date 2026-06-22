from food_kg.extractors.infoods_tagnames import parse_tagnames


def test_parses_tagname_record_and_preserves_provenance() -> None:
    raw = """<NA> sodium\n    Unit: mg\n    Synonyms: natrium\n    Comments: Example comment.\n    Tables: USDA 307\n\n<K> potassium\n    Unit: mg\n"""
    records = list(parse_tagnames(raw, "PART1.TXT", "2026-06-22"))
    assert records == [
        {
            "source_tagname": "NA", "source_name": "sodium", "default_unit": "mg",
            "synonyms_raw": "natrium", "comments": "Example comment.", "tables": "USDA 307",
            "source_id": "SOURCE:FAO_INFOODS_TAGNAMES",
            "source_url": "https://www.fao.org/infoods/infoods/standards-guidelines/food-component-identifiers-tagnames/en/",
            "raw_file": "PART1.TXT", "raw_record_number": 1, "retrieved_at": "2026-06-22",
        },
        {
            "source_tagname": "K", "source_name": "potassium", "default_unit": "mg",
            "synonyms_raw": None, "comments": None, "tables": None,
            "source_id": "SOURCE:FAO_INFOODS_TAGNAMES",
            "source_url": "https://www.fao.org/infoods/infoods/standards-guidelines/food-component-identifiers-tagnames/en/",
            "raw_file": "PART1.TXT", "raw_record_number": 2, "retrieved_at": "2026-06-22",
        },
    ]
