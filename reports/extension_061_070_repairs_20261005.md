# Extension Batches 061–070 repair record

Repair plan authored: 2026-10-05. Final local verification: 2026-10-06. Baseline: `ff7e738f03134796fb6422502b6d39f0c0ed5983`.

The actionable dataset findings from the [original audit](extension_061_070_audit_20261005.md) are repaired. All ten batches retain exactly 500 entries; the extension remains open-ended at 5,000 headwords, with Batch 071 next. This is a validated dataset snapshot, not an assertion of completed native-speaker review or Windows app integration.

## Editorial changes

- Replaced 134 entries: 2 in Batch 061, 10 in 062, 121 in 063 and 1 in 064. These include confirmed joined phrases, unsupported coinages, spellings whose closed form could not be verified to the required standard, a brand and a foreign word. “Not verified for inclusion” does not mean that every removed spelling is nonexistent in English.
- The rejected examples `toiletrybag`, `waterbottle`, `ricecooker`, `foodprocessor` and `airvent` were removed along with their invalid stored forms. Replacements are fresh canonical single words with independently authored Burmese meanings and General American IPA.
- Reviewed all 117 separated-spelling candidates from the audit: 61 retained with current dictionary evidence, 56 replaced. Established variants such as `roadmap`, `carpool`, `nightlight`, `timesheet` and `trashcan` remain. Other replacements address additional findings outside that candidate set.
- Corrected `circularize` to distributing notices, polling by questionnaire and making something circular. Corrected `maraud` and `fleer` POS/meanings, and the selected fabric sense of `jean`.
- Reviewed the flagged IPA for `corp`, `quilting`, `housekeeping`, `weatherize` and `circularize`; the replacement `compere` also uses the American dictionary stress pattern.
- Reviewed plural candidates for 732 selected count nouns and supplied missing useful forms for the 15 originally empty verb entries. Irregular plurals were explicitly handled, including `lockmen`, `pitchmen`, `mitochondria`, `diverticula`, `nasopharynges` and `bialys`. No plural was added for the selected mass sense of `matt` or singular conversational sense of `missis`.

The repair adds **840 new stored-form keys**, including replacement-entry forms, and removes **109 forms belonging to rejected entries**. Stored forms increase by a net **731**. Fourteen proposed forms were excluded to preserve existing ownership; none of the surviving old keys changed owner. The subsequent verb audit finds **zero verb entries with empty forms**. Unowned library suggestions such as `unmaked`, `unbended` and `betrode` were rejected; this audit is diagnostic rather than automatic editorial approval.

The complete before/after changes for 879 touched entries, the authored replacement list, plural selection and lexical references are recorded under [`staging/repairs_061_070_20261005/`](../staging/repairs_061_070_20261005/). The one-time repair script requires the baseline batches and deliberately refuses a second application.

## Validation and packaging

| Batch | Headwords | Stored forms | Burmese meanings |
| --- | ---: | ---: | ---: |
| 061 | 500 | 300 | 506 |
| 062 | 500 | 382 | 501 |
| 063 | 500 | 314 | 509 |
| 064 | 500 | 475 | 528 |
| 065 | 500 | 479 | 524 |
| 066 | 500 | 444 | 533 |
| 067 | 500 | 55 | 526 |
| 068 | 500 | 580 | 568 |
| 069 | 500 | 458 | 567 |
| 070 | 500 | 296 | 567 |
| Total | 5,000 | 3,783 | 5,329 |

All ten batches pass the strengthened validator. The deterministic lookup rebuild matches the manifest and index. The extension has **8,783 unique lookup keys**, with zero internal collisions and zero overlap with frozen v1. The combined exclusion index has **54,600 keys**.

The validator now enforces exact schema fields, lowercase alphabetic keys, stricter IPA characters/whitespace, actual Myanmar letters, duplicate-gloss rejection and invisible/control-character rejection. A reviewed rejection record blocks all 243 removed headword/form spellings even if a headword is mistakenly added to the compound allowlist. The compound heuristic remains a review aid; it cannot determine English lexical legitimacy or Burmese semantic accuracy by itself.

The separate app artifact is [`dist/dictionary_extension.json`](../dist/dictionary_extension.json), with source-equivalent entries sorted by headword. It keeps the same runtime entry schema as frozen v1. Metadata is in [`dist/dictionary_extension.metadata.json`](../dist/dictionary_extension.metadata.json). The builder validates all batches, requires synchronized lookup state and verifies the frozen v1 artifact digest before packaging. CI runs regression tests and the sync workflow maintains this separate artifact for future extension batches.

Checks completed:

- All ten batch validators, lookup check mode, artifact check mode and deterministic source/artifact comparison.
- Twelve extension regression tests covering rejected allowlist overrides, rejected forms, malformed schema/POS, noncanonical keys, IPA, gloss structure, prior and same-batch collisions, artifact determinism and every headword/form lookup owner.
- Existing phrase dictionary tests, to check shared repository compatibility.
- Git whitespace/diff checks and frozen-path comparisons. No frozen dictionary or phrase assets were changed.

Artifact SHA-256 (UTF-8/LF): `53b42c8c45a5bf0e956deed2d1764d0b40381edf88e141c5591461522b45f8cd`.

Combined lookup SHA-256 (trimmed Base64): `e1a9c98ad790da3e1b11b0777e420dc3bf1c427cfacba927146e9cff602d2b0b`.

Frozen v1 artifact SHA-256 remains `fcdb26986ed62bfaa130732ed0e88cc2e30bbc7f964b4b16de47f809783ed325`.

## Remaining release verification

The confirmed dataset defects and packaging gap are resolved. Full independent bilingual review of all 5,000 entries and a complete General American IPA review have not been performed. The repository does not contain the Windows application, so its loader, token normalization, click-to-lookup behavior and rendering have not been tested here. Run that integration test against frozen v1 plus the separate extension artifact before declaring production readiness.

English dictionary sources are recorded for spelling/sense verification; Burmese glosses were independently authored, not copied from those sources.
