import base64, zlib, json, re, hashlib, sys
from pathlib import Path
import cmudict
from lemminflect import getInflection
from eng_to_ipa.stress import find_stress
ROOT=Path(__file__).resolve().parents[3]
STAGE=Path(__file__).resolve().parent
prior=set(zlib.decompress(base64.b64decode((ROOT/'extension_lookup/used_keys_current.zlib.b64').read_text())).decode().splitlines())
rejected=set((ROOT/'extension_rejected_headwords.txt').read_text(encoding='utf8').splitlines())
form_overrides=json.loads((STAGE/'form_overrides.json').read_text(encoding='utf8'))if (STAGE/'form_overrides.json').exists()else{}
CMU=cmudict.dict()
PHONES=dict(zip('aa ae ah ao aw ay b ch d dh eh er ey f g hh ih iy jh k l m n ng ow oy p r s sh t th uh uw v w y z zh'.split(),'ɑ æ ə ɔ aʊ aɪ b tʃ d ð ɛ ɚ eɪ f ɡ h ɪ i dʒ k l m n ŋ oʊ ɔɪ p r s ʃ t θ ʊ u v w j z ʒ'.split()))
overrides=json.loads((STAGE/'ipa_overrides.json').read_text(encoding='utf8')) if (STAGE/'ipa_overrides.json').exists() else {}
for p in sorted(STAGE.glob('ipa_*.txt')):
    for line in p.read_text(encoding='utf8').splitlines():
        if not line.strip()or line.startswith('#'):continue
        word,pronunciation=line.split('|');overrides[word]=pronunciation
def ipa(word):
    if word in overrides:return overrides[word]
    if word not in CMU:return None
    raw=' '.join(CMU[word][0]).lower(); marks=find_stress(raw).split(); out=''
    for r,m in zip(raw.split(),marks):
        name=re.sub('[0-9]','',r); symbol=PHONES[name]
        if name=='ah' and r[-1]in'12':symbol='ʌ'
        if name=='er' and r[-1]in'12':symbol='ɝ'
        out+=(m[0]if m[0]in'ˈˌ'else'')+symbol
    return '/'+out+'/'
rows=[]
for p in sorted(STAGE.glob('authored_*.txt')):
    for i,line in enumerate(p.read_text(encoding='utf8').splitlines(),1):
        if not line.strip()or line.startswith('#'):continue
        parts=line.split('|');assert len(parts)>=3,(p,i,line)
        word,code,glosses=parts[:3];pos={'n':'noun','m':'noun','v':'verb','a':'adjective','d':'adverb','p':'pronoun','c':'conjunction','r':'preposition','i':'interjection','t':'determiner','o':'modal'}.get(code,code)
        rows.append((word,code,pos,glosses.split(';'),parts[3]if len(parts)>3 else''))
heads={r[0]for r in rows};assert len(rows)==len(heads),'duplicate'
owned=prior|heads;entries=[];audit=[];missing=[];issues=[]
for word,code,pos,glosses,explicit in rows:
    if word in prior|rejected:issues.append((word,'excluded'))
    if int(hashlib.sha256(word.encode('ascii')).hexdigest(),16)%10 not in (6,7,8):issues.append((word,'partition'))
    suggestions=[]
    if word in form_overrides:suggestions=form_overrides[word]
    elif explicit:suggestions=explicit.split(',')if explicit!='-'else[]
    elif code=='n':suggestions=list(getInflection(word,tag='NNS')or())
    elif code=='v':
        for tag in ['VBZ','VBD','VBN','VBG']:suggestions.extend(getInflection(word,tag=tag)or())
    forms=[]
    for f in dict.fromkeys(suggestions):
        if f!=word and f not in owned and re.fullmatch('[a-z]+',f):forms.append(f);owned.add(f)
    pronunciation=ipa(word)
    if pronunciation is None:missing.append(word);pronunciation='/REVIEW/'
    entries.append(dict(word=word,pronunciation=pronunciation,forms=forms,meanings=[dict(partOfSpeech=pos,burmese=glosses)]))
    audit.append(dict(word=word,partOfSpeech=pos,formPolicy=code,proposed=list(dict.fromkeys(suggestions)),stored=forms,excluded=[f for f in dict.fromkeys(suggestions)if f not in forms],pronunciationResource='manual'if word in overrides else'CMU',ipa=pronunciation))
(STAGE/'preview.json').write_text(json.dumps(entries,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(STAGE/'forms_ipa_review.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
selected=set((STAGE/'selected_words.txt').read_text().split())if (STAGE/'selected_words.txt').exists()else heads
selected_entries=[e for e in entries if e['word']in selected]
(STAGE/'selected_entries.json').write_text(json.dumps(selected_entries,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(count=len(entries),selected=len(selected_entries),missingIPA=[w for w in missing if w in selected],issues=issues,forms=sum(len(e['forms'])for e in selected_entries)),ensure_ascii=False,indent=2))
if len(entries)==1500 and not missing and not issues:
    for i,batch in enumerate([77,78,79]):(STAGE/f'dictionary_batch_{batch:03}.json').write_text(json.dumps(dict(version=1,batch=batch,entries=entries[i*500:(i+1)*500]),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
