"""Apply recorded editorial decisions and package exactly seven extension batches."""
import base64,copy,hashlib,json,re,sys,zlib
from pathlib import Path
from wordfreq import zipf_frequency
P=Path(__file__).resolve().parent
R=P.parents[1]
sys.stdout.reconfigure(encoding='utf-8')
def read(f):return json.loads((P/f).read_text(encoding='utf-8'))
def write(f,v):(P/f).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
manifest=json.loads((R/'dictionary_extension_manifest.json').read_text(encoding='utf-8'))
assert manifest['latestBatch']==73 and manifest['nextBatch']==74, 'Baseline changed: review ownership before rerunning.'
prior=set(zlib.decompress(base64.b64decode((R/'extension_lookup/used_keys_current.zlib.b64').read_text())).decode().splitlines())
decisions=read('editorial_overrides.json')
evidence=read('draft_lexical_evidence.json')
drafts=read('all_draft_entries.json')
heads={e['word'] for e in drafts}
assert len(heads)==len(drafts)
rejected=[];accepted=[]
for d in drafts:
    if d['word'] in decisions['rejections']:
        rejected.append({'entry':d,'reason':decisions['rejections'][d['word']]})
        continue
    e=copy.deepcopy(d);e.update(decisions['changes'].get(e['word'],{}))
    accepted.append(e)
# Remove only independently reviewed low-value surplus; keep the retained order frequency-first.
surplus_low_priority=set('jejunity palatalized isochronous stative splenetic orbicular vulturine pharisaic fewness autarkic scansion wardership itineration solacement shielder faunal tendinous cotenant inspiriting briefless exceptionable semirigid prepossess homiletics'.split())
accepted.sort(key=lambda e:(e['word'] in surplus_low_priority, -zipf_frequency(e['word'],'en'), e['word']))
assert len(accepted)>=3500, f'Only {len(accepted)} candidates qualify; do not pad.'
selected=accepted[:3500];surplus=accepted[3500:]
new_heads={e['word'] for e in selected}
owners={w:w for w in new_heads};removed=[]
for e in selected:
    forms=[]
    for form in dict.fromkeys(e['forms']):
        if form in prior or form in owners or not re.fullmatch('[a-z]+',form):
            removed.append({'word':e['word'],'form':form,'reason':'Prior owner, reserved canonical headword, or new form owner','owner':owners.get(form,'prior corpus')})
        else:owners[form]=e['word'];forms.append(form)
    e['forms']=forms
    assert e['word'] not in prior and re.fullmatch('[a-z]+',e['word']),e['word']
    assert sum(len(m['burmese']) for m in e['meanings'])<=3,e['word']
    assert 'REVIEW' not in e['pronunciation'],e['word']
keys=prior|set(owners)
flags={e['word']:[e['word'][:i]+'+'+e['word'][i:] for i in range(3,len(e['word'])-2) if e['word'][:i] in keys and e['word'][i:] in keys] for e in selected}
pending=[w for w,s in flags.items() if s and w not in evidence]
assert not pending, f'Publisher verification missing: {pending}'
allow=(R/'extension_closed_compound_allowlist.txt').read_text(encoding='utf-8').rstrip()
existing={l.strip() for l in allow.splitlines() if l.strip() and not l.startswith('#')}
additions=sorted(w for w,s in flags.items() if s and w not in existing)
(P/'reviewed_closed_compound_allowlist.txt').write_text(allow+'\n\n# Batches 074-080: current publisher records in staging/batches074_080/published_lexical_evidence.json\n'+'\n'.join(additions)+'\n',encoding='utf-8')
(P/'validated_batches').mkdir(exist_ok=True)
stats=[]
for number in range(74,81):
    part=selected[(number-74)*500:(number-73)*500]
    runtime=[{k:v for k,v in e.items() if k!='author'} for e in part]
    write(f'validated_batches/dictionary_batch_{number:03d}.json',{'version':1,'batch':number,'entries':runtime})
    stats.append({'batch':number,'headwords':500,'forms':sum(len(e['forms']) for e in part),'meanings':sum(len(m['burmese']) for e in part for m in e['meanings'])})
write('selected_entries.json',selected)
write('reserves.json',[{'entry':e,'reason':'Individually reviewed candidate surplus below publication priority'} for e in surplus]+rejected)
write('final_form_review.json',removed)
write('published_lexical_evidence.json',{w:rs for w,rs in evidence.items() if w in new_heads})
write('publication_summary.json',{'baselineCommit':'f19387bdfb7153bd4022de29a0278dd5e8431a75','baselineLookupKeys':len(prior),'drafts':len(drafts),'editorialRejections':len(rejected),'unpublishedSurplus':len(surplus),'headwords':len(selected),'storedForms':sum(len(e['forms']) for e in selected),'lookupKeysAdded':len(owners),'meanings':sum(len(m['burmese']) for e in selected for m in e['meanings']),'removedForms':len(removed),'verifiedAllowlistAdditions':len(additions),'batches':stats})
print(json.dumps(read('publication_summary.json'),indent=2))
