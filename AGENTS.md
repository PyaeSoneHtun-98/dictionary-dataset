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
8. Commit the new file as `Batches/dictionary_batch_XXX.json`.
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

Batches 001–023 were generated before this repository workflow was initialized. Their complete lookup keys are represented in the cumulative lookup index. Batch 024 onward should be committed directly under `Batches/`.

If historical batch JSON files are later mirrored into the repo, do not alter their data merely to make them fit a new generation rule; validate and document any corrections explicitly.

---

# Phrase Dictionary project — Subtitle Bridge Phrase Dictionary v1

This section is authoritative for the **English multi-word phrase → Burmese** dataset. It is a parallel project and must not alter, regenerate, reorganize, or merge data into the frozen 30,000-word Dictionary v1 assets.

## Frozen single-word assets

Do not modify phrase data into or through:

- `Batches/`
- `lookup/`
- `dictionary_manifest.json`
- `dist/dictionary_v1.json`

The single-word Dictionary v1.0.0 remains frozen.

## Phrase project objective

Create **3,000 unique English multi-word expressions** in **12 batches**, with **exactly 250 entries per batch**.

Use only these types:

- `phrasal_verb`
- `idiom`
- `expression`

Phrase data lives under:

- `PhraseBatches/phrase_batch_XXX.json`
- `phrase_lookup/used_phrase_keys_current.zlib.b64`
- `phrase_manifest.json`
- final artifact: `dist/phrases_v1.json`

## Phrase entry schema

```json
{
  "phrase": "give up",
  "type": "phrasal_verb",
  "forms": [
    "gives up",
    "gave up",
    "given up",
    "giving up"
  ],
  "burmese": [
    "လက်လျှော့သည်",
    "အရှုံးပေးသည်"
  ]
}
```

Batch schema:

```json
{
  "version": 1,
  "batch": 1,
  "entries": []
}
```

Final artifact schema:

```json
{
  "version": 1,
  "entries": []
}
```

Do not add required runtime fields beyond `phrase`, `type`, `forms`, and `burmese`.

## Automatic phrase-batch workflow

When the active task is the Phrase Dictionary and the user says `next batch` or asks for the next phrase batch:

1. Read `phrase_manifest.json`.
2. Use its `nextBatch`; never ask for a number when the manifest resolves it.
3. Decode/load `phrase_lookup/used_phrase_keys_current.zlib.b64`.
4. Build a candidate list substantially larger than 250.
5. Remove all previously used normalized canonical phrases and forms.
6. Prefer high-frequency, high-value movie/TV subtitle expressions.
7. Curate exactly 250 entries.
8. Write natural Burmese meanings using language understanding, not mechanical word-by-word translation.
9. Add only real useful surface forms.
10. Run `python scripts/validate_phrase_batch.py PhraseBatches/phrase_batch_XXX.json`.
11. Commit the validated batch.
12. Run `python scripts/rebuild_phrase_lookup.py --write`.
13. Commit the updated phrase lookup and `phrase_manifest.json`.
14. Report batch number, entry count, type counts, cumulative total, validation result, and unusual editorial decisions.

Use direct commits unless the user explicitly requests a pull request workflow.

## Phrase selection

Prioritize subtitle usefulness, especially:

- common conversational phrasal verbs
- crime, conflict, investigation, and action expressions
- relationships and emotions
- common idioms
- fixed conversational expressions

Use a frequency/usefulness-first approach. Do not generate alphabetically and do not reserve obvious high-value phrases for later batches.

Do not include arbitrary compositional combinations such as `big house`, `red car`, `very good`, or `walk slowly`.

Do not include:

- full sentences or movie quotes
- proper nouns, names, brands, places, or titles
- obscure literary idioms with low subtitle value
- highly technical expressions with little subtitle value
- invented expressions
- artificial padding to reach the target

## Surface-string rules

Canonical `phrase` values must:

- be lowercase
- contain exactly 2–5 whitespace-separated subtitle tokens
- use modern established English
- have no leading/trailing whitespace
- use exactly one space between tokens
- have no sentence-ending punctuation
- contain no placeholders
- be globally unique after normalization

Version 1 supports contiguous surface matching only.

Do not use placeholder/separable patterns such as:

- `pick [something] up`
- `take <someone> out`
- `someone/something`

Phrases longer than five tokens are not allowed in v1.

## Forms

`forms` contains only real alternative surface strings useful in subtitles.

Rules:

- never include the canonical phrase itself
- use correct grammatical/irregular forms only
- each form must contain 2–5 tokens
- no normalized duplicate forms
- no form may collide with another canonical phrase
- no form may be owned by two different entries
- fixed idioms/expressions that do not inflect should use `"forms": []`
- do not add forms merely to populate the array

## Burmese meanings

Burmese quality is the highest priority.

Each entry must contain 1–3 concise semantic meanings. Translate the phrase as a unit, not the individual words.

Meanings must be:

- natural Burmese
- concise and immediately useful during subtitle lookup
- semantically accurate
- appropriate for modern conversational English
- not unnecessarily formal
- independently authored; do not copy proprietary dictionary glosses

Prioritize senses by subtitle frequency, modern conversational usage, and usefulness to an intermediate learner.

## Duplicate and collision policy

The phrase lookup namespace contains normalized canonical phrases plus all stored forms.

A lookup key may have exactly one owner. Reject:

- canonical/canonical duplicates
- canonical/form collisions
- form/form collisions
- duplicates within one entry after normalization
- collisions with any earlier phrase batch

Use `phrase_lookup/used_phrase_keys_current.zlib.b64` as the cumulative exclusion index.

## Required validation

Every phrase batch must pass all structural and collision validation before commit, including:

- exactly 250 entries
- valid UTF-8 JSON
- version 1
- filename and batch field agree
- only allowed phrase types
- canonical phrases and forms are 2–5 tokens
- canonical phrases are lowercase and whitespace-normalized
- no placeholders
- no canonical/form/form collisions
- 1–3 non-empty Burmese meanings
- no duplicate prior lookup keys
- manifest totals remain consistent

The test suite is `python -m unittest tests/test_phrase_dictionary.py`.

## Finalization

After Batch 012:

1. Rebuild the phrase lookup deterministically.
2. Run `python scripts/finalize_phrases_v1.py --write`.
3. Produce `dist/phrases_v1.json` with exactly 3,000 canonical entries.
4. Sort deterministically by canonical phrase.
5. Report canonical count, stored-form count, lookup-key count, type counts, Burmese-meaning count, duplicate/collision counts, and artifact SHA-256.
6. Create `PHRASE_FINALIZATION.md`.
7. Freeze the result as **Phrase Dictionary v1.0.0**.

Phrase Dictionary v1 does not implement fuzzy matching, semantic matching, runtime AI translation, sentence translation, placeholders, separated-object phrasal verbs, cross-cue matching, phrases longer than five tokens, pronunciation, IPA, examples, synonyms/antonyms, UI changes, or macOS work.

