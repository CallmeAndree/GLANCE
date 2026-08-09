# GLANCE — Kịch bản tổng

## Overview
- **Topic**: GLANCE — GNN with LLM Assistance for Neighbor- and Context-aware Embeddings.
  Học *khi nào* nên gọi LLM để hỗ trợ GNN trên text-attributed graph.
- **Hook**: "Gọi LLM cho **mọi** node là lãng phí. Vậy gọi cho node nào?"
- **Target Audience**: Sinh viên đã học GNN cơ bản (message passing, node classification),
  biết LLM ở mức khái niệm. Không yêu cầu biết RL.
- **Estimated Length**: **~29'51" đo thực tế** ở 480p15 (5 section đang có trong
  `build.sh`, xem bảng dưới). Section 2 và 3 dài hơn hẳn các section khác theo thống
  nhất của nhóm, xem ghi chú dưới bảng.
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

Cột "Giao ban đầu" là thời lượng chốt lúc chia việc; cột "Đo thực tế" là số đo từ
`media/videos/<section>/480p15/` của lần build gần nhất (2026-08-07, 480p15).

| # | Section | Owner | Giao ban đầu | Đo thực tế | Mục paper |
|---|---|---|---|---|---|
| 0.1 | Related Work | Hoàng Phan | ~1'30" | chưa dựng | §2, Appendix A (tr.2, 14) |
| 0.2 | Preliminaries | Trúc Mai | ~1'30" | chưa dựng | §3 (tr.3), §4.2.1 (tr.4) |
| 1 | Vấn đề cốt lõi của GNN–LLM fusion | Trúc Mai | ~2'00" | 3'01" | §1 (tr.1–2) |
| 2 | Đánh giá routing heuristic hiện có | Hoàng Phan | ~2'00" | 7'34" | §4.1, Bảng 1 (tr.3–4) |
| 3 | Structural signal + năm routing signal | Nhựt Anh | ~2'15" | **8'07"** | §4.2 & §5.1.1, Hình 1–2, Bảng 2 (tr.4–6) |
| 4 | Kiến trúc GLANCE (từ $\mathbf{f}_v$ trở đi) | Trần Nguyên | ~2'30" | **5'52"** | §5.1, Hình 2 (tr.5–6) |
| 5 | Training objective & thực nghiệm | Thiên Lâm | ~2'45" | 5'14" | §5.2, §6, Bảng 3–5 (tr.7–9) |

Tổng đo thực tế **29'51"** (`build/final.mp4` 29'47" sau khi ghép). Section 0.1 và 0.2
chưa nằm trong mảng `SECTIONS` của `build.sh` nên không có trong bản ghép. Mỗi section
**tự chứa**: mở bằng title card, kết bằng một câu "cầu nối" sang section sau (xem phần
Transitions).

> **Ghi chú về section 2.** Ban đầu section này được giao ~2'00". Nhóm đã thống nhất giữ
> bản dài vì phần phủ định cần đi qua đủ ba heuristic, cách đo NCS, rồi mới tới Bảng 1.
> Nếu sau này thấy mất cân đối thì chỗ cắt được nhiều nhất là `S2_06_Setup` (đang nhắc
> lại tiêu chí chọn node đã nói ở `S2_03`–`S2_05`) và đoạn cảnh báo rewiring cuối `S2_05`.

> **Ghi chú về điểm cắt section 3 / section 4 (chốt 2026-08-07).** Section 3 giờ dựng
> đủ **năm routing signal** và kết thúc tại $\mathbf{f}_v$; section 4 **nhận** $\mathbf{f}_v$
> rồi mới bắt đầu ($\mathbf{f}_v \rightarrow a_v \rightarrow$ top-k $\rightarrow$ LLM
> $\rightarrow$ refiner). 12 cảnh `S4_03`–`S4_14` đã chuyển nguyên sang section 3 thành
> `S3_07`–`S3_19`, và sáu cảnh trùng nội dung của section 3 cũ (`S3_07_NodeEmbedding`–
> `S3_12_Combine`) đã bỏ. Vì vậy section 3 dài hơn hẳn mức giao ban đầu còn section 4
> ngắn lại. Chi tiết trong `sections/s3_nhutanh/TASK.md` và `sections/s4_trannguyen/TASK.md`.

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
- Scene chỉ giải thích khái niệm, công thức hoặc kiến trúc **không hiển thị trích dẫn
  nguồn / `source(...)`**. Giữ provenance trong code và `docs/paper-map.md`.
- Riêng số liệu thực nghiệm lấy từ paper vẫn kèm stamp `source("Table X, p.Y")` ở
  góc dưới phải theo quy tắc kiểm chứng số liệu của repo.

## Color Palette — "Deep Graph"

Phong cách **navy đen — công nghệ / học thuật / hiện đại**, áp xuyên suốt video
GLANCE. Định nghĩa MỘT nơi trong `glance_style.py`; mọi section
`from glance_style import *` **không** tự ghi đè màu cục bộ (S4 từng làm, đã bỏ).

| Vai trò | Hằng số | Hex | Cách dùng |
|---|---|---|---|
| Nền chính | `BG` | `#08111F` (navy đen) | Background toàn video |
| Nền khối / thẻ | `C_PANEL` | `#111E32` (slate navy) | Card, bảng, khung công thức |
| GNN / cấu trúc graph | `C_GNN` | `#3B82F6` (electric blue) | Node GNN, cạnh, message passing |
| LLM / semantic content | `C_LLM` | `#F59E0B` (amber orange) | LLM, text embedding, node được route |
| Router / GLANCE | `C_ROUTER` | `#8B5CF6` (violet) | Routing score, learnable router, fusion |
| Structural signal | `C_SIGNAL` = `C_HIGHLIGHT` | `#22D3EE` (cyan) | Homophily, degree, uncertainty, signals |
| Thành công / dự đoán đúng | `C_GOOD` | `#34D399` (mint green) | Dấu ✓, improvement, vùng hoạt động tốt |
| Cảnh báo / khó / sai | `C_BAD` | `#FB7185` (coral red) | Heterophily, uncertainty cao, dấu ✗ |
| Chữ chính | `INK` | `#F1F5F9` (off-white) | Tiêu đề và nội dung quan trọng |
| Chữ phụ | `MUTED` | `#94A3B8` (blue gray) | Chú thích, citation, secondary text |
| Cạnh đồ thị trung tính | `C_EDGE` | `#334A63` | Đường graph không mang nghĩa GNN |

### Quy ước xuyên suốt video
- **GNN** `C_GNN` · **LLM** `C_LLM` · **Router/GLANCE** `C_ROUTER` ·
  **structural signals** `C_SIGNAL` · **node khó / heterophily / lỗi** `C_BAD` ·
  **kết quả tốt / improvement** `C_GOOD`.
- **Luồng màu**: `C_GNN` (GNN) → `C_SIGNAL` (Signals) → `C_ROUTER` (Router) → `C_LLM` (LLM).

### Tỷ lệ 70 / 20 / 10
- 70% nền navy và các sắc độ tối; 20% chữ trắng/xám và đường graph trung tính;
  10% màu nhấn (xanh / cam / tím / cyan).
- **Không bật hết màu nhấn cùng lúc.** Mỗi scene chỉ **một màu chủ đạo**, tối đa **hai
  màu hỗ trợ**.

### Gradient nhận diện GLANCE
`#3B82F6 → #8B5CF6 → #F59E0B` (GNN → Router → LLM). Dùng cho: logo / tiêu đề GLANCE,
đường routing, thanh routing score, transition GNN↔LLM, intro và outro.

### Áp dụng theo scene
- **TAG**: node xanh nhạt, cạnh `C_GNN`, phần văn bản `C_LLM`.
- **Homophily cao**: `C_GNN` + `C_GOOD`. **Heterophily thấp**: `C_GNN` đối lập `C_BAD`.
- **Uncertainty**: `C_SIGNAL` chuyển dần sang `C_BAD`.
- **Năm routing signals**: `C_SIGNAL`; signal đang giải thích viền `C_ROUTER`.
- **Top-K routing**: node được chọn chuyển xanh → cam qua hiệu ứng tím.
- **Số liệu tích cực (20.4%, 30.1%)**: `C_GOOD`.

## Quy tắc thuyết minh

**Chữ trên hình: tiếng Anh. Kịch bản và giọng đọc: tiếng Việt.** Nhóm đã thống nhất như vậy.
Mọi `txt()`, `heading()`, nhãn biểu đồ, nhãn node và stamp `source()` đều viết tiếng Anh.

- Mỗi câu phụ đề ≤ 2 dòng, ≤ ~14 từ. Nói chậm, một ý một nhịp.
- Số thập phân trong lời đọc dùng **"chấm"**, không dùng "phẩy": `0.08` →
  "không chấm không tám". Số trên hình vẫn giữ dấu chấm theo ký hiệu gốc.
- Chữ cái trong ký hiệu toán phải ghi đúng âm đọc tiếng Việt trong lời thoại:
  `A` → "a", `B` → "bê", `C` → "xê", `D` → "đê", `E` → "e",
  `F` → "ép", `G` → "gờ", `H` → "hắc", `I` → "i", `J` → "di",
  `K` → "ca", `L` → "lờ", `M` → "mờ", `N` → "nờ", `O` → "o",
  `P` → "bê", `Q` → "qui", `R` → "rời", `S` → "ết", `T` → "tê",
  `U` → "u", `V` → "vê", `W` → "vê kép", `X` → "ích", `Y` → "y",
  `Z` → "dét". Dấu phẩy trong chỉ số đọc là "phẩy": `p_{H,A}` →
  "bê hắc phẩy a"; bỏ dấu ngoặc khi đọc đối số: `z_G(v)` → "dét gờ vê".
- Lời trong `VO` chính là kịch bản đọc, nên viết sao cho đọc lên nghe tự nhiên.
  Độ dài nhịp hình bám theo audio thật (`tracker.duration`), không ước bằng tay nữa.
- **Chỉnh nhịp bằng lời, không bóp méo audio.** Khi sửa scene, được phép **THÊM**
  câu thoại để lấp khoảng chết (animation dài hơn giọng đọc) hoặc **BỚT** câu thừa
  cho đỡ lê thê, để giọng đọc và hình trôi chảy liền mạch. **Tuyệt đối không** kéo
  giãn, nén, đổi cao độ hay chèn im lặng vào audio đã sinh. Hãy viết lại kịch bản,
  sinh TTS mới ở tốc độ chuẩn, rồi để audio mới quyết định nhịp animation.
- **Một ý liền mạch dùng một clip TTS.** Không tách một câu giải thích thành nhiều
  `voiceover` chỉ để chia animation, vì TTS có thể đổi nhịp, âm lượng hoặc cao độ
  ở điểm nối. Muốn hình xuất hiện tuần tự thì chạy nhiều animation trong cùng một
  khối `voiceover`; chỉ tách audio khi kịch bản thực sự chuyển ý.
- **Khi agent cần hỏi**: luôn hiện câu hỏi dạng **hộp chọn** (AskUserQuestion) bằng
  tiếng Việt, mỗi phương án một lựa chọn rõ ràng, để người dùng bấm chọn thay vì gõ.
- Chữ trên hình giữ nguyên thuật ngữ tiếng Anh; lời trong `VO` phải viết theo cách
  model TTS đọc tiếng Việt. **Với thuật ngữ, giữ nguyên từ tiếng Anh và ghi phiên
  âm theo cách đọc**, ví dụ `video` → "vi đi ô". Chỉ dịch sang tiếng Việt khi từ
  đó đã có cách nói tự nhiên quen thuộc. `routing` có thể giữ nguyên tiếng Anh
  khi TTS đọc rõ; dùng "định tuyến" khi câu tiếng Việt tự nhiên hơn.
  `embedding` → "véc-tơ biểu diễn". Dùng phiên âm đã chốt: `node` → "nót".
  Phiên âm acronym thống nhất:
  `LLM` → "lờ lờ mờ", `MLP Q` → "mờ lờ bê kiu", `MLP` → "mờ lờ bê", `GNN` → "gờ nờ nờ",
  `GLANCE` → "gờ lans", `GLANCE for Context` → "gờ lans for context",
  `GCN` → "gờ xê en", `NCS` → "en xi ét",
  `TAG` → "ti ây gi". Tên baseline đọc là `E-LLaGNN` → "e lờ lờ a gờ nờ nờ",
  `LLM-GNN` → "lờ lờ mờ, gờ nờ nờ", `LOGIN` → "lốc gin". Tên bộ dữ liệu đọc là `Cora` → "cô ra", `Pubmed` →
  "pắp mét", `Arxiv23` → "ác xíp hai ba". Các từ kỹ thuật còn lại phải dịch
  tự nhiên trong lời đọc: `graph` → "đồ thị", `feature` → "đặc trưng",
  `loss` → "hàm mất mát", `reward` → "phần thưởng", `Refiner` →
  "bộ tinh chỉnh", `prompt` → "câu lệnh", `Top-K` → "tốp ca".
- Lần đầu xuất hiện thuật ngữ: hiện chữ tiếng Anh + một dòng giải thích ngắn bằng tiếng Anh.
- Không dùng ký tự gạch dài `—` / `–` trên hình. Dùng `:` `,` hoặc `·`.
