"""Package manually authored rows; never generate meanings or inflections."""
import base64
import hashlib
import json
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
sys.stdout.reconfigure(encoding='utf-8')
prior = set(zlib.decompress(base64.b64decode((REPO/'extension_lookup/used_keys_current.zlib.b64').read_text())).decode().splitlines())
rejected = {x.strip() for x in (REPO/'extension_rejected_headwords.txt').read_text().splitlines() if x.strip() and not x.startswith('#')}
entries = {}
sources = {}
removed_forms = []
rejections = {'skullduggery': 'Spelling variant of covered skulduggery; retain one lookup owner.', 'disfranchise': 'Covered verb variant of disenfranchise; prefer the existing canonical lemma.'}
for path in sorted(ROOT.glob('authored_*.psv')):
    for number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        if not line.strip():
            continue
        word, pos, ipa, forms, *glosses = line.split('|')
        assert int(hashlib.sha256(word.encode()).hexdigest(),16)%10 == 9, word
        assert word not in prior, word
        assert word not in rejected, word
        if word in rejections:
            continue
        entry = entries.setdefault(word, dict(word=word, pronunciation=ipa, forms=[], meanings=[]))
        assert entry['pronunciation'] == ipa, word
        for form in forms.split(','):
            if not form or form in entry['forms']:
                continue
            if form in prior or form in rejected:
                removed_forms.append({'word':word, 'form':form, 'reason':'Prior lookup/rejected key'})
            else:
                entry['forms'].append(form)
        entry['meanings'].append(dict(partOfSpeech=pos, burmese=glosses))
        sources.setdefault(word, []).append({'path':str(path.relative_to(REPO)).replace('\\','/'), 'line':number})
for item in json.loads((REPO/'staging/batches071_080/reserves.json').read_text(encoding='utf-8')):
    entry = item['entry']
    word = entry['word']
    if int(hashlib.sha256(word.encode()).hexdigest(),16)%10 != 9 or not item['reason'].startswith('Candidate surplus'):
        continue
    assert word not in entries, word
    if word in prior or word in rejected:
        rejections[word] = 'Prior/rejected lookup key'
        continue
    entry['forms'] = [f for f in entry['forms'] if f not in prior and f not in rejected]
    entries[word] = entry
    sources[word] = [{'path':'staging/batches071_080/reserves.json', 'review':'Individually retained descriptive, narrative, concrete or business word; previous surplus was not an editorial rejection.'}]
heads = set(entries)
owners = {word:word for word in heads}
for entry in entries.values():
    kept = []
    for form in entry['forms']:
        if form in heads:
            removed_forms.append({'word':entry['word'], 'form':form, 'reason':'Separate draft canonical headword reserved before forms'})
            continue
        assert form not in owners, (form, entry['word'], owners.get(form))
        owners[form] = entry['word']
        kept.append(form)
    entry['forms'] = kept
    assert sum(len(m['burmese']) for m in entry['meanings']) <= 3, entry['word']
def write(name, value):
    (ROOT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
write('draft_entries.json', list(entries.values()))
write('authorship.json', sources)
write('form_review.json', removed_forms)
write('rejections.json', rejections)
print(json.dumps({'headwords':len(entries), 'storedForms':sum(len(e['forms']) for e in entries.values()), 'priorKeys':len(prior), 'removedForms':len(removed_forms)}))
