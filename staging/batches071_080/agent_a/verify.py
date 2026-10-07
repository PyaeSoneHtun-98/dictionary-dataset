import json,re,sys
from pathlib import Path
from collections import Counter
import base64,zlib,hashlib
D=Path(__file__).resolve().parent
ROOT=D.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from validate_extension_batch import ALLOWED_POS, IPA_CHARACTERS
entries=json.loads((D/'selected_entries.json').read_text(encoding='utf-8'))
prior=set(zlib.decompress(base64.b64decode((ROOT/'extension_lookup/used_keys_current.zlib.b64').read_text())).decode().splitlines())
heads={e['word'] for e in entries}
assert len(heads)==len(entries)
assert not heads&prior
owned=set(prior)|heads
for e in entries:
    assert set(e)=={'word','pronunciation','forms','meanings'}
    assert re.fullmatch('[a-z]+',e['word'])
    assert int(hashlib.sha256(e['word'].encode()).hexdigest(),16)%10 in {0,1,2}
    ipa=e['pronunciation']
    assert ipa.startswith('/') and ipa.endswith('/') and ipa[1:-1] and not re.search(r'\s',ipa)
    assert set(ipa[1:-1])<=IPA_CHARACTERS, (e['word'],ipa)
    assert len(e['forms'])==len(set(e['forms']))
    for f in e['forms']:
        assert re.fullmatch('[a-z]+',f) and f not in owned, (e['word'],f)
        owned.add(f)
    assert e['meanings']
    assert 1<=sum(len(m['burmese']) for m in e['meanings'])<=3
    for m in e['meanings']:
        assert set(m)=={'partOfSpeech','burmese'} and m['partOfSpeech'] in ALLOWED_POS
        assert m['burmese'] and all(g.strip() and not re.search('[A-Za-z]',g) for g in m['burmese'])
lexical={r['word']:r for r in json.loads((D/'lexical_review.json').read_text())}
pending=json.loads((D/'lexical_pending.json').read_text())
assert all(w['word'] in lexical and lexical[w['word']]['decision'].startswith('verified') for w in pending)
result={'entries':len(entries),'forms':sum(len(e['forms']) for e in entries),'lookupKeys':len(owned)-len(prior),'burmeseMeanings':sum(len(m['burmese']) for e in entries for m in e['meanings']),'partOfSpeech':dict(Counter(m['partOfSpeech'] for e in entries for m in e['meanings'])),'priorCollisions':0,'internalCollisions':0,'lexicallyReviewed':len(pending),'missingIPA':0,'sourceSHA256':hashlib.sha256((D/'selected_entries.json').read_bytes()).hexdigest()}
(D/'validation_summary.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
