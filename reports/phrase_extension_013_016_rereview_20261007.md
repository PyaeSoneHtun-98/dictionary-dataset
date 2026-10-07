# Complete second review of phrase Batches 013–016

Reviewed all 1,000 canonical entries, 2,045 original stored forms and their Burmese meanings from baseline commit `4b9b047d6b44c68c8b8a48f24821f60690f75c18`. Three GPT-6.1 Sol agents with high reasoning reviewed Batches 014–016. The coordinator reviewed Batch 013, compared ownership across the frozen and new phrase datasets, and assessed all proposed corrections. An independent reviewer also checked all of Batch 013 and the coordinator's proposals. These are AI editorial reviews; no native Burmese human sign-off or Windows app test is claimed.

## Corrections applied

- **141 entries changed**: 14 in Batch 013, 20 in 014, 65 in 015 and 42 in 016. This includes coverage improvements, not 141 mistranslations.
- **11 canonical slots replaced** with independently verified, distinct expressions. Genuine alternative surfaces were consolidated under earlier extension owners wherever possible.
- **78 entries have revised meanings**, including replaced canonical slots. Corrections clarify agency, fix awkward Burmese, remove unnecessary restrictions and add useful missing senses.
- **84 entries have changed forms**. There are 652 added and 15 removed stored forms in the entry-level before/after comparison, a net increase of 637. Forms transferred from replaced owners are included in these entry-level totals.

| Batch | Entries | Idioms | Phrasal verbs | Expressions | Forms | Burmese meanings |
|---|---:|---:|---:|---:|---:|---:|
| 013 | 250 | 150 | 65 | 35 | 411 | 272 |
| 014 | 250 | 150 | 65 | 35 | 368 | 305 |
| 015 | 250 | 151 | 65 | 34 | 1,063 | 296 |
| 016 | 250 | 150 | 65 | 35 | 840 | 291 |
| Extension | 1,000 | 601 | 260 | 139 | 2,682 | 1,164 |

Combined frozen + extension totals: **4,000 canonicals, 7,509 stored forms, 11,509 lookup keys and 5,256 Burmese meanings**. Next active batch remains **017**.

## Variant ownership

| Replaced canonical | Replacement | Ownership decision |
|---|---|---|
| ace up your sleeve | pet peeve | Sleeve variants now belong to ace in the hole. |
| beside the point | double standard | Frozen that's beside the point already owns this expression; frozen assets unchanged. |
| at rock bottom | ride shotgun | Same low-point idiom as frozen hit rock bottom; do not count the state variant again. |
| for all you know | guilt by association | Pronoun substitution of frozen for all i know; frozen owner unchanged. |
| to all appearances | saving grace | To/from variants now belong to by all appearances. |
| get a raw deal | poetic justice | Useful get inflections now belong to raw deal. |
| go through the roof | take no prisoners | Same frozen through-the-roof idiom with a leading verb; adding its anger sense requires a future documented overlay. |
| live from hand to mouth | make a beeline for | Live inflections now belong to from hand to mouth. |
| open a can of worms | move the goalposts | Open inflections now belong to can of worms. |
| paper over the cracks | at cross purposes | Longer surfaces now belong to paper over. |
| play cat and mouse | run rings around | Play inflections now belong to cat and mouse. |

Cambridge explicitly groups [ace variants](https://dictionary.cambridge.org/dictionary/english/ace-up-sleeve?q=ace-up-your-sleeve) and [to/from/by all appearances](https://dictionary.cambridge.org/dictionary/english/to-from-all-appearances). Other decisions distinguish a new lexical meaning from a grammatical elaboration of an existing owner. We retained hard feelings versus the fixed reassurance no hard feelings, out of proportion with its independent disproportionate-state sense, and to the bone with cold/exhaustion intensity senses beyond frozen cut to the bone.

## Meaning and form examples

- Ivory tower now describes detachment from everyday reality rather than a group of intellectuals. From hand to mouth describes insufficient income for living needs, without asserting daily employment.
- Presumption of innocence, person of interest, hung jury, wrongful death and cease and desist now express the intended referent or action accurately. Cease and desist includes stopping conduct and a formal demand, rather than assuming every letter is a court order.
- Soak up separates learning from enjoying an atmosphere. Stack up covers relative standing and whether a story makes sense. Wash away includes removing dirt/evidence; draw blood includes medical sampling.
- Break your neck has neutral injury agency. Lick your wounds describes recovering after defeat or humiliation, and finite third-person forms use his/her rather than an incorrectly matched your.
- Useful irregular, possessive and noun-plural forms were reviewed. Put words in our/their mouths uses plural mouths. Come out smelling like roses and latch on to are variants under their existing owners.

Publisher URLs, original entries, full proposed replacements and reasons are in the batch review JSON/Markdown files under `staging/phrase_rereview_20261007/`. The coordinator's field-aware applier merged overlapping recommendations without reverting another reviewer's corrected gloss. `applied_changes.json` is the definitive before/after record. Review builders preserve authoring provenance and must not be rerun over these refined review records.

## Final verification

- All four batches have exactly 250 entries and pass structural, Burmese-text, token-length and cumulative ownership validation.
- **All 38 repository tests pass**. Deterministic manifest/index and artifact/metadata checks pass. There are zero exact canonical/form ownership collisions against the frozen base or between extension entries.
- Git comparison against baseline confirms all frozen phrase assets, frozen word assets and existing single-word extension assets unchanged.
- Runtime artifact: `dist/phrases_extension.json`, sorted by canonical phrase, retaining only the established four entry fields.
- Artifact SHA-256 (UTF-8/LF): `26a932d88b8bda52638de7eaf2bc1adb78e0b36099250fa8523f550853ffbb85`.
- Frozen phrase artifact hash remains `951a8bbe54824cf76728393791607798f878a062b19eca63e572278ba8f62926`.

Fresh outputs are saved in `staging/phrase_rereview_20261007/verification_results.json`. Automated checks do not prove semantic perfection. Native Burmese review and actual Windows app loading/lookup tests remain outstanding; the runtime contract still supports only contiguous matching over 2–5 tokens.
