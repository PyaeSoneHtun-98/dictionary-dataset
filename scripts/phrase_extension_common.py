"""Shared validation and deterministic snapshots for the separate phrase extension."""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

from phrase_common import (
    ROOT, encode_lookup_keys, iter_batch_paths, load_json, load_lookup_keys,
    lookup_b64_sha256, normalize_key,
)
from validate_phrase_batch import validate_entry

BATCH_DIR = ROOT / "PhraseExtensionBatches"
MANIFEST = ROOT / "phrase_extension_manifest.json"
INDEX = ROOT / "phrase_extension_lookup/used_phrase_keys_current.zlib.b64"
ARTIFACT = ROOT / "dist/phrases_extension.json"
METADATA = ROOT / "dist/phrases_extension.metadata.json"
BATCH_RE = re.compile(r"^phrase_batch_(\d{3})\.json$")
SURFACE_TOKEN = r"[a-z]+(?:['’-][a-z]+)*['’]?"
SURFACE_RE = re.compile(SURFACE_TOKEN + r"(?: " + SURFACE_TOKEN + r")+")
MYANMAR_RE = re.compile(r"[\u1000-\u102a\u103f\u1050-\u1055]")


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def extension_paths() -> list[Path]:
    paths = sorted(BATCH_DIR.glob("phrase_batch_*.json"))
    if any(not BATCH_RE.fullmatch(p.name) for p in paths):
        raise ValueError("Malformed phrase extension batch filename")
    return paths


def base_dataset() -> tuple[dict[str, str], dict, list[dict]]:
    manifest = load_json(ROOT / "phrase_manifest.json")
    release = manifest["release"]
    if release["status"] != "frozen" or release["canonicalPhrases"] != 3000:
        raise ValueError("Expected frozen Phrase Dictionary v1.0.0 with 3,000 phrases")
    artifact_path = ROOT / release["artifact"]
    raw = artifact_path.read_text(encoding="utf-8").encode("utf-8")
    if hashlib.sha256(raw).hexdigest() != release["artifactSha256"]:
        raise ValueError("Frozen phrase artifact hash mismatch")
    artifact = json.loads(raw)
    paths = iter_batch_paths()
    if [load_json(p)["batch"] for p in paths] != list(range(1, 13)):
        raise ValueError("Frozen phrase source must contain batches 001–012")
    source = [e for p in paths for e in load_json(p)["entries"]]
    if artifact != {"version": 1, "entries": sorted(source, key=lambda e: e["phrase"])}:
        raise ValueError("Frozen phrase source and artifact differ")
    if len(source) != 3000:
        raise ValueError("Frozen phrase source count mismatch")
    owners: dict[str, str] = {}
    for entry in source:
        for surface in [entry["phrase"], *entry["forms"]]:
            key = normalize_key(surface)
            if key in owners:
                raise ValueError(f"Frozen phrase collision: {key!r}")
            owners[key] = "phrase-v1:" + entry["phrase"]
    index_path = ROOT / manifest["lookup"]["path"]
    if set(owners) != load_lookup_keys(index_path):
        raise ValueError("Frozen phrase source and lookup differ")
    if lookup_b64_sha256(index_path.read_text(encoding="ascii")) != manifest["lookup"]["sha256"]:
        raise ValueError("Frozen phrase lookup hash mismatch")
    return owners, manifest, source


def validate_entries(entries: list, owners: dict[str, str]) -> list[str]:
    errors: list[str] = []
    for i, entry in enumerate(entries, 1):
        validate_entry(entry, i, owners, errors)
        if not isinstance(entry, dict):
            continue
        phrase = entry.get("phrase", "")
        surfaces = [phrase]
        if isinstance(entry.get("forms"), list):
            surfaces.extend(entry["forms"])
        for surface in surfaces:
            if not isinstance(surface, str):
                continue
            if surface != normalize_key(surface) or not SURFACE_RE.fullmatch(surface):
                errors.append(f"entry {i}: invalid English surface {surface!r}")
            if any(unicodedata.category(c) in {"Cc", "Cf"} for c in surface):
                errors.append(f"entry {i}: invisible/control character in surface")
        glosses = entry.get("burmese", [])
        if not isinstance(glosses, list):
            continue
        seen: set[str] = set()
        for gloss in glosses:
            if not isinstance(gloss, str):
                continue
            if re.search(r"[A-Za-z]", gloss) or not MYANMAR_RE.search(gloss):
                errors.append(f"entry {i} {phrase!r}: meaning must contain Burmese without English")
            if any(unicodedata.category(c) in {"Cc", "Cf"} for c in gloss):
                errors.append(f"entry {i} {phrase!r}: invisible/control character in meaning")
            if gloss in seen:
                errors.append(f"entry {i} {phrase!r}: duplicate Burmese meaning")
            seen.add(gloss)
    return errors


def read_batch(path: Path, expected: int, owners: dict[str, str]) -> list[dict]:
    if path.name != f"phrase_batch_{expected:03d}.json" or expected < 13:
        raise ValueError(f"Expected extension batch {expected:03d}: {path.name}")
    data = load_json(path)
    if not isinstance(data, dict) or set(data) != {"version", "batch", "entries"}:
        raise ValueError(f"{path.name}: invalid batch schema")
    if type(data["version"]) is not int or data["version"] != 1:
        raise ValueError(f"{path.name}: version must be integer 1")
    if type(data["batch"]) is not int or data["batch"] != expected:
        raise ValueError(f"{path.name}: batch metadata mismatch")
    entries = data["entries"]
    if not isinstance(entries, list) or len(entries) != 250:
        raise ValueError(f"{path.name}: expected exactly 250 entries")
    errors = validate_entries(entries, owners)
    if errors:
        raise ValueError(f"{path.name}: " + "\n".join(errors))
    return entries


def snapshots() -> tuple[dict, str, bytes, dict]:
    owners, base_manifest, base = base_dataset()
    entries: list[dict] = []
    paths = extension_paths()
    for number, path in enumerate(paths, 13):
        entries.extend(read_batch(path, number, owners))
    ordered = sorted(entries, key=lambda e: e["phrase"])
    raw = json_bytes({"version": 1, "entries": ordered})
    encoded = encode_lookup_keys(owners)
    types = Counter(e["type"] for e in entries)
    base_types = Counter(e["type"] for e in base)
    forms = sum(len(e["forms"]) for e in entries)
    meanings = sum(len(e["burmese"]) for e in entries)
    latest = 12 + len(paths)
    manifest = {
        "version": 1,
        "project": "Subtitle Bridge English-Burmese Phrase Dictionary Extension",
        "baseRelease": {
            "version": base_manifest["release"]["version"],
            "canonicalPhrases": len(base), "batches": 12,
            "artifact": "dist/phrases_v1.json",
            "artifactSha256": base_manifest["release"]["artifactSha256"],
            "lookupKeys": len(load_lookup_keys()),
        },
        "entriesPerBatch": 250, "latestBatch": latest, "nextBatch": latest + 1,
        "extensionBatchCount": len(paths), "extensionPhrases": len(entries),
        "totalPhrases": len(base) + len(entries), "extensionStoredForms": forms,
        "extensionBurmeseMeanings": meanings,
        "extensionTypeCounts": {t: types[t] for t in sorted(base_types)},
        "totalTypeCounts": {t: types[t] + base_types[t] for t in sorted(base_types)},
        "batchFilenamePattern": "PhraseExtensionBatches/phrase_batch_XXX.json",
        "status": "in_progress",
        "lookup": {
            "path": "phrase_extension_lookup/used_phrase_keys_current.zlib.b64",
            "baseLookup": "phrase_lookup/used_phrase_keys_current.zlib.b64",
            "encoding": "base64(zlib(utf8 newline-separated keys))",
            "throughBatch": latest, "uniqueLookupKeys": len(owners),
            "sha256": lookup_b64_sha256(encoded), "sha256Scope": "base64-trimmed",
        },
    }
    metadata = {
        "version": 1, "artifact": "dist/phrases_extension.json",
        "sha256": hashlib.sha256(raw).hexdigest(), "sha256Scope": "utf8-lf",
        "throughBatch": latest, "canonicalPhrases": len(entries),
        "storedForms": forms, "lookupKeys": len(entries) + forms,
        "burmeseMeanings": meanings, "typeCounts": manifest["extensionTypeCounts"],
        "baseArtifactSha256": manifest["baseRelease"]["artifactSha256"],
    }
    return manifest, encoded, raw, metadata


def write_or_check(path: Path, raw: bytes, write: bool) -> None:
    if write:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    elif not path.exists() or path.read_text(encoding="utf-8").encode("utf-8") != raw:
        raise ValueError(f"Stale or missing {path.relative_to(ROOT)}; run with --write")
