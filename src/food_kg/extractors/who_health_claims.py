"""Verify configured WHO Healthy Diet claims against an immutable raw snapshot."""

from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path

import yaml


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def normalise(value: str) -> str:
    return " ".join(re.sub(r"\s+", " ", value).casefold().split())


def extract_claims(raw_html: Path, rules_file: Path, output_file: Path, retrieved_at: str | None = None) -> int:
    """Stage only claims whose exact evidence excerpt is present in raw HTML."""
    retrieved_at = retrieved_at or datetime.now(UTC).date().isoformat()
    parser = _TextExtractor()
    parser.feed(raw_html.read_text(encoding="utf-8"))
    page_text = normalise(" ".join(parser.parts))
    rules = yaml.safe_load(rules_file.read_text(encoding="utf-8"))
    records = []
    for claim in rules["claims"]:
        excerpt = normalise(claim["evidence_excerpt"])
        if excerpt not in page_text:
            raise ValueError(f"Evidence excerpt is absent from WHO snapshot for {claim['id']}")
        records.append({
            **claim,
            "source_id": rules["source_id"],
            "source_url": rules["source_url"],
            "raw_file": raw_html.name,
            "retrieved_at": retrieved_at,
        })
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text("".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records), encoding="utf-8")
    return len(records)


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify WHO health claims against a raw HTML snapshot")
    parser.add_argument("--raw-html", type=Path, required=True)
    parser.add_argument("--rules", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--retrieved-at")
    args = parser.parse_args()
    print(f"Staged {extract_claims(args.raw_html, args.rules, args.output, args.retrieved_at)} WHO health claims")


if __name__ == "__main__":
    main()
