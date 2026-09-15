# Lookup index

This directory stores the cumulative exclusion keys used when generating new batches.

Each key is either:

- a previously used headword, or
- a stored inflected form from a previous entry.

The index is sharded alphabetically as plain UTF-8 text, one key per line, so it can be inspected directly through GitHub without downloading every historical batch.

Current shard files:

- `used_a.txt`
- `used_b.txt`
- `used_c.txt`
- `used_de.txt`
- `used_fj.txt`
- `used_ko.txt`
- `used_p.txt`
- `used_qr.txt`
- `used_s.txt`
- `used_tz.txt`

The shards initially represent Batches 001–023. After every new batch, add its headwords and forms to the appropriate shards, sort each shard, and keep keys unique.

The union of these files is the authoritative duplicate-exclusion set.
