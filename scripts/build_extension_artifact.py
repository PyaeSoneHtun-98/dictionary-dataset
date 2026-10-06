#!/usr/bin/env python3
"""Package the extension separately, after validating sources and lookup state."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = Path("dist/dictionary_extension.json")
METADATA = Path("dist/dictionary_extension.metadata.json")


def serialize(data: dict) -> bytes:
    return (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def build(root: Path) -> tuple[bytes, bytes]:
    """Read validated sources; this function never writes frozen or active assets."""
    files = sorted((root / "DictionaryExtensionBatches").glob("dictionary_batch_*.json"))
    for path in files:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/validate_extension_batch.py"), str(path)],
            cwd=root, capture_output=True, text=True, encoding="utf-8",
        )
        if result.returncode:
            raise ValueError(f"{path.name}: {result.stdout}{result.stderr}")
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/rebuild_extension_lookup.py")],
        cwd=root, capture_output=True, text=True, encoding="utf-8",
    )
    if result.returncode:
        raise ValueError(f"Extension state must be synchronized before packaging: {result.stdout}{result.stderr}")

    manifest = json.loads((root / "dictionary_extension_manifest.json").read_text(encoding="utf-8"))
    base = manifest["baseRelease"]
    # Frozen v1's recorded digest uses LF. Universal newline decoding handles
    # existing Windows checkouts without changing a byte of the frozen file.
    base_bytes = (root / base["artifact"]).read_text(encoding="utf-8").encode("utf-8")
    if hashlib.sha256(base_bytes).hexdigest() != base["artifactSha256"]:
        raise ValueError("Frozen v1 artifact does not match its recorded SHA-256")
    entries = [e for path in files for e in json.loads(path.read_text(encoding="utf-8"))["entries"]]
    entries.sort(key=lambda e: e["word"])
    if len(entries) != manifest["extensionHeadwords"]:
        raise ValueError("Manifest extension count does not match artifact sources")
    artifact = serialize({"version": 1, "entries": entries})
    forms = sum(len(e["forms"]) for e in entries)
    metadata = {
        "version": 1,
        "artifact": ARTIFACT.as_posix(),
        "sha256": hashlib.sha256(artifact).hexdigest(),
        "sha256Scope": "utf8-lf",
        "firstBatch": 61 if files else None,
        "throughBatch": manifest["latestBatch"],
        "batchCount": len(files),
        "headwords": len(entries),
        "storedForms": forms,
        "lookupKeys": len(entries) + forms,
        "burmeseMeanings": sum(len(m["burmese"]) for e in entries for m in e["meanings"]),
        "posBlockCounts": dict(sorted(Counter(m["partOfSpeech"] for e in entries for m in e["meanings"]).items())),
        "baseRelease": base,
        "combinedLookup": manifest["lookup"],
    }
    return artifact, serialize(metadata)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=ROOT)
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = ap.parse_args()
    root = args.root.resolve()
    try:
        artifact, metadata = build(root)
        for relative, content in [(ARTIFACT, artifact), (METADATA, metadata)]:
            path = root / relative
            if args.write:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
            elif args.check and (not path.exists() or path.read_bytes() != content):
                raise ValueError(f"{relative}: missing or stale; run with --write")
    except (ValueError, OSError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(metadata.decode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
