#!/usr/bin/env python3
import json
from pathlib import Path

def norm(s): return s.strip().casefold()

used=set()
for path in sorted(Path("Batches").glob("dictionary_batch_*.json")):
    data=json.loads(path.read_text(encoding="utf-8"))
    for e in data["entries"]:
        used.add(norm(e["word"]))
        for f in e.get("forms",[]): used.add(norm(f))

src=Path("staging/dictionary_061_candidates.txt")
words=[]
seen=set()
for raw in src.read_text(encoding="utf-8").split():
    w=norm(raw)
    if not w.isalpha() or "-" in w or w in seen: continue
    seen.add(w)
    if w not in used: words.append(w)

out={"candidateCount":len(seen),"survivorCount":len(words),"survivors":words}
Path("staging/dictionary_061_survivors.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"candidateCount":len(seen),"survivorCount":len(words)},indent=2))
