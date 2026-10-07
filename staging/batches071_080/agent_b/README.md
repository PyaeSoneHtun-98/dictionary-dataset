# Agent B curated continuation candidates

The user's quality-first steering superseded the initial three-batch quota. This directory supplies **737 complete entries** for root's global editorial selection and contiguous 500-entry batch assembly. No final extension batches, manifests, lookup files, frozen assets, commits or pushes were written.

- `selected_entries.json`: complete runtime-schema candidate entries; 234 stored forms and 814 independently authored Burmese meanings.
- `authored_1.txt`, `authored_2.txt`, `authored_3.txt`: manually authored exploratory source rows. Uppercase `N` explicitly requests reviewed count-noun plurals; lowercase `n` is a mass/abstract noun. These files include rejected drafts and should not be integrated directly.
- `editorial_exclusions*.txt`, `editorial_review.json`: extensive removal of rare specialist vocabulary, archaic words, weak derivatives and covered spelling variants. The original 1,514-unique exploratory pool was substantially reduced.
- `lexical_review.json`: current reputable dictionary evidence for all 207 validator split flags and additional closed compounds. Evidence is spelling review only; Burmese meanings were independently written. Cambridge explicitly recognizes `anticorruption`, and Merriam-Webster explicitly recognizes `pinkeye` as a closed variant. The allowlist has not been changed.
- `deferred_lexical_entries.json`: four plausible words whose current dictionary evidence remains pending (`mirrorless`, `fanless`, `pantsless`, `epicness`). Failed page retrieval is not evidence of invalidity. Do not integrate without further lexical review.
- `manual_ipa.txt`, `manual_cmu_corrections.txt`, `reviewed_derivative_ipa.json`, `derivative_ipa_review_notes.json`, `ipa_review.json`: General American pronunciation sources and manual review, including 26 corrections to CMU stress/POS-related readings. Examples corrected include `unbowed`, `dauphin`, `copayment`, `overreliance`, `transformative`, and `tightfisted`.
- `form_review.json`: explicit proposals, stored forms and omitted collisions. Irregular plurals reviewed include `clostridia`, `candelabra`, `columbaria`, `effluvia`, `dybbukim`, and `kinswomen`; `peshmerga` receives no invented plural. The root must check forms across the combined candidate pool.
- `validation_summary.json`: successful local structural, namespace, IPA-character, Burmese, sense-count, prior-collision and within-pool ownership checks.

Run `.local-venv/Scripts/python.exe staging/batches071_080/agent_b/assemble.py`, then `audit.py` to reproduce these files. The canonical extension validator must run after root selects entries and integrates predecessor batches. Final batch numbering remains root's responsibility.
