#!/usr/bin/env python3
"""Validate one post-v1 Subtitle Bridge dictionary extension batch."""

from __future__ import annotations

import argparse
import base64
import json
import re
import sys
import unicodedata
import zlib
from pathlib import Path

ALLOWED_POS = {
    "noun", "verb", "adjective", "adverb", "pronoun", "preposition",
    "conjunction", "interjection", "determiner", "modal", "auxiliary",
}
ASCII_LETTER = re.compile(r"[A-Za-z]")
ENGLISH_WORD = re.compile(r"^[a-z]+$")
MYANMAR_LETTER = re.compile(r"[\u1000-\u102a\u103f\u1050-\u1055\u105a-\u105d\u1061\u1065-\u1066\u106e-\u1070\u1075-\u1081\u108e]")
IPA_CHARACTERS = set("abcdefghijklmnopqrstuvwxyzæðŋɑɒɔəɚɛɝɡɪɹʃʊʌʒʤʧˈˌːˑ.θɾɫɐʔ̩̯̃͡")
BATCH_RE = re.compile(r"^dictionary_batch_(\d{3})\.json$")


def norm(value: str) -> str:
    return value.strip().casefold()


def load_base_keys(path: Path) -> set[str]:
    encoded = path.read_text(encoding="ascii").strip()
    raw = zlib.decompress(base64.b64decode(encoded)).decode("utf-8")
    return {norm(line) for line in raw.splitlines() if line.strip()}


def load_prior_keys(base_lookup: Path, batches_dir: Path, batch_number: int) -> set[str]:
    keys = load_base_keys(base_lookup)
    for path in sorted(batches_dir.glob("dictionary_batch_*.json")):
        match = BATCH_RE.match(path.name)
        if not match:
            continue
        number = int(match.group(1))
        if number >= batch_number:
            continue
        doc = json.loads(path.read_text(encoding="utf-8"))
        for entry in doc.get("entries", []):
            keys.add(norm(entry["word"]))
            for form in entry.get("forms", []):
                keys.add(norm(form))
    return keys


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("batch", type=Path)
    ap.add_argument("--base-lookup", type=Path, default=Path("lookup/used_keys_current.zlib.b64"))
    ap.add_argument("--batches-dir", type=Path, default=Path("DictionaryExtensionBatches"))
    ap.add_argument("--expected-batch", type=int)
    ap.add_argument("--rejected-headwords", type=Path, default=Path("extension_rejected_headwords.txt"))
    ap.add_argument(
        "--closed-compound-allowlist",
        type=Path,
        default=Path("extension_closed_compound_allowlist.txt"),
    )
    args = ap.parse_args()

    errors: list[str] = []
    match = BATCH_RE.match(args.batch.name)
    if not match:
        errors.append("filename must match dictionary_batch_XXX.json")
        batch_number = -1
    else:
        batch_number = int(match.group(1))

    try:
        data = json.loads(args.batch.read_text(encoding="utf-8"))
    except Exception as exc:
        print("INVALID")
        print("-", f"invalid UTF-8 JSON: {exc}")
        return 1

    if not isinstance(data, dict):
        print("INVALID\n- batch must be an object")
        return 1
    if set(data) != {"version", "batch", "entries"}:
        errors.append("batch fields must be exactly version, batch, entries")
    if type(data.get("version")) is not int or data.get("version") != 1:
        errors.append("version must be 1")
    if type(data.get("batch")) is not int or data.get("batch") != batch_number:
        errors.append(f"JSON batch must match filename batch {batch_number}")
    if args.expected_batch is not None and batch_number != args.expected_batch:
        errors.append(f"batch must be {args.expected_batch}")

    entries = data.get("entries")
    if not isinstance(entries, list):
        errors.append("entries must be a list")
        entries = []
    if len(entries) != 500:
        errors.append(f"expected 500 entries, got {len(entries)}")

    prior = load_prior_keys(args.base_lookup, args.batches_dir, batch_number)
    approved_closed_compounds: set[str] = set()
    if args.closed_compound_allowlist.exists():
        approved_closed_compounds = {
            line.strip()
            for line in args.closed_compound_allowlist.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        }
    rejected_headwords = set()
    if args.rejected_headwords.exists():
        rejected_headwords = {
            line.strip() for line in args.rejected_headwords.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        }
    for label, words in [("allowlist", approved_closed_compounds), ("rejected-headword record", rejected_headwords)]:
        if any(not ENGLISH_WORD.fullmatch(w) for w in words):
            errors.append(f"{label}: keys must be lowercase English letters only")

    new_headwords: set[str] = set()
    owner_by_key: dict[str, str] = {}

    for i, entry in enumerate(entries):
        where = f"entry[{i}]"
        if not isinstance(entry, dict):
            errors.append(f"{where}: entry must be an object")
            continue
        if set(entry) != {"word", "pronunciation", "forms", "meanings"}:
            errors.append(f"{where}: fields must be exactly word, pronunciation, forms, meanings")

        word = entry.get("word")
        if not isinstance(word, str) or not word.strip():
            errors.append(f"{where}: missing word")
            continue
        key = norm(word)
        if not ENGLISH_WORD.fullmatch(word):
            errors.append(f"{where} {word!r}: headword must contain lowercase English letters only")
        if key in rejected_headwords:
            errors.append(f"{where} {word!r}: editorially rejected headword; an allowlist cannot override this")
        if word != word.lower() or word != word.strip():
            errors.append(f"{where} {word!r}: headword must be lowercase and trimmed")
        if any(ch.isspace() for ch in word) or "-" in word:
            errors.append(f"{where} {word!r}: headword must be one non-hyphenated word")
        if key in prior:
            errors.append(f"{where} {word!r}: collides with prior v1/extension lookup key")
        if key in new_headwords:
            errors.append(f"{where} {word!r}: duplicate headword inside batch")
        new_headwords.add(key)

        suspicious_splits: list[str] = []
        if key not in approved_closed_compounds:
            for split_at in range(3, len(key) - 2):
                left = key[:split_at]
                right = key[split_at:]
                if left in prior and right in prior:
                    suspicious_splits.append(f"{left}+{right}")
            if suspicious_splits:
                errors.append(
                    f"{where} {word!r}: suspicious glued compound "
                    f"({', '.join(suspicious_splits[:4])}); verify established closed spelling "
                    "and add the canonical headword to extension_closed_compound_allowlist.txt only after lexical review"
                )

        pronunciation = entry.get("pronunciation")
        if (
            not isinstance(pronunciation, str)
            or not re.fullmatch(r"/[^/]+/", pronunciation)
        ):
            errors.append(f"{where} {word!r}: pronunciation must be slash-delimited IPA")
        elif any(unicodedata.category(ch) in {"Cf", "Cc"} for ch in pronunciation):
            errors.append(f"{where} {word!r}: pronunciation contains invisible format characters")
        else:
            if any(ch.isspace() for ch in pronunciation):
                errors.append(
                    f"{where} {word!r}: single-word IPA must not contain whitespace; "
                    "this usually indicates an open/hyphenated multi-word expression was glued together"
                )
            elif any(ch not in IPA_CHARACTERS for ch in pronunciation[1:-1]):
                errors.append(f"{where} {word!r}: pronunciation contains non-IPA characters")

        forms = entry.get("forms")
        if not isinstance(forms, list):
            errors.append(f"{where} {word!r}: forms must be a list")
            forms = []
        local_forms: set[str] = set()
        for form in forms:
            if not isinstance(form, str) or not form.strip():
                errors.append(f"{where} {word!r}: invalid form")
                continue
            form_key = norm(form)
            if form_key in rejected_headwords:
                errors.append(f"{where} {word!r}: editorially rejected lookup form {form!r}")
            if not ENGLISH_WORD.fullmatch(form):
                errors.append(f"{where} {word!r}: form must contain lowercase English letters only: {form!r}")
            if any(ch.isspace() for ch in form.strip()):
                errors.append(f"{where} {word!r}: form must be a single word: {form!r}")
            if form_key == key:
                errors.append(f"{where} {word!r}: headword appears in its own forms")
            if form_key in local_forms:
                errors.append(f"{where} {word!r}: duplicate form {form!r}")
            if form_key in prior:
                errors.append(f"{where} {word!r}: form {form!r} collides with prior lookup key")
            local_forms.add(form_key)

            previous = owner_by_key.get(form_key)
            if previous is not None and previous != word:
                errors.append(
                    f"{where} {word!r}: form {form!r} is already owned in this batch by {previous!r}"
                )
            else:
                owner_by_key[form_key] = word

        meanings = entry.get("meanings")
        if not isinstance(meanings, list) or not meanings:
            errors.append(f"{where} {word!r}: meanings must be a non-empty list")
            continue

        total_glosses = 0
        seen_pos: set[str] = set()
        seen_glosses: set[str] = set()
        for meaning in meanings:
            if not isinstance(meaning, dict):
                errors.append(f"{where} {word!r}: meaning must be an object")
                continue
            if set(meaning) != {"partOfSpeech", "burmese"}:
                errors.append(f"{where} {word!r}: meaning fields must be exactly partOfSpeech, burmese")
            pos = meaning.get("partOfSpeech")
            if not isinstance(pos, str):
                errors.append(f"{where} {word!r}: POS must be a string")
                pos = ""
            if pos not in ALLOWED_POS:
                errors.append(f"{where} {word!r}: invalid POS {pos!r}")
            if pos in seen_pos:
                errors.append(f"{where} {word!r}: repeated POS block {pos!r}")
            seen_pos.add(pos)

            burmese = meaning.get("burmese")
            if not isinstance(burmese, list) or not burmese:
                errors.append(f"{where} {word!r}: Burmese gloss list must be non-empty")
                continue
            total_glosses += len(burmese)
            for gloss in burmese:
                if not isinstance(gloss, str) or not gloss.strip():
                    errors.append(f"{where} {word!r}: empty Burmese gloss")
                elif ASCII_LETTER.search(gloss):
                    errors.append(f"{where} {word!r}: English/Latin text in Burmese gloss {gloss!r}")
                else:
                    if not MYANMAR_LETTER.search(gloss):
                        errors.append(f"{where} {word!r}: gloss must contain Myanmar letters")
                    if gloss != gloss.strip() or any(unicodedata.category(ch) in {"Cf", "Cc"} for ch in gloss):
                        errors.append(f"{where} {word!r}: gloss contains surrounding whitespace or invisible/control characters")
                    if gloss in seen_glosses:
                        errors.append(f"{where} {word!r}: duplicate Burmese gloss")
                    seen_glosses.add(gloss)

        if total_glosses > 3:
            errors.append(f"{where} {word!r}: more than 3 Burmese semantic meanings")

    for key, word in list(owner_by_key.items()):
        if key in new_headwords:
            errors.append(
                f"generated form {key!r} owned by {word!r} collides with a new batch headword"
            )

    if errors:
        print("INVALID")
        for error in errors:
            print("-", error)
        return 1

    print("VALID")
    print("batch:", batch_number)
    print("entries:", len(entries))
    print("prior_lookup_keys:", len(prior))
    print("new_headwords:", len(new_headwords))
    print("new_unique_forms:", len(owner_by_key))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
