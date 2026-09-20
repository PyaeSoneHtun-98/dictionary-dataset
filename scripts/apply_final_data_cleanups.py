#!/usr/bin/env python3
"""Apply final deterministic data cleanups before freezing Dictionary v1."""

from __future__ import annotations

import argparse
import json
import unicodedata
from pathlib import Path
from typing import Any

FORM_FIXES: dict[str, list[str]] = {
    "brag": ["brags", "bragged", "bragging"],
    "abhor": ["abhors", "abhorred", "abhorring"],
    "allude": ["alludes", "alluded", "alluding"],
    "incur": ["incurs", "incurred", "incurring"],
    "rebut": ["rebuts", "rebutted", "rebutting"],
    "shun": ["shuns", "shunned", "shunning"],
    "undo": ["undoes", "undid", "undone", "undoing"],
}


def strip_format_chars(value: str) -> tuple[str, int]:
    removed = sum(1 for ch in value if unicodedata.category(ch) == "Cf")
    cleaned = "".join(ch for ch in value if unicodedata.category(ch) != "Cf")
    return cleaned, removed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batches", type=Path, default=Path("Batches"))
    ap.add_argument("--report", type=Path, default=Path("final_data_cleanup_report.json"))
    args = ap.parse_args()

    changed_files: set[str] = set()
    pronunciation_entries_cleaned = 0
    pronunciation_format_chars_removed = 0
    form_fixes_applied: list[dict[str, Any]] = []
    seen_fix_words: set[str] = set()

    for path in sorted(args.batches.glob("dictionary_batch_*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        changed = False

        for entry in doc["entries"]:
            pronunciation = entry["pronunciation"]
            cleaned, removed = strip_format_chars(pronunciation)
            if removed:
                entry["pronunciation"] = cleaned
                pronunciation_entries_cleaned += 1
                pronunciation_format_chars_removed += removed
                changed = True

            word = entry["word"]
            if word in FORM_FIXES:
                expected = FORM_FIXES[word]
                if entry["forms"] != expected:
                    form_fixes_applied.append(
                        {
                            "word": word,
                            "before": entry["forms"],
                            "after": expected,
                            "batch": doc["batch"],
                        }
                    )
                    entry["forms"] = expected
                    changed = True
                seen_fix_words.add(word)

        if changed:
            path.write_text(
                json.dumps(doc, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            changed_files.add(path.name)

    missing_fix_words = sorted(set(FORM_FIXES) - seen_fix_words)
    if missing_fix_words:
        raise SystemExit(
            "Expected form-fix headwords were not found: " + ", ".join(missing_fix_words)
        )

    report = {
        "version": 1,
        "summary": {
            "batchFilesChanged": len(changed_files),
            "pronunciationEntriesCleaned": pronunciation_entries_cleaned,
            "pronunciationFormatCharactersRemoved": pronunciation_format_chars_removed,
            "formEntriesFixed": len(form_fixes_applied),
        },
        "formFixes": form_fixes_applied,
        "changedFiles": sorted(changed_files),
    }
    args.report.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report["summary"], indent=2))
    for item in form_fixes_applied:
        print(f"{item['word']}: {item['before']} -> {item['after']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
