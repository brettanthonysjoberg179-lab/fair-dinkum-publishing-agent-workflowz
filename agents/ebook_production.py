"""Ebook Production Agent — builds EPUB, PDF, DOCX from approved manuscript."""

AGENT_ID = "ebook_production"
ROLE = "Convert approved manuscript to multiple ebook formats with automated QA."

MCP_TOOLS = ["github"]

INPUT_SCHEMA = {
    "manuscript_path": "str — GitHub path to Release 1.0 manuscript",
    "cover_path": "str",
    "metadata": "dict — title, author, ISBN, etc.",
}

OUTPUT_SCHEMA = {
    "epub_path": "str",
    "pdf_path": "str",
    "docx_path": "str",
    "md_path": "str",
    "txt_path": "str",
    "qa_reports": "list[dict]",
    "build_status": "success | failed",
}

TASKS = [
    "Build EPUB 3.3 (reflowable, valid with EpubCheck)",
    "Build PDF (fixed layout, A4, paginated CSS)",
    "Build DOCX (Word-compatible)",
    "Build plain Markdown (source)",
    "Build plain TXT (accessibility)",
    "Run EPUB structure validation",
    "Run PDF page budget check",
    "Run DOCX sanity check",
    "Commit all build artifacts to GitHub builds/",
    "Create GitHub Release with all artifacts",
]

BUILD_PIPELINE = """
Google Docs
     ↓
Canonical Markdown
     ↓
GitHub
     ↓
Build script
     ↓
EPUB / PDF / DOCX / TXT
     ↓
Automated QA
     ↓
GitHub Release
"""

CONSTRAINTS = [
    "EPUB must pass EpubCheck structural validation",
    "PDF must have correct metadata (title, author, subject)",
    "DOCX must open cleanly in Microsoft Word and LibreOffice",
    "All builds must be reproducible from GitHub source",
    "GitHub retains every release with semantic versioning",
    "Cover image must be embedded in EPUB and PDF",
]
