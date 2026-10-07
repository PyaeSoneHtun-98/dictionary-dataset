"""Apply recorded review decisions after validating the complete coordinated change."""
import argparse
import hashlib
import json
import sys
from collections import Counter
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from phrase_extension_common import base_dataset, json_bytes, validate_entries

parser = argparse.ArgumentParser()
parser.add_argument('--write', action='store_true')
args = parser.parse_args()
review_dir = Path(__file__).parent
files = {n: ROOT / f'PhraseExtensionBatches/phrase_batch_{n:03}.json' for n in range(13, 17)}
batches = {n: json.loads(p.read_text(encoding='utf-8')) for n, p in files.items()}
original = {(n, e['phrase']): deepcopy(e) for n, b in batches.items() for e in b['entries']}
proposed = deepcopy(original)
records = []

def add(number, issue):
    key = (number, issue['phrase'])
    before = original[key]
    recorded_before = issue.get('before', issue.get('original', issue.get('original_entry')))
    if recorded_before is not None and recorded_before != before:
        raise ValueError(f'Review does not match source: {key}')
    after = issue.get('replacement', issue.get('replacement_entry'))
    if not isinstance(after, dict) or set(after) != {'phrase', 'type', 'forms', 'burmese'}:
        raise ValueError(f'Invalid replacement: {key}')
    for field in after:
        if after[field] == before[field]:
            continue
        if proposed[key][field] not in (before[field], after[field]):
            if field == 'forms':
                proposed[key][field] = list(dict.fromkeys(proposed[key][field] + after[field]))
                continue
            raise ValueError(f'Conflicting review decisions: {key} {field}')
        proposed[key][field] = deepcopy(after[field])
    records.append({'batch': number, 'phrase': issue['phrase'],
                    'reason': issue.get('reason', issue.get('reasons', []))})

for number in range(13, 17):
    report = json.loads((review_dir / f'batch{number:03}_review.json').read_text(encoding='utf-8'))
    for issue in report.get('findings', report.get('changes', report.get('issues', []))):
        add(number, issue)
    for issue in report.get('cross_batch_findings', []):
        add(issue['target_batch'], issue)
    for issue in report.get('earlier_extension_owner_consolidations', []):
        target = int(Path(issue['file']).stem.rsplit('_', 1)[1])
        add(target, issue)

owners, _, _ = base_dataset()
errors = validate_entries(list(proposed.values()), owners)
if errors:
    raise ValueError('\n'.join(errors))
changes = []
for key, before in original.items():
    after = proposed[key]
    if after != before:
        changes.append({'batch': key[0], 'phrase': key[1], 'before': before, 'after': after,
                        'changedFields': [field for field in after if before[field] != after[field]]})
summary = {
    'baselineCommit': '4b9b047d6b44c68c8b8a48f24821f60690f75c18',
    'reviewedEntries': 1000,
    'changedEntries': len(changes),
    'changedByBatch': dict(Counter(c['batch'] for c in changes)),
    'canonicalReplacements': sum(c['before']['phrase'] != c['after']['phrase'] for c in changes),
    'meaningChanges': sum(c['before']['burmese'] != c['after']['burmese'] for c in changes),
    'formChanges': sum(c['before']['forms'] != c['after']['forms'] for c in changes),
    'formsAdded': sum(len(set(c['after']['forms']) - set(c['before']['forms'])) for c in changes),
    'formsRemoved': sum(len(set(c['before']['forms']) - set(c['after']['forms'])) for c in changes),
    'changes': changes,
    'reviewRecords': records,
}
if args.write:
    for number, data in batches.items():
        data['entries'] = [proposed[(number, e['phrase'])] for e in data['entries']]
        assert len(data['entries']) == 250
        files[number].write_bytes(json_bytes(data))
    (review_dir / 'applied_changes.json').write_bytes(json_bytes(summary))
print(json.dumps({k: v for k, v in summary.items() if k not in {'changes', 'reviewRecords'}}))
