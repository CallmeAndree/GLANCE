# Task 1 — Phân tích vấn đề cốt lõi của GNN–LLM fusion trên TAG

**Owner:** Trúc Mai · **File:** `s1_trucmai.py` · **Thời lượng mục tiêu:** ~2'00"
**Nguồn:** paper §1 Introduction (tr.1–2).

## Cần trình bày

1. **Bối cảnh**: text hiếm khi tồn tại độc lập — trích dẫn, đồng mua hàng, mạng xã hội đều
   tạo thành TAG. Trước đây TAG dùng feature nông (TF-IDF, word embedding tĩnh) đưa vào GNN;
   giờ người ta ghép LLM vào.

2. **Uniform fusion là vấn đề**: đa số hệ thống hybrid áp *một* chiến lược fusion cho *mọi*
   node, bỏ qua khác biệt per-node về chất lượng ngữ nghĩa và thuộc tính cấu trúc. Hệ quả:
   gọi LLM cho cả những node mà GNN vốn đã dự đoán tốt → chi phí lớn, tradeoff
   accuracy/efficiency kém.

3. **Vì sao uniform fusion sai** — hai mô hình mạnh ở hai vùng khác nhau:
   - GNN tốt khi **homophily cao** và **degree cao**; nhưng các tính chất này thường *không*
     đúng trên TAG thực tế. Các thiết kế GNN nâng cao vẫn chưa xử lý triệt để.
   - LLM tổng quát hoá tốt trong **low-shot**, hợp với node làm GNN suy giảm.
   - Nhưng ép LLM đọc đồ thị dạng text lại **làm méo quan hệ cấu trúc**; với đồ thị mà tín
     hiệu cấu trúc đơn giản, LLM có thể *tệ hơn* GNN.

4. **Aggregate metric che mất tất cả**: cải thiện tổng thể chỉ vài phần trăm, nên không ai
   thấy được *khi nào* LLM có ích → không có tín hiệu hành động để thiết kế chiến lược mới.
   Paper lập luận: lợi ích ở vùng GNN yếu bị bù trừ bởi tổn thất ở chỗ khác. Nhấn mạnh khía
   cạnh **equity across the graph** — chống lại inductive bias của GNN.

5. **Câu hỏi trung tâm** (trích nguyên văn, tr.2):
   > *How, and for which nodes, should we leverage LLMs to complement and bolster GNNs?*

6. **Ba đóng góp của paper** (tr.2) — nêu ngắn, vì section 2–5 sẽ khai triển:
   *(i)* chỉ ra heuristic routing hiện tại brittle; *(ii)* GLANCE — framework cost-aware học
   khi nào gọi LLM; *(iii)* phân tích thực nghiệm trên 4 dataset TAG, tới **+13.0%** trên
   node heterophilous và **+0.9%** overall.

## Lưu ý

- Đây là section "đặt vấn đề" — **chưa** được nói GLANCE giải bằng cách nào. Không spoil
  router, không spoil homophily là tín hiệu (đó là section 2 và 3).
- Nên dùng lại `demo_tag()` để minh hoạ việc gọi LLM cho mọi node.
- Con số ở mục 6 lấy đúng trong `docs/paper-map.md`, đừng làm tròn khác.

**Câu cầu nối cuối section:** *"Nếu phải chọn node để gọi LLM, người ta đã chọn bằng cách nào?"*

## Checklist nộp

- [ ] `manim -ql sections/s1_trucmai/s1_trucmai.py -a` chạy sạch
- [ ] Mọi scene có phụ đề
- [ ] Số liệu có `source(...)`
- [ ] Chỉ dùng màu/helper trong `glance_style.py`
- [ ] Kết đúng câu cầu nối
- [ ] PR từ nhánh `section/truc-mai`
