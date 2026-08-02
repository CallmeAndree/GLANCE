# Bản đồ paper → section

Paper: *GLANCE for Context: Learning When to Leverage LLMs for Node-Aware GNN–LLM
Fusion* — Donald Loveland, Yao-An Yang, Danai Koutra (University of Michigan),
arXiv:2510.10849v1, 12 Oct 2025. PDF: `../GraphDataMining.pdf`.

| Mục paper | Trang | Section video | Owner |
|---|---|---|---|
| Abstract | 1 | (trích cho title card) | — |
| §1 Introduction | 1–2 | **1** | Trúc Mai |
| §2 Related Work | 2–3 | **0.1** | Hoàng Phan |
| §3 Preliminaries | 3 | **0.2** | Trúc Mai |
| §4 Which nodes to route (mở đầu) | 3 | **2** | Hoàng Phan |
| §4.1 Limitations of current routing strategies + Bảng 1 | 3–4 | **2** | Hoàng Phan |
| §4.2 / §4.2.1 Complementary capabilities + Hình 1 | 4 | **3** | Nhựt Anh |
| §4.2.2 Routing with local homophily + Bảng 2 | 5 | **3** | Nhựt Anh |
| §5.1 Components of GLANCE + Hình 2 | 5–6 | **4** | Trần Nguyên |
| §5.2 Training objectives | 6–7 | **5** | Thiên Lâm |
| §6.1 Experimental setup | 7 | **5** | Thiên Lâm |
| §6.2 Kết quả chính + Bảng 3, 4 | 7–8 | **5** | Thiên Lâm |
| §6.3 Router: learned properties + Hình 3 | 8 | **3** (Hình 3) + **5** (ablation) | Nhựt Anh / Thiên Lâm |
| §6.4 Large-scale + Bảng 5 | 9 | **5** | Thiên Lâm |
| §7 Conclusion | 9 | **5** (đóng video) | Thiên Lâm |
| Appendix A Detailed related work | 14 | **0.1** | Hoàng Phan |
| Appendix B Prompting | 14–16 | **4** (Step 2) | Trần Nguyên |
| Appendix C Training & hyperparameters | 16–17 | **5** | Thiên Lâm |

## Số liệu chính (dùng đúng, đừng làm tròn khác)

**Kết quả tổng (Bảng 4, tr.8)** — accuracy trung bình 3 lần chạy:
GLANCE đạt **89.5 ± 0.4** (Cora), **92.6 ± 0.1** (Pubmed), **82.1 ± 0.1** (Arxiv23);
trung bình **+0.5%** so với model tốt kế tiếp.

**Cân bằng theo homophily (Bảng 3, tr.8)**: GLANCE có **average rank 2.4**, model tốt
kế tiếp là **4.7**. Trên bin homophily thấp nhất (0.00–0.25): Cora **46.4 ± 2.4**,
Arxiv23 **45.2 ± 0.7**; Pubmed bin 0.25–0.50 đạt **71.5 ± 0.5**.

**Gain chính (Abstract, §6.2)**: tới **+13.0%** trên node heterophilous (Cora),
**+0.5%** trên Pubmed; gain tổng thể tới **+0.9%**.

**NCS heuristic (Bảng 1, tr.4)**: uncertainty đạt 0.20 / 0.18 / 0.15 (Pubmed, GCN Enh.,
k = 10/15/20%) nhưng **−0.09 / −0.03 / −0.01** trên Cora. Degree và C-density dao động
quanh 0. ⇒ không heuristic nào robust xuyên dataset.

**NCS homophily (Bảng 2, tr.5)**: $h_v$ (true) đạt NCS cao nhất — Cora GCN Enh.
0.24 / 0.11 / 0.05; Pubmed 0.29 / 0.30 / 0.26; Arxiv23 0.15 / 0.14 / 0.15.
Mean rank: $h_v$ **1.03** (cần label), $\hat h_v$ **3.22** (tốt nhất trong nhóm
label-free), uncertainty 3.28, C-density 4.14, degree 4.33, random 4.50, $\bar d_v$ 5.94.

**Stratified (Hình 1, tr.4)**: LLM vượt model tốt kế tiếp (GCNII + LLM enhanced) tới
**+20.4%** trên Cora ở nhóm homophily thấp; chênh lệch giữa subpopulation phân tầng
theo cả degree và homophily lên tới **30.1%** (Hình 5, §E.5).

**Scale (Bảng 5, tr.9)**: Arxiv-Year overall **49.8 ± 0.1**, OGB-Products **82.3 ± 0.1**,
với query rate chỉ **~6.25%** (K = 2, batch 32).

**Sensitivity K (§6.3, tr.8)**: K = 8→12 cho +3.4% ở $h_v$ < 0.25 (Pubmed, Arxiv23),
K = 12→16 cho thêm +3.0%; Cora tụt nhẹ ở K = 8→12 rồi **+12.3%** ở K = 16.
Vùng $h_v$ > 0.75 gần như không đổi (**−0.06%** trung bình).

**Ablation (§6.3, tr.9)**: bỏ feature homophily → giảm **−6.5%** (Cora), **−6.3%**
(Pubmed), **−2.0%** (Arxiv23) ở vùng $h_v$ < 0.5. Trung bình mọi feature:
−0.38% Cora, −1.07% Pubmed, −0.65% Arxiv23.

**Siêu tham số (Appendix C.4, tr.17)**: freeze GNN + LLM, chỉ train router $\pi$ và
refiner $C$. Batch 32, route top-12/batch (mặc định báo cáo). Lịch giảm budget
$K_t = \text{round}(K_{end} + (K_{start} - K_{end}) r^{t-1})$ với $K_{end} = K_{start}/4$,
$r = 0.5$. $\beta \in \{0.1, 0.2, 0.3\}$, $\lambda_{router} = 1.0$, $\lambda_{ent} = 0.01$.
LLM backbone: **Qwen3-Embed-8B**.

**Dataset**: Cora, Pubmed, Arxiv23 (chính); Arxiv-Year, OGB-Products (scale).
Backbone GNN: GCN, GraphSAGE, GCNII; baseline heterophily: FAGCN, GGCN, GBK-GNN.
Split 50/25/25.
