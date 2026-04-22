#!/usr/bin/env python3
"""
Build Lazada product data from Shopee backup source.

Usage:
  python3 crawl.py
  python3 crawl.py --source products_shopee.json --out products_lazada.json

Default behavior:
- Read Shopee source data from products_shopee.json
- Generate Lazada data file products_lazada.json
- Mirror output to products.json for backward compatibility
"""

import argparse
import json
import os
from copy import deepcopy

DIR = os.path.dirname(os.path.abspath(__file__))

ALLOWED_CATEGORY_ORDER = [
    "Make up - Fashion",
    "Tiếp Sức Cày Phim",
    "Săn Sale Gia Dụng",
    "Khác",
]

# Normalize legacy category naming.
CATEGORY_ALIASES = {
    "Săn Sale Đón Tết": "Săn Sale Gia Dụng",
}

LAZADA_CAMPAIGN_LINKS = {
    "Make up - Fashion": {
        "main": "https://s.lazada.vn/s.9hdZy?t=p-i3bSXYZ-sHY12BX",
        "backup": "https://s.lazada.vn/s.9hdaN?t=h5-v2_member-window",
    },
    "Tiếp Sức Cày Phim": {
        "main": "https://s.lazada.vn/s.9hdYL?t=p-i3dMmgt-sHnNHUF",
        "backup": "https://s.lazada.vn/s.9hdaN?t=h5-v2_member-window",
    },
    "Săn Sale Gia Dụng": {
        "main": "https://s.lazada.vn/s.9hdYa?t=p-i2ccxHM-sCoH6Q5",
        "backup": "https://s.lazada.vn/s.9hdaN?t=h5-v2_member-window",
    },
    "Khác": {
        "main": "https://s.lazada.vn/s.9hddF?t=ntv-v1_alp-native",
        "backup": "https://s.lazada.vn/s.9hdaN?t=h5-v2_member-window",
    },
}


def parse_args():
    parser = argparse.ArgumentParser(description="Build Lazada products JSON from backup source")
    parser.add_argument(
        "--source",
        default="products_shopee.json",
        help="Input source JSON file (relative to repo root)",
    )
    parser.add_argument(
        "--out",
        default="products_lazada.json",
        help="Output Lazada JSON file (relative to repo root)",
    )
    parser.add_argument(
        "--mirror",
        default="products.json",
        help="Mirror output file for website compatibility",
    )
    return parser.parse_args()


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, payload):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def normalize_category_name(name):
    return CATEGORY_ALIASES.get(name, name)


def main():
    args = parse_args()

    source_path = os.path.join(DIR, args.source)
    out_path = os.path.join(DIR, args.out)
    mirror_path = os.path.join(DIR, args.mirror)

    if not os.path.exists(source_path):
        raise FileNotFoundError(
            f"Source file not found: {source_path}. "
            "Run crawler Shopee first or restore products_shopee.json."
        )

    data = load_json(source_path)
    source_products = data.get("products") or {}
    source_groups = data.get("groups") or []

    group_count_by_name = {}
    for group in source_groups:
        name = normalize_category_name(str(group.get("name", "")).strip())
        if not name:
            continue
        group_count_by_name[name] = int(group.get("count") or 0)

    lazada_products = {}
    output_groups = []

    for cat_name in ALLOWED_CATEGORY_ORDER:
        source_items = source_products.get(cat_name)

        if source_items is None and cat_name == "Săn Sale Gia Dụng":
            source_items = source_products.get("Săn Sale Đón Tết")

        if not isinstance(source_items, list) or not source_items:
            continue

        links = LAZADA_CAMPAIGN_LINKS[cat_name]
        converted_items = []

        for item in source_items:
            if not isinstance(item, dict):
                continue

            next_item = deepcopy(item)
            next_item["link"] = links["main"]
            next_item["resolved_url"] = links["main"]
            next_item["backup_link"] = links["backup"]
            converted_items.append(next_item)

        if not converted_items:
            continue

        lazada_products[cat_name] = converted_items

        raw_group_count = group_count_by_name.get(cat_name)
        output_groups.append(
            {
                "id": "",
                "name": cat_name,
                "count": raw_group_count if raw_group_count else len(converted_items),
            }
        )

    total_items = sum(len(items) for items in lazada_products.values())

    payload = {
        "groups": output_groups,
        "products": lazada_products,
        "total": total_items,
        "lazadaCampaignLinks": LAZADA_CAMPAIGN_LINKS,
        "source": os.path.basename(source_path),
    }

    save_json(out_path, payload)
    save_json(mirror_path, payload)

    print("═══ Build Lazada Products ═══")
    print(f"Source: {os.path.basename(source_path)}")
    print(f"Saved:  {os.path.basename(out_path)}")
    print(f"Mirror: {os.path.basename(mirror_path)}")
    print(f"Categories: {len(lazada_products)}")
    print(f"Products:   {total_items}")


if __name__ == "__main__":
    main()
