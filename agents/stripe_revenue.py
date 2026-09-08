"""Stripe Revenue Agent — manages payment infrastructure."""

AGENT_ID = "stripe_revenue"
ROLE = "Manage Stripe products, prices, checkout, orders, coupons, and reporting."

MCP_TOOLS = ["stripe_mcp", "github"]

INPUT_SCHEMA = {
    "product_assets": "dict — from Product Packaging Agent",
    "pricing_ladder": "dict",
}

OUTPUT_SCHEMA = {
    "stripe_product_id": "str",
    "prices": "list[dict]",
    "payment_links": "list[str]",
    "webhook_endpoint": "str",
    "coupons": "list[dict]",
    "checkout_url": "str",
}

PRICING_LADDER = {
    "free": {"type": "lead_magnet", "product": "Free Chapter + Checklist"},
    "basic": {"type": "ebook", "price": 9.00, "product": "Basic Ebook (PDF + EPUB)"},
    "standard": {"type": "bundle", "price": 19.00, "product": "Ebook + Workbook"},
    "premium": {"type": "bundle", "price": 29.00, "product": "Complete Bundle"},
    "elite": {"type": "bundle", "price": 49.00, "product": "Premium Bundle / Toolkit"},
}

TASKS = [
    "Create Stripe Product with product name and description",
    "Create Prices for each tier (one-time or recurring)",
    "Generate Payment Links for each price",
    "Configure webhook endpoint for order events",
    "Create launch discount coupon (e.g., 20% off first week)",
    "Store Stripe IDs in GitHub secrets/variables",
    "Test checkout flow end-to-end",
    "Document Stripe product structure in GitHub",
]

TRACKING_METRICS = [
    "Visitors → demand",
    "Leads → lead-gen performance",
    "Checkout starts → purchase intent",
    "Conversion rate → sales efficiency",
    "Average order value → revenue quality",
    "Refund rate → product quality",
    "Revenue → business outcome",
    "Revenue/product → product ranking",
    "Revenue/channel → marketing attribution",
]

CONSTRAINTS = [
    "Stripe is the ONLY payment infrastructure",
    "All Stripe IDs must be stored as GitHub secrets",
    "Webhook must verify signatures",
    "Prices must match Opportunity Scout recommendations",
    "Coupons must have expiration dates",
]
