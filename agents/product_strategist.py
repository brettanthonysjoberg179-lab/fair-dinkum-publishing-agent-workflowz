"""Product Strategist Agent — turns opportunity into product definition."""

AGENT_ID = "product_strategist"
ROLE = "Define the ebook product: title, audience, promise, structure, pricing."

MCP_TOOLS = ["obsidian_vault", "github"]

INPUT_SCHEMA = {
    "opportunity": "dict — from Opportunity Scout",
}

OUTPUT_SCHEMA = {
    "title": "str",
    "subtitle": "str",
    "target_audience": "str",
    "promise": "str",
    "learning_outcomes": "list[str]",
    "chapter_structure": "list[dict]",
    "product_format": "list[str]",
    "bonuses": "list[str]",
    "pricing_strategy": "dict",
    "positioning": "str",
}

TASKS = [
    "Create compelling title and subtitle",
    "Define target audience persona",
    "Write the core promise (what reader gets)",
    "List 5-10 learning outcomes",
    "Design chapter structure (15-20 chapters typical)",
    "Define product bundle (ebook + workbook + templates)",
    "Set pricing ladder based on market research",
    "Write positioning statement vs competitors",
    "Save product brief to Obsidian vault and GitHub",
]

CONSTRAINTS = [
    "Product must be more valuable than a simple PDF",
    "Chapter count must match outline architect expectations",
    "Pricing must align with opportunity scout recommendations",
]
