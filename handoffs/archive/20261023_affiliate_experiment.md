# Handoff — 2026-10-23 affiliate experiment

> **SUPERSEDED / ĐÃ HỦY BỎ**
> Thử nghiệm popup/random affiliate companion tab này đã bị hủy bỏ hoàn toàn và được thay thế bởi cơ chế giỏ hàng tự nguyện (voluntary shopping links).
> **Tài liệu hiện hành:** Xem [handoffs/20261024_current_state.md](../20261024_current_state.md) và [handoffs/20261023_voluntary_shop_links.md](../20261023_voluntary_shop_links.md).
> **KHÔNG khôi phục logic popup, script companion tab hoặc catalog fetch lên trang chủ.**

Status: SUPERSEDED / HỦY BỎ. Lưu trữ lịch sử tham khảo.

## Scope and decisions
Read README.md, context.md, latest Lazada refresh handoff, index.html and Pages workflow.
User superseded the previous separate-Shop-button plan: remove landing catalog,
keep original social/donation actions, open one additional affiliate tab on ordinary
button clicks, randomly selecting TikTok Shop or Lazada with equal probability.
Latest Lazada URL replaces the two earlier URLs supplied in conversation.
User was informed of affiliate-policy and popup-blocking risks before authorizing.
A visible disclosure names both platforms. No hidden iframe, background request,
load-time tab opening, popup bypass, automatic retries, or analytics were added.

## Files
- index.html: remove category markup, CSS and JSON-fetch logic; add disclosure and
  deferred scripts; preserve original links and bank-copy handler.
- site-config.js: two current URLs, enabled switch, review date comment.
- assets/js/affiliate.js: ordinary trusted click handler; preserve native actions;
  allow HTTPS links on vt.tiktok.com and s.lazada.vn only.
- tests/affiliate.test.cjs: 8 VM-based tests of the production script.
- README.md/context.md: current behavior and scope override.

## Verification
- Red: 7 tests failed for missing click handler before implementation.
- Green: `node tests/affiliate.test.cjs`, all 8 passed.
- `node --check` for config, affiliate handler and extracted inline script passed.
- HTML parse comparison against HEAD: all 10 anchor destinations and bank-copy
  data unchanged; catalog fetch/grid removed.
- Standard `node --test` runner failed in this environment without detailed child
  output; direct execution of the same node:test suite ran successfully.
- Browser/mobile/in-app checks and actual affiliate attribution NOT verified.

## Limits and next steps
Popup restrictions may block the additional tab or affect multi-tab behavior;
unit tests do not prove real browser navigation. Test mobile/in-app before publish.
No tracking dashboard or scheduled reminder; review target 2026-11-23.
To disable companion tabs set enabled=false in site-config.js.
No generated payloads, legacy routes, Python scripts or deploy workflow changed.
Do not assume the full AG migration plan is complete.
Existing untracked .agents/ and CONTEXT.md symlink left untouched.
