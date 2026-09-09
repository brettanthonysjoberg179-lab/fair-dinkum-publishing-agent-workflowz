#!/usr/bin/env python3
"""Entry point for running the Fair Dinkum Publishing Agent Workforce server."""
import uvicorn
from app.api import app

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
