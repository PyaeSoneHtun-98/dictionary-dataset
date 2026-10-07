"""Install already-reviewed sources after validating every complete batch."""
import hashlib,json,subprocess,sys
from pathlib import Path
P=Path(__file__).resolve().parent
R=P.parents[1]
sys.stdout.reconfigure(encoding='utf-8')
manifest=json.loads((R/'dictionary_extension_manifest.json').read_text(encoding='utf-8'))
assert manifest['latestBatch']==73 and manifest['nextBatch']==74
sources=[P/'validated_batches'/f'dictionary_batch_{n:03d}.json' for n in range(74,81)]
assert all(not (R/'DictionaryExtensionBatches'/p.name).exists() for p in sources)
records=[]
for source in sources:
    cmd=[sys.executable,str(R/'scripts/validate_extension_batch.py'),str(source),'--expected-batch',str(json.loads(source.read_text(encoding='utf-8'))['batch']),'--base-lookup',str(R/'extension_lookup/used_keys_current.zlib.b64'),'--batches-dir',str(P/'validated_batches'),'--closed-compound-allowlist',str(P/'reviewed_closed_compound_allowlist.txt')]
    run=subprocess.run(cmd,cwd=R,capture_output=True,text=True,encoding='utf-8')
    records.append({'file':source.name,'exitCode':run.returncode,'output':run.stdout.strip(),'sha256Utf8Lf':hashlib.sha256(source.read_text(encoding='utf-8').encode()).hexdigest()})
    assert run.returncode==0,run.stdout+run.stderr
(P/'validation_results.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')
old_allow=(R/'extension_closed_compound_allowlist.txt').read_text(encoding='utf-8').rstrip()
new_allow=(P/'reviewed_closed_compound_allowlist.txt').read_text(encoding='utf-8')
assert new_allow.startswith(old_allow+'\n')
if '--write' in sys.argv:
    for source in sources:(R/'DictionaryExtensionBatches'/source.name).write_bytes(source.read_bytes())
    (R/'extension_closed_compound_allowlist.txt').write_text(new_allow,encoding='utf-8')
    print('Installed reviewed batches 074-080 and verified spelling review records.')
else:print('Validated seven batches; pass --write to install.')
