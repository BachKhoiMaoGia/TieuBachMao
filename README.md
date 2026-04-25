# Bio-link-Tiktok
Tạo page bio cho TikTok + storefront Lazada tĩnh bằng GitHub Pages.

## Refresh dữ liệu Lazada

Source-of-truth cho category/source URL nằm ở:

- `lazada_sources.json`

Playbook triển khai thay thế Shopee => Lazada cho web khác:

- `docs/lazada-migration-playbook.md`

Theo dõi các link Lazada chưa ra được card hợp lệ:

- `lazada_link_errors.md`

### Thêm link sản phẩm affiliate

Dùng CLI helper để thêm link Lazada short affiliate vào đúng category:

```bash
python add_product.py "https://s.lazada.vn/s.xxxx?t=p-xxx"
```

Hoặc thêm nhiều link một lần:

```bash
python add_product.py links.txt
```

Trong đó `links.txt` có mỗi dòng một link. Script sẽ resolve link, fetch tên sản phẩm, gợi ý category, hỏi xác nhận rồi append link vào key `sources` của category trong `lazada_sources.json`.

Script này chỉ cập nhật config nguồn. Sau khi thêm link, nếu muốn build lại payload storefront thì chạy bước refresh bên dưới.

Để cập nhật payload storefront:

```bash
python crawl.py
```

Output sẽ được ghi vào:

- `products_lazada.json`
- `products.json`

Lưu ý:

- `products_shopee.json` hiện là legacy, không còn là upstream cho storefront Lazada.
- `add_product.py` không chạy `crawl.py` và không tự regenerate `products_lazada.json`.
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
