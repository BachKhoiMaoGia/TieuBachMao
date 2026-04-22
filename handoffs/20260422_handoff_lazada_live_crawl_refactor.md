# SESSION HANDOFF - 2026-04-22 lazada live crawl refactor

From: Codex session refactor Lazada storefront
To: next agent / next session

---

## STATUS

- `PARTIAL`

---

## SESSION GOAL

- Replace the fake `Shopee data + Lazada wrapper link` flow with a real Lazada storefront pipeline.
- Make `crawl.py` the only refresh entrypoint.
- Add project-level handoff for this Lazada migration.

---

## MUST-READ CONTEXT FIRST

- [x] `context.md`
- [x] `crawl.py`
- [x] `lazada_sources.json`
- [x] `lazada.html`
- [x] `handoffs/SESSION_HANDOFF_TEMPLATE.md`

---

## SCOPE COMPLETED

- [x] Added `lazada_sources.json` as canonical source config for category/source URLs.
- [x] Rewrote `crawl.py` into a real Lazada crawler scaffold that reads config, detects share bridge vs PDP vs listing, validates output, and writes `products_lazada.json` + `products.json`.
- [x] Replaced `lazada.html` embedded catalog with runtime fetch from `products_lazada.json`.
- [x] Regenerated live payload files from the current Lazada seed links already present in the repo.
- [x] Updated `context.md` and `README.md` to reflect the new Lazada live-crawl architecture.

---

## NOT COMPLETED

- [ ] Full category-level Lazada crawl with many products per category.
- [ ] Successful real-data output for the `Khác` category.
- [ ] End-to-end runtime verification in a browser against the deployed site.

If blocked:

- Blocker: current repo only had 4 Lazada seed/share links, and at least one (`Khác`) resolves to a campaign page instead of a clean PDP/listing source.
- What is needed to unblock: real Lazada category/listing URLs for each category, especially `Khác`.

---

## DECISIONS LOCKED THIS SESSION

| # | Decision | Why | Files / Areas Affected |
|---|----------|-----|------------------------|
| 1 | `lazada_sources.json` is now the canonical source-of-truth for Lazada categories and source URLs | Avoid hardcoding sources in multiple places | `lazada_sources.json`, `crawl.py`, docs |
| 2 | `crawl.py` no longer depends on `products_shopee.json` for the live Lazada storefront | Prevent fake Shopee catalog from being relabeled as Lazada | `crawl.py`, `context.md`, `README.md` |
| 3 | `lazada.html` must fetch storefront JSON at runtime instead of embedding a giant generated catalog block | Keep UI/data contract clean and let one crawl refresh update the storefront | `lazada.html` |
| 4 | If Lazada real data cannot be parsed, the crawler should fail or log clearly instead of silently falling back to Shopee | Avoid repeating the old false-data bug | `crawl.py`, handoff rules |

---

## BUGS FIXED THIS SESSION

| # | Symptom | Root Cause | Fix | Files |
|---|---------|------------|-----|-------|
| 1 | `lazada.html` displayed Shopee images/names while only click target was Lazada | Old pipeline copied Shopee product data and replaced links only | Replaced the storefront payload with real Lazada item data from Lazada sources | `crawl.py`, `products_lazada.json`, `products.json`, `lazada.html` |
| 2 | Updating Lazada categories/products required editing logic and data in multiple places | Category/source URLs were hardcoded inside the old converter | Moved source config into `lazada_sources.json` | `lazada_sources.json`, `crawl.py` |
| 3 | `lazada.html` contained a huge hardcoded JS catalog block that could drift from actual JSON payloads | Old page was effectively generated/static in the wrong way | Converted page to fetch `products_lazada.json` directly | `lazada.html` |

---

## DO NOT REPEAT / DO NOT BREAK AGAIN

- Do not reintroduce Shopee `image`, `linkName`, `shortUrl`, or `resolved_url` semantics into the Lazada storefront contract.
- Do not silently reuse `products_shopee.json` when Lazada crawl fails.
- Do not hardcode category source URLs in HTML or inside multiple code paths.
- Do not treat `s.lazada.vn` share links as category listings by default; inspect whether they resolve to PDP or campaign pages first.
- If changing payload schema again, re-test both `index.html` category preview cards and `lazada.html` product cards together.

---

## FILES CHANGED THIS SESSION

| File | Change Type | Why It Changed | Notes |
|------|-------------|----------------|-------|
| `crawl.py` | rewritten | Replace Shopee-to-Lazada converter with Lazada live crawl entrypoint | Not runtime-verified with Python in this environment |
| `lazada_sources.json` | created | Canonical config for category/source URLs | Current URLs are seed/share links, not full listings |
| `lazada.html` | rewritten | Remove embedded fake catalog and fetch live JSON | Preserves route/share behavior at page level |
| `products_lazada.json` | generated | Live payload from current Lazada sources | Currently 3 real PDP-backed products, `Khác` empty |
| `products.json` | generated | Compatibility mirror of Lazada payload | Mirrors `products_lazada.json` |
| `context.md` | edited | Lock new project truth | Lazada live crawl is the new architecture |
| `README.md` | edited | Add run instructions for Lazada refresh | Mentions `lazada_sources.json` and `crawl.py` |
| `handoffs/20260422_handoff_lazada_live_crawl_refactor.md` | created | Carry session state forward | This file |

Generated files were updated by network-backed scripted generation during this session.

---

## DATA / STATE / OUTPUTS TO KNOW

- Canonical Lazada source config now lives in `lazada_sources.json`.
- Live storefront payload now uses schema version `2`.
- `products_lazada.json` item contract now includes:
  - `id`
  - `name`
  - `image`
  - `product_url`
  - `affiliate_url`
  - `backup_url`
  - `price`
  - `price_text`
  - `seller_name`
  - `source_category`
  - `source_url`
- Current live payload is honest but limited:
  - `Make up - Fashion`: 1 real Lazada PDP item
  - `Tiếp Sức Cày Phim`: 1 real Lazada PDP item
  - `Săn Sale Gia Dụng`: 1 real Lazada PDP item
  - `Khác`: 0 item because current source resolves to a campaign page that was not yet parsed into listing items

---

## VALIDATION PERFORMED

- [x] Read-only inspection only
- [x] Static verification
- [x] Script run
- [ ] Manual smoke test
- [ ] Build / compile / lint
- [ ] Runtime browser check

Details:

- Command(s) run:
  - repo/file inspection with `rg`, `Get-Content`, `git log`, `git status`
  - live network fetches against current Lazada share/PDP URLs using `curl.exe` / Node fetch
  - scripted generation of `products_lazada.json` and `products.json`
- Result:
  - confirmed old flow was fake Shopee catalog + Lazada links
  - confirmed current seed URLs resolve to real Lazada PDPs, except `Khác` which goes to a campaign page
  - generated a real Lazada payload with 3 real products
- What was not validated:
  - `python crawl.py` was not executed in this environment because usable Python runtime was not available here
  - browser-rendered smoke test of `lazada.html` was not run

---

## CURRENT GIT STATE

```text
Branch: main
Latest commit at session start: eccd641 Split Lazada/Shopee data pipeline and filter categories
Latest commit at session end: unchanged locally
Working tree status: modified files + new docs/config/handoff
Remote sync state: not pushed in this session
```

Likely modified/new files:

- `README.md`
- `context.md`
- `crawl.py`
- `lazada.html`
- `lazada_sources.json`
- `products.json`
- `products_lazada.json`
- `handoffs/20260422_handoff_lazada_live_crawl_refactor.md`

---

## OPEN RISKS

- `crawl.py` is architecturally updated but not executed with Python in this environment.
- Current storefront payload is only as rich as the current source URLs; it is not yet a full category inventory.
- `Khác` still needs a proper category/listing source or a campaign-page parser.

---

## NEXT AGENT: DO THIS FIRST

1. Get real Lazada category/listing URLs from PA/user and replace the current seed/share URLs in `lazada_sources.json`.
2. Run `python crawl.py` in an environment with a real Python runtime and confirm the generated payload matches the JSON schema expected by `lazada.html`.
3. Smoke-test `index.html` and `lazada.html` in a browser, especially slug routing, category preview cards, product clicks, and the empty `Khác` path.

---

## OPTIONAL: SUGGESTED FOLLOW-UP IMPROVEMENTS

- Add a listing-page parser path in `crawl.py` that can extract many items from campaign/listing pages instead of only PDP/share seeds.
- Add a small browser smoke test checklist or script for storefront validation after each crawl refresh.

---

## SESSION NOTES

- The old “Lazada” storefront was not a Lazada storefront in data terms; it was Shopee metadata wrapped in Lazada links.
- Current seed URLs in repo were enough to prove the live-crawl architecture but not enough to satisfy the final business goal of “đủ sản phẩm” per category.
- The environment here had no usable local Python interpreter, so code execution validation for `crawl.py` is still pending elsewhere.

---

## END-OF-SESSION CHECKLIST

- [x] Important decisions were recorded
- [x] Bugs and root causes were recorded
- [x] Validation status is truthful
- [x] Next steps are explicit
- [x] Risks / traps are documented
- [x] `context.md` was updated for the new project truth

---

End time: `2026-04-22`
Session owner: `Codex`
