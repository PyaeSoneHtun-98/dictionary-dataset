#!/usr/bin/env python3
"""Rebuild the cumulative lookup for the post-v1 dictionary extension."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import zlib
from pathlib import Path

BATCH_RE = re.compile(r"^dictionary_batch_(\d{3})\.json$")


def norm(value: str) -> str:
    return value.strip().casefold()


def decode_lookup(path: Path) -> set[str]:
    encoded = path.read_text(encoding="ascii").strip()
    logical = zlib.decompress(base64.b64decode(encoded)).decode("utf-8")
    return {norm(line) for line in logical.splitlines() if line.strip()}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-lookup", type=Path, default=Path("lookup/used_keys_current.zlib.b64"))
    ap.add_argument("--batches", type=Path, default=Path("DictionaryExtensionBatches"))
    ap.add_argument("--manifest", type=Path, default=Path("dictionary_extension_manifest.json"))
    ap.add_argument("--index", type=Path, default=Path("extension_lookup/used_keys_current.zlib.b64"))
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    base_keys = decode_lookup(args.base_lookup)
    keys = set(base_keys)
    owners = {key: "dictionary-v1" for key in base_keys}

    batch_files = sorted(args.batches.glob("dictionary_batch_*.json")) if args.batches.exists() else []
    expected = 61
    extension_headwords: set[str] = set()
    extension_forms: set[str] = set()

    for path in batch_files:
        match = BATCH_RE.match(path.name)
        if not match:
            raise SystemExit(f"Malformed extension batch filename: {path.name}")
        number = int(match.group(1))
        if number != expected:
            raise SystemExit(f"Extension batches must be contiguous: expected {expected:03d}, found {number:03d}")
        expected += 1

        doc = json.loads(path.read_text(encoding="utf-8"))
        if doc.get("version") != 1 or doc.get("batch") != number:
            raise SystemExit(f"{path.name}: version/batch metadata mismatch")
        entries = doc.get("entries", [])
        if len(entries) != 500:
            raise SystemExit(f"{path.name}: expected 500 entries, found {len(entries)}")

        for entry in entries:
            word = norm(entry["word"])
            if word in owners:
                raise SystemExit(f"Lookup collision for headword {word!r}: already owned by {owners[word]}")
            owners[word] = f"batch-{number:03d}:{word}"
            keys.add(word)
            extension_headwords.add(word)

            for form_value in entry.get("forms", []):
                form = norm(form_value)
                if form in owners:
                    raise SystemExit(f"Lookup collision for form {form!r}: already owned by {owners[form]}")
                owners[form] = f"batch-{number:03d}:{word}"
                keys.add(form)
                extension_forms.add(form)

    ordered = sorted(keys)
    logical = ("\n".join(ordered) + "\n").encode("utf-8")
    compressed = zlib.compress(logical, level=9)
    b64 = base64.b64encode(compressed).decode("ascii") + "\n"
    digest = hashlib.sha256(b64.strip().encode("ascii")).hexdigest()

    latest = 60 + len(batch_files)
    expected_total_headwords = manifest["baseRelease"]["headwords"] + len(extension_headwords)
    expected_lookup = {
        "path": "extension_lookup/used_keys_current.zlib.b64",
        "encoding": "base64(zlib(utf8 newline-separated keys))",
        "baseLookup": "lookup/used_keys_current.zlib.b64",
        "throughBatch": latest,
        "uniqueLookupKeys": len(keys),
        "uniqueHeadwords": expected_total_headwords,
        "uniqueStoredForms": manifest["baseRelease"]["storedForms"] + len(extension_forms),
        "sha256": digest,
        "sha256Scope": "base64-trimmed",
    }

    updated = dict(manifest)
    updated["latestBatch"] = latest
    updated["nextBatch"] = latest + 1
    updated["extensionBatchCount"] = len(batch_files)
    updated["extensionHeadwords"] = len(extension_headwords)
    updated["totalHeadwords"] = expected_total_headwords
    updated["lookup"] = expected_lookup
    updated["status"] = "in_progress"

    summary = {
        "extensionBatchCount": len(batch_files),
        "latestBatch": latest,
        "nextBatch": latest + 1,
        "extensionHeadwords": len(extension_headwords),
        "totalHeadwords": expected_total_headwords,
        "extensionStoredForms": len(extension_forms),
        "uniqueLookupKeys": len(keys),
        "sha256": digest,
    }

    if args.write:
        args.index.parent.mkdir(parents=True, exist_ok=True)
        args.index.write_text(b64, encoding="ascii")
        args.manifest.write_text(
            json.dumps(updated, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    else:
        current_index = args.index.read_text(encoding="ascii") if args.index.exists() else None
        if current_index != b64:
            raise SystemExit("Extension lookup is stale; run with --write.")
        if manifest != updated:
            raise SystemExit("Extension manifest is stale; run with --write.")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
