# Task 3 — Structural signal: local homophily và relative degree

**Owner:** Nhựt Anh · **File:** `s3_nhutanh.py` · **Thời lượng mục tiêu:** ~2'15"
**Nguồn:** paper §4.2, §4.2.1, §4.2.2, Hình 1 và Bảng 2 (tr.4–5); Hình 3 (tr.8).

## Cần trình bày

1. **Hai đại lượng** (section 0.2 đã giới thiệu, ở đây nhắc lại nhanh rồi khai thác):
   - $h_v = \frac{1}{|\mathcal{N}(v)|}\sum_{u \in \mathcal{N}(v)} \mathbf{1}[y_u = y_v]$ — local homophily
   - $\bar d_v = \frac{1}{|\mathcal{N}(v)|}\sum_{u \in \mathcal{N}(v)} \sqrt{\frac{d_v+1}{d_u+1}}$ — relative degree
   Cả hai đều đã biết là ảnh hưởng GNN, nhưng chưa ai xét chúng cho LLM-graph reasoning.

2. **Phân tích phân tầng (Hình 1, tr.4)** — phần quan trọng nhất của section:
   - Chia node theo bin $h_v$ và bin $\bar d_v$, so accuracy của GNN (std/enhanced) với LLM.
   - **LLM vượt trội rõ trên node heterophilous và node degree thấp**: tới **+20.4%** so với
     model tốt kế tiếp (GCNII + LLM-enhanced) trên Cora.
   - Homophily và degree còn tương tác với nhau: chênh lệch giữa các subpopulation phân tầng
     theo *cả hai* lên tới **30.1%** (Hình 5, §E.5).
   - Kết luận: GNN và LLM **bổ sung** nhau chứ không thay thế nhau.

3. **Homophily làm tín hiệu routing (Bảng 2, tr.5)**:
   - $h_v$ thật đạt NCS cao nhất ở hầu hết cấu hình (Cora GCN Enh.: **0.24 / 0.11 / 0.05**;
     Pubmed: **0.29 / 0.30 / 0.26**; Arxiv23: **0.15 / 0.14 / 0.15**) → đây là **cận trên**
     cho routing dựa trên cấu trúc.
   - Mean rank: $h_v$ **1.03** — nhưng cần label nên **không dùng được lúc inference**.

4. **Proxy không cần label (§4.2.2)** — mấu chốt kỹ thuật:
   - Huấn luyện một MLP $Q$ dự đoán nhãn, $\hat y_v = \arg\max Q(\mathbf{x}_v)$, rồi ước lượng
     $\hat h_v = \frac{1}{|\mathcal{N}(v)|}\sum_{u \in \mathcal{N}(v)} \mathbf{1}[\hat y_u = \hat y_v]$.
   - $\hat h_v$ **bám sát** $h_v$ và thường ngang hoặc vượt các heuristic tĩnh; mean rank
     **3.22** — tốt nhất trong nhóm label-free (uncertainty 3.28, C-density 4.14, degree 4.33,
     random 4.50, $\bar d_v$ 5.94).
   - Nêu luôn bản "mềm" mà GLANCE thực sự dùng (§5.1.1, phương trình 1):
     $\hat h_v = \mathbf{p}_{Q,v} \cdot \big(\frac{1}{|\mathcal{N}_1(v)|}\sum_{u \in \mathcal{N}_1(v)} \mathbf{p}_{Q,u}\big)$ —
     dùng phân phối xác suất thay vì nhãn cứng để tăng độ biểu đạt.

5. **Một ngưỡng homophily là không đủ (Hình 3, tr.8)**: trong các node được route, nhóm
   *được lợi* dồn về phía homophily thấp — đúng giả thuyết. Nhưng **median của nhóm được lợi
   khác nhau giữa các dataset** (Arxiv23 quanh $h \approx 0.5$), nên một ngưỡng cứng
   "chỉ route node heterophilous" là không tối ưu → cần thêm ngữ cảnh, tức là cần một
   **router học được**. Đây chính là lý do tồn tại của section 4.

## Lưu ý

- Đây là section "phát hiện" — bản lề giữa phần phủ định (section 2) và phần giải pháp
  (section 4). Kết phải dẫn được tới nhu cầu có router học được.
- Dùng `demo_tag()`: node 4 (homophily cao) vs node 9 (homophily thấp) để minh hoạ trực quan.
- $\bar d_v$ có mean rank **5.94** — kém nhất. Nói thẳng điều này: relative degree *giải thích*
  được GNN yếu ở đâu, nhưng **không** phải tín hiệu routing tốt. Đừng gộp chung với homophily.

**Câu cầu nối cuối section:** *"Đã có tín hiệu. Giờ ráp nó vào một kiến trúc chạy được."*

## Checklist nộp

- [ ] `manim -ql sections/s3_nhutanh/s3_nhutanh.py -a` chạy sạch
- [ ] Mọi scene có phụ đề
- [ ] Số liệu có `source("Bảng 2, tr.5")` / `source("Hình 1, tr.4")`
- [ ] Chỉ dùng màu/helper trong `glance_style.py`
- [ ] Kết đúng câu cầu nối
- [ ] PR từ nhánh `section/nhut-anh`
