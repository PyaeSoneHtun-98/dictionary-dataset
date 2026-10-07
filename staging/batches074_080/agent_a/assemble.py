import json,re,base64,zlib,hashlib
from pathlib import Path
from collections import defaultdict
from lemminflect import getInflection
from eng_to_ipa.stress import find_stress
from eng_to_ipa.transcribe import get_cmu
import cmudict

D=Path(__file__).resolve().parent
ROOT=D.parents[2]
prior=set(zlib.decompress(base64.b64decode((ROOT/'extension_lookup/used_keys_current.zlib.b64').read_text())).decode().splitlines())
rejected={l.strip() for l in (ROOT/'extension_rejected_headwords.txt').read_text().splitlines() if l.strip() and not l.startswith('#')}
pruned={l.strip() for l in (D/'prune.txt').read_text().splitlines() if l.strip() and not l.startswith('#')}
pool_path=D/'candidate_pool.json'
pool_raw=pool_path.read_bytes() if pool_path.exists() else zlib.decompress((D/'candidate_pool.json.zlib').read_bytes())
pool={x['word']:x for x in json.loads(pool_raw)}
rows=defaultdict(list)
for path in sorted(D.glob('authored_*.psv')):
    for line in path.read_text(encoding='utf-8').splitlines():
        if line:
            w,p,*gloss=line.split('|')
            if w not in pruned: rows[w].append((p,gloss))
heads=set(rows)
assert not heads&(prior|rejected),heads&(prior|rejected)
assert all(re.fullmatch('[a-z]+',w) and int(hashlib.sha256(w.encode()).hexdigest(),16)%10 in {0,1,2} for w in heads)
PHONES=dict(zip('aa ae ah ao aw ay b ch d dh eh er ey f g hh ih iy jh k l m n ng ow oy p r s sh t th uh uw v w y z zh'.split(),'ɑ æ ə ɔ aʊ aɪ b tʃ d ð ɛ ɚ eɪ f ɡ h ɪ i dʒ k l m n ŋ oʊ ɔɪ p r s ʃ t θ ʊ u v w j z ʒ'.split()))
# Restore the explicit phone mapping without relying on positional list edits.
PHONES.update({'uh':'ʊ','uw':'u','v':'v','w':'w','y':'j','z':'z','zh':'ʒ'})
CMU=cmudict.dict()
override={}
for ipafile in sorted(D.glob('ipa*.psv')):
    for l in ipafile.read_text(encoding='utf-8').splitlines():
        if l.strip():
            w,ipa=l.split('|');override[w]='/'+ipa.strip('/')+'/'
def pronunciation(w):
    if w in override:return override[w],'manual review'
    raw=' '.join(CMU[w][0]).lower() if w in CMU else get_cmu([w])[0][0]
    if raw.startswith('__IGNORE__'):return '/REVIEW/','missing'
    result=''
    for token,placed in zip(raw.split(),find_stress(raw).split()):
        phone=re.sub('[0-9]','',token)
        ipa=PHONES[phone]
        if phone=='ah' and token[-1] in '12':ipa='ʌ'
        if phone=='er' and token[-1] in '12':ipa='ɝ'
        result+=(placed[0] if placed[0] in 'ˈˌ' else '')+ipa
    return '/'+result+'/','CMU resource'
posmap={'n':'noun','c':'noun','v':'verb','a':'adjective','r':'adverb'}
irregular={'cut':['cuts','cutting'],'hit':['hits','hitting'],'rip':['rips','ripped','ripping'],'pat':['pats','patted','patting'],'vet':['vets','vetted','vetting'],'bum':['bums','bummed','bumming'],'kid':['kids','kidded','kidding'],'wed':['weds','wed','wedded','wedding'],'overlie':['overlies','overlay','overlain','overlying'],'handwrite':['handwrites','handwrote','handwritten','handwriting'],'overbear':['overbears','overbore','overborne','overbearing'],'outdraw':['outdraws','outdrew','outdrawn','outdrawing'],'spellbind':['spellbinds','spellbound','spellbinding'],'sightread':['sightreads','sightreading'],'ewe':['ewes'],'mujahid':['mujahidin','mujahideen'],'jinni':['jinn'],'erratum':['errata'],'goatherd':['goatherds'],'likeability':[]}
owned=prior|heads|rejected
entries=[];forms_review=[];ipa_review=[];lexical=[]
for w,blocks in rows.items():
    meanings=[];suggestions=[]
    for p,gloss in blocks:
        pos=posmap.get(p,p)
        assert all(g and not re.search('[a-zA-Z\u4e00-\u9fff]',g) for g in gloss),w
        same=next((m for m in meanings if m['partOfSpeech']==pos),None)
        if same:same['burmese'].extend(gloss)
        else:meanings.append({'partOfSpeech':pos,'burmese':gloss})
        if p=='v':
            for tag in ['VBZ','VBD','VBN','VBG']:suggestions.extend(getInflection(w,tag=tag) or [])
        elif p=='c':suggestions.extend(getInflection(w,tag='NNS') or [])
    assert sum(len(m['burmese']) for m in meanings)<=3,w
    if w in irregular:suggestions=irregular[w]
    if w in {'glassworks','lazybones','bowerbird'}:suggestions=[]
    if w=='greenlight':suggestions=['greenlights','greenlit','greenlighted','greenlighting']
    forms=[]
    for form in dict.fromkeys(suggestions):
        if form!=w and form not in owned and re.fullmatch('[a-z]+',form):forms.append(form);owned.add(form)
    forms_review.append({'word':w,'proposed':list(dict.fromkeys(suggestions)),'stored':forms,'excluded':[f for f in dict.fromkeys(suggestions) if f not in forms]})
    ipa,source=pronunciation(w)
    ipa_review.append({'word':w,'ipa':ipa,'source':source})
    splits=[w[:i]+'+'+w[i:] for i in range(3,len(w)-2) if w[:i] in prior and w[i:] in prior]
    if splits or w not in pool or pool[w]['source']!='WordNet':lexical.append({'word':w,'splits':splits,'source':pool.get(w,{}).get('source','additional author selection')})
    entries.append({'word':w,'pronunciation':ipa,'forms':forms,'meanings':meanings})
for name,obj in [('selected_entries.json',entries),('form_review.json',forms_review),('ipa_review.json',ipa_review),('lexical_pending.json',lexical)]:
    (D/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'entries':len(entries),'forms':sum(len(e['forms']) for e in entries),'missingIPA':[r['word'] for r in ipa_review if r['source']=='missing'],'lexicalReviewCount':len(lexical)}))
