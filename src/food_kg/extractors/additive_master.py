"""Extract Appendix 1 of Vietnam's consolidated food-additive regulation."""

from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path

import pdfplumber

SOURCE_ID = "SOURCE:VN_VBHN_09_2024"
SOURCE_URL = "https://datafiles.chinhphu.vn/cpp/files/vbpq/2024/9/09-vbhn-byt.pdf"
FIRST_APPENDIX_PAGE = 12
LAST_APPENDIX_PAGE = 45
# Appendix 1 contains ordinary codes (621), letter variants (150d), nested
# variants (160a(i)) and one E-prefixed code (E914).
INS_PATTERN = re.compile(r"^(?:E)?\d{1,4}[a-z]?(?:\([ivx]+\))?$", re.IGNORECASE)


def clean(value: str | None) -> str:
    return " ".join((value or "").replace("\n", " ").split())


def extract(input_file: Path, output_file: Path, retrieved_at: str | None = None) -> int:
    """Write one provenance-preserving record per valid Appendix 1 table row."""
    retrieved_at = retrieved_at or datetime.now(UTC).date().isoformat()
    records: list[dict] = []
    seen_ins: set[str] = set()
    with pdfplumber.open(input_file) as pdf:
        if len(pdf.pages) < LAST_APPENDIX_PAGE:
            raise ValueError("Regulation PDF does not contain the expected Appendix 1 page range")
        for page_number in range(FIRST_APPENDIX_PAGE, LAST_APPENDIX_PAGE + 1):
            table = pdf.pages[page_number - 1].extract_table() or []
            for row_number, row in enumerate(table, start=1):
                if len(row) < 5:
                    continue
                sequence, ins, name_vi, name_en, functions = map(clean, row[:5])
                if not sequence.rstrip(".").isdigit() or not INS_PATTERN.fullmatch(ins):
                    continue
                if not name_vi or not name_en or not functions:
                    raise ValueError(f"Page {page_number}, row {row_number}: incomplete additive record")
                if ins in seen_ins:
                    raise ValueError(f"Duplicate INS code in Appendix 1: {ins}")
                seen_ins.add(ins)
                records.append({
                    "source_ins": ins,
                    "source_name_vi": name_vi,
                    "source_name_en": name_en,
                    "functional_classes": [item.strip() for item in functions.split(",") if item.strip()],
                    "source_id": SOURCE_ID,
                    "source_url": SOURCE_URL,
                    "raw_file": input_file.name,
                    "raw_page_number": page_number,
                    "raw_record_number": int(sequence.rstrip(".")),
                    "retrieved_at": retrieved_at,
                })
    if not records:
        raise ValueError("No additive records were extracted from Appendix 1")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text("".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records), encoding="utf-8")
    return len(records)


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract Vietnam Appendix 1 food-additive records into staging JSONL")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--retrieved-at")
    args = parser.parse_args()
    print(f"Extracted {extract(args.input, args.output, args.retrieved_at)} additive records to {args.output}")


if __name__ == "__main__":
    main()
