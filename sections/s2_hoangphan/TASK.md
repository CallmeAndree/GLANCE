# Task 2 — Đánh giá các routing heuristic hiện có

**Owner:** Hoàng Phan · **File:** `s2_hoangphan.py` · **Thời lượng:** ~10'20" (đo 10'18" ở 480p15)
**Nguồn:** paper §4 mở đầu và §4.1 + Bảng 1 (tr.3–4).

> Mục tiêu ban đầu là ~2'00". Nhóm đã thống nhất giữ bản dài, xem ghi chú trong `plan.md`.

## Cần trình bày

1. **Đặt vấn đề**: nếu chỉ gọi LLM cho một phần node thì chọn node nào? Ba tiêu chí đã được
   dùng trong các paper trước, mỗi tiêu chí route **top-k%** node ($k \in \{10, 15, 20\}$)
   sang một LLM đã fine-tune:
   - **degree thấp** $d_v$ (E-LLaGNN)
   - **clustering density thấp** (C-density, LLM-GNN)
   - **uncertainty cao** — ước lượng bằng dropout (LOGIN)

2. **Cách đo — Net Correction Score (NCS)**:
   $\text{NCS} = (|WC| - |CW|)\,/\,|R|$ với $R$ là tập node được route, $WC$ = node GNN sai
   nhưng LLM sửa đúng, $CW$ = node GNN đúng mà LLM làm hỏng.
   NCS $= 1$: LLM sửa được mọi node được route. NCS $= -1$: LLM phá hỏng tất cả.
   Giải thích trực quan tại sao đây là thước đo đúng cho *routing*, chứ không phải accuracy tổng.

3. **Setup thí nghiệm**: Cora, Pubmed, Arxiv23; hai backbone GCN và GCNII; hai loại feature
   (original và enhanced sinh bởi Qwen3-8B); GNN và LLM đều **freeze**, chỉ đổi tiêu chí route.
   Có cả **random router** làm mốc so sánh.

4. **Kết quả và kết luận** (Bảng 1, tr.4) — điểm cần làm bật:
   - Uncertainty có vẻ hứa hẹn trên Pubmed và Arxiv23 (GCN Enh.: **0.20 / 0.18 / 0.17** trên
     Pubmed; **0.15 / 0.13 / 0.13** trên Arxiv23 ứng với k = 10/15/20%).
   - Nhưng **cùng chiến lược đó lại âm trên Cora**: **−0.09 / −0.03 / −0.01** — tệ hơn cả
     random router.
   - Degree và C-density dao động quanh 0, không có chiến lược nào robust xuyên dataset.
   - ⇒ **Heuristic tĩnh là dataset-dependent**. Cần một tín hiệu routing có nguyên tắc và
     chuyển giao được giữa các dataset, thay vì luật do người đặt.

## Lưu ý

- Trọng tâm section này là **phủ định**: chứng minh cách làm cũ không ổn định. Đừng giới
  thiệu homophily ở đây — đó là section 3.
- `bar_chart()` trong `glance_style.py` hỗ trợ giá trị âm, dùng để dựng lại Bảng 1 (đối chiếu
  Pubmed và Cora cạnh nhau là cách bật kết luận rõ nhất).
- Toàn bộ số liệu Bảng 1 có trong `docs/paper-map.md`.

**Câu cầu nối cuối section:** *"Heuristic thủ công không ổn định. Vậy tín hiệu nào mới đúng?"*

## Checklist nộp

- [x] `manim -ql sections/s2_hoangphan/s2_hoangphan.py -a` chạy sạch (13 scene, 10'18")
- [x] Mọi scene có phụ đề
- [x] Số liệu có `source("Bảng 1, tr.4")`
- [x] Chỉ dùng màu/helper trong `glance_style.py`
- [x] Kết đúng câu cầu nối
- [ ] PR từ nhánh `section/hoang-phan`
