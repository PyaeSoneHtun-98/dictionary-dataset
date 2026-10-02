# Batch 068 local editorial record

Created on 2026-10-02 against master `c8298c9c421d70f58d8699db9b16015e14a0eeb7`.
The exclusion baseline contains 51,040 frozen-v1 / Batch 061–067 lookup keys.

## Sources and selection

`build_candidates.py` generated 28,938 fresh lexical candidates from WordNet,
wordfreq, and POS-aware lemminflect suggestions. It includes WordNet adjective
satellites, which the Batch 067 generator omitted. `candidates.json` preserves
that source pool; `blueprint.json` records the 500 selected entries and 44 reserve
candidates. Reserve candidates are not completed dictionary entries.

Every selected spelling is an exact WordNet lemma. No spaces or hyphens were
deleted to construct headwords. WordNet data is covered by `WORDNET_LICENSE.txt`.
Definitions in staging are lexical review material, not runtime dictionary fields
or sources of Burmese translations. All Burmese glosses were authored manually.

Established closed spellings were also checked in current dictionaries:

- [hydroplane](https://dictionary.cambridge.org/us/dictionary/english/hydroplane)
- [midfield](https://dictionary.cambridge.org/us/dictionary/english/midfield)
- [lowbrow](https://dictionary.cambridge.org/dictionary/english/lowbrow)
- [doppelganger](https://dictionary.cambridge.org/us/pronunciation/english/doppelganger)
- [postdoc](https://dictionary.cambridge.org/dictionary/english/postdoc?topic=university-and-college-education)
- [brainiac](https://www.oxfordlearnersdictionaries.com/us/definition/english/brainiac)
- [keyboardist](https://dictionary.cambridge.org/dictionary/english/keyboardist)
- [tradesman](https://dictionary.cambridge.org/dictionary/english/tradesman)

No selected headword triggers the validator's glued-compound heuristic. The
closed-compound allowlist was not changed.

## Editorial decisions

- Replaced `chaperon`, `curtsey`, `savannah`, and `lambast` because the lookup
  already covers `chaperone`, `curtsy`, `savanna`, and `lambaste`.
- Added common POS/senses for `love`, `land`, `page`, `wake`, `worth`, and `sweet`
  without exceeding three glosses per entry. These overrides are stored explicitly
  in `meanings_overrides.json`.
- Read all verb-form sets. Corrected morphology suggestions `unmaked`, `repoted`,
  and `repoting`; the actual forms are `unmade`, `repotted`, and `repotting`.
  `unmade` is excluded because it already belongs to the prior lookup.
- Added only manually reviewed count-noun plurals and useful comparatives.
  Actual irregulars include `woke`, `woken`, `seamen`, `tradesmen`, `bursae`, and
  `dominatrices`. Existing keys are omitted instead of being reassigned.
- Empty forms are retained for ordinary mass/abstract nouns and most adjectives
  and adverbs. Correct alternative inflections can coexist when both are useful.

## Pronunciation

Pronunciations use General American IPA. 426 explicit IPA rows cover missing
resource entries and selected resource corrections; all remaining CMU-derived
pronunciations were reviewed. The converter distinguishes stressed AH (`ʌ`) from
unstressed AH (`ə`) and uses rhotic ER. It never joins multiple spoken words by
deleting pronunciation whitespace.

Checks against current US pronunciation entries included
[estuarine](https://dictionary.cambridge.org/pronunciation/english/estuarine),
[garrote](https://dictionary.cambridge.org/pronunciation/english/garrote),
[fecund](https://dictionary.cambridge.org/us/pronunciation/english/fecund),
[remonstrate](https://dictionary.cambridge.org/us/dictionary/english/remonstrate),
[betroth](https://dictionary.cambridge.org/us/pronunciation/english/betroth), and
[sommelier](https://dictionary.cambridge.org/us/pronunciation/english/sommelier).
Only spelling, sense, and pronunciation were checked; proprietary Burmese
translations were not copied.

## Local reproduction

The local Python environment and corpus downloads are ignored by Git.
Install the packages listed in `requirements.txt` into `.local-venv`, and download
WordNet to `.local-nltk` for candidate generation. Candidate generation requires
the original Batch 067 manifest baseline; assembly reconstructs its prior keys
from frozen v1 and earlier extension batches, so assembly remains reproducible
after the extension manifest advances.

```powershell
.\.local-venv\Scripts\python.exe staging/batch068/assemble.py
python scripts/validate_extension_batch.py DictionaryExtensionBatches/dictionary_batch_068.json --expected-batch 68
python scripts/rebuild_extension_lookup.py --write
python scripts/rebuild_extension_lookup.py
```

`review_summary.json` records final counts and the LF-normalized batch SHA-256.
The structural validator does not replace linguistic review.
