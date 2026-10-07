"""Assemble manually authored candidate meanings/IPA and explicit forms."""
import base64, hashlib, json, re, sys, zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
STAGE = Path(__file__).resolve().parent
sys.stdout.reconfigure(encoding='utf-8')
used = set(zlib.decompress(base64.b64decode((ROOT/'extension_lookup/used_keys_current.zlib.b64').read_text().strip())).decode().splitlines())
rejected = {line.strip() for line in (ROOT/'extension_rejected_headwords.txt').read_text().splitlines() if line and not line.startswith('#')}
pruned = {line.split('|')[0].strip() for line in (STAGE/'prune.txt').read_text().splitlines() if line and not line.startswith('#')} if (STAGE/'prune.txt').exists() else set()
entries=[]
for path in sorted(STAGE.glob('authored_*.txt')):
    for line in path.read_text(encoding='utf-8').splitlines():
        if not line.strip(): continue
        parts=line.split('|'); assert len(parts) in (4,5),(path,line)
        w,pos,ipa,gloss=parts[:4]
        assert re.fullmatch('[a-z]+',w) and w not in used|rejected,w
        assert int(hashlib.sha256(w.encode()).hexdigest(),16)%10 == 9,w
        if w in pruned: continue
        assert re.fullmatch('/[^/]+/',ipa) and not any(c.isspace() for c in ipa),w
        forms=parts[4].split(',') if len(parts)==5 else []
        entries.append({'word':w,'pronunciation':ipa,'forms':forms,'meanings':[{'partOfSpeech':pos,'burmese':gloss.split(';')}]})
assert len({e['word'] for e in entries})==len(entries)
heads={e['word'] for e in entries}; owned=used|heads; review=[]
for e in entries:
    stored=[]; excluded=[]
    for f in dict.fromkeys(e['forms']):
        assert re.fullmatch('[a-z]+',f),(e['word'],f)
        if f in owned: excluded.append(f)
        else:stored.append(f);owned.add(f)
    review.append({'word':e['word'],'proposed':e['forms'],'stored':stored,'excluded':excluded})
    e['forms']=stored
entries.sort(key=lambda e:e['word'])
for name,data in [('selected_entries.json',entries),('form_review.json',review)]:
    (STAGE/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'candidates':len(entries),'forms':sum(len(e['forms']) for e in entries),'glosses':sum(len(m['burmese']) for e in entries for m in e['meanings'])}))
