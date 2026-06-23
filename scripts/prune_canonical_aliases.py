"""Remove Alias nodes that duplicate an entity's canonical name or name_vi."""

from __future__ import annotations

import argparse
import os

from dotenv import load_dotenv
from neo4j import GraphDatabase


MATCH = """
MATCH (alias:Alias)-[:REFERS_TO]->(entity)
WHERE alias.name IS NOT NULL
  AND (toLower(trim(alias.name)) = toLower(trim(entity.name))
       OR (entity.name_vi IS NOT NULL AND toLower(trim(alias.name)) = toLower(trim(entity.name_vi))))
RETURN count(DISTINCT alias) AS count
"""
DELETE = """
MATCH (alias:Alias)-[:REFERS_TO]->(entity)
WHERE alias.name IS NOT NULL
  AND (toLower(trim(alias.name)) = toLower(trim(entity.name))
       OR (entity.name_vi IS NOT NULL AND toLower(trim(alias.name)) = toLower(trim(entity.name_vi))))
WITH DISTINCT alias
DETACH DELETE alias
RETURN count(alias) AS deleted
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Delete only aliases that duplicate a canonical name/name_vi")
    parser.add_argument("--apply", action="store_true", help="Perform deletion; omit for a dry run")
    args = parser.parse_args()
    load_dotenv()
    driver = GraphDatabase.driver(os.environ["NEO4J_URI"], auth=(os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"]))
    try:
        with driver.session(database=os.getenv("NEO4J_DATABASE", "neo4j")) as session:
            if args.apply:
                deleted = session.run(DELETE).single()["deleted"]
                print(f"Deleted {deleted} canonical-duplicate Alias nodes.")
            else:
                count = session.run(MATCH).single()["count"]
                print(f"Dry run: would delete {count} canonical-duplicate Alias nodes.")
    finally:
        driver.close()


if __name__ == "__main__":
    main()
