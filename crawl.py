#!/usr/bin/env python3
"""
Build live Lazada storefront data from Lazada sources.

Usage:
  python crawl.py
  python crawl.py --config lazada_sources.json --out products_lazada.json

Design goals:
- `crawl.py` is the only entrypoint needed to refresh Lazada storefront data
- Source-of-truth for categories/sources lives in JSON config
- Output payload contains real Lazada product data, not Shopee placeholders
- Share bridge / PDP / listing URLs are auto-detected where possible
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Iterable, List, Optional, Tuple

DIR = os.path.dirname(os.path.abspath(__file__))

DEFAULT_CONFIG = "lazada_sources.json"
DEFAULT_OUT = "products_lazada.json"
DEFAULT_MIRROR = "products.json"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/135.0.0.0 Safari/537.36"
)

ALLOWED_AFFILIATE_HOSTS = (
    "lazada.vn",
    "s.lazada.vn",
)

LANDING_PAGE_HINTS = (
    "/affiliate/member-window",
    "/affiliate/ams_lp/",
    "/affiliate/6srxcyymkr",
    "/momclub",
)

SHARE_REDIRECT_PATTERNS = (
    r"var\s+REDIRECTURL\s*=\s*new URL\('([^']+)'\)",
    r'<link\s+rel="origin"\s+href="([^"]+)"',
    r'window\.location\.href\s*=\s*"([^"]+)"',
    r"window\.location\.href\s*=\s*'([^']+)'",
    r'location\.replace\(\s*"([^"]+)"\s*\)',
    r"location\.replace\(\s*'([^']+)'\s*\)",
    r'<meta\s+http-equiv="refresh"\s+content="\d+;url=([^"]+)"',
    r'<link\s+rel="canonical"\s+href="([^"]+)"',
    r'<meta\s+property="og:url"\s+content="([^"]+)"',
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build live Lazada storefront payload")
    parser.add_argument(
        "--config",
        default=DEFAULT_CONFIG,
        help="Path to Lazada sources config JSON (relative to repo root)",
    )
    parser.add_argument(
        "--out",
        default=DEFAULT_OUT,
        help="Output storefront payload JSON (relative to repo root)",
    )
    parser.add_argument(
        "--mirror",
        default=DEFAULT_MIRROR,
        help="Mirror output JSON for backward compatibility",
    )
    return parser.parse_args()


def repo_path(path: str) -> str:
    return path if os.path.isabs(path) else os.path.join(DIR, path)


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def save_json(path: str, payload: Any) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def fetch_text(url: str, timeout: int = 25) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "vi,en-US;q=0.9,en;q=0.8",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="ignore")


def slugify(text: str) -> str:
    mapping = str.maketrans(
        {
            "à": "a",
            "á": "a",
            "ả": "a",
            "ã": "a",
            "ạ": "a",
            "ă": "a",
            "ằ": "a",
            "ắ": "a",
            "ẳ": "a",
            "ẵ": "a",
            "ặ": "a",
            "â": "a",
            "ầ": "a",
            "ấ": "a",
            "ẩ": "a",
            "ẫ": "a",
            "ậ": "a",
            "đ": "d",
            "è": "e",
            "é": "e",
            "ẻ": "e",
            "ẽ": "e",
            "ẹ": "e",
            "ê": "e",
            "ề": "e",
            "ế": "e",
            "ể": "e",
            "ễ": "e",
            "ệ": "e",
            "ì": "i",
            "í": "i",
            "ỉ": "i",
            "ĩ": "i",
            "ị": "i",
            "ò": "o",
            "ó": "o",
            "ỏ": "o",
            "õ": "o",
            "ọ": "o",
            "ô": "o",
            "ồ": "o",
            "ố": "o",
            "ổ": "o",
            "ỗ": "o",
            "ộ": "o",
            "ơ": "o",
            "ờ": "o",
            "ớ": "o",
            "ở": "o",
            "ỡ": "o",
            "ợ": "o",
            "ù": "u",
            "ú": "u",
            "ủ": "u",
            "ũ": "u",
            "ụ": "u",
            "ư": "u",
            "ừ": "u",
            "ứ": "u",
            "ử": "u",
            "ữ": "u",
            "ự": "u",
            "ỳ": "y",
            "ý": "y",
            "ỷ": "y",
            "ỹ": "y",
            "ỵ": "y",
        }
    )
    normalized = text.lower().translate(mapping)
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized)
    return normalized.strip("-")


def unescape_url(value: str) -> str:
    return html.unescape(value).replace("\\/", "/")


def looks_like_share_bridge(url: str) -> bool:
    host = urllib.parse.urlparse(url).netloc.lower()
    return host == "s.lazada.vn"


def looks_like_pdp_url(url: str) -> bool:
    return "/products/" in urllib.parse.urlparse(url).path


def looks_like_landing_page_url(url: str) -> bool:
    lowered = url.lower()
    return any(hint in lowered for hint in LANDING_PAGE_HINTS)


def is_allowed_click_url(url: str) -> bool:
    if not url:
        return False
    host = urllib.parse.urlparse(url).netloc.lower()
    return any(host.endswith(domain) for domain in ALLOWED_AFFILIATE_HOSTS)


def canonical_product_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    query = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    blocked_keys = {
        "from_affiliate",
        "t",
        "sub_id1",
        "sub_aff_id",
        "exlaz",
        "dsource",
        "laz_share_info",
        "laz_token",
        "dauto",
        "dfrom",
        "from_share_link",
        "spm",
    }
    clean_query = [(k, v) for k, v in query if k not in blocked_keys]
    return urllib.parse.urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            urllib.parse.urlencode(clean_query, doseq=True),
            "",
        )
    )


def unique_urls(urls: Iterable[Optional[str]]) -> List[str]:
    seen: List[str] = []
    for url in urls:
        if not url:
            continue
        clean = url.strip()
        if clean and clean not in seen:
            seen.append(clean)
    return seen


def url_from_config_entry(entry: Any) -> Optional[str]:
    if isinstance(entry, str):
        return entry
    if isinstance(entry, dict):
        return entry.get("url") or entry.get("href") or entry.get("link")
    return None


def normalize_source_entry(entry: Any, *, default_label: str = "source") -> Optional[Dict[str, Any]]:
    if isinstance(entry, str):
        clean = entry.strip()
        if not clean:
            return None
        return {
            "url": clean,
            "label": default_label,
            "type": "auto",
            "fallback_urls": [],
        }
    if not isinstance(entry, dict):
        return None

    url = str(entry.get("url") or entry.get("href") or entry.get("link") or "").strip()
    if not url:
        return None
    normalized = dict(entry)
    normalized["url"] = url
    normalized.setdefault("label", normalized.get("type") or default_label)
    normalized.setdefault("type", "auto")
    normalized["fallback_urls"] = unique_urls(
        list(normalized.get("fallback_urls") or [])
        + [url_from_config_entry(item) for item in normalized.get("fallbacks") or []]
    )
    return normalized


def category_source_entries(category: Dict[str, Any]) -> List[Dict[str, Any]]:
    entries: List[Dict[str, Any]] = []
    main_url = str(category.get("main") or "").strip()
    if main_url:
        entries.append(
            {
                "url": main_url,
                "label": "Current Lazada main link",
                "type": "main",
                "fallback_urls": [],
            }
        )
    for source in category.get("sources") or []:
        normalized = normalize_source_entry(source, default_label="Manual Lazada product source")
        if normalized:
            entries.append(normalized)
    return entries


def build_affiliate_url(source_url: str, redirect_url: Optional[str], product_url: str) -> str:
    if redirect_url and is_allowed_click_url(redirect_url):
        return redirect_url
    if is_allowed_click_url(source_url):
        return source_url
    return product_url


def build_fallback_urls(
    *,
    product_url: str,
    affiliate_url: str,
    source_url: str,
    redirect_url: Optional[str],
    source_fallbacks: Iterable[str],
    category_fallbacks: Iterable[str],
) -> List[str]:
    urls = unique_urls(
        [
            canonical_product_url(product_url),
            redirect_url,
            source_url,
            *source_fallbacks,
            *category_fallbacks,
        ]
    )
    return [url for url in urls if url != affiliate_url and is_allowed_click_url(url)]


def extract_first(patterns: Iterable[str], text: str) -> Optional[str]:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
        if match:
            return unescape_url(match.group(1).strip())
    return None


def extract_json_ld_objects(html_text: str) -> List[Any]:
    objects: List[Any] = []
    pattern = re.compile(
        r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>',
        flags=re.IGNORECASE | re.DOTALL,
    )
    for match in pattern.finditer(html_text):
        raw = match.group(1).strip()
        if not raw:
            continue
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, list):
            objects.extend(parsed)
        else:
            objects.append(parsed)
    return objects


def extract_pdp_tracking_data(html_text: str) -> Dict[str, Any]:
    match = re.search(
        r'var\s+pdpTrackingData\s*=\s*"((?:\\.|[^"])*)";',
        html_text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return {}
    try:
        decoded = json.loads('"' + match.group(1) + '"')
        payload = json.loads(decoded)
        return payload if isinstance(payload, dict) else {}
    except (json.JSONDecodeError, TypeError):
        return {}


def parse_price_value(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        digits = re.sub(r"[^\d.,]", "", value).replace(".", "").replace(",", ".")
        try:
            return float(digits)
        except ValueError:
            return None
    return None


def normalize_image(value: Any) -> str:
    if isinstance(value, list):
        value = value[0] if value else ""
    if not isinstance(value, str):
        return ""
    value = value.strip()
    if not value:
        return ""
    if value.startswith("//"):
        return "https:" + value
    return value


def product_id_from_url(url: str) -> str:
    match = re.search(r"-i(\d+)-s(\d+)", url)
    if match:
        return f"{match.group(1)}-{match.group(2)}"
    match = re.search(r"itemId=(\d+).*skuId=(\d+)", url)
    if match:
        return f"{match.group(1)}-{match.group(2)}"
    match = re.search(r"i(\d+)", url)
    if match:
        return match.group(1)
    return slugify(url) or url


def build_product_item(
    *,
    category_name: str,
    source_url: str,
    source_label: str,
    product_url: str,
    affiliate_url: str,
    name: str,
    image: str,
    price_text: Optional[str] = None,
    price: Optional[float] = None,
    seller_name: Optional[str] = None,
    item_id: Optional[str] = None,
    fallback_urls: Optional[List[str]] = None,
) -> Optional[Dict[str, Any]]:
    clean_name = (name or "").strip()
    clean_image = normalize_image(image)
    clean_product_url = canonical_product_url(product_url)
    clean_affiliate_url = affiliate_url.strip() if affiliate_url else clean_product_url

    if not clean_name or not clean_image or not is_allowed_click_url(clean_affiliate_url):
        return None

    return {
        "id": item_id or product_id_from_url(clean_product_url),
        "name": clean_name,
        "image": clean_image,
        "product_url": clean_product_url,
        "affiliate_url": clean_affiliate_url,
        "backup_url": (fallback_urls or [None])[0],
        "fallback_urls": fallback_urls or [],
        "price": price,
        "price_text": price_text,
        "seller_name": seller_name,
        "source_category": category_name,
        "source_url": source_url,
        "source_label": source_label,
    }


def parse_pdp_page(
    html_text: str,
    *,
    category_name: str,
    source_url: str,
    source_label: str,
    redirect_url: Optional[str],
    page_url: str,
    source_fallbacks: Iterable[str],
    category_fallbacks: Iterable[str],
) -> Optional[Dict[str, Any]]:
    product_url = canonical_product_url(page_url)
    affiliate_url = build_affiliate_url(source_url, redirect_url, product_url)
    fallback_urls = build_fallback_urls(
        product_url=product_url,
        affiliate_url=affiliate_url,
        source_url=source_url,
        redirect_url=redirect_url,
        source_fallbacks=source_fallbacks,
        category_fallbacks=category_fallbacks,
    )

    for obj in extract_json_ld_objects(html_text):
        obj_type = obj.get("@type") if isinstance(obj, dict) else None
        if obj_type != "Product":
            continue

        offers = obj.get("offers") or {}
        seller = obj.get("brand")
        seller_name = seller.get("name") if isinstance(seller, dict) else None
        item = build_product_item(
            category_name=category_name,
            source_url=source_url,
            source_label=source_label,
            product_url=obj.get("url") or product_url,
            affiliate_url=affiliate_url,
            name=obj.get("name") or "",
            image=normalize_image(obj.get("image")),
            price=parse_price_value(offers.get("price")),
            price_text=(offers.get("priceCurrency") or "") if False else None,
            seller_name=seller_name,
            item_id=obj.get("sku") or obj.get("productID") or product_id_from_url(product_url),
            fallback_urls=fallback_urls,
        )
        if item:
            if not item["price_text"] and item["price"] is not None:
                item["price_text"] = f"{int(item['price']):,} ₫".replace(",", ".")
            return item

    tracking = extract_pdp_tracking_data(html_text)
    if tracking:
        photo = tracking.get("pdt_photo")
        if isinstance(photo, str) and photo.startswith("http"):
            image = photo
        else:
            image = ""
        item = build_product_item(
            category_name=category_name,
            source_url=source_url,
            source_label=source_label,
            product_url=product_url,
            affiliate_url=affiliate_url,
            name=tracking.get("pdt_name") or "",
            image=image,
            price_text=tracking.get("pdt_price"),
            price=parse_price_value(tracking.get("pdt_price")),
            seller_name=tracking.get("brand_name"),
            item_id=f"{tracking.get('pdt_sku')}-{tracking.get('pdt_simplesku')}",
            fallback_urls=fallback_urls,
        )
        if item:
            return item

    title_match = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', html_text, re.IGNORECASE)
    image_match = re.search(r'<meta\s+property="og:image"\s+content="([^"]*)"', html_text, re.IGNORECASE)
    if title_match and image_match:
        return build_product_item(
            category_name=category_name,
            source_url=source_url,
            source_label=source_label,
            product_url=product_url,
            affiliate_url=affiliate_url,
            name=html.unescape(title_match.group(1)),
            image=image_match.group(1),
            item_id=product_id_from_url(product_url),
            fallback_urls=fallback_urls,
        )

    return None


def parse_listing_page(
    html_text: str,
    *,
    category_name: str,
    source_url: str,
    source_label: str,
    redirect_url: Optional[str],
    page_url: str,
    source_fallbacks: Iterable[str],
    category_fallbacks: Iterable[str],
) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []

    for obj in extract_json_ld_objects(html_text):
        if not isinstance(obj, dict) or obj.get("@type") != "ItemList":
            continue
        for entry in obj.get("itemListElement") or []:
            if not isinstance(entry, dict):
                continue
            product = entry.get("item") or entry
            if not isinstance(product, dict):
                continue
            product_url = product.get("url") or ""
            canonical_url = canonical_product_url(product_url)
            affiliate_url = build_affiliate_url(source_url, redirect_url, canonical_url)
            item = build_product_item(
                category_name=category_name,
                source_url=source_url,
                source_label=source_label,
                product_url=product_url,
                affiliate_url=affiliate_url,
                name=product.get("name") or "",
                image=normalize_image(product.get("image")),
                price=parse_price_value((product.get("offers") or {}).get("price")),
                price_text=None,
                seller_name=None,
                item_id=product.get("sku") or product.get("productID") or product_id_from_url(product_url),
                fallback_urls=build_fallback_urls(
                    product_url=canonical_url,
                    affiliate_url=affiliate_url,
                    source_url=source_url,
                    redirect_url=redirect_url,
                    source_fallbacks=source_fallbacks,
                    category_fallbacks=category_fallbacks,
                ),
            )
            if item:
                if item["price"] is not None:
                    item["price_text"] = f"{int(item['price']):,} ₫".replace(",", ".")
                items.append(item)

    return dedupe_items(items)


def crawl_source(
    source: Dict[str, Any],
    category_name: str,
    category_fallbacks: Iterable[str],
) -> Tuple[List[Dict[str, Any]], List[str]]:
    url = str(source.get("url") or "").strip()
    label = str(source.get("label") or source.get("type") or "source").strip()
    source_type = str(source.get("type") or "auto").strip().lower()
    source_fallbacks = unique_urls(source.get("fallback_urls") or [])
    issues: List[str] = []
    if not url:
        return [], ["missing source url"]

    try:
        source_html = fetch_text(url)
    except Exception as exc:  # noqa: BLE001
        return [], [f"{label}: fetch failed for {url} -> {exc}"]

    redirect_url = extract_first(SHARE_REDIRECT_PATTERNS, source_html) if looks_like_share_bridge(url) else None
    target_url = redirect_url or url
    target_is_pdp = looks_like_pdp_url(target_url)
    target_is_landing = looks_like_landing_page_url(target_url)

    if target_is_pdp:
        try:
            page_html = fetch_text(target_url)
        except Exception as exc:  # noqa: BLE001
            return [], [f"{label}: fetch failed for PDP {target_url} -> {exc}"]

        product = parse_pdp_page(
            page_html,
            category_name=category_name,
            source_url=url,
            source_label=label,
            redirect_url=redirect_url,
            page_url=target_url,
            source_fallbacks=source_fallbacks,
            category_fallbacks=category_fallbacks,
        )
        if not product:
            return [], [f"{label}: no product data parsed from PDP {target_url}"]
        return [product], issues

    items = parse_listing_page(
        source_html,
        category_name=category_name,
        source_url=url,
        source_label=label,
        redirect_url=redirect_url,
        page_url=target_url,
        source_fallbacks=source_fallbacks,
        category_fallbacks=category_fallbacks,
    )
    if not items:
        if source_type in {"member_window", "campaign"} or target_is_landing:
            issues.append(f"{label}: landing source resolved but no guest-visible items parsed from {target_url}")
        else:
            issues.append(f"{label}: no listing items parsed from {target_url}")
    return items, issues


def dedupe_items(items: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen: Dict[str, Dict[str, Any]] = {}
    for item in items:
        key = item.get("id") or item.get("product_url") or item.get("affiliate_url")
        if not key:
            continue
        if key not in seen:
            seen[key] = item
    return list(seen.values())


def validate_item(item: Dict[str, Any]) -> Optional[str]:
    if not item.get("name"):
        return "missing name"
    image = item.get("image") or ""
    if not image or (
        "lazcdn" not in image
        and "filebroker-cdn.lazada" not in image
        and "slatic.net" not in image
    ):
        return "missing Lazada image"
    if not is_allowed_click_url(item.get("affiliate_url") or ""):
        return "invalid affiliate URL"
    return None


def build_payload(config: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    categories = config.get("categories") or []
    global_fallbacks = unique_urls(
        url_from_config_entry(entry) for entry in (config.get("global_fallbacks") or [])
    )
    payload_products: Dict[str, List[Dict[str, Any]]] = {}
    groups: List[Dict[str, Any]] = []
    report = {
        "successful_categories": 0,
        "failed_categories": 0,
        "source_errors": [],
        "dropped_items": [],
        "category_counts": {},
    }

    for category in categories:
        name = str(category.get("name") or "").strip()
        if not name:
            continue

        category_fallbacks = unique_urls(
            list(category.get("fallback_urls") or [])
            + [url_from_config_entry(item) for item in (category.get("fallbacks") or [])]
            + [category.get("backup")]
            + global_fallbacks
        )
        collected: List[Dict[str, Any]] = []
        issues: List[str] = []
        for source in category_source_entries(category):
            source_items, source_issues = crawl_source(source, name, category_fallbacks)
            collected.extend(source_items)
            issues.extend(source_issues)

        deduped = dedupe_items(collected)
        valid_items: List[Dict[str, Any]] = []
        for item in deduped:
            error = validate_item(item)
            if error:
                report["dropped_items"].append(
                    {
                        "category": name,
                        "product_url": item.get("product_url"),
                        "reason": error,
                    }
                )
                continue
            valid_items.append(item)

        payload_products[name] = valid_items
        groups.append(
            {
                "id": slugify(name),
                "name": name,
                "slug": category.get("slug") or slugify(name),
                "count": len(valid_items),
                "landing_url": category_fallbacks[0] if category_fallbacks else None,
                "fallback_urls": category_fallbacks,
            }
        )
        report["category_counts"][name] = len(valid_items)

        if valid_items:
            report["successful_categories"] += 1
        else:
            report["failed_categories"] += 1
        report["source_errors"].extend(issues)

    payload = {
        "version": 2,
        "generated_at": dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "source_type": "lazada-live",
        "source_config": DEFAULT_CONFIG,
        "groups": groups,
        "products": payload_products,
        "total": sum(group["count"] for group in groups),
        "report": report,
    }
    return payload, report


def print_summary(report: Dict[str, Any]) -> None:
    print("=== Build Lazada Storefront ===")
    print(f"Categories OK:   {report['successful_categories']}")
    print(f"Categories fail: {report['failed_categories']}")
    print("Items by category:")
    for name, count in report["category_counts"].items():
        print(f"  - {name}: {count}")
    if report["dropped_items"]:
        print(f"Dropped items: {len(report['dropped_items'])}")
    if report["source_errors"]:
        print("Source issues:")
        for issue in report["source_errors"]:
            print(f"  - {issue}")


def main() -> int:
    args = parse_args()
    config_path = repo_path(args.config)
    out_path = repo_path(args.out)
    mirror_path = repo_path(args.mirror)

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    config = load_json(config_path)
    payload, report = build_payload(config)

    if payload["total"] <= 0:
        print_summary(report)
        raise RuntimeError(
            "No Lazada items were crawled. Refusing to overwrite storefront payload with empty data."
        )

    save_json(out_path, payload)
    save_json(mirror_path, payload)
    print_summary(report)
    print(f"Saved:  {os.path.basename(out_path)}")
    print(f"Mirror: {os.path.basename(mirror_path)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
