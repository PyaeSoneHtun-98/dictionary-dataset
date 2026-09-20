#!/usr/bin/env python3
"""Apply conservative repairs to verb entries that currently have zero stored forms.

Rules:
- Never alter an entry that already has at least one stored form.
- Use the first lemminflect result for VBZ/VBD/VBN/VBG.
- Never add the headword itself.
- Skip candidates that are another exact headword.
- Skip candidates already owned as a form by a different headword.
- Skip a few known non-General-American duplicate spellings.
- Add a small reviewed override set for useful modern verbs lemminflect misses.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from lemminflect import getAllInflections

TAGS = ("VBZ", "VBD", "VBN", "VBG")
SKIP_HEADWORDS = {"analyse", "distil", "instil"}

MANUAL_FORMS: dict[str, list[str]] = {
    "micromanage": ["micromanages", "micromanaged", "micromanaging"],
    "outguess": ["outguesses", "outguessed", "outguessing"],
    "overfeed": ["overfeeds", "overfed", "overfeeding"],
    "overfill": ["overfills", "overfilled", "overfilling"],
    "overstaff": ["overstaffs", "overstaffed", "overstaffing"],
    "communize": ["communizes", "communized", "communizing"],
    "decertify": ["decertifies", "decertified", "decertifying"],
    "decontrol": ["decontrols", "decontrolled", "decontrolling"],
    "delist": ["delists", "delisted", "delisting"],
    "federalize": ["federalizes", "federalized", "federalizing"],
    "reacquire": ["reacquires", "reacquired", "reacquiring"],
    "reassume": ["reassumes", "reassumed", "reassuming"],
    "reauthorize": ["reauthorizes", "reauthorized", "reauthorizing"],
    "recapitalize": ["recapitalizes", "recapitalized", "recapitalizing"],
    "redial": ["redials", "redialed", "redialing"],
    "squish": ["squishes", "squished", "squishing"],
    "fuck": ["fucks", "fucked", "fucking"],
    "triangulate": ["triangulates", "triangulated", "triangulating"],
    "hightail": ["hightails", "hightailed", "hightailing"],
    "breastfeed": ["breastfeeds", "breastfed", "breastfeeding"],
    "badmouth": ["badmouths", "badmouthed", "badmouthing"],
    "unchain": ["unchains", "unchained", "unchaining"],
    "unfreeze": ["unfreezes", "unfroze", "unfrozen", "unfreezing"],
    "quieten": ["quietens", "quietened", "quietening"],
    "redline": ["redlines", "redlined", "redlining"],
    "grok": ["groks", "grokked", "grokking"],
    "laze": ["lazes", "lazed", "lazing"],
    "miff": ["miffs", "miffed", "miffing"],
    "roleplay": ["roleplays", "roleplayed", "roleplaying"],
    "headbutt": ["headbutts", "headbutted", "headbutting"],
    "prolapse": ["prolapses", "prolapsed", "prolapsing"],
    "preform": ["preforms", "preformed", "preforming"],
    "resize": ["resizes", "resized", "resizing"],
    "regrow": ["regrows", "regrew", "regrown", "regrowing"],
    "fundraise": ["fundraises", "fundraised", "fundraising"],
    "dropkick": ["dropkicks", "dropkicked", "dropkicking"],
    "unclog": ["unclogs", "unclogged", "unclogging"],
    "unbalance": ["unbalances", "unbalanced", "unbalancing"],
    "rappel": ["rappels", "rappelled", "rappelling"],
    "weaponize": ["weaponizes", "weaponized", "weaponizing"],
    "recode": ["recodes", "recoded", "recoding"],
    "lowball": ["lowballs", "lowballed", "lowballing"],
    "reshoot": ["reshoots", "reshot", "reshooting"],
    "sexualize": ["sexualizes", "sexualized", "sexualizing"],
    "radicalize": ["radicalizes", "radicalized", "radicalizing"],
    "objectify": ["objectifies", "objectified", "objectifying"],
    "upend": ["upends", "upended", "upending"],
    "outscore": ["outscores", "outscored", "outscoring"],
}


def norm(value: str) -> str:
    return value.strip().casefold()


def morphology_candidates(word: str) -> list[str]:
    raw = getAllInflections(word, upos="VERB")
    result: list[str] = []
    seen: set[str] = set()
    head = norm(word)

    for tag in TAGS:
        values = raw.get(tag, ())
        if not values:
            continue
        form = values[0]
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
    ap.add_argument("--report", type=Path, default=Path("verb_form_repair_applied.json"))
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

    changed: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    changed_files: set[Path] = set()

    for path, doc in documents:
        for index, entry in enumerate(doc["entries"]):
            if entry["forms"]:
                continue
            if not any(m["partOfSpeech"] == "verb" for m in entry["meanings"]):
                continue

            word = entry["word"]
            word_key = norm(word)
            if word_key in SKIP_HEADWORDS:
                skipped.append({"word": word, "reason": "spelling-variant-skip"})
                continue

            candidates = morphology_candidates(word)
            source = "lemminflect"
            if not candidates and word_key in MANUAL_FORMS:
                candidates = MANUAL_FORMS[word_key]
                source = "reviewed-manual"

            accepted: list[str] = []
            rejected: list[dict[str, Any]] = []
            seen: set[str] = set()

            for form in candidates:
                key = norm(form)
                if not key or key == word_key or key in seen:
                    continue
                seen.add(key)

                if key in headwords and key != word_key:
                    rejected.append(
                        {"form": form, "reason": "exact-headword", "owners": [key]}
                    )
                    continue

                other_owners = sorted(form_owners.get(key, set()) - {word_key})
                if other_owners:
                    rejected.append(
                        {"form": form, "reason": "form-owner", "owners": other_owners}
                    )
                    continue

                accepted.append(form)

            if not accepted:
                skipped.append(
                    {
                        "word": word,
                        "batch": doc["batch"],
                        "entryIndex": index,
                        "reason": "no-safe-forms",
                        "source": source,
                        "rejected": rejected,
                    }
                )
                continue

            entry["forms"] = accepted
            changed_files.add(path)
            for form in accepted:
                form_owners[norm(form)].add(word_key)
            changed.append(
                {
                    "word": word,
                    "batch": doc["batch"],
                    "entryIndex": index,
                    "forms": accepted,
                    "source": source,
                    "rejected": rejected,
                }
            )

    for path, doc in documents:
        if path in changed_files:
            path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = {
        "version": 1,
        "summary": {
            "entriesRepaired": len(changed),
            "formsAdded": sum(len(x["forms"]) for x in changed),
            "batchFilesChanged": len(changed_files),
            "zeroFormVerbEntriesSkipped": len(skipped),
            "manualOverrideEntriesUsed": sum(1 for x in changed if x["source"] == "reviewed-manual"),
        },
        "changed": changed,
        "skipped": skipped,
    }
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], indent=2))
    print("\nSKIPPED_ZERO_FORM_VERBS")
    print(",".join(x["word"] for x in skipped))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
