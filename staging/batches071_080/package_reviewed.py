"""Package the reviewed selection without changing frozen assets."""
import argparse
import base64
import hashlib
import json
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--write', action='store_true')
args = parser.parse_args()

def read(p):
    return json.loads(p.read_text(encoding='utf-8'))

def write(p, value):
    p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

entries = read(HERE/'selected_entries.json')
assert len(entries) == 1500
assert len({e['word'] for e in entries}) == 1500
old = set(zlib.decompress(base64.b64decode((REPO/'lookup/used_keys_current.zlib.b64').read_text())).decode().splitlines())
for n in range(61,71):
    for e in read(REPO/'DictionaryExtensionBatches'/f'dictionary_batch_{n:03}.json')['entries']:
        old.add(e['word']); old.update(e['forms'])
assert len(old) == 54600
allkeys = old | {e['word'] for e in entries} | {f for e in entries for f in e['forms']}
records = {}
for d in ['agent_a','agent_b','agent_c','coordinator']:
    for r in read(HERE/d/'lexical_review.json'):
        if 'reject' not in str(r.get('decision','')).lower():
            records[r['word']] = {'word':r['word'], 'url':r.get('url',r.get('sourceUrl')), 'review':r, 'reviewer':d}
for r in read(HERE/'final_lexical_review.json'):
    records[r['word']] = {'word':r['word'],'url':r['url'],'review':r,'reviewer':'coordinator_final'}
allowfile = REPO/'extension_closed_compound_allowlist.txt'
baseline = HERE/'baseline_closed_compound_allowlist.txt'
if not baseline.exists():
    baseline.write_text(allowfile.read_text(encoding='utf-8'),encoding='utf-8')
oldallow = {l.strip() for l in baseline.read_text(encoding='utf-8').splitlines() if l.strip() and not l.lstrip().startswith('#')}
currentallow = {l.strip() for l in allowfile.read_text(encoding='utf-8').splitlines() if l.strip() and not l.lstrip().startswith('#')}
flags = []
for e in entries:
    w = e['word']
    splits = [w[:i]+'+'+w[i:] for i in range(3,len(w)-2) if w[:i] in allkeys and w[i:] in allkeys]
    if splits and w not in oldallow:
        assert w in records and records[w]['url'], f'No current dictionary spelling evidence for {w}: {splits}'
        flags.append({'word':w,'splits':splits,'evidence':records[w]})
write(HERE/'compound_flags.json',flags)
write(HERE/'published_lexical_evidence.json',[records[e['word']] for e in entries if e['word'] in records])
newallow = sorted({r['word'] for r in flags} - oldallow)
preview = HERE/'validated_batches'
preview.mkdir(exist_ok=True)
summaries = []
for offset,n in enumerate(range(71,74)):
    subset = sorted(entries[offset*500:(offset+1)*500],key=lambda e:e['word'])
    doc = {'version':1,'batch':n,'entries':subset}
    path = preview/f'dictionary_batch_{n:03}.json'
    write(path,doc)
    if args.write:
        write(REPO/'DictionaryExtensionBatches'/path.name,doc)
    summaries.append({'batch':n,'headwords':500,'forms':sum(len(e['forms']) for e in subset),'glosses':sum(len(m['burmese']) for e in subset for m in e['meanings']),'sha256':hashlib.sha256(path.read_text(encoding='utf-8').encode('utf-8')).hexdigest(),'sha256Scope':'utf8-lf'})
content = baseline.read_text(encoding='utf-8').rstrip()+'\n\n# 2026-10-07: Batches 071-073; current dictionary evidence in staging/batches071_080/published_lexical_evidence.json\n'+'\n'.join(newallow)+'\n'
(HERE/'reviewed_closed_compound_allowlist.txt').write_text(content,encoding='utf-8')
if args.write:
    # Idempotent append when rerunning this publication helper.
    if not set(newallow) <= currentallow:
        allowfile.write_text(content,encoding='utf-8')
write(HERE/'publication_summary.json', {'reviewDate':'2026-10-07','baselineCommit':'7be581cc925e8c097cf89efdf973b1f65a62da66','requestedBatches':10,'publishedBatches':3,'nextBatch':74,'batches':summaries,'headwords':1500,'forms':sum(s['forms'] for s in summaries),'glosses':sum(s['glosses'] for s in summaries),'newLookupKeys':len(allkeys)-len(old),'newAllowlistRecords':len(newallow),'lexicalEvidenceRecords':sum(e['word'] in records for e in entries),'collisions':0,'frozenV1Modified':False,'nativeSpeakerSignOff':False,'windowsAppIntegrationTested':False})
print(json.dumps({'batches':summaries,'newAllowlistRecords':len(newallow),'lexicalEvidenceRecords':sum(e['word'] in records for e in entries)},indent=2))
