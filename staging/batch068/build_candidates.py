"""Build a fresh, reviewable lexical pool; this never writes dictionary entries."""
import base64
import json
import re
import zlib
from pathlib import Path

from lemminflect import getAllLemmas
from nltk.corpus import wordnet as wn
from wordfreq import zipf_frequency

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
manifest = json.loads((ROOT / 'dictionary_extension_manifest.json').read_text(encoding='utf-8'))
assert manifest['latestBatch'] == 67 and manifest['nextBatch'] == 68
prior = set(zlib.decompress(base64.b64decode((ROOT / manifest['lookup']['path']).read_text().strip())).decode().splitlines())
assert len(prior) == manifest['lookup']['uniqueLookupKeys']
posmap = {'n': 'noun', 'v': 'verb', 'a': 'adjective', 's': 'adjective', 'r': 'adverb'}
upos = {'noun': 'NOUN', 'verb': 'VERB', 'adjective': 'ADJ', 'adverb': 'ADV'}
rows = []
for word in sorted(set(wn.all_lemma_names())):
    if word in prior or not re.fullmatch('[a-z]{4,22}', word):
        continue
    synsets = [s for s in wn.synsets(word) if any(l.name() == word for l in s.lemmas())]
    synsets = [s for s in synsets if not s.instance_hypernyms()]
    if not synsets:
        continue
    senses = []
    for s in synsets:
        pos = posmap[s.pos()]
        bases = {b.lower() for vals in getAllLemmas(word, upos=upos[pos]).values() for b in vals}
        if any(b != word for b in bases):
            continue
        senses.append({'pos': pos, 'definition': s.definition()})
    if not senses:
        continue
    freq = zipf_frequency(word, 'en')
    priority = max({'verb': 1.2, 'adjective': 0.8, 'adverb': 0.4, 'noun': 0}[s['pos']] for s in senses)
    split = [word[:i] + '+' + word[i:] for i in range(3, len(word)-2) if word[:i] in prior and word[i:] in prior]
    rows.append({'word': word, 'zipf': round(freq, 2), 'score': round(freq + priority, 2), 'senses': senses, 'possibleSplits': split})
rows.sort(key=lambda x: (-x['score'], -x['zipf'], x['word']))
(OUT / 'candidates.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
(OUT / 'candidate_summary.json').write_text(json.dumps({'count': len(rows), 'excludedLookupKeys': len(prior), 'sources': ['NLTK WordNet (including adjective satellites)', 'wordfreq', 'lemminflect POS-aware lemma suggestions'], 'selection': 'Requires manual lexical and subtitle-usefulness review; no automatic translations'}, indent=2) + '\n', encoding='utf-8')
print('Fresh candidate count:', len(rows))
for row in rows[:900]:
    print(row['word'] + ' | ' + str(row['zipf']) + ' | ' + ' || '.join(s['pos'] + ': ' + s['definition'] for s in row['senses'][:3]))
