"""Research Agent — per-chapter research with sourced evidence."""

AGENT_ID = "research_agent"
ROLE = "Research each chapter: questions → web search → sources → notes → citations."

MCP_TOOLS = ["web_search", "obsidian_vault", "github"]

INPUT_SCHEMA = {
    "chapter": "int",
    "chapter_title": "str",
    "research_questions": "list[str]",
    "outline": "dict",
}

OUTPUT_SCHEMA = {
    "chapter": "int",
    "sources": "list[dict]",
    "notes": "list[dict]",
    "evidence": "list[str]",
    "citations": "list[dict]",
    "research_summary": "str",
}

TASKS = [
    "For each research question, perform web search",
    "Extract primary/credible sources",
    "Record source metadata (title, URL, publisher, date, reliability)",
    "Take structured notes per source",
    "Identify evidence supporting chapter claims",
    "Generate citation entries",
    "Write research summary for chapter",
    "Save to Obsidian vault: Ebook Business/02 Market Research/",
    "Sync research package to GitHub project",
]

CONSTRAINTS = [
    "Every claim must have at least one source",
    "No fabricated citations or statistics",
    "Source reliability must be rated (high/medium/low)",
    "Minimum 5 sources per chapter",
    "All sources must include accessed_date",
]
