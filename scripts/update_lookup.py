#!/usr/bin/env python3
"""Add one validated batch's headwords/forms to the sharded cumulative lookup index."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

SHARDS = [
    ("a", set("a")),
    ("b", set("b")),
    ("c", set("c")),
    ("de", set("de")),
    ("fj", set("fghij")),
    ("ko", set("klmno")),
    ("p", set("p")),
    ("qr", set("qr")),
    ("s", set("s")),
    ("tz", set("tuvwxyz")),
]


def shard_name(key: str) -> str:
    first = key[:1].lower()
    for name, letters in SHARDS:
        if first in letters:
            return name
    raise ValueError(f"unsupported lookup key initial: {key!r}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("batch", type=Path)
    ap.add_argument("--lookup-dir", type=Path, default=Path("lookup"))
    args = ap.parse_args()

    data = json.loads(args.batch.read_text(encoding="utf-8"))
    additions: dict[str, set[str]] = {name: set() for name, _ in SHARDS}

    for entry in data["entries"]:
        for key in [entry["word"], *entry.get("forms", [])]:
            additions[shard_name(key)].add(key)

    total = 0
    for name, _ in SHARDS:
        path = args.lookup_dir / f"used_{name}.txt"
        current = set(path.read_text(encoding="utf-8").splitlines()) if path.exists() else set()
        current.discard("")
        current |= additions[name]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(sorted(current)) + "\n", encoding="utf-8")
        total += len(current)
        print(f"{path}: {len(current)} keys")

    print("total unique lookup keys:", total)


if __name__ == "__main__":
    main()
