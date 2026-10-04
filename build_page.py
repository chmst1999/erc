"""Turn erc_2026_latest.csv into index.html. Run after erc_weekly.py."""
import pandas as pd
from datetime import datetime, timezone

df = pd.read_csv("erc_2026_latest.csv").sort_values("erc_rank")
top = df.head(25)
stamp = datetime.now(timezone.utc).strftime("%B %d, %Y")

rows = []
for r in top.itertuples(index=False):
    gap = abs(int(r.erc_rank) - int(r.colley_rank))
    mark = ' class="split"' if gap > 10 else ""
    rows.append(
        f"<tr><td>{int(r.erc_rank)}</td><td>{r.team}</td>"
        f"<td>{int(r.fbs_wins)}–{int(r.fbs_losses)}</td>"
        f"<td{mark}>{int(r.colley_rank)}</td><td>{r.conference}</td></tr>"
    )

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Equal Result Credit</title>
<style>
  body {{ font-family: Georgia, serif; max-width: 820px; margin: 2rem auto; padding: 0 1rem; color: #1a1a1a; line-height: 1.45; }}
  h1 {{ font-size: 1.6rem; margin-bottom: 0.2rem; }}
  .sub {{ color: #444; margin-top: 0; }}
  table {{ border-collapse: collapse; width: 100%; margin: 1.2rem 0; }}
  th, td {{ text-align: left; padding: 0.35rem 0.45rem; border-bottom: 1px solid #ddd; }}
  th {{ border-bottom: 2px solid #222; }}
  .split {{ color: #7a2e0e; font-weight: 600; }}
</style>
</head>
<body>
<h1>Equal Result Credit</h1>
<p class="sub">Updated {stamp}. FBS games only. Teams need three FBS games to be ranked.</p>
<p>Every opponent has one strength number. Beating that team is worth the same thing no matter who did it. A loss is a loss. An FCS game counts as a bye. Margin counts only up to 21 points. There is no preseason ranking and no conference bonus. Colley uses wins and losses only. A Colley rank in brown differs by more than ten spots, and that week is not settled. Conference is a label, not an input.</p>
<p>Compare with the <a href="https://apnews.com/hub/ap-top-25-college-football-poll">AP poll</a> and the <a href="https://www.usatoday.com/sports/ncaaf/polls/coaches-poll/">coaches' poll</a> released the same week.</p>
<table>
<thead><tr><th>ERC</th><th>Team</th><th>FBS record</th><th>Colley</th><th>Conference</th></tr></thead>
<tbody>
{''.join(rows)}
</tbody>
</table>
</body>
</html>
"""
with open("index.html", "w") as f:
    f.write(html)
print("Wrote index.html")
