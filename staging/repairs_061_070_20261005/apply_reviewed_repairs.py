"""Apply this dated, explicit editorial plan; never mutate frozen v1 assets."""
import argparse, base64, collections, copy, json, re, sys, zlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
STAGE=Path(__file__).resolve().parent
sys.stdout.reconfigure(encoding='utf-8')

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def dump(path, data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args()
    rejected=read(STAGE/'rejected_headwords.json')
    base=set(zlib.decompress(base64.b64decode((ROOT/'lookup/used_keys_current.zlib.b64').read_text().strip())).decode().splitlines())
    docs={int(p.stem.rsplit('_',1)[1]):read(p) for p in sorted((ROOT/'DictionaryExtensionBatches').glob('dictionary_batch_*.json'))}
    originals=copy.deepcopy(docs)
    if not any(e['word']=='cashout' for e in docs[61]['entries']):
        raise SystemExit('This one-time repair plan requires the pre-repair batches from ff7e738f; use repair_log.json to inspect the completed changes.')
    original_keys=base|{k for d in docs.values() for e in d['entries'] for k in [e['word']]+e['forms']}
    candidates=[]
    for line in (STAGE/'authored_replacements.txt').read_text(encoding='utf-8').splitlines():
        if not line.strip():continue
        parts=line.split('|');assert len(parts) in (4,5),parts
        w,pos,ipa,gloss=parts[:4]
        assert w not in original_keys,w
        assert re.fullmatch('[a-z]+',w),w
        candidates.append({'word':w,'pronunciation':ipa,'forms':parts[4].split(',') if len(parts)==5 else [],'meanings':[{'partOfSpeech':pos,'burmese':gloss.split(';')}]})
    assert len({e['word'] for e in candidates})==len(candidates)
    replacements=[];unused=[];cursor=0
    for batch,groups in sorted(rejected.items(),key=lambda x:int(x[0])):
        number=int(batch);reason_by_word={w:reason for reason,words in groups.items() for w in words}
        for i,e in enumerate(docs[number]['entries']):
            if e['word'] not in reason_by_word:continue
            new=copy.deepcopy(candidates[cursor]);cursor+=1
            docs[number]['entries'][i]=new
            replacements.append({'batch':number,'removed':e['word'],'reason':reason_by_word[e['word']],'replacement':new['word'],'removedEntry':e,'newEntry':new})
        assert len([r for r in replacements if r['batch']==number])==len(reason_by_word)
    unused=[e['word'] for e in candidates[cursor:]]
    entries={e['word']:e for d in docs.values() for e in d['entries']}
    # Independently authored concise meanings; established dictionary senses.
    entries['circularize']['meanings']=[{'partOfSpeech':'verb','burmese':['အကြောင်းကြားစာများဖြန့်ဝေသည်','စစ်တမ်းမေးခွန်းများပေးပို့၍သဘောထားကောက်ယူသည်','စက်ဝိုင်းပုံဖြစ်အောင်လုပ်သည်']}]
    entries['maraud'].update(pronunciation='/məˈrɔd/',meanings=[{'partOfSpeech':'verb','burmese':['လုယက်ဖျက်ဆီးရန်လှည့်လည်သွားလာသည်']}])
    entries['fleer']['meanings']=[{'partOfSpeech':'verb','burmese':['လှောင်ပြောင်မဲ့ရွဲ့သည်']}]
    entries['jean']['meanings']=[{'partOfSpeech':'noun','burmese':['ဂျင်းဘောင်းဘီများချုပ်ရန်သုံးသောခိုင်ခံ့သည့်ချည်ထည်']}]
    # Avoid misleading expanded-abbreviation transcription and stress placement.
    entries['corp']['pronunciation']='/kɔrp/'
    entries['quilting']['pronunciation']='/ˈkwɪltɪŋ/'
    entries['housekeeping']['pronunciation']='/ˈhaʊsˌkipɪŋ/'
    entries['weatherize']['pronunciation']='/ˈwɛðəraɪz/'
    entries['circularize']['pronunciation']='/ˈsɝkjələraɪz/'
    approved={w for line in (STAGE/'approved_count_nouns.txt').read_text(encoding='utf-8').splitlines() if line and not line.startswith('#') for w in line.split()}
    approved.discard('matt') # Selected sense is an ordinary mass/quality noun.
    approved.discard('missis') # Selected conversational sense is singular.
    irregular={
        'bowman':['bowmen'],'woodman':['woodmen'],'saleswoman':['saleswomen'],'landsman':['landsmen'],
        'committeeman':['committeemen'],'frogman':['frogmen'],'steelman':['steelmen'],'lumberman':['lumbermen'],
        'nurseryman':['nurserymen'],'mitochondrion':['mitochondria'],'packman':['packmen'],'dustman':['dustmen'],
        'oarsman':['oarsmen'],'adman':['admen'],'cowman':['cowmen'],'jazzman':['jazzmen'],'seedsman':['seedsmen'],
        'wireman':['wiremen'],'pigman':['pigmen'],'chessman':['chessmen'],'layperson':['laypeople','laypersons'],
        'charwoman':['charwomen'],'schoolchild':['schoolchildren'],'forewoman':['forewomen'],'newswoman':['newswomen'],
        'timberman':['timbermen'],'counterman':['countermen'],'foreperson':['forepeople','forepersons'],
        'backwoodsman':['backwoodsmen'],'batman':['batmen'],'diverticulum':['diverticula'],
        'paramecium':['paramecia'],'paparazzo':['paparazzi'],'gimp':['gimps'],
        'kris':['krises'],'dolly':['dollies'],'potpie':['potpies'],'cahoot':['cahoots'],
        'bialy':['bialys'],'glottis':['glottides'],'nasopharynx':['nasopharynges'],
        'lungfish':[],'hagfish':[],
        'lockman':['lockmen'],'pitchman':['pitchmen'],
    }
    verbs={
        'deplatform':['deplatforms','deplatformed','deplatforming'],
        'shadowban':['shadowbans','shadowbanned','shadowbanning'],
        'prebunk':['prebunks','prebunked','prebunking'],
        'gamify':['gamifies','gamified','gamifying'],
        'photobomb':['photobombs','photobombed','photobombing'],
        'misgender':['misgenders','misgendered','misgendering'],
        'overshare':['overshares','overshared','oversharing'],
        'crowdsource':['crowdsources','crowdsourced','crowdsourcing'],
        'upsell':['upsells','upsold','upselling'],
        'downsell':['downsells','downsold','downselling'],
        'rewild':['rewilds','rewilded','rewilding'],
        'weatherize':['weatherizes','weatherized','weatherizing'],
        'circularize':['circularizes','circularized','circularizing'],
        'terraform':['terraforms','terraformed','terraforming'],
        'declutter':['declutters','decluttered','decluttering'],
        'maraud':['marauds','marauded','marauding'],
        'fleer':['fleers','fleered','fleering'],
    }
    # Reserve every original surviving owner before considering replacement forms.
    owners={k:'frozen v1' for k in base}
    for number,d in docs.items():
        for e in d['entries']:
            k=e['word']
            if k in owners:raise ValueError(('headword collision',k,owners[k]))
            owners[k]=k
    original_by_word={e['word']:e for d in originals.values() for e in d['entries']}
    for w,e in entries.items():
        if w in original_by_word:
            for f in e['forms']:
                if f in owners:raise ValueError(('existing form collision',w,f,owners[f]))
                owners[f]=w
    added=[];excluded=[];noun_review=[]
    for number,d in sorted(docs.items()):
        for e in d['entries']:
            w=e['word']; forms=[]
            for f in e['forms']:
                if f not in owners:owners[f]=w;forms.append(f)
                elif owners.get(f)==w:forms.append(f)
                else:excluded.append({'batch':number,'word':w,'form':f,'owner':owners[f]})
            e['forms']=forms
            suggestions=list(verbs.get(w,[]))
            if w in approved:
                assert any(m['partOfSpeech']=='noun' for m in e['meanings']),w
                if w in irregular: plural=irregular[w]
                elif re.search('[^aeiou]y$',w):plural=[w[:-1]+'ies']
                elif w.endswith(('s','sh','ch','x','z')):plural=[w+'es']
                else:plural=[w+'s']
                suggestions+=plural
                noun_review.append({'batch':number,'word':w,'proposed':plural,'selectedMeanings':e['meanings']})
            for f in dict.fromkeys(suggestions):
                assert re.fullmatch('[a-z]+',f),(w,f)
                if f==w or f in e['forms']:continue
                if f in owners:
                    excluded.append({'batch':number,'word':w,'form':f,'owner':owners[f]});continue
                owners[f]=w;e['forms'].append(f);added.append({'batch':number,'word':w,'form':f})
    changes=[]
    for number,doc in docs.items():
        assert len(doc['entries'])==500
        for old,new in zip(originals[number]['entries'],doc['entries']):
            if old!=new:changes.append({'batch':number,'originalWord':old['word'],'word':new['word'],'before':old,'after':new})
    rejected_set={r['removed'] for r in replacements}
    summary={'replacedHeadwords':len(replacements),'addedForms':len(added),'excludedForms':len(excluded),'changedEntries':len(changes),'unusedCandidates':unused,'formsByBatch':{str(n):sum(len(e['forms']) for e in d['entries']) for n,d in docs.items()}}
    log={'version':1,'reviewDate':'2026-10-05','summary':summary,'replacements':replacements,'addedForms':added,'excludedForms':excluded,'nounPluralReview':noun_review,'changes':changes}
    preview=ROOT/'.local-temp/repairs_061_070_preview'
    preview.mkdir(parents=True,exist_ok=True)
    dump(preview/'repair_preview.json',log)
    for number,doc in docs.items():dump(preview/f'dictionary_batch_{number:03d}.json',doc)
    if args.write:
        for number,doc in docs.items():
            if doc!=originals[number]:dump(ROOT/'DictionaryExtensionBatches'/f'dictionary_batch_{number:03d}.json',doc)
        allow=ROOT/'extension_closed_compound_allowlist.txt'
        lines=allow.read_text(encoding='utf-8').splitlines()
        allow.write_text('\n'.join(line for line in lines if line.strip() not in rejected_set)+'\n',encoding='utf-8')
        rejected_keys=rejected_set|{f for r in replacements for f in r['removedEntry']['forms']}
        (ROOT/'extension_rejected_headwords.txt').write_text('# Editorially rejected extension spellings; see dated repair records.\n# Includes removed headwords and their stored forms.\n# Review and update this record only with new lexical evidence.\n'+'\n'.join(sorted(rejected_keys))+'\n',encoding='utf-8')
        dump(STAGE/'repair_log.json',log)
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
