#!/usr/bin/env python3
"""update_playoffs.py — Advance the bracket after each playoff week."""
import json, urllib.request, sys, importlib.util
from pathlib import Path

LEAGUES = {
    "A": {"id":"1402026831841861632","name":"NFL Rivals A",
          "dir":str(Path.home()/"Downloads/rivals-a-v2")},
    "B": {"id":"1403986787751174144","name":"NFL Rivals B",
          "dir":str(Path.home()/"Downloads/rivals-b-v2")},
}
BASE = "https://api.sleeper.app/v1"

def fetch(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.loads(r.read())

def main():
    code = (sys.argv[1].upper() if len(sys.argv) > 1 else "A")
    week = int(sys.argv[2]) if len(sys.argv) > 2 else 15
    cfg = LEAGUES[code]
    lid = cfg["id"]
    dir_p = Path(cfg["dir"])

    state_path = dir_p / "playoff_state.json"
    if not state_path.exists():
        print("ERROR: playoff_state.json not found. Run seed_playoffs.py first.")
        return
    state = json.loads(state_path.read_text())
    seeds = state["seeds"]

    week_data = fetch(BASE + "/league/" + lid + "/matchups/" + str(week))
    scores = {}
    for m in week_data:
        scores[m["roster_id"]] = m.get("points", 0)

    def score(seed):
        rid = seeds[seed]["roster_id"]
        return scores.get(rid, 0.0)

    if week == 15:
        rounds = [("round1","A","1","8"), ("round1","B","4","5"),
                  ("round1","C","2","7"), ("round1","D","3","6")]
    elif week == 16:
        r1 = state["round1"]
        rounds = [("round2","E", r1["A"]["winner"], r1["B"]["winner"]),
                  ("round2","F", r1["C"]["winner"], r1["D"]["winner"])]
    elif week in (17, 18):
        r2 = state["round2"]
        rounds = [("championship","G", r2["E"]["winner"], r2["F"]["winner"])]
    else:
        print("Playoffs run Weeks 15-18.")
        return

    for rnd, key, sa, sb in rounds:
        a = score(sa); b = score(sb)
        state.setdefault(rnd, {})[key] = {
            "seed_a": sa, "seed_b": sb,
            "scores": {sa: a, sb: b},
            "winner": sa if a >= b else sb,
            "loser": sb if a >= b else sa,
        }

    state_path.write_text(json.dumps(state, indent=2))
    print("Updated state for week " + str(week))

    spec = importlib.util.spec_from_file_location("seed_playoffs", dir_p / "seed_playoffs.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.build_html({"id": lid, "name": cfg["name"], "dir": str(dir_p)}, state)

if __name__ == "__main__":
    main()
