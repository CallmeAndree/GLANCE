# GLANCE — Kịch bản tổng

## Overview
- **Topic**: GLANCE — GNN with LLM Assistance for Neighbor- and Context-aware Embeddings.
  Học *khi nào* nên gọi LLM để hỗ trợ GNN trên text-attributed graph.
- **Hook**: "Gọi LLM cho **mọi** node là lãng phí. Vậy gọi cho node nào?"
- **Target Audience**: Sinh viên đã học GNN cơ bản (message passing, node classification),
  biết LLM ở mức khái niệm. Không yêu cầu biết RL.
- **Estimated Length**: ~13–15 phút (6 section, xem bảng dưới).
- **Key Insight**: **Local homophily** là tín hiệu dự báo mạnh nhất cho việc "node này
  LLM giúp được hay không" — và nó có thể ước lượng **không cần label**.
- **Resolution**: 480p15 khi làm nháp → 1080p60 cho bản nộp.
- **Aspect Ratio**: 16:9.

## Narrative Arc
Ta bắt đầu từ một nghịch lý: ghép LLM vào GNN tốn kém khủng khiếp nhưng chỉ tăng
accuracy vài phần trăm. Nguyên nhân không phải LLM vô dụng, mà vì ta áp *cùng một*
chiến lược fusion cho *mọi* node, nên phần LLM giúp được bị trung bình hoá mất trong
metric tổng. Ta đi tìm câu hỏi "node nào?": thử các heuristic sẵn có (degree, density,
uncertainty) và thấy chúng không ổn định giữa các dataset; rồi phát hiện local homophily
mới là tín hiệu đúng. GLANCE biến phát hiện đó thành một router học được, gọi LLM đúng
chỗ GNN thất bại — thắng tới +13% trên node heterophilous mà vẫn rẻ.

---

## Bản đồ section

| # | Section | Owner | Thời lượng | Mục paper |
|---|---|---|---|---|
| 0.1 | Related Work | Hoàng Phan | ~1'30" | §2, Appendix A (tr.2, 14) |
| 0.2 | Preliminaries | Trúc Mai | ~1'30" | §3 (tr.3), §4.2.1 (tr.4) |
| 1 | Vấn đề cốt lõi của GNN–LLM fusion | Trúc Mai | ~2'00" | §1 (tr.1–2) |
| 2 | Đánh giá routing heuristic hiện có | Hoàng Phan | ~2'00" | §4.1, Bảng 1 (tr.3–4) |
| 3 | Structural signal: $h_v$ & $\bar d_v$ | Nhựt Anh | ~2'15" | §4.2, Hình 1, Bảng 2 (tr.4–5) |
| 4 | Kiến trúc GLANCE | Trần Nguyên | ~2'30" | §5.1, Hình 2 (tr.5–6) |
| 5 | Training objective & thực nghiệm | Thiên Lâm | ~2'45" | §5.2, §6, Bảng 3–5 (tr.7–9) |

Tổng ≈ 14'30" kể cả title card. Mỗi section **tự chứa**: mở bằng title card,
kết bằng một câu "cầu nối" sang section sau (xem phần Transitions).

---

## Transitions & Flow

Mỗi section kết bằng đúng một câu dẫn, đã viết sẵn dưới đây. Đọc y nguyên câu này
ở scene cuối để mạch phim liền:

- **0.1 → 0.2**: "Trước khi xem GLANCE làm gì khác, thống nhất vài ký hiệu."
- **0.2 → 1**: "Có đủ ký hiệu rồi, ta quay lại câu hỏi: fusion hiện tại sai ở đâu?"
- **1 → 2**: "Nếu phải chọn node để gọi LLM, người ta đã chọn bằng cách nào?"
- **2 → 3**: "Heuristic thủ công không ổn định. Vậy tín hiệu nào mới đúng?"
- **3 → 4**: "Đã có tín hiệu. Giờ ráp nó vào một kiến trúc chạy được."
- **4 → 5**: "Router không khả vi. Vậy huấn luyện nó kiểu gì — và có thật sự hiệu quả?"

## Shared Elements
- **TAG motif**: đồ thị 12 node dựng bằng `demo_tag()` xuất hiện ở section 0.2, 1, 3, 4.
  Toạ độ định nghĩa một lần trong `glance_style.py` (`DEMO_POS`, `DEMO_EDGES`, `DEMO_LABELS`)
  để người xem nhận ra cùng một đồ thị. Node 4 = hub homophily cao, node 9 = node homophily thấp.
- **Hai khối model**: `labeled_box("GNN", C_GNN)` bên trái, `labeled_box("LLM", C_LLM)`
  bên phải — luôn đặt đúng thứ tự đó, mọi section.
- **Node được route** luôn có viền tím `C_ROUTER`; node không route giữ nguyên màu.
- **Dấu ✓/✗** dùng `check()` / `cross()`, không tự vẽ.
- Mọi số liệu kèm stamp `source("Bảng X, tr.Y")` ở góc dưới phải.

## Color Palette
| Vai trò | Hằng số | Mã |
|---|---|---|
| Nền | `BG` | `#0E1116` |
| Chữ chính | `INK` | `#E8ECF1` |
| Chữ phụ / ghi chú | `MUTED` | `#8B97A8` |
| GNN | `C_GNN` | `#3ECFB2` (teal) |
| LLM | `C_LLM` | `#F2B441` (amber) |
| Router / GLANCE | `C_ROUTER` | `#A98BFF` (violet) |
| Đúng / lợi ích | `C_GOOD` | `#5BD97E` |
| Sai / chi phí | `C_BAD` | `#FF6B6B` |
| Cạnh đồ thị | `C_EDGE` | `#4A5468` |
| Nhấn mạnh chung | `C_HIGHLIGHT` | `#6EA8FE` |

## Quy tắc thuyết minh
- Mỗi câu phụ đề ≤ 2 dòng, ≤ ~14 từ. Nói chậm, một ý một nhịp.
- Chữ trên hình giữ nguyên thuật ngữ tiếng Anh; lời trong `VO` phải viết theo cách
  model TTS đọc tiếng Việt. Dùng phiên âm đã chốt: `node` → "nót"; các thuật ngữ
  còn lại ưu tiên tiếng Việt tự nhiên, như `routing` →
  "định tuyến", `embedding` → "véc-tơ biểu diễn". Phiên âm acronym thống nhất:
  `LLM` → "eo eo em", `MLP Q` → "em eo pi khiu", `GNN` → "gi en en",
  `GLANCE` → "gờ lans".
- Lần đầu xuất hiện thuật ngữ: hiện chữ tiếng Anh + một dòng giải thích tiếng Việt.
