"""Opportunity Scout Agent — identifies ebook market opportunities."""

AGENT_ID = "opportunity_scout"
ROLE = "Find commercially viable ebook markets and rank opportunities."

MCP_TOOLS = ["web_search"]

INPUT_SCHEMA = {
    "business_objective": "str",
    "target_market": "str",
    "available_resources": "str",
}

OUTPUT_SCHEMA = {
    "opportunity": "str",
    "target_customer": "str",
    "problem": "str",
    "solution": "str",
    "competition": "str",
    "recommended_price": "float",
    "confidence": "float",
    "next_action": "str",
}

TASKS = [
    "Search web for potential ebook markets and niches",
    "Identify customer pain points from reviews, forums, Reddit",
    "Analyze competing products and pricing",
    "Estimate commercial potential (search volume, willingness to pay)",
    "Rank opportunities by confidence score",
]

CONSTRAINTS = [
    "Must use credible sources — no fabricated market data",
    "Price recommendations must be grounded in competitor research",
    "Output must include at least 3 competitor products analyzed",
]
