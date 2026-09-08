"""Marketing Agent — generates all sales and distribution content."""

AGENT_ID = "marketing_agent"
ROLE = "Create landing page, sales copy, email sequence, social posts, SEO content."

MCP_TOOLS = ["obsidian_vault", "github"]

INPUT_SCHEMA = {
    "product_assets": "dict — from Product Packaging Agent",
    "target_audience": "str",
    "pricing_ladder": "dict",
}

OUTPUT_SCHEMA = {
    "landing_page": "str — HTML",
    "sales_copy": "str",
    "email_sequence": "list[dict]",
    "blog_articles": "list[str]",
    "social_posts": "list[dict]",
    "seo_articles": "list[str]",
    "lead_magnet": "str",
    "product_comparison": "str",
}

TASKS = [
    "Write landing page HTML (hero, benefits, CTA, FAQ)",
    "Write long-form sales copy (2000+ words)",
    "Create 5-email nurture sequence",
    "Write 3 SEO-optimized blog articles",
    "Generate 10 social media posts (LinkedIn/Twitter/Facebook)",
    "Design lead magnet (free chapter + checklist)",
    "Write product comparison page",
    "Save all assets to GitHub marketing/ and Obsidian 07 Marketing/",
]

CONTENT_FUNNEL = """
FREE CONTENT (blog, social, SEO)
      ↓
EMAIL / LEAD (lead magnet)
      ↓
EBOOK ($9-$19)
      ↓
BUNDLE ($29)
      ↓
PREMIUM ($49+)
"""

CONSTRAINTS = [
    "All content must lead toward checkout",
    "No fabricated testimonials or customer quotes",
    "SEO articles must target keywords from Product Packaging Agent",
    "Social posts must be platform-appropriate in length",
    "Email sequence must have clear CTA in every email",
    "Lead magnet must deliver real value, not be a thin upsell",
]
