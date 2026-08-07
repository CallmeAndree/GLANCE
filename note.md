
## Cần sửa — scene S5_02_TopKProblem

- Scene: [`S5_02_TopKProblem()`](sections/s5_thienlam/s5_thienlam.py:255).
- Dấu tick vàng phía trên các node, thuộc [`tickets`](sections/s5_thienlam/s5_thienlam.py:274), đang chồng lên pill `FIXED BUDGET · K = 2`.
- Hạ cả cụm tick xuống khoảng `0.15` đơn vị; chỉnh ngay sau khi tạo cụm bằng `tickets.shift(DOWN * 0.15)`, hoặc giảm `buff` trong [`next_to()`](sections/s5_thienlam/s5_thienlam.py:274). Giữ nguyên vị trí `budget` và `nodes`.
- Dòng `rank swap → decision jumps` bị dính chữ, nằm ở [`jump_label`](sections/s5_thienlam/s5_thienlam.py:298).
- Không dựng cả câu bằng một lần gọi `txt()`. Tách thành ba mobject `rank swap`, `→`, `decision jumps`, rồi ghép bằng `VGroup(...).arrange(RIGHT, buff=0.12)` để tạo khoảng cách ổn định giữa các cụm từ; sau đó đặt cả group bằng [`next_to()`](sections/s5_thienlam/s5_thienlam.py:299). Giữ nguyên cỡ chữ và màu `C_BAD`.

## Cần sửa — lời thoại chuyển sang bài toán node classification

- Vị trí: khối [`narrated_caption()`](sections/s1_trucmai/s1_trucmai.py:782) trong [`section_2_tag()`](sections/s1_trucmai/s1_trucmai.py:678).
- Đổi lời thoại `Từ hai nguồn thông tin này, bài toán tiếp theo là dự đoán nhãn của những nót chưa biết lớp.` thành: `Bài toán đặt ra là làm thế nào để dự đoán nhãn của những nót chưa biết lớp?`
- Chỉ thay nội dung lời thoại; giữ nguyên animation và timing của `formula`, `pred` cùng các hiệu ứng khác.

## Cần sửa — hiệu ứng Paper B trong section 1

- Scene/đoạn đúng: phần dựng đồ thị trong [`section_2_tag()`](sections/s1_trucmai/s1_trucmai.py:678), cụ thể hiệu ứng hiện [`callout`](sections/s1_trucmai/s1_trucmai.py:727) cùng mũi tên [`link`](sections/s1_trucmai/s1_trucmai.py:728) và viền sáng của `node_B`.
- Cho hiệu ứng Paper B tồn tại lâu hơn để người xem kịp đọc: tăng thời gian chờ sau khi hiệu ứng xuất hiện, ngay trước khi fade out, ví dụ thêm `self.wait(1.0)` sau animation ở [`section_2_tag()`](sections/s1_trucmai/s1_trucmai.py:730).
- Không thay đổi `run_time` của các animation khác; chỉ thêm khoảng pause riêng cho callout/mũi tên/viền node trước lệnh `FadeOut` ở dòng kế tiếp.

## Cần sửa — mũi tên bị xéo trong scene hybrid systems

- Vị trí: các mũi tên [`arr_dl`](sections/s1_trucmai/s1_trucmai.py:885), [`arr_ls`](sections/s1_trucmai/s1_trucmai.py:886) và [`arr_g`](sections/s1_trucmai/s1_trucmai.py:899) trong [`section_3_hybrid_systems()`](sections/s1_trucmai/s1_trucmai.py:798).
- Mũi tên nối các box đang bị chéo/không thẳng hàng như trong frame: sắp xếp lại vị trí các mobject theo cùng trục ngang trước khi tạo mũi tên, hoặc dùng điểm đầu/cuối có cùng tung độ khi gọi helper mũi tên.
- Ưu tiên chỉnh `move_to()` của các box; không xoay mũi tên và không thay đổi timing các hiệu ứng khác.

## Cần sửa — tăng tốc giọng đọc tên các paradigm LLM

- Vị trí: [`section_5_two_paradigms()`](sections/s1_trucmai/s1_trucmai.py:930), gồm khối giới thiệu hai hướng tại [`narrated_caption()`](sections/s1_trucmai/s1_trucmai.py:948), khối `LLM-as-enhancer` tại [`narrated_caption()`](sections/s1_trucmai/s1_trucmai.py:954), và khối `LLM-as-predictor` tại [`narrated_caption()`](sections/s1_trucmai/s1_trucmai.py:1015).
- Sinh lại voice cho các cụm `lờ lờ mờ`, `lờ lờ mờ ass èn han xờ`, và `lờ lờ mờ ass prì đích tờ` với tốc độ nhanh hơn nhẹ để cách đọc liền mạch, tự nhiên hơn; mục tiêu khoảng `1.1x–1.15x` so với tốc độ hiện tại.
- Chỉ áp tốc độ mới cho ba khối lời thoại trên, không đổi tốc độ TTS toàn section hoặc toàn video. Mở rộng [`narrated_caption()`](sections/s1_trucmai/s1_trucmai.py:309) để nhận tùy chọn tốc độ theo từng lời thoại, rồi truyền tùy chọn này vào service khi tạo voice; không time-stretch audio đã cache.
- Vì tốc độ là một phần cấu hình sinh audio, bảo đảm cache key/metadata phân biệt bản nhanh với bản cũ để TTS thực sự được tạo lại. Sau khi audio mới quyết định thời lượng, chỉ đồng bộ lại animation trong đúng ba khối nếu cần; không thay timing của scene khác.

## Cần sửa — scene cũ còn mờ dưới scene tiếp theo

- Khi chuyển từ [`section_2_tag()`](sections/s1_trucmai/s1_trucmai.py:678) sang [`section_3_hybrid_systems()`](sections/s1_trucmai/s1_trucmai.py:798), các object của scene/beat trước chưa được dọn sạch hoàn toàn nên vẫn còn hiện mờ phía dưới.
- Ở đầu [`section_3_hybrid_systems()`](sections/s1_trucmai/s1_trucmai.py:798), sau lệnh fade out hiện có, thêm bước dọn toàn bộ mobject còn lại khỏi scene bằng `self.clear()` hoặc gọi helper dọn scene tương đương nếu workflow hiện tại yêu cầu giữ camera/background.
- Ưu tiên dọn riêng các object còn sót (`graph`, `legend`, các overlay/callout và object trung gian) trước khi tạo nội dung mới; không thay đổi timing các hiệu ứng khác. Kiểm tra đặc biệt các object được lưu qua [`self.tag_blackout`](sections/s1_trucmai/s1_trucmai.py:792) và [`self.tag_punch`](sections/s1_trucmai/s1_trucmai.py:792), vì chúng cần được fade out/remove đầy đủ.

## Cần chỉnh — tăng tốc cách đọc EllaGNN

- Vị trí: hai lời thoại chứa `e lờ lờ a gờ nờ nờ` trong [`s2_hoangphan.py`](sections/s2_hoangphan/s2_hoangphan.py:254) và [`s2_hoangphan.py`](sections/s2_hoangphan/s2_hoangphan.py:331), được phát qua helper [`beat()`](sections/s2_hoangphan/s2_hoangphan.py:46).
- Sinh lại voice cho riêng hai beat này với tốc độ nhanh hơn nhẹ, khoảng `1.1x–1.15x`, để chuỗi chữ cái `e lờ lờ a gờ nờ nờ` được đọc liền và tự nhiên hơn.
- Mở rộng [`beat()`](sections/s2_hoangphan/s2_hoangphan.py:46) để nhận tùy chọn tốc độ theo từng câu, rồi chỉ truyền tùy chọn đó ở hai call site trên. Không đổi tốc độ TTS toàn section và không time-stretch audio cũ.
- Bảo đảm tốc độ nằm trong cache key/metadata để TTS được sinh lại. Audio mới quyết định thời lượng của đúng hai beat; không thay timing các scene khác.

## Cần chỉnh — đầu mũi tên trong scene Static fusion

- Vị trí: [`section_6_static_fusion()`](sections/s1_trucmai/s1_trucmai.py:1141), các mũi tên từ `nodes` vào `fusion` được tạo tại [`arrows`](sections/s1_trucmai/s1_trucmai.py:1164) bằng [`small_arrow()`](sections/s1_trucmai/s1_trucmai.py:69).
- Đầu mũi tên hiện bị tụ vào một vùng chung trước block `Static Fusion`, tạo cảm giác chồng đầu/đầu tên quá to và không chỉ rõ hướng đi của từng node. Chỉnh các endpoint để phân bổ theo chiều dọc trên cạnh trái của `fusion`, mỗi endpoint lệch nhau vừa phải và cách nhau đủ để đầu mũi tên không đè lên nhau.
- Dùng `buff` rõ ràng ở cả phía node và block, ví dụ `buff=0.16–0.22`, đồng thời giảm `tip_length` hoặc `stroke_width` riêng cho nhóm nhiều mũi tên nếu cần; không sửa helper dùng chung nếu các scene khác đang dùng đúng đầu mũi tên hiện tại.
- Không cho các mũi tên kết thúc quá xa block hoặc chạm vào viền/đè lên chữ; endpoint nên là `fusion.get_left() + UP * ...` và đầu mũi tên hướng trực tiếp vào cạnh trái block. Giữ màu `MID` và hiệu ứng `GrowArrow`/timing hiện tại.
- Kiểm tra tương tự các mũi tên routing ở [`r_arr_g`](sections/s1_trucmai/s1_trucmai.py:1219), [`r_arr_l`](sections/s1_trucmai/s1_trucmai.py:1220), [`a_up`](sections/s1_trucmai/s1_trucmai.py:1489), [`a_dn`](sections/s1_trucmai/s1_trucmai.py:1490): mỗi đầu mũi tên phải nằm đúng tại cạnh box đích, không bị cụt, lệch hoặc chồng lên label.

## Cần cải thiện — visual `[SKIP LLM]` của Node A

- Vị trí: [`section_7_node_comparison()`](sections/s1_trucmai/s1_trucmai.py:1254), khối lời thoại `gờ nờ nờ dự đoán đúng...`, cụ thể object [`skip_label`](sections/s1_trucmai/s1_trucmai.py:1272).
- Không chỉ fade-in một dòng chữ `[SKIP LLM]` bên dưới probability bar; hãy biến nó thành một quyết định routing trực quan: từ `gnn_bar_A`/Node A xuất hiện badge xanh `KEEP GNN` hoặc `NO LLM QUERY`, kèm dấu ✓ và một mũi tên xanh đi vào nhánh giữ kết quả GNN.
- Thiết kế đề xuất: tạo `skip_card = panel(...)` màu `C_GOOD`, đặt dưới [`gnn_bar_A`](sections/s1_trucmai/s1_trucmai.py:1272); bên trong gồm `check(color=gs.C_GOOD)`, `t("KEEP GNN", ...)` và dòng phụ nhỏ `No LLM call needed`. Tách hai dòng bằng `VGroup(...).arrange(DOWN, buff=...)`, rồi căn giữa card để không dính chữ hoặc tràn khung.
- Animation: sau khi [`gnn_bar_A`](sections/s1_trucmai/s1_trucmai.py:1272) xuất hiện, highlight ngắn Node A và prediction đúng bằng `Indicate(..., color=gs.C_GOOD)`, sau đó `GrowArrow`/`FadeIn` card với scale nhẹ. Giữ nguyên thời gian các hiệu ứng trước đó; nếu cần thêm pause thì chỉ thêm `self.wait(0.3–0.5)` riêng cho quyết định này.
- Đổi lời thoại thành hướng node-aware/cost-aware rõ hơn: `gờ nờ nờ đã đủ tốt cho nót a, nên ta giữ dự đoán này và không tốn thêm một lần gọi lờ lờ mờ.`
- Có thể giữ `[SKIP LLM]` như nhãn nhỏ phụ, nhưng không dùng làm thông điệp chính; thông điệp chính phải là `KEEP GNN` để khán giả hiểu đây là quyết định giữ nhánh chứ không phải chỉ bỏ qua một hiệu ứng.
- Không thay đổi visual/timing của Node B và Node C; mục tiêu là làm riêng trạng thái Node A dễ đọc và nhất quán với routing của GLANCE.

## Cần cải thiện — beat LLM-as-Predictor: graph context expansion → serialized prompt → token/cost growth

- Vị trí: phần Predictor deep-dive trong [`section_5_two_paradigms()`](sections/s1_trucmai/s1_trucmai.py:930), bắt đầu tại [`token_text`](sections/s1_trucmai/s1_trucmai.py:1014) và khối [`narrated_caption()`](sections/s1_trucmai/s1_trucmai.py:1015); các helper graph/sequence nằm tại [`create_hop_nodes()`](sections/s1_trucmai/s1_trucmai.py:1030), [`make_sequence()`](sections/s1_trucmai/s1_trucmai.py:1045).
- Giữ nguyên concept hiện tại `1-hop → 2-hop → 3-hop → serialize → token/cost tăng`; chỉ làm causal chain rõ và cinematic hơn: `hop expansion → node explosion → serialized text expansion → token growth → cost growth`.
- Đổi lời thoại mở đầu thành: `Với LLM-as-Predictor, thông tin của node và neighborhood phải được tuần tự hóa thành một chuỗi văn bản để LLM xử lý.` Đổi lời thoại các stage thành: `Với một-hop, prompt chỉ cần chứa node trung tâm và một nhóm nhỏ các hàng xóm.`; `Nhưng khi mở rộng sang hai-hop, số node cần mô tả tăng nhanh, kéo theo lượng văn bản trong prompt cũng phình ra.`; `Nếu tiếp tục mở rộng neighborhood, số lượng node có thể tăng rất nhanh. Mỗi node lại mang theo văn bản riêng, khiến prompt ngày càng dài và tốn kém để xử lý.`; câu kết: `Vì vậy, càng đưa nhiều graph context vào LLM, chi phí cho mỗi lần gọi càng lớn. Và nếu làm điều này cho mọi node thì sao?`

### Visual cần chỉnh

- Không cho target, các node theo hop, sequence và counter xuất hiện đồng loạt như hiện tại ở [`self.play()`](sections/s1_trucmai/s1_trucmai.py:1077). Stage 1: target `A` xuất hiện trước, ring 1-hop pulse, node `B/C/D/E` bật lần lượt; mỗi node mới xuất hiện có bản sao bay sang sequence để hành động `Serialize` được nhìn thấy.
- Stage 2: dùng expanding ring từ target, lần lượt mở radius 0 → 0.8 → 1.6; node 2-hop bật theo wave, sequence grow thêm box theo chiều ngang thay vì chỉ `ReplacementTransform` cả dải.
- Stage 3: chia node thành 2–3 wave, mỗi wave gồm ring expand → nodes pop → sequence kéo dài → counter tăng. Không fade-in toàn bộ 3-hop node cùng lúc.
- Counter hiện tại như `Graph nodes: 5` và `Text tokens: 80` tại [`counters`](sections/s1_trucmai/s1_trucmai.py:1070) dễ bị hiểu là số liệu thực nghiệm. Đổi thành card `CONTEXT SIZE` với `Nodes 5`, `Prompt ~80`, thêm label nhỏ `Schematic example`/`Illustrative`; dùng dạng `~80`, `~420`, `~1.3k` nếu vẫn giữ con số.
- Counter nên animate tăng theo stage: `~80 → ~420 → ~760 → ~1.3k`, không nhảy thẳng `420 → 1300`; khi stage cuối tới, đổi `Prompt` sang amber rồi đỏ nhẹ sau một nhịp, không đỏ ngay.
- Sequence phải gợi rõ serialized text, không chỉ giống ID node `[A][B][C]`: thêm mini-lines/stripes trong mỗi box để biểu thị mỗi node mang theo Title/Abstract; có thể giữ label `Serialized graph prompt` và dòng phụ `Graph structure + node text → tokens`.
- Punchline nên đổi từ `Larger graph context -> Longer text sequence` / `More tokens, higher LLM cost` thành `MORE NEIGHBORS → MORE TEXT → MORE LLM COST`, hoặc tốt hơn nếu muốn dẫn sang routing: `WHY QUERY THE LLM FOR EVERY NODE?` với dòng phụ `especially when each query carries neighborhood context`.
- Giảm [`blackout3`](sections/s1_trucmai/s1_trucmai.py:1026) từ `fill_opacity=0.95` xuống khoảng `0.72` để vẫn thấy graph, sequence và counter phía sau punchline.

### Ràng buộc

- Giữ các helper và concept hiện tại; không mở rộng thành một metaphor khác.
- Ghi rõ đây là minh họa khái niệm, không trình bày các counter như số liệu paper cụ thể.
- Không thay đổi timing các scene/beat khác; chỉ điều chỉnh timing nội bộ của Predictor deep-dive khi cần để sequence và counter có đủ thời gian được đọc.

## Cần viết lại — beat “Better semantics, corrupted aggregation”

- Vị trí: beat hiện tại bắt đầu tại [`narrated_caption()`](sections/s1_trucmai/s1_trucmai.py:982) trong [`section_5_two_paradigms()`](sections/s1_trucmai/s1_trucmai.py:930), cùng các object [`noisy_nbhd`](sections/s1_trucmai/s1_trucmai.py:953) và [`noisy_msgs`](sections/s1_trucmai/s1_trucmai.py:976).
- Đổi lời thoại thành: `Tuy nhiên, biểu diễn ngữ nghĩa tốt hơn không giải quyết được vấn đề cấu trúc. Khi neighborhood chứa nhiều tín hiệu xung đột với node trung tâm, GNN vẫn tổng hợp các message này. Kết quả là biểu diễn của node có thể bị kéo sang một vùng khác trong không gian đặc trưng, và dẫn đến dự đoán sai.` Nếu cần giữ beat ngắn, dùng: `Tuy nhiên, biểu diễn ngữ nghĩa tốt hơn không loại bỏ thiên lệch cấu trúc. Với một neighborhood dị phối, message passing vẫn có thể kéo biểu diễn của node theo hướng sai.`
- Đổi tên khái niệm/code từ `noisy_nodes`, `noisy_arrows` sang `conflicting_nodes`, `conflicting_msgs` hoặc `hetero_nodes`, `hetero_msgs`; không gọi mọi heterophilous neighbor là “noise”.
- Thay visual “neighbor đỏ rồi target rung” bằng causal story: `semantic feature tốt → conflicting messages → AGGREGATE/mean → updated representation → prediction bị đổi`. Thêm mini-module `AGGREGATE` trước target; message cùng lớp dùng xanh, message xung đột dùng coral và bay vào module.
- Bỏ hai animation rung target bằng [`there_and_back`](sections/s1_trucmai/s1_trucmai.py:998). Thay bằng latent axis/decision line thể hiện `h_v before → h_v after` dịch theo hướng class đối nghịch; có thể kèm prediction schematic `A: 0.78 → 0.39`, `B: 0.17 → 0.55` và label `Schematic example`.
- Đổi punchline cũ `BETTER TEXT ≠ NO STRUCTURAL BIAS` tại [`bias_text`](sections/s1_trucmai/s1_trucmai.py:1004) thành `BETTER SEMANTICS ≠ RELIABLE AGGREGATION`, kèm dòng phụ `Message passing still depends on neighbors`.
- Không dùng blackout toàn màn hình opacity `0.85`; giảm còn khoảng `0.45` hoặc dùng card riêng để vẫn nhìn thấy graph, các message coral và hướng dịch representation phía sau punchline.
- Giữ nguyên các hiệu ứng/timing không liên quan; chỉ thay phần beat này và bảo đảm kết quả dẫn sang câu hỏi routing: node nào GNN gặp khó và khi nào LLM có thể giúp.

## Cần viết lại — Beat 4 và Beat 5 của hybrid systems

- Vị trí: Beat 4 bắt đầu tại khối [`narrated_caption()`](sections/s1_trucmai/s1_trucmai.py:864) và Beat 5 tại khối [`narrated_caption()`](sections/s1_trucmai/s1_trucmai.py:892), đều thuộc [`section_3_hybrid_systems()`](sections/s1_trucmai/s1_trucmai.py:798).
- Mục tiêu nội dung: Beat 4 phải xây dựng tính bổ sung giữa GNN và LLM; Beat 5 phải chuyển ngay tính bổ sung đó thành bài toán routing của GLANCE. Không kể theo hướng LLM thay thế GNN và không kết thúc bằng thông điệp hybrid fusion đã là lời giải hoàn chỉnh.

### Beat 4 — Hai expert song song: Structure và Semantics

- Không gọi `FadeOut(graph)` và không đẩy GNN thành thành phần phụ. Giữ graph cùng GNN trên màn hình, thu nhỏ/chuyển xuống nhánh dưới nếu cần để dành chỗ cho nhánh LLM phía trên.
- Nhánh xanh: graph/neighbors → GNN → `Structural representation`. Cho message chạy từ hàng xóm về ego node trước khi tạo vector xanh.
- Nhánh cam: `Node text` với `Title` và `Abstract` → LLM → `Semantic representation`. Có thể highlight ngắn các từ khóa trong văn bản rồi co chúng thành vector cam; không mô phỏng attention hoặc cơ chế reasoning nội bộ.
- Frame cuối Beat 4 phải giữ đồng thời hai branch và hai vector để thể hiện hai năng lực bổ sung, không biến thành chuỗi tuần tự `GNN → LLM`.
- Lời thoại đề xuất: `Sự phát triển của các mô hình ngôn ngữ lớn mở ra một nguồn thông tin bổ sung cho graph learning. Nếu GNN học từ cấu trúc và các node lân cận, thì LLM có thể khai thác trực tiếp nội dung văn bản để tạo ra những biểu diễn ngữ nghĩa giàu thông tin.`

### Beat 5 — Fusion hợp lý, nhưng áp dụng đồng loạt tạo vấn đề

- Cho vector cấu trúc xanh và vector ngữ nghĩa cam cùng đi vào block tím `GNN–LLM Fusion` để xác nhận việc kết hợp hai nguồn là hướng tự nhiên.
- Sau nhịp fusion ngắn, zoom out sang graph khoảng 8 node và minh họa cùng một chiến lược được áp cho mọi node. Cho các mũi tên cam sang LLM bật đồng loạt và counter tăng `LLM queries: 0 → 8 / 8`.
- Highlight một node dễ mà GNN đã dự đoán đúng, ví dụ `GNN ✓ · 96% confidence`, nhưng node vẫn bị gửi sang LLM. Dùng chi tiết này để tạo tension accuracy–cost, không khẳng định mọi hệ thống cũ luôn gọi LLM nếu nội dung section phía sau còn cần phân biệt hai paradigm.
- Bỏ frame kết [`LLM + GNN = Hybrid graph learning`](sections/s1_trucmai/s1_trucmai.py:910). Fade/dim các thành phần khác và kết bằng câu hỏi lớn `Does every node really need the LLM?`; dòng nhỏ `Accuracy ↔ Computational cost`. Câu hỏi dùng `INK` hoặc `C_ROUTER`, không dùng màu cam.
- Lời thoại đề xuất: `Vì hai mô hình khai thác những nguồn thông tin khác nhau, một hướng tự nhiên là kết hợp chúng trong cùng một kiến trúc. Tuy nhiên, phần lớn các phương pháp hiện tại áp dụng cùng một chiến lược fusion cho mọi node, khiến LLM vẫn được sử dụng ngay cả khi GNN đã xử lý node đó tốt. Vậy, có thực sự cần gọi LLM cho tất cả các node?`
- Nếu phải giữ Beat 5 trong khoảng 8 giây, rút gọn lời thoại thành: `Kết hợp hai nguồn là một hướng tự nhiên. Nhưng nếu cùng một chiến lược được áp cho mọi node, LLM có thể vẫn bị gọi khi GNN đã dự đoán tốt. Vậy node nào thực sự cần LLM?`

### Ràng buộc chuyển cảnh

- Mạch cần đạt: `GNN knows structure + LLM understands text → combining makes sense → not every node needs the same treatment → when and for which nodes should LLM be used?`
- Beat 4 không xóa GNN; Beat 5 không dừng ở hybrid. Frame cuối phải dẫn tự nhiên sang phần `Which nodes should be routed?` và thesis node-aware/cost-aware của GLANCE.
- Màu: GNN/structure/vector cấu trúc dùng `C_GNN`; LLM/text/vector ngữ nghĩa dùng `C_LLM`; fusion và câu hỏi routing dùng `C_ROUTER`; node dễ dùng `C_GOOD`; node cần hỗ trợ dùng amber/coral và dấu `?`.
