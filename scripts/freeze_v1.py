#!/usr/bin/env python3
"""Freeze a validated Subtitle Bridge Dictionary v1.0 release artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

INTENTIONAL_ZERO_FORM_VERBS = [
    "beware", "daresay",
    "distil", "analyse", "fulfil", "instil", "demonise",
    "snafu", "tink", "rive", "coif", "lour", "abye", "airt", "cere", "larn",
    "nett", "rede", "shew", "slue", "spue", "breaststroke", "brevet",
    "clinker", "whiteout", "teargas", "outcall", "precis", "chasse", "applique",
]

LEGACY_ONLY_HEADWORDS = [
    "bad", "big", "day", "do", "go", "humiliating", "love", "man",
    "new", "no", "run", "say", "see", "thanks", "wait", "yes",
]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", type=Path, default=Path("dictionary_v1_candidate.json"))
    ap.add_argument("--audit", type=Path, default=Path("finalization_report.json"))
    ap.add_argument("--verb-audit", type=Path, default=Path("verb_form_audit_final.json"))
    ap.add_argument("--manifest", type=Path, default=Path("dictionary_manifest.json"))
    ap.add_argument("--output", type=Path, default=Path("dist/dictionary_v1.json"))
    ap.add_argument("--summary", type=Path, default=Path("FINALIZATION.md"))
    ap.add_argument("--source-commit", required=True)
    args = ap.parse_args()

    audit = json.loads(args.audit.read_text(encoding="utf-8"))
    if audit.get("status") != "PASS" or audit.get("summary", {}).get("blockingErrors") != 0:
        raise SystemExit("Refusing to freeze: whole-corpus finalization audit did not PASS.")

    verb_audit = json.loads(args.verb_audit.read_text(encoding="utf-8"))
    observed_zero = sorted(
        row["word"]
        for row in verb_audit.get("rows", [])
        if not row.get("existing")
    )
    expected_zero = sorted(INTENTIONAL_ZERO_FORM_VERBS)
    if observed_zero != expected_zero:
        raise SystemExit(
            "Refusing to freeze: intentional zero-form verb list does not match audit.\n"
            f"Expected: {expected_zero}\nObserved: {observed_zero}"
        )

    observed_legacy = sorted(audit.get("missingLegacyHeadwords", []))
    expected_legacy = sorted(LEGACY_ONLY_HEADWORDS)
    if observed_legacy != expected_legacy:
        raise SystemExit(
            "Refusing to freeze: legacy-only headword list does not match audit.\n"
            f"Expected: {expected_legacy}\nObserved: {observed_legacy}"
        )

    candidate_sha = sha256_file(args.candidate)
    reported_sha = audit["summary"].get("candidateSha256")
    if candidate_sha != reported_sha:
        raise SystemExit(
            f"Refusing to freeze: candidate SHA mismatch: {candidate_sha} != {reported_sha}"
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(args.candidate, args.output)
    artifact_sha = sha256_file(args.output)

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    manifest["release"] = {
        "version": "1.0.0",
        "status": "frozen",
        "sourceCommit": args.source_commit,
        "artifact": args.output.as_posix(),
        "artifactSha256": artifact_sha,
        "batchCount": audit["summary"]["batchFiles"],
        "headwords": audit["summary"]["uniqueHeadwords"],
        "storedForms": audit["summary"]["uniqueStoredForms"],
        "burmeseMeanings": audit["summary"]["burmeseMeanings"],
        "lookupKeys": audit["summary"]["uniqueLookupKeys"],
        "headwordFormOverlaps": audit["summary"]["headwordFormOverlaps"],
        "formFormCollisions": audit["summary"]["formFormCollisions"],
        "intentionalZeroFormVerbs": len(INTENTIONAL_ZERO_FORM_VERBS),
        "legacyOnlyHeadwords": len(LEGACY_ONLY_HEADWORDS),
    }
    args.manifest.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    overlap_lines = []
    for item in audit.get("headwordFormOverlaps", []):
        owners = ", ".join(sorted({owner["headword"] for owner in item["formOwners"]}))
        overlap_lines.append(f"- {item['key']} <- form of {owners}")

    summary = f"""# Subtitle Bridge Dictionary v1.0 Finalization

Release status: Frozen
Source commit: {args.source_commit}
Artifact: {args.output.as_posix()}
Artifact SHA-256: {artifact_sha}

## Final corpus

- Batch files: {audit['summary']['batchFiles']}
- Unique headwords: {audit['summary']['uniqueHeadwords']}
- Stored forms: {audit['summary']['uniqueStoredForms']}
- Burmese semantic meanings: {audit['summary']['burmeseMeanings']}
- Unique lookup keys: {audit['summary']['uniqueLookupKeys']}
- Form-to-form collisions: {audit['summary']['formFormCollisions']}
- Headword-to-form overlaps: {audit['summary']['headwordFormOverlaps']}
- Structural blocking errors: {audit['summary']['blockingErrors']}

The release artifact is generated deterministically from Batches/dictionary_batch_001.json
through Batches/dictionary_batch_060.json. The 60 batch files remain the source dataset.

## Lookup policy

Exact headwords take precedence over stored inflected forms. The following headword/form
overlaps are intentional and non-blocking:

{chr(10).join(overlap_lines)}

No stored form is owned by two different headwords.

## Intentionally form-less verb entries

These 30 entries remain without stored inflections because they are defective/fixed-expression
verbs, spelling variants whose forms collide with preferred headwords, or rare/archaic/specialized
items where automatically inventing forms would reduce data quality:

{", ".join(INTENTIONAL_ZERO_FORM_VERBS)}

## Legacy fallback coverage

The 30,000-headword corpus does not contain these 16 basic/legacy-only entries:

{", ".join(LEGACY_ONLY_HEADWORDS)}

They should be handled during Subtitle Bridge integration as a small structured core supplement
(or another explicit structured coverage mechanism) before the old flat fallback is removed.
They were not inserted into this 30,000-headword corpus merely to satisfy legacy parity.

## Quality/audit scope

Finalization included:

- all 60 batch files and exactly 30,000 unique headwords;
- schema, POS, pronunciation shape, Burmese-field, and max-three-meaning validation;
- global duplicate and collision checks;
- deterministic cumulative lookup-index rebuild;
- verb-inflection audit and targeted missing-form repair;
- frequency-assisted detection and correction of high-confidence form spelling errors;
- removal and future rejection of invisible Unicode format characters in IPA strings;
- deterministic release-artifact SHA-256 verification;
- cross-batch sampling of Burmese meanings and pronunciation/form data.

This is an AI-authored English-to-Burmese dataset. Structural and targeted quality audits do not
replace a future native/bilingual editorial review of every one of the 30,000 entries.
"""
    args.summary.write_text(summary, encoding="utf-8")

    print(json.dumps(manifest["release"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
