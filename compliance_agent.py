#!/usr/bin/env python3
"""
AU AI Compliance Agent — Autonomous Digital Product Agent
=========================================================

An expert agent that manages "The AU AI Compliance Playbook" digital product
across the entire lifecycle: outline → chapters → review → publish.

Capabilities:
- Google Drive file management (Composio)
- Manuscript generation (Ollama/Gemini)
- Chapter assembly and PDF generation
- Gumroad publishing integration

Architecture:
    compliance_agent.py          # Main entry point
    skills/
        drive_manager.py         # Google Drive operations
        manuscript_writer.py     # Content generation
        pdf_assembler.py         # PDF building
        gumroad_publisher.py     # Publishing
    
Usage:
    python compliance_agent.py --scan
    python compliance_agent.py --write
    python compliance_agent.py --assemble
    python compliance_agent.py --publish
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
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "outputs" / "au-ai-compliance-playbook"
LOG_DIR = BASE_DIR / "logs"

# Google Drive folder IDs (from organization)
FD_ROOT_ID = "15NdCCsLDHbkv4-gMAWUxmculVSjmJVb-"
PRODUCTS_ID = "1XSEfGeHEuxWa_Ov6dXghhdV6vv1m9_28"
AU_AI_PLAYBOOK_ID = "1bLHR3EP_bSGTe8X19R6XJoIzbeA9cYkB"
DRAFTS_ID = "1Op-adapYkPzzF_wKN3z20mYcLsWhVEc4"
ASSETS_ID = "12VM9Srn4FO-tP9aWVmjsxkjcAA2teCso"
MARKETING_ID = "1hJ8IMKLjLCZCD8oJGWOYoTdkYnmw0YBa"
DELIVERABLES_ID = "1HBZ7atkCXSrv4TGnjH-q4uGC_3QNUOsI"

# Product metadata
PRODUCT_NAME = "The AU AI Compliance Playbook"
PRODUCT_SUBTITLE = "Small Business Guide to Privacy Act 1988 + Automated Decisions"
PRODUCT_PRICE = 29  # USD

# Setup logging
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "agent.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("compliance-agent")


# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
def load_env():
    """Load .env file."""
    env_file = BASE_DIR / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip()


# ---------------------------------------------------------------------------
# Composio Interface
# ---------------------------------------------------------------------------
def composio(slug: str, params: dict) -> dict | None:
    """Execute a Composio tool via CLI."""
    cmd = [COMPUSIO_CLI, "execute", slug, "-d", json.dumps(params)]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode == 0 and result.stdout.strip():
        data = json.loads(result.stdout)
        if "outputFilePath" in data:
            try:
                pf = Path(data["outputFilePath"])
                return json.loads(pf.read_text())
            except Exception as e:
                log.error("Read output file failed: %s", e)
                return None
        return data
    log.error("Composio %s failed: %s", slug, result.stderr[:200] if result.stderr else result.stdout[:200])
    return None


def drive_list(folder_id: str) -> list:
    """List files in a Drive folder."""
    r = composio("GOOGLEDRIVE_LIST_CHILDREN_V2", {"folderId": folder_id, "fields": "id,name,mimeType"})
    if r and r.get("successful"):
        return r.get("data", {}).get("files", [])
    return []


def drive_download(file_id: str) -> str | None:
    """Download file content as plain text."""
    r = composio("GOOGLEDRIVE_DOWNLOAD_FILE", {"fileId": file_id, "mime_type": "text/plain"})
    if r and r.get("successful"):
        data = r.get("data", {})
        s3 = data.get("downloaded_file_content", {}).get("s3url")
        if s3:
            try:
                import urllib.request
                with urllib.request.urlopen(s3, timeout=30) as resp:
                    return resp.read().decode("utf-8")
            except Exception as e:
                log.error("Download failed: %s", e)
    return None


def drive_upload(name: str, content: str, parent_id: str, mime: str = "application/vnd.google-apps.document") -> dict | None:
    """Upload content as a new Google Drive file."""
    r = composio("GOOGLEDRIVE_CREATE_FILE_FROM_TEXT", {
        "file_name": name,
        "text_content": content,
        "mime_type": mime,
        "parentId": parent_id,
    })
    return r


# ---------------------------------------------------------------------------
# LLM Interface
# ---------------------------------------------------------------------------
def llm_generate(prompt: str, system: str = None) -> str | None:
    """Generate content via Ollama or Gemini."""
    # Try Ollama first
    try:
        import urllib.request
        data = json.dumps({
            "model": os.getenv("OLLAMA_MODEL", "qwen2.5:latest"),
            "prompt": f"{system}\n\n{prompt}" if system else prompt,
            "stream": False,
        }).encode()
        url = f"{os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')}/api/generate"
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=300) as resp:
            result = json.loads(resp.read())
            content = result.get("response", "")
            if content:
                return content
    except Exception as e:
        log.warning("Ollama failed: %s", e)

    # Fallback to Gemini
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            import urllib.request
            data = json.dumps({
                "contents": [{"parts": [{"text": f"{system}\n\n{prompt}" if system else prompt}]}],
                "generationConfig": {"temperature": 0.7, "maxOutputTokens": 4096},
            }).encode()
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
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


# ---------------------------------------------------------------------------
# Manuscript Writer
# ---------------------------------------------------------------------------
CHAPTER_TEMPLATES = [
    {
        "num": 1,
        "title": "The Compliance Crisis",
        "description": "Why Australian small businesses are exposed to AI privacy risks",
        "word_count": 2000,
    },
    {
        "num": 2,
        "title": "The Privacy Act 1988 — What Actually Changed",
        "description": "APP 1.7, automated decisions, and the new enforcement landscape",
        "word_count": 2500,
    },
    {
        "num": 3,
        "title": "OAIC Enforcement — What the Sweeps Mean for You",
        "description": "Real enforcement cases, penalties, and what triggers an audit",
        "word_count": 2000,
    },
    {
        "num": 4,
        "title": "Mapping Your AI Workflows",
        "description": "Where personal data enters your AI systems and how to audit it",
        "word_count": 2500,
    },
    {
        "num": 5,
        "title": "The 90-Day Compliance Checklist",
        "description": "A practical day-by-day plan to achieve compliance",
        "word_count": 2000,
    },
    {
        "num": 6,
        "title": "Privacy Policy Template with AI Disclosure",
        "description": "Ready-to-use template with AI-specific clauses",
        "word_count": 1500,
    },
    {
        "num": 7,
        "title": "Internal AI-Use Policy Template",
        "description": "Staff policy for ChatGPT, Claude, Copilot, and custom AI tools",
        "word_count": 2000,
    },
    {
        "num": 8,
        "title": "Decision Tree — ChatGPT / Claude / Copilot in Your Business",
        "description": "Flowchart-style guide for common AI tools and their compliance status",
        "word_count": 2000,
    },
    {
        "num": 9,
        "title": "Voluntary AI Safety Standard — Guardrails Explained",
        "description": "The 8 guardrails and how to implement them in a small business",
        "word_count": 2000,
    },
    {
        "num": 10,
        "title": "Going Live — Rollout, Audit, and Ongoing Compliance",
        "description": "Implementation guide, audit schedule, and continuous improvement",
        "word_count": 1500,
    },
]


def generate_chapter(chapter: dict) -> str:
    """Generate a single chapter."""
    prompt = f"""Write Chapter {chapter['num']}: {chapter['title']}

Product: {PRODUCT_NAME} — {PRODUCT_SUBTITLE}
Target: Australian small business owners, non-legal audience
Tone: Authoritative but accessible, practical, Australian English
Length: {chapter['word_count']} words
Focus: {chapter['description']}

Rules:
- Use Australian English (e.g., 'organisation', 'practise')
- All factual claims must be <24 months old
- Cite primary sources (OAIC, Australian Government, legislation.gov.au)
- Include real-world examples and case studies
- Add a "Key Takeaways" section at the end
- Include a "Compliance Action Items" checklist where relevant
- No US-centric examples unless clearly marked as international comparison

Write the full chapter in clean markdown."""

    system = f"""You are an Australian privacy law expert and compliance consultant specialising in helping small businesses understand their obligations under the Privacy Act 1988 (Cth), particularly regarding AI and automated decision-making. You write practical, actionable guidance — not legal jargon."""

    return llm_generate(prompt, system)


# ---------------------------------------------------------------------------
# Agent Phases
# ---------------------------------------------------------------------------
def phase_scan():
    """Scan Drive and report what exists."""
    log.info("Scanning Google Drive …")
    
    # Get product folder contents
    drafts = drive_list(DRAFTS_ID)
    assets = drive_list(ASSETS_ID)
    marketing = drive_list(MARKETING_ID)
    deliverables = drive_list(DELIVERABLES_ID)
    
    report = f"""
╔══════════════════════════════════════════════════════════════╗
║  AU AI COMPLIANCE PLAYBOOK — DRIVE SCAN REPORT             ║
╠══════════════════════════════════════════════════════════════╣
║  Product: {PRODUCT_NAME[:50]:50} ║
║  Scan: {datetime.now().strftime('%Y-%m-%d %H:%M'):57} ║
╠══════════════════════════════════════════════════════════════╣
║  01_Drafts:      {len(drafts):3} files                              ║
║  02_Assets:      {len(assets):3} files                              ║
║  03_Marketing:   {len(marketing):3} files                              ║
║  04_Deliverables:{len(deliverables):3} files                              ║
╠══════════════════════════════════════════════════════════════╣
║  Chapter Status:                                             ║"""
    
    existing_chapters = {f["name"] for f in drafts if "Chapter" in f.get("name", "")}
    for ch in CHAPTER_TEMPLATES:
        status = "✅ DONE" if any(ch["title"] in name for name in existing_chapters) else "❌ TODO"
        report += f"\n║  Ch {ch['num']:2d}. {ch['title'][:35]:35} {status:8}      ║"
    
    report += """
╠══════════════════════════════════════════════════════════════╣
║  Next Steps:                                                ║
║  1. Run --write to generate missing chapters                ║
║  2. Run --assemble to build the final PDF                   ║
║  3. Run --publish to upload to Gumroad                      ║
╚══════════════════════════════════════════════════════════════╝"""
    
    log.info(report)
    return report


def phase_write():
    """Generate missing chapters and upload to Drive."""
    log.info("Writing chapters …")
    
    # Get existing drafts
    existing = drive_list(DRAFTS_ID)
    existing_names = {f["name"] for f in existing}
    
    for ch in CHAPTER_TEMPLATES:
        name = f"Chapter {ch['num']:02d}: {ch['title']}"
        if any(ch["title"] in en for en in existing_names):
            log.info("  [%d/%d] SKIP (exists): %s", ch["num"], len(CHAPTER_TEMPLATES), name)
            continue
        
        log.info("  [%d/%d] Generating: %s", ch["num"], len(CHAPTER_TEMPLATES), name)
        content = generate_chapter(ch)
        if not content:
            log.error("    Failed to generate: %s", name)
            continue
        
        r = drive_upload(name, content, DRAFTS_ID)
        if r and r.get("successful"):
            log.info("    Uploaded: %s (%d chars)", name, len(content))
        else:
            log.error("    Upload failed: %s", name)


def phase_assemble():
    """Download all chapters, assemble into manuscript and PDF."""
    log.info("Assembling manuscript …")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Get all drafts
    drafts = drive_list(DRAFTS_ID)
    chapters = sorted(
        [f for f in drafts if "Chapter" in f.get("name", "")],
        key=lambda x: x["name"]
    )
    
    if not chapters:
        log.error("No chapters found — run --write first")
        return
    
    # Build manuscript
    lines = [
        f"# {PRODUCT_NAME}",
        f"## {PRODUCT_SUBTITLE}",
        f"_Generated {datetime.now().strftime('%Y-%m-%d')}_",
        "",
        "---",
        "",
    ]
    
    for ch in chapters:
        content = drive_download(ch["id"])
        if content:
            lines.append(f"\n---\n\n## {ch['name']}\n")
            lines.append(content)
            lines.append("")
    
    manuscript = "\n".join(lines)
    md_path = OUTPUT_DIR / "manuscript.md"
    md_path.write_text(manuscript)
    log.info("Saved: %s (%d chars)", md_path, len(manuscript))
    
    # Convert to PDF if pandoc available
    try:
        pdf_path = OUTPUT_DIR / "AU_AI_Compliance_Playbook.pdf"
        subprocess.run([
            "pandoc", str(md_path), "-o", str(pdf_path),
            "--pdf-engine=xelatex",
            "-V", "geometry:a4paper,margin=2cm",
            "-V", "fontsize=11pt",
            "-V", "toc",
            "--toc-depth=2",
        ], check=True, timeout=60)
        log.info("PDF: %s", pdf_path)
    except FileNotFoundError:
        log.warning("pandoc not installed — keeping markdown")
    except Exception as e:
        log.error("PDF conversion failed: %s", e)


def phase_publish():
    """Upload final PDF to Gumroad."""
    log.info("Publishing to Gumroad …")
    
    pdf_path = OUTPUT_DIR / "AU_AI_Compliance_Playbook.pdf"
    if not pdf_path.exists():
        log.error("PDF not found — run --assemble first")
        return
    
    # TODO: Wire Gumroad API via Composio or direct HTTP
    log.info("Upload placeholder — wire GUMROAD_ACCESS_TOKEN to publish")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    load_env()
    
    parser = argparse.ArgumentParser(
        description="AU AI Compliance Playbook Agent — autonomous digital product management"
    )
    parser.add_argument("--scan", action="store_true", help="Scan Drive for product files")
    parser.add_argument("--write", action="store_true", help="Generate missing chapters")
    parser.add_argument("--assemble", action="store_true", help="Build final PDF")
    parser.add_argument("--publish", action="store_true", help="Upload to Gumroad")
    parser.add_argument("--full-pipeline", action="store_true", help="Run all phases in sequence")
    args = parser.parse_args()
    
    if args.full_pipeline:
        phase_scan()
        phase_write()
        phase_assemble()
        phase_publish()
    elif args.scan:
        phase_scan()
    elif args.write:
        phase_write()
    elif args.assemble:
        phase_assemble()
    elif args.publish:
        phase_publish()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
