import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'PhraseExtensionBatches/phrase_batch_016.json'
data = json.loads(SOURCE.read_text(encoding='utf-8'))
by_phrase = {e['phrase']: e for e in data['entries']}
issues = []

def change(phrase, reason, *, burmese=None, add_forms=None, forms=None, urls=None, category='sense_or_gloss'):
    old = by_phrase[phrase]
    new = copy.deepcopy(old)
    if burmese is not None:
        new['burmese'] = burmese
    if forms is not None:
        new['forms'] = forms
    if add_forms:
        new['forms'] = list(dict.fromkeys(new['forms'] + add_forms))
    assert new != old
    issues.append({'entry_number': data['entries'].index(old)+1, 'phrase': phrase, 'action': 'replace_entry', 'category': category, 'reason': reason, 'original_entry': old, 'replacement_entry': new, 'source_urls': urls or []})

change('skim off', 'The second Burmese gloss repeats two verbs awkwardly. It should identify quietly taking a portion of receipts/profits, without implying that all skimming is violent theft.', burmese=['အပေါ်ယံမှ ခပ်ထုတ်သည်', 'ရငွေထဲမှ အချို့ကို တိတ်တဆိတ် ဖြတ်ယူသည်'])
change('presumption of innocence', 'The current Burmese construction for not yet proven guilty is incomplete; explicitly distinguish proving guilt from merely proving an offence.', burmese=['အပြစ်ရှိကြောင်း မသက်သေပြနိုင်မချင်း အပြစ်ကင်းသူဟု ယူဆခြင်း'])
change('go down the rabbit hole', 'This is an inflecting five-token idiom, not a fixed uninflected expression. The four ordinary tense/aspect surface forms fit the token limit.', add_forms=['goes down the rabbit hole','went down the rabbit hole','gone down the rabbit hole','going down the rabbit hole'], category='useful_forms')
change('soak up', 'Knowledge is understood and remembered, not experienced as an atmosphere. Separate the liquid, information and pleasurable-experience senses within the three-sense ceiling.', burmese=['စုပ်ယူသည်','ဗဟုသုတများကို နားလည်မှတ်သားယူသည်','ပတ်ဝန်းကျင်အရသာကို အားရပါးရ ခံစားသည်'], urls=['https://dictionary.cambridge.org/dictionary/english/soak-up'])
change('grin and bear it', 'The perfect-tense coordinated participle is grinned and borne it. The stored grinned and bore it is valid simple past and should remain.', add_forms=['grinned and borne it'], category='useful_forms', urls=['https://dictionary.cambridge.org/us/dictionary/english/grin-and-bear-it','https://www.merriam-webster.com/dictionary/bear'])
change('person of interest', 'စုံစမ်းလိုသူ can read as a person who wants to investigate. Identify the person being investigated, without labelling them charged or guilty.', burmese=['အမှုနှင့် ပတ်သက်နိုင်သည်ဟု ယူဆ၍ ရဲက စုံစမ်းနေသူ'], urls=['https://www.merriam-webster.com/dictionary/person%20of%20interest'])
change('have a cow', 'The idiom does not require the cause to be trivial; remove အသေးအဖွဲကြောင့်. The emotion is being angry/upset, not positive excitement.', burmese=['အလွန်စိတ်ဆိုးပြီး အကြီးအကျယ် တုံ့ပြန်သည်'], urls=['https://www.merriam-webster.com/dictionary/have%20a%20cow'])
change('stack up', 'How someone/something stacks up against another describes comparison and need not imply that it meets the standard. Retain the accumulation sense and express comparison without a guaranteed favourable result.', burmese=['စုပုံများပြားလာသည်','အခြားသူ သို့မဟုတ် အရာနှင့် နှိုင်းယှဉ်ကြည့်သည်'], urls=['https://www.merriam-webster.com/dictionary/stack%20up'])
change('no contest', 'The legal plea is valid but the common conversational/competition sense of obvious one-sided superiority is missing.', burmese=['စွဲချက်ကို ဝန်မခံသော်လည်း မကန့်ကွက်ကြောင်း ထွက်ဆိုခြင်း','တစ်ဖက်က အပြတ်အသတ် သာလွန်သည်'], urls=['https://www.collinsdictionary.com/dictionary/english/no-contest','https://www.merriam-webster.com/dictionary/no%20contest'])
change('hung jury', 'The headword names a jury unable to agree on the required verdict, not simply the abstract fact that plural juries disagree. Make the noun referent clear.', burmese=['စီရင်ချက်အပေါ် သဘောတူညီမှု မရနိုင်သည့် ဂျူရီအဖွဲ့'])
change('know which way is up', 'Add the normal third-person and participial present forms. All are five tokens; the existing past forms remain grammatical.', add_forms=['knows which way is up','knowing which way is up'], category='useful_forms')
change('lick your wounds', 'The idiom is recovery after humiliation/defeat, rather than literal injuries. licks your wounds normally changes the sufferer away from the subject and is unsuitable as its default reflexive third-person form; use licks his/her wounds.', burmese=['ရှုံးနိမ့်မှုကြောင့် စိတ်ထိခိုက်ရာမှ ပြန်အားတင်းရန် ခဏနားသည်'], forms=['lick my wounds','lick our wounds','lick their wounds','licks his wounds','licks her wounds','licked my wounds','licked your wounds','licked his wounds','licked her wounds','licked our wounds','licked their wounds','licking my wounds','licking your wounds','licking his wounds','licking her wounds','licking our wounds','licking their wounds'], category='sense_and_forms')
change('double jeopardy', 'The legal context is a second prosecution or punishment for the same offence, not ordinary repeated charging without qualification. Add the punishment dimension without explaining jurisdiction-specific exceptions in a lookup gloss.', burmese=['ပြစ်မှုတစ်ခုတည်းအတွက် ထပ်မံတရားစွဲဆို သို့မဟုတ် အပြစ်ပေးခံရခြင်း'], urls=['https://www.law.cornell.edu/wex/double_jeopardy'])
change('tuck in', 'The clothing sense is common in dialogue and is currently missing. Keep the bed-cover and eating senses; all three remain useful.', burmese=['အင်္ကျီအောက်စကို ဘောင်းဘီ သို့မဟုတ် ထဘီထဲ ထည့်သည်','အိပ်ရာထဲ စောင်လုံအောင် ခြုံပေးသည်','အားရပါးရ စစားသည်'], urls=['https://www.oxfordlearnersdictionaries.com/us/definition/american_english/tuck-in'])
change('open the floodgates', 'The figurative phrase can unleash requests, applications, money, discussion or other activity; it is not restricted to problems or emotions. Use a neutral unrestricted gloss.', burmese=['ပိတ်ပင်ကန့်သတ်ထားရာမှ အရာတစ်ခု အလုံးအရင်းဖြင့် ဖြစ်ပေါ်လာစေသည်'], urls=['https://dictionary.cambridge.org/dictionary/english/open-the-floodgates'])
change('cease and desist', 'The current gloss defines an order only. The unhyphenated phrase is also a verbal demand/action to stop; a lawyer letter is not automatically a legal order. Give both the stopping sense and the formal-demand sense.', burmese=['လုပ်နေသည့် အပြုအမူကို ရပ်တန့်ပြီး ထပ်မလုပ်တော့သည်','ဆက်မလုပ်ရန် တရားဝင် တားမြစ်သတိပေးချက်'], add_forms=['ceases and desists','ceased and desisted','ceasing and desisting'], urls=['https://dictionary.cambridge.org/us/dictionary/english/cease-and-desist','https://www.oxfordlearnersdictionaries.com/definition/english/cease-and-desist','https://www.law.cornell.edu/wex/cease_and_desist_letter'])
change('tune in', 'ရုပ်သံကို ဖွင့်နားထောင် alone omits viewing a television programme. Correct the medium-neutral action without changing either sense.', burmese=['ရေဒီယို သို့မဟုတ် ရုပ်သံအစီအစဉ်ကို ဖွင့်ကြည့်နားထောင်သည်','အာရုံစိုက်သည်'])
change('wrongful death', 'The existing wording can imply a criminally guilty act and misses negligence, a central civil wrongful-death context.', burmese=['တစ်ဦး၏ မတရားလုပ်ရပ် သို့မဟုတ် ပေါ့ဆမှုကြောင့် သေဆုံးမှု'], urls=['https://www.law.cornell.edu/wex/wrongful_death'])
change('play the fool', 'ပေါ့ပေါ့ပျက်ပျက် can mean careless or irresponsible behaviour and misses the intentional silly behaviour/joking sense.', burmese=['ပေါက်ကရပြောဆိုပြုမူ၍ ပျော်အောင်လုပ်သည်'], urls=['https://dictionary.cambridge.org/dictionary/english/play-the-fool'])
change('wash away', 'Only an intransitive washed/carried-away gloss is stored. The common transitive wash away dirt, blood or evidence needs the removal sense.', burmese=['ရေနှင့် မျောပါပျောက်သွားသည်','ရေဖြင့် ဆေးကြောဖယ်ရှားသည်'], urls=['https://www.collinsdictionary.com/dictionary/english/wash-away'])
change('pull your punches', 'အားမပါဘဲ ထိုးသည် can imply inability/weakness rather than deliberately withholding force. The figurative sense also extends beyond criticism to deliberate restraint in attacking/competing.', burmese=['ထိုးနှက်ရာတွင် အားကို တမင်လျှော့ထားသည်','ဝေဖန်တိုက်ခိုက်ရာတွင် တမင်အရှိန်လျှော့ထားသည်'], add_forms=['pulled your punches','pulls her punches','pulled his punches','pulled her punches','pulling my punches','pulling his punches','pulling her punches','pull our punches','pull their punches','pull punches','pulls punches','pulled punches','pulling punches'], category='sense_and_forms', urls=['https://www.merriam-webster.com/dictionary/pull%20punches'])
change('wash out', 'The fail a course/training or be eliminated as unsuitable sense is common in military, school and sport dialogue and is absent.', burmese=['ဆေးကြောဖယ်ရှားသည်','မိုးကြောင့် အစီအစဉ် ပျက်သွားသည်','အရည်အချင်းမမီ၍ သင်တန်း သို့မဟုတ် ရွေးချယ်မှုမှ ထွက်ရသည်'], urls=['https://www.merriam-webster.com/dictionary/wash%20out'])
change('put the boot in', 'The existing figurative gloss is useful, but the literal idiomatic attack on someone already down is also a common crime/action sense.', burmese=['လဲနေသူကို ထပ်ကန်ကျောက်သည်','အားနည်းနေသူကို ပိုပြီး ဝေဖန်တိုက်ခိုက်သည်'], urls=['https://dictionary.cambridge.org/dictionary/english/put-the-boot-in'])
change('raise the roof', 'The phrase can also mean angrily and loudly protesting; the stored rejoicing-only sense misses that established common use.', burmese=['အလွန်ကျယ်လောင်စွာ အော်ဟစ်ပျော်မြူးသည်','ဒေါသတကြီး ဆူညံကန့်ကွက်သည်'], urls=['https://www.dictionary.com/browse/raise-the-roof'])

# These additions are specific useful missing surface forms, not new canonical entries.
form_additions = {
    'get your feet wet': ['got your feet wet','gotten your feet wet','gotten my feet wet','got his feet wet','gotten his feet wet','gets her feet wet','got her feet wet','getting my feet wet','getting his feet wet','getting her feet wet','get our feet wet','get their feet wet'],
    'get your wires crossed': ['got your wires crossed','gotten your wires crossed','gotten my wires crossed','got our wires crossed','got their wires crossed','gets his wires crossed','got his wires crossed','got her wires crossed','getting my wires crossed','getting his wires crossed','getting her wires crossed'],
    'go into your shell': ['went into your shell','gone into your shell','gone into my shell','went into her shell','gone into her shell','goes into his shell','went into his shell','gone into his shell','going into my shell','going into his shell','going into her shell'],
    'hang your head': ['hung your head','hung his head','hangs her head','hung her head','hanging my head','hanging his head','hanging her head'],
    'have your work cut out': ['have my work cut out','have our work cut out','have their work cut out','has his work cut out','had your work cut out','had his work cut out','had her work cut out','having my work cut out'],
    'keep your powder dry': ['kept your powder dry','kept his powder dry','keeps her powder dry','kept her powder dry','keeping my powder dry','keeping his powder dry','keeping her powder dry'],
    'kick up your heels': ['kicked up your heels','kicked up her heels','kicks up his heels','kicked up his heels','kicking up my heels','kicking up his heels','kicking up her heels'],
    'lose your shirt': ['lost your shirt','lost his shirt','loses her shirt','lost her shirt','losing my shirt','losing his shirt','losing her shirt'],
    'lose your rag': ['lost your rag','lost her rag','loses his rag','lost his rag','losing my rag','losing his rag','losing her rag'],
    'lose your marbles': ['lost your marbles','lost his marbles','loses her marbles','lost her marbles','losing my marbles','losing his marbles','losing her marbles'],
    'poke your nose in': ['poked your nose in','poked his nose in','pokes her nose in','poked her nose in','poking my nose in','poking his nose in','poking her nose in','poke your nose into','poked your nose into','poking your nose into','poke my nose into','poked my nose into','pokes his nose into','poked his nose into','poking his nose into'],
    'rest on your laurels': ['rested on your laurels','rested on her laurels','rests on his laurels','rested on his laurels','resting on my laurels','resting on his laurels','resting on her laurels'],
}
for phrase, forms in form_additions.items():
    change(phrase, 'The current mixed possessive forms miss ordinary past/participle or third-person strings likely in dialogue. Add the listed grammatical contiguous forms under the existing owner; do not count them as separate phrases.', add_forms=forms, category='useful_forms')
mouth_forms = [f'{verb} words in {poss} mouth' for verb in ['put','puts','putting'] for poss in ['my','your','his','her','our','their'] if f'{verb} words in {poss} mouth' != 'put words in your mouth']
change('put words in your mouth', 'The possessive identifies the person falsely attributed words, not necessarily the actor. Very common puts/putting words in my mouth and his/her/our/their variants are missing; all are five tokens. Past put is identical to base and must not be duplicated.', forms=mouth_forms, category='useful_forms')

replacements = [
 ('go through the roof', 'PhraseBatches/phrase_batch_009.json', 'through the roof', {'phrase':'take no prisoners','type':'idiom','forms':['takes no prisoners','took no prisoners','taken no prisoners','taking no prisoners'],'burmese':['သူတစ်ပါးကို မငဲ့ဘဲ အလျှော့မပေးတမ်း လုပ်ဆောင်သည်']}, ['https://dictionary.cambridge.org/dictionary/english/take-no-prisoners']),
 ('live from hand to mouth', 'PhraseExtensionBatches/phrase_batch_014.json', 'from hand to mouth', {'phrase':'make a beeline for','type':'idiom','forms':['makes a beeline for','made a beeline for','making a beeline for'],'burmese':['လိုရာဆီကို အလျင်အမြန် တည့်တည့်သွားသည်']}, ['https://dictionary.cambridge.org/dictionary/english/make-a-beeline-for']),
 ('open a can of worms', 'PhraseExtensionBatches/phrase_batch_013.json', 'can of worms', {'phrase':'move the goalposts','type':'idiom','forms':['moves the goalposts','moved the goalposts','moving the goalposts'],'burmese':['သဘောတူပြီးသား စည်းကမ်းသတ်မှတ်ချက်ကို ပြန်ပြောင်းပြီး အခက်တွေ့အောင်လုပ်သည်']}, ['https://dictionary.cambridge.org/dictionary/english/move-the-goalposts']),
 ('paper over the cracks', 'PhraseExtensionBatches/phrase_batch_015.json', 'paper over', {'phrase':'at cross purposes','type':'idiom','forms':[],'burmese':['မတူသည့်အကြောင်း သို့မဟုတ် ရည်ရွယ်ချက်ကို ပြောနေ၍ အချင်းချင်း နားလည်မှုလွဲနေသည်']}, ['https://dictionary.cambridge.org/dictionary/english/cross-purposes']),
 ('play cat and mouse', 'PhraseExtensionBatches/phrase_batch_015.json', 'cat and mouse', {'phrase':'run rings around','type':'idiom','forms':['runs rings around','ran rings around','running rings around','run circles around','runs circles around','ran circles around','running circles around'],'burmese':['တစ်ဖက်လူထက် အရည်အချင်းများစွာ သာလွန်သည်']}, ['https://dictionary.cambridge.org/dictionary/english/run-rings-around','https://www.dictionary.com/browse/ring']),
]
consolidations = []
for phrase, owner_file, owner_phrase, replacement, urls in replacements:
    old = by_phrase[phrase]
    owner_data = json.loads((ROOT / owner_file).read_text(encoding='utf-8'))
    owner = next(e for e in owner_data['entries'] if e['phrase'] == owner_phrase)
    if owner_file.startswith('PhraseBatches/'):
        reason = 'This republishes the frozen through-the-roof idiom by adding an inflected leading verb. Its extra anger sense requires a separately documented frozen correction/overlay design, rather than a second extension owner. Root reviewer resolved this overlap in favour of replacement.'
    else:
        reason = 'The longer phrase is the same earlier-owned idiom with its normal leading verb/complement, not a genuinely new phrase. Consolidate valid contiguous strings with the earlier extension owner and replace this canonical slot.'
        merged = copy.deepcopy(owner)
        moved_forms = [phrase]+old['forms']
        if phrase == 'live from hand to mouth':
            moved_forms += ['lives from hand to mouth','lived from hand to mouth','living from hand to mouth']
        if phrase == 'open a can of worms':
            moved_forms += ['opens a can of worms','opened a can of worms','opening a can of worms']
        merged['forms'] = list(dict.fromkeys(owner['forms']+moved_forms))
        consolidations.append({'file':owner_file,'phrase':owner_phrase,'original_entry':owner,'replacement_entry':merged,'reason':'Single-owner consolidation of Batch 016 duplicate; perform together with its canonical replacement.'})
    issues.append({'entry_number':data['entries'].index(old)+1,'phrase':phrase,'action':'replace_canonical_slot','category':'variant_ownership','reason':reason,'related_owner':{'file':owner_file,'phrase':owner_phrase},'original_entry':old,'replacement_entry':replacement,'source_urls':urls})

all_entries = [(p.relative_to(ROOT).as_posix(),e) for folder in ['PhraseBatches','PhraseExtensionBatches'] for p in sorted((ROOT / folder).glob('*.json')) for e in json.loads(p.read_text(encoding='utf-8'))['entries']]
key_owners = {}
exact_conflicts = []
for file,e in all_entries:
    for key in [e['phrase']]+e['forms']:
        key = ' '.join(key.lower().split())
        if key in key_owners:
            exact_conflicts.append({'key':key,'first':key_owners[key],'second':[file,e['phrase']]})
        key_owners[key] = [file,e['phrase']]
proposed_keys = {}
for issue in issues:
    e = issue['replacement_entry']
    for key in [e['phrase']]+e['forms']:
        assert 2 <= len(key.split()) <= 5, key
        assert key == key.lower() and key == ' '.join(key.split()), key
        existing = key_owners.get(key)
        assert existing is None or existing == ['PhraseExtensionBatches/phrase_batch_016.json',issue['phrase']], (key,existing)
        assert key not in proposed_keys, key
        proposed_keys[key] = e['phrase']
    assert 1 <= len(e['burmese']) <= 3
    assert len(e['forms']) == len(set(e['forms']))
    assert e['phrase'] not in e['forms']
for c in consolidations:
    for k in c['replacement_entry']['forms']:
        assert 2 <= len(k.split()) <= 5, k

changed = {i['phrase'] for i in issues}
for issue in issues:
    if issue['phrase'] == 'tuck in':
        issue['source_urls'].insert(0, 'https://www.collinsdictionary.com/dictionary/english/tuck-in')
    if issue['phrase'] == 'open the floodgates':
        issue['source_urls'] = ['https://www.merriam-webster.com/dictionary/open%20the%20floodgates']
    if issue['phrase'] == 'play the fool':
        issue['source_urls'] = ['https://dictionary.cambridge.org/dictionary/english/act-play-the-fool']
issues.sort(key=lambda i:i['entry_number'])
report = {'batch':16,'source_file':'PhraseExtensionBatches/phrase_batch_016.json','source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'reviewed_entry_count':250,'reviewed_form_count':sum(len(e['forms']) for e in data['entries']),'all_namespace_entry_count':len(all_entries),'namespace_exact_conflicts':exact_conflicts,'flagged_entry_count':len(changed),'reviewed_no_change_count':250-len(changed),'reviewed_no_change_phrases':[e['phrase'] for e in data['entries'] if e['phrase'] not in changed],'issues':issues,'earlier_extension_owner_consolidations':consolidations,'notes':['Every entry and stored form was read manually. Exact canonical/form ownership was checked across all frozen and extension batches. Possessive-normalized and contained-string screening was followed by manual semantic review.','New canonical replacements and proposed Batch 016 forms were checked against the entire current namespace, including later entries in Batch 016.','ducks in a row remains a valid four-token contiguous fragment: the full get/have your ducks in a row is six tokens and therefore unavailable in v1.','lay cards on the table/cards on the table remain useful five/four-token contiguous strings. The fuller possessive verbal expression is six tokens.','No placeholder strings or separated-object pattern expansion is proposed.','Positive glosses for hold a candle to and pull your punches can be negated in their surrounding sentence; negation is not represented as an equivalent form.','run rings around and run circles around belong to one replacement owner; past participle run coincides with base and is not duplicated.','No batch, lookup, manifest, runtime artifact, frozen asset or Git data was edited. Publisher source facts informed independently authored Burmese glosses; no proprietary definitions were copied.']}
dest = Path(__file__).parent
(dest/'batch016_review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines = ['# Batch 016 rereview', '', f"Reviewed all 250 entries and {report['reviewed_form_count']} stored forms against {len(all_entries)} frozen/extension entries.", f"Flagged {len(changed)} entries; {250-len(changed)} entries need no change. No exact namespace collisions were found." if not exact_conflicts else f'Exact collisions: {len(exact_conflicts)}.', '', 'Full before/after entries and earlier-owner consolidations are in `batch016_review.json`. Proposed changes are not applied.', '']
for issue in issues:
    lines += [f"## {issue['entry_number']}. {issue['phrase']}",'',issue['reason'],'','```json',json.dumps(issue['replacement_entry'],ensure_ascii=False,indent=2),'```','']
    for u in issue['source_urls']:
        lines.append(f'- [Publisher source]({u})')
    if issue['source_urls']:
        lines.append('')
lines += ['## Earlier extension owner consolidation','','']
for c in consolidations:
    lines += [f"- {c['file']}: **{c['phrase']}** takes the removed Batch 016 strings as forms."]
lines += ['', '## Review notes', ''] + ['- '+n for n in report['notes']]
(dest/'batch016_review.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'flagged_entries':len(changed),'no_change_entries':250-len(changed),'reviewed_forms':report['reviewed_form_count'],'namespace_exact_conflicts':len(exact_conflicts),'owner_consolidations':len(consolidations)},indent=2))
