from pathlib import Path

from food_kg.models import NodeRecord
from food_kg.services.quality_gate import validate_release_gate


def test_rejects_draft_nodes_and_unattested_manifest(tmp_path: Path) -> None:
    node = NodeRecord(label="Source", id="SOURCE:TEST", properties={"name": "Test", "source": "SOURCE:TEST", "source_url": "https://example.test", "reviewed_at": "2026-06-22", "status": "draft"})
    errors = validate_release_gate([node], [], {"source_ids": ["SOURCE:TEST"]}, {"sources": [{"id": "SOURCE:TEST", "url": "https://example.test"}]}, {"required_release_fields": ["version", "released_at", "source_ids", "raw_snapshot", "automated_gate"], "policy_version": "strict-v1", "allowed_statuses": ["active"], "require_source_node_for_every_source": True, "require_raw_snapshot_hashes": False, "required_node_properties": ["source", "source_url", "reviewed_at", "status"]}, tmp_path)
    assert any("status is not eligible" in error for error in errors)
    assert any("not attested" in error for error in errors)
