# Bio-link-Tiktok
Tạo page bio cho TikTok + storefront Lazada tĩnh bằng GitHub Pages.

## Refresh dữ liệu Lazada

Source-of-truth cho category/source URL nằm ở:

- `lazada_sources.json`

Để cập nhật payload storefront:

```bash
python crawl.py
```

Output sẽ được ghi vào:

- `products_lazada.json`
- `products.json`

Lưu ý:

- `products_shopee.json` hiện là legacy, không còn là upstream cho storefront Lazada.
- Nếu muốn mở rộng mỗi category thành nhiều sản phẩm thật, thay seed/share URL hiện tại bằng category/listing URL thật trong `lazada_sources.json`.

## Secret Scan Safety

Repo da them bo loc de tranh push nham thong tin nhay cam.

### Cai hook pre-push (chay 1 lan)

```bash
bash scripts/install-hooks.sh
```

### Quet thu cong

```bash
bash scripts/scan-secrets.sh
```

Neu script phat hien pattern nguy hiem (token/cookie/password), lenh se fail de chan push.
