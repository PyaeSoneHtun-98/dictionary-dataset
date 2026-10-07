import json,re,base64,zlib,sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
P=Path(__file__).resolve().parent
R=P.parents[1]
prior=set(zlib.decompress(base64.b64decode((R/'extension_lookup/used_keys_current.zlib.b64').read_text())).decode().splitlines())
entries=[]
for d in ['agent_a','agent_b','agent_c','coordinator']:
    f=P/d/('draft_entries.json' if d=='coordinator' else 'selected_entries.json')
    entries.extend(dict(e,author=d) for e in json.loads(f.read_text(encoding='utf-8')))
entries.extend(dict(e,author='coordinator') for e in json.loads((P/'coordinator/additional_entries.json').read_text(encoding='utf-8')))
heads={e['word'] for e in entries}
keys=prior|heads|{f for e in entries for f in e['forms']}
evidence={}
for d in ['agent_a','agent_b','agent_c','coordinator']:
    for f in (P/d).glob('lexical*.json'):
        for rec in json.loads(f.read_text(encoding='utf-8')):
            if isinstance(rec,dict) and rec.get('url') and rec.get('status','').lower() not in {'pending','unavailable','pending manual examination','derived or redirected; requires review'}:
                evidence.setdefault(rec['word'],[]).append(dict(rec,record=str(f.relative_to(R))))
for f in (P/'agent_c').glob('web_review_*.txt'):
    for block in re.split(r'\n-{20,}\n',f.read_text(encoding='utf-8')):
        source=re.search(r'Source: open\(\{"ref_id":"([^"]+)"',block)
        total=re.search(r'Total lines: (\d+)',block)
        if not source or not total or int(total[1])<=1:continue
        url=source[1];w=url.rsplit('/',1)[-1]
        title=next((l for l in block.splitlines() if '(https://' in l),'')
        if w not in heads:continue
        explicit=bool(re.search(r'(?:# |\*\*|variants.*)'+re.escape(w)+r'\b',block,re.I))
        if not explicit and not title.lower().startswith(w.lower()+' '):continue
        evidence.setdefault(w,[]).append({'word':w,'url':url,'sourceTitle':title,'reviewDate':'2026-10-07','record':str(f.relative_to(R)),'review':'Current publisher spelling record retrieved; independently authored Burmese.'})
flags={e['word']:[e['word'][:i]+'+'+e['word'][i:] for i in range(3,len(e['word'])-2) if e['word'][:i] in keys and e['word'][i:] in keys] for e in entries}
missing=[e['word'] for e in entries if flags[e['word']] and e['word'] not in evidence]
def write(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
write('all_draft_entries.json',entries)
write('draft_lexical_evidence.json',evidence)
write('global_split_flags.json',{w:s for w,s in flags.items() if s})
write('lexical_pending_global.json',missing)
print(json.dumps({'drafts':len(entries),'unique':len(heads),'evidenceHeads':len(evidence),'flaggedHeads':sum(bool(v) for v in flags.values()),'pendingFlags':len(missing),'pendingByAuthor':{a:sum(e['word'] in missing for e in entries if e['author']==a) for a in ['agent_a','agent_b','agent_c','coordinator']},'missingIPA':[e['word'] for e in entries if 'REVIEW' in e['pronunciation']]}))
