# AGENTS.md — Subtitle Bridge Dictionary

This file is the authoritative instruction set for generating and maintaining the English → Burmese Subtitle Bridge dictionary dataset.

## Project objective

Create **30,000 unique English headwords** in **60 batches**, with **exactly 500 entries per batch**.

The dictionary is for a Windows movie/subtitle application. A user clicks an unfamiliar English subtitle word and should immediately see a useful Burmese lookup result.

The Burmese translation quality is the highest priority.

## Automatic batch workflow

When the user says `next batch`:

1. Read `dictionary_manifest.json`.
2. Use its `nextBatch` value. Never ask for the batch number if the manifest resolves it.
3. Load/decode `lookup/used_keys_current.zlib.b64` and treat every key as excluded.
4. Generate exactly 500 new canonical single-word English headwords.
5. Write natural Burmese meanings manually using language understanding.
6. Add General American IPA and useful inflected forms.
7. Run all validation rules below.
8. Commit the new file as `batches/dictionary_batch_XXX.json`.
9. Update the cumulative lookup index so it contains all old keys plus the new headwords/forms.
10. Update `dictionary_manifest.json` (`latestBatch`, `nextBatch`, `batchCount`, `totalHeadwords`, and lookup metadata).
11. Return the new batch file/result to the user with a short validation summary.

Use direct commits to the repository unless the user explicitly asks for a pull request workflow.

## Entry schema

```json
{
  "word": "string",
  "pronunciation": "string",
  "forms": ["string"],
  "meanings": [
    {
      "partOfSpeech": "string",
      "burmese": ["string"]
    }
  ]
}
```

Batch schema:

```json
{
  "version": 1,
  "batch": 24,
  "entries": []
}
```

## Vocabulary selection

Prioritize words useful in:

- films and TV subtitles
- conversation and relationships
- crime, investigation, law, security, military, and politics
- emotion, personality, conflict, and social situations
- physical actions and descriptive language
- medical, scientific, technical, and business contexts that realistically appear in media
- novels, news, documentaries, and narrative dialogue
- practical concrete nouns where genuinely useful

Avoid padding with extremely basic words such as `the`, `and`, `is`, `yes`, `no`, `hello`, `good`, and `bad` unless a common non-basic lexical sense makes inclusion worthwhile.

Avoid obscure specialist jargon whose subtitle value is very low.

### Headword rules

- Version 1 uses **single-word headwords only**.
- No spaces.
- No hyphenated headwords.
- No proper nouns, person names, place names, brands, fictional character names, or organization names.
- Do not invent closed compounds merely to satisfy the single-word rule.
- Prefer the canonical singular/base lemma over a plural or inflected form.
- Do not add a word if it already exists in the cumulative lookup index as either a previous headword or a previous stored form.
- Prevent same-batch lemma/form collisions as well.

## Burmese meaning rules

Burmese meanings are the most important field.

Write them yourself using language understanding. Do not produce mechanical word-for-word or machine-translation-style Burmese.

The Burmese should be:

- natural
- concise
- idiomatic
- immediately understandable to a native Burmese speaker
- suitable for an instant subtitle lookup
- matched to the actual English sense
- not unnecessarily formal unless the English word itself is formal

For every proposed gloss, silently ask:

> If a Burmese speaker saw only this Burmese meaning while watching a movie, would they understand the English word correctly?

Use established Burmese words or natural short phrases. Do not put English explanations, romanized Burmese, or English text inside Burmese arrays.

### Sense limit

Each headword may have **at most 3 Burmese semantic meanings total across all POS blocks**.

Choose meanings by:

1. usefulness in movies/subtitles
2. common modern English usage
3. usefulness to an intermediate learner

Do not fill all three slots merely because they are available.

Same-POS senses belong in the same Burmese array. Use separate POS blocks only when needed.

## Pronunciation

- General American English only.
- IPA only.
- Exactly one pronunciation per headword.
- Format with slashes, e.g. `/tʃɑrdʒ/`.
- For heteronyms, choose the pronunciation matching the selected dictionary sense(s).
- Manually review words missing from pronunciation resources and words with likely heteronym/stress ambiguity.
- Do not include UK pronunciation or audio information.

## Forms

Include useful forms that a subtitle lookup should resolve.

Examples:

- verbs: `betray` → `betrays`, `betrayed`, `betraying`
- irregular verbs: include actual irregular past/participle forms
- nouns: regular or irregular plural where appropriate
- adjectives: comparative/superlative only when they are real useful lexical forms

Rules:

- Never include the headword itself in `forms`.
- Do not invent unnatural forms.
- Do not create plurals for ordinary mass/abstract nouns merely to populate the field.
- Avoid storing an inflected form if it collides with any earlier lookup key.
- Audit spelling rules manually; generic suffix algorithms are not trusted blindly.

## Allowed POS values

Only:

- `noun`
- `verb`
- `adjective`
- `adverb`
- `pronoun`
- `preposition`
- `conjunction`
- `interjection`
- `determiner`
- `modal`
- `auxiliary`

## Do not include

- example sentences
- English definitions
- synonyms
- antonyms
- etymology
- usage-history notes
- pronunciation audio
- proper nouns
- multi-word expressions or phrasal verbs in Version 1

## Required validation before commit

Every batch must satisfy all of the following:

- exactly 500 entries
- exactly 500 unique headwords in the batch
- batch number and filename match the manifest
- valid UTF-8 JSON
- no duplicate headwords
- no new headword overlaps any cumulative prior headword or form
- no generated new form overlaps a prior headword/form
- no generated form collides with another new headword in the same batch
- no headword appears inside its own `forms`
- no spaces or hyphens in headwords
- no proper names/brands/places
- every entry has exactly one non-empty pronunciation string
- every entry has at least one meaning block
- all POS values are normalized/allowed
- every Burmese gloss is non-empty
- no English/ASCII words inside Burmese glosses
- no entry has more than 3 Burmese semantic meanings total
- after commit, `totalHeadwords == batchCount * 500`

## Repository state

`dictionary_manifest.json` is the canonical project progress record.

`lookup/used_keys_current.zlib.b64` is the canonical cumulative exclusion index. It is zlib-compressed UTF-8 text, Base64 encoded, with one lookup key per line before compression.

Batches 001–023 were generated before this repository workflow was initialized. Their complete lookup keys are represented in the cumulative lookup index. Batch 024 onward should be committed directly under `batches/`.

If historical batch JSON files are later mirrored into the repo, do not alter their data merely to make them fit a new generation rule; validate and document any corrections explicitly.
