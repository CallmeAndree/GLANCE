# Task 4 — Mô tả kiến trúc GLANCE

**Owner:** Trần Nguyên · **File:** `s4_trannguyen.py` · **Thời lượng mục tiêu:** ~2'30"
**Nguồn:** paper §5.1 và Hình 2 (tr.5–6); chi tiết prompt ở Phụ lục B.3 (tr.15–16).

## Cần trình bày

**GLANCE** = **G**NN with **L**LM **A**ssistance for **N**eighbor- and **C**ontext-aware
**E**mbeddings. Ba thành phần: (i) GNN và LLM encoder **đóng băng**, (ii) **router** học được
dùng feature rẻ tiền, (iii) **refiner** hợp nhất embedding cấu trúc và text.

### Step 1 — Sinh và xử lý routing feature (§5.1.1)

Router nhận vector $\mathbf{f}_v$ gồm 5 tín hiệu **rẻ**:
- embedding GNN $\mathbf{z}_G(v)$ từ neighborhood $k$-hop (mang thông tin cấu trúc)
- **uncertainty** của node, ước lượng bằng dropout (proxy độ khó)
- **ước lượng homophily mềm** (phương trình 1):
  $\hat h_v = \mathbf{p}_{Q,v} \cdot \big(\frac{1}{|\mathcal{N}_1(v)|}\sum_{u \in \mathcal{N}_1(v)} \mathbf{p}_{Q,u}\big)$
- **feature gốc** của node và **degree** — để route được cả node có feature nhiễu hoặc thiếu
  ngữ cảnh hàng xóm

Paper lưu ý: uncertainty vốn nhằm bắt heterophily nhưng tương quan này **yếu** (Bảng 9), nên
dùng **cả hai** vì chúng rẻ mà vẫn nhiều thông tin.

**Router** $\pi$: $a_v = \pi(\mathbf{f}_v) = \sigma(\mathbf{w}^\top \mathbf{f}_v) \in [0,1]$.
Điểm thiết kế quan trọng: **không dùng ngưỡng tuyệt đối** mà dùng **top-$k$ theo mini-batch** —
mỗi batch chọn $k$ node có $a_v$ cao nhất. Nhờ vậy ngân sách truy vấn cố định và không phải
calibrate xác suất của router trên toàn đồ thị.

### Step 2 — Dùng LLM pre-trained xử lý neighborhood được route (§5.1.2)

Với node $v \in R$, sinh embedding **nhiều mức** thay vì một embedding duy nhất:
1. chỉ text ego $t_v$
2. ego + tập 1-hop được sample $\{t_v \cup t_u : u \in \mathcal{N}_1(v)\}$
3. ego + tập 2-hop được sample $\{t_v \cup t_u : u \in \mathcal{N}_2(v)\}$

Mỗi mức serialize thành prompt riêng, encode rồi **nối lại**:
$\mathbf{z}_L(v) = [\mathbf{z}_{L,0}(v) \,\|\, \mathbf{z}_{L,1}(v) \,\|\, \mathbf{z}_{L,2}(v)]$.

Vì sao thiết kế vậy: giữ được cả thông tin ego lẫn hàng xóm, prompt không bị dài quá, và khớp
với cách các GNN nâng cao tách riêng từng hop. Dùng embedding thay vì generation cũng **rẻ hơn**
các phương pháp trước.

Chi tiết nên nhắc (Phụ lục B.3): backbone **Qwen3-Embed-8B**; sample tối đa **5 hàng xóm mỗi
hop** (ego-only 1 node, ego+1-hop tối đa 6, ego+2-hop tối đa 26); prompt length 1024 cho
ego-node và 4096 cho ego+1/2-hop; chuẩn hoá $\ell_2$ trước khi nối.

### Step 3 — Refine dự đoán bằng embedding LLM (§5.1.3)

- Node **không** route: giữ nguyên dự đoán GNN qua MLP head $H$ có sẵn.
- Node **có** route: refiner MLP $C$ hợp nhất hai nguồn:
  $\mathbf{p}_{C,v} = \text{softmax}(C([\mathbf{z}_G(v) \,\|\, \mathbf{z}_L(v)]))$.
- Thiết kế **modular**: không phụ thuộc backbone GNN hay LLM cụ thể → đổi được theo dataset
  hoặc ngân sách tính toán.

## Lưu ý

- Nên bám sát Hình 2 (tr.6) — dựng lại sơ đồ 3 bước đó là xương sống của section này.
- Nói rõ **chỉ router $\pi$ và refiner $C$ được huấn luyện**; GNN và LLM đóng băng. Nhưng
  **không** đi vào hàm loss — đó là việc của section 5.
- `pipeline()` và `labeled_box()` trong `glance_style.py` dựng sẵn khối + mũi tên;
  `ego_ring()` để khoanh vùng ego/1-hop/2-hop trên `demo_tag()`.
- Giữ quy ước màu: GNN teal, LLM amber, router tím.

**Câu cầu nối cuối section:** *"Router không khả vi. Vậy huấn luyện nó kiểu gì — và có thật sự hiệu quả?"*

## Checklist nộp

- [ ] `manim -ql sections/s4_trannguyen/s4_trannguyen.py -a` chạy sạch
- [ ] Mọi scene có phụ đề
- [ ] Số liệu / chi tiết có `source("§5.1, tr.5–6")`
- [ ] Chỉ dùng màu/helper trong `glance_style.py`
- [ ] Kết đúng câu cầu nối
- [ ] PR từ nhánh `section/tran-nguyen`
