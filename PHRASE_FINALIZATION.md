# Phrase Dictionary v1.0.0 Finalization

Phrase Dictionary v1.0.0 is frozen for Subtitle Bridge.

## Final dataset

- Source commit: `a0d374f1fd1d6233b2ded6f98a17c877a88f0e08`
- Canonical phrases: **3,000**
- Stored forms: **4,827**
- Unique lookup keys: **7,827**
- Burmese semantic meanings: **4,092**
- Phrasal verbs: **1,185**
- Idioms: **935**
- Expressions: **880**
- Duplicate canonical phrases: **0**
- Variant collisions: **0**
- Runtime artifact: `dist/phrases_v1.json`
- Artifact SHA-256: `951a8bbe54824cf76728393791607798f878a062b19eca63e572278ba8f62926`

## Validation and editorial audit

All 12 source batches contain exactly 250 entries and pass the repository validator.
The cumulative phrase lookup was rebuilt from source before finalization.

Two editorial passes replaced **96** structurally valid but low-value, artificial,
incomplete, or contiguous-matcher-unfriendly entries in Batches 009–012 with
stronger subtitle expressions. The lone ASCII English word found inside a Burmese
gloss was also rewritten in Burmese.

The existing frozen 30,000-headword single-word Dictionary v1 was not modified.

## Runtime contract

The artifact uses the existing Subtitle Bridge phrase schema:
`phrase`, `type`, `forms`, and `burmese`.

Every canonical phrase and stored form is limited to 2–5 tokens for the current
contiguous longest-match phrase detector.
