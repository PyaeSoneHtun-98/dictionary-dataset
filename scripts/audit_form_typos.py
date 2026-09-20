#!/usr/bin/env python3
"""Audit stored verb forms for likely spelling errors.

Uses lemminflect for candidate paradigms and wordfreq only as a confidence aid.
It does not edit data. A correction is reported only when the stored form is
unrecognized for the lemma, a morphology candidate is very close in spelling,
and the candidate is substantially more frequent in modern English.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from lemminflect import getAllInflections
from wordfreq import zipf_frequency

TAGS = ("VBZ", "VBD", "VBN", "VBG")


def norm(value: str) -> str:
    return value.strip().casefold()


def levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        cur = [i]
        for j, cb in enumerate(b, start=1):
            cur.append(
                min(
                    cur[-1] + 1,
                    prev[j] + 1,
                    prev[j - 1] + (ca != cb),
                )
            )
        prev = cur
    return prev[-1]


def role(form: str) -> str:
    if form.endswith("ing"):
        return "VBG"
    if form.endswith("ed") or form.endswith("ied") or form.endswith("d"):
        return "PAST"
    if form.endswith("s") or form.endswith("es") or form.endswith("ies"):
        return "VBZ"
    return "OTHER"


def candidate_pool(raw: dict[str, tuple[str, ...]], stored: str) -> list[str]:
    r = role(stored)
    if r == "VBG":
        tags = ("VBG",)
    elif r == "VBZ":
        tags = ("VBZ",)
    elif r == "PAST":
        tags = ("VBD", "VBN")
    else:
        tags = ("VBD", "VBN", "VBZ", "VBG")

    result: list[str] = []
    seen: set[str] = set()
    for tag in tags:
        for item in raw.get(tag, ()):
            key = norm(item)
            if key not in seen:
                seen.add(key)
                result.append(item)
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batches", type=Path, default=Path("Batches"))
    ap.add_argument("--output", type=Path, default=Path("form_typo_audit.json"))
    args = ap.parse_args()

    findings: list[dict[str, Any]] = []

    for path in sorted(args.batches.glob("dictionary_batch_*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        for index, entry in enumerate(doc["entries"]):
            if not any(m["partOfSpeech"] == "verb" for m in entry["meanings"]):
                continue
            if not entry["forms"]:
                continue

            raw = getAllInflections(entry["word"], upos="VERB")
            recognized = {
                norm(form)
                for tag in TAGS
                for form in raw.get(tag, ())
            }
            if not recognized:
                continue

            has_adjective = any(
                m["partOfSpeech"] == "adjective" for m in entry["meanings"]
            )

            for stored in entry["forms"]:
                stored_key = norm(stored)
                if stored_key in recognized:
                    continue
                if has_adjective and (stored.endswith("er") or stored.endswith("est")):
                    continue

                candidates = candidate_pool(raw, stored)
                scored: list[dict[str, Any]] = []
                for candidate in candidates:
                    distance = levenshtein(stored_key, norm(candidate))
                    if distance > 2:
                        continue
                    scored.append(
                        {
                            "candidate": candidate,
                            "distance": distance,
                            "candidateZipf": round(zipf_frequency(candidate, "en"), 3),
                        }
                    )

                if not scored:
                    continue

                scored.sort(
                    key=lambda x: (
                        x["distance"],
                        -x["candidateZipf"],
                        x["candidate"],
                    )
                )
                best = scored[0]
                stored_zipf = round(zipf_frequency(stored, "en"), 3)
                gain = round(best["candidateZipf"] - stored_zipf, 3)

                high_confidence = (
                    best["distance"] <= 2
                    and best["candidateZipf"] >= 2.0
                    and (
                        (stored_zipf < 1.0 and gain >= 1.0)
                        or gain >= 1.5
                    )
                )

                if high_confidence:
                    findings.append(
                        {
                            "word": entry["word"],
                            "batch": doc["batch"],
                            "entryIndex": index,
                            "stored": stored,
                            "storedZipf": stored_zipf,
                            "suggestedReplacement": best["candidate"],
                            "candidateZipf": best["candidateZipf"],
                            "frequencyGain": gain,
                            "distance": best["distance"],
                            "alternatives": scored[:5],
                        }
                    )

    payload = {
        "version": 1,
        "summary": {
            "highConfidenceLikelyTypos": len(findings),
        },
        "findings": findings,
    }
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(payload["summary"], indent=2))
    for item in findings:
        print(
            f"{item['word']}: {item['stored']} -> {item['suggestedReplacement']} "
            f"(zipf {item['storedZipf']} -> {item['candidateZipf']}, "
            f"distance {item['distance']})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
