"""Rebuild or check the separate cumulative phrase extension index/manifest."""
import argparse
from phrase_extension_common import INDEX, MANIFEST, json_bytes, snapshots, write_or_check


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    try:
        manifest, encoded, _, _ = snapshots()
        write_or_check(INDEX, (encoded + "\n").encode("ascii"), args.write)
        write_or_check(MANIFEST, json_bytes(manifest), args.write)
        print(f"PASS batches={manifest['extensionBatchCount']} extension={manifest['extensionPhrases']} "
              f"total={manifest['totalPhrases']} lookup={manifest['lookup']['uniqueLookupKeys']} "
              f"nextBatch={manifest['nextBatch']:03d}")
        return 0
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
