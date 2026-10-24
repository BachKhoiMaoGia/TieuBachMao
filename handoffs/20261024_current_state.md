# Handover — Trạng thái hiện tại của dự án (2026-10-24)

> **Dành cho Agent kế nhiệm:** Đọc tài liệu này đầu tiên. Đây là nguồn chân lý hiện tại về kiến trúc, quyết định sản phẩm và các file đang hoạt động. **KHÔNG** khôi phục logic popup mở tab ngầm, không tự ý đưa catalog JSON lên trang chủ.

---

## 1. Baseline & Trạng thái Git / Deploy
- **Baseline commit:** `e86aee8f7c41a55912e38a3c9f0126ed44f9d74e`
  - Message: `feat: replace landing catalog with voluntary shopping links`
  - Đã push lên nhánh `main` của remote `https://github.com/BachKhoiMaoGia/TieuBachMao.git`.
- **Trạng thái deploy (Xác minh qua GitHub Actions):**
  - **ĐÃ DEPLOY THÀNH CÔNG:** Workflow `Deploy to GitHub Pages` chạy trên commit `e86aee8` đã hoàn thành thành công (`conclusion: success`, thời gian chạy 23s) và workflow `Secret Scan` cũng đã đạt (`conclusion: success`, 8s).
  - Trang web chính thức đang hoạt động tại: `https://gocphimtieubach.page`.

---

## 2. Nhận diện Repo & Phạm vi công việc
- **Repo này:** Website chính thức `gocphimtieubach.page` (Remote: `BachKhoiMaoGia/TieuBachMao.git`).
- **Lưu ý quan trọng:** **KHÔNG** nhầm lẫn với repo công cụ xử lý video/phim `ToolTBM.git` (nằm ở workspace `TieuBachMao`).
- **Tech stack:** HTML5, CSS3 và Vanilla JavaScript thuần. **Không sử dụng framework build** (không Next.js, không Vite, không React, không bundler).

---

## 3. Kiến trúc hiện tại & Bản đồ file cần sửa

| Nhu cầu thay đổi | File cần sửa | Lưu ý |
|---|---|---|
| **Thay đổi link/icon/nội dung trang chủ bio** | `index.html` | Chứa toàn bộ CSS inline và JS inline của trang chủ. Không import file script bên ngoài. |
| **Sửa 2 link giỏ hàng Affiliate** | `index.html` | Cập nhật trực tiếp thuộc tính `href` của `.shop-tiktok` và `.shop-lazada`. |
| **Sửa số tài khoản / thông tin donate** | `index.html` | Cập nhật thuộc tính `data-copy` trên `.copy-bank-btn` và text hiển thị. |
| **Sửa trang storefront danh mục phụ** | `lazada.html` | Trang hiển thị danh mục sản phẩm chi tiết theo tab/slug, đọc từ `products_lazada.json`. |
| **Thêm link affiliate Lazada vào config** | `lazada_sources.json` | Dùng CLI helper: `python add_product.py <link>` (chỉ cập nhật config, không tự chạy crawler). |
| **Crawl cập nhật dữ liệu sản phẩm Lazada** | `crawl.py` | Tạo ra `products_lazada.json` và `products.json`. **Không tự tiện chạy trong các phiên dọn dẹp/sửa docs.** |

### Phân biệt rõ phần cũ được giữ lại ngoài luồng trang chủ:
- `lazada.html` vẫn tồn tại nguyên vẹn, phục vụ xem danh mục chi tiết nếu người dùng truy cập trực tiếp URL.
- `shopee.html`: Shim chuyển hướng sang `lazada.html` để giữ tương thích các link cũ.
- `404.html`: Trang tĩnh fallback cho GitHub Pages.
- `crawl_shopee.py`: Script crawl Shopee cũ. **CẢNH BÁO:** Chạy file này có thể sinh lại file `shopee.html` ghi đè trang redirect. Hiện tại không chạy file này.
- Các file trên **được giữ lại có chủ đích**, không bị xóa và không nằm trong luồng chạy của trang chủ `index.html`.

---

## 4. Quyết định sản phẩm: Đã chốt vs Đã hủy

### ✅ Quyết định ĐÃ CHỐT:
1. **Hai giỏ hàng tự nguyện (Voluntary Shop Links):**
   - Đặt ngay dưới header (lời giới thiệu Tiểu Bạch Mao) và đứng trước danh sách các kênh mạng xã hội.
   - **Giỏ TikTok Shop:** `https://vt.tiktok.com/ZS9UwsBsuFLKt-KD8oG/`
   - **Giỏ Lazada:** `https://s.lazada.vn/s.pl59e?t=h5`
   - Thuộc tính: `target="_blank" rel="noopener sponsored"`.
2. **Không làm phiền người dùng:**
   - Người dùng chủ động bấm giỏ nào thì chỉ mở đúng giỏ đó.
   - Bấm vào các kênh Social (TikTok, Facebook, Telegram, YouTube) hay Website Xem Phim chỉ mở đúng kênh đó, **tuyệt đối không mở kèm tab affiliate ngầm**.
   - Bấm nút Copy TPBank chỉ ghi clipboard và hiện Toast thông báo, **không mở popup**.
   - Trang chủ **không gọi fetch `products_lazada.json`** và không render card sản phẩm để tối ưu tốc độ tải trang.
3. **Đồ họa SVG inline chuẩn mực:**
   - Icon tim ở tiêu đề mua sắm và 2 icon giỏ hàng dùng SVG inline thuần: 16×16px, `currentColor`, `aria-hidden="true"`, `focusable="false"`.

### ❌ Phương án ĐÃ HỦY BỎ (Không khôi phục):
- **Hủy bỏ hoàn toàn thử nghiệm popup companion tab:** Ý tưởng tự động mở tab affiliate khi người dùng bấm bất kỳ link nào trên trang (trước đây có trong `site-config.js`, `assets/js/affiliate.js`) đã bị loại bỏ vì vi phạm chính sách và làm giảm trải nghiệm người dùng. Tài liệu thử nghiệm cũ đã được lưu trữ tại `handoffs/archive/20261023_affiliate_experiment.md` với nhãn `SUPERSEDED`.
- **Hủy bỏ kế hoạch refactor sang thư mục public/ hoặc framework:** Giữ mô hình file tĩnh đơn giản, trực tiếp tại root của repo.

---

## 5. Kết quả kiểm tra Browser Automation & Giới hạn

### Kết quả đã xác minh (Không cần chạy lại kiểm thử nếu không sửa code):
- Kiểm thử được thực hiện bằng Google Chrome for Testing Headless (`v156.0.8078.47`) và `puppeteer-core`:
  - **320px × 740px:** `scrollWidth === clientWidth === 320px` (không tràn ngang). Khoảng cách giữa `@gocphimtieubach` và badge "Kênh chính" là 10px (`overlaps: false`). Chiều cao nút giỏ hàng đạt 54px.
  - **375px × 812px:** `scrollWidth === 375px`, nút bấm chia 2 cột đều 150×44px, khoảng cách badge 10px.
  - **390px × 844px & 1440px × 900px:** Bố cục hoàn hảo, cân đối.
  - **Click thật:** Giỏ TikTok phân giải đến trang sản phẩm TikTok Shop; Giỏ Lazada mở đúng link; Social mở đúng profile; Nút TPBank ghi đúng `TPBank · 22992011295` vào clipboard và mở đúng 0 popup tab.
  - **Console:** 0 lỗi JavaScript.

### Vị trí Artifacts kiểm thử:
- Toàn bộ ảnh chụp thực tế và metrics lưu tại thư mục cục bộ của IDE:
  `/home/dp/.gemini/antigravity-ide/brain/1f4f2361-39b0-42a4-8c97-a8bdeb9e3d2b/verification_artifacts/`
  *(Bao gồm: `audit_report.json`, `audit.cjs`, `mobile-320x740-full.png`, `mobile-375x812-full.png`, `desktop-1440x900-viewport.png`, v.v.).*
- **Lưu ý:** Đây là artifact sinh ra trên máy local `dell-sever`, không đưa vào git repository để tránh phình dung lượng.

### Giới hạn còn lại chưa kiểm tra:
1. **Thiết bị điện thoại vật lý thực tế:** Chưa kiểm tra hành vi mở deep-link ứng dụng TikTok/Lazada trên trình duyệt Safari iOS hoặc Chrome Android thật.
2. **Đối soát hoa hồng Affiliate:** Chưa có dữ liệu thực tế về ghi nhận click/đơn hàng trên dashboard TikTok Shop Affiliate và Lazada Affiliate.

---

## 6. Các file Local / Untracked được giữ có chủ đích
- `.agents/`: Chứa Session Memory (`.agents/memory/sessions.md`) và Agent Customizations của IDE. Không stage vào git.
- `CONTEXT.md`: Symlink trỏ đến `context.md` để đảm bảo tương thích cho các công cụ ngữ cảnh. Không commit symlink này.

---

## 7. Các bước tiếp theo (Next Steps)
1. **Smoke-check trên điện thoại thật:** Chủ repo / tester mở trực tiếp `https://gocphimtieubach.page` trên điện thoại cá nhân, bấm thử 2 giỏ hàng và copy STK để kiểm tra cảm giác thực tế.
2. **Kế hoạch tương lai (nếu có yêu cầu từ chủ repo):**
   - Tách CSS/JS inline của `index.html` thành file riêng.
   - Cấu hình lại workflow artifact deploy Pages để tách riêng các script Python / docs nếu cần làm gọn gói deploy.
   - Tuyệt đối không làm trước khi có yêu cầu cụ thể.
