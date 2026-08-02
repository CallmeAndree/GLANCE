# Task 5 — Training objective và kết quả thực nghiệm của GLANCE

**Owner:** Thiên Lâm · **File:** `s5_thienlam.py` · **Thời lượng mục tiêu:** ~2'45"
**Nguồn:** paper §5.2 (tr.6–7), §6 (tr.7–9), Phụ lục C.4 (tr.17).

## Phần A — Training objective (§5.2)

1. **Vì sao không backprop thẳng được**: quyết định route là **rời rạc** và còn phải dựng
   prompt, nên gradient không chảy qua được. ⇒ coi routing như bài toán **contextual bandit**,
   huấn luyện bằng loss kiểu **policy gradient**.

2. **So sánh phản thực (counterfactual) và reward**: với node được route, tính luôn dự đoán
   "giá như dùng GNN" qua head $H$ có sẵn: $\mathbf{p}_{H,v} = \text{softmax}(H(\mathbf{z}_G(v)))$,
   rồi so hai loss $\ell_v^{(GNN)}$ và $\ell_v^{(LLM)}$:
   $$r_v = \begin{cases} \ell_v^{(GNN)} - \ell_v^{(LLM)} - \beta & \text{nếu } a_v \in \text{top-}k \\ -\ell_v^{(GNN)} & \text{nếu không route} \end{cases}$$
   - Số hạng đầu = mức giảm loss nhờ gọi LLM; $\beta \ge 0$ là **giá của một lần gọi LLM**.
   - $\beta$ lớn ⇒ phạt nặng hơn, router dè dặt hơn. $r_v > 0$ nghĩa là lần gọi đó đáng tiền.
   - Lưu ý: counterfactual **chỉ** tính cho node được route.

3. **Hàm mục tiêu**:
   - Router: $\ell_v^{(route)} = -r_v \log \pi(\mathbf{f}_v) - \lambda_{\mathcal{H}} \mathcal{H}_{ent}[\pi(\mathbf{f}_v)]$
     (lấy cảm hứng REINFORCE, nhưng **chọn top-$k$ tất định** khi train để ngân sách truy vấn ổn định).
   - Dự đoán: $\ell_v^{(pred)} = \mathbf{1}[a_v \in \text{top-}k]\,\ell_v^{(LLM)} + (1 - \mathbf{1}[a_v \in \text{top-}k])\,\ell_v^{(GNN)}$
   - Tổng: $\mathcal{L} = \frac{1}{|\mathcal{B}|}\sum_{v \in \mathcal{B}} \ell_v^{(pred)} + \lambda_{router}\,\ell_v^{(route)}$
   - Số hạng đầu lo **độ chính xác**, số hạng sau lo **routing có ý thức chi phí**.
   - **GNN $F$ và LLM $L$ đóng băng — chỉ train $C$ và $\pi$.**

4. **Siêu tham số đáng nhắc** (Phụ lục C.4): batch 32, route top-12/batch cho số liệu báo cáo;
   lịch giảm ngân sách $K_t = \text{round}(K_{end} + (K_{start}-K_{end})r^{t-1})$ với
   $K_{end} = K_{start}/4$, $r = 0.5$; $\beta \in \{0.1, 0.2, 0.3\}$, $\lambda_{router} = 1.0$,
   $\lambda_{ent} = 0.01$.

## Phần B — Kết quả thực nghiệm (§6)

5. **Setup**: Cora, Pubmed, Arxiv23 (chính) + Arxiv-Year, OGB-Products (quy mô lớn).
   Baseline: GCN, GraphSAGE, GCNII trên 3 chế độ (feature gốc / LLM-enhanced / LOGIN-filtered),
   cộng nhóm GNN chuyên heterophily FAGCN, GGCN, GBK-GNN. Cùng split, cùng protocol, cùng text encoder.

6. **Kết quả chính**:
   - Overall (Bảng 4, tr.8): **89.5 ± 0.4** Cora, **92.6 ± 0.1** Pubmed, **82.1 ± 0.1** Arxiv23 —
     trung bình **+0.5%** so với model tốt kế tiếp, mà **dùng ít lần gọi LLM hơn hẳn**.
   - Phân tầng (Bảng 3, tr.8): GLANCE có **average rank 2.4** so với **4.7** của model kế tiếp
     → **cân bằng nhất trên toàn phổ homophily**. Gain lớn nhất ở node heterophilous:
     **+13%** trên Cora, **+0.5%** trên Pubmed.

7. **Router học được gì (§6.3, Hình 3)**: node được route dồn về phía homophily thấp, và nhóm
   *được lợi* còn lệch thấp hơn nữa → xác nhận giả thuyết heterophily là chỗ GNN hỏng và LLM
   có giá trị. (Nhựt Anh cũng dùng hình này ở section 3 — thống nhất với bạn để không trùng lặp,
   ở đây chỉ nhắc như bằng chứng router hoạt động đúng thiết kế.)

8. **Độ nhạy theo ngân sách $K$** (batch 32, $K \in \{8,12,16\}$): tăng $K$ cải thiện đều ở node
   heterophilous — $h_v < 0.25$ tăng **+3.4%** khi $K$: 8→12 và thêm **+3.0%** khi 12→16 (Pubmed,
   Arxiv23); Cora tụt nhẹ ở 8→12 rồi **+12.3%** ở $K = 16$. Vùng $h_v > 0.75$ gần như không đổi
   (**−0.06%**) → tăng ngân sách không làm hỏng node dễ.

9. **Ablation feature routing (§6.3)**: bỏ từng feature đều giảm (trung bình −0.38% Cora,
   −1.07% Pubmed, −0.65% Arxiv23), nhưng **bỏ feature homophily là tệ nhất**: **−6.5%** Cora,
   **−6.3%** Pubmed, **−2.0%** Arxiv23 ở vùng $h_v < 0.5$ → homophily đúng là tín hiệu chủ lực.

10. **Quy mô lớn (§6.4, Bảng 5)**: Arxiv-Year và OGB-Products lớn hơn nhiều lần dataset thường
    dùng. Với query rate chỉ **~6.25%** ($K = 2$, batch 32), GLANCE vẫn thắng: overall
    **49.8 ± 0.1** và **82.3 ± 0.1**. GGCN thì OOM trên OGB-Products.

11. **Kết luận video** (§7): homophily là tín hiệu tin cậy để biết GNN hỏng ở đâu và LLM giỏi
    ở đâu; GLANCE biến nó thành một chiến lược fusion cost-aware, học *khi nào* gọi LLM.
    Đây là scene cuối của cả video — đóng lại vòng cung mở ra từ section 1.

## Lưu ý

- Section này dài nhất, nên tách rõ hai nửa: **objective** rồi **kết quả**.
- Mọi con số lấy từ `docs/paper-map.md`, đừng gõ lại từ trí nhớ. Luôn kèm `source(...)`.
- `bar_chart()` có sẵn cho Bảng 3/4/5; giá trị âm cũng vẽ được.
- Scene cuối nên nhắc lại câu hỏi trung tâm mà Trúc Mai nêu ở section 1 để khép mạch phim.

## Checklist nộp

- [ ] `manim -ql sections/s5_thienlam/s5_thienlam.py -a` chạy sạch
- [ ] Mọi scene có phụ đề
- [ ] Mọi số liệu có `source("Bảng X, tr.Y")`
- [ ] Chỉ dùng màu/helper trong `glance_style.py`
- [ ] Scene cuối khép lại câu hỏi của section 1
- [ ] PR từ nhánh `section/thien-lam`
