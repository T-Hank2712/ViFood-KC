"""Extract FAO/INFOODS Tagname TXT files into provenance-preserving staging JSONL."""

from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterator

SOURCE_ID = "SOURCE:FAO_INFOODS_TAGNAMES"
SOURCE_URL = "https://www.fao.org/infoods/infoods/standards-guidelines/food-component-identifiers-tagnames/en/"
RECORD_START = re.compile(r"^<(?P<tag>[A-Z0-9-]+)>\s*", re.MULTILINE)
FIELD_START = re.compile(r"^\s*(?P<name>Units?|Comments?|Synonyms?|Tables?)\s*:\s*", re.MULTILINE | re.IGNORECASE)


def normalize(value: str) -> str:
    return " ".join(value.replace("\r", "").split())


def parse_tagnames(text: str, raw_file: str, retrieved_at: str) -> Iterator[dict[str, object]]:
    """Yield one staging record per `<TAGNAME>` entry in an INFOODS part file."""
    matches = list(RECORD_START.finditer(text))
    for index, match in enumerate(matches, start=1):
        body_end = matches[index].start() if index < len(matches) else len(text)
        body = text[match.end():body_end]
        fields = list(FIELD_START.finditer(body))
        name = normalize(body[:fields[0].start()] if fields else body)
        if not name:
            continue
        values: dict[str, str] = {}
        for field_index, field in enumerate(fields):
            end = fields[field_index + 1].start() if field_index + 1 < len(fields) else len(body)
            key = field.group("name").lower().rstrip("s")
            values[key] = normalize(body[field.end():end])
        synonym_text = values.get("synonym", "")
        yield {
            "source_tagname": match.group("tag"),
            "source_name": name,
            "default_unit": values.get("unit") or None,
            "synonyms_raw": synonym_text or None,
            "comments": values.get("comment") or None,
            "tables": values.get("table") or None,
            "source_id": SOURCE_ID,
            "source_url": SOURCE_URL,
            "raw_file": raw_file,
            "raw_record_number": index,
            "retrieved_at": retrieved_at,
        }


def extract(input_dir: Path, output_file: Path, retrieved_at: str | None = None) -> int:
    retrieved_at = retrieved_at or datetime.now(UTC).date().isoformat()
    source_files = sorted(input_dir.glob("PART*.TXT"))
    if not source_files:
        raise FileNotFoundError(f"No PART*.TXT files found in {input_dir}")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with output_file.open("w", encoding="utf-8") as output:
        for path in source_files:
            # PART1 is ISO-8859-1; this encoding safely reads all current parts.
            text = path.read_text(encoding="iso-8859-1")
            for record in parse_tagnames(text, path.name, retrieved_at):
                output.write(json.dumps(record, ensure_ascii=False) + "\n")
                count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract FAO/INFOODS Tagnames into staging JSONL")
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--retrieved-at", help="ISO date; defaults to today's UTC date")
    args = parser.parse_args()
    count = extract(args.input_dir, args.output, args.retrieved_at)
    print(f"Extracted {count} INFOODS Tagname records to {args.output}")


if __name__ == "__main__":
    main()
