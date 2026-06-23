"""Remove legacy INS Alias nodes superseded by Additive.ins."""

from __future__ import annotations

import argparse
import os

from dotenv import load_dotenv
from neo4j import GraphDatabase


SOURCE_ID = "SOURCE:VN_VBHN_09_2024"
MATCH = """
MATCH (alias:Alias {source: $source_id, alias_type: 'ins-code'})-[:REFERS_TO]->(:Additive)
RETURN count(DISTINCT alias) AS count
"""
DELETE = """
MATCH (alias:Alias {source: $source_id, alias_type: 'ins-code'})-[:REFERS_TO]->(:Additive)
WITH DISTINCT alias
DETACH DELETE alias
RETURN count(alias) AS deleted
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Delete only legacy INS aliases for Additive nodes")
    parser.add_argument("--apply", action="store_true", help="Perform deletion; omit for a dry run")
    args = parser.parse_args()
    load_dotenv()
    driver = GraphDatabase.driver(os.environ["NEO4J_URI"], auth=(os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"]))
    try:
        with driver.session(database=os.getenv("NEO4J_DATABASE", "neo4j")) as session:
            if args.apply:
                deleted = session.run(DELETE, source_id=SOURCE_ID).single()["deleted"]
                print(f"Deleted {deleted} legacy additive INS Alias nodes.")
            else:
                count = session.run(MATCH, source_id=SOURCE_ID).single()["count"]
                print(f"Dry run: would delete {count} legacy additive INS Alias nodes.")
    finally:
        driver.close()


if __name__ == "__main__":
    main()
