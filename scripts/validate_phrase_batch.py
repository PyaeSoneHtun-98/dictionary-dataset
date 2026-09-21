#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from phrase_common import (
    ALLOWED_TYPES,
    PHRASE_MANIFEST_PATH,
    PLACEHOLDER_RE,
    batch_number_from_path,
    iter_batch_paths,
    load_json,
    normalize_key,
    token_count,
)


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def validate_entry(entry, index: int, seen_keys: dict[str, str], errors: list[str]) -> None:
    where = f"entry {index}"
    if not isinstance(entry, dict):
        fail(errors, f"{where}: must be an object")
        return

    expected = {"phrase", "type", "forms", "burmese"}
    actual = set(entry)
    if actual != expected:
        fail(errors, f"{where}: fields must be exactly {sorted(expected)}; got {sorted(actual)}")

    phrase = entry.get("phrase")
    phrase_type = entry.get("type")
    forms = entry.get("forms")
    burmese = entry.get("burmese")

    if not isinstance(phrase, str) or not phrase:
        fail(errors, f"{where}: phrase must be a non-empty string")
        return

    canonical_norm = normalize_key(phrase)
    if phrase != canonical_norm:
        fail(errors, f"{where}: canonical phrase must be lowercase with normalized single spaces: {phrase!r}")
    if not 2 <= token_count(phrase) <= 5:
        fail(errors, f"{where}: canonical phrase must contain 2-5 tokens: {phrase!r}")
    if PLACEHOLDER_RE.search(phrase):
        fail(errors, f"{where}: placeholder syntax is forbidden: {phrase!r}")
    if phrase[-1:] in ".,!?;:":
        fail(errors, f"{where}: sentence-ending punctuation is forbidden: {phrase!r}")

    if phrase_type not in ALLOWED_TYPES:
        fail(errors, f"{where}: unsupported type {phrase_type!r}")

    if not isinstance(forms, list):
        fail(errors, f"{where}: forms must be an array")
        forms = []
    if not isinstance(burmese, list) or not 1 <= len(burmese) <= 3:
        fail(errors, f"{where}: burmese must contain 1-3 meanings")
        burmese = []

    for meaning_index, meaning in enumerate(burmese, start=1):
        if not isinstance(meaning, str) or not meaning.strip():
            fail(errors, f"{where}: burmese meaning {meaning_index} must be a non-empty string")
        elif meaning != meaning.strip():
            fail(errors, f"{where}: burmese meaning {meaning_index} has leading/trailing whitespace")

    local_keys: set[str] = set()
    owner = f"{where} canonical {phrase!r}"
    if canonical_norm in seen_keys:
        fail(errors, f"{where}: lookup collision {phrase!r} with {seen_keys[canonical_norm]}")
    else:
        seen_keys[canonical_norm] = owner
    local_keys.add(canonical_norm)

    for form_index, form in enumerate(forms, start=1):
        form_where = f"{where} form {form_index}"
        if not isinstance(form, str) or not form:
            fail(errors, f"{form_where}: must be a non-empty string")
            continue
        if form != " ".join(form.split()):
            fail(errors, f"{form_where}: whitespace must be normalized: {form!r}")
        if not 2 <= token_count(form) <= 5:
            fail(errors, f"{form_where}: must contain 2-5 tokens: {form!r}")
        if PLACEHOLDER_RE.search(form):
            fail(errors, f"{form_where}: placeholder syntax is forbidden: {form!r}")
        key = normalize_key(form)
        if key in local_keys:
            fail(errors, f"{form_where}: duplicates canonical phrase or another form after normalization: {form!r}")
        elif key in seen_keys:
            fail(errors, f"{form_where}: lookup collision {form!r} with {seen_keys[key]}")
        else:
            seen_keys[key] = f"{form_where} {form!r}"
        local_keys.add(key)


def load_prior_keys(current_path: Path) -> dict[str, str]:
    seen: dict[str, str] = {}
    current_number = batch_number_from_path(current_path)
    for path in iter_batch_paths():
        number = batch_number_from_path(path)
        if number >= current_number or path.resolve() == current_path.resolve():
            continue
        data = load_json(path)
        for i, entry in enumerate(data.get("entries", []), start=1):
            for surface in [entry.get("phrase"), *entry.get("forms", [])]:
                if not isinstance(surface, str):
                    continue
                key = normalize_key(surface)
                seen[key] = f"{path.name} entry {i} surface {surface!r}"
    return seen


def validate_batch(path: Path, check_manifest: bool = True) -> list[str]:
    errors: list[str] = []
    try:
        batch_number = batch_number_from_path(path)
    except ValueError as exc:
        return [str(exc)]

    try:
        data = load_json(path)
    except Exception as exc:
        return [f"Invalid UTF-8 JSON: {exc}"]

    if not isinstance(data, dict):
        return ["Batch root must be an object"]

    if set(data) != {"version", "batch", "entries"}:
        fail(errors, "Batch fields must be exactly: version, batch, entries")
    if data.get("version") != 1:
        fail(errors, "version must equal 1")
    if data.get("batch") != batch_number:
        fail(errors, f"batch field must equal filename batch number {batch_number}")

    entries = data.get("entries")
    if not isinstance(entries, list):
        fail(errors, "entries must be an array")
        entries = []
    if len(entries) != 250:
        fail(errors, f"batch must contain exactly 250 entries; got {len(entries)}")

    seen_keys = load_prior_keys(path)
    prior_keys = set(seen_keys)
    for index, entry in enumerate(entries, start=1):
        validate_entry(entry, index, seen_keys, errors)

    current_keys = set(seen_keys) - prior_keys
    if len(current_keys) < len(entries):
        fail(errors, "current batch has fewer unique lookup keys than canonical entries")

    if check_manifest and PHRASE_MANIFEST_PATH.exists():
        manifest = load_json(PHRASE_MANIFEST_PATH)
        next_batch = manifest.get("nextBatch")
        if next_batch is not None and batch_number != next_batch:
            fail(errors, f"manifest nextBatch is {next_batch}, but validating batch {batch_number}")
        if manifest.get("entriesPerBatch") != 250:
            fail(errors, "manifest entriesPerBatch must equal 250")
        expected_total = manifest.get("batchCount", 0) * 250
        if manifest.get("totalPhrases") != expected_total:
            fail(errors, "manifest cumulative total is inconsistent before this batch")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("batch", type=Path)
    parser.add_argument("--no-manifest-check", action="store_true")
    args = parser.parse_args()

    errors = validate_batch(args.batch, check_manifest=not args.no_manifest_check)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"FAILED: {len(errors)} validation error(s)", file=sys.stderr)
        return 1

    data = load_json(args.batch)
    type_counts = {t: 0 for t in sorted(ALLOWED_TYPES)}
    forms = 0
    for entry in data["entries"]:
        type_counts[entry["type"]] += 1
        forms += len(entry["forms"])
    print(
        f"PASS batch={data['batch']:03d} entries=250 forms={forms} "
        + " ".join(f"{k}={v}" for k, v in type_counts.items())
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
