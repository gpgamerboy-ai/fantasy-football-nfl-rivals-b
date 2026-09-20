#!/usr/bin/env python3
"""seed_playoffs.py — Seed the playoff bracket after NFL Week 14."""
import json, urllib.request, sys
from pathlib import Path

LEAGUES = {
    "A": {
        "id": "1402026831841861632", "name": "NFL Rivals A",
        "dir": str(Path.home() / "Downloads/rivals-a-v2"),
        "owners": {"BMX58":"steelers","mucci22":"bengals","loorich":"lions",
                   "VicArthur7":"vikings","LilTissa":"eagles","Mikemooch2323":"giants",
                   "Mikestev7":"seahawks","kidrich44":"cardinals"},
        "display": {"steelers":"Steelers","bengals":"Bengals","lions":"Lions",
                    "vikings":"Vikings","eagles":"Eagles","giants":"Giants",
                    "seahawks":"Seahawks","cardinals":"Cardinals"},
    },
    "B": {
        "id": "1403986787751174144", "name": "NFL Rivals B",
        "dir": str(Path.home() / "Downloads/rivals-b-v2"),
        "owners": {"loorich":"ravens","passwordistaco12":"chargers","GreenScout":"panthers",
                   "Mikemooch2323":"broncos","spencerk42":"falcons","kidrich44":"chiefs",
                   "peb12772":"raiders","OldOn":"browns"},
        "display": {"ravens":"Ravens","chargers":"Chargers","panthers":"Panthers",
                    "broncos":"Broncos","falcons":"Falcons","chiefs":"Chiefs",
                    "raiders":"Raiders","browns":"Browns"},
    },
}
BASE = "https://api.sleeper.app/v1"

LOGO_MAP = {
    "steelers":"pittsburgh-steelers-logo.png","bengals":"cincinnati-bengals-logo.png",
    "lions":"detroit-lions-logo.png","vikings":"minnesota-vikings-logo.png",
    "eagles":"philadelphia-eagles-logo.png","giants":"new-york-giants-logo.png",
    "seahawks":"seattle-seahawks-logo.png","cardinals":"arizona-cardinals-logo.png",
    "ravens":"baltimore-ravens-logo.png","browns":"cleveland-browns-logo.png",
    "raiders":"oakland-raiders-logo.png","chargers":"los-angeles-chargers-logo.png",
    "broncos":"denver-broncos-logo.png","chiefs":"kansas-city-chiefs-logo.png",
    "falcons":"atlanta-falcons-logo.png","panthers":"carolina-panthers-logo.png",
}

def nfl_logo(folder):
    return LOGO_MAP.get(folder, "NFL-Shield.jpg")

def fetch(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.loads(r.read())

def team_card(seed_str, seeds):
    t = seeds.get(seed_str)
    if not t:
        return ('<div class="team"><span class="seed-badge">' + seed_str +
                '</span><img src="logos/NFL-Shield.jpg" alt=""><div class="info">' +
                '<div class="name">TBD</div></div></div>')
    return ('<div class="team"><span class="seed-badge">' + seed_str + '</span>'
            '<img src="logos/' + nfl_logo(t["folder"]) + '" alt="">'
            '<div class="info"><div class="name">' + t["display"] + '</div>'
            '<div class="record">' + str(t["wins"]) + '-' + str(t["losses"]) + '-' + str(t["ties"]) +
            ' &middot; ' + format(t["pf"], ".1f") + ' avg</div></div></div>')

def scored_team_card(seed_str, score, is_winner, seeds):
    t = seeds.get(seed_str)
    if not t: return ""
    cls = "team winner" if is_winner else "team loser"
    return ('<div class="' + cls + '"><span class="seed-badge">' + seed_str + '</span>'
            '<img src="logos/' + nfl_logo(t["folder"]) + '" alt="">'
            '<div class="info"><div class="name">' + t["display"] + '</div></div>'
            '<div class="score">' + format(score, ".1f") + '</div></div>')

def build_html(cfg, state):
    seeds = state["seeds"]
    r1 = state.get("round1", {})
    r2 = state.get("round2", {})

    def r1_matchup(key, sa, sb):
        m = r1.get(key)
        if m:
            a_win = m["scores"][sa] >= m["scores"][sb]
            return ('<div class="matchup">'
                    + scored_team_card(sa, m["scores"][sa], a_win, seeds)
                    + scored_team_card(sb, m["scores"][sb], not a_win, seeds)
                    + '</div>')
        return '<div class="matchup">' + team_card(sa, seeds) + team_card(sb, seeds) + '</div>'

    def r2_matchup(key, sa, sb):
        m = r2.get(key)
        if m:
            a_win = m["scores"][sa] >= m["scores"][sb]
            return ('<div class="matchup">'
                    + scored_team_card(sa, m["scores"][sa], a_win, seeds)
                    + scored_team_card(sb, m["scores"][sb], not a_win, seeds)
                    + '</div>')
        sa_d = sa if sa else "--"
        sb_d = sb if sb else "--"
        return ('<div class="matchup">'
                '<div class="team"><span class="seed-badge">' + sa_d +
                '</span><img src="logos/NFL-Shield.jpg" alt=""><div class="info"><div class="name">TBD</div></div></div>'
                '<div class="team"><span class="seed-badge">' + sb_d +
                '</span><img src="logos/NFL-Shield.jpg" alt=""><div class="info"><div class="name">TBD</div></div></div>'
                '</div>')

    r1_a_winner = r1.get("A", {}).get("winner", "")
    r1_b_winner = r1.get("B", {}).get("winner", "")
    r1_c_winner = r1.get("C", {}).get("winner", "")
    r1_d_winner = r1.get("D", {}).get("winner", "")
    r2_e_winner = r2.get("E", {}).get("winner", "")
    r2_f_winner = r2.get("F", {}).get("winner", "")

    css = """
    :root{--bg:#F5F6F8;--card:#FFF;--border:#E5E7EB;--navy:#0B2265;--red:#C8102E;--text:#1A1A1A;--mid:#4B5563;--light:#9CA3AF;--shadow:0 1px 3px rgba(0,0,0,0.06),0 4px 12px rgba(0,0,0,0.04);}
    *{box-sizing:border-box;}
    body{margin:0;background:var(--bg);color:var(--text);font-family:'Inter',Arial,sans-serif;padding:30px 20px 60px;}
    .page{max-width:1560px;margin:0 auto;}
    .back{display:inline-block;padding:10px 18px;background:var(--navy);color:#fff;text-decoration:none;border-radius:6px;font-weight:600;font-size:14px;margin-bottom:26px;}
    header{text-align:center;margin-bottom:36px;}
    header h1{font-family:'Oswald',Arial,sans-serif;font-size:clamp(32px,4vw,46px);color:var(--navy);margin:0 0 10px;}
    header .accent{width:80px;height:4px;background:var(--red);margin:0 auto 12px;}
    header p{color:var(--mid);font-size:16px;margin:0;font-style:italic;}
    .bracket{display:flex;gap:22px;justify-content:center;align-items:flex-start;flex-wrap:wrap;}
    .round{display:flex;flex-direction:column;gap:20px;min-width:320px;flex:1 1 320px;max-width:400px;}
    .round h2{font-family:'Oswald',Arial,sans-serif;font-size:14px;color:var(--navy);text-align:center;text-transform:uppercase;letter-spacing:0.15em;margin:0 0 2px;padding-bottom:8px;border-bottom:2px solid var(--red);}
    .week-tag{text-align:center;color:var(--light);font-size:12px;margin-bottom:6px;letter-spacing:0.06em;}
    .matchup{background:var(--card);border-radius:10px;border:1px solid var(--border);box-shadow:var(--shadow);padding:14px;display:flex;flex-direction:column;gap:10px;}
    .team{display:flex;align-items:center;gap:12px;padding:10px 12px;border-radius:8px;background:#FAFAFB;}
    .team img{height:56px;width:56px;object-fit:contain;}
    .team .seed-badge{width:32px;height:32px;border-radius:50%;background:var(--red);color:#fff;display:flex;align-items:center;justify-content:center;font-family:'Oswald',Arial,sans-serif;font-weight:700;font-size:16px;flex-shrink:0;}
    .team .info{flex:1;}
    .team .name{font-family:'Oswald',Arial,sans-serif;font-size:16px;font-weight:600;color:var(--navy);}
    .team .record{font-size:11.5px;color:var(--light);margin-top:2px;}
    .team .score{font-family:'Oswald',Arial,sans-serif;font-size:24px;font-weight:700;color:var(--navy);}
    .team.winner{background:linear-gradient(90deg,rgba(11,34,101,0.06),rgba(11,34,101,0.02));border-left:4px solid var(--red);}
    .team.winner .score{color:var(--red);}
    .team.loser{opacity:0.55;}
    .champion-card{background:var(--card);border-radius:12px;border:2px dashed var(--border);padding:24px;text-align:center;box-shadow:var(--shadow);}
    .champion-card .trophy{font-size:52px;margin-bottom:8px;opacity:0.35;}
    .champion-card .label{font-family:'Oswald',Arial,sans-serif;color:var(--navy);font-size:14px;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:10px;opacity:0.7;}
    .champion-card .placeholder{color:var(--light);font-size:13px;font-style:italic;}
    """

    html = (
        '<!DOCTYPE html>\n<html lang="en"><head><meta charset="UTF-8"><title>' + cfg["name"] +
        ' &mdash; Playoffs</title>\n'
        '<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">\n'
        '<style>' + css + '</style></head><body>\n'
        '<div class="page">\n'
        '<a href="index.html" class="back">&larr; Back to League Home</a>\n'
        '<header><h1>&#127942; ' + cfg["name"] + ' &mdash; Playoff Bracket</h1><div class="accent"></div>'
        '<p>Four rounds. One trophy. Weeks 15&ndash;18.</p></header>\n'
        '<div class="bracket">\n'
        '<div class="round"><h2>Round 1</h2><div class="week-tag">NFL Week 15</div>\n'
        + r1_matchup("A", "1", "8") +
        r1_matchup("B", "4", "5") +
        r1_matchup("C", "2", "7") +
        r1_matchup("D", "3", "6") +
        '</div>\n'
        '<div class="round"><h2>Round 2</h2><div class="week-tag">NFL Week 16</div>\n'
        + r2_matchup("E", r1_a_winner, r1_b_winner) +
        r2_matchup("F", r1_c_winner, r1_d_winner) +
        '</div>\n'
        '<div class="round"><h2>Championship</h2><div class="week-tag">NFL Weeks 17 &amp; 18</div>\n'
        + r2_matchup("G", r2_e_winner, r2_f_winner) +
        '</div>\n'
        '<div class="round"><h2>Champion</h2><div class="week-tag">&nbsp;</div>\n'
        '<div class="champion-card"><div class="trophy">&#127942;</div><div class="label">League Champion</div>'
        '<div class="placeholder">Crowned after Week 18</div></div>\n'
        '</div>\n</div></div></body></html>'
    )
    out = Path(cfg["dir"]) / "playoffs.html"
    out.write_text(html)
    print("Wrote: " + str(out))

def main():
    code = (sys.argv[1].upper() if len(sys.argv) > 1 else "A")
    cfg = LEAGUES[code]
    lid = cfg["id"]
    users = fetch(BASE + "/league/" + lid + "/users")
    rosters = fetch(BASE + "/league/" + lid + "/rosters")

    owner_by_rid = {}
    for r in rosters:
        o = next((u for u in users if u["user_id"] == r["owner_id"]), None)
        if o: owner_by_rid[r["roster_id"]] = o["display_name"]

    teams = []
    for r in rosters:
        rid = r["roster_id"]
        s = r.get("settings", {})
        owner = owner_by_rid.get(rid, "")
        folder = cfg["owners"].get(owner)
        if not folder: continue
        wins = s.get("wins", 0); losses = s.get("losses", 0); ties = s.get("ties", 0)
        if wins + losses == 0: ties = 0
        teams.append({
            "roster_id": rid, "folder": folder,
            "display": cfg["display"].get(folder, folder.title()),
            "wins": wins, "losses": losses, "ties": ties,
            "pf": s.get("fpts", 0) + s.get("fpts_decimal", 0) / 100,
            "pa": s.get("fpts_against", 0) + s.get("fpts_against_decimal", 0) / 100,
        })
    teams.sort(key=lambda t: (-t["wins"], -t["pf"]))

    seeds = {}
    for i, t in enumerate(teams[:8], 1):
        seeds[str(i)] = t

    state = {"league": code, "league_name": cfg["name"], "seeds": seeds,
             "round1": {}, "round2": {}, "championship": {}}
    state_path = Path(cfg["dir"]) / "playoff_state.json"
    state_path.write_text(json.dumps(state, indent=2))
    print("Seeds written to " + str(state_path))
    for i in range(1, 9):
        t = seeds[str(i)]
        print("  " + str(i) + ". " + t["display"].ljust(12) + " " +
              str(t["wins"]) + "-" + str(t["losses"]) + "-" + str(t["ties"]) +
              "  PF:" + format(t["pf"], ".2f"))

    build_html(cfg, state)

if __name__ == "__main__":
    main()
