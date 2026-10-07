# Extension Batches 074–080 review

Date: 2026-10-07. Baseline: `f19387bdfb7153bd4022de29a0278dd5e8431a75`, through Batch 073, 56,703 cumulative lookup keys.

The user's requested continuation through Batch 080 is complete. Seven batches add 3,500 canonical headwords, 1,975 stored forms and 3,983 Burmese semantic meanings. The frozen 30,000-word v1 release and the phrase project remain unchanged.

## Published counts

| Batch | Headwords | Stored forms | Burmese meanings |
| --- | ---: | ---: | ---: |
| 074 | 500 | 344 | 628 |
| 075 | 500 | 227 | 562 |
| 076 | 500 | 280 | 551 |
| 077 | 500 | 241 | 570 |
| 078 | 500 | 181 | 569 |
| 079 | 500 | 361 | 550 |
| 080 | 500 | 341 | 553 |
| Added | 3,500 | 1,975 | 3,983 |

Extension totals: 20 batches, 10,000 headwords, 6,361 stored forms, 16,361 lookup keys and 10,980 Burmese meanings. Combined with frozen v1: 40,000 canonical headwords and 62,178 unique lookup keys. The manifest's next batch is **081**.

## Editorial process

Three GPT-6.1 Sol agents with high reasoning drafted separate SHA-256 partitions, as requested by the user; the coordinator handled the remaining partition. The agents reached their usage limit before final review finished. The coordinator completed source checks, morphology and IPA corrections, targeted Burmese review, integration and validation locally.

The candidate search expanded beyond the earlier run to include overlooked short words with useful lexical senses, modern vocabulary, narrative description, practical objects, trades, legal and political language, and realistic medical/scientific documentary terms. WordNet and frequency resources supported discovery; Burmese glosses were independently authored using language understanding. No translation service generated the Burmese.

The combined draft contained 3,579 unique heads. Sixty were rejected during integration and 19 remain unpublished as lower-priority surplus. Earlier explicit quality deferrals were not bulk-restored. Previously unpublished surplus was reconsidered individually. Runtime sources contain exactly 3,500 new heads; exploratory staging files are not runtime dictionary payloads.

`staging/batches074_080/editorial_overrides.json` records final changes and exclusions. Examples include:

- Covered spelling variants: litchi/lychee, smidgeon/smidgen, flunkey/flunky, pernickety/persnickety and likeability/likability.
- Conflicting draft variants: empanel/impanel, sniveller/sniveler and blowzy/blowsy.
- Open or hyphenated expressions without sufficient current closed-spelling evidence, including namedrop, spotweld, sixpack, bottlefeed and loanshark. Failed retrieval alone was not treated as proof that a word does not exist; uncertain cases were deferred.
- Irregular or misspelled forms: overtopped, crosscutting, cheerled, underspent, foreknew/foreknown, unwove/unwoven, reprogrammed/reprogramming, and compound plurals ending in men/women. Unnatural plurals for sawbones, muggins and slyboots were removed.
- Invalid IPA characters and stress placement were repaired. General American IPA remains one pronunciation per entry, without whitespace.
- Burmese corrections included cob (corncob rather than husk), kepi (a projecting front brim rather than a ceiling), and clearer medical senses for overdiagnose and filariasis.
- The frequent irregular forms **saw** and **won** belong to **see** and **win**. Conflicting tool/currency heads were deferred instead of taking ownership of those common subtitle keys.

Canonical heads were reserved before storing forms, with the explicit saw/won usefulness decisions above. Twelve additional proposed forms were omitted because another canonical head, earlier key or retained form already owned them. Detailed decisions are in `final_form_review.json`; authors' preliminary form records remain available separately.

## Spelling evidence and source records

Current publisher records were checked using Merriam-Webster, Collins, Cambridge, Oxford, Dictionary.com and Vocabulary.com. Explicit closed alternatives and derived-word listings were checked separately from page redirects or user-submitted word suggestions. Publisher Burmese translations were not copied.

The final compound/split review added 1,317 entries to the spelling review list, each backed by publisher metadata in `staging/batches074_080/published_lexical_evidence.json`. Many flags are legitimate suffix derivatives accidentally split by the scanner, rather than English compounds. Genuine compound-looking words outside the scanner's flags received additional checks. The review list records established spellings; it does not make an invented glued expression acceptable.

The staging directory preserves authored sources, pronunciation/form review records, final overrides, unpublished candidates and validator results. Candidate pools are retained as deterministic zlib archives with hashes in `candidate_pool_archives.json`; the WordNet license is included. Full publisher retrieval text was reduced to spelling metadata, URLs, dates and record hashes. Staging packaging scripts target the Batch 073 baseline and should not be rerun against the advanced manifest without a new ownership review.

## Verification

- Every new batch passed `scripts/validate_extension_batch.py`, including all prior frozen and extension keys and earlier new batches.
- Deterministic lookup rebuild completed; the manifest advanced to 080/081.
- Separate extension artifact build and `--check` passed. The builder revalidated all 20 extension batches and verified the frozen artifact digest.
- `python -m unittest tests/test_extension_dictionary.py tests/test_phrase_dictionary.py`: **24 tests passed**.
- Every one of the 6,500 previous extension entries is unchanged in the rebuilt artifact. Frozen v1 files and phrase files have no Git diff.
- No duplicate canonical heads or lookup-owner collisions remain.

Extension artifact SHA-256 (UTF-8, LF): `2c0818ba6d5d835af2a28a5d2a98c0a96b6414d0af2c252bf9caf32a1bc16086`.

Cumulative Base64 lookup SHA-256 (trimmed): `2c7090b41fde9e462e84da2948a5952084730b4003db1dc85e855fdc0cef26f1`.

Frozen v1 artifact SHA-256 (UTF-8, LF), unchanged: `fcdb26986ed62bfaa130732ed0e88cc2e30bbc7f964b4b16de47f809783ed325`.

These checks establish structural integrity, deterministic packaging and the documented editorial review. Independent native Burmese editorial sign-off and actual Windows app loading/lookup testing have not been performed; production readiness is not claimed.
