# Subtitle Bridge Dictionary Dataset

English → Burmese dictionary data for **Subtitle Bridge**, a subtitle/movie lookup application.

## Goal

- 30,000 English headwords
- 60 batches
- exactly 500 headwords per batch
- General American IPA
- concise, natural Burmese meanings optimized for movie/TV subtitle lookup

## Current progress

Batches 001–060 have been generated: **30,000 unique headwords**. The Version 1 dataset target is complete.

The repository now contains the complete Version 1 source dataset: Batches 001–060 are mirrored under `Batches/`. The cumulative lookup index under `lookup/` covers all headwords and stored forms through Batch 060.

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
