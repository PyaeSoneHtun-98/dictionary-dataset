"""Assemble manually written meanings and General American IPA; audit forms separately."""
import sys,json,re
from pathlib import Path
from lemminflect import getInflection
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from validate_extension_batch import load_prior_keys
batch=int(sys.argv[1]);stage=ROOT/'staging'/f'batch{batch:03d}'
prior=load_prior_keys(ROOT/'lookup/used_keys_current.zlib.b64',ROOT/'DictionaryExtensionBatches',batch)
rows=[]
for path in sorted(stage.glob('authored_*.txt')):
 for line in path.read_text(encoding='utf8').splitlines():
  if line.strip():
   parts=line.split('|');assert len(parts) in (4,5),(path,line)
   rows.append(parts)
heads={r[0] for r in rows};assert len(heads)==len(rows),'duplicate headwords'
collisions=sorted(heads&prior);assert not collisions,collisions
owned=prior|heads;entries=[];review=[]
for row in rows:
 word,pos,ipa,glosses=row[:4];spec=row[4] if len(row)==5 else ''
 assert re.fullmatch('[a-z]+',word),word
 assert ipa.startswith('/') and ipa.endswith('/') and not any(c.isspace() for c in ipa),word
 meanings=[{'partOfSpeech':pos,'burmese':glosses.split(';')}]
 suggestions=[]
 if spec=='+': suggestions=list(getInflection(word,tag='NNS') or ())
 elif spec: suggestions=spec.split(',')
 elif pos=='verb':
  for tag in ['VBZ','VBD','VBN','VBG']:suggestions.extend(getInflection(word,tag=tag) or ())
 forms=[]
 for form in dict.fromkeys(suggestions):
  if form!=word and form not in owned:
   assert re.fullmatch('[a-z]+',form),(word,form)
   forms.append(form);owned.add(form)
 if suggestions:review.append({'word':word,'suggested':list(dict.fromkeys(suggestions)),'stored':forms,'excluded':[f for f in dict.fromkeys(suggestions) if f not in forms]})
 entries.append({'word':word,'pronunciation':ipa,'forms':forms,'meanings':meanings})
entries.sort(key=lambda e:e['word'])
doc={'version':1,'batch':batch,'entries':entries}
(stage/'preview.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(stage/'forms_review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'batch':batch,'entries':len(entries),'forms':sum(len(e['forms']) for e in entries),'glosses':sum(len(m['burmese']) for e in entries for m in e['meanings'])}))
if len(entries)==500:
 (ROOT/'DictionaryExtensionBatches'/f'dictionary_batch_{batch:03d}.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
