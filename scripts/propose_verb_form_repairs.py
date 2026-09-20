#!/usr/bin/env python3
"""Propose conservative repairs for missing verb forms.

Uses lemminflect only as a morphology source. Existing forms are preserved.
Only verbs with fewer than three stored forms are considered. Candidate forms
come from VBZ/VBD/VBN/VBG, use the first morphology suggestion for each tag,
and are skipped when they would collide with another exact headword or another
headword's stored form.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from lemminflect import getAllInflections

TAGS = ("VBZ", "VBD", "VBN", "VBG")


def norm(value: str) -> str:
    return value.strip().casefold()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batches", type=Path, default=Path("Batches"))
    ap.add_argument("--output", type=Path, default=Path("verb_form_repair_proposal.json"))
    args = ap.parse_args()

    documents: list[tuple[Path, dict[str, Any]]] = []
    headwords: set[str] = set()
    form_owners: dict[str, set[str]] = defaultdict(set)

    for path in sorted(args.batches.glob("dictionary_batch_*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        documents.append((path, doc))
        for entry in doc["entries"]:
            headwords.add(norm(entry["word"]))

    for _, doc in documents:
        for entry in doc["entries"]:
            owner = norm(entry["word"])
            for form in entry["forms"]:
                form_owners[norm(form)].add(owner)

    proposals: list[dict[str, Any]] = []
    skipped_collisions: list[dict[str, Any]] = []
    no_morphology: list[dict[str, Any]] = []

    for path, doc in documents:
        for index, entry in enumerate(doc["entries"]):
            if len(entry["forms"]) >= 3:
                continue
            if not any(m["partOfSpeech"] == "verb" for m in entry["meanings"]):
                continue

            word = entry["word"]
            word_key = norm(word)
            existing = list(entry["forms"])
            existing_keys = {norm(x) for x in existing}
            raw = getAllInflections(word, upos="VERB")

            candidates: list[dict[str, str]] = []
            seen: set[str] = set()
            for tag in TAGS:
                values = raw.get(tag, ())
                if not values:
                    continue
                form = values[0]
                key = norm(form)
                if not key or key == word_key or key in existing_keys or key in seen:
                    continue
                if any(ch.isspace() for ch in form) or "-" in form:
                    continue
                seen.add(key)
                candidates.append({"tag": tag, "form": form})

            if not candidates and not existing:
                no_morphology.append(
                    {"word": word, "batch": doc["batch"], "entryIndex": index}
                )
                continue

            accepted: list[dict[str, str]] = []
            rejected: list[dict[str, Any]] = []
            for candidate in candidates:
                key = norm(candidate["form"])
                if key in headwords and key != word_key:
                    rejected.append(
                        {
                            **candidate,
                            "reason": "exact-headword",
                            "owners": [key],
                        }
                    )
                    continue
                other_form_owners = sorted(form_owners.get(key, set()) - {word_key})
                if other_form_owners:
                    rejected.append(
                        {
                            **candidate,
                            "reason": "form-owner",
                            "owners": other_form_owners,
                        }
                    )
                    continue
                accepted.append(candidate)

            if accepted:
                proposals.append(
                    {
                        "word": word,
                        "batch": doc["batch"],
                        "entryIndex": index,
                        "existing": existing,
                        "add": [x["form"] for x in accepted],
                        "taggedAdd": accepted,
                        "rejected": rejected,
                    }
                )
            elif rejected:
                skipped_collisions.append(
                    {
                        "word": word,
                        "batch": doc["batch"],
                        "entryIndex": index,
                        "existing": existing,
                        "rejected": rejected,
                    }
                )

    payload = {
        "version": 1,
        "summary": {
            "entriesWithSafeAdditions": len(proposals),
            "formsToAdd": sum(len(x["add"]) for x in proposals),
            "entriesBlockedByCollisions": len(skipped_collisions),
            "zeroFormEntriesWithoutMorphology": len(no_morphology),
        },
        "proposals": proposals,
        "blockedByCollisions": skipped_collisions,
        "zeroFormEntriesWithoutMorphology": no_morphology,
    }
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(payload["summary"], indent=2))
    print("\nSAMPLE_PROPOSALS")
    for item in proposals[:120]:
        print(
            f"{item['word']} | existing={','.join(item['existing'])} | "
            f"add={','.join(item['add'])} | rejected={json.dumps(item['rejected'], ensure_ascii=False)}"
        )
    print("\nZERO_FORM_NO_MORPHOLOGY")
    print(",".join(x["word"] for x in no_morphology))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
