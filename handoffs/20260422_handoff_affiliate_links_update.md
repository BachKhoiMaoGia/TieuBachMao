# SESSION HANDOFF - 2026-04-22 affiliate links update

From: Codex session affiliate-link data update
To: next agent / next session

---

## STATUS

- `COMPLETED FOR REQUESTED SCOPE`

---

## SESSION GOAL

- Update Lazada affiliate links cleanly without touching architecture.
- Limit changes to:
  - `lazada_sources.json`
  - `products_lazada.json`
- Keep `shopee.html` redirect shim untouched.

---

## LINKS UPDATED

### Category config in `lazada_sources.json`

- `make-up-fashion`
  - main: `https://s.lazada.vn/s.9hdZy?t=p-i3bSXYZ-sHY12BX`
  - backup: `https://s.lazada.vn/s.9hdaN?t=h5-v2_member-window`
- `tiep-suc-cay-phim`
  - main: `https://s.lazada.vn/s.9hdYL?t=p-i3dMmgt-sHnNHUF`
  - backup: `https://s.lazada.vn/s.9hdaN?t=h5-v2_member-window`
- `san-sale-gia-dung`
  - main: `https://s.lazada.vn/s.9hdYa?t=p-i2ccxHM-sCoH6Q5`
  - backup: `https://s.lazada.vn/s.9hdaN?t=h5-v2_member-window`
- `khac`
  - main: `https://s.lazada.vn/s.9hddF?t=ntv-v1_alp-native`
  - backup: `https://s.lazada.vn/s.9hdaN?t=h5-v2_member-window`

### Global fallbacks in `lazada_sources.json`

- `https://s.lazada.vn/s.9h2Cr?t=h5-v2_6SrXCyYmkR`
- `https://s.lazada.vn/s.9h2y5`

### Product data in `products_lazada.json`

Updated `affiliate_url` only for the 3 existing items:

- `Make up - Fashion` item -> `https://s.lazada.vn/s.9hdZy?t=p-i3bSXYZ-sHY12BX`
- `Tiếp Sức Cày Phim` item -> `https://s.lazada.vn/s.9hdYL?t=p-i3dMmgt-sHnNHUF`
- `Săn Sale Gia Dụng` item -> `https://s.lazada.vn/s.9hdYa?t=p-i2ccxHM-sCoH6Q5`

No item was added or removed.
No JSON schema change was made.

---

## VALIDATION PERFORMED

- [x] Verified local static server serves `index.html`
- [x] Verified `index.html` category cards load from `products_lazada.json`
- [x] Verified category cards route to `lazada.html?slug=...`, not Shopee
- [x] Verified `products_lazada.json` now contains the new category main links in `affiliate_url`
- [x] Verified `lazada.html` source code still uses `affiliate_url` as the primary product CTA target
- [x] Verified `shopee.html?slug=make-up-fashion` redirects to `lazada.html?slug=make-up-fashion`

Validation notes:

- Browser verification on `lazada.html` itself hit an existing runtime error:
  - console: `Invalid or unexpected token`
- Because this session was explicitly locked to data/config only, that page-level JS issue was not fixed here.
- Static inspection still confirms the page uses:
  - `productHref(item) { return item.affiliate_url || item.product_url || '#'; }`
  - so the updated `affiliate_url` values are the primary CTA targets once the page renders.

---

## IMPORTANT CURRENT STATE

- `Khác` still has `0` item in `products_lazada.json`.
- Category can still exist in config and routing.
- Expected current behavior for `Khác`:
  - category exists in config
  - no product card is present because item count is still `0`
  - main link for `Khác` is now updated in `lazada_sources.json`

---

## DO NOT REPEAT / DO NOT BREAK AGAIN

- Do not touch `shopee.html` redirect logic in follow-up link-only tasks.
- Do not mass-replace Vietnamese text based on terminal mojibake.
- Do not start `member-window` extraction or add new items in follow-up work that is only meant to replace affiliate links.
- Do not change `products_lazada.json` structure in a data-only link refresh task.

---

## NEXT STEP AFTER THIS SESSION

1. Push/verify deploy if not already done in the current session.
2. Separate next task from this one:
   - either fix the existing `lazada.html` runtime syntax error
   - or continue with `member-window` / richer crawl extraction
3. Keep the scope narrow if the next task is still only about affiliate-link replacement.

---

End time: `2026-04-22`
Session owner: `Codex`
