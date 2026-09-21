#!/usr/bin/env python3
from __future__ import annotations

import base64
import hashlib
import json
import re
import unicodedata
import zlib
from collections import Counter
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
PHRASE_BATCH_DIR = ROOT / "PhraseBatches"
PHRASE_LOOKUP_PATH = ROOT / "phrase_lookup" / "used_phrase_keys_current.zlib.b64"
PHRASE_MANIFEST_PATH = ROOT / "phrase_manifest.json"
ALLOWED_TYPES = {"phrasal_verb", "idiom", "expression"}
BATCH_RE = re.compile(r"^phrase_batch_(\d{3})\.json$")
PLACEHOLDER_RE = re.compile(
    r"[\[\]{}<>]|(?:someone|somebody|something)/(?:someone|somebody|something)",
    re.IGNORECASE,
)


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write("\n")


def normalize_key(value: str) -> str:
    value = unicodedata.normalize("NFKC", value)
    return " ".join(value.split()).casefold()


def token_count(value: str) -> int:
    return len(value.split())


def batch_number_from_path(path: Path) -> int:
    match = BATCH_RE.match(path.name)
    if not match:
        raise ValueError(
            f"Invalid phrase batch filename: {path.name}; expected phrase_batch_XXX.json"
        )
    return int(match.group(1))


def iter_batch_paths() -> list[Path]:
    if not PHRASE_BATCH_DIR.exists():
        return []
    return sorted(
        (p for p in PHRASE_BATCH_DIR.glob("phrase_batch_*.json") if BATCH_RE.match(p.name)),
        key=batch_number_from_path,
    )


def load_lookup_keys(path: Path = PHRASE_LOOKUP_PATH) -> set[str]:
    if not path.exists():
        return set()
    encoded = path.read_text(encoding="utf-8").strip()
    if not encoded:
        return set()
    raw = zlib.decompress(base64.b64decode(encoded)).decode("utf-8")
    return {line for line in raw.splitlines() if line}


def encode_lookup_keys(keys: Iterable[str]) -> str:
    raw = "\n".join(sorted(set(keys))).encode("utf-8")
    return base64.b64encode(zlib.compress(raw, level=9)).decode("ascii")


def lookup_b64_sha256(encoded: str) -> str:
    return hashlib.sha256(encoded.strip().encode("ascii")).hexdigest()


def collect_dataset_stats(batch_paths: Iterable[Path]) -> dict:
    canonical = 0
    stored_forms = 0
    meanings = 0
    type_counts = Counter()
    lookup_keys: set[str] = set()
    for path in batch_paths:
        data = load_json(path)
        for entry in data.get("entries", []):
            canonical += 1
            type_counts[entry["type"]] += 1
            meanings += len(entry["burmese"])
            canonical_key = normalize_key(entry["phrase"])
            lookup_keys.add(canonical_key)
            for form in entry["forms"]:
                stored_forms += 1
                lookup_keys.add(normalize_key(form))
    return {
        "canonicalPhrases": canonical,
        "storedForms": stored_forms,
        "burmeseMeanings": meanings,
        "uniqueLookupKeys": len(lookup_keys),
        "lookupKeys": lookup_keys,
        "typeCounts": {
            key: type_counts.get(key, 0)
            for key in ("phrasal_verb", "idiom", "expression")
        },
    }
