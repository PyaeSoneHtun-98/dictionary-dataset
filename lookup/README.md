# Lookup index

This directory stores the cumulative lookup-key index for the Subtitle Bridge dictionary.

The canonical current index is:

- `used_keys_current.zlib.b64`

It is Base64-encoded zlib-compressed UTF-8 text with one normalized lookup key per line before compression.

A lookup key is either:

- one of the 30,000 dictionary headwords, or
- a stored inflected form.

The index is rebuilt deterministically from all 60 JSON source batches with:

```bash
python scripts/rebuild_lookup.py
```

`dictionary_manifest.json` records the current headword/form/key counts and the SHA-256 for the encoded index.

Batches 001–060 are all mirrored under `Batches/`; the compressed current index is derived data, not a substitute for the source batches.
