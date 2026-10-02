# Batch 069 editorial record

Created locally on 2026-10-02, after Batch 068. Prior namespace: 52,118 keys.

The candidate pool is a fresh residual of the WordNet/wordfreq pool documented
in `../batch068/README.md`, with an additional current frequency-gap list.
It is substantially larger than 500. Pool items and reserves are review material,
not approved runtime entries. Names, brands, spelling variants, participles,
and low-value specialist candidates were rejected during selection.

All 500 selected entries have independently authored Burmese meanings and
manually written General American IPA in `authored_*.txt`. The pipe-separated
source format is word, POS, IPA, semicolon-separated meanings, optional forms.
A plus sign requests count-noun plural suggestions. Actual stored forms were
read and reviewed in `forms_review.json`; existing ownership is never reassigned.
Irregulars include outwore/outworn, bestrode/bestridden, misdealt, seraphim,
paparazzi, and the appropriate -men plurals. Tamales and perigees were supplied
explicitly after morphology suggestions returned the unchanged lemma.

`editorial_rejections.json` records 31 replacements with narrative vocabulary.
`lexical_review.json` records current Merriam-Webster closed-spelling checks,
including derivative entries bodybuilder and skateboarder. Expectorate is an
accidental expect+orate split, not a glued phrase. No spelling was manufactured
by removing separators. Dictionary checks were for spelling/sense/IPA only;
Burmese glosses were not copied from dictionary sources.

Reproduce with `.local-venv/Scripts/python.exe staging/build_reviewed_batches.py 69`.
Then run the extension validator and deterministic lookup rebuild. Assembly
reconstructs prior ownership from frozen v1 and earlier extension batches.
The runtime schema has no added fields. Frozen v1 and phrase assets are untouched.

Validation: 500 headwords, 458 stored forms, 567 Burmese glosses, no collisions.
Lookup after sync: 53,076 keys; total headwords: 34,500; next batch: 070.

Final review replaced extravert and marquis because extrovert and marquess are
already covered. Added doc (doctor sense) and homeboy, verified in current
Merriam-Webster. Added eight useful adjective forms. Updated lachrymose IPA
from current American dictionary evidence. The staged review summary and
selection list describe the final data; earlier comparison records retain the
original resource differences for audit.
