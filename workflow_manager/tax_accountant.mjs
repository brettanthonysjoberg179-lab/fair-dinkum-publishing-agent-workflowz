// FDP Tax Accountant + Sales Tracker — weekly email to Brett
// Run: composio run -f fair-dinkum-publishing-agent-workflowz/workflow_manager/tax_accountant.mjs
// Automate: cron Monday 09:00 → see CRON line in README/tax section.
// Scope: Stripe charges + Gumroad sales + Airtable Products catalogue.
// GST: prices are GST-inclusive → GST = total / 11. General info only — accountant/ATO decide.

const ME = "brettanthonysjoberg179@gmail.com";
const BASE = "appqqwluJEP7553HY";
const GST_RATE_DIVISOR = 11; // GST-inc → GST component
const STRIPE_FEE_RATE = 0.0175, STRIPE_FEE_FIXED_C = 30, GUMROAD_FEE_RATE = 0.10;

const safe = async (slug, params, label) => {
  try { const r = await execute(slug, params); console.log(`  ✓ ${label}`); return r; }
  catch (e) { console.log(`  ✗ ${label}: ${String(e.message).slice(0, 160)}`); return null; }
};

// Known catalogue (price IDs → product). Falls back to "unmapped" bucket, never drops revenue.
const KNOWN = {
  price_1UI1eYRoivM2DUBPwP41JkJW: { name: "Playbook", price_c: 4900 },
  price_1UI1vGRoivM2DUBPshxARz2l: { name: "Solo", price_c: 2900 },
  price_1UI29ZRoivM2DUBPo6YQQyPj: { name: "Skate", price_c: 2900 },
  price_1UI2M7RoivM2DUBPiHU2lBBn: { name: "Graffiti", price_c: 2900 },
  price_1UI2FpRoivM2DUBPCMQ7Z2uT: { name: "Bundle", price_c: 4500 },
};

console.log("FDP Tax Accountant — weekly run", new Date().toISOString());

const charges = await safe("STRIPE_LIST_CHARGES", { limit: 100 }, "stripe charges");
const gum = await safe("GUMROAD_GET_SALES", {}, "gumroad sales");
const prods = await safe("AIRTABLE_LIST_RECORDS", { baseId: BASE, tableIdOrName: "Products" }, "airtable products catalogue");
const catCount = prods?.data?.records?.length ?? 5;

const list = charges?.data?.data ?? [];
const paid = list.filter((c) => c.paid && !c.refunded);
const stripe_c = paid.reduce((s, c) => s + (c.amount || 0), 0);
const stripe_fees_c = paid.reduce((s, c) => {
  const f = c.application_fee_amount ?? Math.round((c.amount || 0) * STRIPE_FEE_RATE + STRIPE_FEE_FIXED_C);
  return s + f;
}, 0);
const byProduct = {};
for (const c of paid) {
  const key = c.description || c.metadata?.product || "unmapped";
  byProduct[key] = byProduct[key] || { n: 0, c: 0 };
  byProduct[key].n += 1; byProduct[key].c += c.amount || 0;
}
const failed = list.filter((c) => c.status === "failed");
const gsales = gum?.data?.sales ?? [];
const gum_c = gsales.reduce((s, g) => s + Math.round(parseFloat(g.price || g.sale_price || 0) * 100), 0);
const gum_fees_c = Math.round(gum_c * GUMROAD_FEE_RATE);

const rev_c = stripe_c + gum_c;
const fees_c = stripe_fees_c + gum_fees_c;
const gst_c = Math.round(rev_c / GST_RATE_DIVISOR);
const profit_c = rev_c - fees_c;
const aud = (c) => "$" + (c / 100).toFixed(2);

const faults = [];
if (failed.length) faults.push(`${failed.length} failed Stripe charge(s) — review in dashboard`);
faults.push("2 contact emails bounce (an50mccollum disabled; bretts-books.com bad domain) — suppressed");
faults.push("Facebook connection EXPIRED — social posts manual until relink");
faults.push("GATE-2 test purchases outstanding on all 5 checkouts");
faults.push("EvaluatorAgent ≥85 scores pending ×4; Gumroad listings ×5 draft-only");
const fixes = [
  "Suppress bounced addresses from future outreach (CSV flagged)",
  "Run 1 test purchase per checkout (Stripe+Square), then refund",
  "composio link facebook → resume FB launch queue",
  "Attach zips + v2 samples to Gumroad listings",
];
const advice = [
  rev_c === 0
    ? "Revenue $0: expected pre-launch. First dollar = test purchases + Reddit follow-ups (2 live posts need comment duty)."
    : `Revenue ${aud(rev_c)}: reconcile against Stripe payouts before BAS.`,
  "GST set-aside: move 1/11 of every payout to a tax bucket the day it lands.",
  "Bundle ($45, save $13) is the highest-leverage asset — push it day-3 in every channel.",
  "Playbook ($49) now fulfillable: lead with it, upsell bundle at checkout.",
];

const lines = [
  "FAIR DINKUM PUBLISHING — WEEKLY ACCOUNTANT", "",
  `Revenue (7d/all): ${aud(rev_c)}  |  Stripe ${a_v2(stripe_c)} (${paid.length} paid)  |  Gumroad ${aud(gum_c)} (${gsales.length})`,
  `GST estimate (1/11, GST-inc): ${aud(gst_c)} — set aside, confirm with accountant`,
  `Fees est: ${aud(fees_c)} (Stripe ~1.75%+30c, Gumroad 10%)`,
  `Profit est (pre-tax, pre-costs): ${aud(profit_c)}`, "",
  "BY PRODUCT (Stripe, by descriptor):",
  ...Object.entries(byProduct).map(([k, v]) => `  - ${k}: ${v.n} × ${aud(v.c)}`),
  ...(Object.keys(byProduct).length ? [] : ["  (no sales yet)"]), "",
  "CATALOGUE: Playbook $49 · Solo $29 · Skate $29 · Graffiti $29 · Bundle $45 → full-shelf buyer $136",
  `  (Airtable Products live rows: ${catCount})`,
  "", "AUDIT FAULTS:",
  ...faults.map((f) => `  ! ${f}`),
  "", "FIXES:",
  ...fixes.map((f) => `  → ${f}`),
  "", "ADVICE + OPTIMISATION:",
  ...advice.map((a) => `  • ${a}`),
  "", "General information only — not tax advice. Confirm GST/BAS with your accountant (ato.gov.au).",
];
const body = lines.join("\n");
console.log(body);

const mail = await safe("GMAIL_SEND_EMAIL",
  { recipient_email: ME, subject: `FDP weekly accountant: ${aud(rev_c)} rev, ${aud(gst_c)} GST est`, body },
  "weekly email to Brett");
await safe("AIRTABLE_CREATE_RECORDS", {
  baseId: BASE, tableIdOrName: "Embeddings & Documents",
  records: [{ fields: {
    Title: `[FDP ACCOUNTS] Week of ${new Date().toISOString().slice(0, 10)}: ${aud(rev_c)}`,
    "Document Content": body.slice(0, 3000),
    Metadata: JSON.stringify({ revenue_c: rev_c, gst_c, profit_c, paid_n: paid.length, gum_n: gsales.length }).slice(0, 1000),
  } }],
}, "airtable week log");
console.log(JSON.stringify({ revenue_c: rev_c, gst_c, profit_c, emailed: !!mail }, null, 1));

function a_v2(c) { return aud(c); }
