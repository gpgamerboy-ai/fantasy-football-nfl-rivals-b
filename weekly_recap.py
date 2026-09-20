#!/usr/bin/env python3
"""weekly_recap.py — Auto-generate weekly recap from Sleeper."""
import json, urllib.request, sys
from pathlib import Path

LEAGUES = {
    "A": {
        "id": "1402026831841861632",
        "name": "NFL Rivals A",
        "dir": str(Path.home() / "Downloads/rivals-a-v2"),
        "owners": {
            "BMX58":"Steelers","mucci22":"Bengals","loorich":"Lions",
            "VicArthur7":"Vikings","LilTissa":"Eagles","Mikemooch2323":"Giants",
            "Mikestev7":"Seahawks","kidrich44":"Cardinals",
        },
    },
    "B": {
        "id": "1403986787751174144",
        "name": "NFL Rivals B",
        "dir": str(Path.home() / "Downloads/rivals-b-v2"),
        "owners": {
            "loorich":"Ravens","passwordistaco12":"Chargers","GreenScout":"Panthers",
            "Mikemooch2323":"Broncos","spencerk42":"Falcons","kidrich44":"Chiefs",
            "peb12772":"Raiders","OldOn":"Browns",
        },
    },
}
BASE = "https://api.sleeper.app/v1"

def fetch(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.loads(r.read())

def main():
    code = (sys.argv[1].upper() if len(sys.argv) > 1 else "A")
    week = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    cfg = LEAGUES[code]
    lid = cfg["id"]
    owner_map = cfg["owners"]

    users = fetch(f"{BASE}/league/{lid}/users")
    rosters = fetch(f"{BASE}/league/{lid}/rosters")
    all_matchups = {w: fetch(f"{BASE}/league/{lid}/matchups/{w}") for w in range(1, week + 1)}

    roster_owner = {}
    for r in rosters:
        o = next((u for u in users if u["user_id"] == r["owner_id"]), None)
        if o: roster_owner[r["roster_id"]] = o["display_name"]

    def tname(rid):
        return owner_map.get(roster_owner.get(rid, ""), f"Roster {rid}")

    def pair_games(w):
        by_mid = {}
        for m in all_matchups.get(w, []):
            mid = m.get("matchup_id")
            if mid is None: continue
            by_mid.setdefault(mid, []).append(m)
        out = []
        for mid, pair in by_mid.items():
            if len(pair) != 2: continue
            a, b = pair
            out.append({
                "rid_a": a["roster_id"], "rid_b": b["roster_id"],
                "a_pts": a["points"], "b_pts": b["points"],
                "margin": abs(a["points"] - b["points"]),
                "total": a["points"] + b["points"],
            })
        return out

    def won_this_week(rid, w):
        for g in pair_games(w):
            if g["rid_a"] == rid: return g["a_pts"] > g["b_pts"]
            if g["rid_b"] == rid: return g["b_pts"] > g["a_pts"]
        return None

    def streak(rid, up_to):
        last = None; count = 0
        for w in range(up_to, 0, -1):
            r = won_this_week(rid, w)
            if r is None: break
            s = "W" if r else "L"
            if last is None: last = s; count = 1
            elif s == last: count += 1
            else: break
        return last, count

    teams = []
    for r in rosters:
        rid = r["roster_id"]; s = r.get("settings", {})
        wk_won = won_this_week(rid, week)
        wk_pts = 0
        for g in pair_games(week):
            if g["rid_a"] == rid: wk_pts = g["a_pts"]
            elif g["rid_b"] == rid: wk_pts = g["b_pts"]
        teams.append({
            "rid": rid, "name": tname(rid),
            "wins": s.get("wins", 0), "losses": s.get("losses", 0), "ties": 0 if (s.get("wins",0)+s.get("losses",0)==0) else s.get("ties", 0),
            "pf": s.get("fpts", 0) + s.get("fpts_decimal", 0)/100,
            "pa": s.get("fpts_against", 0) + s.get("fpts_against_decimal", 0)/100,
            "wk_pts": wk_pts, "wk_won": wk_won,
        })

    games = pair_games(week)
    def pretty(g):
        a_n, b_n = tname(g["rid_a"]), tname(g["rid_b"])
        if g["a_pts"] >= g["b_pts"]: w, l, ws, ls = a_n, b_n, g["a_pts"], g["b_pts"]
        else: w, l, ws, ls = b_n, a_n, g["b_pts"], g["a_pts"]
        return w, l, ws, ls, g["margin"], g["total"]

    top = max(teams, key=lambda t: t["wk_pts"])
    biggest = max(games, key=lambda g: g["margin"])
    closest = min(games, key=lambda g: g["margin"])
    highest = max(games, key=lambda g: g["total"])

    # streaks
    w_streaks = []
    broken = []
    for t in teams:
        s, n = streak(t["rid"], week)
        if s == "W" and n >= 2: w_streaks.append((t["name"], n))
        if s == "W" and n == 1 and t["losses"] > 0:
            _, prev = streak(t["rid"], week - 1)
            if prev >= 2 and won_this_week(t["rid"], week - 1) is False:
                broken.append((t["name"], prev))

    # standings
    cur_rank = {t["name"]: i+1 for i, t in enumerate(sorted(teams, key=lambda x: (-x["wins"], -x["pf"])))}
    last_sort = sorted(teams, key=lambda t: (
        -(t["wins"] - (1 if t["wk_won"] else 0)),
        -(t["pf"] - t["wk_pts"])
    ))
    prev_rank = {t["name"]: i+1 for i, t in enumerate(last_sort)}

    movers = []
    for t in teams:
        n = t["name"]
        if n in cur_rank and n in prev_rank and cur_rank[n] != prev_rank[n]:
            delta = prev_rank[n] - cur_rank[n]
            movers.append((n, prev_rank[n], cur_rank[n], delta))

    # season leaders
    best = max(teams, key=lambda t: (t["wins"], t["pf"]))
    top_off = max(teams, key=lambda t: t["pf"])
    stf_def = min(teams, key=lambda t: t["pa"])

    out = []
    out.append(f"🏈 WEEK {week} RECAP — {cfg['name']}")
    out.append("")
    out.append("🥇 TOP SCORER THIS WEEK")
    out.append(f"{top['name']} — {top['wk_pts']:.2f} pts")
    out.append("")
    w, l, ws, ls, m, tot = pretty(biggest)
    out.append("💥 BIGGEST BLOWOUT")
    out.append(f"{w} def. {l} — {ws:.2f} – {ls:.2f}")
    out.append("")
    w, l, ws, ls, m, tot = pretty(closest)
    out.append("🎯 CLOSEST GAME")
    out.append(f"{w} def. {l} — {ws:.2f} – {ls:.2f} (margin {m:.2f})")
    out.append("")
    w, l, ws, ls, m, tot = pretty(highest)
    out.append("📈 HIGHEST-SCORING GAME")
    out.append(f"{w} vs {l} — {tot:.2f} combined")
    out.append("")
    if w_streaks:
        out.append("🔥 WIN STREAK WATCH")
        for name, n in w_streaks:
            out.append(f"{name} — {n} wins in a row")
        out.append("")
    if broken:
        out.append("💔 LOSING STREAK BROKEN")
        for name, n in broken:
            out.append(f"{name} snapped a {n}-game losing streak")
        out.append("")
    out.append("📊 WEEKEND LEADERS")
    out.append(f"Most Points For: {top['name']} — {top['wk_pts']:.2f}")
    lowest = min(teams, key=lambda t: t["wk_pts"])
    out.append(f"Fewest Points For: {lowest['name']} — {lowest['wk_pts']:.2f}")
    out.append("")
    out.append(f"🏆 SEASON LEADERS (through Week {week})")
    out.append(f"Best Record: {best['name']} — {best['wins']}-{best['losses']}-{best['ties']}")
    out.append(f"Top Scoring Offense: {top_off['name']} — {top_off['pf']:.2f} total")
    out.append(f"Stingiest Defense: {stf_def['name']} — {stf_def['pa']:.2f} PA")
    out.append("")
    if movers:
        out.append("📈 STANDINGS SHAKEUP")
        for name, old, new, delta in sorted(movers, key=lambda x: -abs(x[3]))[:4]:
            arrow = "⬆️" if delta > 0 else "⬇️"
            out.append(f"{arrow} {name}: #{old} → #{new}")
        out.append("")
    out.append("— The Commissioner")
    text = "\n".join(out)

    out_path = Path(cfg["dir"]) / f"recap_week{week}.txt"
    out_path.write_text(text)
    print(text)
    print(f"\n[saved to {out_path}]")

if __name__ == "__main__":
    main()
