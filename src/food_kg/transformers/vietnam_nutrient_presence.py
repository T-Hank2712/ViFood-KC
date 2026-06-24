"""Build nutrient candidates from an exact INFOODS--Vietnam FCT tag intersection."""

from __future__ import annotations

import json
import re
from pathlib import Path


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _nutrient_id(tagname: str) -> str:
    return "NUTRIENT:INFOODS_" + re.sub(r"[^A-Z0-9]+", "_", tagname.upper())


def build_candidates(
    infoods_staging: Path, vietnam_components: Path, reviewed_at: str,
    labeling_requirements: Path | None = None,
) -> list[dict]:
    """Select only tags present verbatim in both authoritative sources.

    No string similarity score is calculated or stored.  A component is either
    represented by the same INFOODS tagname in the Vietnam table or it is not
    eligible for this automated release.
    """
    vietnam_by_tag = {record["source_tagname"]: record for record in _read_jsonl(vietnam_components)}
    labeling_by_tag = {
        record["source_tagname"]: record
        for record in _read_jsonl(labeling_requirements)
    } if labeling_requirements else {}
    candidates: list[dict] = []
    for source in _read_jsonl(infoods_staging):
        tagname = source["source_tagname"]
        vietnam = vietnam_by_tag.get(tagname)
        labeling = labeling_by_tag.get(tagname)
        if not vietnam and not labeling:
            continue
        properties = {
            "name": source["source_name"],
            "external_code": tagname,
            "default_unit": source["default_unit"],
            "source": source["source_id"],
            "source_url": source["source_url"],
            "source_version": "INFOODS Tagnames snapshot 2026-06-22",
            "reviewed_at": reviewed_at,
            "status": "draft",
        }
        if vietnam:
            properties.update({
                "vietnam_presence_source": vietnam["source_id"],
                "vietnam_presence_source_url": vietnam["source_url"],
                "vietnam_fct_columns": vietnam["source_columns"],
                "vietnam_fct_value_count": vietnam["food_records_with_value"],
            })
        if labeling:
            properties.update({
                "name_vi": labeling["name_vi"],
                "vietnam_labeling_source": labeling["source_id"],
                "vietnam_labeling_source_url": labeling["source_url"],
                "vietnam_label_requirement": labeling["label_requirement"],
                "vietnam_legal_reference": labeling["legal_reference"],
                "vietnam_labeling_source_page": labeling["source_page"],
            })
        candidates.append({
            "label": "Nutrient",
            "id": _nutrient_id(tagname),
            "properties": properties,
        })
    return candidates
