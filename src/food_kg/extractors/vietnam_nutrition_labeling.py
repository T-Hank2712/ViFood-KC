"""Provide the verified nutrient scope of Vietnam Circular 29/2023/TT-BYT.

The official PDF is a scan.  The small, stable legal list below was visually
verified from Article 5 (pages 3--4) and is deliberately encoded as exact
INFOODS tagnames.  The extractor verifies that every tag exists in the
INFOODS snapshot before allowing it into staging.
"""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

SOURCE_ID = "SOURCE:VN_TT29_2023"
SOURCE_URL = "https://vfa.gov.vn/van-ban/tai-tep-158f3069a435b314a80bdcb024f8e422.html"
LEGAL_COMPONENTS = (
    ("ENERC", "Năng lượng", "required", "Điều 5 khoản 1 điểm a", 3),
    ("PROCNT", "Chất đạm", "required", "Điều 5 khoản 1 điểm b", 4),
    ("CHOCDF", "Carbohydrat", "required", "Điều 5 khoản 1 điểm c", 4),
    ("FAT", "Chất béo", "required", "Điều 5 khoản 1 điểm d", 4),
    ("NA", "Natri", "required", "Điều 5 khoản 1 điểm đ", 4),
    ("SUGAR", "Đường tổng số", "conditional", "Điều 5 khoản 2", 4),
    ("FASAT", "Chất béo bão hòa", "conditional", "Điều 5 khoản 3", 4),
)


def extract_requirements(infoods_staging: Path, raw_pdf: Path, output_file: Path, retrieved_at: str | None = None) -> int:
    retrieved_at = retrieved_at or datetime.now(UTC).date().isoformat()
    infoods_tags = {
        json.loads(line)["source_tagname"]
        for line in infoods_staging.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }
    missing = [tag for tag, *_ in LEGAL_COMPONENTS if tag not in infoods_tags]
    if missing:
        raise ValueError(f"Vietnam nutrition-label tags missing from INFOODS staging: {', '.join(missing)}")
    records = [
        {
            "source_tagname": tag, "name_vi": name_vi, "label_requirement": requirement,
            "legal_reference": reference, "source_page": page, "source_id": SOURCE_ID,
            "source_url": SOURCE_URL, "raw_file": raw_pdf.name, "retrieved_at": retrieved_at,
        }
        for tag, name_vi, requirement, reference, page in LEGAL_COMPONENTS
    ]
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text("".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records), encoding="utf-8")
    return len(records)


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage verified Vietnam nutrition-labelling requirements")
    parser.add_argument("--infoods-staging", type=Path, required=True)
    parser.add_argument("--raw-pdf", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--retrieved-at")
    args = parser.parse_args()
    print(f"Extracted {extract_requirements(args.infoods_staging, args.raw_pdf, args.output, args.retrieved_at)} Vietnam nutrition-label requirements")


if __name__ == "__main__":
    main()
