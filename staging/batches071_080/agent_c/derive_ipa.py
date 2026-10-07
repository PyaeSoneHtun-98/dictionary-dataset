import runpy,json,re
from pathlib import Path
s=Path(__file__).parent
a=runpy.run_path(str(s/'assemble.py'))
ipa=a['ipa'];cmu=a['CMU'];selected=set((s/'selected_words.txt').read_text().split());derived=[];missing=[]
for word,code,pos,glosses,explicit in a['rows']:
    if word not in selected or ipa(word):continue
    candidates=[]
    if word.endswith('ly'):
        root=word[:-2];candidates+=[(root,'li')]
        if root.endswith('i'):candidates+=[(root[:-1]+'y','li')]
        if word.endswith('ally'):candidates+=[(word[:-4]+'al','li')]
    if word.startswith('un'):candidates+=[(word[2:],'','ʌn')]
    if word.endswith('ness'):
        root=word[:-4];candidates+=[(root,'nəs')]
        if root.endswith('i'):candidates+=[(root[:-1]+'y','nəs')]
    if word.endswith('less'):candidates+=[(word[:-4],'ləs')]
    if word.endswith('ish'):candidates+=[(word[:-3],'ɪʃ')]
    found=False
    for spec in candidates:
        root,suffix=spec[:2];prefix=spec[2]if len(spec)>2 else''
        if root in cmu:
            ip='/'+prefix+ipa(root)[1:-1]+suffix+'/'
            derived.append((word,ip,root));found=True;break
    if not found:missing.append(word)
(s/'derived_review.txt').write_text('\n'.join(w+'|'+p+'|'+r for w,p,r in derived)+'\n',encoding='utf8')
(s/'missing_selected.txt').write_text(' '.join(missing),encoding='utf8')
print('DERIVED',len(derived));print('\n'.join(w+' '+p+' <- '+r for w,p,r in derived));print('MISSING',len(missing));print(' '.join(missing))
