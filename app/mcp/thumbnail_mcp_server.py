#!/usr/bin/env python3
"""
Thumbnail Generator MCP Server.

Provides a service for generating standardized thumbnails.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.thumbnail_generator import generate_thumbnail
import os

app = FastAPI(
    title="Thumbnail Generator MCP Server",
    description="MCP Server for generating standardized product thumbnails",
    version="1.0.0"
)

# Request Model
class GenerateThumbnailRequest(BaseModel):
    title: str
    output_path: str
    background_color: Optional[str] = "#1a1a1a"
    text_color: Optional[str] = "#ffffff"

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "thumbnail-generator"}

@app.post("/generate")
def generate(request: GenerateThumbnailRequest):
    """Generate a thumbnail image."""
    try:
        path = generate_thumbnail(
            request.title,
            request.output_path,
            request.background_color,
            request.text_color
        )
        return {"status": "success", "path": path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# MCP Protocol endpoints
@app.post("/mcp/tools/list")
def list_tools():
    """List available MCP tools."""
    return {
        "tools": [
            {
                "name": "generate_thumbnail",
                "description": "Generate a standardized product thumbnail",
                "properties": {
                    "title": {"type": "string", "description": "Title text on thumbnail"},
                    "output_path": {"type": "string", "description": "Output file path"},
                    "background_color": {"type": "string", "description": "Hex color for background"},
                    "text_color": {"type": "string", "description": "Hex color for text"}
                },
                "required": ["title", "output_path"]
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)
