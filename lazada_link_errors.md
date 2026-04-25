# Lazada Link Errors

Last checked: 2026-04-25

This file tracks Lazada source links that did not become valid storefront product cards during the latest `crawl.py` run.

## Current Errors

| Source | Category | Status | Reason | Next Check |
|---|---|---|---|---|
| `https://s.lazada.vn/s.ljrQD?t=p-i3czEE8-sHju5kk` | `Săn Sale Gia Dụng` | No product card | Short link resolved to PDP `https://www.lazada.vn/products/pdp-i3324491964-s16252561750.html...`, but the crawler could not parse usable product data from the returned HTML during the final run. | Re-run later; if still failing, replace with a fresh PDP affiliate short link. |
| `https://s.lazada.vn/s.ljrAt?t=p-i1zCzr6-s8xQ9EG` | `Tiếp Sức Cày Phim` | Dropped item | Product URL parsed for `Mì sấy trẻ em Miu Miu...`, but no valid Lazada image was parsed, so the crawler dropped it instead of publishing a broken card. | Inspect page HTML/image metadata; replace link if Lazada does not expose a valid image. |
| `https://s.lazada.vn/s.9hddF?t=ntv-v1_alp-native` | `Khác` main | No listing items | Campaign/landing source resolves, but static guest-visible HTML parsing still does not expose product list items. | Keep only as fallback/link target unless a signed runtime extraction path is implemented. |

## Latest Payload Impact

- `products_lazada.json` total: `26`
- `Make up - Fashion`: `11`
- `Tiếp Sức Cày Phim`: `11`
- `Săn Sale Gia Dụng`: `4`
- `Khác`: `0`

## Notes

- These are not secret credentials; they are public affiliate/source URLs.
- Do not remove working source links just because campaign/member-window links do not parse as listing feeds.
- Prefer replacing failing PDP links with fresh Lazada PDP affiliate short links over forcing incomplete product cards into the payload.
