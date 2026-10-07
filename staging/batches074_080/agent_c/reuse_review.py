"""Carry forward only individually reviewed unpublished authored reserves."""
import json
from pathlib import Path
P=Path(__file__).resolve().parent
OLD=P.parents[1]/'batches071_080'
groups={
 'Personality, interpersonal conflict and character description in dialogue and novels': 'cliquish mulish doltish conscienceless doddery technophobic coltish waggish guileful voguish rumbustious',
 'Concrete visual, physical and situational description in narrative': 'spangly starkers frolicsome ignitable phlegmy footsore colorfast unpressed',
 'Business, border and repair dialogue': 'merchantable rectifiable dutiable',
 'Narration of tone, emotion or visible action': 'dazedly captivatingly frostily gratingly lethargically wonderingly frigidly thirstily vivaciously lingeringly lopsidedly contritely ashamedly flimsily cagily hectically joylessly falteringly pluckily reservedly abstractedly affectedly banteringly brutishly clammily complainingly conceitedly daftly flashily greasily gushingly lukewarmly mincingly mirthfully murkily perplexedly pettishly pitiably quaveringly raspingly skittishly slackly stickily talkatively wheezingly',
 'Interpersonal judgment, deception and hostile speech in crime stories and novels': 'reprehensibly traitorously speciously egotistically adulterously avariciously dictatorially fishily prudishly salaciously slanderously sordidly subserviently tawdrily tritely trustfully vitriolically',
 'Common explanatory narrative about limits, outcomes and behavior': 'superfluously uncontroversially blamelessly disadvantageously inconsequentially permissively thriftily excusably manageably pardonably',
 'Novels, food and expressive dialogue': 'queerly polemically servilely poisonously detestably ebulliently scrumptiously tastily weightily',
}
selected={w:r for r,words in groups.items() for w in words.split()}
reserves=json.loads((OLD/'reserves.json').read_text(encoding='utf8'))
entries=[r['entry'] for r in reserves if r['source']=='agent_c' and r['entry']['word'] in selected]
assert {e['word'] for e in entries}==selected.keys(),selected.keys()-{e['word']for e in entries}
(P/'reviewed_reserves.json').write_text(json.dumps(entries,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(P/'reserve_editorial_review.json').write_text(json.dumps([{'word':e['word'],'source':'staging/batches071_080/agent_c independently authored unpublished reserve','decision':'retain after individual re-review','credibleMediaUse':selected[e['word']]}for e in entries],ensure_ascii=False,indent=2)+'\n',encoding='utf8')
oldlex=json.loads((OLD/'agent_c/lexical_review.json').read_text(encoding='utf8'))
(P/'reserve_lexical_review.json').write_text(json.dumps([e for e in oldlex if e['word'] in selected],ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Reviewed reserves',len(entries))
