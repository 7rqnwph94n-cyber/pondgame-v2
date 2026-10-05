"""Replay the 2026-10-04 human opening (no Autoplay) through the bridge:  python3 tools/replay_human_opening.py <until_second> [overlay] [plan]"""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from economy.bridge import Session, handle
PLAN = json.load(open(ROOT / (sys.argv[3] if len(sys.argv) > 3 else 'docs/milestone_b/human_opening_2026-10-04.plan.json')))   # [[second, cmd], ...]
until = int(sys.argv[1])
overlay = sys.argv[2] if len(sys.argv) > 2 else 'economy/data/experiments/candidate_playable_v1.json'   # the plan was recorded on this package
s = Session([str(ROOT / overlay)])
log = []
t = 1
for at, cmd in PLAN + [[until, None]]:
    while at > t:
        step = min(600, at - t)
        handle(s, {"id": 0, "op": "advance", "seconds": step}); t += step
    if cmd:
        r = handle(s, {"id": 0, "op": "command", "cmd": cmd})
        log.append(f"{at//60:02d}:{at%60:02d} {cmd['do']} {cmd.get('building') or cmd.get('target') or cmd.get('residence','')} -> {'ok' if r['ok'] else r['reasons']}")
v = handle(s, {"id": 0, "op": "view"})["view"]
print("\n".join(log))
print(f"== {v['time']} {v['season']} (next {v['next_season']} in {v['seconds_to_next_season']//60}m) pop {v['population']} food {v['food_minutes'] and round(v['food_minutes'],1)} builders {v['builders']} upkeep {v['maintenance_upkeep']}")
print("store", {k: x for k, x in sorted(v['store'].items()) if x})
wf = {c: {k: round(x, 1) for k, x in d.items()} for c, d in v['workforce'].items() if d['supply'] or d['demand']}
print("workforce", wf)
for fid, f in v['facilities'].items():
    if f['blockers'] or f['status'] != 'running':
        print(" F", fid, f['status'], f"prio {f['labour_priority']}", [b['text'] for b in f['blockers']])
for sid, x in v['sites'].items():
    print(" S", sid, x['state'], x['progress'], [b['text'] for b in x['blockers']])
for rid, r in v['residences'].items():
    print(" R", rid, r['tier'], r['condition'], r['population'], [b['text'] for b in r['blockers']][:3])
print("events", v['events'][-6:] if False else [e for e in s.sim.events if not e.startswith('00:00')][-8:])
