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
- Completed extension batches: **061–073**, **6,500 headwords**
- Next batch: **074** (the manifest remains authoritative)
- Batch size: **500 headwords**
- Extension lookup: `extension_lookup/used_keys_current.zlib.b64`
- The extension exclusion namespace starts with all **45,817** frozen v1 lookup keys, so new headwords/forms cannot duplicate the released 30k corpus.
- No new extension batch modifies `Batches/`, `lookup/`, `dictionary_manifest.json`, or `dist/dictionary_v1.json`.
- Separate app artifact: `dist/dictionary_extension.json`, with counts and SHA-256 in `dist/dictionary_extension.metadata.json`.
- Current extension: **4,386 stored forms**, **10,886 extension lookup keys**; combined exclusion namespace: **56,703 keys**.

Load the frozen `dist/dictionary_v1.json` and the separate extension artifact to provide 36,500 canonical entries. Both use `{ "version": 1, "entries": [...] }` and the same entry schema. Index each headword and its stored forms; every extension key has one owner and is disjoint from the frozen lookup namespace. The `.zlib.b64` lookup files are generation exclusion indexes, not Burmese definition payloads.

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
