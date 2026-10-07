import base64,hashlib,json,re,sys,zlib
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];STAGE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'scripts'))
from validate_extension_batch import ALLOWED_POS,IPA_CHARACTERS,MYANMAR_LETTER
prior=set(zlib.decompress(base64.b64decode((ROOT/'extension_lookup/used_keys_current.zlib.b64').read_bytes())).decode().splitlines())
prior.update(w.strip() for w in (ROOT/'extension_rejected_headwords.txt').read_text().splitlines() if w.strip() and not w.startswith('#'))
a=json.loads((STAGE/'selected_entries.json').read_text(encoding='utf-8'));heads={e['word'] for e in a};assert len(heads)==len(a)
owned=set(heads);forms=0;glosses=0
for e in a:
 assert set(e)=={'word','pronunciation','forms','meanings'}
 w=e['word'];assert re.fullmatch('[a-z]+',w) and w not in prior
 assert int(hashlib.sha256(w.encode()).hexdigest(),16)%10 in {3,4,5}
 p=e['pronunciation'];assert re.fullmatch('/[^/]+/',p) and not any(c.isspace() for c in p)
 assert all(c in IPA_CHARACTERS for c in p[1:-1]),(w,p)
 for f in e['forms']:
  assert re.fullmatch('[a-z]+',f) and f not in prior and f not in owned,(w,f)
  owned.add(f);forms+=1
 n=0
 for m in e['meanings']:
  assert set(m)=={'partOfSpeech','burmese'} and m['partOfSpeech'] in ALLOWED_POS
  assert all(g.strip() and not re.search('[A-Za-z]',g) and MYANMAR_LETTER.search(g) for g in m['burmese'])
  n+=len(m['burmese'])
 assert 1<=n<=3,w;glosses+=n
lex=json.loads((STAGE/'lexical_review.json').read_text(encoding='utf-8'));verified={r['word'] for r in lex if r['status']=='confirmed_dictionary_entry'}
flags=json.loads((STAGE/'flagged_lexical.json').read_text());assert set(flags)<=verified,sorted(set(flags)-verified)
summary={'entries':len(a),'storedForms':forms,'lookupKeys':len(a)+forms,'burmeseMeanings':glosses,'posCounts':dict(Counter(e['meanings'][0]['partOfSpeech'] for e in a)),'structuralErrors':0,'priorCollisions':0,'withinPoolCollisions':0,'unreviewedIPA':0,'flaggedLexicalHeadwords':len(flags),'verifiedLexicalRecords':len(verified&heads),'deferredLexicalCandidates':4,'notes':['Final canonical extension validator must run after root integrates predecessors.','Root must resolve form collisions across the global ten-batch candidate pool.','No 500-entry batch or repository state was changed; root chooses and numbers the final quality-qualified batches.']}
(STAGE/'validation_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary,indent=2))
