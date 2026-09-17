#!/usr/bin/env python3
"""Fetch Sleeper standings and regenerate teams.html for NFL Rivals B."""
import json, urllib.request
from pathlib import Path

LEAGUE_ID = "1403986787751174144"
LEAGUE_NAME = "NFL Rivals B"

OWNER_TO_FOLDER = {
    "loorich": "ravens",
    "passwordistaco12": "chargers",
    "GreenScout": "panthers",
    "Mikemooch2323": "broncos",
    "spencerk42": "falcons",
    "kidrich44": "chiefs",
    "peb12772": "raiders",
    "OldOn": "browns",
}
FOLDER_TO_DISPLAY = {
    "ravens": "Ravens", "chargers": "Chargers", "panthers": "Panthers",
    "broncos": "Broncos", "falcons": "Falcons", "chiefs": "Chiefs",
    "raiders": "Raiders", "browns": "Browns",
}

ROOT = Path(__file__).resolve().parent
BASE = "https://api.sleeper.app/v1"

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
        teams.append({
            "folder": folder,
            "display": FOLDER_TO_DISPLAY.get(folder, folder.title()),
            "wins": s.get("wins", 0),
            "losses": s.get("losses", 0),
            "ties": s.get("ties", 0),
            "pf": s.get("fpts", 0) + s.get("fpts_decimal", 0) / 100,
            "pa": s.get("fpts_against", 0) + s.get("fpts_against_decimal", 0) / 100,
        })
    teams.sort(key=lambda t: (-t["wins"], -t["pf"]))
    return teams

def build_html(teams):
    rows = []
    for i, t in enumerate(teams, start=1):
        wl = f"{t['wins']}-{t['losses']}" + (f"-{t['ties']}" if t["ties"] else "")
        rows.append(
            f'<tr><td>{i}</td>'
            f'<td><a href="teams/{t["folder"]}/index.html">{t["display"]}</a></td>'
            f'<td>{wl}</td><td>{t["pf"]:.2f}</td><td>{t["pa"]:.2f}</td></tr>'
        )
    return f'''<!DOCTYPE html>
<html>
<head><title>{LEAGUE_NAME} - Standings</title>
<style>
body {{ font-family: Arial; padding: 40px; background: #0a2342; color: #fff; }}
h1 {{ color: #FB4F14; text-align: center; }}
table {{ width: 100%; max-width: 800px; margin: 20px auto; border-collapse: collapse; }}
th {{ background: #FB4F14; padding: 12px; text-align: left; }}
td {{ padding: 12px; border-bottom: 1px solid #333; }}
tr:hover {{ background: #1a3a5c; }}
a {{ color: #fff; text-decoration: none; }}
a:hover {{ color: #FB4F14; }}
.back {{ display: inline-block; padding: 10px 20px; background: #FB4F14; color: #fff; text-decoration: none; border-radius: 5px; margin-bottom: 20px; }}
</style>
</head>
<body>
<a href="index.html" class="back">&larr; Back to League Home</a>
<h1>{LEAGUE_NAME} - Standings</h1>
<table>
<tr><th>Rank</th><th>Team</th><th>W-L</th><th>PF</th><th>PA</th></tr>
{"".join(rows)}
</table>
</body>
</html>
'''

if __name__ == "__main__":
    teams = get_standings()
    (ROOT / "teams.html").write_text(build_html(teams))
    print(f"Wrote teams.html with {len(teams)} teams")
    for i, t in enumerate(teams, 1):
        print(f"  {i}. {t['display']:12s} {t['wins']}-{t['losses']}  PF:{t['pf']:.2f}  PA:{t['pa']:.2f}")
