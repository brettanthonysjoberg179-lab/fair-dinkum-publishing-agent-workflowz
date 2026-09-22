# Fair Dinkum Publishing — Workflow Manager (99% automated)

Ebook Business: **Fair Dinkum Publishing** (Brett Sjoberg, ABN 63 590 716 023, Adelaide SA)
Brand: **Aussie Agent Workflowz** — flipbook ebooks + agent guides.

## What this is
`fair_dinkum_manager.mjs` runs the 9-stage pipeline via Composio (`composio run -f ...`):
**research → draft → generate → build → construct → package → publish (GATE-1) → sell (GATE-2) → market**

It chains your existing fleet — it does NOT replace it:
- `contents-generator-workforce/` (25 agents) → research/outline/SEO/social
- `digital_product_workforce/outputs/prod-fairdinkum-ebook-001/` (9-stage scaffold + brief) → product source of truth
- `fair-dinkum-publishing-agent-workflowz/app/` (18 agents + FastAPI) → manuscript→fulfillment
- `fair-dinkum-book-hub/` (Next.js) → storefront
- `rags_memory_db/` → long-term memory (10 active, business context ids 6–10)
- `Documents/Obsidian Vault/` → per-book archive note
- Composio (all ACTIVE): gmail, googlecalendar, googledocs, googledrive, github, airtable, square, stripe, canva, gumroad, reddit, firecrawl

## Run it
```bash
# 1. Edit CONFIG at top of fair_dinkum_manager.mjs (TITLE, NICHE, PRICE, STAGE, AUTO, REPO)
# 2. Safe single stage:
composio run -f fair-dinkum-publishing-agent-workflowz/workflow_manager/fair_dinkum_manager.mjs
# 3. Full pipeline (GATEs auto-logged — still do 1 live test purchase):
#    set STAGE="all", AUTO=true, then run again
```

Stage file: `stages.json`. Obsidian template: `obsidian_template.md`.

## Proven live (this session)
- RESEARCH 4/4: Airtable row rec1cgaCzgfFVS9xu + recSxI0elo35bVB4Z, GitHub issue (brettanthonysjoberg179-lab/brett-sjobergs-aussie-agent-workflowz), Calendar milestone, Gmail draft
- DRAFT: Google Doc outline (1mwUS8C… + new runs), Drive folder (fixed `parent_id`)
- Gmail/Canva/Airtable/Docs exports proven in `composio-demo/gmail_agent/`
- Stripe product dry-run OK; Square schema fixed (`{order, idempotency_key}`)
- RAGS: 5 business memories stored (ids 6–10)

## 99% automation — the 1% (humans)
- GATE-1 (publish): approve eval ≥85/100 + flipbook + cover + price
- GATE-2 (sell): 1 live test purchase on Stripe + Square + Gumroad
Everything else (research log, outline doc, manuscript queue, build notes, cover draft, QA issue, launch events, social pack, archive) is agent-run.

## Next to try
1. `STAGE="generate"` → queue manuscript (manuscript_author), then `build` → geo-toolkit PDF
2. `STAGE="sell" --dry-run` first: `composio execute STRIPE_CREATE_PRODUCT --dry-run -d '{name:"FDP …"}'`
3. Real checkout in Stripe test mode before live
4. `composio dev init` + `dev triggers` if you want push-based Gmail triggers instead of polling
5. Point `fair-dinkum-book-hub` at live Stripe price + Gumroad URL from `sell/02-skus.json`
