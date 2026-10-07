"""Assemble independently authored meanings and reviewed candidate morphology."""
import base64, collections, hashlib, json, re, zlib
from pathlib import Path
import cmudict
from eng_to_ipa.stress import find_stress
from lemminflect import getInflection

ROOT=Path(__file__).resolve().parents[3]
STAGE=Path(__file__).resolve().parent
prior=set(zlib.decompress(base64.b64decode((ROOT/'extension_lookup/used_keys_current.zlib.b64').read_bytes())).decode().splitlines())
prior.update(w.strip() for w in (ROOT/'extension_rejected_headwords.txt').read_text().splitlines() if w.strip() and not w.startswith('#'))
excluded=set((STAGE/'editorial_exclusions.txt').read_text(encoding='utf-8').splitlines())
fixes={'vig\u200borish':'vigorish','explo\u200bitatory':'exploitatory','contemplativ\u200beness':'contemplativeness'}
tags={'N':'noun','n':'noun','a':'adjective','v':'verb','adv':'adverb'}
authored={}; rejects=[]; duplicates=[]
for p in sorted(STAGE.glob('authored_*.txt')):
 for i,l in enumerate(p.read_text(encoding='utf-8').splitlines(),1):
  if not l.strip():continue
  w,t,*g=l.split('|');w=fixes.get(w,w)
  reason=None
  if w in excluded:reason='manual editorial exclusion: low subtitle usefulness or redundant variant'
  elif w in prior:reason='excluded prior namespace'
  elif not re.fullmatch('[a-z]+',w):reason='invalid orthography'
  elif int(hashlib.sha256(w.encode()).hexdigest(),16)%10 not in {3,4,5}:reason='outside assigned namespace'
  if reason:rejects.append({'word':w,'reason':reason,'source':p.name,'line':i});continue
  if w in authored:duplicates.append({'word':w,'source':p.name,'line':i});continue
  authored[w]=(t,g,p.name,i)
CMU=cmudict.dict()
reviewed_derivatives=json.loads((STAGE/'reviewed_derivative_ipa.json').read_text(encoding='utf-8')) if (STAGE/'reviewed_derivative_ipa.json').exists() else {}
PHONES=dict(zip('aa ae ah ao aw ay b ch d dh eh er ey f g hh ih iy jh k l m n ng ow oy p r s sh t th uh uw v w y z zh'.split(),'ɑ æ ə ɔ aʊ aɪ b tʃ d ð ɛ ɚ eɪ f ɡ h ɪ i dʒ k l m n ŋ oʊ ɔɪ p r s ʃ t θ ʊ u v w j z ʒ'.split()))
ipa_overrides=json.loads((STAGE/'pronunciation_overrides.json').read_text(encoding='utf-8')) if (STAGE/'pronunciation_overrides.json').exists() else {}
for line in (STAGE/'manual_ipa.txt').read_text(encoding='utf-8').splitlines():
 w,ipa=line.split('|');ipa_overrides[w]=ipa
form_overrides={'millipede':['millipedes'],'litchi':['litchis'],'kohlrabi':['kohlrabis'],'garbanzo':['garbanzos'],'waybill':['waybills'],'passersby':[],'cryptanalyst':['cryptanalysts']}
form_overrides.update({'clostridium':['clostridia'],'peshmerga':[],'candelabrum':['candelabra','candelabrums'],'columbarium':['columbaria','columbariums'],'effluvium':['effluvia'],'flatfoot':['flatfeet','flatfoots'],'dybbuk':['dybbuks','dybbukim'],'euchre':[],'fiddly':['fiddlier','fiddliest'],'giggly':['gigglier','giggliest']})
form_overrides.update({'ass':['asses'],'fib':['fibs','fibbed','fibbing'],'bob':['bobs','bobbed','bobbing'],'tsk':[],'specs':[],'togs':[],'victuals':[],'sweetbreads':[],'bedclothes':[],'spareribs':[],'tinsnips':[],'macronutrient':[],'conman':['conmen'],'forex':[],'crypto':[],'resupply':['resupplies','resupplied','resupplying'],'misspend':['misspends','misspent','misspending'],'unclothe':['unclothes','unclothed','unclothing'],'woodlouse':['woodlice']})
ipa_review=[];forms_review=[];entries=[];missing=[];heads=set(authored);owned=prior|heads
for w,(t,g,source,line) in authored.items():
 if w in ipa_overrides:ipa=ipa_overrides[w]; origin='manual GA override'
 elif w in reviewed_derivatives:ipa=reviewed_derivatives[w];origin='manually reviewed derivative of existing GA headword'
 elif w in CMU:
  raw=' '.join(CMU[w][0]).lower(); marked=find_stress(raw).split();out=''
  for r,m in zip(raw.split(),marked):
   phone=re.sub('[0-9]','',r);sym=PHONES[phone]
   if phone=='ah' and r[-1:] in '12':sym='ʌ'
   if phone=='er' and r[-1:] in '12':sym='ɝ'
   out+=(m[0] if m[0] in 'ˈˌ' else '')+sym
  ipa='/'+out+'/';origin='CMU first GA variant; stress placed by eng_to_ipa'
 else:ipa='/REVIEW/';origin='requires manual GA IPA';missing.append(w)
 proposals=[]
 if t=='v':
  for tag in ['VBZ','VBD','VBN','VBG']:proposals.extend(getInflection(w,tag=tag) or [])
 elif t=='N':proposals.extend(getInflection(w,tag='NNS') or [])
 if w in form_overrides:proposals=form_overrides[w]
 forms=[];omitted=[]
 for f in dict.fromkeys(proposals):
  if f!=w and re.fullmatch('[a-z]+',f) and f not in owned:forms.append(f);owned.add(f)
  else:omitted.append(f)
 pos=tags.get(t,t)
 assert 1<=len(g)<=3 and all(g) and all(not re.search('[A-Za-z]',v) for v in g),(w,g)
 entries.append({'word':w,'pronunciation':ipa,'forms':forms,'meanings':[{'partOfSpeech':pos,'burmese':g}]})
 ipa_review.append({'word':w,'pronunciation':ipa,'origin':origin,'cmuVariants':CMU.get(w,[])})
 if proposals:forms_review.append({'word':w,'proposed':list(dict.fromkeys(proposals)),'stored':forms,'omitted':omitted,'review':'Count nouns explicitly selected by authored N tag; verbs reviewed by authored v tag; global root collision filtering still required.'})
(STAGE/'selected_entries.json').write_text(json.dumps(entries,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(STAGE/'ipa_review.json').write_text(json.dumps(ipa_review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(STAGE/'form_review.json').write_text(json.dumps(forms_review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(STAGE/'editorial_review.json').write_text(json.dumps({'rejected':rejects,'duplicateDraftRowsIgnored':duplicates,'summary':'Authored sources are exploratory. Retained entries selected for modern subtitle, novel, news and documentary usefulness. Narrow technical, archaic and weak derivatives excluded. No final batches or frozen assets written.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
allow={l.strip() for l in (ROOT/'extension_closed_compound_allowlist.txt').read_text().splitlines() if l.strip() and not l.startswith('#')}
flags={}
for w in heads:
 if w in allow:continue
 splits=[w[:i]+'+'+w[i:] for i in range(3,len(w)-2) if w[:i] in prior and w[i:] in prior]
 if splits:flags[w]=splits
(STAGE/'flagged_lexical.json').write_text(json.dumps(flags,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'selected':len(entries),'forms':sum(len(e['forms']) for e in entries),'missingIPA':missing,'flaggedLexicalCount':len(flags)},ensure_ascii=False,indent=2))
