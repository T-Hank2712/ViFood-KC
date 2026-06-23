"""Remove Vietnam Additive nodes with no permitted packaged-food use in the graph."""

from __future__ import annotations

import argparse
import os

from dotenv import load_dotenv
from neo4j import GraphDatabase

SOURCE_ID = "SOURCE:VN_VBHN_09_2024"
COUNT = """
MATCH (a:Additive {source: $source_id})
WHERE NOT (a)-[:PERMITTED_IN]->(:FoodCategory)
RETURN count(a) AS count
"""
DELETE = """
MATCH (a:Additive {source: $source_id})
WHERE NOT (a)-[:PERMITTED_IN]->(:FoodCategory)
WITH collect(a) AS additives
UNWIND additives AS additive
DETACH DELETE additive
WITH size(additives) AS deleted
MATCH (f:FunctionalClass {source: $source_id})
WHERE NOT ()-[:HAS_FUNCTION]->(f)
WITH deleted, collect(f) AS orphan_functions
FOREACH (f IN orphan_functions | DETACH DELETE f)
RETURN deleted
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    load_dotenv()
    driver = GraphDatabase.driver(os.environ["NEO4J_URI"], auth=(os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"]))
    try:
        with driver.session(database=os.getenv("NEO4J_DATABASE", "neo4j")) as session:
            if args.apply:
                print(f"Deleted {session.run(DELETE, source_id=SOURCE_ID).single()['deleted']} unused packaged-food Additive nodes.")
            else:
                print(f"Dry run: would delete {session.run(COUNT, source_id=SOURCE_ID).single()['count']} unused packaged-food Additive nodes.")
    finally:
        driver.close()


if __name__ == "__main__":
    main()
