# Fair Dinkum Publishing — Status Report (2026-09-21)

**Business:** Fair Dinkum Publishing · Brett Sjoberg · ABN 63 590 716 023 · Adelaide SA
**Brand:** Aussie Agent Workflowz · **Pipeline:** 99% automated, 2 human gates
**Manager:** `workflow_manager/fair_dinkum_manager.mjs` (STAGE=research, ready for #5)

## Live catalogue (Stripe livemode, verified)

| # | Product | AUD | Stripe product | Stripe price | Square | Status |
|---|---|---|---|---|---|---|
| 1 | Aussie Agent Workflowz Playbook | 49 | `prod_VIcugUNfw6fbPO` | `price_1UI1eYRoivM2DUBPwP41JkJW` | ✓ | live — test buy pending |
| 2 | Solopreneur OS | 29 | `prod_VIdBsUqzSyGwSt` | `price_1UI1vGRoivM2DUBPshxARz2l` | ✓ | live — test buy pending |
| 3 | History of Skateboarding | 29 | `prod_VIdQSFqt9w3NA4` | `price_1UI29ZRoivM2DUBPo6YQQyPj` | ✓ | live — test buy pending |
| 4 | History of Graffiti | 29 | `prod_VIddCXnfmE3NVJ` | `price_1UI2M7RoivM2DUBPiHU2lBBn` | ✓ | live — test buy pending |
| B | Skate+Graffiti 2-pack | 45 (was 58, save 13) | `prod_VIdWgTaiTbMpLN` | `price_1UI2FpRoivM2DUBPCMQ7Z2uT` | ✓ | live — test buy pending |

Full shelf single-buyer value: **$136 AUD**. Bundle buyer journey: $45 → upsell playbook $49 + solo $29 = **$123**.

## Pipeline proof (per book: research 4/4, draft 2/2, generate/build/construct/package/publish/market)
- Docs: outlines for all 4 (e.g. graffiti `120QyBnV…`, skate `1oPjSktV…`, solo `1vmvJNvM…`) + proof doc `17NgLhtEyRky…`
- Drive folders + build notes · Canva covers 1600×2560 · GitHub QA + research issues (`brettanthonysjoberg179-lab/brett-sjobergs-aussie-agent-workflowz`)
- Calendar: kickoff + GATE-1 + launch-week events · Gmail: research/launch/GATE-1 drafts (zero sends)
- Airtable `appqqwluJEP7553HY / Embeddings & Documents`: 16 records (tracking + research + launch + DONE logs recjky4PzA9VM9Gep, recYoNoqLteQhO9uR, recekVg16X2WxjOF4, recJofKfoRX6EQEAO, reczaeRi7JzDJf1QG)
- RAGS: 10 active memories (business context ids 6–10) · Obsidian: FDP-MUAWUCDY.md, FDP-MUAXBHHK.md + template
- SKU source of truth: `digital_product_workforce/outputs/prod-fairdinkum-*/sell/02-skus.json`

## Solo manuscript (2026-09-21 — COMPLETE)
- 12 files in `book/solopreneurs-os/` (foreword + ch1–10: promise, bulldust, OS, capture, review, fix, money, seen, mistakes, 30 days)
- PDF 16pp + flipbook + zip 22KB (sha `07f7422e…`) · Drive PDF `1vPKbQgm…`, zip `1mUDlzPS…`
- $29 listing now fulfillable · Airtable `recKSi0wvY7VqTDRh`

## Playbook manuscript (2026-09-21 — COMPLETE, debt paid)
- 12 files in `book/aussie-agent-playbook/` (foreword + ch1–10: promise, bulldust, framework, setup, 12 workflows, fix matrix, money, launch, mistakes, 30 days)
- PDF 17pp + flipbook + zip 27KB (sha `8f81aa61…`) · Drive PDF `1CN97rjq…`, zip `1UP42ciA…`
- Full copy gifted to petermckee601 (msg `1a0c34fd5dedd28c`) · $49 listing now fulfillable · Airtable `recbyTahbo1CO0E6J`

## Accountant (2026-09-21 — WEEKLY, automated)
- `workflow_manager/tax_accountant.mjs` — Stripe charges + Gumroad sales + Airtable catalogue → revenue, GST/11 set-aside, fees, profit, audit faults, fixes, advice → Gmail to Brett + Airtable week log
- Cron: `0 9 * * 1` ACST Mondays → `tax_weekly.log` · first run emailed ✓ (baseline $0, honest)
- General info only, not tax advice — accountant/ATO decide

## Deploy (2026-09-22 — PERMANENT Vercel URL, verified live)
- **https://fair-dinkum-shelf.vercel.app** (project `fair-dinkum-shelf`, root + `/sales/` both 200)
- Tunnel URL retired (died in restart, superseded) · Airtable `reczJw4kWMElXGW2p`
- Redeploy: stage site dir, then `vercel deploy --yes --prod` (login persists)
- TODO: custom domain + `success_url` → hub/shelf instead of example.com

## Storefront: Airtable Products = LIVE SHELF (2026-09-21)
- 5 records in `appqqwluJEP7553HY / Products` (Name + Price + Status Done + buy/sample links in Notes):
  Playbook `recnzLoTDFgWvlBjK` · Solo `recVNcmJ9mD52gbMr` · Skate `recLL5UQa0GLjLa98` · Graffiti `recIDGCo0hC2FBRFZ` · Bundle `recQTVj0g3kRZ7pnY`
- Build an Airtable Interface → Gallery on Products for an instant no-code storefront
- Next.js hub port: code-complete but NOT building — pre-existing template breakage (`app/blog/page.tsx` imports missing `./[slug]/page`, template was never wired). Fixed so far: installed next/react/tailwind/radix/supabase. Remaining: template's own missing route. `sales/` static stays the web shelf.

## Hub port (2026-09-21 — CODE-COMPLETE, not build-verified)
- `data/products.ts` (5 live Stripe links + sample URLs), `app/shelf/` + `app/shelf/[slug]/` (static params, metadata), `public/covers+thumbs`, homepage "Browse the ebook shelf" CTA
- Transpile OK (esbuild); full `next build` pending — hub's node_modules is the ebook toolchain (no next installed)
- Live shelf stays `sales/` until: `npm i next react react-dom && npx next build` + deploy · Airtable `rec0UPTodROc9WLRI`

## Sales pages (2026-09-21 — LIVE buy links)
- 5 covers 1600×2560 + 5 thumbs 600×315 (`gumroad-covers/FDP-*`, `gumroad-thumbs/FDP-*`, green/gold, `make_covers.py`)
- `sales/`: index + 5 product pages, real Stripe payment links (`buy.stripe.com/...02`–`06`), public sample downloads
- Payment links minted via `proxy` query-string POST (proxy JSON-wraps bodies — raw slugs can't do payment_links)
- Airtable `recphypQnqMln0qmu` · TODO: `success_url` → book-hub, serve `sales/` or port into Next.js hub

## Free samples v2 (2026-09-21 — PRO pagination, FDPDoc engine)
- Skate ch1: 9pp · Graffiti ch1: 6pp · Playbook/Solo teasers: 3pp each
- Cover no-folio → content opens p.1 with running heads → buy CTA closer
- Drive: playbook `1c6YEq7d…`, solo `1_tajUSf…`, skate `1JS_beQC…`, graffiti `15hEoyV…`
- Builder `build_samples.py` v2 · Airtable `recEWKT7CLfj7F5aa`

## Free samples (2026-09-21 — lead magnets, in Drive)
- Skate ch1: 23KB `1gdLa8PI1ixKs5ziV1HWzYh4rsAd3Ezpv` · Graffiti ch1: 14KB `1JRvZImu_PVKOvnwO-A3ZVELI0tzWZ1eV`
- Playbook teaser: 3KB `1sou6ktpwBrFEBF_rAp4OcgN5Pxj1LQ4p` · Solo teaser: 3KB `18DD-upkshIniAjerbBxQnwKZGX3B72m_`
- All `build/03-sample.pdf` w/ buy CTA · builder `build_samples.py` · Airtable `recAWMyga8Lzm59YJ`
- Use: attach to Gumroad listings as free preview + email to curious contacts

## Go-live (2026-09-21 — Reddit LIVE, Facebook blocked)
- 🔴 LIVE r/skateboarding: https://www.reddit.com/r/skateboarding/comments/1wm6z5b/ (Discussion flair, 65-char title limit hit, shortened)
- 🔴 LIVE r/Graffiti: https://www.reddit.com/r/Graffiti/comments/1wm6zcl/
- 🔵 Facebook NOT posted — connection EXPIRED (`facebook_shirt-exter`). Fix: `composio link facebook`, then paste FB packs from 02-social-pack.md files
- Airtable `recadveduPNVL3JXf` · Next: first-5-comments duty on both posts, then X/TikTok/LinkedIn

## Launch packs (2026-09-21 — drafts only, nothing posted)
- Skate `market/02-social-pack.md` (reddit/X7/TikTok3/FB/LinkedIn, UTM) + `01-launch-checklist.md`
- Graffiti `market/02-social-pack.md` (+ bundle day-3 push) + `01-launch-checklist.md`
- Airtable `recPrVgWGR14LhFwy` · Gmail launch draft ready · Go-live needs explicit GO (public posts)

## Package (2026-09-21 — Gumroad zips, sha256, in Drive)
- Skate: `01-gumroad-package.zip` 308KB (sha `1090a678…`), Drive `1ynrMNEsgC5JozQSCfgkmALmdFqfjlxEa`
- Graffiti: `01-gumroad-package.zip` 202KB (sha `2948b37c…`), Drive `10tsoa2hV69rW5HftIApMFGYuB4NjGELn`
- Each: PDF + flipbook + README · checksums in `package/02-checksums.txt` · Airtable `recwHsrQ7yTwErTBn`

## Build artifacts v2 (2026-09-21 — PROFESSIONAL pagination)
- Engine: `FDPDoc` (BaseDocTemplate): cover no-folio → front roman (i, ii…) → body arabic (1, 2…), chapters open on fresh pages, running heads (title verso / chapter recto), opener pages centred folio, dot-leader TOC via multiBuild
- Verified: skate **114 pages**, graffiti **77 pages**, TOC page numbers resolve, roman folio on contents
- Skate PDF `1yxDj0NAaxBE88vCzUCBthtQQMreFDofB` (304KB) · zip 314KB (sha `f71163fb…`) Drive `1V0nBoa2dmNZZjlK-v-eQI1EJxlyVoz5m`
- Graffiti PDF `1D4X-Cr7LSRnOBZYv3NW6HZcHSMxCa4-x` (199KB) · zip 206KB (sha `09064ac9…`) Drive `1HE1T1tdAfSgLGrRl2xMNKT6Gb1T6F98R`
- Pageless counterpart: `01-flipbook.html` reflowable readers (302/203KB) — pagination for print/Gumroad, pageless for web
- Airtable `rec3K1MSs0JFDFdVR`

## Build artifacts (2026-09-21 — real PDFs, reportlab A4)
- Skate: 18ch, `prod-fairdinkum-ebook-003/build/02-ebook.pdf` (293KB) + `01-flipbook.html` (302KB) · Drive `1LocL5-wiryvr9zHrAiKLl3RMEMQjGPrY`
- Graffiti: 16ch, `prod-fairdinkum-ebook-004/build/02-ebook.pdf` (192KB) + `01-flipbook.html` (203KB) · Drive `1xXFVrIguU32FNIJ7Qlqpr6BoofK-kOiW`
- Builder: `workflow_manager/build_ebook_pdf.py` (`skate|graffiti|all`) · Airtable `recYqWulaFGUUaAEt`
- Playbook + Solo PDFs: queued (manuscripts to write first)

## Manuscript readiness
- Skate: 10/10 chapters exist (`book/the-history-of-skateboarding/`) ✅
- Graffiti: 12/12 chapters exist (`book/the-history-of-graffiti/`) ✅
- Playbook: brief + outline, manuscript to write · Solo: brief + outline, manuscript to write

## To revenue (in order)
1. [ ] Test purchases: playbook $49, solo $29, bundle $45 (covers skate single), graffiti $29 — then refund
2. [ ] Checkout `success_url` → fair-dinkum-book-hub (currently example.com)
3. [ ] Gumroad listings ×5 (SKUs FDP-AAW-001-GUM, FDP-SOLO-002-GUM, FDP-SKATE-003-GUM, FDP-GRAF-004-GUM, FDP-BUNDLE-001-GUM)
4. [ ] Build PDFs: skate + graffiti first (manuscripts exist) via geo-toolkit → `build/02-ebook.pdf`
5. [ ] EvaluatorAgent ≥85 → `publish/01-evaluation-report.json` ×4
6. [ ] Launch week: reddit/X/tiktok/FB/LinkedIn packs (market drafts ready)

## 30-day math (illustrative, AUD, pre-fees)
- 10 bundles ($450) + 5 playbooks ($245) + 5 solos ($145) = **$840**
- Stripe AU fee ≈ 1.75% + 30¢ → net ≈ **$810** · Gumroad (10%) only on gumroad-channel sales
- Costs: $0 marginal (digital) + sunk time + Canva/Drive free tier
