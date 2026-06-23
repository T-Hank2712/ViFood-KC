"""Remove legacy FAO/INFOODS Alias nodes superseded by Nutrient.external_code."""

from __future__ import annotations

import argparse
import os

from dotenv import load_dotenv
from neo4j import GraphDatabase


SOURCE_ID = "SOURCE:FAO_INFOODS_TAGNAMES"
MATCH = """
MATCH (alias:Alias {source: $source_id})-[:REFERS_TO]->(:Nutrient)
RETURN count(DISTINCT alias) AS count
"""
DELETE = """
MATCH (alias:Alias {source: $source_id})-[:REFERS_TO]->(:Nutrient)
WITH DISTINCT alias
DETACH DELETE alias
RETURN count(alias) AS deleted
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Delete only legacy INFOODS external-code aliases for Nutrient nodes")
    parser.add_argument("--apply", action="store_true", help="Perform deletion; omit for a dry run")
    args = parser.parse_args()
    load_dotenv()
    driver = GraphDatabase.driver(os.environ["NEO4J_URI"], auth=(os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"]))
    try:
        with driver.session(database=os.getenv("NEO4J_DATABASE", "neo4j")) as session:
            if args.apply:
                deleted = session.run(DELETE, source_id=SOURCE_ID).single()["deleted"]
                print(f"Deleted {deleted} legacy nutrient external-code Alias nodes.")
            else:
                count = session.run(MATCH, source_id=SOURCE_ID).single()["count"]
                print(f"Dry run: would delete {count} legacy nutrient external-code Alias nodes.")
    finally:
        driver.close()


if __name__ == "__main__":
    main()
