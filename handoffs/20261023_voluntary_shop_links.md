# Handoff — 2026-10-23 voluntary shop links

Status: Implemented locally and fully verified via browser automation. Ready for commit. Not pushed or deployed.
Read first: context.md (current override), README.md, index.html.

## 1. Mục tiêu & Quyết định thiết kế
- Thay thế hoàn toàn thử nghiệm popup/random affiliate trước đó bằng hai nút mua sắm tự nguyện đặt dưới header, trước danh sách kênh mạng xã hội.
- Loại bỏ hoàn toàn khối hiển thị card sản phẩm và không gọi tải catalog JSON (`products_lazada.json`) trên trang chủ.
- Người dùng chủ động bấm giỏ nào thì chỉ mở đúng giỏ hàng đó:
  - **Giỏ TikTok Shop:** `https://vt.tiktok.com/ZS9UwsBsuFLKt-KD8oG/`
  - **Giỏ Lazada:** `https://s.lazada.vn/s.pl59e?t=h5`
- Không có hành vi random, không popup tự động, không mở kèm link affiliate khi người dùng bấm social, donate hay copy STK TPBank.

## 2. Chi tiết thay đổi code
- **`index.html`:**
  - Khối mua sắm gồm thông điệp kêu gọi ủng hộ hoa hồng và 2 nút bấm: Giỏ TikTok Shop & Giỏ Lazada.
  - Sử dụng SVG inline cho icon tim (header) và 2 icon giỏ hàng: kích thước chuẩn 16×16px, `aria-hidden="true"`, `focusable="false"`, màu sắc theo `currentColor`.
  - Thuộc tính liên kết: `target="_blank" rel="noopener sponsored"`.
  - CSS responsive tinh chỉnh cho màn hình hẹp ($\le 400\text{px}$ và $320\text{px}$): cho phép bẻ dòng tiêu đề dài khi cần, giảm padding lồng nhau, khối donate dùng grid 2 cột tránh chèn ép chữ.
  - Giữ nguyên toàn bộ 10 liên kết social/xem phim và nút copy STK TPBank ban đầu.
- **Dọn dẹp code thử nghiệm:**
  - Xóa bỏ các file thử nghiệm popup trước đó: `site-config.js`, `assets/js/affiliate.js`, và test VM.
- **Tài liệu:**
  - Cập nhật `README.md`, `context.md`.

## 3. Kết quả xác minh thực tế (Browser Automation)
Môi trường kiểm thử: Google Chrome for Testing (v156.0.8078.47) chạy qua `puppeteer-core` với script `audit.cjs` trên cổng nội bộ `http://127.0.0.1:8765/`.

### 3.1 Giao diện & Đo đạc Responsive
- **320px × 740px:**
  - `scrollWidth = clientWidth = 320px` (không tràn ngang).
  - Khoảng cách giữa tiêu đề kênh `@gocphimtieubach` và badge "Kênh chính" = 10px (`overlaps: false`).
  - Nút giỏ hàng có chiều cao 54px (đạt chuẩn touch target $\ge 44\text{px}$); khoảng cách giữa SVG và chữ là 5px.
- **375px × 812px:**
  - `scrollWidth = clientWidth = 375px` (không tràn ngang).
  - Khoảng cách tiêu đề và badge = 10px (`overlaps: false`).
  - Nút giỏ hàng có kích thước 150×44px.
- **390px × 844px & 1440px × 900px:**
  - Hiển thị chuẩn xác, không tràn ngang, không vỡ layout.

### 3.2 Kiểm tra SVG
- Icon tim: `<svg class="shop-icon">` kích thước 16×16px, `fill="currentColor"`, có `aria-hidden="true"`, `focusable="false"`.
- Icon giỏ TikTok & Lazada: `<svg class="shop-icon">` kích thước 16×16px, `stroke="currentColor"`, `stroke-width="1.8"`, có `aria-hidden="true"`, `focusable="false"`.

### 3.3 Tương tác click thật & Clipboard
- **Click Giỏ TikTok:** Kích hoạt mở popup tab mới trỏ tới link TikTok Shop rút gọn và phân giải thành công tới trang sản phẩm TikTok.
- **Click Giỏ Lazada:** Kích hoạt mở popup tab mới trỏ tới đúng `https://s.lazada.vn/s.pl59e?t=h5`.
- **Click Social TikTok:** Mở tab mới trỏ tới `https://www.tiktok.com/@gocphimtieubach` mà không mở kèm bất kỳ tab affiliate nào.
- **Click nút Copy TPBank:**
  - Đọc clipboard thật (`navigator.clipboard.readText()`): nhận đúng chuỗi `TPBank · 22992011295`.
  - Hiển thị toast thông báo "Đã copy thông tin TPBank".
  - Số popup tab phát sinh: **0**.
- **Console errors:** 0 lỗi.

## 4. Trạng thái còn lại & Rủi ro chưa kiểm tra
- **Chưa thử nghiệm trên thiết bị di động vật lý:** Kiểm thử hiện tại được thực hiện bằng trình duyệt Chrome headless chuẩn với giả lập viewport di động.
- **Chưa ghi nhận hoa hồng thực tế:** Cần theo dõi chuyển đổi đơn hàng trên dashboard TikTok Shop Affiliate và Lazada Affiliate sau khi trang được đưa lên production.
- Không thay đổi các route storefront (`lazada.html`, `shopee.html`), crawler Python hay dataset `products_lazada.json`.
- Thư mục `.agents/` và symlink `CONTEXT.md` được giữ nguyên trạng thái không track trong Git.
