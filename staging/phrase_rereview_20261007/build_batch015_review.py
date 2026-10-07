import json
import copy
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'scripts'))
from phrase_common import normalize_key
from phrase_extension_common import base_dataset, validate_entries
path = ROOT / 'PhraseExtensionBatches/phrase_batch_015.json'
data = json.loads(path.read_text(encoding='utf-8'))
entries = {e['phrase']: e for e in data['entries']}
findings = {}

def revise(phrase, reason, *, burmese=None, forms=None, add_forms=None, sources=(), replacement=None, category='meaning'):
    if phrase not in findings:
        findings[phrase] = {'entry_number': list(entries).index(phrase)+1, 'phrase': phrase, 'action': 'replace', 'categories': [], 'reasons': [], 'source_urls': [], 'original': copy.deepcopy(entries[phrase]), 'replacement': copy.deepcopy(entries[phrase])}
    f = findings[phrase]
    if category not in f['categories']: f['categories'].append(category)
    f['reasons'].append(reason)
    for source in sources:
        if source not in f['source_urls']: f['source_urls'].append(source)
    e = f['replacement']
    if replacement is not None: f['replacement'] = copy.deepcopy(replacement); e = f['replacement']
    if burmese is not None: e['burmese'] = burmese
    if forms is not None: e['forms'] = forms
    if add_forms:
        for form in add_forms:
            if form != e['phrase'] and form not in e['forms']: e['forms'].append(form)

revise('rough justice', 'The current gloss covers rough summary punishment only. The expression also describes harsh or unfair treatment/outcomes without any legal ruling.', burmese=['မမျှတဘဲ ပြင်းထန်သည့် ဆက်ဆံမှု သို့မဟုတ် အကျိုးဆက်', 'အသေးစိတ်မစစ်ဆေးဘဲ ကြမ်းကြမ်းတမ်းတမ်း ဆုံးဖြတ်အရေးယူခြင်း'], sources=['https://dictionary.cambridge.org/us/dictionary/english/rough-justice-luck'])
revise('rough ride', 'Add the common sense of receiving sustained criticism or harsh treatment; a merely difficult experience can conceal the interpersonal sense.', burmese=['ခက်ခဲပင်ပန်းသည့် အတွေ့အကြုံ', 'ပြင်းပြင်းထန်ထန် ဝေဖန်၊ ဆက်ဆံခံရမှု'], sources=['https://dictionary.cambridge.org/us/dictionary/english/rough-ride'])
revise('soft touch', 'The countable person sense has the useful plural soft touches, currently absent.', add_forms=['soft touches'], category='forms')
revise('kick around', 'The harsh-treatment sense is common in dialogue and absent. Retain the two selected senses and use the third available slot.', burmese=['အကြံကို ဆွေးနွေးစဉ်းစားသည်', 'ဟိုဟိုဒီဒီ လျှောက်နေသည်', 'မညှာမတာ ဆက်ဆံသည်'], sources=['https://www.collinsdictionary.com/dictionary/english/kick-around'])
revise('hot on the heels of', 'This wording commonly describes one event following almost immediately after another, not just physical pursuit.', burmese=['နောက်က အနီးကပ် လိုက်လာသော', 'တစ်ခုခုဖြစ်ပြီး မကြာမီ ဆက်ဖြစ်လာသော'], sources=['https://dictionary.cambridge.org/us/dictionary/english/hot-on-heels'])
revise('chicken-and-egg problem', 'The current origin-order gloss omits the very common circular-dependency dilemma: each necessary step requires the other to happen first.', burmese=['ဘယ်အရာက အရင်စဖြစ်သလဲ ဆုံးဖြတ်ရခက်သည့်ကိစ္စ', 'တစ်ခုဖြစ်ဖို့ နောက်တစ်ခုက အရင်ဖြစ်ရမည်ဆိုပြီး အပြန်အလှန် ပိတ်မိနေသည့်ပြဿနာ'], sources=['https://www.collinsdictionary.com/dictionary/english/chicken-and-egg'])
revise('latch on', 'The literal attachment gloss is unduly forceful. Add the established infant-feeding sense; keep understanding distinct from the interest/opportunity sense selected under latch onto.', burmese=['တင်းတင်း ဆုပ်ကိုင်တွယ်ကပ်သည်', 'သဘောပေါက်သွားသည်', 'ကလေးက နို့သီးခေါင်းကို ကောင်းစွာငုံပြီး နို့စို့သည်'], sources=['https://dictionary.cambridge.org/us/dictionary/english/latch-on', 'https://www.collinsdictionary.com/dictionary/english/latch-on'])
revise('latch onto', 'Latch on to is the established spaced spelling alternative and belongs under the same owner rather than becoming another canonical entry.', add_forms=['latch on to', 'latches on to', 'latched on to', 'latching on to'], sources=['https://dictionary.cambridge.org/dictionary/english/latch'], category='forms')
revise("rat's nest", 'The regular plural retains the singular possessive rat\'s: rat\'s nests. The existing rats\' nests is a different, also grammatical possessive surface and need not be removed.', add_forms=["rat's nests"], sources=['https://www.collinsdictionary.com/dictionary/english/rats-nest'], category='forms')
revise('break your neck', 'The physical sense means suffering a broken neck, not necessarily deliberately causing one. Make the Burmese agency neutral.', burmese=['လည်ပင်းကျိုးသည်', 'အလွန်ကြိုးပမ်းအားထုတ်သည်'])
revise('bare your teeth', 'The literal teeth-baring sense is useful in animal/action scenes and missing from the metaphor-only gloss.', burmese=['သွားဖြဲပြသည်', 'ရန်လိုသည့်သဘော ပြသည်'])
revise('catch your death', 'This idiom is an emphatic warning about catching a very bad cold. Ordinary catching a cold is too weak.', burmese=['အအေးမိပြီး အပြင်းအထန် နေမကောင်းဖြစ်သည်'], sources=['https://dictionary.cambridge.org/dictionary/english/catch-death-of-cold'])
revise('polish up', 'Add the ordinary literal polishing sense alongside improving knowledge or skill.', burmese=['ပွတ်တိုက်၍ တောက်ပြောင်အောင်လုပ်သည်', 'ပိုကောင်းအောင် ပြုပြင်လေ့ကျင့်သည်'])
revise('without reservation', 'The idiomatic plural without reservations is a real useful surface variant, with the same meaning.', add_forms=['without reservations'], category='forms')
revise('come out in the wash', 'This is an inflecting verb idiom, not a frozen uninflected expression. Current forms=[] misses common came/comes/coming surfaces.', add_forms=['comes out in the wash', 'came out in the wash', 'coming out in the wash'], sources=['https://www.collinsdictionary.com/us/dictionary/english/come-out-in-the-wash'], category='forms')
revise('come out smelling of roses', 'The common American like roses surface and come up variants belong to this owner. Every proposed surface stays within five tokens; smelling like a rose is six tokens and is excluded.', add_forms=['come out smelling like roses', 'comes out smelling like roses', 'came out smelling like roses', 'coming out smelling like roses','come up smelling of roses','comes up smelling of roses','came up smelling of roses','coming up smelling of roses','come up smelling like roses','comes up smelling like roses','came up smelling like roses','coming up smelling like roses'], sources=['https://dictionary.cambridge.org/dictionary/english/come-up-out-smelling-of-roses','https://dictionary.cambridge.org/dictionary/english/come-up-out-smelling-like-roses'], category='forms')
revise("within a hair's breadth", 'The phrase means extremely close to something, including danger or success; the present gloss implies narrowly missing an outcome in all contexts.', burmese=['အလွန်နီးကပ်သည့် အကွာအဝေးမှာ', 'နည်းနည်းလေးသာ လိုတော့သည့်အခြေအနေမှာ'])
revise('cut the apron strings', 'The cutting can be done by the child or the parent. The current gloss assigns agency only to the child.', burmese=['မိဘနှင့် သားသမီးကြား အလွန်အကျွံ မှီခိုမှုကို ဖြတ်တောက်သည်'])
revise('do a number on', 'The object can be a body part, property, a plan, or a person. သူတစ်ပါး unnecessarily restricts it to another person.', burmese=['ထိခိုက်ပျက်စီး၊ ဒုက္ခရောက်စေသည်'])
revise('draw blood', 'Add the very common medical sense of taking a blood sample. Also make the injury sense explicit about causing bleeding rather than having been injured.', burmese=['သွေးနမူနာ ယူသည်', 'သွေးထွက်အောင် လုပ်သည်', 'အငြင်းအခုံတွင် တစ်ဖက်သားကို ထိခိုက်စေသည်'])
revise('roll in', 'Add the common informal arrival sense, often late or casually, alongside large-quantity arrivals.', burmese=['အများအပြား ဝင်လာသည်', 'အေးအေးဆေးဆေး သို့မဟုတ် နောက်ကျမှ ရောက်လာသည်'], sources=['https://dictionary.cambridge.org/us/dictionary/english/roll-in'])
revise('round up', 'Police/military roundup means arresting or capturing a group, which is not communicated by simply gathering people. Also clarify numerical rounding is to a whole/simple number.', burmese=['လူ၊ တိရစ္ဆာန် သို့မဟုတ် ပစ္စည်းများကို လိုက်စုသည်', 'လူတစ်စုကို လိုက်လံဖမ်းဆီးသည်', 'ကိန်းကို အနီးဆုံး ပိုကြီးသည့် အလုံးကိန်း သို့မဟုတ် အကြမ်းဖျဉ်းကိန်းအဖြစ် ပြောင်းသည်'], sources=['https://dictionary.cambridge.org/dictionary/english/round-up', 'https://www.collinsdictionary.com/english-language-learning/round-up'])
revise('round off', 'Rounding is to the nearest whole/simple number; nearest number alone is underspecified.', burmese=['အဆုံးသတ်ကို လှလှပပ ပြီးစီးစေသည်', 'ကိန်းကို အနီးဆုံး အလုံးကိန်း သို့မဟုတ် အကြမ်းဖျဉ်းကိန်းအဖြစ် ပြောင်းသည်'])
revise('fall on your feet', 'A fortunate successful outcome after difficulty need not be escape from that difficulty. Replace the overly narrow escape gloss.', burmese=['အခက်အခဲကြားမှ ကံကောင်းစွာ အဆင်ပြေသွားသည်'])
revise('fly the coop', 'The idiom covers leaving secretly or escaping; it does not require prior physical confinement.', burmese=['တိတ်တဆိတ် ထွက်ပြေးထွက်ခွာသည်'])
revise('follow your nose', 'စိတ်အာရုံ is vague here. The second idiomatic sense is trusting instinct/intuition in deciding what to do.', burmese=['ရှေ့တည့်တည့် ဆက်သွားသည်', 'ကိုယ့်ပင်ကိုအသိစိတ်ကို အားကိုးပြီး လုပ်သည်'], sources=['https://dictionary.cambridge.org/us/dictionary/english/follow-nose'])
revise('get a raw deal', 'Correct the unnatural အဆက်ဆံခံရ construction while preserving the unfair-treatment meaning.', burmese=['မတရားသဖြင့် ဆက်ဆံခံရသည်'])
revise('scrape together', 'The defining sense is gathering enough with difficulty, not gathering inadequately. The present Burmese can imply that the amount remains insufficient.', burmese=['လိုအပ်သည့်ပမာဏရအောင် ခက်ခက်ခဲခဲ ရှာဖွေစုဆောင်းသည်'])
revise('get an earful', 'An earful is a severe telling-off; it need not last a long time. Replace the duration restriction with severity.', burmese=['ပြင်းပြင်းထန်ထန် ဆူပူအပြောခံရသည်'])
revise('get religion', 'Add actual religious conversion. Figuratively this can mean starting to take a matter seriously/carefully without a prior moral error, or adopting an improved course after recognizing a problem. Preserve those distinct useful senses within the three-meaning limit.', burmese=['ဘာသာရေးကို အလေးအနက် ယုံကြည်ကိုးကွယ်လာသည်', 'ကိစ္စတစ်ခုကို အလေးအနက်ထားပြီး သေချာလုပ်လာသည်', 'အမှားကို သဘောပေါက်ပြီး လုပ်ပုံလုပ်နည်း ပြောင်းလာသည်'], sources=['https://www.merriam-webster.com/dictionary/get%20religion','https://dictionary.cambridge.org/us/dictionary/english/get-religion','https://www.collinsdictionary.com/us/dictionary/english/get-religion'])
revise('get the boot', 'Dismissal from a relationship/group is a common sense in addition to losing a job.', burmese=['အလုပ်မှ ထုတ်ပယ်ခံရသည်', 'အဖွဲ့ သို့မဟုတ် အချစ်ရေးမှ ဖယ်ထုတ်ခံရသည်'], sources=['https://www.collinsdictionary.com/us/dictionary/english/get-be-given-the-boot'])
revise('get the ax', 'Store the standard axe spelling under the same owner, not as another new phrase.', add_forms=['get the axe', 'gets the axe', 'got the axe', 'gotten the axe', 'getting the axe'], category='forms')

# Each verb and possessive pattern below was manually reviewed. Expansion only
# serializes reviewed grammatical combinations; it is not a lexical inference.
# These actual surface strings contain no slots and do not add separated objects.
patterns = [
 ('rain on your parade', ['rain','rains','rained','raining'], 'on {p} parade', False),
 ('blow your top', ['blow','blows','blew','blown','blowing'], '{p} top', True),
 ('blow your stack', ['blow','blows','blew','blown','blowing'], '{p} stack', True),
 ('blow your brains out', ['blow','blows','blew','blown','blowing'], '{p} brains out', False),
 ('beat your chest', ['beat','beats','beaten','beating'], '{p} chest', True),
 ('break your heart', ['break','breaks','broke','broken','breaking'], '{p} heart', False),
 ('break your neck', ['break','breaks','broke','broken','breaking'], '{p} neck', True),
 ('bite your nails', ['bite','bites','bit','bitten','biting'], '{p} nails', True),
 ('bare your teeth', ['bare','bares','bared','baring'], '{p} teeth', True),
 ('bend your ear', ['bend','bends','bent','bending'], '{p} ear', False),
 ('bet your bottom dollar', ['bet','bets','betting'], '{p} bottom dollar', True),
 ('button your lip', ['button','buttons','buttoned','buttoning'], '{p} lip', True),
 ('catch your death', ['catch','catches','caught','catching'], '{p} death', True),
 ('chew your ear off', ['chew','chews','chewed','chewing'], '{p} ear off', False),
 ('come into your own', ['come','comes','came','coming'], 'into {p} own', True),
 ('cool your heels', ['cool','cools','cooled','cooling'], '{p} heels', True),
 ('cramp your style', ['cramp','cramps','cramped','cramping'], '{p} style', False),
 ('cut your own throat', ['cut','cuts','cutting'], '{p} own throat', True),
 ('dance to your tune', ['dance','dances','danced','dancing'], 'to {p} tune', False),
 ('dig your own grave', ['dig','digs','dug','digging'], '{p} own grave', True),
 ('do your head in', ['do','does','did','done','doing'], '{p} head in', False),
 ('do your bit', ['do','does','did','done','doing'], '{p} bit', True),
 ('eat your words', ['eat','eats','ate','eaten','eating'], '{p} words', True),
 ('eat your heart out', ['eat','eats','ate','eaten','eating'], '{p} heart out', True),
 ('eat out of your hand', ['eat','eats','ate','eaten','eating'], 'out of {p} hand', False),
 ('fall on your feet', ['fall','falls','fell','fallen','falling'], 'on {p} feet', True),
 ('fall on your sword', ['fall','falls','fell','fallen','falling'], 'on {p} sword', True),
 ('fall flat on your face', ['fall','falls','fell','fallen','falling'], 'flat on {p} face', True),
 ('feather your nest', ['feather','feathers','feathered','feathering'], '{p} nest', True),
 ('find your voice', ['find','finds','found','finding'], '{p} voice', True),
 ('follow your nose', ['follow','follows','followed','following'], '{p} nose', True),
]
for phrase, verbs, tail, self_owned in patterns:
    additions = []
    for possessor in ['my','your','his','her']:
        for idx, verb in enumerate(verbs):
            # Third-person reflexive idioms require a matching third-person
            # possessor; forms such as 'eats my words' change the selected sense.
            if self_owned and idx == 1 and possessor in ['my','your']: continue
            additions.append(verb+' '+tail.format(p=possessor))
    revise(phrase, 'Common first/second/third-person possessive surfaces and useful tense/participle surfaces are missing. Add reviewed real contiguous strings; do not treat possessive substitutions as new canonical entries.', add_forms=additions, category='forms')

revise('bury yourself in work', 'Add common reflexive-person and tense surfaces. Use matched himself/herself forms for third-person present; no generic object slot is inserted.', add_forms=['bury himself in work','bury herself in work','bury ourselves in work','bury themselves in work','buries himself in work','buried yourself in work','buried himself in work','buried herself in work','buried ourselves in work','buried themselves in work','burying myself in work','burying himself in work','burying herself in work','burying ourselves in work','burying themselves in work'], category='forms')
revise('monkey on your back', 'The possessive varies in real subtitle use; the current single your possessor misses my/his/her surfaces.', add_forms=['monkey on my back','monkey on his back','monkey on her back','monkeys on my back','monkeys on his back','monkeys on her back'], category='forms')
revise('egg on your face', 'The current forms skip common your/her surfaces and the common have/has/had egg construction. Keep this existing idiom owner and fill useful surfaces within five tokens.', add_forms=['egg on her face','have egg on your face','have egg on his face','have egg on her face','has egg on her face','had egg on your face','had egg on his face','had egg on her face','having egg on my face','having egg on his face','having egg on her face'], category='forms')

revise('for all you know', 'This is only a pronoun substitution of frozen Batch 007 for all i know, contrary to the extension novelty rule. Replace the extension row with a distinct unused expression; do not change the frozen owner.', replacement={'phrase':'guilt by association','type':'expression','forms':[],'burmese':['မကောင်းသူများနှင့် ပတ်သက်မိသဖြင့် ကိုယ်ပါ အပြစ်ရှိသည်ဟု သတ်မှတ်ခံရခြင်း']}, sources=['https://www.merriam-webster.com/dictionary/guilt%20by%20association'], category='duplicate_variant')
revise('to all appearances', 'Cambridge explicitly lists to/from/by all appearances as variants. Batch 013 by all appearances owns this expression. Replace this new canonical row with a distinct unused idiom and consolidate the variant surfaces under the existing extension owner.', replacement={'phrase':'saving grace','type':'idiom','forms':['saving graces'],'burmese':['မကောင်းသည့်အချက်များကြားမှ တန်ဖိုးထားစရာ ကောင်းကွက်']}, sources=['https://dictionary.cambridge.org/dictionary/english/to-from-all-appearances','https://www.collinsdictionary.com/us/dictionary/english/saving-grace'], category='duplicate_variant')
revise('get a raw deal', 'Batch 013 raw deal already owns this idiom. Adding get is a light-verb surface of that existing idiom, not a distinct new expression. Consolidate the get surfaces under raw deal and replace this row with the distinct unused poetic justice.', replacement={'phrase':'poetic justice','type':'idiom','forms':[],'burmese':['ကိုယ်လုပ်ခဲ့သည့် မကောင်းမှုနှင့် လိုက်ဖက်စွာ ဝဋ်လည်ခြင်း']}, sources=['https://dictionary.cambridge.org/dictionary/english/poetic-justice'], category='duplicate_variant')

p13 = ROOT/'PhraseExtensionBatches/phrase_batch_013.json'
e13 = next(e for e in json.loads(p13.read_text(encoding='utf-8'))['entries'] if e['phrase']=='by all appearances')
r13 = copy.deepcopy(e13)
for form in ['to all appearances','from all appearances']:
    if form not in r13['forms']: r13['forms'].append(form)
cross = [{'target_batch':13,'phrase':'by all appearances','action':'replace','reason':'Consolidate established preposition variants under this existing extension owner; remove the duplicate canonical from Batch 015.', 'original':e13,'replacement':r13,'source_urls':['https://dictionary.cambridge.org/dictionary/english/to-from-all-appearances']}]
raw13 = next(e for e in json.loads(p13.read_text(encoding='utf-8'))['entries'] if e['phrase']=='raw deal')
rawr13 = copy.deepcopy(raw13)
rawr13['burmese'] = ['မတရားသဖြင့် ဆက်ဆံခံရမှု']
for form in ['get a raw deal','gets a raw deal','got a raw deal','gotten a raw deal','getting a raw deal']:
    if form not in rawr13['forms']: rawr13['forms'].append(form)
cross.append({'target_batch':13,'phrase':'raw deal','action':'replace','reason':'Consolidate the light-verb get surfaces under this existing idiom owner; use natural Burmese for unfair treatment.', 'original':raw13,'replacement':rawr13,'source_urls':[]})

proposed = [findings[e['phrase']]['replacement'] if e['phrase'] in findings else e for e in data['entries']]
owners = {}
collisions = []
for folder in ['PhraseBatches','PhraseExtensionBatches']:
    for p in sorted((ROOT/folder).glob('*.json')):
        batch_entries = proposed if p==path else json.loads(p.read_text(encoding='utf-8'))['entries']
        if p==p13: batch_entries=[r13 if e['phrase']=='by all appearances' else rawr13 if e['phrase']=='raw deal' else e for e in batch_entries]
        for e in batch_entries:
            for key in [e['phrase']]+e['forms']:
                key = normalize_key(key)
                if key in owners: collisions.append({'key':key,'first':owners[key],'second':[str(p.relative_to(ROOT)),e['phrase']]})
                else: owners[key]=[str(p.relative_to(ROOT)),e['phrase']]
for e in proposed:
    assert 2<=len(e['phrase'].split())<=5
    assert len(e['forms'])==len(set(e['forms']))
    assert e['phrase'] not in e['forms']
    assert all(2<=len(f.split())<=5 for f in e['forms'])
    assert 1<=len(e['burmese'])<=3
assert len(proposed)==250
assert not collisions, collisions
validator_owners, _, _ = base_dataset()
for p in sorted((ROOT/'PhraseExtensionBatches').glob('*.json')):
    validator_entries = proposed if p==path else json.loads(p.read_text(encoding='utf-8'))['entries']
    if p==p13: validator_entries=[r13 if e['phrase']=='by all appearances' else rawr13 if e['phrase']=='raw deal' else e for e in validator_entries]
    errors = validate_entries(validator_entries, validator_owners)
    assert not errors, errors
report = {'review_date':'2026-10-07','batch':15,'input_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'reviewed_entry_count':250,'reviewed_stored_form_count':sum(len(e['forms']) for e in data['entries']),'changed_entry_count':len(findings),'reviewed_no_change_count':250-len(findings),'all_entries_reviewed_for':['Burmese naturalness and sense accuracy','common subtitle sense omissions','type','established lexical construction','grammatical forms and possessive/reflexive ownership','mandatory object insertion','exact and cosmetic variant ownership against all 16 frozen/extension batches'],'findings':list(findings.values()),'cross_batch_findings':cross,'proposed_snapshot_checks':{'entries_in_batch':250,'stored_forms_in_batch':sum(len(e['forms']) for e in proposed),'lookup_collisions_across_all_batches':len(collisions),'surface_tokens_and_sense_limits':'pass'},'editorial_notes':['No source batches, artifacts, indexes, manifests, or git state were modified by this review.','Do not collapse distinct lexical synonyms, such as scale back/scale down, scare away/scare off, or different verb lemmas, solely because Burmese meanings coincide.','latch on and latch onto have independently attested selected constructions/senses; preserve separate entries. latch on to variants are assigned to latch onto, with full key checks.','All existing forms were reviewed. Past tense beat/bet/cast/cost/cut can equal the canonical surface and is already matchable; do not add the canonical to forms.','Positive bat an eyelid is grammatical; common negation precedes the stored substring and is handled at subtitle sentence level. No false grammatical rejection is proposed.','Forms use common actual my/your/his/her surfaces. A Cartesian product of every person/number/object insertion was deliberately not treated as compulsory.','Proposed Burmese glosses are independently authored. Source links establish English facts and variants; no proprietary gloss is copied.']}
outdir = Path(__file__).resolve().parent
(outdir/'batch015_review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines = ['# Batch 015 rereview','',f"Reviewed all 250 entries and {report['reviewed_stored_form_count']} existing stored forms. {len(findings)} entries have concrete proposals; {250-len(findings)} entries need no change.",'', 'Proposals pass a simulated 16-batch exact owner/collision check, surface token limits, and the three-meaning limit. Source assets and git were not modified.','']
for f in findings.values():
    lines += [f"## {f['entry_number']}. {f['phrase']}", '', ' '.join(f['reasons']), '', '```json',json.dumps(f['replacement'],ensure_ascii=False,indent=2),'```','']
    if f['source_urls']: lines += ['Sources: '+', '.join(f'[{u.split("/")[2]}]({u})' for u in f['source_urls']), '']
lines += ['## Cross-batch ownership proposal','', json.dumps(cross,ensure_ascii=False,indent=2),'','## No-change entries','', ', '.join(e['phrase'] for e in data['entries'] if e['phrase'] not in findings), '','## Editorial decisions','']
lines += ['- '+note for note in report['editorial_notes']]
(outdir/'batch015_review.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({k:report[k] for k in ['batch','reviewed_entry_count','reviewed_stored_form_count','changed_entry_count','reviewed_no_change_count','proposed_snapshot_checks']},ensure_ascii=False,indent=2))
