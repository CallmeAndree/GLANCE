---
name: glance-video
description: Làm việc an toàn và nhất quán trong repo video GLANCE bằng Manim Community Edition. Dùng skill này mỗi khi Codex được yêu cầu viết, sửa, render, debug hoặc review scene/video GLANCE, đặc biệt với sections/, glance_style.py, build.sh, tools/, phụ đề, số liệu paper hoặc kết quả render.
---

# Làm việc trong repo video GLANCE

## Nạp workflow chuẩn

1. Xác định root repo chứa `glance_style.py`, `build.sh`, `sections/` và `.claude/`.
2. Đọc toàn bộ [`../../../.claude/skills/glance-video/SKILL.md`](../../../.claude/skills/glance-video/SKILL.md) trước khi phân tích, sửa file hay chạy lệnh.
3. Tuân thủ tài liệu đó như nguồn quy tắc chuẩn cho cấu trúc repo, phạm vi section, dữ liệu paper, API style, render/build và kiểm tra hình ảnh.

Giữ `.claude/skills/glance-video/SKILL.md` làm nguồn nội dung duy nhất để Claude Code và Codex không lệch quy ước. Chỉ ghi hướng dẫn riêng cho Codex trong adapter này.

## Áp dụng bằng Codex

- Chạy mọi lệnh dự án từ root repo; dùng đúng conda env `graphdm` như workflow chuẩn chỉ định.
- Trước khi sửa một section, đọc `TASK.md`, `plan.md` và phần liên quan trong `docs/paper-map.md` theo đúng thứ tự workflow.
- Sau khi render, dùng công cụ xem ảnh của Codex để kiểm tra frame đã trích; không kết luận bố cục đúng chỉ dựa vào exit code.
- Giữ nguyên mọi thay đổi không liên quan của người dùng và không sửa section khác nếu chưa được yêu cầu rõ ràng.
- Nếu cần cập nhật quy ước dùng chung, sửa nguồn chuẩn trong `.claude/skills/glance-video/SKILL.md`, rồi chỉ cập nhật adapter này khi thay đổi dành riêng cho Codex.
