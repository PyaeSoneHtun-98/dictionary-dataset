# Batch 070 editorial record

Created locally on 2026-10-02. Prior namespace after finalized Batch 069:
53,076 frozen/extension headword and form keys. The 27,883-item candidate pool
is the residual of the fresh WordNet/wordfreq pool documented in Batch 068.
WordNet definitions are review material, covered by the license in Batch 068.
Candidate pools and reserves are not approved runtime data.

All 500 selected Burmese meanings and General American IPA were manually
written in `authored_*.txt`. Translation services were not used. The shared
`staging/build_reviewed_batches.py` assembles those rows deterministically.
Count-noun plurals are opt-in; every stored form set was read and checked.
Manual irregulars include bethought, outfought, madwomen, sportswomen,
groomsmen, granulomata, neuromata and pleurae. Scintillating and freewheeling
retain their existing owners. Neologisms was supplied explicitly after the
morphology resource suggested both unchanged and plural forms.

`lexical_review.json` records current dictionary checks for every flagged
closed spelling, plus additional compound-looking words. Most checks use
Merriam-Webster. Lifehack uses Oxford's explicitly closed noun headword and
one-word IPA; other dictionaries also permit the open variant. No headword
was created by deleting spaces or hyphens. Accidental split matches such as
gibbet/glutton are legitimate dictionary words, not constructed compounds.
Schoolwide was dropped after current dictionary verification failed.
Frostbitten was replaced because canonical frostbite is already covered.
The closed noun screwup is kept; the open phrasal verb screw up is not added.

Covered variants whirr, grannie, phial, flautist and disfranchise were removed.
Semantic glosses and heteronyms are matched to their selected POS/senses.
Resource comparison records retain pronunciation differences for audit;
corruptive/cherubic retain proper consonant placement rather than importing
an automatic stress-conversion artifact. Antipersonnel uses unstressed /ɚ/.
Useful adjective comparatives were explicitly supplied and checked.

Run `.local-venv/Scripts/python.exe staging/build_reviewed_batches.py 70`,
then the extension validator and deterministic rebuild. Assembly reconstructs
prior ownership from frozen v1 and earlier extension batch files.

Validation: exactly 500 entries, 293 stored forms, 567 Burmese glosses,
no new headword/form collisions. After sync: total headwords 35,000,
lookup keys 53,869, latest batch 070, next batch 071. Frozen dictionary v1
and the phrase dictionary were not changed. See `review_summary.json`.
