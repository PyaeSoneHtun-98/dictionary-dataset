# Dictionary Extension Lexical Audit — 2026-09-30

## Scope

Audited post-v1 single-word extension Batches 061–068 against the repository's
single-word policy.

Frozen Dictionary v1.0.0 (Batches 001–060, 30,000 headwords) is not modified.

## Finding

The extension contains systematic open/hyphenated English expressions that were
made to look like single-word headwords by removing spaces or hyphens.

A conservative automated signal is whitespace inside the IPA while the stored
headword has no whitespace:

| Batch | IPA indicates multiple spoken words |
| --- | ---: |
| 061 | 2 / 500 |
| 062 | 2 / 500 |
| 063 | 12 / 500 |
| 064 | 19 / 500 |
| 065 | 21 / 500 |
| 066 | 48 / 500 |
| 067 | 30 / 500 |
| 068 | 500 / 500 |

This is a lower bound, not the total number of bad lexical entries, because some
glued expressions also had IPA written without spaces.

Examples include `parkinglot`, `machinelearning`, `voiceactor`,
`moneylaundering`, `digitalfootprint`, `relationshipadvice`,
`alarmclock`, `birthdaycake`, `customerservice`, and `socialmedia`.

## Repair decision

Because contamination spans every unfrozen extension batch and becomes severe in
later batches, Batches 061–068 are removed from the active extension layer and
the extension is reset to the frozen 30,000-headword v1 baseline.

The pre-audit state is preserved on branch:

`archive/extension-061-068-pre-audit-2026-09-30`

and remains recoverable from Git history.

The next clean extension batch is therefore Batch 061.

## Validator hardening

`scripts/validate_extension_batch.py` now rejects:

1. whitespace inside IPA for a single-word extension headword; and
2. suspicious concatenations that can be segmented into two previously known
   lookup keys, unless the exact closed compound was manually reviewed and
   recorded in `extension_closed_compound_allowlist.txt`.

The allowlist is for verified established closed compounds only. It must never be
used to approve an open or hyphenated expression after deleting separators.
