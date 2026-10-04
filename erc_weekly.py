# Equal Result Credit weekly job
# Run every Monday after games are final. No hand editing.
# Requires: Python 3, pandas, numpy.
#
# What it does
# 1. Downloads the public season schedule.
# 2. Drops FCS games (treated as byes).
# 3. Solves ERC (capped-margin least squares) and Colley (wins only).
# 4. Ranks only teams with at least 3 FBS games.
# 5. Writes a CSV. Publish that file; do not retype it.

import sys
import pandas as pd
import numpy as np

SEASON = int(sys.argv[1]) if len(sys.argv) > 1 else 2026
MIN_GAMES = 3
CAP = 21
URL = (
    "https://github.com/sportsdataverse/sportsdataverse-data/"
    f"releases/download/cfb_schedules/cfb_schedules_{SEASON}.csv.gz"
)

df = pd.read_csv(URL)
df = df[(df["completed"] == True) & df["home_points"].notna() & df["away_points"].notna()]
fbs = df[(df["home_division"] == "fbs") & (df["away_division"] == "fbs")].copy()
conf = {}
for r in df.itertuples(index=False):
    if r.home_division == "fbs":
        conf[r.home_team] = r.home_conference
    if r.away_division == "fbs":
        conf[r.away_team] = r.away_conference

teams = sorted(set(fbs["home_team"]) | set(fbs["away_team"]))
idx = {t: i for i, t in enumerate(teams)}
n = len(teams)
A = np.zeros((len(fbs) + 1, n + 1))
b = np.zeros(len(fbs) + 1)
for k, r in enumerate(fbs.itertuples(index=False)):
    margin = max(-CAP, min(CAP, float(r.home_points - r.away_points)))
    A[k, idx[r.home_team]] = 1
    A[k, idx[r.away_team]] = -1
    if not bool(r.neutral_site):
        A[k, n] = 1
    b[k] = margin
A[-1, :n] = 1
coef, *_ = np.linalg.lstsq(A, b, rcond=None)

C = np.eye(n) * 2
cb = np.ones(n)
w = {t: 0 for t in teams}
l = {t: 0 for t in teams}
gp = {t: 0 for t in teams}
for r in fbs.itertuples(index=False):
    hi, ai = idx[r.home_team], idx[r.away_team]
    C[hi, hi] += 1
    C[ai, ai] += 1
    C[hi, ai] -= 1
    C[ai, hi] -= 1
    gp[r.home_team] += 1
    gp[r.away_team] += 1
    if r.home_points > r.away_points:
        w[r.home_team] += 1
        l[r.away_team] += 1
    elif r.away_points > r.home_points:
        w[r.away_team] += 1
        l[r.home_team] += 1
    else:
        w[r.home_team] += 0.5
        w[r.away_team] += 0.5
for t in teams:
    cb[idx[t]] = 1 + (w[t] - l[t]) / 2
colley = np.linalg.solve(C, cb)

rows = []
for t in teams:
    if gp[t] < MIN_GAMES:
        continue
    rows.append({
        "team": t,
        "conference": conf.get(t, ""),
        "erc": coef[idx[t]],
        "colley": colley[idx[t]],
        "fbs_wins": int(w[t]),
        "fbs_losses": int(l[t]),
        "fbs_games": gp[t],
    })
out = pd.DataFrame(rows)
out["erc_rank"] = out["erc"].rank(ascending=False, method="min").astype(int)
out["colley_rank"] = out["colley"].rank(ascending=False, method="min").astype(int)
out = out.sort_values("erc")
out.to_csv(f"erc_{SEASON}_latest.csv", index=False)
print(f"Wrote erc_{SEASON}_latest.csv  teams={len(out)}  games={len(fbs)}  hfa={coef[n]:.2f}")
