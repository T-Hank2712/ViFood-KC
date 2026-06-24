"""Extract INFOODS-tagged components from the SMILING Vietnam FCT workbook.

The workbook is distributed by FAO as an XLSX file.  Its food table uses
INFOODS component tags (for example ``PROTCNT(g)`` and ``VITC(mg)``), so this
extractor deliberately works from those tags rather than comparing nutrient
names with fuzzy text matching.
"""

from __future__ import annotations

import argparse
import json
import re
import zipfile
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from xml.etree import ElementTree as ET

SOURCE_ID = "SOURCE:VN_SMILING_FCT_2013"
SOURCE_URL = "https://www.fao.org/fileadmin/templates/food_composition/documents/FCT_SMILING_PROJECT_ASIA/D3_5a_SMILING_FCT_Vietnam_180713_protected.xlsx"
SPREADSHEET_NAMESPACE = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
RELATIONSHIPS_NAMESPACE = "{http://schemas.openxmlformats.org/package/2006/relationships}"
WORKBOOK_RELATIONSHIPS_NAMESPACE = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
TAG_WITH_UNIT = re.compile(r"^(?P<tag>[A-Za-z0-9_]+)\((?P<unit>[^)]+)\)$")
# The SMILING workbook uses the historical spelling PROTCNT, while the current
# INFOODS Tagnames standard spells the same, explicitly described component
# PROCNT.  This is a versioned one-to-one compatibility correction, not fuzzy
# matching and not a semantic inference.
TAGNAME_COMPATIBILITY = {"PROTCNT": "PROCNT"}


def _column_index(reference: str) -> int:
    """Convert an Excel cell reference such as ``Z2`` to a zero-based column."""
    letters = "".join(character for character in reference if character.isalpha())
    value = 0
    for letter in letters:
        value = value * 26 + ord(letter.upper()) - ord("A") + 1
    return value - 1


def _shared_strings(archive: zipfile.ZipFile) -> list[str]:
    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    strings = []
    for item in root.findall(f"{SPREADSHEET_NAMESPACE}si"):
        strings.append("".join(node.text or "" for node in item.iter(f"{SPREADSHEET_NAMESPACE}t")))
    return strings


def _worksheet_path(archive: zipfile.ZipFile, sheet_name: str) -> str:
    workbook = ET.fromstring(archive.read("xl/workbook.xml"))
    relation_id = next(
        sheet.attrib[f"{WORKBOOK_RELATIONSHIPS_NAMESPACE}id"]
        for sheet in workbook.findall(f".//{SPREADSHEET_NAMESPACE}sheet")
        if sheet.attrib["name"] == sheet_name
    )
    relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    target = next(
        relation.attrib["Target"]
        for relation in relationships.findall(f"{RELATIONSHIPS_NAMESPACE}Relationship")
        if relation.attrib["Id"] == relation_id
    )
    return f"xl/{target.lstrip('/')}"


def _rows(archive: zipfile.ZipFile, sheet_name: str) -> list[list[str | None]]:
    shared_strings = _shared_strings(archive)
    root = ET.fromstring(archive.read(_worksheet_path(archive, sheet_name)))
    parsed_rows: list[list[str | None]] = []
    for row in root.findall(f".//{SPREADSHEET_NAMESPACE}sheetData/{SPREADSHEET_NAMESPACE}row"):
        values: list[str | None] = []
        for cell in row.findall(f"{SPREADSHEET_NAMESPACE}c"):
            index = _column_index(cell.attrib["r"])
            values.extend([None] * max(0, index - len(values)))
            raw = cell.findtext(f"{SPREADSHEET_NAMESPACE}v")
            value = shared_strings[int(raw)] if raw is not None and cell.attrib.get("t") == "s" else raw
            if index == len(values):
                values.append(value)
            else:
                values[index] = value
        parsed_rows.append(values)
    return parsed_rows


def _canonical_tag(header: str) -> tuple[str, str | None] | None:
    """Return the INFOODS tag and unit encoded in a Vietnam FCT column header."""
    if header == "ENERGY":
        # The workbook's component-description sheet defines this energy column
        # with the INFOODS tag ENERC; the table header omits the tag for brevity.
        return "ENERC", None
    match = TAG_WITH_UNIT.fullmatch(header)
    if not match:
        return None
    tag = match.group("tag").upper()
    return TAGNAME_COMPATIBILITY.get(tag, tag), match.group("unit")


def extract_components(input_file: Path, output_file: Path, report_file: Path | None = None, retrieved_at: str | None = None) -> int:
    """Write one provenance-preserving record for every tagged FCT component.

    Components that do not occur in the current INFOODS snapshot (for example
    ``DFE``) are retained for the later intersection report but not promoted.
    They require an explicit, source-backed crosswalk rather than a guessed
    equivalence.
    """
    retrieved_at = retrieved_at or datetime.now(UTC).date().isoformat()
    with zipfile.ZipFile(input_file) as archive:
        rows = _rows(archive, "WP3 FCT")
    header_index = next(index for index, row in enumerate(rows) if row and row[0] == "Code")
    headers = rows[header_index]
    non_empty_counts: dict[int, int] = defaultdict(int)
    for row in rows[header_index + 1:]:
        for index, value in enumerate(row):
            if value not in (None, ""):
                non_empty_counts[index] += 1

    components: dict[str, dict] = {}
    unmapped: list[str] = []
    for index, header in enumerate(headers[5:], start=5):
        if not header:
            continue
        parsed = _canonical_tag(header)
        if not parsed:
            unmapped.append(header)
            continue
        tag, unit = parsed
        record = components.setdefault(tag, {
            "source_tagname": tag,
            "source_columns": [],
            "source_units": [],
            "food_records_with_value": 0,
            "source_id": SOURCE_ID,
            "source_url": SOURCE_URL,
            "raw_file": input_file.name,
            "retrieved_at": retrieved_at,
        })
        record["source_columns"].append(header)
        if unit and unit not in record["source_units"]:
            record["source_units"].append(unit)
        record["food_records_with_value"] += non_empty_counts[index]

    records = [components[tag] for tag in sorted(components)]
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text("".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records), encoding="utf-8")
    if report_file:
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text(json.dumps({
            "source_id": SOURCE_ID,
            "raw_file": input_file.name,
            "component_count": len(records),
            "unmapped_columns": unmapped,
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return len(records)


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract exact INFOODS tags from the Vietnam SMILING FCT workbook")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--retrieved-at")
    args = parser.parse_args()
    print(f"Extracted {extract_components(args.input, args.output, args.report, args.retrieved_at)} Vietnam FCT component tags")


if __name__ == "__main__":
    main()
