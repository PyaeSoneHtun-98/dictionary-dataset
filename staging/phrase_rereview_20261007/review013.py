"""Record the coordinator's complete second review of Batch 013; no runtime writes."""
import json
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
entries = json.loads((ROOT / 'PhraseExtensionBatches/phrase_batch_013.json').read_text(encoding='utf-8'))['entries']
original = {e['phrase']: e for e in entries}
changes = []

def propose(key, reason, sources=(), **fields):
    replacement = deepcopy(original[key])
    replacement.update(fields)
    changes.append({'batch': 13, 'phrase': key, 'reason': reason,
                    'sources': list(sources), 'before': original[key], 'replacement': replacement})

propose('ace in the hole', 'Cambridge explicitly treats ace up your sleeve as the same idiom. Consolidate that entry and real possessor/plural surfaces under one owner.',
        ['https://dictionary.cambridge.org/dictionary/english/ace-up-sleeve?q=ace-up-your-sleeve'],
        forms=['aces in the hole', 'ace up your sleeve', 'ace up my sleeve', 'ace up his sleeve', 'ace up her sleeve', 'ace up our sleeve', 'ace up their sleeve', 'aces up your sleeve', 'aces up my sleeve', 'aces up his sleeve', 'aces up her sleeve', 'aces up our sleeves', 'aces up their sleeves', 'ace up our sleeves', 'ace up their sleeves'],
        burmese=['လိုအပ်မှ ထုတ်သုံးမည့် အသာစီးရစရာ လျှို့ဝှက်နည်း သို့မဟုတ် အစွမ်းအစ'])
propose('ace up your sleeve', 'Replace the duplicate idiom owner with a useful, independently verified and unused expression.',
        ['https://dictionary.cambridge.org/us/dictionary/english/pet-peeve'],
        phrase='pet peeve', type='idiom', forms=['pet peeves'], burmese=['ကိုယ့်အတွက် အထူးစိတ်အနှောင့်အယှက်ဖြစ်စေသည့် အရာ'])
propose('beside the point', "The frozen entry that's beside the point already owns this expression. Do not count a shorter cosmetic variant as new.",
        ['https://dictionary.cambridge.org/us/dictionary/english/double-standard'],
        phrase='double standard', type='expression', forms=['double standards'], burmese=['တူညီသည့်ကိစ္စကို လူအလိုက် မမျှမတ စံနှစ်မျိုးထား၍ ဆက်ဆံခြင်း'])
propose('at rock bottom', 'Frozen hit rock bottom already owns this idiom; changing the verb to a state preposition must not count as a new idiom. Replace with distinct subtitle vocabulary.',
        ['https://www.collinsdictionary.com/dictionary/english/ride-shotgun'],
        phrase='ride shotgun', type='idiom', forms=['rides shotgun', 'rode shotgun', 'ridden shotgun', 'riding shotgun'], burmese=['ကားမောင်းသူဘေး ရှေ့ခုံမှာ ထိုင်လိုက်သည်'])
propose('skeleton in the closet', 'Include common plural and cupboard variants under the same owner.',
        forms=['skeletons in the closet', 'skeleton in the cupboard', 'skeletons in the cupboard'])
propose("wolf in sheep's clothing", 'Useful real irregular plural surface is missing.', forms=["wolves in sheep's clothing"])
propose('snake in the grass', 'Useful real noun plural surface is missing.', forms=['snakes in the grass'])
propose('gun down', 'Correct Burmese action spelling: ပစ်လှဲ indicates shooting someone down; ပစ်လဲ is an incorrect action construction.',
        burmese=['သေနတ်ဖြင့် ပစ်လှဲသည်'])
propose('suck up to', 'Flattering for advantage is not restricted to a workplace superior.',
        burmese=['မျက်နှာရအောင် ဖားသည်'])
propose('shrug off', 'Include the common physical shoulder movement sense as well as figurative dismissal.',
        ['https://www.oxfordlearnersdictionaries.com/us/definition/english/shrug-off'],
        burmese=['အရေးမထားဘဲ ပယ်ချသည်', 'ပခုံးတွန့်၍ ဖယ်ထုတ်သည်'])
propose('hush up', 'Include the common American keep-quiet sense as well as hiding information.',
        ['https://www.collinsdictionary.com/dictionary/english/hush-up'],
        burmese=['လူမသိအောင် ဖုံးဖိထားသည်', 'တိတ်တိတ်နေသည်'])

report = {'batch': 13, 'reviewedEntries': 250, 'reviewedForms': sum(len(e['forms']) for e in entries),
          'method': 'Every canonical, stored form and Burmese sense read; cross-owner variant comparison against all frozen and extension entries.',
          'findings': changes, 'unchangedEntries': 250-len(changes)}
(Path(__file__).parent / 'batch013_review.json').write_bytes((json.dumps(report, ensure_ascii=False, indent=2)+'\n').encode('utf-8'))
print(f'Recorded {len(changes)} actionable findings for 250 reviewed entries')
