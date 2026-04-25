# TieuBachMao Project Context

Last updated: 2026-04-25 (Lazada end-to-end refresh with migration playbook)
Repo: `BachKhoiMaoGia/TieuBachMao`
Primary branch: `main`
Deploy target: GitHub Pages static site
Canonical remote: `https://github.com/BachKhoiMaoGia/TieuBachMao.git`

---

## 1. Project Purpose

This repo is the public static landing site for the `Tiểu Bạch Mao` brand/community.

It currently serves 3 business functions:

1. Bio-link landing page for traffic from TikTok/social channels.
2. Traffic router to owned destinations:
   - TikTok accounts
   - Telegram
   - Facebook group/page
   - YouTube
   - main film website
   - donation links
3. Affiliate storefront for product recommendation traffic, currently centered on live Lazada product data.

This is not a framework app. It is a static HTML/CSS/JS site with a small Python data pipeline.

---

## 2. Current Runtime Architecture

### 2.1 Public entrypoints

- `index.html`
  - Main landing page.
  - Contains most styling inline in `<style>`.
  - Renders social links, donation block, and Lazada category cards.
  - Fetches `products_lazada.json` client-side to build category preview cards.

- `lazada.html`
  - Main affiliate storefront page currently in use.
  - Shows products by category with tab navigation.
  - Supports category-specific deep links via query slug and clean path logic.
  - Fetches `products_lazada.json` at runtime instead of embedding catalog data inline.

- `shopee.html`
  - No longer the active storefront.
  - Now acts as a redirect shim to Lazada routes/pages for backward compatibility.

- `404.html`
  - Static fallback page for deployment.

### 2.2 Static assets

- Favicons: `favicon.ico`, `favicon-32x32.png`, `favicon-192x192.png`, `favicon-512x512.png`, `apple-touch-icon.png`
- Brand/media assets: `Asset 3.webp`, `og-image.jpg`, `Telepost.png`, `Thumnailweb.png`
- Domain config: `CNAME`

### 2.3 Legacy / alternate files

- `linkbio_tieubachmao.html`
  - Snapshot/variant of landing UI.
  - Not the main runtime entrypoint unless explicitly repurposed later.

- `style.css`
  - Older styling layer for older templates/variants.
  - Current live pages rely mostly on inline CSS inside HTML files instead.

- `template-1-minimal/`, `template-2-neon/`, `template-3-card/`
  - Design alternatives / historical templates.
  - Not part of the active deployment flow unless intentionally revived.

---

## 3. Data Pipeline Overview

The current pipeline is split into two stages:

1. Crawl Shopee affiliate source data.
2. Crawl/normalize Lazada source URLs into the Lazada storefront dataset used by the live site.

### 3.1 Stage A: Shopee source crawl

File: `crawl_shopee.py`

Responsibilities:

- Calls `https://collshp.com/api/v3/gql/graphql`
- Fetches affiliate group/category metadata for storefront suffix `tieubachmao`
- Fetches products per group
- Fetches all products to infer uncategorized items
- Resolves Shopee short links
- Writes `products_shopee.json`
- Historically generated a full `shopee.html` storefront page

Important note:

- `crawl_shopee.py` is the source-of-truth generator for raw affiliate catalog structure.
- It still reflects Shopee-origin metadata even though the public storefront has migrated to Lazada.

### 3.2 Stage B: Lazada live crawl

File: `crawl.py`

Responsibilities:

- Reads `lazada_sources.json`
- Crawls real Lazada source URLs
- Auto-detects share bridge URLs vs PDP URLs vs listing URLs where possible
- Preserves source-level and category-level Lazada fallback links in normalized output
- Normalizes live product data into storefront payload format
- Writes `products_lazada.json`
- Mirrors output to `products.json` for backward compatibility

This script is now the canonical Lazada storefront pipeline.
It must not silently fall back to Shopee-origin product data for live Lazada output.

Current checkpoint reality:

- PDP-style share links are the only reliable item-level sources confirmed in this environment.
- `member-window` and campaign-style links can be resolved and classified, but are not yet producing guest-visible multi-item feeds through the current static HTML parse path.
- The crawler now keeps those Lazada-native fallback links in the payload/config instead of discarding them.

### 3.3 Lazada source config

File: `lazada_sources.json`

Responsibilities:

- Declares storefront category order
- Stores category slugs and source URLs
- Stores Lazada-native source roles such as `main`, `backup`, and repo-level global fallback URLs
- Acts as the single config file to edit when new Lazada sources are added
- Allows future replacement of current seed/share URLs with richer category/listing URLs without changing crawler architecture

Current configured source graph:

- Each approved category has:
  - one main Lazada share link
  - one backup `member-window` link
  - optional `sources` array for manually added product-level Lazada affiliate short links
- Current `sources` counts after the 2026-04-25 end-to-end refresh:
  - `Make up - Fashion`: 10 links
  - `Tiếp Sức Cày Phim`: 11 links
  - `Săn Sale Gia Dụng`: 4 links
  - `Khác`: 0 links
- Repo-level global fallbacks currently include:
  - `https://s.lazada.vn/s.9h2Cr?t=h5-v2_6SrXCyYmkR`
  - `https://s.lazada.vn/s.9h2y5`

### 3.4 Lazada product-link helper

File: `add_product.py`

Responsibilities:

- CLI helper for adding Lazada affiliate short links to `lazada_sources.json`
- Accepts either one link or a text file with one link per line:
  - `python add_product.py "https://s.lazada.vn/s.xxxx?t=p-xxx"`
  - `python add_product.py links.txt`
- Resolves Lazada short links to final Lazada URLs
- Fetches product HTML with `requests` and `beautifulsoup4`
- Extracts product title and breadcrumb/category hints where available
- Suggests one of the four approved storefront categories by keyword matching
- Prompts the operator to confirm or override the category
- Appends the original affiliate short link under the selected category's `sources` array
- Creates `sources` beside `main` / `backup` when the key does not exist
- Was batch-tested on 2026-04-25 with 25 real Lazada affiliate links; all links resolved and were appended to `lazada_sources.json`

Important notes:

- `add_product.py` only edits source config.
- It does not run `crawl.py`.
- It does not regenerate `products_lazada.json` or `products.json`.
- Newly added `sources` links do not appear on the live storefront until the crawler/generator path is updated or verified to consume them and the payload files are regenerated intentionally.
- Dependencies are tracked in `requirements.txt`: `requests`, `beautifulsoup4`.
- Keep UTF-8 read/write behavior intact because category names and product titles contain Vietnamese text.

### 3.5 Current active data files

- `products_shopee.json`
  - Legacy Shopee-source dataset
  - No longer the upstream source for the live Lazada storefront
  - Keep only as archival / fallback reference unless product direction explicitly revives it

- `products_lazada.json`
  - Canonical live dataset for the current storefront UI
  - This is the file `index.html` reads for category cards
  - This is the data basis for the active Lazada shopping experience
  - Current honest payload after the 2026-04-25 end-to-end refresh is:
    - 11 real PDP-backed items for `Make up - Fashion`
    - 11 real PDP-backed items for `Tiếp Sức Cày Phim`
    - 4 real PDP-backed items for `Săn Sale Gia Dụng`
    - 0 item for `KhÃ¡c`
    - 1 dropped item remains in the payload report because no valid Lazada image was parsed
    - 1 source currently resolves to a PDP but did not expose parseable product data during the final crawl

- `lazada_link_errors.md`
  - Tracks source links that did not become valid product cards in the latest crawl
  - Current tracked issues:
    - `https://s.lazada.vn/s.ljrQD?t=p-i3czEE8-sHju5kk`: PDP resolved but product data was not parseable
    - `https://s.lazada.vn/s.ljrAt?t=p-i1zCzr6-s8xQ9EG`: item parsed but dropped because no valid Lazada image was found
    - `https://s.lazada.vn/s.9hddF?t=ntv-v1_alp-native`: campaign/landing source did not expose guest-visible listing items

- `products.json`
  - Mirror of Lazada output
  - Exists for compatibility
  - Do not treat as the canonical source unless a legacy page explicitly depends on it

---

## 4. Canonical Category Rules

The current live storefront is intentionally restricted to these categories:

1. `Make up - Fashion`
2. `Tiếp Sức Cày Phim`
3. `Săn Sale Gia Dụng`
4. `Khác`

Legacy alias handling:

- `Săn Sale Đón Tết` must normalize to `Săn Sale Gia Dụng`

Important implications:

- `products_shopee.json` may still contain categories such as:
  - `Decor Góc Xem Phim`
  - `Phụ Kiện Điện Thoại`
- These are intentionally excluded from the current live Lazada experience unless product/business direction changes.

Do not “fix” this filtering accidentally.
It is a product decision, not a missing-data bug.

---

## 5. Frontend Behavior That Must Stay Correct

### 5.1 `index.html`

Must continue to:

- Render as a lightweight static landing page without build tooling
- Load `products_lazada.json` client-side
- Show only allowed categories
- Map category cards to `lazada.html?slug=...`
- Keep donation copy/open behavior working
- Keep fallback behavior if category JSON cannot load

### 5.2 `lazada.html`

Must continue to:

- Open category tabs properly
- Support:
  - `?slug=...`
  - clean-path slug parsing
  - all-products fallback
- Filter out disallowed categories even if present in payload
- Normalize `Săn Sale Đón Tết` to `Săn Sale Gia Dụng`
- Prefer `affiliate_url` for primary click behavior
- Keep `backup_url` / `fallback_urls` compatible with current and future fallback handling
- Preserve share URL generation behavior
- Preserve backward-compatible handling for paths migrated from old Shopee routes

### 5.3 `shopee.html`

Must remain a redirect compatibility layer unless there is an explicit decision to restore a Shopee storefront.

Do not reintroduce a conflicting second storefront accidentally.

---

## 6. Git State and Recent History

As of 2026-04-22:

- Branch checked: `main`
- Repo status: clean working tree at time of analysis
- `HEAD` matched `origin/main`

Latest commit at review time:

- `eccd641` `Split Lazada/Shopee data pipeline and filter categories`

Recent visible commit history:

- `eccd641` Split Lazada/Shopee data pipeline and filter categories
- `f0be13d` Fix category card URLs to lazada query route
- `673be66` Update Facebook links and fix Lazada card fallback flow
- `f9d34bf` Migrate Shopee routes to Lazada and add link fallback
- `5f66edd` Add product image previews to Shopee category cards

Interpretation:

- The project recently migrated from a Shopee-facing storefront to a Lazada-facing storefront.
- Route compatibility and fallback behavior are now important historical constraints.

---

## 7. Deployment and Repo Safety

### 7.1 Deployment

File: `.github/workflows/pages.yml`

Behavior:

- Deploys the repo to GitHub Pages on push to `main`
- Uploads the whole repo root as the Pages artifact

Operational consequence:

- Any file added at repo root can become part of deploy output unless ignored by deployment changes later.

### 7.2 Secret scanning

Files:

- `.github/workflows/secret-scan.yml`
- `.githooks/pre-push`
- `scripts/install-hooks.sh`
- `scripts/scan-secrets.sh`

Behavior:

- CI scans tracked files for obvious token/cookie/password patterns
- Local `pre-push` hook can block bad pushes before remote push

Operational consequence:

- Do not commit experimental credentials or copied cookies into this repo
- If editing scripts, preserve the safety role of the scan flow

---

## 8. Encoding and Environment Notes

Important:

- Source files are intended to be UTF-8.
- In constrained PowerShell environments, Vietnamese may display as mojibake in terminal output.
- Do not assume the repo files are corrupted just because terminal rendering looks wrong.

Rule:

- Verify by file semantics and encoding-aware editors before performing mass text “cleanup”.
- Avoid broad search/replace on Vietnamese content unless you have confirmed actual file corruption.

---

## 9. Important Files Map

### Core runtime

- `index.html`
- `lazada.html`
- `shopee.html`
- `products_lazada.json`
- `products.json`
- `lazada_link_errors.md`
- `CNAME`

### Data pipeline

- `crawl_shopee.py`
- `crawl.py`
- `add_product.py`
- `lazada_sources.json`
- `products_shopee.json`
- `requirements.txt`

### Repo/process

- `README.md`
- `docs/lazada-migration-playbook.md`
- `.github/workflows/pages.yml`
- `.github/workflows/secret-scan.yml`
- `.githooks/pre-push`
- `scripts/install-hooks.sh`
- `scripts/scan-secrets.sh`

### Non-canonical / legacy / reference-only

- `linkbio_tieubachmao.html`
- `style.css`
- `template-1-minimal/*`
- `template-2-neon/*`
- `template-3-card/*`

---

## 10. Decisions Already Locked In

These are not to be casually reversed:

1. The live storefront is Lazada-first, not Shopee-first.
2. `lazada_sources.json` is the upstream source config for the live Lazada storefront.
3. `products_lazada.json` is the live storefront data source.
4. `products.json` is compatibility mirror data, not primary truth.
5. Category exposure is intentionally filtered to 4 approved groups.
6. `shopee.html` is currently a redirect compatibility shim.
7. Backward compatibility for migrated routes matters.
8. GitHub Pages deploys directly from this repo without a separate build step.

If any of these change, the change must be explicitly documented in both:

- `context.md`
- the session handoff for that work

---

## 11. Known Risks and Easy Regression Traps

### Trap 1: Mistaking mirror data for source-of-truth

- Editing only `products.json` is usually wrong.
- If live data changes, inspect whether `products_lazada.json` and/or source generation scripts must change too.

### Trap 2: Re-enabling legacy categories by accident

- Some categories exist in source data but are intentionally hidden.
- Do not “restore missing categories” unless product direction explicitly asks for it.

### Trap 3: Breaking migrated route behavior

- Lazada page logic currently handles old Shopee-linked patterns.
- Route cleanup must preserve old traffic links where possible.

### Trap 4: Rebuilding styling from scratch without cause

- Current pages are handcrafted static pages with inline CSS.
- Avoid introducing a build stack or refactor churn unless explicitly requested.

### Trap 5: Confusing unused templates with live code

- `template-*` directories are not the active site.
- Do not spend time fixing them unless task scope explicitly includes them.

### Trap 6: “Fixing” mojibake that only exists in terminal output

- Confirm actual file encoding before changing Vietnamese text.

### Trap 7: Breaking Pages deploy by moving runtime files

- Because Pages uploads the repo root directly, renaming or moving entry files has deploy consequences immediately.

---

## 12. Non-Negotiable Agent Rules For This Repo

When handing this repo to a new agent, these rules should be treated as mandatory:

1. Read `context.md` before making structural changes.
2. Check `git status --short --branch` before editing.
3. Check latest commit and recent handoff before touching routing, data pipeline, or category logic.
4. Treat `products_lazada.json` as live display data.
5. Treat `lazada_sources.json` as the upstream source config for the live Lazada storefront.
6. Do not remove backward-compatible Lazada/Shopee route handling unless explicitly requested.
7. Do not reintroduce hidden categories without an explicit product decision.
8. Do not mass-edit Vietnamese copy based only on broken terminal rendering.
9. Document any important decision in the session handoff.
10. If a bug is fixed, record:
   - symptom
   - root cause
   - files touched
   - what must not be broken again
11. Do not claim `member-window` or campaign sources already yield full product feeds unless real parsed output was verified.
12. Do not replace a working PDP affiliate URL with a generic campaign fallback when item-level Lazada data already exists.

---

## 13. Recommended Change Workflow

For product/UI changes:

1. Inspect `index.html` and/or `lazada.html`
2. Identify whether the change is:
   - pure markup/CSS/JS
   - data-driven
   - route-driven
3. Verify whether any JSON payload assumptions change
4. Verify route/share/fallback behavior after edits
5. Update handoff with regressions to watch

For data/catalog changes:

1. Determine whether the requested change belongs in:
   - source crawl
   - conversion
   - output data only
2. Use `add_product.py` when the task is only to append product affiliate short links into `lazada_sources.json`
3. Prefer changing generator logic over hand-editing generated outputs when repeatability matters
4. If output files are regenerated, state that clearly in the handoff
5. For Lazada fallback sources, distinguish clearly between:
   - URL resolution success
   - HTML parse success
   - guest-visible item extraction success
   - signed runtime/API extraction success

For route changes:

1. Inspect old compatibility logic first
2. Preserve existing inbound links unless explicit migration says otherwise
3. Call out any URL behavior change in the handoff

---

## 14. Validation Checklist After Meaningful Changes

Use this checklist whenever a session changes runtime behavior:

- `index.html` still loads and renders key cards
- category cards still populate from `products_lazada.json`
- allowed category filtering still holds
- `lazada.html` still opens category tabs correctly
- `lazada.html` no longer contains embedded Shopee-era catalog data
- slug route / query route still resolves to expected category
- share button still generates expected URL
- fallback link logic still works
- `shopee.html` redirect still works if touched
- JSON payload structure remains compatible with frontend expectations
- Pages deploy assumptions are still valid
- any claim about `member-window` / campaign coverage states explicitly whether the result is:
  - no items
  - partial items
  - full items

If data pipeline files changed:

- output file names are unchanged unless intentionally migrated
- category alias normalization still works
- mirror behavior to `products.json` is still intentional

---

## 15. Handoff Requirements For Every Future Session

Every meaningful work session should leave a handoff file under `handoffs/`.

Minimum required contents:

1. Session status
2. Goal/scope
3. Files read first
4. What changed
5. Decisions made
6. Bugs fixed and root causes
7. Regressions to avoid
8. Validation performed
9. Open risks / unfinished work
10. Exact next steps for the next agent

Recommended template:

- `handoffs/SESSION_HANDOFF_TEMPLATE.md`

---

## 16. Suggested Future Documentation Improvements

These are good future upgrades but not mandatory right now:

1. Add a small `docs/data-flow.md` diagram if pipeline complexity grows.
2. Split generated vs hand-authored files more explicitly.
3. Add a tiny maintenance command section in `README.md`.
4. Add a deploy smoke-check checklist after Pages publish.

---

## 17. Quick Summary For A New Agent

If you have only one minute:

- This is a static GitHub Pages site for `Tiểu Bạch Mao`.
- `index.html` is the main bio landing page.
- `lazada.html` is the active affiliate storefront.
- `shopee.html` is now a redirect compatibility page.
- `crawl.py` is the real Lazada storefront crawler.
- `add_product.py` is a CLI helper for appending Lazada affiliate links into `lazada_sources.json`; it does not regenerate storefront data.
- `lazada_sources.json` is the category/source config file.
- Live storefront categories are intentionally limited to 4 groups.
- `products_lazada.json` is the important live data file.
- `products_shopee.json` is legacy, not the live Lazada source anymore.
- Current checkpoint ships 26 real PDP-derived Lazada products; `member-window` and campaign fallbacks are configured but not yet producing full parsed feeds.
- `docs/lazada-migration-playbook.md` documents the reusable Shopee => Lazada replacement method for other static web systems.
- Be careful with route compatibility, category filtering, false mojibake fixes, and overclaiming fallback coverage.
