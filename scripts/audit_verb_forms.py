#!/usr/bin/env python3
"""Compare stored verb forms with morphology suggestions from lemminflect.

This script is an audit aid only. It never edits dictionary data.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from lemminflect import getAllInflections

VERB_TAGS = ("VBZ", "VBD", "VBN", "VBG", "VBP")


def norm(value: str) -> str:
    return value.strip().casefold()


def suggested_forms(word: str) -> list[str]:
    inflections = getAllInflections(word, upos="VERB")
    result: list[str] = []
    seen: set[str] = set()
    head = norm(word)

    for tag in VERB_TAGS:
        for form in inflections.get(tag, ()):
            key = norm(form)
            if not key or key == head or key in seen:
                continue
            if any(ch.isspace() for ch in form) or "-" in form:
                continue
            seen.add(key)
            result.append(form)

    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batches", type=Path, default=Path("Batches"))
    ap.add_argument("--output", type=Path, default=Path("verb_form_audit.json"))
    args = ap.parse_args()

    rows: list[dict[str, Any]] = []
    lookup_owners: dict[str, set[str]] = {}

    documents = []
    for path in sorted(args.batches.glob("dictionary_batch_*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        documents.append((path, doc))
        for entry in doc["entries"]:
            word = norm(entry["word"])
            lookup_owners.setdefault(word, set()).add(word)
            for form in entry["forms"]:
                lookup_owners.setdefault(norm(form), set()).add(word)

    for path, doc in documents:
        for index, entry in enumerate(doc["entries"]):
            if not any(m["partOfSpeech"] == "verb" for m in entry["meanings"]):
                continue

            word = entry["word"]
            existing = list(entry["forms"])
            suggestions = suggested_forms(word)
            existing_keys = {norm(x) for x in existing}
            suggestion_keys = {norm(x) for x in suggestions}

            missing = [x for x in suggestions if norm(x) not in existing_keys]
            extra = [x for x in existing if norm(x) not in suggestion_keys]

            conflicts: list[dict[str, Any]] = []
            for form in missing:
                owners = sorted(lookup_owners.get(norm(form), set()) - {norm(word)})
                if owners:
                    conflicts.append({"form": form, "existingOwners": owners})

            if missing or extra or len(existing) < 3:
                rows.append(
                    {
                        "word": word,
                        "batch": doc["batch"],
                        "entryIndex": index,
                        "existing": existing,
                        "suggested": suggestions,
                        "missing": missing,
                        "extra": extra,
                        "conflicts": conflicts,
                    }
                )

    summary = {
        "verbRowsNeedingReview": len(rows),
        "zeroStoredForms": sum(1 for row in rows if not row["existing"]),
        "withMissingSuggestions": sum(1 for row in rows if row["missing"]),
        "withConflictingSuggestions": sum(1 for row in rows if row["conflicts"]),
        "withExtraStoredForms": sum(1 for row in rows if row["extra"]),
    }

    payload = {"version": 1, "summary": summary, "rows": rows}
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2))
    print("\nZERO_FORM_VERBS")
    for row in rows:
        if not row["existing"]:
            print(
                f"{row['word']} | suggested={','.join(row['suggested'])} | "
                f"conflicts={json.dumps(row['conflicts'], ensure_ascii=False)}"
            )


if __name__ == "__main__":
    raise SystemExit(main())
