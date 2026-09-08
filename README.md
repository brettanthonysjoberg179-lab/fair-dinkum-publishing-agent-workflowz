# Ebook Builder Agent Workforce

End-to-end **Ebook Production → QA → Publishing → Stripe Monetisation** workforce powered by MCP architecture.

## Structure

```
book-builder/
├── agents/           # 12 specialist agents
│   ├── opportunity_scout.py
│   ├── product_strategist.py
│   ├── research_agent.py
│   ├── outline_architect.py
│   ├── author_agent.py
│   ├── google_docs_editor.py
│   ├── editorial_qa.py
│   ├── ebook_production.py
│   ├── product_packaging.py
│   ├── stripe_revenue.py
│   ├── marketing_agent.py
│   └── customer_feedback.py
├── workflows/        # Orchestrator state machine
│   └── orchestrator.yaml
├── scripts/          # Runner utilities
│   └── orchestrator.py
└── templates/        # Book/manuscript templates
```

## Workforce

1. **Opportunity Scout** — finds ebook markets, ranks opportunities
2. **Product Strategist** — title, audience, promise, structure, pricing
3. **Research Agent** — per-chapter research with sourced evidence
4. **Outline Architect** — hierarchical outline as source of truth
5. **Author Agent** — writes manuscript chapter by chapter
6. **Google Docs Editor** — editorial workflow via Google Docs
7. **Editorial QA** — content, language, research, commercial checks
8. **Ebook Production** — EPUB, PDF, DOCX, TXT builds
9. **Product Packaging** — descriptions, SEO, bonuses, bundle
10. **Stripe Revenue** — products, prices, checkout, webhooks
11. **Marketing Agent** — landing page, emails, social, SEO
12. **Customer Feedback** — post-sale intelligence loop

## Orchestrator State Machine

```
IDEA → RESEARCHING → VALIDATING → APPROVED → OUTLINING → WRITING → EDITING → QA → PRODUCTION → PACKAGING → READY_FOR_SALE → SELLING → OPTIMISING
```

## Quick Start

```bash
# Run a single agent
python3 scripts/orchestrator.py opportunity_scout '{"business_objective": "...", "target_market": "...", "available_resources": "..."}'
```

## MCP Dependencies

- `web_search` — research and market analysis
- `github` — version control and releases
- `obsidian_vault` — long-term knowledge
- `google_docs` — collaborative editing
- `stripe_mcp` — payment infrastructure

## Knowledge Module

See `~/Documents/Obsidian Vault/KM-EBOOK-BUILDER-WORKFORCE.md` for the full architecture spec.

## Business Model

> Find commercially viable problems → build useful digital products → distribute them → collect payment → learn from customers → improve the product → repeat.
