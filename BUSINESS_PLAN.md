# Fair Dinkum Publishing — Business Plan & Status Report

**Founder:** Brett Anthony Sjoberg
**Entity:** Fair Dinkum Publishing | ABN 63 590 716 023
**Location:** Adelaide, South Australia (ACST, UTC+09:30)
**Date:** 2026-09-22

---

## 1. Executive Summary

Fair Dinkum Publishing is an AI-automated ebook publishing operation. The system researches markets, generates manuscripts, produces sales assets, processes payments, and launches products — with humans only intervening at two quality gates (pre-publish approval and live checkout verification).

The full pipeline is: Research → Draft → Generate → Build → Construct → Package → Publish → Sell → Market.

---

## 2. What Is COMPLETE & LIVE

### 2.1 Backend Infrastructure
| Component | Status | Location |
|-----------|--------|----------|
| FastAPI MCP server (15 agents) | ✅ Code complete | `fair-dinkum-publishing-agent-workflowz/app/` |
| SQLAlchemy ORM + 5 models | ✅ Complete | `app/models/` |
| SQLite database (163KB, schema applied) | ✅ Live | `data/app.db` |
| Alembic migrations | ✅ Complete | `alembic/versions/` |
| Stripe payment service (customers, products, prices, checkout, stats) | ✅ Full implementation | `app/services/stripe.py` |
| Google Drive service (upload, folders, sharing) | ✅ Complete | `app/services/google_drive.py` |
| Google Drive MCP server (port 8001) | ✅ Complete | `app/mcp/google_drive_mcp_server.py` |
| Thumbnail Generator MCP server (port 8002) | ✅ Complete | `app/mcp/thumbnail_mcp_server.py` |
| Workflow orchestration (16-step pipeline) | ✅ Complete | `app/services/workflow.py` |
| Composio 9-stage manager script | ✅ Complete | `workflow_manager/fair_dinkum_manager.mjs` |
| 15 agent class definitions + base | ✅ Code complete | `app/agents/` |

### 2.2 Existing Workforce Assets (reusable)
| Component | Status | Location |
|-----------|--------|----------|
| RAG memory module (772 lines, embeddings + SQLite vector store) | ✅ Complete | `contents-generator-workforce/shared/rag.py` |
| MasterOrchestrator (task decomposition + dispatch) | ✅ Complete | `contents-generator-workforce/agents/orchestrator/` |
| Orchestrator with task ledger (Researcher→Creator→Evaluator→Seller) | ✅ Complete | `digital_product_workforce/agents/orchestrator.py` |
| Email Workflow (Triage/Draft/Summary/Archive/Image agents) | ✅ Complete | `Software-Architect-Engineer-MCP/src/email_workflow.py` |

### 2.3 Frontend & Marketing
| Component | Status | Location |
|-----------|--------|----------|
| Next.js book hub (pricing, auth, product pages, blog) | ✅ Shell complete | `fair-dinkum-book-hub/` |
| Product listing: "True Blue Aussie Agent Workflowz" ($149) | ✅ Copy written | `app/products/.../GUMROAD_LISTING.md` |
| Launch kit (Reddit, X thread, launch checklist) | ✅ Complete | `workflow_manager/launch_kit.md` |
| Cover image (existing) | ✅ Generated | `ebook-cover-agent/covers/` |
| Google Doc manuscript outline | ✅ Created | Link in launch_kit.md |
| Google Drive cover | ✅ Uploaded | Link in launch_kit.md |

### 2.4 Composio Integrations (configured in manager)
- Airtable (tracking rows)
- GitHub (issues)
- Google Calendar (milestones)
- Gmail (drafts)
- Google Docs (outlines)
- Google Drive (file storage)
- Canva (cover design)
- Stripe (payments)
- Square (orders)

---

## 3. What Is STUB / NOT WIRED (Missing)

### 3.1 Critical Gaps (Blocking Launch)

| Gap | Impact | Priority |
|-----|--------|----------|
| **Agents don't call LLMs** — all agents return mock `status: success` with placeholder data. No actual content generation. | P0 — System produces no real output |
| **No RAGS integration** — agents have no memory of past runs, no retrieval-augmented generation | P0 — No learning between runs |
| **Email agent not connected** — exists in isolation, not wired to orchestrator or publishing workflow | P1 — No inbound trigger |
| **No human-in-the-loop Gmail approval gate** — user specifically requires email-based auth + approvals | P1 — Can't get approval signals |
| **No sub-agent communication** — email agent doesn't spawn or talk to publishing sub-agents | P1 — No orchestration |
| **Book hub content is wrong** — chapters are GitHub Copilot themed, not Fair Dinkum Publishing | P2 — Confusing product |
| **No actual ebook build** — `build_ebook_pdf.py` exists but isn't connected to agent pipeline | P2 — No deliverable |
| **Stripe endpoints not tested** — routes exist but no live API key test | P2 — Payment risk |
| **Cover agent wired but not tested** — calls `ebook-cover-agent` CLI but no verification | P3 — Cover risk |
| **No automated workflow tasks with RAGS** — user explicitly asked for this automation | P1 — Missing feature |

### 3.2 Architecture Gaps

| Gap | Description |
|-----|-------------|
| No orchestrator↔email bridge | Orchestrator has no way to receive inbound email triggers |
| No email↔sub-agent dispatch | Email agent can't spawn publishing workflow tasks |
| No approval state machine | GATE-1/GATE-2 are manual flags, not automated approval flows |
| No Gmail API integration | No actual Gmail read/send in the publishing system |
| RAG module exists but is orphaned | Built for contents-generator-workforce, never integrated into fair-dinkum |

---

## 4. Revenue Model

### Products
1. **True Blue Aussie Agent Workflowz** — $149 AUD (Gumroad, PayPal)
   - 49 prompts + 10 n8n workflows + MCP configs + PayPal processing
   - Status: Listing copy complete, bundle not yet packaged
   
2. **"100 AI Prompts for Real Estate Agents"** — $29 AUD
   - Was deleted (Gumroad daily limit), needs recreation after midnight UTC
   - Source PDF exists: `geo-toolkit/real_estate_prompt_pack.pdf`

3. **"The Autonomous Content Workforce" (Book)** — Future
   - All 10 chapters written to `book/autonomous-content-workforce/`
   - Obsidian vault + sales copy complete

### Target Metrics
- Break-even: 10 sales/month = ~$1,341 AUD (True Blue product)
- 50 sales/month = $6,705 AUD
- 100 sales/month = $13,410 AUD

---

## 5. Automation Architecture Plan

### 5.1 RAGS Workflow Automation
```
┌─────────────────────────────────────────────────────────────────┐
│                    RAGS Memory Layer                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  Embedding   │  │   SQLite     │  │   Document           │  │
│  │  Backend     │─▶│   Vector     │◀──▶│   Chunking           │  │
│  │  (ST/OpenAI) │  │   Store      │  │   + Retrieval        │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│         ▲                                      │                 │
│         │              ┌───────────────────────┘                 │
│         │              ▼                                         │
│  ┌──────┴──────────────────────────────────┐                    │
│  │         Publishing Agents               │                    │
│  │  Each agent stores + retrieves from RAG │                    │
│  │  • Past research → better research      │                    │
│  │  • Past outlines → consistent structure  │                    │
│  │  • Past manuscripts → style learning    │                    │
│  │  • Past evaluations → quality patterns  │                    │
│  └─────────────────────────────────────────┘                    │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Email Orchestrator + Sub-Agent Workflow
```
┌─────────────────────────────────────────────────────────────────────┐
│                     EMAIL ORCHESTRATOR                               │
│                                                                      │
│  ┌──────────┐    ┌──────────────┐    ┌───────────────────────────┐  │
│  │  Gmail   │───▶│  Triage      │───▶│  Classification           │  │
│  │  Watch   │    │  Agent       │    │  (P1-P5 / Category)       │  │
│  └──────────┘    └──────────────┘    └────────────┬──────────────┘  │
│                                                    │                 │
│                         ┌─────────────────────────┼──────┐         │
│                         ▼                         ▼      ▼         │
│              ┌──────────────────┐    ┌─────────────────────────┐   │
│              │  HITL Approval   │    │  Auto-Spawn Sub-Agents  │   │
│              │  (Gmail Reply)   │    │                         │   │
│              │                  │    │  • Publishing Workflow    │   │
│              │  "APPROVE pub-1" │    │  • Research Only         │   │
│              │  → triggers      │    │  • Cover Generation      │   │
│              │    pipeline      │    │  • Market Launch         │   │
│              └──────────────────┘    └─────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### 5.3 Human-in-the-Loop Gmail Approval Gate
```
┌─────────────────────────────────────────────────────────────────────┐
│                  HITL APPROVAL SYSTEM                                │
│                                                                      │
│  Publishing Agent                                                     │
│       │                                                               │
│       ▼                                                               │
│  ┌─────────────────┐     ┌──────────────────────────────────────┐   │
│  │  GATE-1 CHECK   │────▶│  Send Approval Email to Brett        │   │
│  │  eval >= 85?    │     │  Subject: [FDP GATE-1] approve XYZ  │   │
│  └─────────────────┘     │  Body: checklist + links             │   │
│       │                  └──────────────────┬───────────────────┘   │
│       │                                     │                        │
│       │                  ┌──────────────────▼───────────────────┐   │
│       │                  │  Brett Replies to Gmail               │   │
│       │                  │  "APPROVE FDP-XXXX"  → proceeds       │   │
│       │                  │  "REJECT FDP-XXXX"  → halts + logs   │   │
│       │                  │  "CHANGES: ..."      → replans        │   │
│       │                  └──────────────────────────────────────┘   │
│       │                                                              │
│       ▼                                                               │
│  ┌─────────────────┐     ┌──────────────────────────────────────┐   │
│  │  GATE-2 CHECK   │────▶│  Send Live Checkout Test Email       │   │
│  │  live purchase? │     │  "Complete test purchase at: [link]" │   │
│  └─────────────────┘     └──────────────────────────────────────┘   │
│                                                                      │
│  AUTH: Email-based (no OAuth). Brett reads Gmail, replies APPROVE.   │
│  Email agent watches inbox, parses reply, updates project status.   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 6. Immediate Next Steps (Priority Order)

### Phase 1: Core Automation (This Week)
1. ✅ Write business plan + task list (this document)
2. 🔨 Integrate RAGS module into fair-dinkum agents
3. 🔨 Connect email workflow to orchestrator agent
4. 🔨 Build HITL Gmail approval gate
5. 🔨 Wire sub-agent dispatch from email triage

### Phase 2: LLM Integration (Next Week)
6. 🔨 Add LLM client to publishing agents (Gemini/Ollama/HF routing)
7. 🔨 Replace mock agent responses with real generation
8. 🔨 Test end-to-end pipeline with real data

### Phase 3: Product Completion (Week 3)
9. 🔨 Fix book hub content (rewrite chapters for Fair Dinkum)
10. 🔨 Package True Blue bundle for Gumroad
11. 🔨 Recreate Real Estate prompts product (after midnight UTC)
12. 🔨 Test Stripe live payments

### Phase 4: Launch (Week 4)
13. 🔨 Execute launch kit (Reddit, X, FB, LinkedIn)
14. 🔨 Monitor first 10 sales + iterate

---

## 7. Key Risks

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Gumroad daily product limit | High | Schedule creation after midnight UTC |
| Agent LLM costs | Medium | Start with Gemini flash (cheap), scale up |
| Stripe account verification | Medium | Test early, have PayPal fallback |
| Content quality (AI slop) | High | RAGS + HITL gate + editorial agent |
| Email approval latency | Low | Auto-approve option for trusted senders |

---

*Document auto-generated from codebase audit. Last updated: 2026-09-22.*
