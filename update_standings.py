#!/usr/bin/env python3
"""Fetch Sleeper standings and regenerate teams.html (light theme)."""
import json, urllib.request
from pathlib import Path

LEAGUE_ID = '1403986787751174144'
LEAGUE_NAME = 'NFL Rivals B'
OWNER_TO_FOLDER = {'loorich': 'ravens', 'passwordistaco12': 'chargers', 'GreenScout': 'panthers', 'Mikemooch2323': 'broncos', 'spencerk42': 'falcons', 'kidrich44': 'chiefs', 'peb12772': 'raiders', 'OldOn': 'browns'}
FOLDER_TO_DISPLAY = {'ravens': 'Ravens', 'chargers': 'Chargers', 'panthers': 'Panthers', 'broncos': 'Broncos', 'falcons': 'Falcons', 'chiefs': 'Chiefs', 'raiders': 'Raiders', 'browns': 'Browns'}

ROOT = Path(__file__).resolve().parent
BASE = "https://api.sleeper.app/v1"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>__NAME__ - Standings</title>
<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root{--bg:#F5F6F8;--card:#FFFFFF;--border:#E5E7EB;--navy:#0B2265;--red:#C8102E;--text:#1A1A1A;--mid:#4B5563;--shadow:0 1px 3px rgba(0,0,0,0.06),0 4px 12px rgba(0,0,0,0.04);}
*{box-sizing:border-box;}
body{margin:0;background:var(--bg);color:var(--text);font-family:'Inter',Arial,sans-serif;padding:30px 20px 60px;-webkit-font-smoothing:antialiased;}
.page{max-width:900px;margin:0 auto;}
.back{display:inline-block;padding:10px 18px;background:var(--navy);color:#fff;text-decoration:none;border-radius:6px;font-weight:600;font-size:14px;margin-bottom:26px;}
.back:hover{background:var(--red);}
header{text-align:center;margin-bottom:30px;}
header h1{font-family:'Oswald',Arial,sans-serif;font-size:clamp(28px,4vw,40px);color:var(--navy);margin:0 0 10px;letter-spacing:0.02em;}
header .accent{width:80px;height:4px;background:var(--red);margin:0 auto 12px;}
header p{color:var(--mid);font-size:15px;margin:0;font-style:italic;}
.card{background:var(--card);border-radius:10px;border:1px solid var(--border);box-shadow:var(--shadow);overflow:hidden;}
table{width:100%;border-collapse:collapse;}
thead{background:var(--navy);color:#fff;}
th{font-family:'Oswald',Arial,sans-serif;font-size:13px;text-transform:uppercase;letter-spacing:0.1em;padding:14px 16px;text-align:left;font-weight:600;}
th.num{text-align:right;width:110px;}
th.rank{width:70px;}
tbody tr{border-bottom:1px solid var(--border);}
tbody tr:last-child{border-bottom:none;}
tbody tr:hover{background:#FAFAFB;}
td{padding:14px 16px;font-size:15px;}
td.team a{color:var(--navy);text-decoration:none;font-family:'Oswald',Arial,sans-serif;font-weight:600;font-size:17px;letter-spacing:0.02em;}
td.team a:hover{color:var(--red);}
td.num{text-align:right;font-variant-numeric:tabular-nums;font-weight:600;color:var(--text);}
.badge{display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border-radius:50%;background:var(--red);color:#fff;font-family:'Oswald',Arial,sans-serif;font-weight:700;font-size:15px;}
tbody tr:nth-child(1) .badge{background:var(--navy);}
</style>
</head>
<body>
<div class="page">
<a href="index.html" class="back">&larr; Back to League Home</a>
<header>
<h1>&#127942; __NAME__ &mdash; Standings</h1>
<div class="accent"></div>
<p>Updated automatically from Sleeper.</p>
</header>
<div class="card">
<table>
<thead>
<tr><th class="rank">Rank</th><th>Team</th><th class="num">W-L-T</th><th class="num">PF</th><th class="num">PA</th></tr>
</thead>
<tbody>
__ROWS__
</tbody>
</table>
</div>
</div>
</body>
</html>
"""

def fetch(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.loads(r.read())

def get_standings():
    users = fetch(f"{BASE}/league/{LEAGUE_ID}/users")
    rosters = fetch(f"{BASE}/league/{LEAGUE_ID}/rosters")
    teams = []
    for roster in rosters:
        owner = next((u for u in users if u["user_id"] == roster["owner_id"]), None)
        if not owner: continue
        username = owner["display_name"]
        folder = OWNER_TO_FOLDER.get(username)
        if not folder:
            print(f"WARNING: no folder mapping for {username}")
            continue
        s = roster.get("settings", {})
        wins = s.get("wins", 0); losses = s.get("losses", 0); ties = s.get("ties", 0)
        if wins + losses == 0: ties = 0
        teams.append({
            "folder": folder,
            "display": FOLDER_TO_DISPLAY.get(folder, folder.title()),
            "wins": wins, "losses": losses, "ties": ties,
            "pf": s.get("fpts", 0) + s.get("fpts_decimal", 0)/100,
            "pa": s.get("fpts_against", 0) + s.get("fpts_against_decimal", 0)/100,
        })
    teams.sort(key=lambda t: (-t["wins"], -t["pf"]))
    return teams

def build_html(teams):
    rows = []
    for i, t in enumerate(teams, 1):
        wl = f"{t['wins']}-{t['losses']}-{t['ties']}"
        rows.append(
            '<tr>'
            f'<td class="rank"><span class="badge">{i}</span></td>'
            f'<td class="team"><a href="teams/{t["folder"]}/index.html">{t["display"]}</a></td>'
            f'<td class="num">{wl}</td>'
            f'<td class="num">{t["pf"]:.2f}</td>'
            f'<td class="num">{t["pa"]:.2f}</td>'
            '</tr>'
        )
    html = HTML_TEMPLATE.replace("__NAME__", LEAGUE_NAME)
    html = html.replace("__ROWS__", "\n".join(rows))
    return html

if __name__ == "__main__":
    teams = get_standings()
    (ROOT / "teams.html").write_text(build_html(teams))
    print(f"Wrote teams.html with {len(teams)} teams")
    for i, t in enumerate(teams, 1):
        print(f"  {i}. {t['display']:12s} {t['wins']}-{t['losses']}-{t['ties']}  PF:{t['pf']:.2f}  PA:{t['pa']:.2f}")
