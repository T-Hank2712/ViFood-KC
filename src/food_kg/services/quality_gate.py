"""Strict automated admission checks for curated releases before Neo4j import."""

from __future__ import annotations

import hashlib
from pathlib import Path
from urllib.parse import urlparse

import yaml

from food_kg.models import NodeRecord, RelationshipRecord
from food_kg.validators import validate_curated_graph


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_release_gate(nodes: list[NodeRecord], relationships: list[RelationshipRecord], manifest: dict, registry: dict, policy: dict, project_root: Path) -> list[str]:
    errors = validate_curated_graph(nodes, relationships)
    for field in policy["required_release_fields"]:
        if not manifest.get(field):
            errors.append(f"Release manifest missing required field: {field}")
    if manifest.get("automated_gate", {}).get("policy_version") != policy["policy_version"]:
        errors.append("Release manifest is not attested with the current quality-gate policy")
    if manifest.get("automated_gate", {}).get("ambiguous_alias_count", 0) != 0:
        errors.append("Release contains ambiguous aliases")
    registry_sources = {source["id"]: source for source in registry.get("sources", [])}
    release_sources = set(manifest.get("source_ids", []))
    source_nodes = {node.id for node in nodes if node.label == "Source"}
    for node in nodes:
        source_id = node.properties.get("source")
        if source_id not in registry_sources:
            errors.append(f"{node.id}: source is absent from trusted source registry ({source_id})")
        if source_id not in release_sources:
            errors.append(f"{node.id}: source is absent from release manifest ({source_id})")
        if policy["require_source_node_for_every_source"] and source_id not in source_nodes:
            errors.append(f"{node.id}: source node is absent from release ({source_id})")
        if node.properties.get("status") not in policy["allowed_statuses"]:
            errors.append(f"{node.id}: status is not eligible for automated import")
        for field in policy["required_node_properties"]:
            if not node.properties.get(field):
                errors.append(f"{node.id}: missing required gate property {field}")
    if policy["require_raw_snapshot_hashes"]:
        for item in manifest.get("raw_snapshot", {}).get("files", []):
            raw_path = project_root / item.get("path", "")
            if not raw_path.is_file():
                errors.append(f"Raw snapshot file is missing: {item.get('path')}")
            elif sha256(raw_path) != item.get("sha256"):
                errors.append(f"Raw snapshot hash mismatch: {item.get('path')}")
    return errors
