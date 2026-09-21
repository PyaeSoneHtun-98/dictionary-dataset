#!/usr/bin/env python3
from __future__ import annotations

import argparse

from phrase_common import (
    PHRASE_LOOKUP_PATH,
    PHRASE_MANIFEST_PATH,
    collect_dataset_stats,
    encode_lookup_keys,
    iter_batch_paths,
    load_json,
    lookup_b64_sha256,
    write_json,
)
from validate_phrase_batch import validate_batch


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write lookup and manifest updates")
    args = parser.parse_args()

    paths = iter_batch_paths()
    for path in paths:
        errors = validate_batch(path, check_manifest=False)
        if errors:
            for error in errors:
                print(f"{path.name}: ERROR: {error}")
            return 1

    numbers = [load_json(path)["batch"] for path in paths]
    expected_numbers = list(range(1, len(paths) + 1))
    if numbers != expected_numbers:
        print(f"ERROR: phrase batches must be contiguous from 001; got {numbers}")
        return 1

    stats = collect_dataset_stats(paths)
    encoded = encode_lookup_keys(stats["lookupKeys"])

    if args.write:
        PHRASE_LOOKUP_PATH.parent.mkdir(parents=True, exist_ok=True)
        PHRASE_LOOKUP_PATH.write_text(encoded + "\n", encoding="utf-8", newline="\n")

        manifest = load_json(PHRASE_MANIFEST_PATH)
        batch_count = len(paths)
        latest = batch_count
        target_batches = manifest["targetBatches"]
        manifest["latestBatch"] = latest
        manifest["nextBatch"] = latest + 1 if latest < target_batches else None
        manifest["batchCount"] = batch_count
        manifest["totalPhrases"] = stats["canonicalPhrases"]
        manifest["typeCounts"] = stats["typeCounts"]
        manifest["status"] = "complete" if latest == target_batches else "in_progress"
        manifest["lookup"] = {
            "path": "phrase_lookup/used_phrase_keys_current.zlib.b64",
            "encoding": "base64(zlib(utf8 newline-separated keys))",
            "throughBatch": latest,
            "uniqueLookupKeys": stats["uniqueLookupKeys"],
            "canonicalPhrases": stats["canonicalPhrases"],
            "storedForms": stats["storedForms"],
            "sha256": lookup_b64_sha256(encoded),
            "sha256Scope": "base64-trimmed",
        }
        write_json(PHRASE_MANIFEST_PATH, manifest)

    print(
        f"PASS batches={len(paths)} canonical={stats['canonicalPhrases']} "
        f"forms={stats['storedForms']} lookupKeys={stats['uniqueLookupKeys']} "
        f"types={stats['typeCounts']}"
    )
    if not args.write:
        print("Dry run only; use --write to update lookup and manifest.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
