"""
FormFav Service — Aus Gallops Form Get (Free Tier + Pro Graceful Fallback)
Handles meetings + form guides via https://api.formfav.com/v1
Auth: X-API-Key header from FORMFAV_API_KEY env var

Free tier: /form/venues, /form/meetings, /form
Pro tier (403 on free): /predictions, /stats/*, /stats/track-bias/*
  -> caught and replaced with heuristic scoring fallback

Usage:
  from app.services.formfav import FormFavService
  svc = FormFavService()
  result = await svc.fetch_aus_gallops(date="2026-09-23")  # tomorrow
"""
import os
import json
import asyncio
import httpx
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List

BASE_URL = "https://api.formfav.com/v1"
DEFAULT_TIMEOUT = 20

class FormFavService:
    def __init__(self, api_key: Optional[str] = None, base_url: str = BASE_URL):
        self.api_key = api_key or os.getenv("FORMFAV_API_KEY") or "fk_d3cb8497840a530813b19013d47483436e998d3e1686072cd95c1122db33439d"
        self.base_url = base_url.rstrip("/")
        if not self.api_key:
            raise ValueError("FORMFAV_API_KEY not set. Export FORMFAV_API_KEY or pass api_key.")
        self.headers = {"X-API-Key": self.api_key}

    def _check_key(self):
        if not self.api_key or len(self.api_key) < 10:
            raise ValueError("Invalid FORMFAV_API_KEY")

    async def get_venues(self) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            r = await client.get(f"{self.base_url}/form/venues", headers=self.headers)
            r.raise_for_status()
            return r.json()

    async def get_meetings(self, date: str, race_code: str = "gallops", country: Optional[str] = None, timezone: Optional[str] = None) -> Dict[str, Any]:
        params: Dict[str, Any] = {"date": date, "race_code": race_code}
        if country: params["country"] = country
        if timezone: params["timezone"] = timezone
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            r = await client.get(f"{self.base_url}/form/meetings", headers=self.headers, params=params)
            r.raise_for_status()
            return r.json()

    async def get_form(self, date: str, track: str, race: int) -> Dict[str, Any]:
        params = {"date": date, "track": track, "race": race}
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            r = await client.get(f"{self.base_url}/form", headers=self.headers, params=params)
            r.raise_for_status()
            return r.json()

    async def get_predictions(self, date: str, track: str, race: int) -> Dict[str, Any]:
        """Pro tier — returns 403 on free. Caller should handle."""
        params = {"date": date, "track": track, "race": race}
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            r = await client.get(f"{self.base_url}/predictions", headers=self.headers, params=params)
            if r.status_code == 403:
                return {"error": "pro_tier_required", "detail": r.json().get("detail"), "status": 403}
            r.raise_for_status()
            return r.json()

    async def get_jockey_stats(self, name: str) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            r = await client.get(f"{self.base_url}/stats/jockey/{name}", headers=self.headers)
            if r.status_code == 403:
                return {"error": "pro_tier_required", "status": 403}
            r.raise_for_status()
            return r.json()

    async def get_trainer_stats(self, name: str) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            r = await client.get(f"{self.base_url}/stats/trainer/{name}", headers=self.headers)
            if r.status_code == 403:
                return {"error": "pro_tier_required", "status": 403}
            r.raise_for_status()
            return r.json()

    async def get_track_bias(self, track: str, distance: Optional[str] = None) -> Dict[str, Any]:
        params = {}
        if distance: params["distance"] = distance
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            r = await client.get(f"{self.base_url}/stats/track-bias/{track}", headers=self.headers, params=params)
            if r.status_code == 403:
                return {"error": "pro_tier_required", "status": 403}
            r.raise_for_status()
            return r.json()

    async def get_runner_stats(self, name: str) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            r = await client.get(f"{self.base_url}/stats/runner/{name}", headers=self.headers)
            if r.status_code == 403:
                return {"error": "pro_tier_required", "status": 403}
            r.raise_for_status()
            return r.json()

    # ---------- Heuristic Ranking (Free Tier Fallback for Pro Predictions) ----------
    @staticmethod
    def heuristic_score(runner: Dict[str, Any], condition: str = "good", distance_m: int = 1200) -> float:
        """
        Free-tier fallback scoring when /predictions is 403.
        Weighted sum from stats available in /form response.
        Returns 0-100 score.
        """
        stats = runner.get("stats", {})
        overall = stats.get("overall", {})
        track = stats.get("track", {})
        conditions = stats.get("conditions", {})
        cond_stats = conditions.get(condition.lower(), {}) if condition else {}
        first_up = stats.get("firstUp", {})
        second_up = stats.get("secondUp", {})

        score = 0.0

        # overall win% 30
        score += overall.get("winPercent", 0) * 30
        # place% 20
        score += overall.get("placePercent", 0) * 20
        # track familiarity 15
        score += track.get("winPercent", 0) * 10
        score += track.get("placePercent", 0) * 5
        # condition suitability 10
        if cond_stats:
            score += cond_stats.get("winPercent", 0) * 7
            score += cond_stats.get("placePercent", 0) * 3
        # first/second up 5
        score += first_up.get("winPercent", 0) * 2.5
        score += second_up.get("winPercent", 0) * 2.5
        # barrier bias (simple): inside 1-4 good for <=1400, wider ok for longer
        barrier = runner.get("barrier", 99)
        if distance_m <= 1400:
            if barrier <= 4: score += 4
            elif barrier <= 8: score += 2
            elif barrier >= 12: score -= 2
        else:
            if barrier <= 6: score += 2
            if barrier >= 14: score -= 1
        # recent form: count of 1,2,3 in last form string
        form = runner.get("form", "") or ""
        recent = form[-5:]  # last 5
        placings = sum(1 for c in recent if c in "123")
        score += placings * 1.5
        # career prize money log bonus (class)
        try:
            prize_str = runner.get("careerPrizeMoney", "$0").replace("$","").replace(",","")
            prize = float(prize_str)
            if prize > 50000: score += 3
            elif prize > 20000: score += 1.5
        except: pass
        # age/sex penalty: older 8+ slight penalty
        age = runner.get("age", 4)
        if age >= 8: score -= 1
        if age == 3 and distance_m >= 1800: score -= 0.5  # young stayers risk

        # weight claim bonus (apprentice claim indicates weight off)
        if runner.get("claim"):
            score += 0.5

        # scratched = 0
        if runner.get("scratched"):
            return 0.0

        # normalize to 0-100, cap — tuned to avoid capping (raw 0-18 → 20-88)
        scaled = min(99, max(18, 22 + score * 3.2))
        return round(scaled, 1)

    def rank_runners_heuristic(self, runners: List[Dict[str, Any]], condition: str, distance: str) -> List[Dict[str, Any]]:
        try:
            dist_m = int(str(distance).replace("m","").strip())
        except: dist_m = 1200
        ranked = []
        for r in runners:
            s = self.heuristic_score(r, condition, dist_m)
            ranked.append({**r, "_heuristic_score": s})
        ranked.sort(key=lambda x: x["_heuristic_score"], reverse=True)
        # add win probability approx via softmax-ish
        total = sum(x["_heuristic_score"] for x in ranked) or 1
        for r in ranked:
            r["_heuristic_win_prob"] = round(r["_heuristic_score"] / total * 100, 1)
        return ranked

    # ---------- Orchestrator: Fetch all AU gallops for a date ----------
    async def fetch_aus_gallops(self, date: str, save_dir: Optional[Path] = None, include_predictions: bool = True, generate_markdown: bool = True) -> Dict[str, Any]:
        """
        Fetch AU gallops meetings + form guides for a date.
        Saves JSON + markdown to save_dir (default: ./outputs/formfav/{date}/ or /tmp/opencode)
        Returns summary dict.
        """
        self._check_key()
        if save_dir is None:
            save_dir = Path(f"outputs/formfav/{date}")
            # fallback to /tmp if no write permission
            try:
                save_dir.mkdir(parents=True, exist_ok=True)
            except:
                save_dir = Path(f"/tmp/opencode/formfav_{date}")
                save_dir.mkdir(parents=True, exist_ok=True)
        else:
            save_dir = Path(save_dir)
            save_dir.mkdir(parents=True, exist_ok=True)

        # 1. Meetings
        meetings_data = await self.get_meetings(date=date, race_code="gallops")
        all_meetings = meetings_data.get("meetings", [])
        au_meetings = [m for m in all_meetings if m.get("country") == "au"]
        # Save meetings index
        with open(save_dir / f"meetings_{date}.json", "w") as f:
            json.dump(meetings_data, f, indent=2)
        with open(save_dir / f"meetings_au_{date}.json", "w") as f:
            json.dump({"date": date, "au_meetings": au_meetings, "total_au": len(au_meetings)}, f, indent=2)

        forms: List[Dict[str, Any]] = []
        predictions: List[Dict[str, Any]] = []
        markdown_lines: List[str] = []

        if generate_markdown:
            markdown_lines.append(f"# Form Guides — Aus Gallops — {date}")
            markdown_lines.append(f"_Generated {datetime.now().isoformat()} | FormFav API v1 | AU meetings: {len(au_meetings)}_")
            markdown_lines.append("")
            total_races = sum(len(m["races"]) for m in au_meetings)
            markdown_lines.append(f"**Summary:** {len(au_meetings)} tracks | {total_races} races")
            for m in au_meetings:
                markdown_lines.append(f"- **{m['track']}** (`{m['slug']}`) — {len(m['races'])} races — {m['races'][0].get('timezone','')}")
            markdown_lines.append("\n---\n")

        pro_blocked = False
        # 2. Loop each race
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            for meeting in au_meetings:
                slug = meeting["slug"]
                for race_info in meeting["races"]:
                    rn = race_info["raceNumber"]
                    # fetch form (free tier)
                    try:
                        r = await client.get(f"{self.base_url}/form", headers=self.headers, params={"date": date, "track": slug, "race": rn})
                        r.raise_for_status()
                        form = r.json()
                    except Exception as e:
                        form = {"error": str(e), "track": slug, "raceNumber": rn}
                        continue

                    # save raw form
                    with open(save_dir / f"{slug}_R{rn}.json", "w") as f:
                        json.dump(form, f, indent=2)
                    forms.append(form)

                    # predictions (pro) — optional
                    pred = None
                    if include_predictions:
                        try:
                            pr = await client.get(f"{self.base_url}/predictions", headers=self.headers, params={"date": date, "track": slug, "race": rn})
                            if pr.status_code == 403:
                                pro_blocked = True
                                pred = {"error": "pro_tier_required", "status": 403}
                            else:
                                pr.raise_for_status()
                                pred = pr.json()
                                with open(save_dir / f"{slug}_R{rn}_predictions.json", "w") as f:
                                    json.dump(pred, f, indent=2)
                                predictions.append(pred)
                        except: pass
                        await asyncio.sleep(0.2)

                    # heuristic rank fallback if pro blocked or missing
                    runners = form.get("runners", [])
                    condition = form.get("condition", "Good")
                    distance = form.get("distance", "1200m")
                    ranked = self.rank_runners_heuristic(runners, condition, distance)

                    if generate_markdown:
                        markdown_lines.append(f"## {form.get('track')} — Race {rn}: {form.get('raceName')}")
                        markdown_lines.append(f"**{distance} | {form.get('raceClass')} | {condition} {form.get('weather','')} | Prize ${form.get('prizeMoney','')} | {form.get('startTime')} {form.get('timezone','')} | {len(runners)} runners**")
                        markdown_lines.append("")
                        if pro_blocked:
                            markdown_lines.append(f">_Pro predictions unavailable (Free tier 403) — heuristic ranking below (free-tier fallback)_")
                            markdown_lines.append("")
                        # table
                        markdown_lines.append("| # | Horse | B | Wgt | Jockey | Trainer | Form | W-P% | Score | Prob | SCR |")
                        markdown_lines.append("|---:|---|---|---|---|---|---|---|---|---|---|---|")
                        for r_data in ranked:
                            wgt = f"{r_data.get('weight','')}kg" + (f" (-{r_data.get('claim')})" if r_data.get('claim') else "")
                            stats = r_data.get("stats", {}).get("overall", {})
                            wp = f"{stats.get('starts',0)} ({stats.get('winPercent',0)*100:.0f}%/{stats.get('placePercent',0)*100:.0f}%)" if stats else "-"
                            score = r_data.get("_heuristic_score","-")
                            prob = f"{r_data.get('_heuristic_win_prob','-')}%"
                            scr = "SCR" if r_data.get("scratched") else ""
                            markdown_lines.append(f"| {r_data.get('number')} | **{r_data.get('name')}** | {r_data.get('barrier')} | {wgt} | {r_data.get('jockey','-')} | {r_data.get('trainer','')[:22]} | `{r_data.get('form','-')}` | {wp} | {score} | {prob} | {scr} |")
                        markdown_lines.append("")
                        # top 3 heuristic
                        top3 = [r for r in ranked if not r.get("scratched")][:3]
                        if top3:
                            markdown_lines.append(f"**Heuristic Top 3:** 1. {top3[0]['name']} ({top3[0]['_heuristic_score']}) — 2. {top3[1]['name'] if len(top3)>1 else '-'} — 3. {top3[2]['name'] if len(top3)>2 else '-'}")
                            markdown_lines.append("")
                        scr_list = [r["name"] for r in runners if r.get("scratched")]
                        if scr_list:
                            markdown_lines.append(f">Scratched: {', '.join(scr_list)}")
                            markdown_lines.append("")
                        markdown_lines.append("---\n")
                    await asyncio.sleep(0.25)

        # write markdown
        md_path = None
        if generate_markdown and markdown_lines:
            md_path = save_dir / f"FORM_GUIDES_{date}.md"
            with open(md_path, "w") as f:
                f.write("\n".join(markdown_lines))
            # also copy to legacy /tmp for debugging
            try:
                Path(f"/tmp/opencode/form_guides_{date}.md").write_text("\n".join(markdown_lines))
            except: pass

        return {
            "date": date,
            "au_meetings": len(au_meetings),
            "total_meetings": len(all_meetings),
            "forms_fetched": len(forms),
            "predictions_fetched": len(predictions),
            "pro_blocked": pro_blocked,
            "save_dir": str(save_dir),
            "markdown": str(md_path) if md_path else None,
            "meetings": au_meetings,
        }

    # Sync wrapper for CLI/scripts
    def fetch_aus_gallops_sync(self, date: str, **kwargs) -> Dict[str, Any]:
        return asyncio.run(self.fetch_aus_gallops(date, **kwargs))

# CLI helper
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="FormFav Aus Gallops Form Get")
    parser.add_argument("--date", default=(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"), help="YYYY-MM-DD (default: tomorrow)")
    parser.add_argument("--no-predictions", action="store_true", help="skip Pro predictions")
    parser.add_argument("--out", default=None, help="output directory")
    args = parser.parse_args()
    svc = FormFavService()
    result = svc.fetch_aus_gallops_sync(args.date, save_dir=Path(args.out) if args.out else None, include_predictions=not args.no_predictions)
    print(json.dumps(result, indent=2))
