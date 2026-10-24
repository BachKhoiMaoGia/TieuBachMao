# gocphimtieubach.page (Tiểu Bạch Mao Bio Link)

Website tĩnh chính thức phục vụ liên kết Bio mạng xã hội (TikTok, Facebook, Telegram, YouTube), thông tin donate và liên kết mua sắm tự nguyện cho cộng đồng **Tiểu Bạch Mao**.

- **Tên miền:** [https://gocphimtieubach.page](https://gocphimtieubach.page)
- **Repository:** `BachKhoiMaoGia/TieuBachMao` (nhánh `main`)
- **Lưu ý:** Đây là repository website tĩnh, **không nhầm lẫn** với repo công cụ xử lý video `ToolTBM.git` (nằm ở workspace `TieuBachMao`).
- **Tài liệu bàn giao chi tiết:** Xem [handoffs/20261024_current_state.md](handoffs/20261024_current_state.md).

---

## 1. Hiện trạng Trang chủ (`index.html`)

Trang chủ được xây dựng bằng **HTML5, CSS3 và Vanilla JavaScript thuần**, triển khai trực tiếp qua GitHub Pages không cần bước build framework.

### Khối Giỏ Mua Sắm Tự Nguyện (Dưới Header, trước Social)
- Hai nút liên kết mua sắm trực tiếp để người xem chủ động ủng hộ hoa hồng:
  - **Giỏ TikTok Shop:** `https://vt.tiktok.com/ZS9UwsBsuFLKt-KD8oG/`
  - **Giỏ Lazada:** `https://s.lazada.vn/s.pl59e?t=h5`
- **Cách cập nhật link:** Chỉnh sửa trực tiếp thuộc tính `href` trong [index.html](index.html).
- **Thiết kế & Đồ họa:**
  - Icon tim ở tiêu đề mua sắm và 2 icon giỏ hàng sử dụng **SVG inline** (16×16px, `currentColor`, `aria-hidden="true"`, `focusable="false"`).
  - Tối ưu responsive hoàn toàn trên các màn hình nhỏ (320px, 375px, 390px) và desktop (1440px), không tràn ngang, không bị đè chữ hay kẹt badge.
- **Quy tắc tương tác:**
  - **Không có popup, không random tab:** Người dùng bấm giỏ nào thì chỉ mở đúng giỏ đó (`target="_blank" rel="noopener sponsored"`).
  - **Bảo toàn hành vi gốc:** Các liên kết mạng xã hội (TikTok, Facebook, Telegram, YouTube) và website Xem Phim mở độc lập, tuyệt đối **không mở kèm tab affiliate ngầm**.
  - **Ủng hộ Mao / Donate:** Bấm nút copy STK TPBank (`22992011295`) sẽ ghi trực tiếp vào clipboard máy và hiện toast thông báo "Đã copy thông tin TPBank", không mở bất kỳ tab hay liên kết ngoài nào.
  - **Không tải catalog JSON trên trang chủ:** Trang chủ không fetch `products_lazada.json` để tối đa hóa tốc độ tải và giữ giao diện tinh gọn.

---

## 2. Phần storefront và dữ liệu được giữ lại ngoài luồng trang chủ

Các thành phần sau vẫn tồn tại nguyên vẹn trong repository phục vụ nhu cầu tra cứu và storefront chuyên sâu khi người dùng truy cập trực tiếp URL, nhưng **tách biệt khỏi luồng trang chủ**:

- **Storefront Lazada (`lazada.html`):** Trang danh mục sản phẩm chi tiết theo tab/slug, tải dữ liệu từ `products_lazada.json`.
- **Trang chuyển hướng Shopee (`shopee.html`):** Giữ vai trò redirect shim sang `lazada.html` để duy trì tính tương thích với các liên kết cũ trước đây.
- **Trang lỗi 404 (`404.html`):** Fallback tĩnh của GitHub Pages.
- **Dataset sản phẩm:** `products_lazada.json`, `products.json` (mirror), và `products_shopee.json` (legacy).

---

## 3. Tài liệu tham khảo: Pipeline Crawler & Cập nhật dữ liệu Lazada

> ⚠️ **LƯU Ý:** Không chạy crawler khi đang thực hiện các tác vụ sửa tài liệu hoặc chỉnh giao diện trang chủ.

### Thêm link sản phẩm Affiliate Lazada vào config nguồn
File cấu hình nguồn: `lazada_sources.json`. Dùng công cụ CLI để append link:

```bash
python add_product.py "https://s.lazada.vn/s.xxxx?t=p-xxx"
# Hoặc thêm nhiều link từ file:
python add_product.py links.txt
```
*Lưu ý: `add_product.py` chỉ cập nhật config `lazada_sources.json`, không tự động chạy crawler và không sửa `products_lazada.json`.*

### Chạy crawler cập nhật payload storefront (Khi cần)
```bash
python crawl.py
```
- Script đọc `lazada_sources.json` và tạo ra `products_lazada.json` (đồng thời mirror sang `products.json`).
- Theo dõi các link lỗi tại `lazada_link_errors.md`.
- **CẢNH BÁO:** Không chạy `crawl_shopee.py` vì script cũ này có thể sinh lại `shopee.html` ghi đè trang chuyển hướng tương thích.

---

## 4. Kiểm tra an toàn bảo mật (Secret Scanning)

Repo được tích hợp bộ lọc chống rò rỉ token, cookie và password:

- **Cài đặt hook pre-push (chạy 1 lần):**
  ```bash
  bash scripts/install-hooks.sh
  ```
- **Quét thủ công kiểm tra bí mật:**
  ```bash
  bash scripts/scan-secrets.sh
  ```
- Script sẽ chặn push nếu phát hiện mẫu dữ liệu nhạy cảm.

---

## 5. Quy trình phát triển & Nghiệm thu
1. Trước khi làm việc: Đọc [context.md](context.md) và [handoffs/20261024_current_state.md](handoffs/20261024_current_state.md).
2. Kiểm tra `git status` trước và sau mỗi thay đổi.
3. Chạy `git diff --check` và `bash scripts/scan-secrets.sh` trước khi commit.
4. **Tuyệt đối không commit:** thư mục `.agents/`, symlink `CONTEXT.md`, hay các file artifact kiểm thử ngoài workspace.
