"""Build an importable, provenance-complete HealthClaim release."""

from __future__ import annotations

import json
from pathlib import Path

WHO_SOURCE_ID = "SOURCE:WHO_HEALTHY_DIET"
WHO_SOURCE_URL = "https://www.who.int/news-room/fact-sheets/detail/healthy-diet"


def _jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def build_release(staging_file: Path, nutrient_nodes_file: Path, reviewed_at: str) -> tuple[list[dict], list[dict]]:
    nutrient_nodes = json.loads(nutrient_nodes_file.read_text(encoding="utf-8"))
    nutrients_by_code = {
        node["properties"]["external_code"]: node
        for node in nutrient_nodes
        if node["label"] == "Nutrient"
    }
    infoods_sources = [node for node in nutrient_nodes if node["label"] == "Source" and node["id"] == "SOURCE:FAO_INFOODS_TAGNAMES"]
    if not infoods_sources:
        raise ValueError("Nutrient release must include SOURCE:FAO_INFOODS_TAGNAMES")
    who_source = {
        "label": "Source", "id": WHO_SOURCE_ID,
        "properties": {
            "name": "WHO Healthy Diet", "source_type": "public-health-guidance", "url": WHO_SOURCE_URL,
            "source": WHO_SOURCE_ID, "source_url": WHO_SOURCE_URL,
            "reviewed_at": reviewed_at, "status": "active",
        },
    }
    nodes: list[dict] = [infoods_sources[0], who_source]
    relationships: list[dict] = []
    included_nutrients: set[str] = set()
    for record in _jsonl(staging_file):
        subject_codes = record.get("subject_external_codes", [record.get("subject_external_code")])
        nutrients = []
        for code in subject_codes:
            nutrient = nutrients_by_code.get(code)
            if not nutrient:
                raise ValueError(f"Claim {record['id']} references unavailable Nutrient {code}")
            if nutrient["id"] not in included_nutrients:
                nodes.append(nutrient)
                included_nutrients.add(nutrient["id"])
            nutrients.append(nutrient)
        outcome = {
            "label": "HealthOutcome", "id": record["outcome_id"],
            "properties": {
                "name": record["outcome_name"], "source": WHO_SOURCE_ID, "source_url": WHO_SOURCE_URL,
                "reviewed_at": reviewed_at, "status": "active",
            },
        }
        claim = {
            "label": "HealthClaim", "id": record["id"],
            "properties": {
                "name": record["claim_text"], "claim_text": record["claim_text"],
                "conditions_of_use": record["conditions_of_use"], "evidence_level": record["evidence_level"],
                "evidence_excerpt": record["evidence_excerpt"], "source": WHO_SOURCE_ID,
                "source_url": WHO_SOURCE_URL, "reviewed_at": reviewed_at, "status": "active",
            },
        }
        nodes.extend([outcome, claim])
        relationships.extend([
            *[
                {"start_id": claim["id"], "end_id": nutrient["id"], "type": "SUBJECT_OF", "properties": {"role": "primary"}}
                for nutrient in nutrients
            ],
            {"start_id": claim["id"], "end_id": outcome["id"], "type": "OUTCOME", "properties": {"effect_direction": record["effect_direction"]}},
            {"start_id": claim["id"], "end_id": WHO_SOURCE_ID, "type": "EVIDENCED_BY", "properties": {"evidence_role": "primary", "evidence_excerpt": record["evidence_excerpt"]}},
        ])
    return nodes, relationships
