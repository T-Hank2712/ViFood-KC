from pathlib import Path

import pytest

from food_kg.extractors.chebi import extract_record


def test_extracts_ld_json_molecular_entity(tmp_path: Path) -> None:
    page = tmp_path / "CHEBI_1.html"
    page.write_text('<script type="application/ld+json">{"@type":"MolecularEntity","name":"glucose","identifier":"CHEBI:1","url":"https://example.test/CHEBI:1","molecularFormula":"C6H12O6"}</script>', encoding="utf-8")
    record = extract_record(page, "CHEBI:1", "2026-06-25")
    assert record["name"] == "glucose"
    assert record["molecular_formula"] == "C6H12O6"


def test_rejects_mismatched_chebi_id(tmp_path: Path) -> None:
    page = tmp_path / "CHEBI_1.html"
    page.write_text('<script type="application/ld+json">{"@type":"MolecularEntity","name":"glucose","identifier":"CHEBI:2"}</script>', encoding="utf-8")
    with pytest.raises(ValueError, match="expected CHEBI:1"):
        extract_record(page, "CHEBI:1", "2026-06-25")
