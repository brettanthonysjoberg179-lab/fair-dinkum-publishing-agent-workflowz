#!/usr/bin/env python3
"""AU AI Compliance Playbook Agent — generates manuscript, manages chapters, publishes to Gumroad.

This agent:
- Pulls outline from Google Drive
- Generates chapter content using local LLM (Ollama) or Gemini
- Creates Google Docs for each chapter
- Assembles final PDF
- Can trigger Gumroad publishing

Usage:
    python compliance_agent.py --scan          # Scan Drive for playbook files
    python compliance_agent.py --generate     # Generate missing chapters
    python compliance_agent.py --assemble     # Build final PDF
    python compliance_agent.py --publish      # Upload to Gumroad
"""
import argparse
import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
COMPUSIO_CLI = "/home/brettanthonysjoberg179/.local/bin/composio"
OUT_DIR = Path("outputs/au-ai-compliance-playbook")
LOG_DIR = Path("logs")

FD_ROOT = "15NdCCsLDHbkv4-gMAWUxmculVSjmJVb-"
AU_AI_PLAYBOOK = "1bLHR3EP_bSGTe8X19R6XJoIzbeA9cYkB"
AU_AI_DRAFTS = "1Op-adapYkPzzF_wKN3z20mYcLsWhVEc4"
AU_AI_ASSETS = "12VM9Srn4FO-tP9aWVmjsxkjcAA2teCso"
AU_AI_MARKETING = "1hJ8IMKLjLCZCD8oJGWOYoTdkYnmw0YBa"
AU_AI_DELIVERABLES = "1HBZ7atkCXSrv4TGnjH-q4uGC_3QNUOsI"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "compliance_agent.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("compliance-agent")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def load_env():
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip()


def composio_exec(slug: str, params: dict) -> dict | None:
    cmd = [COMPUSIO_CLI, "execute", slug, "-d", json.dumps(params)]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode == 0 and result.stdout.strip():
        data = json.loads(result.stdout)
        if "outputFilePath" in data:
            return json.loads(Path(data["outputFilePath"]).read_text())
        return data
    log.error("Composio %s failed: %s", slug, result.stderr[:300])
    return None


def download_file(file_id: str) -> str | None:
    r = composio_exec("GOOGLEDRIVE_DOWNLOAD_FILE", {"fileId": file_id, "mime_type": "text/plain"})
    if not r or not r.get("successful"):
        return None
    s3 = r["data"].get("downloaded_file_content", {}).get("s3url")
    if not s3:
        return None
    import urllib.request
    try:
        with urllib.request.urlopen(s3, timeout=30) as resp:
            return resp.read().decode("utf-8")
    except Exception as e:
        log.error("Download failed: %s", e)
        return None


# ---------------------------------------------------------------------------
# Agent stages
# ---------------------------------------------------------------------------
def scan_drive():
    """Scan Google Drive for all AU AI Compliance Playbook files."""
    log.info("Scanning Drive …")
    files = []
    page = None
    while True:
        params = {"pageSize": 100, "fields": "id,name,mimeType,parents"}
        if page:
            params["pageToken"] = page
        r = composio_exec("GOOGLEDRIVE_LIST_FILES", params)
        if not r:
            break
        data = r.get("data", r)
        files.extend(data.get("files", []))
        page = data.get("nextPageToken")
        if not page:
            break

    au_ai = [f for f in files if "FDP" in f.get("name", "") or "AU AI" in f.get("name", "")]
    log.info("Found %d AU AI-related files", len(au_ai))
    for f in au_ai:
        log.info("  %s | %s | parents=%d", f["name"][:60], f["id"][:12], len(f.get("parents", [])))
    return au_ai


def generate_chapters():
    """Read outline, generate chapter content, upload as Google Docs."""
    log.info("Generating chapters …")

    # 1. Download outline
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outline_files = list(OUT_DIR.glob("AU_AI_Compliance_Playbook*.txt"))
    if not outline_files:
        log.error("No outline found — run --scan first")
        return

    outline = outline_files[0].read_text()
    log.info("Outline: %d chars", len(outline))

    # 2. Extract chapter titles from outline
    chapters = []
    for line in outline.splitlines():
        if line.strip() and line[0].isdigit() and "." in line[:4]:
            title = line.split(".", 1)[1].strip()
            if title and "Back matter" not in title.lower():
                chapters.append(title)

    if not chapters:
        # Fallback — use default 10-chapter structure
        chapters = [
            "The Compliance Crisis: Why Australian Businesses Are Exposed",
            "The Privacy Act 1988 — What Actually Changed (APP 1.7, Automated Decisions)",
            "OAIC Enforcement: What the Sweeps Mean for You",
            "Mapping Your AI Workflows: Where Personal Data Enters",
            "The 90-Day Compliance Checklist",
            "Privacy Policy Template with AI Disclosure",
            "Internal AI-Use Policy Template",
            "Decision Tree: ChatGPT / Claude / Copilot in Your Business",
            "Voluntary AI Safety Standard — Guardrails Explained",
            "Going Live: Rollout, Audit, and Ongoing Compliance",
        ]

    log.info("Chapters to generate: %d", len(chapters))

    # 3. Check which chapters already exist
    existing = composio_exec("GOOGLEDRIVE_LIST_CHILDREN_V2", {
        "folderId": AU_AI_DRAFTS, "fields": "id,name"
    })
    existing_names = {f["name"] for f in existing.get("data", {}).get("files", [])} if existing else set()
    log.info("Existing drafts: %d", len(existing_names))

    # 4. Generate each missing chapter
    for i, title in enumerate(chapters, 1):
        doc_name = f"Chapter {i:02d}: {title}"
        if doc_name in existing_names:
            log.info("  [%d/%d] SKIP (exists): %s", i, len(chapters), doc_name)
            continue

        log.info("  [%d/%d] Generating: %s", i, len(chapters), doc_name)

        # Build chapter prompt
        prompt = f"""Write a comprehensive chapter for a ebook titled
"The AU AI Compliance Playbook: Small Business Guide to Privacy Act 1988 + Automated Decisions".

Chapter {i}: {title}

Context:
- Target audience: Australian small business owners (non-legal)
- Tone: authoritative but accessible, practical, Australian English
- Length: 1500-2000 words
- Include: real OAIC enforcement examples, practical checklists, action items
- Fact gate: all claims <24mo old, cite primary sources, include disclaimer

Write the full chapter in markdown."""

        # Generate content via Ollama
        content = generate_with_ollama(prompt)
        if not content:
            content = generate_with_gemini(prompt)
        if not content:
            log.error("    No content generated for %s", doc_name)
            continue

        # Upload as Google Doc
        r = composio_exec("GOOGLEDRIVE_CREATE_FILE_FROM_TEXT", {
            "file_name": doc_name,
            "text_content": content,
            "mime_type": "text/plain",
            "parentId": AU_AI_DRAFTS,
        })
        if r and r.get("successful"):
            log.info("    Uploaded: %s", doc_name)
        else:
            log.error("    Upload failed: %s", doc_name)


def generate_with_ollama(prompt: str) -> str | None:
    """Generate content via local Ollama."""
    try:
        import urllib.request
        data = json.dumps({
            "model": os.getenv("OLLAMA_MODEL", "llama3.2:latest"),
            "prompt": prompt,
            "stream": False,
        }).encode()
        req = urllib.request.Request(
            f"{os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')}/api/generate",
            data=data,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=300) as resp:
            result = json.loads(resp.read())
            return result.get("response", "")
    except Exception as e:
        log.warning("Ollama failed: %s", e)
        return None


def generate_with_gemini(prompt: str) -> str | None:
    """Generate content via Google Gemini API."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    try:
        import urllib.request
        data = json.dumps({
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 4096},
        }).encode()
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={api_key}"
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())
            candidates = result.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                return parts[0].get("text", "") if parts else None
    except Exception as e:
        log.warning("Gemini failed: %s", e)
        return None


def assemble_pdf():
    """Download all chapters and assemble into final PDF."""
    log.info("Assembling PDF …")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Get all draft chapters
    r = composio_exec("GOOGLEDRIVE_LIST_CHILDREN_V2", {
        "folderId": AU_AI_DRAFTS, "fields": "id,name"
    })
    if not r or not r.get("successful"):
        log.error("Failed to list chapters")
        return

    chapters = sorted(
        r["data"].get("files", []),
        key=lambda x: x["name"]
    )
    log.info("Found %d chapters", len(chapters))

    full_text = [""]
    full_text.append("# The AU AI Compliance Playbook")
    full_text.append("## Small Business Guide to Privacy Act 1988 + Automated Decisions")
    full_text.append(f"_Generated {datetime.now().strftime('%Y-%m-%d')}_")
    full_text.append("")

    for ch in chapters:
        content = download_file(ch["id"])
        if content:
            full_text.append(f"\n---\n\n## {ch['name']}\n")
            full_text.append(content)

    manuscript = "\n".join(full_text)
    out_path = OUT_DIR / "AU_AI_Compliance_Playbook_Full.md"
    out_path.write_text(manuscript)
    log.info("Saved: %s (%d chars)", out_path, len(manuscript))

    # Convert to PDF via pandoc if available
    try:
        pdf_path = OUT_DIR / "AU_AI_Compliance_Playbook_Final.pdf"
        subprocess.run([
            "pandoc", str(out_path), "-o", str(pdf_path),
            "--pdf-engine=xelatex",
            "-V", "geometry:a4paper",
            "-V", "fontsize=11pt",
        ], check=True, timeout=60)
        log.info("PDF: %s", pdf_path)
    except FileNotFoundError:
        log.warning("pandoc not installed — keeping markdown")
    except Exception as e:
        log.error("PDF conversion failed: %s", e)


def publish_gumroad():
    """Upload final PDF to Gumroad."""
    log.info("Publishing to Gumroad …")
    # Placeholder — would use Gumroad API via Composio or direct HTTP
    log.info("Gumroad upload not yet wired — add GUMROAD_ACCESS_TOKEN to .env")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    load_env()
    LOG_DIR.mkdir(exist_ok=True)

    parser = argparse.ArgumentParser(description="AU AI Compliance Playbook Agent")
    parser.add_argument("--scan", action="store_true", help="Scan Drive for playbook files")
    parser.add_argument("--generate", action="store_true", help="Generate missing chapter drafts")
    parser.add_argument("--assemble", action="store_true", help="Assemble final PDF")
    parser.add_argument("--publish", action="store_true", help="Upload to Gumroad")
    args = parser.parse_args()

    if args.scan:
        scan_drive()
    elif args.generate:
        generate_chapters()
    elif args.assemble:
        assemble_pdf()
    elif args.publish:
        publish_gumroad()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
