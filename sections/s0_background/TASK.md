# Section 0 — Background

Section này gồm hai phần, hai file riêng, hai người phụ trách.

| Phần | Nội dung | Owner | File |
|---|---|---|---|
| 0.1 | Related Work | **Hoàng Phan** | `s0a_related_work.py` |
| 0.2 | Preliminaries | **Trúc Mai** | `s0b_preliminaries.py` |

Thời lượng mục tiêu: mỗi phần ~1'30".

---

## 0.1 — Related Work (Hoàng Phan)

**Nguồn:** paper §2 (tr.2–3) và Phụ lục A (tr.14).

Cần trình bày:

- **Static GNN-LLM Fusion**
  - *LLM-as-Enhancer* — LLM sinh feature/embedding cho text node, GNN vẫn là bộ dự đoán.
  - *LLM-as-Predictor* — LLM thay GNN, nhận đồ thị đã serialize thành prompt và tự dự đoán nhãn.
  - Hạn chế của từng hướng (paper nói rõ ở Phụ lục A): Enhancer bị feature tĩnh và vẫn kế
    thừa inductive bias của GNN; Predictor mất topology, vướng giới hạn độ dài prompt và
    serialization mismatch. MoE và hướng "LLM chọn giữa các GNN" vẫn bị khoá trong bias của GNN.
- **Adaptive GNN-LLM Fusion** — ba phương pháp, mỗi phương pháp nêu *chọn node bằng gì* và
  *yếu ở đâu*:
  - *E-LLaGNN* — heuristic cố định (degree, centrality, độ dài text); phải chỉnh tay, hiệu quả
    thay đổi theo dataset.
  - *LOGIN* — dùng uncertainty của GNN để rewire node khó; việc rewire có thể xoá mất cạnh
    heterophilous vốn hữu ích.
  - *LLM-GNN* — dùng clustering density làm proxy độ khó (label-free).
- **Khoảng trống mà GLANCE lấp** — đúng ba điểm paper tự nêu (Phụ lục A, tr.14):
  1. Xác định *có hệ thống* thuộc tính cấu trúc nào dự báo được lợi ích của LLM, thay vì chọn
     đại một metric; học cách route mà không cần ngưỡng đặt trước.
  2. **Giữ nguyên cấu trúc đồ thị** thay vì sửa/rewire nó.
  3. **Huấn luyện thẳng router** dưới truy vấn không khả vi, thay vì sửa dữ liệu để tạo ảnh hưởng.

**Câu cầu nối cuối phần** (đọc đúng câu này): *"Trước khi xem GLANCE làm gì khác, thống nhất vài ký hiệu."*

---

## 0.2 — Preliminaries (Trúc Mai)

**Nguồn:** paper §3 (tr.3); định nghĩa $h_v$, $\bar d_v$ ở §4.2.1 (tr.4).

Cần trình bày:

- **Text-Attributed Graph (TAG)**: $\mathcal{G} = (\mathcal{V}, \mathcal{E}, T, Y)$ với
  $n = |\mathcal{V}|$ node, $T = \{t_v\}$ là text của mỗi node, $Y = \{y_v\}$ là nhãn.
  Ví dụ thực tế: mạng trích dẫn, đồ thị đồng mua hàng, mạng xã hội.
- **Node classification**: học $\psi : (\mathcal{G}, T) \rightarrow Y$ — dự đoán nhãn từ *cả*
  cấu trúc lẫn text.
- **GNN message passing**:
  $\mathbf{h}_v^{(\ell)} = \text{UPDATE}^{(\ell)}(\mathbf{h}_v^{(\ell-1)}, \text{AGGREGATE}^{(\ell)}(\{\mathbf{h}_u^{(\ell-1)} : u \in \mathcal{N}(v)\}))$,
  dự đoán $\hat y_v = \arg\max \text{MLP}(\mathbf{h}_v^{(L)})$, khởi tạo $\mathbf{h}_v^{(0)} = \mathbf{x}_v$ lấy từ $t_v$.
  Nêu điểm yếu đã biết: degree thấp, heterophily, oversmoothing.
- **LLM-as-Embedder vs LLM-as-Predictor**: embedder sinh $\mathbf{z}_v$ ghép được với GNN;
  predictor sinh thẳng nhãn nhưng dễ hallucinate và thường cần fine-tune.
  **Nói rõ GLANCE chọn embedder** — đây là chi tiết section 4 sẽ dùng lại.
- **Giới thiệu sớm hai đại lượng** (section 3 sẽ khai thác):
  - local homophily $h_v = \frac{1}{|\mathcal{N}(v)|}\sum_{u \in \mathcal{N}(v)} \mathbf{1}[y_u = y_v]$
  - relative degree $\bar d_v = \frac{1}{|\mathcal{N}(v)|}\sum_{u \in \mathcal{N}(v)} \sqrt{\frac{d_v+1}{d_u+1}}$,
    $\bar d_v > 1$ nghĩa là node có degree cao hơn hàng xóm.

Dùng `demo_tag()` để minh hoạ — đồ thị 12 node dùng chung cả video, node 4 là hub homophily
cao, node 9 là node homophily thấp. Section 1, 3, 4 sẽ dùng lại đúng đồ thị này.

**Câu cầu nối cuối phần:** *"Có đủ ký hiệu rồi, ta quay lại câu hỏi: fusion hiện tại sai ở đâu?"*

---

## Checklist nộp

- [ ] Các scene render sạch: `manim -ql sections/s0_background/<file>.py -a`
- [ ] Mọi scene đều có phụ đề (`add_subcaption` / tham số `subcaption`)
- [ ] Số liệu nào trích paper đều có `source("§X, tr.Y")`
- [ ] Chỉ dùng màu/helper trong `glance_style.py`
- [ ] Thời lượng nằm trong khoảng ±20% mục tiêu
- [ ] Kết đúng câu cầu nối ghi ở trên
- [ ] Push nhánh `section/<tên>` và mở PR vào `main`
