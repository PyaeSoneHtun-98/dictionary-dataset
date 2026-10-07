# Phrase extension Batches 013–016

The user authorized 1,000 additional useful English → Burmese phrases, including idioms. They are packaged separately from frozen Phrase Dictionary v1.0.0. No frozen phrase assets, frozen single-word assets, or existing single-word extension data were changed.

## Result

| Batch | Entries | Idioms | Phrasal verbs | Expressions | Forms |
|---|---:|---:|---:|---:|---:|
| 013 | 250 | 150 | 65 | 35 | 374 |
| 014 | 250 | 150 | 65 | 35 | 352 |
| 015 | 250 | 150 | 65 | 35 | 646 |
| 016 | 250 | 150 | 65 | 35 | 673 |
| New total | 1,000 | 600 | 260 | 140 | 2,045 |

- New Burmese meanings: **1,128**.
- New lookup keys: **3,045**; combined frozen + extension lookup keys: **10,872**.
- Combined canonical phrases: **4,000**; combined forms: **6,872**; combined meanings: **5,220**.
- Combined types: **1,535 idioms**, **1,445 phrasal verbs**, **1,020 expressions**.
- Next active phrase batch: **017** in `phrase_extension_manifest.json`.
- New runtime artifact: `dist/phrases_extension.json`.
- Artifact SHA-256 (UTF-8/LF): `6a195e24be5e586771cacb3013bbd7dbf83fb3384e967a6010e7becaf75c2556`.
- Frozen phrase artifact SHA-256 remains `951a8bbe54824cf76728393791607798f878a062b19eca63e572278ba8f62926`.

## Curation and independent review

Three GPT-6.1 Sol agents with high reasoning drafted idioms, phrasal/domain expressions, and conversational/fixed expressions. The coordinator independently authored another 240 entries. Draft Burmese meanings were written using language understanding; no machine-translation package or proprietary Burmese gloss source was used.

The final reviewed source pools contain 240 coordinator entries, 484 idiom-agent entries, 452 verb-agent entries, and 616 expression-agent entries: **1,792 draft rows** before combined exclusion/ownership filtering. The cross-draft selector found **1,663 eligible unique owners**, selected **1,000**, and retained **663 unpublished eligible owners** for future review. Raw authoring pools were larger and were pruned before these reviewed drafts. Neither raw nor unpublished candidates are release data.

Independent peer reviews covered all 240 coordinator entries, all 545 entries in the idiom draft before its final pruning/corrections, and all 452 verb-pool entries, including meanings and forms. The coordinator reviewed the selected expression-agent entries and applied explicit additional decisions. The final selection comes from 226 coordinator entries, 412 idiom-agent entries, 309 verb-agent entries, and 53 expression-agent entries. Peer review is an AI editorial check, not native human sign-off or an empirical frequency study.

Examples prioritized for subtitle usefulness include lawyer up, in the loop, run out of steam, touch base, dead to rights, smoking gun, red herring, elephant in the room, skeleton in the closet, sitting duck, food for thought, and up the ante. Selection is based on qualitative relevance to dialogue, relationships, emotion, crime, action, and narrative media. We did not measure coverage against a licensed subtitle corpus.

## Editorial decisions

- Excluded malformed spellings, incomplete fragments of longer idioms, arbitrary collocations, proper-name expressions, weak specialist terms, and low-priority dated/regional expressions where stronger candidates were available.
- Rejected active patterns requiring an intervening object, such as throw under the bus, bring to justice, take into custody, put through the wringer, and sell down the river. Real passive uses do not justify an unsupported bare active canonical for this contiguous matcher.
- Rejected frozen-equivalent variants, including for old times' sake versus frozen for old times sake, and cosmetic/prepositional elaborations of existing phrases.
- Consolidated go up in smoke/up in smoke, go from strength to strength/from strength to strength, cut to the quick/to the quick, and heart of stone/have a heart of stone into single owners with real alternative surfaces. Other established variants were likewise kept under one owner.
- Corrected Burmese sense/agency issues in all the same, at daggers drawn, by a country mile, small fry, good sport, poor sport, do the honors, eat your hat, reasonable doubt, contempt of court, and soften up.
- Added concise literal senses alongside figurative senses for break your neck, bite your nails, foam at the mouth, and blow a fuse, so action and medical scenes remain understandable.
- Reviewed actual irregular verbs, noun plurals, possessive/reflexive variants, and the maximum five-token limit. No hypothetical forms or mass-noun plurals were added just to increase counts.
- Each batch mixes types while preserving the editorial order within each type; the separate artifact sorts canonicals deterministically.

Detailed publisher URLs and decisions are in the individual `*_review.md` and `*_peer_review.md` files under `staging/phrases013_016/`. Dictionaries were consulted for English lexical status, construction, and disputed senses; published definitions were not copied into runtime data.

## Engineering and validation

- Added a separate manifest, cumulative exclusion index, runtime artifact, artifact metadata, validator, deterministic rebuild/builder scripts, regression tests, and CI workflow.
- Reconstructed ownership from frozen source/artifact plus earlier extension batches rather than trusting the mutable extension index.
- All four batches pass exact-250, schema, normalized surface, 2–5-token, Burmese-only meaning, and global ownership checks.
- **Zero new canonical/form collisions**, including across batches and against every frozen lookup key.
- Manifest/index and runtime artifact/metadata deterministic checks pass.
- **All 38 repository tests pass** (12 frozen phrase, 14 phrase extension, 12 single-word extension).
- Independent infrastructure review found no material correctness issues.
- Git comparison against baseline commit `93803ae` confirms frozen phrase files and all existing word data unchanged.

Validation outputs are saved in `staging/phrases013_016/verification_results.json`. Selection and rejection records are in `selection_audit.json`; runtime entries retain only the existing four fields.

## Runtime scope and remaining release checks

Load the frozen and extension runtime artifacts together and index each canonical and stored form. They share the same schema and have disjoint lookup ownership. The compressed index is a generation exclusion namespace, not a Burmese definition payload.

No Windows app integration or loading test was performed in this dataset repository. Native Burmese human editorial sign-off is also outstanding. Existing frozen-entry form gaps were not silently repaired; those require the separately documented correction/overlay approach described in AGENTS.md.
