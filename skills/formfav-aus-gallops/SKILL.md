---
name: formfav-aus-gallops
description: Fetch Australian Gallops form guides via FormFav API (free tier) with Pro-tier graceful fallback and heuristic ranking. Use when user asks for gallops form, tomorrow's races, track form, meetings, or FormFav predictions.
---

# FormFav Aus Gallops Form Get

Fetch → Filter AU → Save → Markdown + Heuristic Ranking. Works on **Free tier** (no Pro key needed).

## When to use
- `get tomorrow's aus gallops meets and form` 
- `pull form for Warwick Farm Randwick Eagle Farm`
- `predictions` requested but free tier returns 403 → use heuristic fallback

## Auth
- Env: `FORMFAV_API_KEY=fk_d3cb8497840a530813b19013d47483436e998d3e1686072cd95c1122db33439d`
- Header: `X-API-Key: $FORMFAV_API_KEY`
- Base: `https://api.formfav.com/v1`

## Endpoints (and tier)
- `GET /form/venues` — free — lookup slugs (e.g. `warwick-farm`, `eagle-farm`)
- `GET /form/meetings?date=YYYY-MM-DD&race_code=gallops` — free — returns 22+ meetings, filter `country=='au'`
- `GET /form?date=YYYY-MM-DD&track=SLUG&race=N` — free — full form + runners + stats (use for 37 races)
- `GET /predictions?date=&track=&race=` — **Pro tier** — free returns `403 Access denied. Your 'free' tier does not include model predictions.` → fallback to heuristic
- `GET /stats/jockey/{name}` `/stats/trainer/{name}` `/stats/track-bias/{track}` `/stats/runner/{name}` — **Pro tier** → 403 on free

## Procedure

### 1. Resolve date
Default `tomorrow` in `Australia/Sydney`. Accept `YYYY-MM-DD`, `today`, `tomorrow`. Validate format.

```bash
DATE="2026-09-23"  # or $(date -d tomorrow +%F) AEST
export FORMFAV_API_KEY="${FORMFAV_API_KEY:-fk_d3cb8497840a530813b19013d47483436e998d3e1686072cd95c1122db33439d}"
```

### 2. Fetch meetings + filter AU
```bash
curl -s -H "X-API-Key: $FORMFAV_API_KEY" "https://api.formfav.com/v1/form/meetings?date=$DATE&race_code=gallops" -o /tmp/meetings_$DATE.json
python3 -c "import json; d=json.load(open('/tmp/meetings_$DATE.json')); print([m['track'] for m in d['meetings'] if m['country']=='au'])"
```
Expected 2026-09-23: 5 tracks → `eagle-farm`, `gawler`, `geelong`, `northam`, `warwick-farm` (37 races, 444 runners).

### 3. Fetch all forms (free tier loop)
Use `app/services/formfav.py` (FormFavService) — async httpx, 250ms delay, saves to `outputs/formfav/$DATE/`:

```python
from app.services.formfav import FormFavService
svc = FormFavService()
result = await svc.fetch_aus_gallops(date="2026-09-23")  # or .fetch_aus_gallops_sync()
# or agent:
from app.agents.formfav_gallops_agent import FormFavGallopsAgent
agent = FormFavGallopsAgent(project_id="formfav-2026-09-23", date="2026-09-23")
res = agent.execute()
```

CLI:
```bash
python3 -m app.services.formfav --date 2026-09-23
python3 app/services/formfav.py --date tomorrow --out outputs/formfav/today
```

### 4. Handle Pro 403 gracefully
- `GET /predictions` on free → `{"detail":"Access denied. Your 'free' tier does not include model predictions. Upgrade to Pro or Enterprise."}` → set `pro_blocked=True`.
- Do NOT retry indefinitely. Fall back to `FormFavService.heuristic_score()` / `rank_runners_heuristic()`:
  - Inputs from `/form` runner.stats: `overall win%*30 + place%*20 + track*15 + condition*10 + barrier bias + recent `form` 123 placings + prize log`
  - Barrier: 1-4 bonus <=1400m.
  - Output: `_heuristic_score` 0-100 + `_heuristic_win_prob`.
  - Mark markdown: `> Pro predictions unavailable (Free tier 403) — heuristic ranking`

Also applies to `/stats/*` + `/stats/track-bias/*` → same 403 (`This feature requires Pro tier or higher. Your current tier: Free.`). Fallback uses in-form stats.

### 5. Outputs
- `outputs/formfav/$DATE/meetings_$DATE.json` + `meetings_au_$DATE.json`
- `outputs/formfav/$DATE/{slug}_R{N}.json` (37 files, ~19-50K each, 1.3M total)
- `outputs/formfav/$DATE/{slug}_R{N}_predictions.json` (only if Pro)
- `outputs/formfav/$DATE/FORM_GUIDES_$DATE.md` (782 lines, 62K, table per race + Top 3 heuristic)
- Legacy: `/tmp/opencode/forms_$DATE/` + `/tmp/opencode/form_guides_$DATE.md`
- `FORM_GUIDES_2026-09-23.md` in project root (for 2026-09-23 proof)
- RAGS memory log: `formfav_fetch` fact, conf 0.99

### 6. Markdown template per race
```
## Warwick Farm — Race 1: Tab Plate
**1200m | 3YO+ MDN FM | Good 4 Fine | Prize $100000 | 03:50 UTC (Australia/Sydney) | 10 runners**
| # | Horse | B | Wgt | Jockey | Trainer | Form | W-P% | Score | Prob | SCR |
Top 3: 1. Moon Flash 67.2 — 2. Double Vision — 3. Love Story
> Scratched: ...
```

### 7. Rate limits & errors
- Header `x-ratelimit-remaining-day: 960/1000`. Delay 200-300ms between calls (37 races ~9s).
- On 429, sleep 1s and retry once.
- Confirm meets before fetching forms; if 0 AU meets, report date + suggest venue check via `/form/venues`.

### 8. Verification
```bash
ls -lh outputs/formfav/$DATE/ && wc -l outputs/formfav/$DATE/FORM_GUIDES_$DATE.md
cat outputs/formfav/$DATE/FORM_GUIDES_$DATE.md | head -n 80
```

### 9. Example — tomorrow's fetch (proven 2026-09-23)
```
FormFavService.fetch_aus_gallops_sync("2026-09-23")
→ {au_meetings:5, total_meetings:22, forms_fetched:37, predictions_fetched:0, pro_blocked:true, save_dir:"outputs/formfav/2026-09-23"}
```

Do not fabricate predictions. If Pro blocked, explicitly state fallback and show heuristic scores.
