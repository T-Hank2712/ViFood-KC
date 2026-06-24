import json
import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

from food_kg.graph import Neo4jImporter
from food_kg.models import NodeRecord, RelationshipRecord

load_dotenv()

pytestmark = pytest.mark.skipif(not all(os.getenv(k) for k in ("NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD")), reason="Neo4j environment is not configured")

ROOT = Path(__file__).parents[2]

def load(relative: str, model):
    return [model.model_validate(item) for item in json.loads((ROOT / relative).read_text())]

def test_nutrient_release_import_is_idempotent() -> None:
    importer = Neo4jImporter.from_environment(os.environ["NEO4J_URI"], os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"], os.getenv("NEO4J_DATABASE", "neo4j"))
    nodes = load("data/curated/nodes/nutrients_vietnam_infoods_v0.2.0.json", NodeRecord)
    relationships = load("data/curated/relationships/nutrients_vietnam_infoods_v0.2.0.json", RelationshipRecord)
    try:
        importer.import_release(nodes, relationships)
        importer.import_release(nodes, relationships)
        with importer.driver.session(database=importer.database) as session:
            count = session.run("MATCH (n:Nutrient) WHERE n.source = 'SOURCE:FAO_INFOODS_TAGNAMES' RETURN count(n) AS count").single()["count"]
        assert count == 21
    finally:
        importer.close()
