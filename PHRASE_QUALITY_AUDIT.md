# Phrase Dictionary Editorial Audit

This audit records the final editorial cleanup performed before Phrase Dictionary v1 finalization.

## Scope

- All 3,000 entries were checked mechanically for schema, 2–5 token limits, normalization, duplicate/collision safety, type validity, and Burmese meaning presence.
- Later batches were additionally reviewed for artificial padding, compositional directional fragments, incomplete/separable constructions that the contiguous matcher cannot reliably see, and low-value subtitle lookup candidates.
- 61 low-value/artificial/incomplete entries in Batches 009–012 were replaced in place with stronger subtitle expressions and idioms.
- The lone ASCII English word found inside a Burmese gloss (`follow back`) was rewritten in Burmese.
- Total canonical phrase count remains exactly 3,000.

## Editorial principles applied

Entries were removed when they were primarily ordinary compositional motion/direction strings, awkward generated combinations, incomplete idioms, or constructions whose object normally separates the stored words in real subtitles.

Replacement entries prioritize common conversational dialogue, established idioms, and fixed expressions that can be matched contiguously by Subtitle Bridge.

## Result

After this cleanup, the dataset should be revalidated, the cumulative phrase lookup rebuilt, and the deterministic v1 artifact finalized before application integration.
