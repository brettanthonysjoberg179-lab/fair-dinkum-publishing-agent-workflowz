#!/usr/bin/env python3
"""
FormFav Gallops CLI — wrapper for FormFavService
Usage:
  python workflow_manager/formfav_gallops_cli.py --date tomorrow
  python workflow_manager/formfav_gallops_cli.py --date 2026-09-23 --out outputs/formfav/2026-09-23
  python workflow_manager/formfav_gallops_cli.py --list-tracks --date 2026-09-23
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
from datetime import datetime, timedelta
from app.services.formfav import FormFavService
from app.agents.formfav_gallops_agent import FormFavGallopsAgent
import json

def parse_date(s: str) -> str:
    if s.lower() == "tomorrow":
        return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    if s.lower() == "today":
        return datetime.now().strftime("%Y-%m-%d")
    # validate YYYY-MM-DD
    datetime.strptime(s, "%Y-%m-%d")
    return s

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="FormFav Aus Gallops — Fetch form guides (Free tier)")
    p.add_argument("--date", default="tomorrow", help="YYYY-MM-DD | today | tomorrow (default: tomorrow)")
    p.add_argument("--out", default=None, help="output directory (default: outputs/formfav/<date>/)")
    p.add_argument("--no-predictions", action="store_true", help="skip Pro predictions (free tier will 403 anyway)")
    p.add_argument("--list-tracks", action="store_true", help="only list AU tracks for date")
    p.add_argument("--via-agent", action="store_true", help="run via FormFavGallopsAgent (logs to RAGS)")
    args = p.parse_args()

    date = parse_date(args.date)

    if args.list_tracks:
        tracks = FormFavGallopsAgent.list_tracks(date=date)
        print(f"AU Gallops tracks for {date}: {len(tracks)}")
        for t in tracks:
            print(f" - {t['track']} ({t['slug']}) — {len(t['races'])} races")
        sys.exit(0)

    if args.via_agent:
        agent = FormFavGallopsAgent(project_id=f"formfav-{date}", date=date, include_predictions=not args.no_predictions)
        res = agent.execute()
        print(json.dumps(res, indent=2))
    else:
        svc = FormFavService()
        result = svc.fetch_aus_gallops_sync(date=date, save_dir=Path(args.out) if args.out else None, include_predictions=not args.no_predictions)
        print(json.dumps(result, indent=2))
        print(f"\n✅ Markdown: {result['markdown']}")
        print(f"📁 Dir: {result['save_dir']}")
        if result['pro_blocked']:
            print("⚠️  Pro predictions blocked (Free tier 403) — heuristic ranking used.")
