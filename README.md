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
- Next batch: **061**
- Batch size: **500 headwords**
- Extension lookup: `extension_lookup/used_keys_current.zlib.b64`
- The extension exclusion namespace starts with all **45,817** frozen v1 lookup keys, so new headwords/forms cannot duplicate the released 30k corpus.
- No new extension batch modifies `Batches/`, `lookup/`, `dictionary_manifest.json`, or `dist/dictionary_v1.json`.

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
