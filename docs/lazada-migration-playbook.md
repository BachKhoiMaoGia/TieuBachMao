# Shopee to Lazada Migration Playbook

This playbook summarizes the reusable method used in this repo to replace a Shopee-facing affiliate storefront with a Lazada-first storefront.

## Target Architecture

- Keep the public site static when possible.
- Make Lazada source configuration explicit in one JSON file.
- Generate storefront payload JSON from live Lazada product pages.
- Keep old Shopee routes as redirects or compatibility shims.
- Avoid mixing Shopee-origin product data into Lazada output.

## File Roles

- `lazada_sources.json`
  - Human-maintained source config.
  - Stores category order, `main`, `backup`, and optional product-level `sources`.
- `add_product.py`
  - CLI helper for adding Lazada short affiliate links into `lazada_sources.json`.
  - Resolves/fetches product info only to help category selection.
  - Does not regenerate storefront payloads.
- `crawl.py`
  - Canonical Lazada payload generator.
  - Reads `lazada_sources.json`.
  - Crawls Lazada PDP/share/listing sources.
  - Writes `products_lazada.json`.
  - Mirrors output to `products.json` for legacy compatibility.
- `products_lazada.json`
  - Runtime storefront data consumed by the frontend.
- `shopee.html`
  - Compatibility redirect layer, not the active storefront.

## Migration Steps

1. Inventory the existing Shopee storefront.
   - Identify public entrypoints.
   - Identify old route patterns.
   - Identify category names and business-approved category set.

2. Decide the Lazada category taxonomy.
   - Keep only categories that should be visible.
   - Add alias rules for old category names if inbound links still use them.
   - Do not expose legacy Shopee categories by accident.

3. Create `lazada_sources.json`.
   - Add one object per category.
   - Include `slug`, `name`, `main`, `backup`, and optional `sources`.
   - Keep global fallback links separate under `global_fallbacks`.

4. Add product-level Lazada affiliate links.
   - Put links into `links.txt`, one link per line.
   - Run:
     ```bash
     python add_product.py links.txt
     ```
   - Confirm each suggested category.
   - Review `lazada_sources.json` after the run.

5. Generate live Lazada payload.
   - Run:
     ```bash
     python crawl.py
     ```
   - Confirm non-zero category counts.
   - Confirm `products_lazada.json` and `products.json` are mirrored.
   - Inspect `report.dropped_items` before shipping.

6. Update frontend data loading.
   - Point active pages to `products_lazada.json`.
   - Keep category filters and aliases explicit.
   - Use `affiliate_url` as primary click target.
   - Preserve fallback links in payload for future handling.

7. Preserve route compatibility.
   - Keep old Shopee URLs redirecting to Lazada equivalents.
   - Support both query routes such as `lazada.html?slug=...` and any clean path routes already in circulation.

8. Validate before publishing.
   - Check `index.html` category cards.
   - Check `lazada.html` tabs and all-products view.
   - Check category deep links.
   - Check product card click URLs.
   - Check generated payload counts and dropped item report.

## Technical Notes

- Lazada short links often resolve through HTML redirect hints rather than plain HTTP redirects.
- Product pages may expose usable data through:
  - JSON-LD `Product`
  - `pdpTrackingData`
  - Open Graph metadata
- Lazada image hosts are not limited to one CDN. Known valid hosts include:
  - `lazcdn`
  - `filebroker-cdn.lazada`
  - `slatic.net`
- Member-window and campaign landing pages may resolve correctly but still not expose guest-visible product lists in static HTML.
- Treat URL resolution, HTML parsing, and item extraction as separate validation stages.

## Data Contract

Generated payload shape:

```json
{
  "version": 2,
  "source_type": "lazada-live",
  "groups": [
    {
      "id": "make-up-fashion",
      "name": "Make up - Fashion",
      "slug": "make-up-fashion",
      "count": 11
    }
  ],
  "products": {
    "Make up - Fashion": [
      {
        "name": "Product name",
        "image": "https://...",
        "product_url": "https://www.lazada.vn/...",
        "affiliate_url": "https://s.lazada.vn/...",
        "backup_url": "https://...",
        "fallback_urls": []
      }
    ]
  },
  "report": {
    "dropped_items": [],
    "source_errors": []
  }
}
```

Frontend pages should tolerate extra fields and should not depend on generated timestamps.

## Common Failure Modes

- Crawler refuses to overwrite payload because zero items were extracted.
- Product was parsed but dropped because image host validation is too narrow.
- Batch category suggestions are wrong because keyword matching is broad.
- Old Shopee links break because redirect shim was removed.
- New Lazada links are added to config but payload was not regenerated.
- Payload is regenerated from campaign/member-window links that do not expose item feeds, producing empty categories.

## Reuse Checklist For Another Static Web System

- [ ] Keep old entrypoints and redirect them intentionally.
- [ ] Create a Lazada source config before changing frontend code.
- [ ] Add links with an operator-confirmed CLI flow.
- [ ] Generate a separate Lazada payload file.
- [ ] Mirror old data filename only when required for compatibility.
- [ ] Keep category allow-listing explicit.
- [ ] Document any intentionally hidden legacy categories.
- [ ] Treat dropped item reports as release-blocking until reviewed.
- [ ] Smoke-test category cards, tabs, deep links, and product clicks.
