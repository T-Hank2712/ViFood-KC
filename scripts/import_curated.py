"""Import one reviewed curated release. Raw/staging data is deliberately unsupported."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv
import yaml

from food_kg.graph import Neo4jImporter
from food_kg.models import NodeRecord, RelationshipRecord
from food_kg.services.quality_gate import validate_release_gate

def read_json(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--nodes", type=Path, required=True)
    parser.add_argument("--relationships", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True, help="Attested release manifest")
    args = parser.parse_args()
    load_dotenv()
    root = Path(__file__).parents[1]
    nodes = [NodeRecord.model_validate(item) for item in read_json(args.nodes)]
    relationships = [RelationshipRecord.model_validate(item) for item in read_json(args.relationships)]
    manifest = yaml.safe_load(args.manifest.read_text(encoding="utf-8"))
    registry = yaml.safe_load((root / "config/source_registry.yaml").read_text(encoding="utf-8"))
    policy = yaml.safe_load((root / "config/quality_gate.yaml").read_text(encoding="utf-8"))
    errors = validate_release_gate(nodes, relationships, manifest, registry, policy, root)
    if errors:
        raise ValueError("Automated quality gate rejected this release:\n- " + "\n- ".join(errors))
    importer = Neo4jImporter.from_environment(
        os.environ["NEO4J_URI"], os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"],
        os.getenv("NEO4J_DATABASE", "neo4j"),
    )
    try:
        stats = importer.import_release(
            nodes, relationships,
        )
        print(f"Merged {stats.nodes_merged} nodes and {stats.relationships_merged} relationships.")
    finally:
        importer.close()

if __name__ == "__main__":
    main()
