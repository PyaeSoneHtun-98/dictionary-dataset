"""Assemble manually authored TSV meanings with reviewed pronunciation/forms."""
import base64
import json
import re
import sys
import zlib
from pathlib import Path

from eng_to_ipa.stress import find_stress
from eng_to_ipa.transcribe import get_cmu
from lemminflect import getInflection
import cmudict

ROOT = Path(__file__).resolve().parents[2]
STAGE = Path(__file__).resolve().parent
PHONES = dict(zip(
    'aa ae ah ao aw ay b ch d dh eh er ey f g hh ih iy jh k l m n ng ow oy p r s sh t th uh uw v w y z zh'.split(),
    'ɑ æ ə ɔ aʊ aɪ b tʃ d ð ɛ ɚ eɪ f ɡ h ɪ i dʒ k l m n ŋ oʊ ɔɪ p r s ʃ t θ ʊ u v w j z ʒ'.split()))
sys.path.insert(0, str(ROOT / 'scripts'))
from validate_extension_batch import load_prior_keys
prior = load_prior_keys(ROOT / 'lookup/used_keys_current.zlib.b64', ROOT / 'DictionaryExtensionBatches', 68)
overrides = json.loads((STAGE / 'pronunciation_overrides.json').read_text(encoding='utf-8')) if (STAGE / 'pronunciation_overrides.json').exists() else {}
for p in sorted((STAGE / 'ipa').glob('part_*.tsv')):
    for line in p.read_text(encoding='utf-8').splitlines():
        if line.strip():
            word, ipa = line.split('\t')
            assert word not in overrides, word
            overrides[word] = ipa
form_overrides = json.loads((STAGE / 'form_overrides.json').read_text(encoding='utf-8')) if (STAGE / 'form_overrides.json').exists() else {}
meaning_overrides = json.loads((STAGE / 'meanings_overrides.json').read_text(encoding='utf-8')) if (STAGE / 'meanings_overrides.json').exists() else {}
CMU = cmudict.dict()

def pronunciation(word):
    if word in overrides:
        return overrides[word]
    original = ' '.join(CMU[word][0]).lower() if word in CMU else get_cmu([word])[0][0]
    if original.startswith('__IGNORE__'):
        return None
    marked = find_stress(original).split()
    tokens = original.split()
    assert len(marked) == len(tokens), (word, original, marked)
    out = ''
    for raw, placed in zip(tokens, marked):
        name = re.sub('[0-9]', '', raw)
        mark = placed[0] if placed[0] in 'ˈˌ' else ''
        ipa = PHONES[name]
        if name == 'ah' and raw[-1] in '12':
            ipa = 'ʌ'
        if name == 'er' and raw[-1] in '12':
            ipa = 'ɝ'
        out += mark + ipa
    return '/' + out + '/'

authored = []
for p in sorted((STAGE / 'translations').glob('part_*.tsv')):
    for line in p.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        word, pos, glosses = line.split('\t')
        authored.append((word, pos, glosses.split('|')))
heads = {r[0] for r in authored}
assert len(heads) == len(authored)
entries = []
missing = []
form_review = []
owned = set(prior) | heads
for word, pos, glosses in authored:
    assert word not in prior, word
    ipa = pronunciation(word)
    if ipa is None:
        missing.append(word)
        ipa = '/REVIEW/'
    forms = []
    suggestions = []
    meanings = meaning_overrides.get(word, [{'partOfSpeech': pos, 'burmese': glosses}])
    if word in form_overrides:
        suggestions = form_overrides[word]
    elif any(m['partOfSpeech'] == 'verb' for m in meanings):
        for tag in ['VBZ', 'VBD', 'VBN', 'VBG']:
            suggestions.extend(getInflection(word, tag=tag) or ())
    elif pos == 'noun':
        # Noun plurals are opt-in through the manually reviewed override file.
        suggestions = []
    for f in suggestions:
        if f != word and f not in owned and f not in forms:
            assert re.fullmatch('[a-z]+', f), (word, f)
            forms.append(f)
            owned.add(f)
    if any(m['partOfSpeech'] == 'verb' for m in meanings) or word in form_overrides:
        form_review.append({'word': word, 'suggestions': list(dict.fromkeys(suggestions)), 'stored': forms, 'excluded': list(dict.fromkeys(f for f in suggestions if f not in forms))})
    entries.append({'word': word, 'pronunciation': ipa, 'forms': forms, 'meanings': meanings})
(STAGE / 'assembled_preview.json').write_text(json.dumps({'version': 1, 'batch': 68, 'entries': entries}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
(STAGE / 'forms_review.json').write_text(json.dumps(form_review, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'entries': len(entries), 'missingPronunciations': missing, 'storedForms': sum(len(e['forms']) for e in entries), 'glosses': sum(len(m['burmese']) for e in entries for m in e['meanings'])}, indent=2))
if len(entries) == 500 and not missing:
    target = ROOT / 'DictionaryExtensionBatches/dictionary_batch_068.json'
    target.write_text(json.dumps({'version': 1, 'batch': 68, 'entries': entries}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
