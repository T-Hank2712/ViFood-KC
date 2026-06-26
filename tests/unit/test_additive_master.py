import json
from pathlib import Path

import pytest

from food_kg.extractors.additive_master import extract
from food_kg.transformers.additive_master import build_candidates


def test_build_candidates_uses_every_staging_row(tmp_path: Path) -> None:
    staging = tmp_path / "staging.jsonl"
    staging.write_text(json.dumps({"source_ins": "621", "source_name_vi": "Mononatri glutamat", "source_name_en": "Monosodium L-glutamate", "functional_classes": ["Chất điều vị"], "source_id": "SOURCE:VN_VBHN_09_2024", "source_url": "https://example.test", "raw_page_number": 1, "raw_record_number": 2}, ensure_ascii=False) + "\n", encoding="utf-8")
    candidates = build_candidates(staging, "2026-06-22")
    assert candidates[0]["id"] == "ADDITIVE:INS_621"
    assert candidates[0]["properties"]["name_vi"] == "Mononatri glutamat"
    assert candidates[0]["functional_classes"] == ["Chất điều vị"]
    assert "functional_classes" not in candidates[0]["properties"]


def test_extract_rejects_pdf_without_expected_appendix(tmp_path: Path) -> None:
    with pytest.raises(Exception):
        extract(tmp_path / "missing.pdf", tmp_path / "staging.jsonl", "2026-06-22")
