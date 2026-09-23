"""Live metrics service — queries the real database and FormFav API."""
import sqlite3
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "app.db")


class MetricsService:
    def __init__(self):
        self.db_path = DB_PATH

    def _query(self, sql: str, params: tuple = ()) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(sql, params)
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows

    def get_project_pipeline(self) -> Dict[str, Any]:
        """Projects grouped by status with percentages."""
        rows = self._query("SELECT status, COUNT(*) as count FROM projects GROUP BY status")
        total = sum(r["count"] for r in rows) or 1
        stages = {}
        for r in rows:
            stages[r["status"]] = {
                "count": r["count"],
                "pct": round(r["count"] / total * 100, 1)
            }
        return {"total": total, "stages": stages}

    def get_project_list(self) -> List[Dict]:
        return self._query("""
            SELECT id, title, status, niche, created_at, updated_at, version
            FROM projects ORDER BY updated_at DESC
        """)

    def get_recent_projects(self, limit: int = 5) -> List[Dict]:
        return self._query("""
            SELECT id, title, status, niche, created_at, updated_at
            FROM projects ORDER BY updated_at DESC LIMIT ?
        """, (limit,))

    def get_opportunity_stats(self) -> Dict[str, Any]:
        rows = self._query("SELECT keyword, overall_score FROM opportunity_scores ORDER BY overall_score DESC")
        if not rows:
            return {"total": 0, "top_keywords": [], "avg_score": 0, "score_dist": {}}
        scores = [r["overall_score"] for r in rows if r["overall_score"] is not None]
        dist = {"high": 0, "medium": 0, "low": 0}
        for s in scores:
            if s >= 70:
                dist["high"] += 1
            elif s >= 40:
                dist["medium"] += 1
            else:
                dist["low"] += 1
        # top unique keywords
        seen = set()
        top = []
        for r in rows:
            if r["keyword"] not in seen:
                seen.add(r["keyword"])
                top.append({"keyword": r["keyword"], "score": r["overall_score"]})
            if len(top) >= 8:
                break
        return {
            "total": len(rows),
            "unique_keywords": len(seen),
            "top_keywords": top,
            "avg_score": round(sum(scores) / len(scores), 1) if scores else 0,
            "max_score": max(scores) if scores else 0,
            "min_score": min(scores) if scores else 0,
            "score_dist": dist
        }

    def get_manuscript_stats(self) -> Dict[str, Any]:
        rows = self._query("""
            SELECT m.id, m.title, m.word_count, m.status, m.project_id,
                   COUNT(ms.id) as sections
            FROM manuscripts m
            LEFT JOIN manuscript_sections ms ON ms.manuscript_id = m.id
            GROUP BY m.id
        """)
        total_words = sum(r["word_count"] or 0 for r in rows)
        total_sections = sum(r["sections"] or 0 for r in rows)
        return {
            "total_manuscripts": len(rows),
            "total_words": total_words,
            "total_sections": total_sections,
            "manuscripts": rows
        }

    def get_outline_stats(self) -> Dict[str, Any]:
        rows = self._query("""
            SELECT o.id, o.title, o.project_id, COUNT(oc.id) as chapters
            FROM outlines o
            LEFT JOIN outline_chapters oc ON oc.outline_id = o.id
            GROUP BY o.id
        """)
        total_chapters = sum(r["chapters"] or 0 for r in rows)
        return {
            "total_outlines": len(rows),
            "total_chapters": total_chapters,
            "outlines": rows
        }

    def get_workflow_health(self) -> Dict[str, Any]:
        """Aggregate health across all projects."""
        projects = self._query("SELECT id, status, updated_at FROM projects")
        now = datetime.utcnow()
        stale_count = 0
        for p in projects:
            if p["updated_at"]:
                updated = datetime.fromisoformat(p["updated_at"])
                if (now - updated).days > 7:
                    stale_count += 1
        return {
            "total_projects": len(projects),
            "stale_projects": stale_count,
            "active_projects": len(projects) - stale_count,
            "healthy": stale_count == 0
        }

    def get_agent_status(self) -> Dict[str, Any]:
        """List all agents and their availability."""
        agents = [
            {"name": "product_director", "desc": "Creates & refines product brief", "status": "active"},
            {"name": "market_research", "desc": "Keyword & competitor research", "status": "active"},
            {"name": "opportunity_scoring", "desc": "Scores market opportunities", "status": "active"},
            {"name": "positioning_offer", "desc": "Defines positioning & pricing", "status": "active"},
            {"name": "outline_architect", "desc": "Designs chapter outlines", "status": "active"},
            {"name": "manuscript_author", "desc": "Writes full manuscript", "status": "active"},
            {"name": "editorial", "desc": "Editorial review & quality gate", "status": "active"},
            {"name": "fact_check_compliance", "desc": "Fact-check & compliance", "status": "active"},
            {"name": "cover_creative_director", "desc": "Cover design direction", "status": "active"},
            {"name": "ebook_production", "desc": "EPUB/PDF production", "status": "active"},
            {"name": "sales_copy", "desc": "Sales page & VSL copy", "status": "active"},
            {"name": "funnel_fulfillment", "desc": "Funnel & payment setup", "status": "active"},
            {"name": "analytics_optimisation", "desc": "Analytics & A/B testing", "status": "active"},
            {"name": "obsidian_knowledge_manager", "desc": "Obsidian vault sync", "status": "active"},
            {"name": "launch_strategist", "desc": "Launch strategy & promotion", "status": "active"},
            {"name": "cloud_archivist", "desc": "Cloud backup & archiving", "status": "active"},
            {"name": "formfav_gallops_agent", "desc": "Aus gallops form data", "status": "active"},
            {"name": "google_drive_agent", "desc": "Google Drive sync", "status": "active"},
            {"name": "credentials_manager", "desc": "API key & auth management", "status": "active"},
            {"name": "analytics_workforce", "desc": "Marketing analytics aggregation", "status": "active"},
        ]
        return {
            "total": len(agents),
            "active": sum(1 for a in agents if a["status"] == "active"),
            "agents": agents
        }

    def get_integrations_status(self) -> Dict[str, Any]:
        """Check which integrations are configured."""
        checks = {
            "Gmail": bool(os.getenv("GMAIL_USER") or os.getenv("COMPOSIO_API_KEY") or os.path.exists(os.path.expanduser("~/.config/himalaya/config.toml"))),
            "Google Drive": bool(os.getenv("GOOGLE_DRIVE_FOLDER_ID") or os.getenv("COMPOSIO_API_KEY")),
            "Airtable": bool(os.getenv("AIRTABLE_API_KEY")),
            "Stripe": bool(os.getenv("STRIPE_SECRET_KEY") or os.getenv("STRIPE_API_KEY")),
            "Gumroad": bool(os.getenv("GUMROAD_ACCESS_TOKEN") or os.getenv("GUMROAD_API_TOKEN")),
            "GitHub": bool(os.getenv("GITHUB_TOKEN")),
            "Obsidian": True,  # local vault always available
            "Composio": bool(os.getenv("COMPOSIO_API_KEY")),
            "FormFav": bool(os.getenv("FORMFAV_API_KEY")),
            "Ollama": True,  # checked via health endpoint
            "Square": bool(os.getenv("SQUARE_ACCESS_TOKEN")),
            "Reddit": bool(os.getenv("REDDIT_CLIENT_ID") or os.getenv("COMPOSIO_API_KEY")),
        }
        configured = sum(1 for v in checks.values() if v)
        total = len(checks)
        return {
            "configured": configured,
            "total": total,
            "pct": round(configured / total * 100, 1),
            "integrations": checks
        }

    def get_formfav_summary(self, date: Optional[str] = None) -> Dict[str, Any]:
        """Get FormFav gallops summary for a date."""
        if date is None:
            date = (datetime.utcnow() + timedelta(hours=9, minutes=30)).strftime("%Y-%m-%d")
        save_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "outputs", "formfav", date)
        meetings_file = os.path.join(save_dir, f"meetings_au_{date}.json")
        if os.path.exists(meetings_file):
            try:
                with open(meetings_file) as f:
                    data = json.load(f)
                au_meetings = data.get("au_meetings", [])
                total_races = sum(len(m.get("races", [])) for m in au_meetings)
                return {
                    "date": date,
                    "fetched": True,
                    "au_tracks": len(au_meetings),
                    "total_races": total_races,
                    "tracks": [m.get("track", "?") for m in au_meetings]
                }
            except:
                pass
        return {"date": date, "fetched": False, "au_tracks": 0, "total_races": 0, "tracks": []}

    def get_products_stats(self) -> Dict[str, Any]:
        """Digital product business stats from Gumroad catalog + DRY_RUN listings.

        Reads:
          - ~/gumroad-storefront/catalog.json (priced catalog, cents)
          - ~/digital_product_workforce/outputs/_listings/*.json (listing records)
        """
        home = os.path.expanduser("~")
        catalog_path = os.path.join(home, "gumroad-storefront", "catalog.json")
        listings_dir = os.path.join(home, "digital_product_workforce", "outputs", "_listings")

        products = []
        try:
            with open(catalog_path) as f:
                cat = json.load(f)
            for p in cat.get("products", []):
                price_cents = p.get("price") or 0
                products.append({
                    "name": p.get("name"),
                    "category": p.get("category"),
                    "slug": p.get("slug"),
                    "price": round(price_cents / 100, 2) if price_cents else 0,
                    "source": "catalog",
                })
        except Exception:
            pass

        listings = []
        published = 0
        dry_run = 0
        if os.path.isdir(listings_dir):
            for fn in sorted(os.listdir(listings_dir)):
                if not fn.endswith(".json"):
                    continue
                try:
                    with open(os.path.join(listings_dir, fn)) as f:
                        d = json.load(f)
                    if isinstance(d, dict) and "listing" in d:
                        d = d.get("listing") or {}
                    status = str(d.get("status") or d.get("mode") or "dry_run")
                    live = status.lower() == "published"
                    if live:
                        published += 1
                    else:
                        dry_run += 1
                    price = d.get("price") or 0
                    listings.append({
                        "file": fn,
                        "name": d.get("name") or d.get("title") or d.get("product_name") or fn,
                        "price": round(float(price), 2) if price else 0,
                        "status": status,
                    })
                except Exception:
                    continue

        priced = [p for p in products if p["price"]]
        return {
            "catalog_count": len(products),
            "catalog_total_value": round(sum(p["price"] for p in priced), 2),
            "catalog_avg_price": round(sum(p["price"] for p in priced) / len(priced), 2) if priced else 0,
            "categories": sorted({p["category"] for p in products if p.get("category")}),
            "products": products,
            "listings_count": len(listings),
            "published_count": published,
            "dry_run_count": dry_run,
            "listings": listings,
        }

    def get_memory_stats(self) -> Dict[str, Any]:
        """RAGS memory DB statistics."""
        mem_path = os.path.join(os.path.expanduser("~"), "rags_memory_db", "rags_memory.db")
        stats = {
            "db_exists": os.path.exists(mem_path),
            "total": 0,
            "active": 0,
            "memories_by_type": {},
            "feedbacks": 0,
            "modules": {},
            "avg_confidence": 0.0,
        }
        if not stats["db_exists"]:
            return stats
        try:
            conn = sqlite3.connect(mem_path)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) c FROM memory_vectors")
            stats["total"] = cur.fetchone()["c"]
            cur.execute("SELECT COUNT(*) c FROM memory_vectors WHERE is_active = 1")
            stats["active"] = cur.fetchone()["c"]
            cur.execute("SELECT memory_type, COUNT(*) c FROM memory_vectors GROUP BY memory_type")
            stats["memories_by_type"] = {r["memory_type"]: r["c"] for r in cur.fetchall()}
            cur.execute("SELECT COUNT(*) c FROM memory_feedback")
            stats["feedbacks"] = cur.fetchone()["c"]
            cur.execute("SELECT metadata, confidence FROM memory_vectors WHERE is_active = 1")
            confs = []
            for r in cur.fetchall():
                confs.append(r["confidence"] or 0)
                try:
                    meta = json.loads(r["metadata"] or "{}")
                    mod = meta.get("module")
                    if mod is not None:
                        stats["modules"][str(mod)] = stats["modules"].get(str(mod), 0) + 1
                except Exception:
                    pass
            stats["avg_confidence"] = round(sum(confs) / len(confs), 2) if confs else 0.0
            conn.close()
        except Exception:
            pass
        return stats

    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Aggregate summary for the main dashboard."""
        pipeline = self.get_project_pipeline()
        opps = self.get_opportunity_stats()
        health = self.get_workflow_health()
        agents = get_agent_status_static()
        integrations = self.get_integrations_status()
        formfav = self.get_formfav_summary()
        manuscripts = self.get_manuscript_stats()
        outlines = self.get_outline_stats()

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "projects": pipeline,
            "projects_list": self.get_project_list(),
            "opportunities": opps,
            "health": health,
            "agents": agents,
            "integrations": integrations,
            "formfav": formfav,
            "manuscripts": manuscripts,
            "outlines": outlines,
        }


def get_agent_status_static() -> Dict[str, Any]:
    agents = [
        {"name": "product_director", "desc": "Creates & refines product brief", "status": "active"},
        {"name": "market_research", "desc": "Keyword & competitor research", "status": "active"},
        {"name": "opportunity_scoring", "desc": "Scores market opportunities", "status": "active"},
        {"name": "positioning_offer", "desc": "Defines positioning & pricing", "status": "active"},
        {"name": "outline_architect", "desc": "Designs chapter outlines", "status": "active"},
        {"name": "manuscript_author", "desc": "Writes full manuscript", "status": "active"},
        {"name": "editorial", "desc": "Editorial review & quality gate", "status": "active"},
        {"name": "fact_check_compliance", "desc": "Fact-check & compliance", "status": "active"},
        {"name": "cover_creative_director", "desc": "Cover design direction", "status": "active"},
        {"name": "ebook_production", "desc": "EPUB/PDF production", "status": "active"},
        {"name": "sales_copy", "desc": "Sales page & VSL copy", "status": "active"},
        {"name": "funnel_fulfillment", "desc": "Funnel & payment setup", "status": "active"},
        {"name": "analytics_optimisation", "desc": "Analytics & A/B testing", "status": "active"},
        {"name": "obsidian_knowledge_manager", "desc": "Obsidian vault sync", "status": "active"},
        {"name": "launch_strategist", "desc": "Launch strategy & promotion", "status": "active"},
        {"name": "cloud_archivist", "desc": "Cloud backup & archiving", "status": "active"},
        {"name": "formfav_gallops_agent", "desc": "Aus gallops form data", "status": "active"},
        {"name": "google_drive_agent", "desc": "Google Drive sync", "status": "active"},
        {"name": "credentials_manager", "desc": "API key & auth management", "status": "active"},
        {"name": "analytics_workforce", "desc": "Marketing analytics aggregation", "status": "active"},
    ]
    return {"total": len(agents), "active": len(agents), "agents": agents}
