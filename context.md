# TieuBachMao Project Context

Last updated: 2026-10-24
Repo: `BachKhoiMaoGia/TieuBachMao`
Primary branch: `main`
Deploy target: GitHub Pages static site (`https://gocphimtieubach.page`)
Canonical remote: `https://github.com/BachKhoiMaoGia/TieuBachMao.git`
Current handover: `handoffs/20261024_current_state.md`

---

## 1. Project Identity & Purpose

This repo is the official public static website for the `Tiểu Bạch Mao` brand/community.

> **CRITICAL DISTINCTION:**
> - This repository is `BachKhoiMaoGia/TieuBachMao.git` located at `/home/dp/workspace/projects/active/gocphimtieubach.page`.
> - Do **NOT** confuse it with the video translation/tool repository `ToolTBM.git` located in the `TieuBachMao` workspace.
> - This is **NOT** a framework app. It is built strictly with Vanilla HTML5, CSS3, and JavaScript, deploying directly to GitHub Pages without any bundler or build step.

### Active Roles
1. **Bio-link Landing Page (`index.html`):**
   - High-traffic mobile/desktop portal from TikTok and other social channels.
   - Traffic router to owned channels: TikTok accounts, Telegram, Facebook group/page, YouTube, main film website (`gocphimtieubach.studio`), and TPBank donation.
   - **Voluntary shopping links:** Two direct affiliate anchors (TikTok Shop & Lazada) placed below the bio header and above the social links.
2. **Dedicated Storefront Page (`lazada.html`):**
   - Multi-category affiliate storefront for deep product browsing, loading data dynamically from `products_lazada.json`.
   - Kept intact as a secondary destination accessible via direct link or query slug.

---

## 2. Current Architecture & Rules by Component

### 2.1 The Landing Page (`index.html`) — Canonical Truth
- **Single Source of Truth for Landing:** Contains all HTML markup, inline `<style>`, and minimal inline `<script>`. No external JS script imports.
- **Voluntary Shop Links Block:**
  - Located under the header, before the social cards section.
  - Features friendly copy requesting community support via shopping commissions.
  - **TikTok Shop:** `https://vt.tiktok.com/ZS9UwsBsuFLKt-KD8oG/` (`target="_blank" rel="noopener sponsored"`).
  - **Lazada:** `https://s.lazada.vn/s.pl59e?t=h5` (`target="_blank" rel="noopener sponsored"`).
  - Edit URLs directly in `index.html`.
  - Decorated with inline SVGs (16×16px, `currentColor`, `aria-hidden="true"`, `focusable="false"`) for the header heart and both shopping carts.
- **Strict Interaction Contract:**
  - **NO popups, NO companion tabs, NO random URLs:** Clicking either shop link opens only that destination.
  - **Original links strictly preserved:** Clicking Social links or Film website opens only that target. Never trigger affiliate navigation in the background.
  - **Donation Block:** Clicking the copy button copies `TPBank · 22992011295` directly to the system clipboard and displays `#donateToast` ("Đã copy thông tin TPBank"). Opens **0** popups/tabs.
  - **NO landing catalog fetch:** `index.html` does **NOT** fetch `products_lazada.json` or render product cards. This keeps landing load instant and lightweight.
- **Responsive Layout:**
  - Fully verified across 320px, 375px, 390px, and 1440px viewports.
  - Horizontal overflow is zero (`scrollWidth === clientWidth`).
  - Badge and long titles have guaranteed wrapping and spacing ($\ge 10\text{px}$) to prevent overlap.
  - Shop buttons maintain touch target $\ge 44\text{px}$.
  - *Note:* Verified via clean headless Chrome automation; physical mobile device feel and live affiliate commission attribution remain pending verification.

### 2.2 Secondary / Retained Runtime Files
These files remain active in the repository for specialized routes and backward compatibility, outside the main landing loop:

- **`lazada.html`:**
  - The live multi-category affiliate storefront.
  - Loads `products_lazada.json` client-side at runtime.
  - Supports category navigation via tab buttons, `?slug=...` query param, and path slug parsing.
  - Filters allowed categories down to 4 approved groups (`Make up - Fashion`, `Tiếp Sức Cày Phim`, `Săn Sale Gia Dụng`, `Khác`).
- **`shopee.html`:**
  - Retained as a redirect compatibility shim to redirect legacy incoming Shopee traffic to `lazada.html`.
- **`404.html`:**
  - Static fallback page for GitHub Pages.
- **`CNAME`:**
  - Configures custom domain `gocphimtieubach.page`.

---

## 3. Data Pipeline & Crawler (Reference Guide)

> ⚠️ **OPERATIONAL RULE:** Do **NOT** run crawlers during document cleanup or landing page maintenance sessions.

### 3.1 Lazada Storefront Pipeline (`crawl.py`)
- Upstream source configuration: `lazada_sources.json`.
- Output datasets:
  - `products_lazada.json`: Live data consumed by `lazada.html`.
  - `products.json`: Mirror compatibility copy.
- To append new affiliate links into config:
  ```bash
  python add_product.py "https://s.lazada.vn/s.xxxx?t=p-xxx"
  # Or batch from file:
  python add_product.py links.txt
  ```
  *(Note: `add_product.py` only updates `lazada_sources.json`; it does NOT run the crawler or modify output JSON).*
- To regenerate live payload:
  ```bash
  python crawl.py
  ```
- Track unparseable / dropped links in `lazada_link_errors.md`.

### 3.2 Legacy Shopee Crawler (`crawl_shopee.py`)
- Historical crawler reading Shopee GraphQL API and writing `products_shopee.json`.
- **WARNING:** Running `crawl_shopee.py` can regenerate a standalone `shopee.html` and overwrite the redirect shim. Do not execute unless explicitly tasked with restoring a Shopee storefront.

---

## 4. Locked Decisions & Discarded Experiments

### ✅ Locked Decisions:
1. Landing page displays voluntary shop links only; no automated popup tabs.
2. SVG icons used for shopping block; site emojis elsewhere preserved.
3. Live storefront categories on `lazada.html` restricted to 4 approved groups.
4. Deployment is static directly from repo root via GitHub Pages.

### ❌ Discarded / Superseded Experiments:
1. **Random Affiliate Companion Tab Experiment (2026-10-23):**
   - Attempted to open background affiliate tabs on arbitrary clicks via `site-config.js` and `assets/js/affiliate.js`.
   - **CANCELED AND REMOVED:** Scripts deleted from repo. Handoff archived at `handoffs/archive/20261023_affiliate_experiment.md` with `SUPERSEDED` status. Never re-introduce.
2. **Framework / Monorepo Migration Plan:**
   - Canceled. Site remains static HTML/CSS/JS without build tooling.

---

## 5. Security & Deployment

- **Deployment Workflow:** `.github/workflows/pages.yml` triggers on push to `main` and uploads repo root directly to GitHub Pages.
- **Secret Scanning:**
  - `.github/workflows/secret-scan.yml` enforces CI scanning.
  - Local pre-push hook: `bash scripts/install-hooks.sh`.
  - Manual check: `bash scripts/scan-secrets.sh`.
  - Do not hardcode tokens, cookies, or credentials.

---

## 6. Non-Negotiable Agent Rules for this Repo
1. Read `handoffs/20261024_current_state.md` and `context.md` before starting work.
2. Check `git status` before and after any change.
3. Never use `git add .` or `git add -A`.
4. Keep `.agents/` and `CONTEXT.md` untouched and untracked.
5. Do not modify `index.html` to fetch JSON or restore popups without explicit user instruction.
6. Verify changes with `git diff --check` and `bash scripts/scan-secrets.sh` before committing.
