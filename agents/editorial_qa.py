"""Editorial QA Agent — validates content, language, research, commercial quality."""

AGENT_ID = "editorial_qa"
ROLE = "Multi-axis QA check: content, language, research, commercial viability."

MCP_TOOLS = ["github"]

INPUT_SCHEMA = {
    "manuscript_path": "str — GitHub path to approved manuscript",
    "outline": "dict",
    "product_brief": "dict",
}

OUTPUT_SCHEMA = {
    "status": "PASS | FAIL",
    "critical_issues": "list[str]",
    "warnings": "list[str]",
    "recommended_improvements": "list[str]",
    "scores": {
        "content_completeness": "float 0-1",
        "logical_flow": "float 0-1",
        "language_quality": "float 0-1",
        "citation_coverage": "float 0-1",
        "commercial_strength": "float 0-1",
    },
}

TASKS = [
    "Check content: completeness, logical flow, repetition, contradictions",
    "Check language: grammar, spelling, readability, tone, consistency",
    "Check research: citation coverage, source quality, unsupported claims",
    "Check commercial: clear outcome, strong intro/conclusion, CTAs, positioning",
    "Compare against outline: missing chapters, weak sections",
    "Score each axis 0-1",
    "Generate PASS/FAIL verdict",
    "Write QA report to GitHub qa/",
]

CONSTRAINTS = [
    "FAIL if any critical issue found",
    "FAIL if citation coverage < 80% of claims",
    "FAIL if missing chapters from outline",
    "FAIL if readability score below target audience level",
    "Warnings do not block publishing but must be addressed",
    "QA report must be machine-readable JSON",
]
