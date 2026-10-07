import json, re, base64, zlib, hashlib
from pathlib import Path
from eng_to_ipa.stress import find_stress
from eng_to_ipa.transcribe import get_cmu
from lemminflect import getInflection
import cmudict

D=Path(__file__).resolve().parent
ROOT=D.parents[2]
prior=set(zlib.decompress(base64.b64decode((ROOT/'extension_lookup/used_keys_current.zlib.b64').read_text())).decode().splitlines())
rejected={l.strip() for l in (ROOT/'extension_rejected_headwords.txt').read_text().splitlines() if l.strip() and not l.startswith('#')}
pruned={l.strip() for l in (D/'prune.txt').read_text().splitlines() if l.strip() and not l.startswith('#')}
pool={x['word']:x for x in json.loads((D/'candidate_pool.json').read_text())}
rows=[]
for p in sorted(D.glob('authored_*.psv')):
    for l in p.read_text(encoding='utf-8').splitlines():
        if l and l.split('|')[0] not in pruned:
            rows.append(l.split('|'))
heads={r[0] for r in rows}
assert len(heads)==len(rows)
assert not heads&(prior|rejected)
assert all(int(hashlib.sha256(w.encode()).hexdigest(),16)%10 in {0,1,2} for w in heads)
PHONES=dict(zip('aa ae ah ao aw ay b ch d dh eh er ey f g hh ih iy jh k l m n ng ow oy p r s sh t th uh uw v w y z zh'.split(),'ɑ æ ə ɔ aʊ aɪ b tʃ d ð ɛ ɚ eɪ f ɡ h ɪ i dʒ k l m n ŋ oʊ ɔɪ p r s ʃ t θ ʊ u v w j z ʒ'.split()))
CMU=cmudict.dict()
override={}
if (D/'ipa.psv').exists():
    for l in (D/'ipa.psv').read_text(encoding='utf-8').splitlines():
        if l.strip():
            w,ipa=l.split('|'); override[w]='/'+ipa.strip('/')+'/'
def pronunciation(w):
    if w in override: return override[w], 'manual review'
    orig=' '.join(CMU[w][0]).lower() if w in CMU else get_cmu([w])[0][0]
    if orig.startswith('__IGNORE__'): return '/REVIEW/', 'missing'
    out=''
    for raw,placed in zip(orig.split(),find_stress(orig).split()):
        name=re.sub('[0-9]','',raw)
        ipa=PHONES[name]
        if name=='ah' and raw[-1] in '12': ipa='ʌ'
        if name=='er' and raw[-1] in '12': ipa='ɝ'
        out+=(placed[0] if placed[0] in 'ˈˌ' else '')+ipa
    return '/'+out+'/', 'CMU resource'
posmap={'n':'noun','c':'noun','v':'verb','a':'adjective','r':'adverb'}
irregular={'noblewoman':['noblewomen'],'phoenix':['phoenixes'],'pika':['pikas'],'larynx':['larynges','larynxes'],'rewind':['rewinds','rewound','rewinding'],'dunno':[],'dawg':['dawgs'],'vlog':['vlogs'],'carb':['carbs'],'sissy':['sissies'],'clit':['clits'],'sensei':[],'psych':['psychs','psyched','psyching']}
entries=[]; forms_review=[]; ipa_review=[]; owned=prior|heads|rejected
lexical=[]
for row in rows:
    w,p,*gloss=row
    pos=posmap.get(p,p)
    assert 1<=len(gloss)<=3 and all(not re.search('[a-zA-Z]',g) for g in gloss)
    ipa,source=pronunciation(w)
    suggestions=[]
    if w in irregular: suggestions=irregular[w]
    elif pos=='verb':
        for tag in ['VBZ','VBD','VBN','VBG']: suggestions.extend(getInflection(w,tag=tag) or [])
    elif p=='c': suggestions=list(getInflection(w,tag='NNS') or [])
    forms=[]
    for f in dict.fromkeys(suggestions):
        if f!=w and f not in owned and re.fullmatch('[a-z]+',f):
            forms.append(f); owned.add(f)
    forms_review.append({'word':w,'countNoun':p=='c','proposed':list(dict.fromkeys(suggestions)),'stored':forms,'excluded':[f for f in dict.fromkeys(suggestions) if f not in forms]})
    ipa_review.append({'word':w,'ipa':ipa,'source':source})
    splits=[w[:i]+'+'+w[i:] for i in range(3,len(w)-2) if w[:i] in prior and w[i:] in prior]
    if splits or w not in pool or w in {'newsboy','wristlet','breathalyzer','scrubland'}:
        lexical.append({'word':w,'splits':splits})
    entries.append({'word':w,'pronunciation':ipa,'forms':forms,'meanings':[{'partOfSpeech':pos,'burmese':gloss}]})
for name,obj in [('selected_entries.json',entries),('form_review.json',forms_review),('ipa_review.json',ipa_review),('lexical_pending.json',lexical)]:
    (D/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'entries':len(entries),'forms':sum(len(e['forms']) for e in entries),'missingIPA':[r['word'] for r in ipa_review if r['source']=='missing'],'lexicalReviewCount':len(lexical)},ensure_ascii=False))
