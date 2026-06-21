"""Import one reviewed curated release. Raw/staging data is deliberately unsupported."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv

from food_kg.graph import Neo4jImporter
from food_kg.models import NodeRecord, RelationshipRecord

def read_json(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--nodes", type=Path, required=True)
    parser.add_argument("--relationships", type=Path, required=True)
    args = parser.parse_args()
    load_dotenv()
    importer = Neo4jImporter.from_environment(
        os.environ["NEO4J_URI"], os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"],
        os.getenv("NEO4J_DATABASE", "neo4j"),
    )
    try:
        stats = importer.import_release(
            [NodeRecord.model_validate(item) for item in read_json(args.nodes)],
            [RelationshipRecord.model_validate(item) for item in read_json(args.relationships)],
        )
        print(f"Merged {stats.nodes_merged} nodes and {stats.relationships_merged} relationships.")
    finally:
        importer.close()

if __name__ == "__main__":
    main()
