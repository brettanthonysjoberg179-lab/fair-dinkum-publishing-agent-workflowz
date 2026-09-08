"""Author Agent — writes manuscript chapter by chapter."""

AGENT_ID = "author_agent"
ROLE = "Write manuscript chapters following approved outline with research evidence."

MCP_TOOLS = ["obsidian_vault", "github"]

INPUT_SCHEMA = {
    "chapter_number": "int",
    "chapter_outline": "dict — from Outline Architect",
    "research_package": "dict — from Research Agent",
    "style_guide": "dict",
}

OUTPUT_SCHEMA = {
    "chapter_number": "int",
    "title": "str",
    "word_count": "int",
    "content": "str — Markdown",
    "citations_used": "int",
    "status": "draft | revision | approved",
}

TASKS = [
    "Read chapter outline and research package",
    "Write chapter following approved outline structure",
    "Use research evidence — include specific data points",
    "Preserve all citations inline",
    "Avoid invented facts or unsupported claims",
    "Maintain consistent terminology throughout",
    "Include practical examples and actionable steps",
    "Write for specified audience level",
    "Save chapter to GitHub manuscript/",
    "Flag any sections needing additional research",
]

CONSTRAINTS = [
    "Follow approved outline exactly — no detours",
    "Every factual claim needs a citation",
    "No unnecessary repetition between chapters",
    "Minimum word count per chapter: 1000 words",
    "Maximum word count per chapter: 3000 words",
    "Do NOT fabricate statistics, quotes, or examples",
    "Use Australian English spelling for AU market books",
]
