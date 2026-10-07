"""Package only new phrases, using the existing four-field runtime schema."""
import argparse
from phrase_extension_common import ARTIFACT, METADATA, json_bytes, snapshots, write_or_check


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        _, _, raw, metadata = snapshots()
        write_or_check(ARTIFACT, raw, args.write)
        write_or_check(METADATA, json_bytes(metadata), args.write)
        print(f"PASS canonical={metadata['canonicalPhrases']} forms={metadata['storedForms']} "
              f"lookup={metadata['lookupKeys']} sha256={metadata['sha256']}")
        return 0
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
