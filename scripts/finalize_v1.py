#!/usr/bin/env python3
"""Whole-corpus audit and deterministic v1 candidate builder for Subtitle Bridge."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ALLOWED_POS = {
    "noun", "verb", "adjective", "adverb", "pronoun", "preposition",
    "conjunction", "interjection", "determiner", "modal", "auxiliary",
}
BATCH_RE = re.compile(r"^dictionary_batch_(\d{3})\.json$")
ASCII_LETTER = re.compile(r"[A-Za-z]")
LEGACY_KEY_RE = re.compile(r"^\s{2}([a-z][a-z']*):\s*\{", re.MULTILINE)


def norm(value: str) -> str:
    return value.strip().casefold()


def load_legacy_headwords(path: Path | None) -> list[str]:
    if path is None or not path.exists():
        return []
    return sorted(set(LEGACY_KEY_RE.findall(path.read_text(encoding="utf-8"))))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batches", type=Path, default=Path("Batches"))
    ap.add_argument("--manifest", type=Path, default=Path("dictionary_manifest.json"))
    ap.add_argument("--legacy-ts", type=Path)
    ap.add_argument("--report-json", type=Path, default=Path("finalization_report.json"))
    ap.add_argument("--report-md", type=Path, default=Path("finalization_report.md"))
    ap.add_argument("--candidate", type=Path, default=Path("dictionary_v1_candidate.json"))
    args = ap.parse_args()

    blocking: list[str] = []
    warnings: list[str] = []
    batch_files = sorted(args.batches.glob("dictionary_batch_*.json"))
    expected_names = [f"dictionary_batch_{i:03d}.json" for i in range(1, 61)]
    actual_names = [p.name for p in batch_files]

    if actual_names != expected_names:
        missing = [x for x in expected_names if x not in actual_names]
        extra = [x for x in actual_names if x not in expected_names]
        if missing:
            blocking.append("Missing batch files: " + ", ".join(missing))
        if extra:
            blocking.append("Unexpected batch-like files: " + ", ".join(extra))

    entries: list[dict[str, Any]] = []
    batch_stats: list[dict[str, Any]] = []
    headword_locations: dict[str, list[str]] = defaultdict(list)
    form_owners: dict[str, list[dict[str, Any]]] = defaultdict(list)
    total_forms = 0
    total_glosses = 0

    for path in batch_files:
        match = BATCH_RE.match(path.name)
        if not match:
            blocking.append(f"{path.name}: malformed batch filename")
            continue
        number = int(match.group(1))
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            blocking.append(f"{path.name}: invalid UTF-8 JSON: {exc}")
            continue

        if doc.get("version") != 1:
            blocking.append(f"{path.name}: version must be 1")
        if doc.get("batch") != number:
            blocking.append(
                f"{path.name}: JSON batch {doc.get('batch')!r} does not match filename {number}"
            )

        batch_entries = doc.get("entries")
        if not isinstance(batch_entries, list):
            blocking.append(f"{path.name}: entries must be an array")
            continue
        if len(batch_entries) != 500:
            blocking.append(f"{path.name}: expected 500 entries, found {len(batch_entries)}")

        batch_stats.append({"batch": number, "entries": len(batch_entries)})

        for idx, entry in enumerate(batch_entries):
            loc = f"{path.name}:entries[{idx}]"
            if not isinstance(entry, dict):
                blocking.append(f"{loc}: entry must be an object")
                continue

            word = entry.get("word")
            if not isinstance(word, str) or not word.strip():
                blocking.append(f"{loc}: missing/non-string headword")
                continue
            word_key = norm(word)
            if word != word.lower():
                blocking.append(f"{loc}: headword must be lowercase: {word!r}")
            if re.search(r"\s", word) or "-" in word:
                blocking.append(f"{loc}: v1 headword must be one non-hyphenated word: {word!r}")
            headword_locations[word_key].append(loc)

            pronunciation = entry.get("pronunciation")
            if (
                not isinstance(pronunciation, str)
                or not pronunciation.strip()
                or not re.fullmatch(r"/.+/", pronunciation.strip())
            ):
                blocking.append(f"{loc} {word!r}: pronunciation must be slash-delimited IPA")

            forms = entry.get("forms")
            if not isinstance(forms, list):
                blocking.append(f"{loc} {word!r}: forms must be an array")
                forms = []
            seen_forms: set[str] = set()
            for form in forms:
                total_forms += 1
                if not isinstance(form, str) or not form.strip():
                    blocking.append(f"{loc} {word!r}: invalid empty/non-string form")
                    continue
                form_key = norm(form)
                if re.search(r"\s", form.strip()):
                    blocking.append(f"{loc} {word!r}: form must be a single word: {form!r}")
                if form_key in seen_forms:
                    blocking.append(f"{loc} {word!r}: duplicate form {form!r}")
                seen_forms.add(form_key)
                if form_key == word_key:
                    blocking.append(f"{loc} {word!r}: headword appears in its own forms")
                form_owners[form_key].append(
                    {"headword": word_key, "display": form, "location": loc, "batch": number}
                )

            meanings = entry.get("meanings")
            if not isinstance(meanings, list) or not meanings:
                blocking.append(f"{loc} {word!r}: meanings must be a non-empty array")
                meanings = []

            seen_pos: set[str] = set()
            semantic_count = 0
            for mi, meaning in enumerate(meanings):
                mloc = f"{loc}.meanings[{mi}]"
                if not isinstance(meaning, dict):
                    blocking.append(f"{mloc}: meaning must be an object")
                    continue
                pos = meaning.get("partOfSpeech")
                if pos not in ALLOWED_POS:
                    blocking.append(f"{mloc}: unsupported POS {pos!r}")
                if pos in seen_pos:
                    blocking.append(f"{loc} {word!r}: repeated POS block {pos!r}")
                seen_pos.add(pos)

                burmese = meaning.get("burmese")
                if not isinstance(burmese, list) or not burmese:
                    blocking.append(f"{mloc}: Burmese meanings must be a non-empty array")
                    continue
                seen_glosses: set[str] = set()
                for bi, gloss in enumerate(burmese):
                    semantic_count += 1
                    total_glosses += 1
                    if not isinstance(gloss, str) or not gloss.strip():
                        blocking.append(f"{mloc}.burmese[{bi}]: empty/non-string gloss")
                        continue
                    normalized_gloss = gloss.strip()
                    if normalized_gloss in seen_glosses:
                        blocking.append(f"{mloc}: duplicate Burmese gloss {gloss!r}")
                    seen_glosses.add(normalized_gloss)
                    if ASCII_LETTER.search(gloss):
                        blocking.append(
                            f"{mloc}.burmese[{bi}]: Latin/English text found in Burmese gloss {gloss!r}"
                        )

            if semantic_count > 3:
                blocking.append(
                    f"{loc} {word!r}: maximum 3 Burmese meanings allowed, found {semantic_count}"
                )

            entries.append(
                {
                    "word": word,
                    "pronunciation": pronunciation,
                    "forms": forms,
                    "meanings": meanings,
                }
            )

    duplicate_headwords = [
        {"key": key, "locations": locs}
        for key, locs in sorted(headword_locations.items())
        if len(locs) > 1
    ]
    for item in duplicate_headwords:
        blocking.append(
            f"Duplicate headword {item['key']!r} across {', '.join(item['locations'])}"
        )

    headword_keys = set(headword_locations)
    form_form_collisions: list[dict[str, Any]] = []
    for key, owners in sorted(form_owners.items()):
        unique_heads = sorted({o["headword"] for o in owners})
        if len(unique_heads) > 1:
            form_form_collisions.append({"form": key, "headwords": unique_heads, "owners": owners})
            blocking.append(f"Form collision {key!r}: forms of {', '.join(unique_heads)}")

    headword_form_overlaps: list[dict[str, Any]] = []
    for key in sorted(headword_keys & set(form_owners)):
        owners = [o for o in form_owners[key] if o["headword"] != key]
        if owners:
            headword_form_overlaps.append(
                {"key": key, "headwordLocations": headword_locations[key], "formOwners": owners}
            )

    manifest: dict[str, Any] = {}
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    except Exception as exc:
        blocking.append(f"Manifest could not be parsed: {exc}")

    unique_headwords = len(headword_keys)
    unique_forms = len(form_owners)
    unique_lookup_keys = len(headword_keys | set(form_owners))

    expected_manifest = {
        "targetHeadwords": 30000,
        "targetBatches": 60,
        "entriesPerBatch": 500,
        "latestBatch": 60,
        "nextBatch": None,
        "batchCount": 60,
        "totalHeadwords": 30000,
        "status": "complete",
    }
    manifest_mismatches: list[dict[str, Any]] = []
    for key, expected in expected_manifest.items():
        if manifest.get(key) != expected:
            manifest_mismatches.append(
                {"field": key, "expected": expected, "actual": manifest.get(key)}
            )

    lookup = manifest.get("lookup") if isinstance(manifest.get("lookup"), dict) else {}
    for key, actual, expected in [
        ("uniqueHeadwords", lookup.get("uniqueHeadwords"), unique_headwords),
        ("uniqueStoredForms", lookup.get("uniqueStoredForms"), unique_forms),
        ("uniqueLookupKeys", lookup.get("uniqueLookupKeys"), unique_lookup_keys),
        ("throughBatch", lookup.get("throughBatch"), 60),
    ]:
        if actual != expected:
            manifest_mismatches.append(
                {"field": f"lookup.{key}", "expected": expected, "actual": actual}
            )

    historical = manifest.get("historicalBatches")
    if isinstance(historical, dict) and historical.get("mirroredAsJson") is not True:
        warnings.append(
            "Manifest historicalBatches.mirroredAsJson is stale: batch JSON files 001-023 are present."
        )

    legacy_headwords = load_legacy_headwords(args.legacy_ts)
    missing_legacy = sorted(set(legacy_headwords) - headword_keys)
    if missing_legacy:
        warnings.append(
            f"{len(missing_legacy)} legacy fallback headwords are absent from the 30k corpus."
        )

    candidate = {"version": 1, "entries": sorted(entries, key=lambda e: e["word"])}
    candidate_text = json.dumps(candidate, ensure_ascii=False, indent=2) + "\n"
    candidate_sha256 = hashlib.sha256(candidate_text.encode("utf-8")).hexdigest()
    if not blocking:
        args.candidate.write_text(candidate_text, encoding="utf-8")

    report = {
        "version": 1,
        "status": "PASS" if not blocking else "FAIL",
        "summary": {
            "batchFiles": len(batch_files),
            "entries": len(entries),
            "uniqueHeadwords": unique_headwords,
            "totalStoredForms": total_forms,
            "uniqueStoredForms": unique_forms,
            "burmeseMeanings": total_glosses,
            "uniqueLookupKeys": unique_lookup_keys,
            "headwordFormOverlaps": len(headword_form_overlaps),
            "formFormCollisions": len(form_form_collisions),
            "legacyHeadwordsChecked": len(legacy_headwords),
            "missingLegacyHeadwords": len(missing_legacy),
            "blockingErrors": len(blocking),
            "warnings": len(warnings),
            "candidateSha256": candidate_sha256 if not blocking else None,
        },
        "blockingErrors": blocking,
        "warnings": warnings,
        "manifestMismatches": manifest_mismatches,
        "duplicateHeadwords": duplicate_headwords,
        "formFormCollisions": form_form_collisions,
        "headwordFormOverlaps": headword_form_overlaps,
        "missingLegacyHeadwords": missing_legacy,
        "batchStats": batch_stats,
    }

    args.report_json.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    lines = [
        "# Subtitle Bridge Dictionary v1 Finalization Audit",
        "",
        f"Status: {report['status']}",
        "",
        "## Summary",
        "",
    ]
    for key, value in report["summary"].items():
        lines.append(f"- {key}: {value}")

    lines += ["", "## Manifest mismatches", ""]
    if manifest_mismatches:
        for item in manifest_mismatches:
            lines.append(
                f"- {item['field']} expected {item['expected']!r}, actual {item['actual']!r}"
            )
    else:
        lines.append("- None")

    lines += ["", "## Headword / form overlaps", ""]
    if headword_form_overlaps:
        for item in headword_form_overlaps:
            owners = ", ".join(sorted({o["headword"] for o in item["formOwners"]}))
            lines.append(f"- {item['key']} is a headword and a stored form of: {owners}")
    else:
        lines.append("- None")

    lines += ["", "## Form / form collisions", ""]
    if form_form_collisions:
        for item in form_form_collisions:
            lines.append(
                f"- {item['form']} is stored by multiple headwords: {', '.join(item['headwords'])}"
            )
    else:
        lines.append("- None")

    lines += ["", "## Legacy fallback coverage", ""]
    if legacy_headwords:
        lines.append(f"- Checked {len(legacy_headwords)} current legacy headwords.")
        if missing_legacy:
            lines.append("- Missing: " + ", ".join(missing_legacy))
        else:
            lines.append("- All legacy fallback headwords are present in the 30k corpus.")
    else:
        lines.append("- Legacy file not supplied; coverage was not checked.")

    lines += ["", "## Blocking errors", ""]
    lines.extend([f"- {item}" for item in blocking] if blocking else ["- None"])

    lines += ["", "## Warnings", ""]
    lines.extend([f"- {item}" for item in warnings] if warnings else ["- None"])

    args.report_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))

    if headword_form_overlaps:
        print("\nHEADWORD_FORM_OVERLAPS")
        for item in headword_form_overlaps:
            owners = ",".join(sorted({o["headword"] for o in item["formOwners"]}))
            print(f"{item['key']} <- {owners}")

    if form_form_collisions:
        print("\nFORM_FORM_COLLISIONS")
        for item in form_form_collisions:
            print(f"{item['form']} <- {','.join(item['headwords'])}")

    if missing_legacy:
        print("\nMISSING_LEGACY_HEADWORDS")
        print(",".join(missing_legacy))

    if manifest_mismatches:
        print("\nMANIFEST_MISMATCHES")
        for item in manifest_mismatches:
            print(f"{item['field']}: expected={item['expected']!r} actual={item['actual']!r}")

    if warnings:
        print("\nWARNINGS")
        for item in warnings:
            print(item)

    if blocking:
        print("\nBLOCKING_ERRORS", file=sys.stderr)
        for item in blocking:
            print(item, file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
