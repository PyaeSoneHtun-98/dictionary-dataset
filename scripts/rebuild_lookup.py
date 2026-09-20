#!/usr/bin/env python3
"""Rebuild the canonical cumulative lookup index from all batch JSON files."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import zlib
from pathlib import Path


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def detect_existing_hash_scope(index_path: Path, manifest_sha: str | None) -> str:
    if not index_path.exists() or not manifest_sha:
        return "logical-text"

    raw_file = index_path.read_bytes()
    try:
        b64_text = raw_file.decode("ascii").strip()
        compressed = base64.b64decode(b64_text)
        logical = zlib.decompress(compressed)
    except Exception:
        return "logical-text"

    candidates = {
        "logical-text": sha256_bytes(logical),
        "compressed-bytes": sha256_bytes(compressed),
        "base64-file": sha256_bytes(raw_file),
        "base64-trimmed": sha256_bytes(b64_text.encode("ascii")),
    }
    for scope, value in candidates.items():
        if value == manifest_sha:
            return scope
    return "logical-text"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batches", type=Path, default=Path("Batches"))
    ap.add_argument("--manifest", type=Path, default=Path("dictionary_manifest.json"))
    ap.add_argument(
        "--index",
        type=Path,
        default=Path("lookup/used_keys_current.zlib.b64"),
    )
    args = ap.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    old_lookup = manifest.get("lookup", {})
    old_sha = old_lookup.get("sha256") if isinstance(old_lookup, dict) else None
    hash_scope = detect_existing_hash_scope(args.index, old_sha)

    headwords: set[str] = set()
    forms: set[str] = set()

    batch_files = sorted(args.batches.glob("dictionary_batch_*.json"))
    if len(batch_files) != 60:
        raise SystemExit(f"Expected 60 batch files, found {len(batch_files)}")

    for path in batch_files:
        doc = json.loads(path.read_text(encoding="utf-8"))
        for entry in doc["entries"]:
            headwords.add(entry["word"].strip().casefold())
            for form in entry.get("forms", []):
                forms.add(form.strip().casefold())

    keys = sorted(headwords | forms)
    logical_text = ("\n".join(keys) + "\n").encode("utf-8")
    compressed = zlib.compress(logical_text, level=9)
    b64_text = base64.b64encode(compressed).decode("ascii") + "\n"
    args.index.parent.mkdir(parents=True, exist_ok=True)
    args.index.write_text(b64_text, encoding="ascii")

    raw_file = b64_text.encode("ascii")
    if hash_scope == "compressed-bytes":
        digest = sha256_bytes(compressed)
    elif hash_scope == "base64-file":
        digest = sha256_bytes(raw_file)
    elif hash_scope == "base64-trimmed":
        digest = sha256_bytes(b64_text.strip().encode("ascii"))
    else:
        hash_scope = "logical-text"
        digest = sha256_bytes(logical_text)

    lookup = manifest.setdefault("lookup", {})
    lookup["path"] = "lookup/used_keys_current.zlib.b64"
    lookup["encoding"] = "base64(zlib(utf8 newline-separated keys))"
    lookup["throughBatch"] = 60
    lookup["uniqueLookupKeys"] = len(keys)
    lookup["uniqueHeadwords"] = len(headwords)
    lookup["uniqueStoredForms"] = len(forms)
    lookup["sha256"] = digest
    lookup["sha256Scope"] = hash_scope

    args.manifest.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "batchFiles": len(batch_files),
                "uniqueHeadwords": len(headwords),
                "uniqueStoredForms": len(forms),
                "uniqueLookupKeys": len(keys),
                "sha256": digest,
                "sha256Scope": hash_scope,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
