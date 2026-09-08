"""Product Packaging Agent — creates product listing assets for sale."""

AGENT_ID = "product_packaging"
ROLE = "Create all product listing assets: descriptions, metadata, bonuses, SEO."

MCP_TOOLS = ["obsidian_vault", "github"]

INPUT_SCHEMA = {
    "product_brief": "dict — from Product Strategist",
    "manuscript": "dict — approved manuscript summary",
    "build_artifacts": "dict — from Ebook Production",
}

OUTPUT_SCHEMA = {
    "cover_brief": "dict",
    "short_description": "str — 160 chars max",
    "long_description": "str — 4000 chars",
    "benefits": "list[str]",
    "table_of_contents": "str",
    "author_bio": "str",
    "seo_metadata": "dict",
    "keywords": "list[str]",
    "faq": "list[dict]",
    "bonus_descriptions": "list[dict]",
    "license_terms": "str",
    "product_bundle": "dict",
}

TASKS = [
    "Write short description (160 chars, punchy)",
    "Write long description (4000 chars, benefits-focused)",
    "Create bullet-point benefit list (6-10 items)",
    "Generate formatted table of contents",
    "Write author bio (third person)",
    "Research and list SEO keywords",
    "Write FAQ (10 questions)",
    "Describe each bonus item with value statement",
    "Define license terms (personal use, commercial rights, etc.)",
    "Design product bundle structure",
    "Save all assets to Obsidian vault and GitHub marketing/",
]

PRODUCT_BUNDLE_EXAMPLE = """
Ebook (PDF + EPUB)
+ Workbook (fillable PDF)
+ Checklist (printable PDF)
+ Templates (editable DOCX)
+ Quick-start guide (1-page PDF)
"""

CONSTRAINTS = [
    "Short description must fit 160 characters for meta tags",
    "Benefits must lead with customer outcome, not feature",
    "FAQ must address top 5 objections from market research",
    "Keywords must match Opportunity Scout search data",
    "License terms must be clear and legally safe",
]
