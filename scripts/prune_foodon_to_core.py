"""Remove FoodOn taxonomy records outside a curated core release after that release is imported."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase


def load_ids(nodes_file: Path) -> tuple[list[str], list[str]]:
    nodes = json.loads(nodes_file.read_text(encoding="utf-8"))
    categories = [node["id"] for node in nodes if node["label"] == "FoodCategory"]
    aliases = [node["id"] for node in nodes if node["label"] == "Alias"]
    if not categories:
        raise ValueError("Core release contains no FoodCategory nodes")
    return categories, aliases


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--nodes", type=Path, required=True, help="Curated core nodes JSON")
    parser.add_argument("--apply", action="store_true", help="Perform deletion; omit for a dry-run count")
    args = parser.parse_args()
    category_ids, alias_ids = load_ids(args.nodes)
    load_dotenv()
    driver = GraphDatabase.driver(os.environ["NEO4J_URI"], auth=(os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"]))
    database = os.getenv("NEO4J_DATABASE", "neo4j")
    category_filter = "c.source = 'SOURCE:FOODON' AND NOT c.id IN $keep_ids"
    alias_filter = "a.source IN ['SOURCE:FOODON', 'SOURCE:VIFOOD_TRANSLATION_SEED'] AND NOT a.id IN $keep_ids"
    try:
        with driver.session(database=database) as session:
            categories = session.run(f"MATCH (c:FoodCategory) WHERE {category_filter} RETURN count(c) AS count", keep_ids=category_ids).single()["count"]
            aliases = session.run(f"MATCH (a:Alias) WHERE {alias_filter} RETURN count(a) AS count", keep_ids=alias_ids).single()["count"]
            if not args.apply:
                print(f"Dry run: would delete {categories} FoodCategory nodes and {aliases} FoodOn/translation Alias nodes.")
                return
            deleted_categories = session.run(f"MATCH (c:FoodCategory) WHERE {category_filter} DETACH DELETE c", keep_ids=category_ids).consume().counters.nodes_deleted
            deleted_aliases = session.run(f"MATCH (a:Alias) WHERE {alias_filter} DETACH DELETE a", keep_ids=alias_ids).consume().counters.nodes_deleted
            print(f"Deleted {deleted_categories} FoodCategory nodes and {deleted_aliases} Alias nodes outside the FoodOn knowledge core.")
    finally:
        driver.close()


if __name__ == "__main__":
    main()
