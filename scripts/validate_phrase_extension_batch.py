"""Validate a phrase extension batch against immutable base and earlier batches."""
import argparse
from pathlib import Path
from phrase_extension_common import BATCH_RE, base_dataset, extension_paths, read_batch


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("batch", type=Path)
    parser.add_argument("--expected-batch", type=int)
    args = parser.parse_args()
    try:
        match = BATCH_RE.fullmatch(args.batch.name)
        if not match:
            raise ValueError("Invalid phrase extension batch filename")
        number = int(match[1])
        if args.expected_batch is not None and args.expected_batch != number:
            raise ValueError("Unexpected batch number")
        owners, _, _ = base_dataset()
        prior = [p for p in extension_paths() if int(BATCH_RE.fullmatch(p.name)[1]) < number]
        if len(prior) != number - 13:
            raise ValueError("Missing earlier extension batches")
        for expected, path in enumerate(prior, 13):
            read_batch(path, expected, owners)
        entries = read_batch(args.batch, number, owners)
        print(f"PASS batch={number:03d} entries=250 forms={sum(len(e['forms']) for e in entries)}")
        return 0
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
