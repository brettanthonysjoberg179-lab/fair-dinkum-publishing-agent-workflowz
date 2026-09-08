"""Customer Feedback Agent — post-sale intelligence loop."""

AGENT_ID = "customer_feedback"
ROLE = "Collect and analyze customer feedback for product improvement."

MCP_TOOLS = ["stripe_mcp", "obsidian_vault", "github"]

INPUT_SCHEMA = {
    "stripe_product_id": "str",
    "time_period": "str — e.g., 'last_30_days'",
}

OUTPUT_SCHEMA = {
    "reviews": "list[dict]",
    "support_requests": "list[dict]",
    "refund_reasons": "list[dict]",
    "frequently_misunderstood": "list[str]",
    "feature_requests": "list[str]",
    "product_feedback": "list[dict]",
    "improvement_recommendations": "list[str]",
    "next_edition_priorities": "list[str]",
}

TASKS = [
    "Pull Stripe sales and refund data for time period",
    "Collect customer reviews from marketplace",
    "Aggregate support request themes",
    "Analyze refund reasons by category",
    "Identify frequently misunderstood sections",
    "Compile feature requests",
    "Generate improvement recommendations",
    "Feed insights back to Obsidian for next edition",
    "Create GitHub issue for next edition backlog",
]

FEEDBACK_LOOP = """
TRAFFIC → LANDING PAGE → LEADS → CHECKOUT → SALES → REVENUE
  ↓
CUSTOMER FEEDBACK → CONVERSION ANALYSIS → PRODUCT/MARKETING CHANGES → MORE TRAFFIC
"""

CONSTRAINTS = [
    "All feedback must be tied to actual sales data",
    "Refund analysis must distinguish between product quality and wrong customer",
    "Next edition priorities must be ranked by revenue impact",
    "Never share customer PII in GitHub or Obsidian",
    "Feedback insights must be actionable, not vague",
]
