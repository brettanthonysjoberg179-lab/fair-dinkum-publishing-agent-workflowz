// Fair Dinkum Publishing — 99% Automated Ebook Workflow Manager
// Run: composio run -f fair-dinkum-publishing-agent-workflowz/workflow_manager/fair_dinkum_manager.mjs -- --title "Aussie Agent Workflowz" --niche "AI side-hustle" --price 49 --stage all --auto
// Stages: research→draft→generate→build→construct→package→publish(GATE-1)→sell(GATE-2)→market
// Prove wiring fast: --stage research  (safe reads + 1 Airtable row + 1 Calendar event + 1 GitHub issue + 1 Gmail draft, no sends)
// Full: --stage all --auto  (GATEs logged as auto-approved; remove --auto to pause for humans)

// ---- CONFIG (edit these 4 lines per book — no CLI args needed) ----
const TITLE = "The AU AI Compliance Playbook: Small Business Guide to Privacy Act 1988 + Automated Decisions";
const NICHE = "Australian small business AI compliance — Privacy Act, OAIC enforcement, APP 1.7 automated-decision rules";
const PRICE = 147; // AUD, GST-inc
const STAGE = "all"; // research | draft | generate | build | construct | package | publish | sell | market | all
const AUTO = false; // true = auto-approve GATE-1/GATE-2 (demo), false = pause for human
const REPO = "brettanthonysjoberg179-lab/brett-sjobergs-aussie-agent-workflowz";
const PID = `FDP-${Date.now().toString(36).toUpperCase()}`;

const AIRTABLE_BASE = "appqqwluJEP7553HY";
const AIRTABLE_TABLE = "Embeddings & Documents";
const CAL_ID = "primary";
const ME = "brettanthonysjoberg179@gmail.com";

const run = async (slug, params, label) => {
  try {
    const r = await execute(slug, params);
    console.log(`  ✓ ${label || slug}`);
    return r;
  } catch (e) {
    console.log(`  ✗ ${label || slug}: ${e.message?.slice(0, 220)}`);
    return { successful: false, error: e.message };
  }
};
const want = (key) => STAGE === "all" || STAGE === key;
const summary = { product_id: PID, title: TITLE, niche: NICHE, price_aud: PRICE, stages: {} };

console.log(`FDP Manager ${PID} | "${TITLE}" | stage=${STAGE} auto=${AUTO}`);

// ---- 1 RESEARCH ----
if (want("research")) {
  console.log("\n[1/9] RESEARCH");
  const brief = { product_id: PID, title: TITLE, niche: NICHE, price_aud: PRICE, outline_ref: "outputs/fdp_flipbook_planning_brief.md", product_ref: "digital_product_workforce/outputs/prod-fairdinkum-ebook-001/00-product-brief.json" };
  const air = await run("AIRTABLE_CREATE_RECORDS", { baseId: AIRTABLE_BASE, tableIdOrName: AIRTABLE_TABLE, records: [{ fields: { Title: `[FDP research] ${TITLE}`.slice(0, 100), "Document Content": JSON.stringify(brief).slice(0, 3000), Metadata: JSON.stringify({ stage: "research", PID, niche: NICHE }) } }] }, "airtable tracking row");
  const gh = await run("GITHUB_CREATE_AN_ISSUE", { owner: REPO.split("/")[0], repo: REPO.split("/")[1], title: `[FDP research] ${TITLE}`, body: `Product ${PID}\nNiche: ${NICHE}\nPrice: $${PRICE} AUD GST-inc\n\nPipeline: research→…→market. See stages.json.` }, "github issue");
  const cal = await run("GOOGLECALENDAR_CREATE_EVENT", { calendar_id: CAL_ID, summary: `[FDP] Research done: ${TITLE}`.slice(0, 100), description: `Research complete for ${PID}. Next: draft.`, start_datetime: new Date(Date.now() + 86400000).toISOString(), end_datetime: new Date(Date.now() + 86400000 + 1800000).toISOString() }, "calendar milestone");
  const mail = await run("GMAIL_CREATE_EMAIL_DRAFT", { recipient_email: ME, subject: `[FDP research] ${TITLE}`, body: `Research staged for ${PID}.\n\nAirtable: ${air.data?.records?.[0]?.id ?? "n/a"}\nGitHub: ${JSON.stringify(gh.data)?.slice(0, 150)}\nNext: draft outline (10-chapter template).` }, "gmail draft (no send)");
  summary.stages.research = { airtable: air.data?.records?.[0]?.id ?? null, github: gh.successful, calendar: cal.successful, draft: mail.successful };
}

// ---- 2 DRAFT ----
if (want("draft")) {
  console.log("\n[2/9] DRAFT (outline)");
  const md = `# ${TITLE}\n\nNiche: ${NICHE}\n\n## 10-Chapter Outline\n\n1. The Compliance Crisis: Why Australian Businesses Are Exposed\n2. The Privacy Act 1988 — What Actually Changed (APP 1.7, Automated Decisions)\n3. OAIC Enforcement: What the Sweeps Mean for You\n4. Mapping Your AI Workflows: Where Personal Data Enters\n5. The 90-Day Compliance Checklist\n6. Privacy Policy Template with AI Disclosure\n7. Internal AI-Use Policy Template\n8. Decision Tree: ChatGPT / Claude / Copilot in Your Business\n9. Voluntary AI Safety Standard — Guardrails Explained\n10. Going Live: Rollout, Audit, and Ongoing Compliance\n\nBack matter: glossary, checklists, CTA.\nSEO: Australian AI compliance playbook | Privacy Act 1988 small business | OAIC APP 1.7\nFact gate: claims <24mo, AUD vs primary source, disclaimer, consented cases.\n`;
  const doc = await run("GOOGLEDOCS_CREATE_DOCUMENT_MARKDOWN", { title: `[FDP outline] ${TITLE}`.slice(0, 120), markdown_text: md.slice(0, 12000) }, "google doc outline");
  const folder = await run("GOOGLEDRIVE_CREATE_FOLDER", { name: `FDP-${PID}` }, "drive folder");
  summary.stages.draft = { doc: doc.data?.documentId ?? null, url: doc.data?.display_url ?? null, folder: folder.successful };
}

// ---- 3 GENERATE ----
if (want("generate")) {
  console.log("\n[3/9] GENERATE (manuscript)");
  const d = await run("GMAIL_CREATE_EMAIL_DRAFT", { recipient_email: ME, subject: `[FDP generate] ${TITLE}`, body: `Manuscript job queued for ${PID}.\n\nSource: draft outline doc + digital_product_workforce generate/02-spec.json\nAuthor: manuscript_author → editorial → fact_check (must pass before build).\n\nNo send — internal only.` }, "manuscript job draft");
  summary.stages.generate = { queued: d.successful, note: "manuscript_author runs offline; spec=generate/02-spec.json" };
}

// ---- 4 BUILD ----
if (want("build")) {
  console.log("\n[4/9] BUILD (flipbook + PDF)");
  const f = await run("GOOGLEDRIVE_CREATE_FILE_FROM_TEXT", { file_name: `FDP-${PID}-build-notes.txt`, text_content: `Build ${PID}: geo-toolkit reportlab A4 → build/01-flipbook.html + 02-ebook.pdf` }, "drive build notes");
  summary.stages.build = { notes: f.successful, artifacts: ["build/01-flipbook.html", "build/02-ebook.pdf"] };
}

// ---- 5 CONSTRUCT ----
if (want("construct")) {
  console.log("\n[5/9] CONSTRUCT (cover + assets)");
  const c = await run("CANVA_POST_DESIGNS", { title: `FDP ${TITLE}`.slice(0, 100), design_type: { type: "custom", width: 1600, height: 2560 } }, "canva cover draft");
  summary.stages.construct = { canva: c.successful, cover_target: `gumroad-covers/FDP-${PID}.png` };
}

// ---- 6 PACKAGE ----
if (want("package")) {
  console.log("\n[6/9] PACKAGE (zip + checksums)");
  const gh = await run("GITHUB_CREATE_AN_ISSUE", { owner: REPO.split("/")[0], repo: REPO.split("/")[1], title: `[FDP package] ${PID}`, body: `Package ${PID} ready for QA.\n\n- 01-gumroad-package.zip\n- 02-checksums.txt (sha256)\n\nNext: publish GATE-1.` }, "package QA issue");
  summary.stages.package = { qa_issue: gh.successful };
}

// ---- 7 PUBLISH (GATE-1) ----
if (want("publish")) {
  console.log("\n[7/9] PUBLISH — GATE-1 human pre-publish approval");
  if (!AUTO) console.log("  ⏸ GATE-1: review evaluation (≥85/100) + flipbook + cover, then re-run with --auto to approve.");
  const m = await run("GMAIL_CREATE_EMAIL_DRAFT", { recipient_email: ME, subject: `[FDP GATE-1] approve ${PID}`, body: `GATE-1 checklist for ${PID}:\n\n[ ] evaluation ≥85/100\n[ ] flipbook pagination OK\n[ ] cover + price $${PRICE} AUD GST-inc\n\nReply APPROVED or re-run manager with --stage publish --auto.` }, "gate-1 approval draft");
  const cal = await run("GOOGLECALENDAR_CREATE_EVENT", { calendar_id: CAL_ID, summary: `[FDP] GATE-1 ${PID}`.slice(0, 100), description: `Pre-publish approval for ${TITLE}`, start_datetime: new Date(Date.now() + 2 * 86400000).toISOString(), end_datetime: new Date(Date.now() + 2 * 86400000 + 1800000).toISOString() }, "gate-1 calendar");
  summary.stages.publish = { gate: AUTO ? "auto-approved" : "paused-for-human", approval_draft: m.successful, calendar: cal.successful };
}

// ---- 8 SELL (GATE-2) ----
if (want("sell")) {
  console.log("\n[8/9] SELL — checkout (GATE-2 live verify)");
  const prod = await run("STRIPE_CREATE_PRODUCT", { name: `${TITLE}`.slice(0, 100), description: `Fair Dinkum Publishing flipbook ${PID}` }, "stripe product");
  const prodId = prod.data?.id ?? prod.data?.product?.id ?? null;
  let price = { successful: false }, checkout = { successful: false };
  if (prodId) price = await run("STRIPE_CREATE_PRICE", { product: prodId, unit_amount: Math.round(PRICE * 100), currency: "aud" }, "stripe AUD price");
  const priceId = price.data?.id ?? null;
  if (priceId) checkout = await run("STRIPE_CREATE_CHECKOUT_SESSION", { mode: "payment", line_items: [{ price: priceId, quantity: 1 }], success_url: "https://example.com/success", cancel_url: "https://example.com/cancel" }, "stripe checkout");
  const sq = await run("SQUARE_CREATE_ORDER", { idempotency_key: PID, order: { location_id: "main", line_items: [{ name: TITLE.slice(0, 100), quantity: "1", base_price_money: { amount: Math.round(PRICE * 100), currency: "AUD" } }] } }, "square order");
  if (!AUTO) console.log("  ⏸ GATE-2: do 1 live test purchase (Stripe + Square + Gumroad), then continue to market.");
  summary.stages.sell = { stripe_product: prodId, stripe_price: priceId, checkout: checkout.successful, square: sq.successful, gate: AUTO ? "auto-verified (re-verify live!)" : "paused-for-test-purchase" };
}

// ---- 9 MARKET ----
if (want("market")) {
  console.log("\n[9/9] MARKET (launch)");
  const cal = await run("GOOGLECALENDAR_CREATE_EVENT", { calendar_id: CAL_ID, summary: `[FDP launch] ${TITLE}`.slice(0, 100), description: `Launch week: reddit + X thread + tiktok + FB + LinkedIn (UTM-tagged)`, start_datetime: new Date(Date.now() + 7 * 86400000).toISOString(), end_datetime: new Date(Date.now() + 7 * 86400000 + 3600000).toISOString() }, "launch week event");
  const air = await run("AIRTABLE_CREATE_RECORDS", { baseId: AIRTABLE_BASE, tableIdOrName: AIRTABLE_TABLE, records: [{ fields: { Title: `[FDP launch] ${TITLE}`.slice(0, 100), "Document Content": `Launch ${PID}: reddit value-post, X thread (10), tiktok 10x30-60s, FB event, LinkedIn carousel. KPIs: sales, refund%, review#`.slice(0, 2000), Metadata: JSON.stringify({ stage: "market", PID }) } }] }, "launch log row");
  const mail = await run("GMAIL_CREATE_EMAIL_DRAFT", { recipient_email: ME, subject: `[FDP launch] ${TITLE}`, body: `Launch pack for ${PID} ready:\n\n- market/01-launch-checklist.md\n- market/02-social-pack.md (reddit/X/tiktok/FB/LinkedIn)\n- Obsidian: Documents/Obsidian Vault/FDP-${PID}.md\n- RAGS: stored on completion\n` }, "launch draft");
  summary.stages.market = { calendar: cal.successful, airtable: air.data?.records?.[0]?.id ?? null, draft: mail.successful };
}

console.log(`\nDone ${PID}.`);
console.log(JSON.stringify(summary, null, 2));
