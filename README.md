# Subtitle Bridge Dictionary Dataset

English → Burmese dictionary data for **Subtitle Bridge**, a subtitle/movie lookup application.

## Goal

- 30,000 English headwords
- 60 batches
- exactly 500 headwords per batch
- General American IPA
- concise, natural Burmese meanings optimized for movie/TV subtitle lookup

## Current progress

Batches 001–038 have been generated: **19,000 unique headwords**.

The repository is the source of truth for all work from Batch 024 onward. The historical lookup keys from Batches 001–023 are stored in `lookup/legacy_used_keys_001_023.zlib.b64` so new batches can be checked against all prior headwords and inflected forms even before the older batch JSON files are mirrored here.

## Layout

```text
AGENTS.md                     permanent generation rules
dictionary_manifest.json      project progress / next batch
Batches/                      generated batch JSON files
lookup/                       prior lookup-key indexes
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
