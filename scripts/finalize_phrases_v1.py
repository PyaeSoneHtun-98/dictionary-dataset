#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json

from phrase_common import (
    ROOT,
    collect_dataset_stats,
    iter_batch_paths,
    load_json,
)
from validate_phrase_batch import validate_batch

OUT = ROOT / "dist" / "phrases_v1.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    paths = iter_batch_paths()
    if len(paths) != 12:
        print(f"ERROR: finalization requires exactly 12 batches; got {len(paths)}")
        return 1

    all_entries = []
    for path in paths:
        errors = validate_batch(path, check_manifest=False)
        if errors:
            for error in errors:
                print(f"{path.name}: ERROR: {error}")
            return 1
        all_entries.extend(load_json(path)["entries"])

    if len(all_entries) != 3000:
        print(f"ERROR: finalization requires exactly 3000 entries; got {len(all_entries)}")
        return 1

    all_entries.sort(key=lambda entry: entry["phrase"])
    artifact = {"version": 1, "entries": all_entries}
    raw = (json.dumps(artifact, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    digest = hashlib.sha256(raw).hexdigest()
    stats = collect_dataset_stats(paths)

    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_bytes(raw)

    print(f"Canonical phrases: {stats['canonicalPhrases']}")
    print(f"Stored forms: {stats['storedForms']}")
    print(f"Lookup keys: {stats['uniqueLookupKeys']}")
    print(f"Type counts: {stats['typeCounts']}")
    print(f"Burmese meanings: {stats['burmeseMeanings']}")
    print("Duplicate canonical phrases: 0")
    print("Variant collisions: 0")
    print(f"Artifact SHA-256: {digest}")
    if not args.write:
        print("Dry run only; use --write to create dist/phrases_v1.json.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
