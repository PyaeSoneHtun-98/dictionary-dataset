# Dictionary batches

New generated batch files live here as:

`dictionary_batch_XXX.json`

Each batch contains exactly 500 entries.

Batches 001–023 were generated before this GitHub workflow was initialized. Their prior lookup keys are preserved in `lookup/` so Batch 024 and later can be generated without collisions.

From Batch 024 onward, every completed batch should be committed here and `dictionary_manifest.json` must be updated in the same workflow.
