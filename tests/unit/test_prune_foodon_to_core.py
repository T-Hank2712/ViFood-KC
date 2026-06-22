import json

from scripts.prune_foodon_to_core import load_ids


def test_load_ids_reads_only_category_and_alias_ids(tmp_path) -> None:
    nodes = tmp_path / "nodes.json"
    nodes.write_text(json.dumps([
        {"label": "FoodCategory", "id": "CATEGORY:FOODON_1"},
        {"label": "Alias", "id": "ALIAS:FOODON_1"},
        {"label": "Source", "id": "SOURCE:FOODON"},
    ]))
    assert load_ids(nodes) == (["CATEGORY:FOODON_1"], ["ALIAS:FOODON_1"])
