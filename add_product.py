#!/usr/bin/env python3
"""
Add Lazada affiliate product links into lazada_sources.json from the CLI.

Usage:
  python add_product.py "https://s.lazada.vn/s.xxxx?t=p-xxx"
  python add_product.py links.txt
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


REPO_DIR = Path(__file__).resolve().parent
CONFIG_PATH = REPO_DIR / "lazada_sources.json"
TIMEOUT = 25
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/135.0.0.0 Safari/537.36"
)

CATEGORY_OPTIONS = [
    "Make up - Fashion",
    "Tiếp Sức Cày Phim",
    "Săn Sale Gia Dụng",
    "Khác",
]

CATEGORY_KEYWORDS = {
    "Make up - Fashion": [
        "son",
        "phấn",
        "kem",
        "serum",
        "mặt nạ",
        "cushion",
        "kiềm dầu",
        "nước hoa",
        "skincare",
        "makeup",
        "thời trang",
        "áo",
        "quần",
        "đầm",
        "váy",
        "đồ bộ",
        "sơ mi",
        "áo thun",
        "cotton",
        "túi",
        "balo",
        "giày",
        "phụ kiện thời trang",
    ],
    "Tiếp Sức Cày Phim": [
        "snack",
        "bánh",
        "kẹo",
        "nước uống",
        "nước giải khát",
        "cà phê",
        "trà",
        "ngũ cốc",
        "granola",
        "hạt",
        "ăn vặt",
        "xúc xích",
        "phở",
        "mì",
        "tai nghe",
        "giá đỡ",
        "đèn",
        "gối",
        "chăn",
        "chuột",
        "bàn phím",
        "bàn học",
        "bàn văn phòng",
    ],
    "Săn Sale Gia Dụng": [
        "nồi",
        "chảo",
        "bếp",
        "bát",
        "tô",
        "hộp bảo quản",
        "tủ lạnh",
        "máy giặt",
        "quạt",
        "máy hút bụi",
        "đồ dùng nhà bếp",
        "gia dụng",
        "vệ sinh",
    ],
}

SHORTLINK_PATTERNS = (
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


def configure_stdio() -> None:
    for stream_name in ("stdout", "stderr", "stdin"):
        stream = getattr(sys, stream_name, None)
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            if stream_name == "stdin":
                reconfigure(encoding="utf-8", errors="ignore")
            else:
                reconfigure(encoding="utf-8", errors="replace")


def eprint(message: str) -> None:
    print(message, file=sys.stderr)


def load_inputs(args: Sequence[str]) -> List[str]:
    if len(args) != 2:
        raise ValueError(
            'Usage: python add_product.py "https://s.lazada.vn/s.xxxx?t=p-xxx" or python add_product.py links.txt'
        )

    raw = args[1].strip()
    if not raw:
        raise ValueError("Input is empty.")

    input_path = Path(raw)
    if input_path.exists() and input_path.is_file():
        lines = input_path.read_text(encoding="utf-8").splitlines()
        return [line.strip() for line in lines if line.strip()]

    return [raw]


def fetch_url(url: str, *, allow_redirects: bool = True) -> requests.Response:
    response = requests.get(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept-Language": "vi,en-US;q=0.9,en;q=0.8",
        },
        timeout=TIMEOUT,
        allow_redirects=allow_redirects,
    )
    response.raise_for_status()
    return response


def extract_shortlink_target(html: str) -> Optional[str]:
    for pattern in SHORTLINK_PATTERNS:
        match = re.search(pattern, html, flags=re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).replace("\\/", "/").strip()
    return None


def is_lazada_url(url: str) -> bool:
    host = urlparse(url).netloc.lower()
    return host == "lazada.vn" or host.endswith(".lazada.vn")


def resolve_lazada_url(url: str) -> Optional[str]:
    try:
        response = fetch_url(url)
    except requests.RequestException as exc:
        eprint(f"Warning: Khong resolve duoc link {url} -> {exc}")
        return None

    final_url = response.url
    if is_lazada_url(final_url) and "/products/" in final_url:
        return final_url

    if "s.lazada.vn" in urlparse(url).netloc.lower():
        extracted = extract_shortlink_target(response.text)
        if extracted and is_lazada_url(extracted):
            return extracted

    return final_url if is_lazada_url(final_url) and final_url != url else None


def extract_title_from_soup(soup: BeautifulSoup) -> Optional[str]:
    meta_candidates = [
        ("meta", {"property": "og:title"}, "content"),
        ("meta", {"name": "title"}, "content"),
        ("meta", {"name": "twitter:title"}, "content"),
    ]
    for tag_name, attrs, value_key in meta_candidates:
        node = soup.find(tag_name, attrs=attrs)
        if node and node.get(value_key):
            return str(node.get(value_key)).strip()

    title_tag = soup.find("title")
    if title_tag and title_tag.get_text(strip=True):
        return title_tag.get_text(strip=True)

    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            payload = json.loads(script.get_text(strip=True))
        except json.JSONDecodeError:
            continue
        candidates = payload if isinstance(payload, list) else [payload]
        for obj in candidates:
            if isinstance(obj, dict) and obj.get("@type") == "Product" and obj.get("name"):
                return str(obj["name"]).strip()

    return None


def extract_breadcrumbs_from_soup(soup: BeautifulSoup) -> List[str]:
    breadcrumbs: List[str] = []
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            payload = json.loads(script.get_text(strip=True))
        except json.JSONDecodeError:
            continue
        candidates = payload if isinstance(payload, list) else [payload]
        for obj in candidates:
            if not isinstance(obj, dict) or obj.get("@type") != "BreadcrumbList":
                continue
            for item in obj.get("itemListElement") or []:
                if not isinstance(item, dict):
                    continue
                name = item.get("name")
                if not name and isinstance(item.get("item"), dict):
                    name = item["item"].get("name")
                if name:
                    breadcrumbs.append(str(name).strip())
            if breadcrumbs:
                return breadcrumbs

    selectors = [
        "[data-spm-anchor-id*='breadcrumb'] a",
        ".breadcrumb a",
        ".lzd-breadcrumb a",
        "nav[aria-label='breadcrumb'] a",
    ]
    for selector in selectors:
        nodes = soup.select(selector)
        values = [node.get_text(" ", strip=True) for node in nodes if node.get_text(" ", strip=True)]
        if values:
            return values
    return breadcrumbs


def fetch_product_info(final_url: str) -> Tuple[Optional[str], List[str]]:
    try:
        response = fetch_url(final_url)
    except requests.RequestException as exc:
        eprint(f"Warning: Khong fetch duoc product page {final_url} -> {exc}")
        return None, []

    soup = BeautifulSoup(response.text, "html.parser")
    title = extract_title_from_soup(soup)
    breadcrumbs = extract_breadcrumbs_from_soup(soup)
    return title, breadcrumbs


def guess_category(title: str, breadcrumbs: Iterable[str]) -> str:
    haystack = " ".join([title, *breadcrumbs]).lower()
    best_category = "Khác"
    best_score = 0

    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword_matches(haystack, keyword))
        if score > best_score:
            best_score = score
            best_category = category

    return best_category


def keyword_matches(haystack: str, keyword: str) -> bool:
    keyword = keyword.lower().strip()
    if not keyword:
        return False
    if " " in keyword:
        return keyword in haystack
    return re.search(rf"(?<!\w){re.escape(keyword)}(?!\w)", haystack) is not None


def prompt_manual_title(link: str) -> str:
    print(f"Warning: Khong lay duoc ten san pham tu {link}")
    manual = input("Nhap ten san pham thu cong: ").strip()
    return manual or link


def prompt_category(product_name: str, suggested: str) -> str:
    print(f"Sản phẩm: {product_name}")
    print(f"Gợi ý category: {suggested}")
    print("Chọn category:")
    for index, category in enumerate(CATEGORY_OPTIONS, start=1):
        print(f"{index}. {category}")
    choice = input("(Enter = dùng gợi ý, hoặc nhập 1-4): ").strip()
    if not choice:
        return suggested
    if choice in {"1", "2", "3", "4"}:
        return CATEGORY_OPTIONS[int(choice) - 1]
    print("Nhap khong hop le, dung goi y mac dinh.")
    return suggested


def load_config() -> Dict[str, object]:
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"JSON parse error in {CONFIG_PATH.name}: {exc}") from exc


def insert_sources_key(category: Dict[str, object], values: List[str]) -> Dict[str, object]:
    if "sources" in category:
        category["sources"] = values
        return category

    rebuilt: Dict[str, object] = {}
    inserted = False
    for key, value in category.items():
        rebuilt[key] = value
        if key == "backup":
            rebuilt["sources"] = values
            inserted = True
    if not inserted:
        rebuilt["sources"] = values
    return rebuilt


def append_link_to_category(config: Dict[str, object], category_name: str, link: str) -> bool:
    categories = config.get("categories")
    if not isinstance(categories, list):
        raise RuntimeError('Invalid lazada_sources.json: missing "categories" array.')

    for index, category in enumerate(categories):
        if not isinstance(category, dict):
            continue
        if str(category.get("name")) != category_name:
            continue

        current_sources = category.get("sources")
        if current_sources is None:
            source_values: List[str] = []
        elif isinstance(current_sources, list):
            source_values = [str(item) for item in current_sources]
        else:
            raise RuntimeError(f'Invalid "sources" value in category "{category_name}".')

        if link in source_values:
            print(f"✓ Link da ton tai trong {category_name}")
            return False

        source_values.append(link)
        categories[index] = insert_sources_key(category, source_values)
        return True

    raise RuntimeError(f'Category "{category_name}" not found in lazada_sources.json.')


def save_config(config: Dict[str, object]) -> None:
    CONFIG_PATH.write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def process_link(config: Dict[str, object], short_link: str) -> bool:
    final_url = resolve_lazada_url(short_link)
    if not final_url:
        eprint(f"Warning: Bo qua link khong resolve duoc: {short_link}")
        return False

    title, breadcrumbs = fetch_product_info(final_url)
    if not title:
        title = prompt_manual_title(final_url)

    suggested = guess_category(title, breadcrumbs)
    selected = prompt_category(title, suggested)

    changed = append_link_to_category(config, selected, short_link)
    if changed:
        print(f"✓ Đã thêm vào {selected}")
    return changed


def main(argv: Sequence[str]) -> int:
    try:
        links = load_inputs(argv)
        config = load_config()
    except (ValueError, RuntimeError) as exc:
        eprint(str(exc))
        return 1

    changed = False
    for link in links:
        try:
            changed = process_link(config, link) or changed
        except RuntimeError as exc:
            eprint(str(exc))
            return 1

    if changed:
        save_config(config)
    return 0


if __name__ == "__main__":
    configure_stdio()
    sys.exit(main(sys.argv))
