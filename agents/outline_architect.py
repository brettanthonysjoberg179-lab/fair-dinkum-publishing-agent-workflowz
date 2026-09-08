"""Outline Architect — builds hierarchical chapter structure."""

AGENT_ID = "outline_architect"
ROLE = "Create the detailed chapter-by-chapter outline as the single source of truth."

MCP_TOOLS = ["obsidian_vault", "github"]

INPUT_SCHEMA = {
    "product_brief": "dict — from Product Strategist",
    "research": "dict — from Research Agent",
}

OUTPUT_SCHEMA = {
    "book_title": "str",
    "total_chapters": "int",
    "introduction": "str",
    "conclusion": "str",
    "chapters": [
        {
            "number": "int",
            "title": "str",
            "sections": [
                {
                    "name": "str",
                    "key_points": "list[str]",
                    "example": "str",
                    "action_steps": "list[str]",
                }
            ],
            "learning_outcome": "str",
        }
    ],
}

TASKS = [
    "Design introduction hook",
    "Create chapter titles aligned with product promise",
    "For each chapter, define 3-5 sections",
    "Assign learning outcomes to each chapter",
    "Ensure logical flow and no gaps",
    "Write conclusion chapter",
    "Save outline to Obsidian and GitHub as canonical structure",
    "Validate: total word budget vs target",
]

CONSTRAINTS = [
    "Outline is the single source of truth for Author Agent",
    "Must cover all learning outcomes from product brief",
    "Chapter count must match product strategist definition",
    "No orphaned sections — every section connects to an outcome",
]
