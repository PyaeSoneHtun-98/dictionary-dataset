"""Publish the reviewed 1,000-entry selection as four independent 250-entry batches."""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from phrase_extension_common import BATCH_DIR, base_dataset, json_bytes, validate_entries


def main():
    if any(BATCH_DIR.glob("phrase_batch_*.json")):
        raise ValueError("This publication script only initializes Batches 013–016; refusing to overwrite batches")
    entries = json.loads((Path(__file__).parent / "selected_entries.json").read_text(encoding="utf-8"))
    if len(entries) != 1000 or Counter(e["type"] for e in entries) != {"idiom": 600, "phrasal_verb": 260, "expression": 140}:
        raise ValueError("Unexpected reviewed selection count/type distribution")
    owners = base_dataset()[0]
    errors = validate_entries(entries, owners)
    if errors:
        raise ValueError("\n".join(errors))
    by_type = {t: [e for e in entries if e["type"] == t] for t in ["idiom", "phrasal_verb", "expression"]}
    quota = {"idiom": 150, "phrasal_verb": 65, "expression": 35}
    # Interleave types while preserving the editorial usefulness order within each type.
    positions = sorted(( (j + 0.5) / count, t, j)
                       for t, count in quota.items() for j in range(count))
    BATCH_DIR.mkdir(parents=True, exist_ok=True)
    for offset, number in enumerate(range(13, 17)):
        batch = [by_type[t][offset * quota[t] + j] for _, t, j in positions]
        path = BATCH_DIR / f"phrase_batch_{number:03d}.json"
        path.write_bytes(json_bytes({"version": 1, "batch": number, "entries": batch}))
        print(f"WROTE {path.name} entries=250 types={dict(Counter(e['type'] for e in batch))}")


if __name__ == "__main__":
    main()
