"""Commit pronunciation derivatives after manual phonetic/stress review."""
import json
from pathlib import Path
s=Path(__file__).parent
fixes={
 'shirtless':'/ˈʃɝtləs/', 'tingly':'/ˈtɪŋɡli/', 'unsub':'/ˈʌnsʌb/',
 'piggish':'/ˈpɪɡɪʃ/', 'spangly':'/ˈspæŋɡli/', 'superfluously':'/suˈpɝfluəsli/',
 'spherically':'/ˈsfɛrɪkəli/', 'sweepingly':'/ˈswipɪŋli/', 'lopsidedly':'/ˌlɑpˈsaɪdɪdli/',
 'disadvantageously':'/ˌdɪsədvænˈteɪdʒəsli/', 'inconsequentially':'/ˌɪnkɑnsəˈkwɛnʃəli/',
 'thriftily':'/ˈθrɪftəli/', 'abstractedly':'/əbˈstræktɪdli/',
 'ebulliently':'/ɪˈbʊljəntli/', 'lukewarmly':'/ˌlukˈwɔrmli/',
 'quaveringly':'/ˈkweɪvɚɪŋli/', 'slanderously':'/ˈslændɚəsli/',
 'speechlessly':'/ˈspitʃləsli/', 'straightforwardness':'/ˌstreɪtˈfɔrwɚdnəs/',
 'uncleanness':'/ʌnˈklinnəs/', 'manipulatively':'/məˈnɪpjələtɪvli/',
 'servilely':'/ˈsɝvəli/', 'greasily':'/ˈɡrisəli/', 'pruriently':'/ˈprʊriəntli/',
 'unseeing':'/ʌnˈsiɪŋ/', 'unframed':'/ʌnˈfreɪmd/', 'unpowered':'/ʌnˈpaʊɚd/',
 'untucked':'/ʌnˈtʌkt/', 'untagged':'/ʌnˈtæɡd/', 'untrimmed':'/ʌnˈtrɪmd/',
 'unhealed':'/ʌnˈhild/', 'unshared':'/ʌnˈʃɛrd/', 'unpressed':'/ʌnˈprɛst/',
}
accepted=[];review=[]
for line in (s/'derived_review.txt').read_text(encoding='utf8').splitlines():
    word,pronunciation,root=line.split('|')
    corrected=fixes.get(word,pronunciation.replace('əlli','əli'))
    if 'ˈ'not in corrected:corrected='/ˈ'+corrected[1:]
    accepted.append(word+'|'+corrected)
    review.append(dict(word=word,resource='CMU parent lemma plus regular suffix/prefix; manually reviewed',parentLemma=root,proposed=pronunciation,reviewed=corrected))
(s/'ipa_derived.txt').write_text('\n'.join(accepted)+'\n',encoding='utf8')
(s/'derived_ipa_review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
