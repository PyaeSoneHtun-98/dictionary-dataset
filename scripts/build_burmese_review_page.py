"""Build a self-contained, offline human review page; never modify dataset assets."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
artifact = ROOT / 'dist/phrases_extension.json'
raw = artifact.read_text(encoding='utf-8').encode('utf-8')
digest = hashlib.sha256(raw).hexdigest()
metadata = json.loads((ROOT / 'dist/phrases_extension.metadata.json').read_text(encoding='utf-8'))
if digest != metadata['sha256']:
    raise ValueError('Artifact metadata hash mismatch')
entries = json.loads(raw)['entries']
batch_by_phrase = {}
for path in sorted((ROOT / 'PhraseExtensionBatches').glob('phrase_batch_*.json')):
    batch = json.loads(path.read_text(encoding='utf-8'))
    batch_by_phrase.update({e['phrase']: batch['batch'] for e in batch['entries']})
history = json.loads((ROOT / 'staging/phrase_rereview_20261007/applied_changes.json').read_text(encoding='utf-8'))
changed = {c['after']['phrase']: c for c in history['changes']}
data = {'artifactSha256': digest, 'entries': [{**e, 'batch': batch_by_phrase[e['phrase']],
        'revised': e['phrase'] in changed,
        'before': changed[e['phrase']]['before'] if e['phrase'] in changed else None} for e in entries]}
payload = json.dumps(data, ensure_ascii=False).replace('<', '\\u003c')
template = ROOT / 'scripts/burmese_review_page.html'
output = ROOT / 'reports/burmese_manual_review.html'
page = template.read_text(encoding='utf-8').replace('__REVIEW_DATA__', payload)
page = page.replace('__ENTRY_COUNT__', f'{len(entries):,}').replace('__REVISED_COUNT__', str(len(changed)))
output.write_bytes(page.encode('utf-8'))
print(f'Built {output.name}: {len(entries)} entries, {len(changed)} revised; no dataset changes')
