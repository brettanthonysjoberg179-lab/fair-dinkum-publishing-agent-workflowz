# formfav_gallops_agent.py
from .base import BaseAgent
from app.services.formfav import FormFavService
from datetime import datetime, timedelta
from pathlib import Path
import os

class FormFavGallopsAgent(BaseAgent):
    """
    MCP / Agent Workforce wrapper for FormFav Aus Gallops Form Get.
    Routes: market_research -> form data -> analysis
    Orchestrates via FormFavService (free tier + heuristic fallback).
    """
    def __init__(self, project_id, date: str = None, include_predictions: bool = True):
        super().__init__(project_id)
        # default to tomorrow in Australia/Sydney
        if date is None:
            # tomorrow
            date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        self.date = date
        self.include_predictions = include_predictions
        self.service = FormFavService()

    def execute(self):
        self.update_status(f'Fetching Aus Gallops forms for {self.date}')
        try:
            result = self.service.fetch_aus_gallops_sync(
                date=self.date,
                include_predictions=self.include_predictions
            )
            self.outputs = result
            # also store to RAGS memory if available
            try:
                from app.services.rags_memory import RAGSMemoryService
                mem = RAGSMemoryService()
                mem.store_memory(
                    content=f"FormFav AU Gallops {self.date}: {result['au_meetings']} tracks, {result['forms_fetched']} forms, pro_blocked={result['pro_blocked']}, dir={result['save_dir']}",
                    metadata={"type": "formfav_fetch", "date": self.date, "pro_blocked": result['pro_blocked']},
                    confidence=0.99
                )
            except Exception:
                pass

            return {
                'status': 'success',
                'message': f"Fetched {result['forms_fetched']} forms for {result['au_meetings']} AU tracks ({self.date}) — saved to {result['save_dir']}",
                'data': result,
                'pro_blocked': result['pro_blocked'],
                'markdown': result['markdown']
            }
        except Exception as e:
            self.update_status('failed')
            return {
                'status': 'error',
                'message': str(e),
                'data': None
            }

    @staticmethod
    def list_tracks(date: str = None):
        svc = FormFavService()
        import asyncio
        if date is None:
            date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        async def _run():
            return await svc.get_meetings(date, race_code="gallops")
        data = asyncio.run(_run())
        au = [m for m in data.get("meetings", []) if m.get("country") == "au"]
        return au
