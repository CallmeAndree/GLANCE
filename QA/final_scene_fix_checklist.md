# Final scene-fix checklist (timeline x4)

Nguồn timestamp: video full x4 hiện tại. Sau mỗi lần sửa timing, dùng tên class scene làm mốc chính.

Quy ước:

- `[ ]` chưa sửa
- `[x]` đã sửa code
- `Render: [ ]` chưa render no-audio x4 scene nhỏ
- `QA: [ ]` chưa xem lại scene đã render
- Scene có nhiều lỗi: sửa hết các dòng trong cùng nhóm rồi mới render một lần.
- “Section title khoảng 2 phút” được hiểu là **2 giây** vì đây là page chrome ngắn trong video x4.

## Global style

- [x] Section title sau badge số dùng weight `HEAVY`, màu tương phản cao.
- [x] Section title chỉ hiện 2 giây ở scene mở section; scene sau giữ badge gọn.
- [x] Tăng stroke cho `avatar_node`/user và node graph dùng chung.
- [x] Thêm `node_focus_ring()` làm hiệu ứng focus tròn chuẩn cho node.
- [ ] Đổi các highlight node riêng trong từng scene từ box/`Indicate` sang ring tròn khi xử lý scene đó.
- [x] Chữ cỡ nhỏ tự dùng `SEMIBOLD`; chữ mono nhỏ cũng dày hơn.
- [x] Tăng contrast `INK`, `MUTED`; cạnh trung tính đổi sang blue-slate sáng hơn.
- [x] Tăng stroke cho panel, box, chip, document icon và connector dùng chung.
- [x] `doc_icon` dùng paper dọc, viền trắng dày, dòng bên trong màu lime.
- [x] Thêm connector chuẩn theo đúng trục tâm và cắt tại boundary của hai element.
- [ ] Rà connector tự dựng trong từng scene khi xử lý timestamp tương ứng.
- [ ] Rà tag riêng trong từng scene: có viền và nền không trong suốt.
- Render: không thực hiện theo yêu cầu.

## S1 — `Task1GLANCERebuilt`

> Đã thêm 10 `next_section()` boundary; aggregate được tách riêng thành hai clip. Output x4/no-audio: `build/qa_scenes/S1_x4_no_audio/`.

- [x] 0:04 — Arrow xuất phát giữa hai element, nằm ngang. Render: [x] QA: [x]
- [x] 0:06 — Thu nhỏ dòng “GLANCE for Context”; bỏ outline box, play outline chữ; đưa poster và title gần nhau. Render: [x] QA: [x]
- [x] 0:06 — Xóa frame mọi element hiện đồng thời. Render: [x] QA: [x]
- [x] 0:08 — Paper theo node-text style, rectangle dọc. Render: [x] QA: [x]
- [x] 0:10 — Chữ trong node màu trắng. Render: [x] QA: [x]
- [x] 0:11 — Script không nhắc node B nên đã đổi callout thành node A và đặt paper trên graph. Render: [x] QA: [x]
- [x] 0:15 — Đẩy cụm element lên và canh giữa. Render: [x] QA: [x]
- [x] 0:20 — Đưa GNN vào giữa hai embedding; arrow ở giữa. Render: [x] QA: [x]
- [x] 0:33 — Đẩy các element dưới lên vùng trống. Render: [x] QA: [x]
- [x] 0:45 — Xóa frame mọi element hiện đồng thời. Render: [x] QA: [x]
- [x] 0:53 — Paper xếp ngang; context size nằm trên dãy paper, không đè “serialised”. Render: [x] QA: [x]
- [x] 0:56 — Background hoàn toàn opaque. Render: [x] QA: [x]
- [x] 1:09 — Arrow bắt nguồn đúng tâm router. Render: [x] QA: [x]
- [x] 1:12 — Ô LLM bằng ô GNN prediction; arrow giữa hai ô chỉ xuống “keep GNN”. Render: [x] QA: [x]
- [x] 1:17 — Text xuống dòng, không tràn viền. Render: [x] QA: [x]
- [x] 1:20 — Text xuống dòng, không tràn viền. Render: [x] QA: [x]
- [x] 1:22 — Đưa hai dòng gần nhau; dùng element node thay cho chữ đơn thuần. Render: [x] QA: [x]
- [x] 1:29 — Tách “90 easy nodes… +13pts” và “GNN… +0.4pts” thành hai beat; chữ lớn, canh giữa. Render: [x] QA: [x]

### S1 — vòng QA ảnh bổ sung

- [x] Opening/title và frame 0:45 không còn mobject cũ lộ lại ở cuối beat. Render: [x] QA: [x]
- [x] Paper A nhỏ hơn, nằm trên graph; arrow neo giữa cạnh dưới của paper và dừng ở viền node A. Render: [x] QA: [x]
- [x] Arrow từ hai embedding xuất phát đúng trung điểm; bộ đếm “LLM queries” được kéo lên khỏi vùng che. Render: [x] QA: [x]
- [x] Router dùng port giữa cạnh: ba arrow vào giữa cạnh trái, hai arrow ra giữa cạnh phải; shaft không đè lên box. Render: [x] QA: [x]
- [x] Paper Node A/B/C là rectangle dọc, đã thu nhỏ; nội dung dài được tách dòng. Render: [x] QA: [x]
- [x] Grid 100 node được giữ lại; easy dots và hard dots đổi màu theo hai nhịp animation. Render: [x] QA: [x]
- [x] Card easy/hard có padding; hai card GNN/FUSION ở overall có cùng kích thước. Render: [x] QA: [x]
- [x] Full S1 x4, no-audio: `build/GLANCE_S1_x4_no_audio.mp4` (96.87 giây). Render: [x] QA: [x]

## S2

### `S2_02_TwoQuestions`

- [x] 1:54 — Xuống dòng giữa “GNN difficulty” và “LLM advantage”. Render: [x] QA: [x]

### `S2_03_Degree`

- [x] 2:05 — Không hiện “routed to the LLM” từ đầu; lần lượt tick + tag, degree, wasted LLM call.
- [x] 2:08 — Tag “wasted LLM call” có nền opaque, viền; node đồng bộ style có viền.
- [x] 2:12 — “highest degree → never routed” thành tag cạnh dấu X, đủ rõ.
- Render: [x] QA: [x]

### `S2_05_Uncertainty`

- [ ] 2:42 — Một ô trên; dưới là hai ô “degree”, “c-density”; copy xuống dòng “Doesn't imply / that LLM would do better”. Render: [ ] QA: [ ]

### `S2_08_Table1`

- [x] 3:48 — Chọn tối đa ba số liệu; đặt font lớn vào khoảng trống; chú thích ý nghĩa bên dưới; bỏ arrow chỉ số liệu. Render: [x] QA: [x]

### `S2_10_DegreeDensity`

- [ ] 4:21 — Áp dụng cùng rule tối đa ba số liệu + chú thích, không arrow. Render: [ ] QA: [ ]

### `S2_12_Limits`

- [x] 4:44 — Hạ “three limitations” xuống một chút. Render: [x] QA: [x]

## S3

### `S3_01_LocalHomophily`

- [x] 5:08 — Hạ “How much…” để không chạm section title (buff 0.75 → 1.05). Render: [x] QA: [x]

### `S3_02_RelativeDegree`

- [x] 5:23 — Hạ “Compared with…” để không chạm section title (buff 0.75 → 1.05). Render: [x] QA: [x]

### `S3_18_Degree`

- [x] 8:06 — Sửa text tràn: `equation_card()` trong `glance_style.py` chỉ `fit_width` cho công thức, không áp cho caption bên dưới, khiến “semantic feature + structural degree” tràn khỏi khung. Đã thêm `fit_width` cho caption (ảnh hưởng chung mọi nơi dùng `equation_card`, kể cả S4). Render: [x] QA: [x]

## S4

### `S4_02_EndToEnd`

- [x] 8:40 — `camera.frame.restore()` gọi ngoài `self.play()` nên nhảy khung hình tức thì ngay sau bước kéo camera ra (scale 1.08) — đúng là “hai chuyển động”, bước sau không animate. Đã animate cả bước restore (0.35s), tổng thời lượng trong khối voiceover giữ nguyên. Render: [x] QA: [x]
- [x] 8:50 — Line nối TAG vào ba module (GNN/MLP/GRAPH): lần kiểm đầu tưởng đã nối đúng (tag_trunk dọc trông như chạm module), nhưng thực ra 3 arrow (`tag_branches`) gần như biến mất — `branch_x` (offset cố định `input_right_x + 0.55`) tình cờ trùng gần sát mép trái module (cách nhau 0.012 đơn vị, nhỏ hơn nhiều `buff=0.08` của arrow) nên arrow co về độ dài âm/rỗng; chỉ có `tag_trunk` (line dọc, vẽ riêng) đè lên đúng chỗ tạo ảo giác đã nối. In toạ độ thực tế (`get_left()`, `get_center()`) ra để xác nhận thay vì đoán qua ảnh. Đổi `branch_x` sang trung điểm giữa TAG và mép module, đảm bảo khoảng cách luôn dương bất kể `step1_content` bị `fit_into` scale lại bao nhiêu. **Vòng 2:** đổi hẳn ba nhánh từ `small_arrow` sang `Line` trần (không mũi tên, không buff ở đầu) để dính liền vào trục dọc `tag_trunk`; `GrowArrow` → `Create`. “keep GNN” xuống sát line: label neo bằng offset cứng `CORRIDOR_Y + 0.30`, cách xa line thật; đổi sang `next_to(corridor_point, UP, buff=0.08)` — cùng buff “sát” dùng cho các arrow khác trong file. Render: [x] QA: [x]

### `S4_15_RouterScore`

- [x] 9:01 — `score_states` đổi từ 4 lần lặp cùng nót A (`a_A=...` x4) sang bốn nót khác nhau A/B/C/D; “routing score is not a class probability” tăng size 19→26, đổi từ neo mép phải sang `next_to(router_name, UP)` canh giữa phía trên router. Render: [x] QA: [x]

### `S4_16_TopK`

- [x] 9:07 — Root cause: `initial_rows.animate.move_to(LEFT*2.35)` canh giữa lại theo y=0, còn `top_line`/`top_label` chỉ `shift(LEFT*2.35)` (giữ nguyên y) — hai kiểu di chuyển khác nhau nên line trôi khỏi ranh giới top-3. Đổi `initial_rows` sang `shift` cho khớp. Render: [x] QA: [x]

### `S4_28_RefinerMLP`

- [x] 10:21 — Probability thêm bar "element" tỉ lệ theo value (cùng ngôn ngữ hình với `probability_bars` ở các scene khác) + khung `SurroundingRectangle` quanh hàng xác suất cao nhất (0.80, Graph Mining). **Vòng 2:** nhãn layer trước đây neo `next_to(layers[i], DOWN)` — tức theo đáy TỪNG cột nót, nên thụt vào giữa hình và đè lên network; đổi sang một hàng y cố định dưới đáy network, chỉ trượt theo trục x của layer đang sáng. softmax từ text trần (`mt`) thành module thật: hộp dọc hẹp `RoundedRectangle` + chữ `softmax` xoay 90°, ba nót logits nối vào hộp bằng `Line`, một mũi tên duy nhất ra cột xác suất. Render: [x] QA: [x]

### `S4_30_FinalPrediction`

- [x] 10:36 — Ring quanh router thu nhỏ (radius 0.70 → 0.58). Root cause của "arrow không từ tâm" + "lộ line": hai arrow WITH LLM/WITHOUT LLM dùng chung điểm cố định `router.get_right()` (hướng 3 giờ) cho cả nhánh chéo lên lẫn chéo xuống, khiến line cắt qua vòng tròn thay vì toả đúng hướng từ tâm. Đổi sang `boundary_arrow(router, header)` (tính theo trục tâm-tới-tâm, cắt đúng tại biên theo từng hướng) — sửa cả hai triệu chứng cùng lúc. Render: [x] QA: [x]

## S5

### `S5_04_Reward` (+ `S5_03_CounterfactualLoss`, `S5_05_JointObjective`)

- [x] 11:12 — “SAME TRUE LABEL y_A” thực ra nằm ở cuối `S5_03_CounterfactualLoss`, không phải `S5_04` — bỏ hẳn (lời đọc đã nói “cùng một nhãn thật” và cả hai công thức ℓ_GNN/ℓ_LLM đã có y_A). Render: [x] QA: [x]
- [x] 11:14 — Thu nhỏ hai ô loss `ℓ_v^GNN`/`ℓ_v^LLM` trong `S5_04` (pill width 2.5 → 2.15) cho cân đối với ô “gain 2.00” bên cạnh. Render: [x] QA: [x]
- [x] 11:19 — Bỏ “ILLUSTRATIVE VALUES”; EXAMPLE tách hai dòng (“gain 0.05 − β 0.10 = reward −0.05” / “→ remains negative even when routed”). “if skipped”: “bỏ” ở đây nghĩa là ĐẶT chứ không phải xoá — pill “IF SKIPPED” dời thành beat mở đầu riêng của `S5_05_JointObjective` (VO[“reward_skip”] đi theo), không còn chung frame với “IF ROUTED” của `S5_04` nữa. Render: [x] QA: [x]

### `S5_06_Setup`

> Mapping xác nhận bằng cách trích thẳng frame từ `build/GLANCE_full_S1-S5_x4_silent_QA_fixed.mp4`
> tại đúng giây x4 (11:50 → t=710s), không đoán qua thứ tự beat: 11:50 = beat GNN+LLM→ONE MODEL?,
> 11:53 = beat dataset, 11:56 = beat baseline.

- [x] Scene title “Experimental setup” — `shift(DOWN * 0.20)` cho thoáng với hàng banner.
- [x] 11:50 — Beat GNN+LLM→ONE MODEL?: bỏ hai toạ độ x tuyệt đối (`-2.25` / `3.10`) vốn làm cụm lệch trái so với tâm; đổi sang `arrange(RIGHT, buff=1.05)` rồi canh giữa cả cụm, hạ từ y=0.95 xuống y=0.10.
- [x] 11:53 — Cụm dataset đẩy lên (y −0.25 → 0.10).
- [x] 11:56 — Cụm baseline đẩy lên (y −0.45 → −0.10).
- [x] (thêm, theo yêu cầu) Beat budget: `dots`/`budget` cũng bỏ toạ độ x tuyệt đối, `arrange(RIGHT, buff=1.15)` để khép khoảng trống giữa lưới chấm và thẻ, đẩy lên (y −0.55 → −0.20).
- Render: [x] QA: [x]

### `S5_07_BalancedResults`

> Trích frame x4 để map: `S5_07` thực ra bắt đầu ~12:02, nên **11:59 vẫn là beat budget
> của `S5_06`** (đã canh giữa ở mục trên). 12:07 = beat bar-chart tổng, 12:09 = beat CORA hardest group.

- [x] 11:59 — Thuộc `S5_06_Setup` (beat budget), đã xử lý ở mục trên. Thêm ở đây: bar-chart tổng canh theo **dãy cột** thay vì cả group — nhãn trục y chiếm một khoảng bên trái nên canh group làm phần cột lệch phải.
- [x] 12:07 — Hạ graph (y 0.72 → 0.40); nâng pill "OVERALL MARGIN…" (y −2.28 → −1.95).
- [x] 12:09 — Font CORA: cả dòng bị bọc trong một `MathTex` nên phần chữ ra font serif LaTeX, lạc khỏi font chung. Tách ra — chữ dùng `txt()`, chỉ `(h_v<0.25)` giữ `MathTex`.
- [x] (phát hiện thêm) Tiêu đề "CORA · HARDEST GROUP" gần chạm nhãn "+13.0" của mũi tên chênh lệch — nới `buff` 0.45 → 0.72.
- Render: [x] QA: [x]

### `S5_08_RouterLearned`

- [x] 12:20 — Hạ dòng câu hỏi “Does the router learn the right nodes?” (`shift(DOWN*0.20)`).
- [x] 12:26 — Hai dòng thống kê K/h_v dùng `SMALL_SIZE−5`/`−4` màu `MUTED` nên gần như không đọc được ở bản x4; tăng lên `SMALL_SIZE−2`, đổi sang `INK` + `BOLD`, `MathTex` 25→29, thêm `fit_width(12.4)` chống tràn.
- [x] 12:29 — Trích frame x4 cho thấy mốc này rơi vào **beat ablation của `S5_08`** (không phải `S5_09`): hai biểu đồ REMOVE 1 FEATURE / REMOVE HOMOPHILY nằm thấp (y −0.85) sát banner cuối. Nâng lên y −0.50, `divider` chỉnh theo.
- Render: [x] QA: [x]

### `S5_09_RoutingControls`

- [x] Không cần sửa. Mốc 12:29 mà checklist gán cho scene này thực ra thuộc `S5_08` (xem trên); `S5_09` bắt đầu ~12:32 và hai card ROUTE ALL / RANDOM ROUTING đã canh giữa đúng. Đã thử hạ title nhưng làm card bị chật nên revert — không đổi gì.

### `S5_10_Scale`

> Cả hai mục 12:50 và 12:52 đều thuộc scene này — badge trên frame x4 tại t=772 là **10**, không phải 11.
> `S5_11_Callout` là scene “Takeaways: GLANCE in five points”, kiểm tra lại thấy không có lỗi.

- [x] 12:50 — Lưới chấm và card ROUTING RATE chỉ cách nhau ~0.1 đơn vị nên trông như dính; đẩy card sang phải (x −1.05 → −0.75).
- [x] 12:52 — Pill “GGCN · OOM” đặt `next_to(result, RIGHT)` nên mép phải rơi vào x≈7.25, vượt nửa bề rộng khung (7.11) và **bị cắt mất ngoài màn hình**; chuyển xuống dưới cụm hai ô dataset. Card ROUTING RATE hạ về y=0.05 để nằm đúng giữa hai ô kết quả, hai mũi tên toả đối xứng. Giữ lại grid vì sau khi dời pill đã đủ chỗ.
- Render: [x] QA: [x]

### `S5_11_Callout`

- [x] Không cần sửa — mục “12:52” trong checklist thực ra mô tả nội dung của `S5_10_Scale` (đã xử lý ở trên). Scene Takeaways kiểm tra frame thấy bố cục sạch.

## S1 — Revision 2026-08-13

- [x] Bỏ toàn bộ Paper A callout, arrow và nhịp chờ tương ứng.
- [x] Predicted label đặt sát dưới node A.
- [x] Ô GNN nâng lên; arrow nhắm tâm và dừng tại biên ô.
- [x] LLM queries nâng lên và thêm khung opaque có viền.
- [x] Node A/B/C thu nhỏ; hai nhánh Keep GNN / Query LLM cân giữa router.
- [x] Paper node canh giữa hai ô GNN / LLM.
- [x] Bỏ pipeline LLM-AS-ENHANCER khỏi frame trục; nâng và làm dày trục.
- [x] Xóa các FadeOut dư làm element cũ tái xuất hiện.
- [x] Dọn object ẩn trước khi fade lớp phủ opaque ở các chuyển cảnh TAG, context cost và aggregate.
- [x] Smoke render no-audio và kiểm tra frame trực quan.
- [x] Full render timing gốc, encode no-audio x4, kiểm tra stream/duration.
- [x] Trục latent xích trái, đặt cạnh graph; arrow đỏ trùng đúng trục.
- [x] Hai dòng số đỏ đặt ngay dưới graph.
- [x] Thu nhỏ Paper Node A/B/C để tạo gap với hai ô prediction.
- [x] Render lại full no-audio x4 sau revision mới.
