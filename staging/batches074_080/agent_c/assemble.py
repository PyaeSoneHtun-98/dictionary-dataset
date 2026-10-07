import json,base64,zlib,hashlib,re,sys
from pathlib import Path
P=Path(__file__).resolve().parent
ROOT=P.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
def suspicious_closed_compound_splits(w,keys):
 return [w[:i]+'+'+w[i:]for i in range(3,len(w)-2)if w[:i]in keys and w[i:]in keys]
prior=set(zlib.decompress(base64.b64decode((ROOT/'extension_lookup/used_keys_current.zlib.b64').read_text())).decode().splitlines())
rejected=set((ROOT/'extension_rejected_headwords.txt').read_text(encoding='utf8').splitlines())|{'kafkaesque','fogey','letch','equipage'}
entries=[];notes=[]
pos={'n':'noun','m':'noun','v':'verb','a':'adjective','d':'adverb','i':'interjection'}
for p in sorted(P.glob('authored_*.txt')):
 for line in p.read_text(encoding='utf8').splitlines():
  if not line.strip() or line.startswith('#'):continue
  w,c,g,ipa,f=line.split('|')
  entries.append({'word':w,'pronunciation':ipa,'forms':f.split(',')if f!='-'else[],'meanings':[{'partOfSpeech':pos[c],'burmese':g.split(';')}]})
  notes.append({'word':w,'authoredSource':p.name,'ipa':'independently authored and reviewed GA IPA','formsProposed':f.split(',')if f!='-'else[]})
entries+=json.loads((P/'reviewed_reserves.json').read_text(encoding='utf8'))
issues=[];selected=[]
for e in entries:
 w=e['word']
 reason=None
 if w in prior:reason='current lookup key'
 elif w in rejected:reason='prior explicit rejection'
 elif int(hashlib.sha256(w.encode()).hexdigest(),16)%10 not in {6,7,8}:reason='outside exclusive namespace'
 elif w.replace('our','or').replace('ll','l')in prior and ('our'in w or'll'in w):reason='covered American spelling variant'
 if reason:issues.append({'word':w,'reason':reason})
 else:selected.append(e)
heads={e['word']for e in selected};assert len(heads)==len(selected),'duplicate head'
owned=prior|heads;collisions=[]
for e in selected:
 kept=[]
 for f in dict.fromkeys(e['forms']):
  if f in owned:collisions.append({'word':e['word'],'form':f,'reason':'head/form already owned'})
  else:kept.append(f);owned.add(f)
 e['forms']=kept
flags=[]
for e in selected:
 w=e['word'];s=suspicious_closed_compound_splits(w,prior|heads)
 if s:flags.append({'word':w,'splits':s})
errors=[]
allowed=set('abcdefghijklmnopqrstuvwxyzæðŋɑɒɔəɚɛɝɡɪɹʃʊʌʒʤʧˈˌːˑ.θɾɫɐʔ̩̯̃͡')
for e in selected:
 p=e['pronunciation'];g=[g for m in e['meanings']for g in m['burmese']]
 if not p.startswith('/')or not p.endswith('/')or any(c not in allowed for c in p[1:-1]):errors.append({'word':e['word'],'reason':'IPA characters or spacing','ipa':p})
 if not 1<=len(g)<=3 or any(re.search('[A-Za-z]',x)or not re.search('[\u1000-\u109f]',x)for x in g):errors.append({'word':e['word'],'reason':'gloss validation'})
def write(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
write('selected_entries.json',selected);write('draft_editorial_exclusions.json',issues);write('forms_review.json',{'authored':notes,'collisionsExcluded':collisions});write('split_flags.json',flags)
write('validation_summary.json',{'entries':len(selected),'forms':sum(len(e['forms'])for e in selected),'baselineKeys':len(prior),'excludedDrafts':issues,'errors':errors,'compoundFlags':len(flags)})
print(json.dumps({'entries':len(selected),'forms':sum(len(e['forms'])for e in selected),'errors':errors,'excluded':issues,'flags':len(flags)},ensure_ascii=False))
