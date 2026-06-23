"""Extract Appendix 2A additive maximum-use rows from 09/VBHN-BYT."""

from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path

import pdfplumber

SOURCE_ID = "SOURCE:VN_VBHN_09_2024"
SOURCE_URL = "https://datafiles.chinhphu.vn/cpp/files/vbpq/2024/9/09-vbhn-byt.pdf"
INS = re.compile(r"^(?:E)?\d{1,4}[a-z]?(?:\([ivx]+\))?$", re.I)
APPENDIX_INS = re.compile(r"^(?:E)?\d{3,4}[a-z]?(?:\([ivx]+\))?$", re.I)
FOOD_CODE = re.compile(r"^\d{2}(?:\.\d+)+$")


def clean(words: list[dict]) -> str:
    return " ".join(word["text"] for word in sorted(words, key=lambda word: word["x0"]))


def page_rows(page: pdfplumber.page.Page) -> list[list[dict]]:
    buckets: dict[int, list[dict]] = {}
    for word in page.extract_words(x_tolerance=2, y_tolerance=2):
        buckets.setdefault(round(word["top"]), []).append(word)
    return [buckets[key] for key in sorted(buckets)]


def extract_appendix_2a(input_file: Path, output_file: Path, retrieved_at: str | None = None) -> int:
    retrieved_at = retrieved_at or datetime.now(UTC).date().isoformat()
    records: list[dict] = []
    current_ins: list[str] = []
    in_ins_section = False
    last_record: dict | None = None
    with pdfplumber.open(input_file) as pdf:
        for page_number in range(46, 358):
            for row in page_rows(pdf.pages[page_number - 1]):
                left = [word for word in row if word["x0"] < 150]
                middle = [word for word in row if 150 <= word["x0"] < 425]
                maximum = [word for word in row if 425 <= word["x0"] < 490]
                notes = [word for word in row if word["x0"] >= 490]
                left_text, middle_text, max_text, note_text = clean(left), clean(middle), clean(maximum), clean(notes)
                if left_text == "INS" and "Tên phụ gia" in clean(row):
                    current_ins, in_ins_section, last_record = [], True, None
                    continue
                if "Mã nhóm" in left_text and "Nhóm thực phẩm" in clean(row):
                    in_ins_section, last_record = False, None
                    continue
                if in_ins_section and INS.fullmatch(left_text):
                    current_ins.append(left_text)
                    continue
                if FOOD_CODE.fullmatch(left_text) and (max_text in {"GMP", "QS"} or max_text.isdigit()):
                    if not current_ins or not middle_text:
                        raise ValueError(f"Page {page_number}: food row has no additive context")
                    record = {
                        "appendix": "2A", "ins_codes": current_ins.copy(), "food_group_code": left_text,
                        "food_group_name_vi": middle_text, "maximum_level": max_text,
                        "unit": "mg/kg" if max_text not in {"GMP", "QS"} else max_text,
                        "note": note_text or None, "source_id": SOURCE_ID, "source_url": SOURCE_URL,
                        "raw_file": input_file.name, "raw_page_number": page_number,
                        "retrieved_at": retrieved_at,
                    }
                    records.append(record)
                    last_record = record
                elif last_record and middle_text and not max_text and not note_text and not left_text:
                    last_record["food_group_name_vi"] += " " + middle_text
    if not records:
        raise ValueError("No Appendix 2A permission rows were extracted")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text("".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records), encoding="utf-8")
    return len(records)


def extract_appendix_2b(input_file: Path, output_file: Path, retrieved_at: str | None = None) -> int:
    """Extract Appendix 2B rows, preserving its source text category verbatim."""
    retrieved_at = retrieved_at or datetime.now(UTC).date().isoformat()
    records, current_ins, current_names, last_record, pending = [], [], {}, None, None
    in_ins_section = in_table = False
    with pdfplumber.open(input_file) as pdf:
        for page_number in range(358, 388):
            for row in page_rows(pdf.pages[page_number - 1]):
                left = [word for word in row if word["x0"] < 380]
                maximum = [word for word in row if 380 <= word["x0"] < 470]
                notes = [word for word in row if word["x0"] >= 470]
                left_text, max_text, note_text, all_text = clean(left), clean(maximum), clean(notes), clean(row)
                if in_table and left_text and re.fullmatch(r"[A-ZÀ-Ỵ\s]+", left_text):
                    current_ins, in_ins_section, in_table, last_record, pending = [], False, False, None, None
                    continue
                if all_text.startswith("INS") and "Tên phụ gia" in all_text:
                    current_ins, current_names, in_ins_section, in_table, last_record, pending = [], {}, True, False, None, None
                    continue
                if "Nhóm thực phẩm" in all_text and "ML" in all_text:
                    in_ins_section, in_table, last_record, pending = False, True, None, None
                    continue
                first_token = left_text.split(maxsplit=1)[0] if left_text else ""
                if in_ins_section and APPENDIX_INS.fullmatch(first_token):
                    current_ins.append(first_token)
                    current_names[first_token] = left_text.removeprefix(first_token).strip()
                    continue
                # Uppercase additive headings and legal footnotes terminate the prior table.
                if in_table and ("được bổ sung" in all_text or "có hiệu lực" in all_text or "thi hành từ ngày" in all_text):
                    continue
                if in_table and left_text.isdigit():
                    continue
                if not in_table or not current_ins:
                    continue
                if max_text and not left_text:
                    pending = (max_text, note_text)
                    continue
                if left_text and (max_text or pending):
                    value, note = (max_text, note_text) if max_text else pending
                    pending = None
                    record = {
                        "appendix": "2B", "ins_codes": current_ins.copy(), "source_additive_names": current_names.copy(), "food_group_code": None,
                        "food_group_name_vi": left_text, "maximum_level": value,
                        "unit": "mg/kg" if value not in {"GMP", "QS"} else value,
                        "note": note or None, "source_id": SOURCE_ID, "source_url": SOURCE_URL,
                        "raw_file": input_file.name, "raw_page_number": page_number,
                        "retrieved_at": retrieved_at,
                    }
                    records.append(record)
                    last_record = record
                elif left_text and last_record:
                    last_record["food_group_name_vi"] += " " + left_text
    if not records:
        raise ValueError("No Appendix 2B permission rows were extracted")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text("".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records), encoding="utf-8")
    return len(records)


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract Vietnam Appendix 2A/2B additive-use limits")
    parser.add_argument("--appendix", choices=("2A", "2B"), default="2A")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--retrieved-at")
    args = parser.parse_args()
    extract_fn = extract_appendix_2a if args.appendix == "2A" else extract_appendix_2b
    print(f"Extracted {extract_fn(args.input, args.output, args.retrieved_at)} Appendix {args.appendix} rows")


if __name__ == "__main__":
    main()
