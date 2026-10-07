# Subtitle Bridge Dictionary Dataset

English → Burmese dictionary data for **Subtitle Bridge**, a subtitle/movie lookup application.

## Goal

- 30,000 English headwords
- 60 batches
- exactly 500 headwords per batch
- General American IPA
- concise, natural Burmese meanings optimized for movie/TV subtitle lookup

## Current progress

Batches 001–060 have been generated: **30,000 unique headwords**. Dictionary **v1.0.0 is frozen**.

The repository now contains the complete Version 1 source dataset: Batches 001–060 are mirrored under `Batches/`. The cumulative lookup index under `lookup/` covers all headwords and stored forms through Batch 060.

## Frozen v1.0 release

- Final artifact: `dist/dictionary_v1.json`
- Finalization record: `FINALIZATION.md`
- Headwords: 30,000
- Stored forms: 15,864
- Burmese semantic meanings: 38,001
- Unique lookup keys: 45,817
- Form-to-form collisions: 0
- Artifact SHA-256: `fcdb26986ed62bfaa130732ed0e88cc2e30bbc7f964b4b16de47f809783ed325`

The 60 files under `Batches/` remain the source dataset. The frozen artifact is generated deterministically from those batches.


## Active dictionary extension

Dictionary v1.0.0 remains frozen and unchanged. New single-word vocabulary continues separately from **Batch 061** in `DictionaryExtensionBatches/`.

- Active manifest: `dictionary_extension_manifest.json`
- Completed extension batches: **061–080**, **10,000 headwords**
- Next batch: **081** (the manifest remains authoritative)
- Batch size: **500 headwords**
- Extension lookup: `extension_lookup/used_keys_current.zlib.b64`
- The extension exclusion namespace starts with all **45,817** frozen v1 lookup keys, so new headwords/forms cannot duplicate the released 30k corpus.
- No new extension batch modifies `Batches/`, `lookup/`, `dictionary_manifest.json`, or `dist/dictionary_v1.json`.
- Separate app artifact: `dist/dictionary_extension.json`, with counts and SHA-256 in `dist/dictionary_extension.metadata.json`.
- Current extension: **6,361 stored forms**, **16,361 extension lookup keys**; combined exclusion namespace: **62,178 keys**.

Load the frozen `dist/dictionary_v1.json` and the separate extension artifact to provide 40,000 canonical entries. Both use `{ "version": 1, "entries": [...] }` and the same entry schema. Index each headword and its stored forms; every extension key has one owner and is disjoint from the frozen lookup namespace. The `.zlib.b64` lookup files are generation exclusion indexes, not Burmese definition payloads.

Validate and synchronize the extension with:

```powershell
python scripts/rebuild_extension_lookup.py --write
python scripts/build_extension_artifact.py --write
python scripts/build_extension_artifact.py --check
python -m unittest tests/test_extension_dictionary.py
```

The builder validates every extension batch before packaging and verifies the frozen artifact's recorded SHA-256. CI validates generated snapshots, and the sync workflow updates the extension manifest, lookup and separate artifact when new batches arrive.

The 2026-10-05 audit findings and repairs are documented in `reports/extension_061_070_audit_20261005.md` and `reports/extension_061_070_repairs_20261005.md`. Structural and lookup tests pass. Full native-speaker editorial sign-off and actual Windows app loading/lookup testing remain release gates; they have not been performed in this dataset repository.

The 2026-10-07 continuation added Batches 071–073, prioritizing subtitle usefulness over the requested ten-batch count. Selection, spelling evidence, corrections and remaining candidates are documented in `reports/extension_071_073_review_20261007.md` and `staging/batches071_080/`.

The subsequent continuation completed Batches 074–080 after expanding and reviewing the candidate pool. Editorial decisions, publisher spelling records, validation results and unpublished candidates are documented in `reports/extension_074_080_review_20261007.md` and `staging/batches074_080/`.

## Phrase dictionary and useful idiom extension

Phrase Dictionary **v1.0.0 is frozen** at **3,000 phrases**, **4,827 forms**, and **7,827 lookup keys**. Its source remains under `PhraseBatches/`, with `phrase_manifest.json`, `phrase_lookup/`, `dist/phrases_v1.json`, and `PHRASE_FINALIZATION.md` unchanged.

The separate phrase extension adds **Batches 013–016**, exactly **250 entries per batch**:

- **1,000 new phrases:** 601 idioms, 260 phrasal verbs, and 139 fixed expressions
- **2,682 stored forms**, **3,682 extension lookup keys**, and **1,164 Burmese meanings**
- **4,000 combined canonical phrases**, **7,509 forms**, and **11,509 lookup keys**
- Active state: `phrase_extension_manifest.json`; next batch **017**
- Source: `PhraseExtensionBatches/phrase_batch_XXX.json`
- Exclusion index: `phrase_extension_lookup/used_phrase_keys_current.zlib.b64`
- App artifact: `dist/phrases_extension.json`; counts/hash: `dist/phrases_extension.metadata.json`

Load both `dist/phrases_v1.json` and `dist/phrases_extension.json`. Both use `{ "version": 1, "entries": [...] }` and entries with exactly `phrase`, `type`, `forms`, and `burmese`. Index each canonical and stored form for contiguous, longest-phrase matching over 2–5 subtitle tokens. The compressed lookup files are generation exclusion indexes, not definition payloads. Separated-object patterns, fuzzy matching, and sentence translation are not implemented by these data artifacts.

Validate and synchronize with:

```powershell
python scripts/validate_phrase_extension_batch.py PhraseExtensionBatches/phrase_batch_016.json --expected-batch 16
python scripts/rebuild_phrase_extension_lookup.py --write
python scripts/build_phrase_extension_artifact.py --write
python scripts/build_phrase_extension_artifact.py --check
python -m unittest discover -s tests
```

CI checks batches and deterministic snapshots without changing frozen assets. The initial review record is `reports/phrase_extension_013_016_review_20261007.md`; authored drafts, peer findings, editorial decisions, and unpublished candidates are in `staging/phrases013_016/`. The complete second review and applied corrections are documented in `reports/phrase_extension_013_016_rereview_20261007.md` and `staging/phrase_rereview_20261007/`. Native Burmese human sign-off and actual Windows app loading/lookup tests remain outstanding.

## Layout

```text
AGENTS.md                     permanent generation rules
dictionary_manifest.json      project progress / next batch
Batches/                      generated batch JSON files
lookup/                       frozen v1 lookup-key index
DictionaryExtensionBatches/   Batch 061+ source files (created as batches are added)
dictionary_extension_manifest.json  active extension progress
extension_lookup/             v1 + extension cumulative lookup index
scripts/                      validation and index utilities
```

## Batch format

```json
{
  "version": 1,
  "batch": 24,
  "entries": [
    {
      "word": "example",
      "pronunciation": "/ɪɡˈzæmpəl/",
      "forms": ["examples"],
      "meanings": [
        {
          "partOfSpeech": "noun",
          "burmese": ["ဥပမာ"]
        }
      ]
    }
  ]
}
```

See `AGENTS.md` for the authoritative generation and validation rules.
