"""Persist completed editorial, lexical, phonetic, and validation reviews."""
import json,base64,zlib,re,hashlib,collections
from pathlib import Path
s=Path(__file__).parent;r=s.parents[2]
entries=json.loads((s/'selected_entries.json').read_text(encoding='utf8'))
prior=set(zlib.decompress(base64.b64decode((r/'extension_lookup/used_keys_current.zlib.b64').read_text())).decode().splitlines())
verified=set('''
roughhouse housebreak jackknife bonehead tearaway knockabout pallbearer schoolmistress nightspot eyewash leaseholder headstand gumdrop moonshiner horsefly popgun snuffbox
wildcard motorsport shirtless multiverse bubblegum butthurt subpar undercard biofilm partway
germfree footsore colorfast conscienceless nonliving overweening lightless spiritless semiconscious drugless seriocomic
teenaged undersized undernourished semiarid transmittable tuneless alienable amendable apelike cleanable merchantable frolicsome expectable venturesome toilsome technophobic counteractive shockable ponderable
viewership underrepresented psychosocial mentorship underserved underfunded ridership interactivity underutilized suboptimal logistically supermajority organizationally socioeconomically radioactively macroscopically typographically polemically lethargically remorsefully ascetically egotistically hectically
detestably manageably mirthfully pardonably phlegmatically trustfully voyeuristically sundries swashbuckler literalism overestimation wretchedness exactness kiloton dingbat straightness counterargument oddness pointlessness aloneness antiserum uncleanness offensiveness protectiveness unselfishness mentalism repetitiveness interposition straightforwardness handsomeness merchantability spittoon
obliviousness conciseness falseness slickness conformism exclusiveness religiousness monarchism photophobia seaworthiness archduchess distinctness originalism senselessness deceitfulness expansiveness innovativeness hyperextension sexpot overexertion deviousness leanness inattentiveness unresponsiveness connoisseurship kilobyte lushness warmness monotheist nymphomania
whenever whichever itself whereby preorder rebar ginormous nonzero undersexed preterm polycystic fuckery unsub repo parkour kaiju matcha emoji repurpose
'''.split())
special={
 'fuckhead':('https://ahdictionary.com/word/search.html?q=fuckhead','American Heritage gives the closed vulgar noun headword.'),
 'highchair':('https://ahdictionary.com/word/search.html?q=highchair','American Heritage gives the closed noun headword.'),
 'weedkiller':('https://www.oxfordlearnersdictionaries.com/us/definition/english/weedkiller','Oxford gives the closed noun headword and American IPA.'),
 'shopfront':('https://dictionary.cambridge.org/us/dictionary/english/shopfront','Cambridge gives the closed noun headword and American IPA.'),
 'spacetime':('https://www.dictionary.com/browse/spacetime','Explicit closed variant of space-time.'),
 'freeform':('https://ahdictionary.com/word/search.html?q=freeform','American Heritage gives the closed adjective headword; also Dictionary.com explicitly lists freeform as a variant.'),
 'config':('https://www.collinsdictionary.com/us/dictionary/english/config','Established clipping of configuration; con+fig is a heuristic false positive.'),
 'vitriolically':('https://dictionary.cambridge.org/dictionary/english/vitriolically','Established manner adverb; US IPA consulted.'),
 'pfft':('https://www.collinsdictionary.com/us/dictionary/english/pfft','Lexicalized interjection; American pronunciation /ft/ consulted.'),
}
records=[];missing=[]
for e in entries:
    w=e['word'];splits=[w[:i]+'+'+w[i:]for i in range(3,len(w)-2)if w[:i]in prior and w[i:]in prior]
    if w in special:url,note=special[w]
    elif w in verified:url='https://www.merriam-webster.com/dictionary/'+w;note='Current dictionary confirms the closed headword or explicitly lists the closed derivative/variant.'
    elif not splits:continue
    else:missing.append((w,splits));continue
    if w=='wildcard':note='Closed spelling explicitly documented for computing sense; selected gloss restricted to this sense.'
    if w=='germfree':note='Merriam-Webster explicitly lists germfree as a closed variant of germ-free; not an invented glued spelling.'
    records.append(dict(word=w,status='verified',reviewedDate='2026-10-07',url=url,suspiciousSplits=splits,decision=note))
assert not missing,missing
(s/'lexical_review.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(s/'closed_compound_allowlist_proposed.txt').write_text('\n'.join(sorted(x['word']for x in records if x['suspiciousSplits']))+'\n',encoding='utf8')
allwords=[l.split('|')[0]for p in s.glob('authored_*.txt')for l in p.read_text(encoding='utf8').splitlines()if l.strip()and not l.startswith('#')]
selected={e['word']for e in entries}
editorial=dict(authoredDrafts=len(allwords),selected=len(entries),rejectedAfterDraft=[dict(word=w,reason='Excluded from current usable pool after subtitle usefulness and canonical-spelling review; not necessarily an invalid English word.')for w in allwords if w not in selected],specificDecisions=[
 'No assigned batch-number files were produced after the user changed the target to quality-dependent aggregation.',
 'Excluded gramma, saree, flautist and kabob as low-value alternatives of established covered lemmas.',
 'Stored no plurals for mass/abstract nouns. Bitters, rounders, and sundries retain their established plural-only lexical senses.',
 'Reviewed homunculus/homunculi, ileum/ilea, embolus/emboli, vivarium/vivaria and diptych/diptychs; kaiju plural is invariant and therefore not stored.',
 'Reviewed all selected missing-resource IPA. Cussed uses the adjective pronunciation; noir, quinoa, genocidal, rentier, menarche, mortgagor, and compound/derivative stress received explicit corrections.',
 'Burmese glosses independently authored. WordNet English definitions used for lexical sense review only.',
],originalAssignedTarget=1500,shortfall=1500-len(entries))
(s/'editorial_review.json').write_text(json.dumps(editorial,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
errors=[];owned=prior|selected;newforms=set();ipa_chars=set('abcdefghijklmnopqrstuvwxyzæðŋɑɒɔəɚɛɝɡɪɹʃʊʌʒʤʧˈˌːˑ.θɾɫɐʔ̩̯̃͡')
for e in entries:
    w=e['word'];assert re.fullmatch('[a-z]+',w),w;assert w not in prior,w;assert int(hashlib.sha256(w.encode()).hexdigest(),16)%10 in(6,7,8),w
    assert set(e)=={'word','pronunciation','forms','meanings'},w
    p=e['pronunciation'];assert re.fullmatch('/[^/]+/',p)and not any(c.isspace()for c in p),w;assert set(p[1:-1])<=ipa_chars,(w,p)
    assert len(e['forms'])==len(set(e['forms'])),w
    for f in e['forms']:assert re.fullmatch('[a-z]+',f)and f not in owned|newforms,(w,f);newforms.add(f)
    assert 1<=sum(len(m['burmese'])for m in e['meanings'])<=3,w
    for m in e['meanings']:
        assert m['partOfSpeech']in{'noun','verb','adjective','adverb','pronoun','preposition','conjunction','interjection','determiner','modal','auxiliary'},w
        for g in m['burmese']:assert g.strip()and not re.search('[A-Za-z]',g)and re.search('[\u1000-\u109f]',g),(w,g)
summary=dict(result='PASS',selectedHeadwords=len(entries),storedForms=len(newforms),lookupKeys=len(entries)+len(newforms),meanings=sum(len(m['burmese'])for e in entries for m in e['meanings']),partOfSpeechCounts=dict(collections.Counter(m['partOfSpeech']for e in entries for m in e['meanings'])),lexicalReviews=len(records),suspiciousSplitsVerified=sum(bool(x['suspiciousSplits'])for x in records),sha256=hashlib.sha256((s/'selected_entries.json').read_bytes()).hexdigest(),scope='Staged candidate schema, exclusion, spelling-format, IPA-format, gloss-count, and within-selection collision checks. Root runs canonical exactly-500 batch validation after global integration.')
(s/'validation_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(summary,indent=2))
