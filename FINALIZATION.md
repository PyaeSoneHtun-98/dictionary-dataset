# Subtitle Bridge Dictionary v1.0 Finalization

Release status: Frozen
Source commit: 630e0a1d10f5b5505734295dc44e6edde2a022d1
Artifact: dist/dictionary_v1.json
Artifact SHA-256: fcdb26986ed62bfaa130732ed0e88cc2e30bbc7f964b4b16de47f809783ed325

## Final corpus

- Batch files: 60
- Unique headwords: 30000
- Stored forms: 15864
- Burmese semantic meanings: 38001
- Unique lookup keys: 45817
- Form-to-form collisions: 0
- Headword-to-form overlaps: 47
- Structural blocking errors: 0

The release artifact is generated deterministically from Batches/dictionary_batch_001.json
through Batches/dictionary_batch_060.json. The 60 batch files remain the source dataset.

## Lookup policy

Exact headwords take precedence over stored inflected forms. The following headword/form
overlaps are intentional and non-blocking:

- accustomed <- form of accustom
- agitated <- form of agitate
- alleged <- form of allege
- amazed <- form of amaze
- astonished <- form of astonish
- astonishing <- form of astonish
- baffling <- form of baffle
- bargaining <- form of bargain
- bewildered <- form of bewilder
- bleeding <- form of bleed
- charming <- form of charm
- classified <- form of classify
- compelling <- form of compel
- complicated <- form of complicate
- concerned <- form of concern
- confused <- form of confuse
- convincing <- form of convince
- damaged <- form of damage
- dazzling <- form of dazzle
- determined <- form of determine
- devastated <- form of devastate
- disappointed <- form of disappoint
- disturbing <- form of disturb
- embarrassed <- form of embarrass
- enraged <- form of enrage
- forbidden <- form of forbid
- frozen <- form of freeze
- frustrated <- form of frustrate
- healing <- form of heal
- hidden <- form of hide
- limited <- form of limit
- missing <- form of miss
- obsessed <- form of obsess
- overwhelming <- form of overwhelm
- poisoning <- form of poison
- premises <- form of premise
- prevailing <- form of prevail
- relieved <- form of relieve
- satisfied <- form of satisfy
- scared <- form of scare
- smuggling <- form of smuggle
- stranger <- form of strange
- subdued <- form of subdue
- understanding <- form of understand
- undone <- form of undo
- warning <- form of warn
- wounded <- form of wound

No stored form is owned by two different headwords.

## Intentionally form-less verb entries

These 30 entries remain without stored inflections because they are defective/fixed-expression
verbs, spelling variants whose forms collide with preferred headwords, or rare/archaic/specialized
items where automatically inventing forms would reduce data quality:

beware, daresay, distil, analyse, fulfil, instil, demonise, snafu, tink, rive, coif, lour, abye, airt, cere, larn, nett, rede, shew, slue, spue, breaststroke, brevet, clinker, whiteout, teargas, outcall, precis, chasse, applique

## Legacy fallback coverage

The 30,000-headword corpus does not contain these 16 basic/legacy-only entries:

bad, big, day, do, go, humiliating, love, man, new, no, run, say, see, thanks, wait, yes

They should be handled during Subtitle Bridge integration as a small structured core supplement
(or another explicit structured coverage mechanism) before the old flat fallback is removed.
They were not inserted into this 30,000-headword corpus merely to satisfy legacy parity.

## Quality/audit scope

Finalization included:

- all 60 batch files and exactly 30,000 unique headwords;
- schema, POS, pronunciation shape, Burmese-field, and max-three-meaning validation;
- global duplicate and collision checks;
- deterministic cumulative lookup-index rebuild;
- verb-inflection audit and targeted missing-form repair;
- frequency-assisted detection and correction of high-confidence form spelling errors;
- removal and future rejection of invisible Unicode format characters in IPA strings;
- deterministic release-artifact SHA-256 verification;
- cross-batch sampling of Burmese meanings and pronunciation/form data.

This is an AI-authored English-to-Burmese dataset. Structural and targeted quality audits do not
replace a future native/bilingual editorial review of every one of the 30,000 entries.
