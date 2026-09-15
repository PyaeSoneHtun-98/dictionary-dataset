#!/usr/bin/env python3
"""Validate one Subtitle Bridge dictionary batch against cumulative lookup shards."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ALLOWED_POS = {
    "noun", "verb", "adjective", "adverb", "pronoun", "preposition",
    "conjunction", "interjection", "determiner", "modal", "auxiliary",
}
ASCII_LETTER = re.compile(r"[A-Za-z]")


def load_prior_keys(lookup_dir: Path) -> set[str]:
    keys: set[str] = set()
    for path in sorted(lookup_dir.glob("used_*.txt")):
        for line in path.read_text(encoding="utf-8").splitlines():
            key = line.strip()
            if key:
                keys.add(key)
    return keys


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("batch", type=Path)
    ap.add_argument("--lookup-dir", type=Path, default=Path("lookup"))
    ap.add_argument("--expected-batch", type=int)
    args = ap.parse_args()

    data = json.loads(args.batch.read_text(encoding="utf-8"))
    entries = data.get("entries", [])
    prior = load_prior_keys(args.lookup_dir)
    errors: list[str] = []

    if data.get("version") != 1:
        fail(errors, "version must be 1")
    if args.expected_batch is not None and data.get("batch") != args.expected_batch:
        fail(errors, f"batch must be {args.expected_batch}")
    if len(entries) != 500:
        fail(errors, f"expected 500 entries, got {len(entries)}")

    words = [e.get("word") for e in entries]
    if len(set(words)) != len(words):
        fail(errors, "duplicate headwords inside batch")

    new_head_set = set(words)
    new_forms_all: list[str] = []

    for i, entry in enumerate(entries):
        where = f"entry[{i}]"
        word = entry.get("word")
        if not isinstance(word, str) or not word:
            fail(errors, f"{where}: missing word")
            continue
        if word != word.lower():
            fail(errors, f"{where} {word!r}: headword must be lowercase")
        if any(ch.isspace() for ch in word) or "-" in word:
            fail(errors, f"{where} {word!r}: headword must be single non-hyphenated word")
        if word in prior:
            fail(errors, f"{where} {word!r}: collides with prior lookup key")

        pron = entry.get("pronunciation")
        if not isinstance(pron, str) or len(pron) < 3 or not (pron.startswith("/") and pron.endswith("/")):
            fail(errors, f"{where} {word!r}: invalid pronunciation")

        forms = entry.get("forms")
        if not isinstance(forms, list):
            fail(errors, f"{where} {word!r}: forms must be a list")
            forms = []
        if len(forms) != len(set(forms)):
            fail(errors, f"{where} {word!r}: duplicate forms")
        if word in forms:
            fail(errors, f"{where} {word!r}: headword appears in its own forms")
        for form in forms:
            if not isinstance(form, str) or not form:
                fail(errors, f"{where} {word!r}: invalid empty/non-string form")
                continue
            if form in prior:
                fail(errors, f"{where} {word!r}: form {form!r} collides with prior lookup key")
            new_forms_all.append(form)

        meanings = entry.get("meanings")
        if not isinstance(meanings, list) or not meanings:
            fail(errors, f"{where} {word!r}: meanings must be a non-empty list")
            continue

        total_glosses = 0
        for m in meanings:
            pos = m.get("partOfSpeech") if isinstance(m, dict) else None
            if pos not in ALLOWED_POS:
                fail(errors, f"{where} {word!r}: invalid POS {pos!r}")
            burmese = m.get("burmese") if isinstance(m, dict) else None
            if not isinstance(burmese, list) or not burmese:
                fail(errors, f"{where} {word!r}: Burmese gloss list must be non-empty")
                continue
            total_glosses += len(burmese)
            for gloss in burmese:
                if not isinstance(gloss, str) or not gloss.strip():
                    fail(errors, f"{where} {word!r}: empty Burmese gloss")
                elif ASCII_LETTER.search(gloss):
                    fail(errors, f"{where} {word!r}: English/Latin text in Burmese gloss {gloss!r}")
        if total_glosses > 3:
            fail(errors, f"{where} {word!r}: more than 3 Burmese semantic meanings")

    for form in new_forms_all:
        if form in new_head_set:
            fail(errors, f"generated form {form!r} collides with a new batch headword")

    if errors:
        print("INVALID")
        for error in errors:
            print("-", error)
        return 1

    print("VALID")
    print("entries:", len(entries))
    print("unique_headwords:", len(new_head_set))
    print("prior_lookup_keys:", len(prior))
    print("new_forms:", len(new_forms_all))
    print("new_unique_forms:", len(set(new_forms_all)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
