"""Create strict Vietnam-relevant nutrient candidates without a hand-picked nutrient list."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from food_kg.extractors.vietnam_food_composition import extract_components
from food_kg.extractors.vietnam_nutrition_labeling import extract_requirements
from food_kg.transformers.vietnam_nutrient_presence import build_candidates


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--infoods-staging", type=Path, required=True)
    parser.add_argument("--vietnam-fct", type=Path, required=True)
    parser.add_argument("--components-output", type=Path, required=True)
    parser.add_argument("--report-output", type=Path, required=True)
    parser.add_argument("--nutrition-label-pdf", type=Path, required=True)
    parser.add_argument("--labeling-output", type=Path, required=True)
    parser.add_argument("--candidates-output", type=Path, required=True)
    parser.add_argument("--reviewed-at", default=date.today().isoformat())
    args = parser.parse_args()

    component_count = extract_components(
        args.vietnam_fct, args.components_output, args.report_output, args.reviewed_at
    )
    extract_requirements(args.infoods_staging, args.nutrition_label_pdf, args.labeling_output, args.reviewed_at)
    candidates = build_candidates(args.infoods_staging, args.components_output, args.reviewed_at, args.labeling_output)
    component_tags = {
        json.loads(line)["source_tagname"]
        for line in args.components_output.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }
    selected_tags = {candidate["properties"]["external_code"] for candidate in candidates}
    report = json.loads(args.report_output.read_text(encoding="utf-8"))
    report["unmatched_infoods_tags"] = sorted(component_tags - selected_tags)
    args.report_output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.candidates_output.parent.mkdir(parents=True, exist_ok=True)
    args.candidates_output.write_text(json.dumps(candidates, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Extracted {component_count} Vietnam FCT tags; created {len(candidates)} exact INFOODS candidates")


if __name__ == "__main__":
    main()
