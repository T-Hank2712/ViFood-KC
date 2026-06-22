"""Attach source-file hashes and automated-gate metadata to a curated release manifest."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import yaml


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--raw-file", type=Path, action="append", required=True)
    parser.add_argument("--ambiguous-alias-count", type=int, default=0)
    args = parser.parse_args()
    root = Path.cwd().resolve()
    manifest = yaml.safe_load(args.manifest.read_text(encoding="utf-8"))
    manifest["raw_snapshot"] = {"files": [{"path": str(path.resolve().relative_to(root)), "sha256": file_hash(path)} for path in args.raw_file]}
    manifest["automated_gate"] = {"policy_version": "strict-v1", "ambiguous_alias_count": args.ambiguous_alias_count}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False), encoding="utf-8")
    print(f"Attested release manifest: {args.output}")


if __name__ == "__main__":
    main()
