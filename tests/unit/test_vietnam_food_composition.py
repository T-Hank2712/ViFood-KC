import json
import zipfile
from pathlib import Path

from food_kg.extractors.vietnam_food_composition import extract_components


def _workbook(path: Path) -> None:
    content_types = '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>'
    workbook = '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="WP3 FCT" sheetId="1" r:id="rId1"/></sheets></workbook>'
    relationships = '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Target="worksheets/sheet1.xml" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet"/></Relationships>'
    strings = '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><si><t>Code</t></si><si><t>ENERGY</t></si><si><t>PROTCNT(g)</t></si><si><t>DFE(mcg)</t></si></sst>'
    sheet = '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData><row r="2"><c r="A2" t="s"><v>0</v></c><c r="F2" t="s"><v>1</v></c><c r="G2" t="s"><v>2</v></c><c r="H2" t="s"><v>3</v></c></row><row r="3"><c r="A3"><v>1</v></c><c r="F3"><v>12</v></c><c r="G3"><v>3</v></c><c r="H3"><v>4</v></c></row></sheetData></worksheet>'
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("xl/workbook.xml", workbook)
        archive.writestr("xl/_rels/workbook.xml.rels", relationships)
        archive.writestr("xl/sharedStrings.xml", strings)
        archive.writestr("xl/worksheets/sheet1.xml", sheet)


def test_extracts_exact_tags_and_reports_unmapped_columns(tmp_path):
    workbook = tmp_path / "table.xlsx"
    output = tmp_path / "components.jsonl"
    report = tmp_path / "report.json"
    _workbook(workbook)

    assert extract_components(workbook, output, report, "2026-06-24") == 3
    assert [json.loads(line)["source_tagname"] for line in output.read_text().splitlines()] == ["DFE", "ENERC", "PROCNT"]
    assert json.loads(report.read_text())["unmapped_columns"] == []
