"""Google Docs Editor — manages editorial workflow via Google Docs."""

AGENT_ID = "google_docs_editor"
ROLE = "Orchestrate Google Docs editorial workflow: import, review, revisions, export."

MCP_TOOLS = ["google_docs", "github"]

INPUT_SCHEMA = {
    "manuscript_path": "str — GitHub path to approved markdown",
    "version": "str — e.g., Draft 0.1, Editorial 0.5, Beta 0.9, Release 1.0",
}

OUTPUT_SCHEMA = {
    "document_id": "str",
    "document_url": "str",
    "version": "str",
    "export_path": "str",
    "changes_made": "list[str]",
}

TASKS = [
    "Create new Google Doc from manuscript markdown",
    "Apply formatting: headings, body text, citations",
    "Export to canonical markdown and commit to GitHub",
    "Track version: Draft 0.1 → 0.2 → Editorial 0.5 → Beta 0.9 → Release 1.0",
    "Merge editorial changes back to GitHub",
    "Generate changelog of editorial revisions",
]

WORKFLOW = """
GitHub manuscript (markdown)
       ↓
Google Docs (human review)
       ↓
Editorial changes
       ↓
Approved manuscript
       ↓
GitHub (canonical markdown)
"""

CONSTRAINTS = [
    "Google Docs is the collaborative workspace — never the source of truth",
    "GitHub markdown is always canonical",
    "Version labels must follow: Draft, Editorial, Beta, Release",
    "All editorial changes must be traceable in git history",
]
