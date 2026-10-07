# Extension Batches 071–073 review — 2026-10-07

Added **1,500 independently authored headwords**, **603 stored forms** and **1,668 Burmese glosses** in three complete batches. The user requested ten batches, then explicitly chose **“Keep subtitle usefulness”** when asked whether rarer vocabulary should be included to reach the count. This run therefore stops at three full batches and leaves Batch 074 next.

| Batch | Headwords | Forms | Burmese glosses |
| --- | ---: | ---: | ---: |
| 071 | 500 | 234 | 547 |
| 072 | 500 | 195 | 563 |
| 073 | 500 | 174 | 558 |
| Added | 1,500 | 603 | 1,668 |

The extension now has **13 batches, 6,500 headwords, 4,386 stored forms and 10,886 lookup keys**. Together with frozen v1, the dataset has **36,500 headwords** and **56,703 exclusion keys**.

## Selection and authorship

Baseline: `7be581cc925e8c097cf89efdf973b1f65a62da66`, through Batch 070, with 54,600 exclusion keys. Candidates were drawn from locally installed WordNet and wordfreq resources and manually selected for plausible subtitle, conversation, narrative, news and documentary use. English sense resources were selection aids; Burmese meanings were independently authored.

Three parallel GPT-6.1 Sol agents at high reasoning, as requested by the user, supplied 437, 737 and 577 complete candidate entries. The coordinator supplied 268. SHA-256 headword partitioning prevented duplicate draft headwords across authors; forms were checked again across the combined pool.

The 2,019 candidate entries received further coordinator review. Of these, 195 were rejected or deferred for spelling variants, elementary coverage, specialist vocabulary, archaic vocabulary or unresolved spelling evidence. The remaining 1,824 candidates were ordered by subtitle usefulness, using wordfreq 3.1.1 English Zipf frequencies as a tie-breaker and explicit promotions for useful dialogue and conflict vocabulary. Only three complete 500-entry batches were packaged. The other 519 drafts are recorded in `staging/batches071_080/reserves.json`; they are candidates, including rejected/deferred drafts, and **must not be loaded as approved dictionary data**.

Agent A completed a peer review of the coordinator's draft. The additional requested peer reviews of Agents A and B stopped when the agents hit their account usage limit. The coordinator continued reviewing the saved drafts locally. The work does not constitute independent native-speaker sign-off.

## Corrections and spelling evidence

The final override record is `staging/batches071_080/final_review_overrides.json`. Corrections include:

- `quadriplegia`: paralysis of all four limbs, without incorrectly specifying a stroke as the cause.
- `bisection`: division into two equal parts.
- `partway`: part of the way, without fixing the distance at one half.
- `wildcard`: the unpredictable-person/thing sense alongside the computing sense.
- `tailgater`: someone driving too close behind the preceding vehicle.
- `bulgur`: cracked wheat, rather than flour.
- `antiterrorism`: noun POS for prevention/counteraction of terrorism.
- General American IPA adjustments for `pascal`, `semiofficial`, `preterm`, `entrepreneurialism` and `whew`.

Useful comparative forms were manually added for `pointy`, `saggy`, `bendy`, `croaky` and `snarly`. Prior keys and all selected headwords were reserved before any new forms were assigned. `cowry` was excluded as a spelling variant of the selected `cowrie`; the final published set has no ownership collisions.

The spelling review contains 545 source records for published words in `staging/batches071_080/published_lexical_evidence.json`. Reputable current dictionaries confirm the selected closed compounds and scanner false positives. The scanner was conservatively run against all old and selected new keys, producing 460 new allowlist records; many are ordinary derivatives such as `spaciousness`, rather than compounds. Each has a recorded dictionary URL and review decision. No unverified glued expression was added to the allowlist.

For example, [Merriam-Webster confirms handsewn](https://www.merriam-webster.com/dictionary/handsewn), and [Collins confirms gunsight](https://www.collinsdictionary.com/us/dictionary/english/gunsight). `eveningwear` was deferred because closed spelling was not established in the sources checked; [Collins lists evening wear as an open expression](https://www.collinsdictionary.com/us/dictionary/english/evening-wear). Failed retrieval alone was not treated as proof that a word is invalid.

## Validation and packaging

All three staged batches passed `scripts/validate_extension_batch.py`, with the complete baseline namespace and earlier staged batches as exclusions. The standard artifact builder then validated all 13 canonical extension batches and rebuilt the separate artifact. Validation found zero prior-key overlaps, duplicate headwords, headword/form collisions or form/form collisions. Schema, Burmese-only glosses, permitted POS, the three-gloss limit and single-word IPA checks passed.

The following checks passed:

```text
python scripts/rebuild_extension_lookup.py --write
python scripts/build_extension_artifact.py --write
python scripts/build_extension_artifact.py --check
python -m unittest tests/test_extension_dictionary.py tests/test_phrase_dictionary.py
git diff --check
```

All **24 regression tests** passed. Frozen v1 and phrase assets have no Git changes. The frozen artifact's normalized UTF-8/LF SHA-256 remains `fcdb26986ed62bfaa130732ed0e88cc2e30bbc7f964b4b16de47f809783ed325`.

Extension artifact SHA-256: `adce3b14873d53e747d16a7d264f751d66c61fd320e4db3a87b1b90091237481` (UTF-8/LF).

Combined lookup SHA-256: `782e074145d452eed4e705d7d494c6296c0cfdc2c01251e27c762159186eb128` (trimmed Base64).

Per-batch hashes and counts are in `staging/batches071_080/publication_summary.json`. Source rows, pronunciation/form reviews, spelling URLs and final selection decisions are retained under that staging directory. The large transient candidate pools were omitted; Agent A's pool retains only membership words required by its historical assembly script. WordNet licensing is already recorded at `staging/batch068/WORDNET_LICENSE.txt`.

The agent assembly scripts are historical draft tools and assume the baseline exclusion state. To reproduce final selection from the saved complete drafts, use `finish_review.py` followed by `package_reviewed.py` in `staging/batches071_080/`; these reconstruct exclusions through Batch 070. Final runtime files are the canonical batches and `dist/dictionary_extension.json`.

Full native-speaker editorial sign-off and loading/lookup testing in the actual Windows application remain unperformed release checks. Passing dataset validation does not by itself establish production readiness.
