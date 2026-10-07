"""Assemble reviewed drafts; final batch publication is a separate reviewed step."""
import copy
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from phrase_extension_common import base_dataset, json_bytes, validate_entries

HERE = Path(__file__).resolve().parent
SOURCES = ["coordinator", "idioms", "verbs", "expressions"]
PRIORITY = """lawyer up|in the loop|run out of steam|touch base|on a roll|dead to rights|
hold a grudge|in a pinch|raise the stakes|cut the mustard|smoking gun|red herring|
elephant in the room|skeleton in the closet|wolf in sheep's clothing|snake in the grass|
ace in the hole|ace up your sleeve|black sheep|dark horse|cash cow|silver bullet|
silver lining|glass ceiling|house of cards|can of worms|bundle of nerves|couch potato|
backseat driver|wet blanket|party pooper|social butterfly|shrinking violet|tough cookie|
bad apple|good egg|sore loser|fair weather friend|foul play|dirty laundry|clean slate|
clean bill of health|clean sweep|smooth sailing|diamond in the rough|rough around the edges|
hard pill to swallow|hard feelings|soft spot|sore point|hot potato|hot seat|hot air|
hot under the collar|cold shoulder|cliff hanger|chicken out|clam up|doze off|nod off|
butt in|boot up|buckle up|brighten up|cordon off|fess up|hunker down|hush up|jot down|
rat on|rat out|string along|rough up|size up|sober up|shrug off|single out|win over|
gun down|hack into|gloss over|creep up on|map out|mop up|peter out|pig out|pipe down|
pitch in|shell out|suss out|flesh out|flush out|frown on|gear up|crank up|hash out|
spell out|weigh in on|tip off|squeal on|snitch on|on tenterhooks|under your thumb|
up the ante|at your wits' end|at the eleventh hour|at death's door|on your last legs|
on your high horse|under your wing|behind bars|up in smoke|out of this world|
under the microscope|beyond the pale|on the rebound|in your element|behind the curve|
plea bargain|search warrant|arrest warrant|probable cause|reasonable doubt|class action|
restraining order|witness protection|inside job|cover story|safe house|double agent|
black market|money laundering|conflict of interest|insider trading|red tape|blank check"""
PRIORITY = [p.strip() for p in PRIORITY.replace("\n", "").split("|")]
PRIORITY += """better half|fall guy|whipping boy|sitting duck|salt of the earth|
life of the party|heart of stone|labor of love|match made in heaven|easy mark|open book|
food for thought|pipe dream|butterflies in your stomach|raw deal|fair shake|shot in the arm|
kick in the teeth|pat on the back|slap on the wrist|stab in the back|bone of contention|
tongue in cheek|in stitches|green with envy|fit to be tied|hopping mad|tickled pink|
on top of the world|in the doghouse|in a fog|in a rut|in a pickle|all thumbs|
all heart|child's play|cheap shot|free rein|free ride|in the driver's seat|
in the crosshairs|out of your element|in the home stretch|on the rocks|on the level|
on the wagon|off the wagon|off the wall|out of the picture|dead in the water|
larger than life|just deserts|comfort food|white lie|loaded question""".replace("\n", "").split("|")
PRIORITY = [p.strip() for p in PRIORITY]


def signature(value):
    value = value.replace("’", "'")
    value = re.sub(r"\b(my|your|his|her|its|our|their)\b", "poss", value)
    if value.startswith("as ") and " as " in value[3:]:
        value = value[3:]
    value = re.sub(r"^(a|an|the) ", "", value)
    return value.replace("'", "").replace("-", " ")


def main():
    owners, _, _ = base_dataset()
    frozen_signatures = {signature(k): k for k in owners}
    signature_owners = dict(frozen_signatures)
    reviews = {}
    for source in SOURCES:
        path = HERE / (source + "_peer_review.json")
        reviews[source] = {x["phrase"]: x for x in json.loads(path.read_text(encoding="utf-8"))} if path.exists() else {}
    editorial = json.loads((HERE / "editorial_decisions.json").read_text(encoding="utf-8"))
    rejects, pool = [], []
    draft_counts = {}
    for source in SOURCES:
        data = json.loads((HERE / (source + ".json")).read_text(encoding="utf-8"))
        draft_counts[source] = len(data)
        for original in data:
            entry = copy.deepcopy(original)
            phrase = entry["phrase"]
            decision = editorial.get(phrase) or reviews[source].get(phrase)
            if decision and decision["action"] == "reject":
                rejects.append({"source": source, "phrase": phrase, "reason": decision["reason"]})
                continue
            if decision and decision["action"] == "replace":
                entry = copy.deepcopy(decision["replacement"])
            sig = signature(entry["phrase"])
            if sig in signature_owners:
                rejects.append({"source": source, "phrase": phrase,
                                "reason": "Equivalent article/possessor/simile surface or duplicate draft",
                                "owner": signature_owners[sig]})
                continue
            trial = dict(owners)
            errors = validate_entries([entry], trial)
            if errors:
                rejects.append({"source": source, "phrase": phrase, "reason": "Lookup/schema conflict", "errors": errors})
                continue
            owners = trial
            for surface in [entry["phrase"], *entry["forms"]]:
                signature_owners[signature(surface)] = entry["phrase"]
            pool.append({"source": source, "entry": entry})
    by_phrase = {x["entry"]["phrase"]: x for x in pool}
    chosen = []
    used = set()
    def add(item):
        phrase = item["entry"]["phrase"]
        if phrase not in used:
            chosen.append(item)
            used.add(phrase)
    for phrase in PRIORITY:
        if phrase in by_phrase:
            add(by_phrase[phrase])
    # Curate an idiom-heavy collection while retaining practical verbs and fixed expressions.
    # The quotas are ceilings used to choose among the reviewed pool, not padding targets.
    for typ, ceiling in [("idiom", 600), ("phrasal_verb", 260)]:
        for item in pool:
            if Counter(x["entry"]["type"] for x in chosen)[typ] >= ceiling:
                break
            if item["entry"]["type"] == typ:
                add(item)
    for item in pool:
        if len(chosen) >= 1000:
            break
        if item["entry"]["type"] == "expression":
            add(item)
    if len(chosen) < 1000:
        for item in pool:
            if len(chosen) >= 1000:
                break
            add(item)
    if len(chosen) != 1000:
        raise ValueError(f"Need exactly 1,000 selected entries; have {len(chosen)} from {len(pool)}")
    entries = [x["entry"] for x in chosen]
    errors = validate_entries(entries, base_dataset()[0])
    if errors:
        raise ValueError("\n".join(errors))
    stats = {
        "draftCounts": draft_counts, "rawDraftEntries": sum(draft_counts.values()),
        "eligibleUniqueEntries": len(pool), "selectedEntries": len(chosen),
        "selectedTypeCounts": dict(Counter(e["type"] for e in entries)),
        "selectedSourceCounts": dict(Counter(x["source"] for x in chosen)),
        "selectedForms": sum(len(e["forms"]) for e in entries),
        "selectedMeanings": sum(len(e["burmese"]) for e in entries),
        "selectedOwnership": [{"phrase": x["entry"]["phrase"], "source": x["source"]} for x in chosen],
        "rejections": rejects,
        "unpublishedEligiblePhrases": [x["entry"]["phrase"] for x in pool if x["entry"]["phrase"] not in used],
    }
    (HERE / "selected_entries.json").write_bytes(json_bytes(entries))
    (HERE / "selection_audit.json").write_bytes(json_bytes(stats))
    print(json.dumps({k: v for k, v in stats.items() if k not in {"selectedOwnership", "rejections", "unpublishedEligiblePhrases"}}, indent=2))


if __name__ == "__main__":
    main()
