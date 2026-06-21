"""The only component that writes curated records to Neo4j."""

from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable

from neo4j import Driver, GraphDatabase

from food_kg.models import NodeRecord, RelationshipRecord
from food_kg.validators import validate_curated_graph

logger = logging.getLogger(__name__)

@dataclass
class ImportStats:
    nodes_merged: int = 0
    relationships_merged: int = 0
    failed: int = 0

class Neo4jImporter:
    def __init__(self, driver: Driver, database: str = "neo4j", batch_size: int = 500) -> None:
        self.driver, self.database, self.batch_size = driver, database, batch_size

    @classmethod
    def from_environment(cls, uri: str, user: str, password: str, database: str = "neo4j") -> "Neo4jImporter":
        return cls(GraphDatabase.driver(uri, auth=(user, password)), database)

    def close(self) -> None:
        self.driver.close()

    def import_release(self, nodes: Iterable[NodeRecord], relationships: Iterable[RelationshipRecord]) -> ImportStats:
        nodes, relationships = list(nodes), list(relationships)
        errors = validate_curated_graph(nodes, relationships)
        if errors:
            raise ValueError("Curated release is invalid:\n- " + "\n- ".join(errors))
        stats = ImportStats()
        grouped: dict[str, list[NodeRecord]] = defaultdict(list)
        for node in nodes:
            grouped[node.label].append(node)
        with self.driver.session(database=self.database) as session:
            for label, records in grouped.items():
                for batch in _batches(records, self.batch_size):
                    query = (
                        f"UNWIND $rows AS row MERGE (n:`{label}` {{id: row.id}}) "
                        "ON CREATE SET n.created_at = datetime() "
                        "SET n += row.properties, n.updated_at = datetime()"
                    )
                    session.run(query, rows=[r.model_dump() for r in batch]).consume()
                    stats.nodes_merged += len(batch)
            relationship_groups: dict[str, list[RelationshipRecord]] = defaultdict(list)
            for relationship in relationships:
                relationship_groups[relationship.type].append(relationship)
            for relationship_type, records in relationship_groups.items():
                for batch in _batches(records, self.batch_size):
                    query = (
                        "UNWIND $rows AS row "
                        "MATCH (start {id: row.start_id}), (end {id: row.end_id}) "
                        f"MERGE (start)-[r:`{relationship_type}`]->(end) "
                        "ON CREATE SET r.created_at = datetime() "
                        "SET r += row.properties, r.updated_at = datetime()"
                    )
                    session.run(query, rows=[r.model_dump() for r in batch]).consume()
                    stats.relationships_merged += len(batch)
        logger.info("Neo4j import complete: nodes=%d relationships=%d failed=%d", stats.nodes_merged, stats.relationships_merged, stats.failed)
        return stats

def _batches(records: list[NodeRecord] | list[RelationshipRecord], size: int) -> Iterable[list]:
    for index in range(0, len(records), size):
        yield records[index:index + size]
