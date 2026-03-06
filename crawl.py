#!/usr/bin/env python3
"""
Crawl Shopee affiliate products & generate shopee.html
Chạy: python3 crawl.py
Sau đó: git add -A && git commit -m "Update products" && git push origin main:gh-pages
"""
import json, urllib.request, urllib.error, time, os, re

DIR = os.path.dirname(os.path.abspath(__file__))
API = "https://collshp.com/api/v3/gql/graphql"
HEADERS = {"Content-Type": "application/json", "Referer": "https://collshp.com/tieubachmao"}

LINK_QUERY = """query getLinkLists($urlSuffix: String!, $pageSize: String, $pageNum: String, $groupId: String) {
  landingPageLinkList(urlSuffix: $urlSuffix, pageSize: $pageSize, pageNum: $pageNum, groupId: $groupId) {
    totalCount
    linkList { linkId link linkName image linkType groupIds }
  }
}"""

def api_call(query, variables=None):
    payload = json.dumps({"operationName": "getLinkLists", "query": query, "variables": variables or {}})
    req = urllib.request.Request(API, data=payload.encode(), headers=HEADERS, method="POST")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

def fetch_groups():
    q = '{ storefrontGroupList(urlSuffix: "tieubachmao", uuId: "c", deviceId: "c") { groupList { groupId groupName totalCount } } }'
    payload = json.dumps({"query": q})
    req = urllib.request.Request(API, data=payload.encode(), headers=HEADERS, method="POST")
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
    return [g for g in data["data"]["storefrontGroupList"]["groupList"] if int(g["totalCount"]) > 0]

def fetch_products(group_id=None):
    items, page = [], 1
    while True:
        variables = {"urlSuffix": "tieubachmao", "pageSize": "50", "pageNum": str(page)}
        if group_id:
            variables["groupId"] = group_id
        result = api_call(LINK_QUERY, variables)["data"]["landingPageLinkList"]
        items.extend(result["linkList"])
        if len(items) >= int(result["totalCount"]):
            break
        page += 1
    return items

def resolve_shortlink(url):
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            self.redirected_url = newurl
            return None
    handler = NoRedirect()
    opener = urllib.request.build_opener(handler)
    try:
        opener.open(urllib.request.Request(url, method="HEAD"))
    except urllib.error.HTTPError:
        pass
    resolved = getattr(handler, "redirected_url", url)
    if "error_page" in resolved:
        return url
    return resolved

def generate_html(categories):
    data_json = json.dumps(categories, ensure_ascii=False)
    return f'''<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🛒 Góc Đồ Tiện Ích - Tiểu Bạch Mao</title>
    <meta name="description" content="Bộ sưu tập đồ tiện ích Shopee từ Tiểu Bạch Mao 🛒 Bấm vào sản phẩm để mua trực tiếp trên app Shopee!">

    <!-- Favicon -->
    <link rel="icon" type="image/x-icon" href="favicon.ico">
    <link rel="icon" type="image/png" sizes="32x32" href="favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="192x192" href="favicon-192x192.png">
    <link rel="apple-touch-icon" href="apple-touch-icon.png">

    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://bachkhoimaogia.github.io/TieuBachMao/shopee.html">
    <meta property="og:title" content="🛒 Góc Đồ Tiện Ích - Tiểu Bạch Mao">
    <meta property="og:description" content="Bộ sưu tập đồ tiện ích Shopee từ Tiểu Bạch Mao 🛒 Bấm vào sản phẩm để mua trực tiếp trên app Shopee!">
    <meta property="og:image" content="https://bachkhoimaogia.github.io/TieuBachMao/og-image.jpg">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="🛒 Góc Đồ Tiện Ích - Tiểu Bạch Mao">
    <meta name="twitter:description" content="Bộ sưu tập đồ tiện ích Shopee từ Tiểu Bạch Mao 🛒 Bấm vào sản phẩm để mua trực tiếp trên app Shopee!">
    <meta name="twitter:image" content="https://bachkhoimaogia.github.io/TieuBachMao/og-image.jpg">

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:'Plus Jakarta Sans',-apple-system,sans-serif; min-height:100vh; background:#0c0c1d; color:#fff; overflow-x:hidden; }}
.bg-orbs {{ position:fixed; top:0; left:0; right:0; bottom:0; z-index:0; overflow:hidden; pointer-events:none; }}
.orb {{ position:absolute; border-radius:50%; filter:blur(100px); opacity:0.4; }}
.orb-1 {{ width:350px; height:350px; background:#667eea; top:-80px; left:-60px; animation:drift 12s ease-in-out infinite alternate; }}
.orb-2 {{ width:300px; height:300px; background:#ee4d2d; bottom:-60px; right:-80px; animation:drift 10s ease-in-out infinite alternate-reverse; }}
@keyframes drift {{ 0%{{transform:translate(0,0) scale(1)}} 50%{{transform:translate(30px,-20px) scale(1.05)}} 100%{{transform:translate(-10px,10px) scale(1)}} }}
.header {{ position:sticky; top:0; z-index:100; background:rgba(12,12,29,0.85); backdrop-filter:blur(20px); -webkit-backdrop-filter:blur(20px); border-bottom:1px solid rgba(255,255,255,0.08); padding:14px 16px; display:flex; align-items:center; gap:12px; }}
.back-btn {{ display:flex; align-items:center; gap:6px; color:rgba(255,255,255,0.7); text-decoration:none; font-size:14px; font-weight:500; transition:color 0.2s; }}
.back-btn:hover {{ color:#fff; }}
.header-title {{ font-size:16px; font-weight:700; flex:1; }}
.header-count {{ font-size:12px; color:rgba(255,255,255,0.5); }}
.tabs {{ position:sticky; top:52px; z-index:99; background:rgba(12,12,29,0.9); backdrop-filter:blur(20px); -webkit-backdrop-filter:blur(20px); padding:10px 16px; display:flex; gap:8px; overflow-x:auto; -webkit-overflow-scrolling:touch; scrollbar-width:none; border-bottom:1px solid rgba(255,255,255,0.05); }}
.tabs::-webkit-scrollbar {{ display:none; }}
.tab {{ flex-shrink:0; padding:8px 16px; border-radius:20px; font-size:13px; font-weight:600; background:rgba(255,255,255,0.06); color:rgba(255,255,255,0.6); border:1px solid rgba(255,255,255,0.08); cursor:pointer; transition:all 0.3s; white-space:nowrap; }}
.tab:hover {{ background:rgba(255,255,255,0.1); color:#fff; }}
.tab.active {{ background:linear-gradient(135deg,#ee4d2d,#ff6633); color:#fff; border-color:transparent; box-shadow:0 2px 12px rgba(238,77,45,0.3); }}
.tab .count {{ display:inline-block; background:rgba(255,255,255,0.2); border-radius:10px; padding:1px 6px; font-size:11px; margin-left:4px; }}
.content {{ position:relative; z-index:1; padding:16px; max-width:800px; margin:0 auto; }}
.category {{ margin-bottom:28px; }}
.category-title {{ font-size:18px; font-weight:700; margin-bottom:14px; padding-left:4px; display:flex; align-items:center; gap:8px; }}
.category-title::before {{ content:''; display:inline-block; width:4px; height:20px; border-radius:2px; background:linear-gradient(135deg,#ee4d2d,#ff6633); }}
.products {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(150px,1fr)); gap:12px; }}
.product-card {{ background:rgba(255,255,255,0.06); border-radius:16px; overflow:hidden; border:1px solid rgba(255,255,255,0.08); transition:all 0.3s ease; text-decoration:none; color:inherit; display:flex; flex-direction:column; }}
.product-card:hover {{ transform:translateY(-3px); border-color:rgba(238,77,45,0.4); box-shadow:0 8px 24px rgba(238,77,45,0.15); }}
.product-card:active {{ transform:scale(0.97); }}
.product-img-wrap {{ position:relative; width:100%; padding-top:100%; background:rgba(255,255,255,0.03); overflow:hidden; }}
.product-img {{ position:absolute; top:0; left:0; width:100%; height:100%; object-fit:cover; transition:transform 0.3s; }}
.product-card:hover .product-img {{ transform:scale(1.05); }}
.product-info {{ padding:10px 12px 12px; flex:1; display:flex; flex-direction:column; }}
.product-name {{ font-size:12px; font-weight:500; line-height:1.4; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; color:rgba(255,255,255,0.9); flex:1; }}
.product-buy {{ margin-top:8px; display:flex; align-items:center; justify-content:center; gap:4px; padding:6px; border-radius:8px; background:linear-gradient(135deg,#ee4d2d,#ff6633); font-size:11px; font-weight:700; color:#fff; transition:opacity 0.2s; }}
.product-buy:hover {{ opacity:0.85; }}
.product-buy svg {{ width:12px; height:12px; }}
.product-img-wrap .placeholder {{ position:absolute; top:0; left:0; width:100%; height:100%; background:linear-gradient(110deg,rgba(255,255,255,0.03) 30%,rgba(255,255,255,0.08) 50%,rgba(255,255,255,0.03) 70%); background-size:200% 100%; animation:shimmer 1.5s infinite; }}
@keyframes shimmer {{ 0%{{background-position:200% 0}} 100%{{background-position:-200% 0}} }}
.shop-footer {{ text-align:center; padding:20px 16px 32px; color:rgba(255,255,255,0.3); font-size:12px; }}
.share-fab {{ position:fixed; bottom:24px; right:20px; z-index:200; width:50px; height:50px; border-radius:50%; border:none; background:linear-gradient(135deg,#667eea,#764ba2); color:#fff; box-shadow:0 4px 20px rgba(102,126,234,0.4); cursor:pointer; display:flex; align-items:center; justify-content:center; transition:transform 0.2s,box-shadow 0.2s; }}
.share-fab:hover {{ transform:scale(1.1); box-shadow:0 6px 28px rgba(102,126,234,0.5); }}
.share-fab:active {{ transform:scale(0.95); }}
.share-fab svg {{ width:22px; height:22px; }}
.share-toast {{ position:fixed; bottom:90px; left:50%; transform:translateX(-50%) translateY(20px); background:rgba(16,185,129,0.95); color:#fff; padding:10px 20px; border-radius:20px; font-size:13px; font-weight:600; opacity:0; transition:opacity 0.3s,transform 0.3s; pointer-events:none; z-index:201; white-space:nowrap; }}
.share-toast.show {{ opacity:1; transform:translateX(-50%) translateY(0); }}
.inapp-banner {{ background:rgba(255,193,7,0.15); border:1px solid rgba(255,193,7,0.3); border-radius:12px; padding:12px 16px; margin:0 16px 8px; font-size:13px; color:#ffd54f; line-height:1.5; text-align:center; font-weight:600; }}
@media (max-width:380px) {{ .products {{ grid-template-columns:repeat(2,1fr); gap:8px; }} .product-info {{ padding:8px 8px 10px; }} }}
    </style>
</head>
<body>
    <div class="bg-orbs"><div class="orb orb-1"></div><div class="orb orb-2"></div></div>
    <div class="inapp-banner" id="inappBanner">
        <p>🧡 Khi bấm link Shopee, nhớ chọn <br><strong>"Mở bằng app Shopee"</strong> để ủng hộ bà Mao <br> chút hoa hồng affiliate nha, <br>cảm ơn bạn nhiều lắm! 🙏</p>
    </div>
    <div class="header">
        <a href="index.html" class="back-btn">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polyline points="15 18 9 12 15 6"/></svg>
            Về
        </a>
        <span class="header-title">🛒 Góc Đồ Tiện Ích</span>
        <span class="header-count" id="totalCount"></span>
    </div>
    <div class="tabs" id="tabsContainer"></div>
    <div class="content" id="contentContainer"></div>
    <div class="shop-footer">
        <p>Bấm sản phẩm → mở thẳng app Shopee 🛍️</p>
        <p style="margin-top:4px">© 2026 Tiểu Bạch Mao</p>
    </div>
    <button class="share-fab" id="shareBtn" title="Chia sẻ trang này">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
    </button>
    <div class="share-toast" id="shareToast">✅ Đã copy link!</div>
<script>
var CATEGORIES = {data_json};

var isIOS = /iphone|ipad|ipod/i.test(navigator.userAgent);
var isAndroid = /android/i.test(navigator.userAgent);
function isInApp() {{ return /musical_ly|tiktok|bytedancewebview|instagram|fbav|fban|zalo/i.test(navigator.userAgent); }}



// Slug helper to match category by slug
function slugify(str) {{
    var map = {{'à':'a','á':'a','ả':'a','ã':'a','ạ':'a','ă':'a','ằ':'a','ắ':'a','ẳ':'a','ẵ':'a','ặ':'a','â':'a','ầ':'a','ấ':'a','ẩ':'a','ẫ':'a','ậ':'a','đ':'d','è':'e','é':'e','ẻ':'e','ẽ':'e','ẹ':'e','ê':'e','ề':'e','ế':'e','ể':'e','ễ':'e','ệ':'e','ì':'i','í':'i','ỉ':'i','ĩ':'i','ị':'i','ò':'o','ó':'o','ỏ':'o','õ':'o','ọ':'o','ô':'o','ồ':'o','ố':'o','ổ':'o','ỗ':'o','ộ':'o','ơ':'o','ờ':'o','ớ':'o','ở':'o','ỡ':'o','ợ':'o','ù':'u','ú':'u','ủ':'u','ũ':'u','ụ':'u','ư':'u','ừ':'u','ứ':'u','ử':'u','ữ':'u','ự':'u','ỳ':'y','ý':'y','ỷ':'y','ỹ':'y','ỵ':'y'}};
    return str.toLowerCase().split('').map(function(c){{return map[c]||c;}}).join('').replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
}}

var params = new URLSearchParams(location.search);
var catParam = params.get('cat');
var slugParam = params.get('slug');
var initialCatIdx = -1;
if (slugParam) {{
    CATEGORIES.forEach(function(c, i) {{ if (slugify(c.name) === slugParam) initialCatIdx = i; }});
}} else if (catParam !== null) {{
    CATEGORIES.forEach(function(c, i) {{ if (c.name === catParam) initialCatIdx = i; }});
}}

var tabsEl = document.getElementById('tabsContainer');
var allTab = document.createElement('div');
allTab.className = 'tab' + (initialCatIdx === -1 ? ' active' : '');
allTab.textContent = 'Tất cả';
allTab.onclick = function() {{ showCategory(-1); }};
tabsEl.appendChild(allTab);

var totalItems = 0;
CATEGORIES.forEach(function(cat, i) {{
    totalItems += cat.items.length;
    var tab = document.createElement('div');
    tab.className = 'tab' + (i === initialCatIdx ? ' active' : '');
    tab.innerHTML = cat.name + ' <span class="count">' + cat.items.length + '</span>';
    tab.onclick = function() {{ showCategory(i); }};
    tabsEl.appendChild(tab);
}});
document.getElementById('totalCount').textContent = totalItems + ' sản phẩm';

function showCategory(idx) {{
    var tabs = tabsEl.querySelectorAll('.tab');
    tabs.forEach(function(t, i) {{ t.classList.toggle('active', i === idx + 1); }});
    var content = document.getElementById('contentContainer');
    content.innerHTML = '';
    var catsToShow = idx === -1 ? CATEGORIES : [CATEGORIES[idx]];
    catsToShow.forEach(function(cat) {{
        var section = document.createElement('div');
        section.className = 'category';
        section.innerHTML = '<div class="category-title">' + cat.name + '</div>';
        var grid = document.createElement('div');
        grid.className = 'products';
        cat.items.forEach(function(item) {{
            var card = document.createElement('a');
            card.className = 'product-card';
            // Dùng shortUrl (s.shopee.vn) làm href — trình duyệt mở trực tiếp
            // Universal Links (iOS) + App Links (Android) sẽ mở app Shopee
            card.href = item.shortUrl;
            card.target = '_blank';
            card.rel = 'noopener';

            // Chỉ can thiệp JS khi ở in-app browser Android (để văng ra Chrome)
            if (isInApp() && isAndroid) {{
                card.onclick = function(e) {{
                    e.preventDefault();
                    var intentUrl = 'intent://' + item.shortUrl.replace(/^https?:\\/\\//, '') +
                        '#Intent;scheme=https;package=com.android.chrome;end';
                    window.location.href = intentUrl;
                }};
            }}
            // iOS & desktop: KHÔNG preventDefault → Universal Links / App Links tự xử lý

            card.innerHTML =
                '<div class="product-img-wrap">' +
                    '<div class="placeholder"></div>' +
                    '<img class="product-img" loading="lazy" alt="" src="' + item.image + '" onload="this.previousElementSibling.style.display=\\x27none\\x27" onerror="this.previousElementSibling.style.display=\\x27none\\x27;this.style.display=\\x27none\\x27">' +
                '</div>' +
                '<div class="product-info">' +
                    '<div class="product-name">' + item.name + '</div>' +
                    '<div class="product-buy">' +
                        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 01-8 0"/></svg>' +
                        'Mua ngay' +
                    '</div>' +
                '</div>';
            grid.appendChild(card);
        }});
        section.appendChild(grid);
        content.appendChild(section);
    }});
    window.scrollTo({{ top: 0, behavior: 'smooth' }});
}}

showCategory(initialCatIdx);

// Share button
document.getElementById('shareBtn').onclick = function() {{
    var shareUrl = location.href;
    var shareTitle = document.title;
    var shareText = '🛒 Xem đồ tiện ích Shopee từ Tiểu Bạch Mao!';
    if (navigator.share) {{
        navigator.share({{ title: shareTitle, text: shareText, url: shareUrl }}).catch(function(){{}});
    }} else {{
        navigator.clipboard.writeText(shareUrl).then(function() {{
            var toast = document.getElementById('shareToast');
            toast.classList.add('show');
            setTimeout(function() {{ toast.classList.remove('show'); }}, 2000);
        }});
    }}
}};
</script>
</body>
</html>'''


# ─── MAIN ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("═══ Crawl Shopee Affiliate Products ═══\n")

    # 1. Fetch groups
    print("📦 Fetching categories...")
    groups = fetch_groups()
    for g in groups:
        print(f"   {g['groupName']}: {g['totalCount']} items")

    # 2. Fetch products per group
    print("\n🔍 Fetching products per category...")
    all_items = fetch_products()
    print(f"   Total products: {len(all_items)}")

    categorized = {}
    for g in groups:
        items = fetch_products(g["groupId"])
        if items:
            categorized[g["groupName"]] = items
            print(f"   ✓ {g['groupName']}: {len(items)}")

    # Find uncategorized
    cat_ids = {i["linkId"] for items in categorized.values() for i in items}
    uncat = [i for i in all_items if i["linkId"] not in cat_ids]
    if uncat:
        categorized["Khác"] = uncat
        print(f"   ✓ Khác: {len(uncat)}")

    # 3. Resolve shortlinks
    print("\n🔗 Resolving shortlinks...")
    total_items = sum(len(v) for v in categorized.values())
    resolved = 0
    for cat, items in categorized.items():
        for item in items:
            item["resolved_url"] = resolve_shortlink(item["link"])
            resolved += 1
            if resolved % 20 == 0:
                print(f"   {resolved}/{total_items} resolved...")
            time.sleep(0.05)
    print(f"   ✓ All {resolved} links resolved")

    # 4. Save products.json
    output = {
        "groups": [{"id": g["groupId"], "name": g["groupName"], "count": int(g["totalCount"])} for g in groups],
        "products": categorized,
        "total": len(all_items)
    }
    products_path = os.path.join(DIR, "products.json")
    with open(products_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Saved products.json")

    # 5. Build categories data for HTML
    categories = []
    for cat, items in categorized.items():
        cat_items = []
        for item in items:
            img = item["image"]
            if img and not img.startswith("http"):
                img = "https://cf.shopee.sg/file/" + img
            cat_items.append({
                "name": item["linkName"],
                "image": img,
                "url": item["resolved_url"],
                "shortUrl": item["link"]
            })
        categories.append({"name": cat, "items": cat_items})

    # 6. Generate shopee.html
    html = generate_html(categories)
    html_path = os.path.join(DIR, "shopee.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"🌐 Generated shopee.html ({len(html)//1024}KB)")

    # 7. Summary
    print(f"\n═══ Done! ═══")
    print(f"📊 {len(categories)} categories, {total_items} products")
    print(f"\n👉 Tiếp theo chạy:")
    print(f"   git add -A && git commit -m 'Update products' && git push origin main && git push origin main:gh-pages")
