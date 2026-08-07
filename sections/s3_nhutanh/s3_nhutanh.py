"""Section 3 — Structural signal.  Owner: Nhựt Anh.

Nguồn trong paper: §4.2.1 (tr.4) — định nghĩa local homophily.
Kịch bản chi tiết: sections/s3_nhutanh/TASK.md

Cảnh 1 — Local homophily. Năm nhịp theo storyboard của nhóm:
    1. giới thiệu tín hiệu, node v + 4 hàng xóm
    2. kiểm tra từng hàng xóm, dựng công thức
    3. thay số, h_v = 0.75
    4. homophily cao  → message nhất quán → GNN đúng
    5. homophily thấp → neighborhood heterophilous → GNN sai

Cảnh 6–19 — Step 1 của kiến trúc (§5.1.1, tr.5–6): năm routing signals.
Section 3 dừng đúng ở f_v; phần router / top-k / refiner thuộc section 4.

Cảnh 7–19 vốn là S4_03…S4_14 của section 4, đã chuyển nguyên sang đây theo
thống nhất của nhóm để section 3 tự tạo đủ năm signal rồi mới bàn giao f_v.
Vì vậy chúng dùng ngôn ngữ hình của section 4 (`step_header`, `equation_card`,
`takeaway_chip`) chứ không dùng `heading()` như cảnh 1–5; cảnh 6 cũng đã đổi sang
`step_header` để dãy số trên pill chạy liên tục 06→19. Hai đoạn độc đáo của
bản cũ được giữ lại: bảng hard vs soft ở cuối S3_16, và cảnh báo d_v vs relative
degree ở cuối S3_18 — signal thứ năm là **degree thô** d_v, không phải relative
degree đã phân tích ở cảnh 2.

Thời lượng do chính giọng đọc quyết định (manim-voiceover), không ép tay.
Đoạn mở đầu 0:00–0:32 chưa có kịch bản nên chưa dựng.

Render:  manim -ql sections/s3_nhutanh/s3_nhutanh.py -a
Đổi giọng: GLANCE_TTS=azure manim -ql ...   (xem GlanceScene trong glance_style.py)
"""

import pathlib
import sys

# Cho phép import glance_style.py ở thư mục gốc repo.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from glance_style import *  # noqa: E402,F403

SECTION = "3"
SECTION_NAME = "Structural signal"
OWNER = "Nhựt Anh"
ACCENT = SECTION_COLORS.get(SECTION, C_HIGHLIGHT)

# Vị trí node trong cảnh 1: v ở giữa, 4 hàng xóm quanh nó.
V_POS = LEFT * 3.4 + UP * 0.35
U_POS = [
    V_POS + UP * 1.45 + LEFT * 1.55,     # u1
    V_POS + UP * 1.45 + RIGHT * 1.55,    # u2
    V_POS + DOWN * 1.45 + LEFT * 1.55,   # u3
    V_POS + DOWN * 1.45 + RIGHT * 1.55,  # u4
]
# Ba hàng xóm cùng nhãn với v, một hàng xóm khác nhãn.
SAME_LABEL = [True, True, True, False]

# Lời thuyết minh. Viết theo cách ĐỌC LÊN, không theo cách viết công thức:
# "h_v" đọc thành "hắc phẩy vê", "3/4" đọc thành "ba phần tư". Đổi text ở đây là
# audio tự sinh lại; giữ nguyên text thì dùng bản đã cache, render nhanh.
VO = {
    "intro": (
        "Tín hiệu đầu tiên là độ đồng nhất cục bộ. "
        "Nó đo mức độ tương đồng về nhãn giữa một nót và các hàng xóm trực tiếp của nó."
    ),
    "check": (
        "Cụ thể, với mỗi hàng xóm u, ta kiểm tra liệu nhãn của u "
        "có giống nhãn của vê hay không. "
        "Sau đó lấy tỷ lệ trên toàn bộ tập hàng xóm."
    ),
    "value": (
        "Trong ví dụ này, ba trong bốn hàng xóm cùng nhãn với vê, "
        "vì vậy hắc phẩy vê bằng ba phần tư, tức không chấm bảy năm."
    ),
    "high": (
        "Khi độ đồng nhất cục bộ cao, thông tin từ hàng xóm thường nhất quán với nót trung tâm. "
        "Vì gờ nờ nờ học bằng cách tổng hợp thông tin lân cận, "
        "quá trình truyền thông điệp thường có lợi trong trường hợp này."
    ),
    "low": (
        "Ngược lại, khi độ đồng nhất cục bộ thấp, phần lớn hàng xóm thuộc lớp khác. "
        "Việc tổng hợp các biểu diễn này có thể đưa tín hiệu không phù hợp "
        "vào nót trung tâm, và khiến gờ nờ nờ dự đoán sai."
    ),
    # --- Cảnh 2: relative degree ---
    "rd_intro": (
        "Tín hiệu thứ hai là bậc tương đối. "
        "Bậc thông thường chỉ cho biết nót có bao nhiêu cạnh. "
        "Bậc tương đối đặt giá trị đó trong bối cảnh của chính tập hàng xóm."
    ),
    "rd_formula": (
        "Với mỗi hàng xóm u, tác giả so sánh bậc của vê với bậc của u, "
        "rồi lấy trung bình trên tất cả hàng xóm."
    ),
    "rd_scale": (
        "Nếu bậc tương đối lớn hơn một, nót vê có xu hướng kết nối nhiều hơn các hàng xóm. "
        "Nếu nhỏ hơn một, nó kết nối ít hơn các nót xung quanh."
    ),
    "rd_value": (
        "Trong ví dụ này, bậc của vê thấp hơn cả hai hàng xóm, "
        "nên bậc tương đối xấp xỉ không chấm bảy chín, nhỏ hơn một."
    ),
    # --- Cảnh 3: GNN và LLM bổ sung nhau ---
    "cp_setup": (
        "Sau đó, tác giả chia các nót thành từng nhóm theo độ đồng nhất cục bộ "
        "và bậc tương đối, rồi so sánh độ chính xác của gờ nờ nờ với lờ lờ mờ trong mỗi nhóm."
    ),
    "cp_trend": (
        "Kết quả cho thấy một xu hướng bổ sung rõ rệt. "
        "Gi en en hoạt động tốt ở những vùng có độ đồng nhất cao và được kết nối tốt. "
        "Nhưng khi độ đồng nhất hoặc bậc tương đối giảm, lợi thế của lờ lờ mờ tăng lên."
    ),
    "cp_gain": (
        "Trên Cô-ra, ở nhóm nót khó, lờ lờ mờ đạt mức cải thiện tới hai mươi chấm bốn phần trăm "
        "so với mô hình tốt tiếp theo là gi xi en hai sử dụng đặc trưng được lờ lờ mờ tăng cường."
    ),
    "cp_interact": (
        "Hai tín hiệu này còn tương tác với nhau. "
        "Khi đồng thời phân nhóm theo cả độ đồng nhất và bậc, "
        "chênh lệch hiệu năng giữa các nhóm cấu trúc có thể lên tới ba mươi chấm một phần trăm."
    ),
    # --- Cảnh 4: true -> estimated homophily ---
    "eh_problem": (
        "Độ đồng nhất cục bộ có vẻ là một tín hiệu định tuyến rất tốt. "
        "Tuy nhiên, công thức này cần nhãn thật của nót và hàng xóm, "
        "đúng vào những thông tin không có sẵn đối với các nót cần dự đoán."
    ),
    "eh_mlp": (
        "Để giải quyết vấn đề này, tác giả huấn luyện một mờ lờ bê kiu "
        "trên đặc trưng nót để dự đoán nhãn tạm thời."
    ),
    "eh_estimate": (
        "Sau đó, các nhãn dự đoán được dùng thay cho nhãn thật "
        "để tính độ đồng nhất cục bộ ước lượng."
    ),
    "eh_rank": (
        "Trong đánh giá định tuyến bằng en xi ét, độ đồng nhất thực có thứ hạng trung bình tốt nhất. "
        "Quan trọng hơn, khi loại bỏ những tín hiệu cần nhãn thật, "
        "độ đồng nhất ước lượng đạt thứ hạng trung bình tốt nhất "
        "trong các phương pháp kinh nghiệm không cần nhãn."
    ),
    # --- Cảnh kết ---
    "end_summary": (
        "Như vậy, độ đồng nhất cục bộ và bậc tương đối không trực tiếp dự đoán nhãn. "
        "Chúng giúp nhận diện những nót có cấu trúc bất lợi đối với gờ nờ nờ, "
        "và nơi lờ lờ mờ có khả năng tạo thêm giá trị."
    ),
    "end_router": (
        "Tuy nhiên, kết quả cũng cho thấy không có một tín hiệu đơn lẻ nào "
        "đủ ổn định để quyết định định tuyến trong mọi trường hợp. "
        "Vì vậy, gờ lans không sử dụng một ngưỡng cố định. "
        "Thay vào đó, nó kết hợp các tín hiệu này trong một bộ định tuyến "
        "được học thích nghi cho từng nót."
    ),
    "end_next": (
        "Phần tiếp theo sẽ đi vào chính những tín hiệu mà bộ định tuyến này đọc từ mỗi nót."
    ),
    # ------------------------------------------------------------------
    # Phần bổ sung — năm routing signals của Step 1 (§5.1.1, tr.5–6).
    # ------------------------------------------------------------------
    "fs_open": (
        "Vì vậy, thay vì chỉ dựa vào độ đồng nhất, gờ lans mô tả mỗi nót "
        "bằng năm tín hiệu định tuyến bổ sung cho nhau."
    ),
    "fs_roles": (
        "Mỗi tín hiệu phản ánh một khía cạnh khác nhau: thông tin gờ nờ nờ đã học được, "
        "mức độ tin cậy của gờ nờ nờ, sự nhất quán với hàng xóm, "
        "nội dung riêng của nót, và lượng thông tin cấu trúc sẵn có. "
        "Phần còn lại của mục này sẽ dựng lần lượt từng tín hiệu."
    ),
    # --- Cảnh 7: ba nguồn thông tin của node ---
    "ts_intro": (
        "Năm tín hiệu này đến từ ba nguồn. Với nót a, gờ lans thu thập lần lượt "
        "ba nhóm thông tin sau."
    ),
    "ts_gnn": (
        "Nhóm thứ nhất đến từ gờ nờ nờ, gồm véc-tơ biểu diễn của nót, "
        "dự đoán ban đầu và độ bất định."
    ),
    "ts_mlp": (
        "Nhóm thứ hai đến từ một mờ lờ bê riêng, được gọi là qui, chỉ sử dụng đặc trưng "
        "của nót để hỗ trợ ước lượng độ đồng nhất."
    ),
    "ts_direct": (
        "Nhóm cuối cùng là thông tin trực tiếp, gồm đặc trưng gốc và bậc của nót."
    ),
    "ts_close": (
        "Các nguồn thông tin này sẽ được kết hợp để bộ định tuyến quyết định "
        "có nên sử dụng lờ lờ mờ cho nót a hay không. "
        "Ta bắt đầu từ nhóm thứ nhất: những gì gờ nờ nờ tạo ra."
    ),
    # --- Cảnh 8: trạng thái ban đầu của GNN ---
    "is_layer0": (
        "Đầu tiên, nót a được đưa vào mô hình nền gờ nờ nờ. Ở lớp số không, "
        "trạng thái ẩn của nót a chính là đặc trưng ban đầu của nót. "
        "Nói cách khác, hắc phẩy a mũ không bằng ích phẩy a."
    ),
    "is_example": (
        "Ví dụ, nếu đặc trưng của nót a là véc-tơ không chấm tám, âm không chấm một "
        "và không chấm năm, thì trạng thái ẩn ban đầu cũng nhận đúng véc-tơ này."
    ),
    "is_noneighbor": "Ở bước này chưa có thông tin từ các nót hàng xóm.",
    # --- Cảnh 9: bước tổng hợp ---
    "ag_open": "Tiếp theo là bước tổng hợp.",
    "ag_collect": (
        "Gờ nờ nờ thu thập trạng thái ẩn của các nót hàng xóm của a, "
        "ví dụ như bê, xê, đê và e."
    ),
    "ag_combine": (
        "Sau đó, các véc-tơ này được tổng hợp thành một thông điệp hàng xóm. "
        "Trong hoạt cảnh, chúng ta sử dụng phép trung bình để minh họa."
    ),
    "ag_math": (
        "Bốn véc-tơ hàng xóm được cộng lại rồi chia cho bốn, tạo thành thông điệp mới "
        "là không chấm năm, không chấm năm. Lưu ý rằng phép trung bình chỉ là một ví dụ; "
        "tùy mô hình nền gờ nờ nờ, phép tổng hợp có thể được cài đặt theo cách khác."
    ),
    # --- Cảnh 10: bước cập nhật ---
    "up_intro": (
        "Sau khi có thông điệp hàng xóm, gờ nờ nờ thực hiện bước cập nhật. "
        "Bước này kết hợp trạng thái trước đó của nót a với thông tin vừa tổng hợp từ hàng xóm."
    ),
    "up_example": (
        # "minh họa" đứng ngay đầu câu bị giọng đọc phát méo; bỏ hẳn từ này và
        # dùng "ở đây" cho câu chạy trơn. Đổi text cũng khiến TTS sinh lại.
        "Trong ví dụ ở đây, trạng thái cũ của a là không chấm hai, không chấm tám, "
        "còn thông điệp hàng xóm là không chấm sáu, không chấm bốn."
    ),
    "up_result": (
        "Sau bước cập nhật, ta thu được một biểu diễn mới là không chấm bốn, không chấm sáu."
    ),
    "up_caveat": (
        "Các con số này chỉ dùng để minh họa luồng xử lý. Trong mô hình thực tế, "
        "giá trị được quyết định bởi các tham số đã học."
    ),
    # --- Cảnh 11: trước và sau khi cập nhật ---
    "ba_identity": (
        "Điểm cần lưu ý là nót a vẫn là cùng một bài báo. "
        "Thứ thay đổi không phải danh tính của nót mà là biểu diễn của nó."
    ),
    "ba_before": "Trước bước cập nhật, véc-tơ chủ yếu chứa thông tin của chính nót a.",
    "ba_after": "Sau bước cập nhật, véc-tơ đã tích hợp thêm bằng chứng từ vùng lân cận.",
    "ba_repeat": (
        "Quá trình tổng hợp và cập nhật có thể được lặp lại qua nhiều lớp gờ nờ nờ "
        "để thu được biểu diễn cuối cùng."
    ),
    # --- Cảnh 12 — Signal 1: node embedding z_G(A) ---
    "ep_graph": (
        "Quay lại đồ thị quen thuộc của cả video. Nót a cùng vùng lân cận trong "
        "phạm vi ca bước được đưa vào mô hình nền gờ nờ nờ."
    ),
    "ep_two": "Sau các lớp truyền thông điệp, gờ nờ nờ tạo ra hai đầu ra quan trọng.",
    "ep_embedding": (
        "Đầu ra thứ nhất là véc-tơ biểu diễn dét gờ a. Véc-tơ biểu diễn này tóm tắt "
        "cả đặc trưng của nót a và thông tin cấu trúc mà gờ nờ nờ đã học được. "
        "Đây chính là tín hiệu định tuyến đầu tiên."
    ),
    "ep_prediction": "Đầu ra thứ hai là dự đoán ban đầu bê hắc phẩy a.",
    "ep_head": (
        "Đầu dự đoán nhận véc-tơ biểu diễn, đi qua mờ lờ bê và sóp mác để tạo xác suất "
        "trên các lớp. Đây cũng là dự đoán cuối cùng nếu nót a không được gửi sang lờ lờ mờ, "
        "và nó được lưu lại chứ không phải một thành phần của véc-tơ định tuyến."
    ),
    # --- Cảnh 13 — Signal 2: uncertainty u_A ---
    "uc_stable": (
        "Gờ lans không chỉ quan tâm gờ nờ nờ dự đoán lớp nào "
        "mà còn quan tâm dự đoán đó có ổn định hay không."
    ),
    "uc_dropout": (
        "Hệ thống thực hiện nhiều lượt truyền xuôi với đờ-róp-ao cho cùng một nót. "
        "Nếu các lần chạy tạo ra phân phối gần giống nhau, gờ nờ nờ tương đối chắc chắn."
    ),
    "uc_high": (
        "Ngược lại, nếu kết quả thay đổi nhiều giữa các lần chạy, "
        "độ bất định của nót sẽ cao."
    ),
    "uc_signal": (
        "Độ bất định là một tín hiệu cho thấy nót a có thể là trường hợp khó, "
        "nhưng nó không được sử dụng riêng lẻ để quyết định định tuyến."
    ),
    # --- Cảnh 14: MLP Q ---
    "mq_intro": (
        "Song song với gờ nờ nờ, gờ lans sử dụng một mờ lờ bê được ký hiệu là qui."
    ),
    "mq_nostructure": (
        "Khác với gờ nờ nờ, mờ lờ bê này chỉ nhận đặc trưng ích phẩy vê của nót, "
        "không sử dụng cạnh và không thực hiện truyền thông điệp."
    ),
    "mq_output": (
        "Với mỗi nót, qui tạo ra một phân phối xác suất mềm bê qui phẩy vê."
    ),
    "mq_shared": (
        "Cùng một mờ lờ bê được áp dụng cho nót a và các nót hàng xóm bê, xê, đê, e."
    ),
    "mq_purpose": (
        "Mục đích của các phân phối này không phải để thay thế dự đoán của gờ nờ nờ, "
        "mà để hỗ trợ ước lượng mức độ tương đồng giữa nót và vùng lân cận."
    ),
    # --- Cảnh 15: trung bình phân phối hàng xóm ---
    "na_collect": (
        "Để đánh giá vùng lân cận của a, gờ lans lấy một phân phối từ mỗi nót hàng xóm."
    ),
    "na_sum": "Các phân phối của bê, xê, đê và e được cộng lại thành ết phẩy a.",
    "na_divide": "Sau đó, tổng này được chia cho số lượng hàng xóm.",
    "na_average": (
        "Trong ví dụ, nót a có bốn hàng xóm nên hệ thống chia cho bốn và thu được "
        "phân phối trung bình không chấm hai bảy năm, không chấm bốn tám không, "
        "không chấm hai bốn năm."
    ),
    "na_meaning": (
        "Véc-tơ này đại diện cho xu hướng lớp chung trong vùng lân cận của nót a."
    ),
    # --- Cảnh 16 — Signal 3: soft homophily h mũ ---
    "sh_compare": (
        "Tiếp theo, gờ lans so sánh phân phối của chính nót a "
        "với phân phối trung bình của các hàng xóm."
    ),
    "sh_dot": "Phép so sánh được thực hiện bằng tích vô hướng.",
    "sh_meaning": (
        "Nếu hai phân phối tương tự nhau, giá trị sẽ cao, cho thấy nót a có xu hướng "
        "giống vùng lân cận. Nếu hai phân phối khác nhau, giá trị này sẽ thấp "
        "và nót a có khả năng nằm trong vùng dị phối."
    ),
    "sh_soft": (
        "So với việc chỉ kiểm tra hai nhãn dự đoán có giống nhau hay không, "
        "phiên bản mềm còn giữ lại mức độ chắc chắn của mờ lờ bê."
    ),
    "sh_prior": (
        "Đây chỉ là một tín hiệu tiên nghiệm cho việc định tuyến, "
        "nghĩa là một tín hiệu hỗ trợ bộ định tuyến, "
        "chứ không trực tiếp quyết định việc gọi lờ lờ mờ."
    ),
    # --- Cảnh 17 — Signal 4: đặc trưng gốc x_A ---
    "nf_keep": (
        "Ngoài các biểu diễn đã được học, gờ lans vẫn giữ lại thông tin gốc của nót a."
    ),
    "nf_vector": (
        "Thành phần đầu tiên là ích phẩy a, tức đặc trưng được trích xuất từ nội dung văn bản."
    ),
    "nf_ego": (
        "Đặc trưng này giữ nguyên nội dung riêng của nót trước khi gờ nờ nờ tổng hợp "
        "thông tin từ hàng xóm, nên nó vẫn hữu ích khi véc-tơ biểu diễn của gờ nờ nờ "
        "bị vùng lân cận làm nhiễu."
    ),
    # --- Cảnh 18 — Signal 5: bậc d_A ---
    "dg_degree": (
        "Thành phần thứ hai là bậc đê phẩy a, thể hiện số lượng hàng xóm trực tiếp."
    ),
    "dg_count": "Trong ví dụ, a kết nối với bốn nót nên bậc bằng bốn.",
    "dg_direct": (
        "Hai thông tin này giúp bộ định tuyến quan sát trực tiếp cả đặc điểm ngữ nghĩa "
        "ban đầu lẫn lượng thông tin cấu trúc mà gờ nờ nờ có thể khai thác."
    ),
    "dg_vs_rd": (
        "Cần phân biệt rõ với phần phân tích lúc nãy: ở đó ta dùng bậc tương đối "
        "để so sánh nót với hàng xóm, còn bộ định tuyến của gờ lans dùng bậc thô, "
        "tức trực tiếp số lượng hàng xóm."
    ),
    # --- Cảnh 19: ghép năm signal thành f_A ---
    "rf_cards": (
        "Đến đây, toàn bộ tín hiệu được ghép thành đặc trưng định tuyến ép phẩy a."
    ),
    "rf_five": (
        "Véc-tơ này gồm năm thành phần: véc-tơ biểu diễn của gờ nờ nờ, độ bất định, "
        "độ đồng nhất ước lượng, đặc trưng gốc và bậc. "
        "Mỗi thành phần phản ánh một khía cạnh khác nhau của nót a."
    ),
    "rf_note": (
        "Quan trọng là không có một tín hiệu riêng lẻ nào tự quyết định định tuyến. "
        "Bộ định tuyến sẽ học cách xem xét tổ hợp của cả năm tín hiệu."
    ),
    "rf_close": (
        "Đến đây, năm nguồn thông tin đã được nối thành một véc-tơ đặc trưng định tuyến. "
        "Véc-tơ này mô tả trạng thái của nót, nhưng chưa phải là quyết định gọi lờ lờ mờ. "
        "Đã có tín hiệu. Giờ ráp nó vào một kiến trúc chạy được."
    ),
}

# Số liệu Hình 1 (tr.4), panel Cora — xem docs/paper-map.md.
H_BINS = ["0.0–0.2", "0.2–0.4", "0.4–0.6", "0.6–0.8", "0.8–1.0"]
H_COUNTS = [220, 195, 240, 265, 1920]
H_SERIES = [
    {"name": "LLM", "values": [0.505, 0.585, 0.625, 0.850, 0.955], "color": C_LLM},
    {"name": "GCNII (Enh.)", "values": [0.301, 0.520, 0.645, 0.915, 0.975], "color": C_GNN},
    {"name": "GCN (Std.)", "values": [0.185, 0.320, 0.600, 0.900, 0.975], "color": MUTED},
]


# --------------------------------------------------------------------------
# Phần bổ sung — năm routing signals (Hình 2 & §5.1.1, tr.5–6).
#
# Thứ tự và tên đúng theo khối "Step 1" trong Hình 2. Signal thứ năm là degree
# thô d_v, KHÔNG phải relative degree của §4.2.1 — hai đại lượng khác nhau.
# Mỗi signal giữ một màu cố định xuyên suốt các cảnh 6–12 để dễ theo dõi.
# --------------------------------------------------------------------------
SIGNALS = [
    ("Node embedding", C_GNN, "Representation"),
    ("Node uncertainty", C_BAD, "Confidence"),
    ("Homophily estimation", C_GOOD, "Alignment"),
    ("Node features", C_LLM, "Content"),
    ("Degree", C_HIGHLIGHT, "Connectivity"),
]

# Provenance của phần kiến trúc (cảnh 6–19). Scene khái niệm không hiện stamp
# nguồn trên hình, xem "Shared Elements" trong plan.md.
SRC_ARCH = "§5.1.1 & Figure 2, pp.5–6"


class S3_01_LocalHomophily(GlanceScene):
    """Cảnh 1 — Local homophily."""

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()

        # ------------------------------------------------------------------
        # Nhịp 1 — Giới thiệu tín hiệu. Node v và bốn hàng xóm.
        # ------------------------------------------------------------------
        head = heading("Signal 1: Local homophily", color=ACCENT).to_edge(UP, buff=0.75)
        v_dot = Dot(V_POS, radius=0.24, color=C_GNN)
        v_lab = txt("v", size=22, color=INK).next_to(v_dot, DOWN, buff=0.18)

        u_dots, u_labs, edges = [], VGroup(), VGroup()
        for i, (pos, same) in enumerate(zip(U_POS, SAME_LABEL)):
            color = C_GNN if same else C_BAD
            u_dots.append(Dot(pos, radius=0.20, color=color))
            u_labs.add(txt(f"u{i + 1}", size=18, color=MUTED)
                       .next_to(u_dots[-1], UP, buff=0.14))
            edges.add(Line(V_POS, pos, stroke_width=2.4, color=C_EDGE, z_index=-1))

        legend = VGroup(
            VGroup(Dot(radius=0.1, color=C_GNN), txt("same label", size=17, color=INK)
                   ).arrange(RIGHT, buff=0.2),
            VGroup(Dot(radius=0.1, color=C_BAD), txt("different label", size=17, color=INK)
                   ).arrange(RIGHT, buff=0.2),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        legend.next_to(edges, DOWN, buff=0.7)

        with self.voiceover(text=VO["intro"]):
            self.play(Write(head), run_time=1.6)
            self.play(GrowFromCenter(v_dot), FadeIn(v_lab), run_time=1.2)
            for dot, lab, edge in zip(u_dots, u_labs, edges):
                self.play(Create(edge), GrowFromCenter(dot), FadeIn(lab), run_time=0.85)
            self.play(FadeIn(legend, shift=UP * 0.15), run_time=0.9)

        # ------------------------------------------------------------------
        # Nhịp 2 — Kiểm tra từng hàng xóm, dựng công thức từng phần.
        # ------------------------------------------------------------------
        formula = MathTex(
            r"h_v", r"=", r"\frac{1}{|\mathcal{N}(v)|}",
            r"\sum_{u \in \mathcal{N}(v)}", r"\mathbf{1}[y_u = y_v]",
            font_size=40,
        )
        formula[0].set_color(ACCENT)
        formula[4].set_color(C_HIGHLIGHT)
        formula.to_edge(RIGHT, buff=0.9).shift(UP * 1.1)
        if formula.width > 6.4:
            formula.scale_to_fit_width(6.4)

        digits = VGroup()
        for dot, same in zip(u_dots, SAME_LABEL):
            digit = txt("1" if same else "0", size=26,
                        color=C_GOOD if same else C_BAD, weight=BOLD)
            digit.move_to(dot.get_center() + normalize(dot.get_center() - V_POS) * 0.55)
            digits.add(digit)

        with self.voiceover(text=VO["check"]):
            self.play(Write(formula[0]), Write(formula[1]), run_time=1.0)
            # Công thức lộ dần SONG SONG với việc kiểm tra từng hàng xóm: mỗi nhịp
            # vừa sáng một nót vừa viết thêm một mảnh công thức, theo đúng thứ tự
            # đọc — đếm từng hàng xóm, cộng trên cả tập, rồi lấy trung bình. Bản cũ
            # kiểm hết bốn nót rồi mới viết công thức nên hai thứ rời nhau.
            reveal_order = [formula[4], formula[3], formula[2], None]
            for (dot, digit, same), part in zip(zip(u_dots, digits, SAME_LABEL), reveal_order):
                anims = [
                    Indicate(dot, color=C_GOOD if same else C_BAD, scale_factor=1.5),
                    FadeIn(digit, scale=0.6),
                ]
                if part is not None:
                    anims.append(Write(part))
                self.play(*anims, run_time=1.0)
                self.wait(0.2)

        # ------------------------------------------------------------------
        # Nhịp 3 — Thay số: h_v = (1+1+1+0)/4 = 0.75
        # ------------------------------------------------------------------
        numeric = MathTex(r"h_v", r"=", r"\frac{1 + 1 + 1 + 0}{4}", r"=", r"0.75",
                          font_size=40)
        numeric[0].set_color(ACCENT)
        numeric[4].set_color(C_GOOD)
        numeric.move_to(formula).align_to(formula, RIGHT)
        if numeric.width > 6.4:
            numeric.scale_to_fit_width(6.4)

        with self.voiceover(text=VO["value"]):
            self.play(TransformMatchingTex(formula, numeric), run_time=1.6)
            self.play(Indicate(numeric[4], color=C_GOOD, scale_factor=1.25), run_time=1.0)

        # ------------------------------------------------------------------
        # Nhịp 4 — Homophily cao: message nhất quán, GNN đúng.
        # ------------------------------------------------------------------
        gnn_box = labeled_box("GNN", C_GNN, width=2.3, height=0.95)
        gnn_box.next_to(numeric, DOWN, buff=1.5)
        arrow_in = Arrow(v_dot.get_right(), gnn_box.get_left(), buff=0.25,
                         stroke_width=3, color=MUTED,
                         max_tip_length_to_length_ratio=0.06)
        ok = check(color=C_GOOD, size=0.5).next_to(gnn_box, RIGHT, buff=0.4)
        caption_hi = txt("High homophily → consistent neighborhood",
                         size=23, color=C_GOOD).to_edge(DOWN, buff=0.55)

        with self.voiceover(text=VO["high"]):
            self.play(FadeOut(digits), run_time=0.6)
            self.play(FadeIn(gnn_box), GrowArrow(arrow_in), run_time=1.0)
            self.play(*self.messages(u_dots, [C_GNN] * 4), run_time=1.8)
            self.play(Flash(v_dot, color=C_GNN, flash_radius=0.5), run_time=0.8)
            self.play(FadeIn(ok, scale=0.6), run_time=0.8)
            self.play(FadeIn(caption_hi, shift=UP * 0.2), run_time=0.9)
            self.play(*self.messages(u_dots, [C_GNN] * 4), run_time=1.8)

        # ------------------------------------------------------------------
        # Nhịp 5 — Homophily thấp: hàng xóm khác lớp, GNN sai.
        # ------------------------------------------------------------------
        low = MathTex(r"h_v", r"=", r"\frac{0 + 0 + 0 + 0}{4}", r"=", r"0.00",
                      font_size=40)
        low[0].set_color(ACCENT)
        low[4].set_color(C_BAD)
        low.move_to(numeric).align_to(numeric, RIGHT)
        if low.width > 6.4:
            low.scale_to_fit_width(6.4)
        bad = cross(color=C_BAD, size=0.42).next_to(gnn_box, RIGHT, buff=0.45)
        caption_lo = txt("Low homophily → heterophilous neighborhood",
                         size=23, color=C_BAD).to_edge(DOWN, buff=0.55)

        with self.voiceover(text=VO["low"]):
            self.play(FadeOut(caption_hi), FadeOut(ok), run_time=0.5)
            self.play(*[d.animate.set_color(C_BAD)
                        for d, same in zip(u_dots, SAME_LABEL) if same], run_time=1.4)
            self.play(TransformMatchingTex(numeric, low), run_time=1.3)
            self.play(*self.messages(u_dots, [C_BAD] * 4), run_time=1.8)
            self.play(v_dot.animate.set_color(interpolate_color(C_GNN, C_BAD, 0.55)),
                      run_time=0.8)
            self.play(FadeIn(bad, scale=0.6), run_time=0.7)
            self.play(FadeIn(caption_lo, shift=UP * 0.2), run_time=0.9)

        self.wait(1.2)

    # ----------------------------------------------------------------------
    def messages(self, dots, colors):
        """Thông điệp chạy từ hàng xóm về node trung tâm."""
        return [
            ShowPassingFlash(
                Line(dot.get_center(), V_POS, stroke_width=6, color=color),
                time_width=0.45,
            )
            for dot, color in zip(dots, colors)
        ]


def spokes(center, count, angle_start, angle_end, length=0.7,
           color=C_EDGE, dot_color=MUTED):
    """Các cạnh phụ toả ra từ một node, để thể hiện degree của node đó."""
    group = VGroup()
    if count <= 0:
        return group
    for i in range(count):
        t = 0.5 if count == 1 else i / (count - 1)
        angle = angle_start + (angle_end - angle_start) * t
        tip = center + np.array([np.cos(angle), np.sin(angle), 0.0]) * length
        group.add(
            Line(center, tip, stroke_width=2.0, color=color, z_index=-1),
            Dot(tip, radius=0.075, color=dot_color),
        )
    return group


class S3_02_RelativeDegree(GlanceScene):
    """Cảnh 2 — Relative degree."""

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        head = heading("Signal 2: Relative degree", color=ACCENT).to_edge(UP, buff=0.75)

        # v có degree 2; hàng xóm u1 degree 5, u2 degree 3.
        v_pos = LEFT * 4.0 + DOWN * 0.2
        u1_pos = v_pos + RIGHT * 1.9 + UP * 1.25
        u2_pos = v_pos + RIGHT * 1.9 + DOWN * 1.25

        v_dot = Dot(v_pos, radius=0.24, color=C_HIGHLIGHT)
        u1_dot = Dot(u1_pos, radius=0.20, color=MUTED)
        u2_dot = Dot(u2_pos, radius=0.20, color=MUTED)
        e1 = Line(v_pos, u1_pos, stroke_width=2.6, color=C_EDGE, z_index=-1)
        e2 = Line(v_pos, u2_pos, stroke_width=2.6, color=C_EDGE, z_index=-1)

        # u1 còn 4 cạnh nữa (tổng 5), u2 còn 2 cạnh nữa (tổng 3).
        u1_spokes = spokes(u1_pos, 4, -PI / 6, PI / 2 + 0.3)
        u2_spokes = spokes(u2_pos, 2, -PI / 2 - 0.2, 0.0)

        # Ký hiệu bậc dựng bằng MathTex: viết "d_v" bằng txt() thì gạch dưới hiện
        # nguyên xi thay vì thành chỉ số dưới.
        v_deg = MathTex(r"d_v = 2", font_size=30, color=C_HIGHLIGHT)
        v_deg.next_to(v_dot, LEFT, buff=0.25)
        u1_deg = MathTex(r"d_u = 5", font_size=27, color=INK).next_to(u1_dot, UP, buff=0.55)
        u2_deg = MathTex(r"d_u = 3", font_size=27, color=INK).next_to(u2_dot, DOWN, buff=0.55)

        note = txt("Not just: how many edges does this node have?", size=21, color=MUTED)
        note.to_edge(DOWN, buff=0.75)

        with self.voiceover(text=VO["rd_intro"]):
            self.play(Write(head), run_time=1.2)
            self.play(GrowFromCenter(v_dot), FadeIn(v_deg), run_time=0.9)
            self.play(Create(e1), GrowFromCenter(u1_dot),
                      Create(e2), GrowFromCenter(u2_dot), run_time=1.0)
            self.play(Create(u1_spokes), FadeIn(u1_deg), run_time=1.0)
            self.play(Create(u2_spokes), FadeIn(u2_deg), run_time=0.9)
            self.play(FadeIn(note, shift=UP * 0.15), run_time=0.8)

        # --- Công thức, tô sáng từng thành phần ---
        formula = MathTex(
            r"\bar{d}_v", r"=", r"\frac{1}{|\mathcal{N}(v)|}",
            r"\sum_{u \in \mathcal{N}(v)}", r"\sqrt{\frac{d_v + 1}{d_u + 1}}",
            font_size=40,
        )
        formula[0].set_color(ACCENT)
        formula.to_edge(RIGHT, buff=1.0).shift(UP * 0.9)
        if formula.width > 6.2:
            formula.scale_to_fit_width(6.2)

        with self.voiceover(text=VO["rd_formula"]):
            self.play(FadeOut(note), run_time=0.4)
            self.play(Write(formula), run_time=1.8)
            self.play(formula[4].animate.set_color(C_HIGHLIGHT),
                      Indicate(v_deg, color=C_HIGHLIGHT, scale_factor=1.2), run_time=1.0)
            self.play(Indicate(u1_deg, color=C_LLM, scale_factor=1.2),
                      Indicate(u2_deg, color=C_LLM, scale_factor=1.2), run_time=1.0)
            self.play(formula[4].animate.set_color(INK),
                      formula[2].animate.set_color(C_GOOD),
                      formula[3].animate.set_color(C_GOOD), run_time=1.0)
            self.play(formula[2].animate.set_color(INK),
                      formula[3].animate.set_color(INK), run_time=0.6)

        # --- Thanh đo quanh mốc 1 ---
        scale_line = NumberLine(
            x_range=[0.4, 1.6, 0.2], length=5.6, include_numbers=True,
            font_size=20, color=C_EDGE,
            decimal_number_config={"num_decimal_places": 1},
        )
        scale_line.next_to(formula, DOWN, buff=1.5).align_to(formula, RIGHT)
        scale_line.shift(RIGHT * 0.3)
        one_mark = Line(UP * 0.28, DOWN * 0.28, color=INK, stroke_width=3)
        one_mark.move_to(scale_line.n2p(1.0))
        less = txt("less connected than its neighbors", size=16, color=C_BAD)
        less.next_to(scale_line.n2p(0.62), UP, buff=0.45)
        more = txt("more connected than its neighbors", size=16, color=C_GOOD)
        more.next_to(scale_line.n2p(1.38), UP, buff=0.45)
        marker = Dot(scale_line.n2p(1.0), radius=0.13, color=C_HIGHLIGHT)

        with self.voiceover(text=VO["rd_scale"]):
            self.play(Create(scale_line), Create(one_mark), run_time=1.1)
            self.play(FadeIn(marker), run_time=0.4)
            self.play(marker.animate.move_to(scale_line.n2p(1.38)),
                      FadeIn(more), run_time=1.2)
            self.play(marker.animate.move_to(scale_line.n2p(0.62)),
                      FadeIn(less), run_time=1.2)

        # --- Thay số cho ví dụ ---
        numeric = MathTex(
            r"\bar{d}_v", r"=", r"\tfrac{1}{2}\left(\sqrt{\tfrac{3}{6}} + \sqrt{\tfrac{3}{4}}\right)",
            r"\approx", r"0.79",
            font_size=38,
        )
        numeric[0].set_color(ACCENT)
        numeric[4].set_color(C_BAD)
        numeric.move_to(formula).align_to(formula, RIGHT)
        if numeric.width > 6.2:
            numeric.scale_to_fit_width(6.2)

        caveat = txt("Low relative degree ≠ low absolute degree",
                     size=19, color=MUTED).to_edge(DOWN, buff=0.75)

        with self.voiceover(text=VO["rd_value"]):
            self.play(TransformMatchingTex(formula, numeric), run_time=1.5)
            self.play(marker.animate.move_to(scale_line.n2p(0.79)),
                      Indicate(numeric[4], color=C_BAD, scale_factor=1.2), run_time=1.2)
            self.play(FadeIn(caveat, shift=UP * 0.15), run_time=0.8)

        self.wait(1.0)


class S3_03_Complementary(GlanceScene):
    """Cảnh 3 — GNN và LLM bổ sung cho nhau."""

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        head = heading("GNN and LLM excel in different regions", color=ACCENT)
        head.to_edge(UP, buff=0.7)

        chart = line_chart(
            H_SERIES, H_BINS, y_range=(0.0, 1.0, 0.25),
            width=7.4, height=3.5, bars=H_COUNTS, bar_label="Node count",
            x_label="Local homophily bin",
        )
        chart.legend.next_to(chart.axes, RIGHT, buff=0.5).shift(DOWN * 0.55)
        chart.shift(DOWN * 0.4 + LEFT * 0.35)
        ylab = txt("Accuracy", size=16, color=MUTED).rotate(PI / 2)
        ylab.next_to(chart.axes, LEFT, buff=0.3)

        with self.voiceover(text=VO["cp_setup"]):
            self.play(Write(head), run_time=1.2)
            self.play(Create(chart.axes), FadeIn(chart.ticks), FadeIn(ylab), run_time=1.2)
            self.play(FadeIn(chart.bars), run_time=0.5)
            for spec in H_SERIES:
                plot = chart.plots[spec["name"]]
                self.play(Create(plot.path), FadeIn(plot.dots), run_time=0.75)
            self.play(FadeIn(chart.legend), run_time=0.5)

        # --- Quét từ vùng homophily cao sang thấp ---
        band = Rectangle(
            width=chart.axes.x_length / len(H_BINS), height=chart.axes.y_length + 0.3,
            stroke_width=0, fill_color=INK, fill_opacity=0.10,
        )
        band.move_to([chart.axes.c2p(4.5, 0.5)[0], chart.axes.get_center()[1], 0])
        tag_gnn = txt("GNN wins", size=20, color=C_GNN)
        tag_llm = txt("LLM wins", size=20, color=C_LLM)

        with self.voiceover(text=VO["cp_trend"]):
            self.play(FadeIn(band), run_time=0.5)
            tag_gnn.next_to(band, UP, buff=0.2)
            self.play(FadeIn(tag_gnn),
                      Indicate(chart.plots["GCNII (Enh.)"].dots[4], color=C_GNN,
                               scale_factor=2.2), run_time=1.2)
            self.play(band.animate.move_to(
                [chart.axes.c2p(2.5, 0.5)[0], chart.axes.get_center()[1], 0]),
                FadeOut(tag_gnn), run_time=1.4)
            self.play(band.animate.move_to(
                [chart.axes.c2p(0.5, 0.5)[0], chart.axes.get_center()[1], 0]),
                run_time=1.4)
            tag_llm.next_to(band, UP, buff=0.2)
            self.play(FadeIn(tag_llm),
                      Indicate(chart.plots["LLM"].dots[0], color=C_LLM,
                               scale_factor=2.2), run_time=1.2)

        # --- +20.4% ở bin thấp nhất ---
        p_llm = chart.point("LLM", 0)
        p_gnn = chart.point("GCNII (Enh.)", 0)
        brace = BraceBetweenPoints(p_gnn, p_llm, direction=LEFT, color=C_GOOD)
        gain = txt("+20.4%", size=26, color=C_GOOD, weight=BOLD)
        gain.next_to(p_llm, UP, buff=0.2)
        gain_note = txt("Cora hard-node group only, not the full dataset",
                        size=18, color=MUTED).to_edge(DOWN, buff=0.72)

        with self.voiceover(text=VO["cp_gain"]):
            self.play(FadeOut(band), FadeOut(tag_llm), run_time=0.4)
            self.play(GrowFromCenter(brace), FadeIn(gain), run_time=1.1)
            self.play(FadeIn(gain_note), run_time=0.8)

        # --- Heatmap tương tác hai chiều ---
        with self.voiceover(text=VO["cp_interact"]):
            self.play(FadeOut(VGroup(chart, ylab, brace, gain, gain_note)), run_time=0.7)
            grid, axes_labels = self.heatmap()
            self.play(FadeIn(axes_labels), run_time=0.5)
            self.play(LaggedStart(*[FadeIn(c) for c in grid], lag_ratio=0.05), run_time=1.8)

            spread = txt("30.1% across structural subpopulations",
                         size=24, color=INK, weight=BOLD)
            spread.next_to(grid, RIGHT, buff=0.7)
            caveat = txt("difference BETWEEN structural groups,\nnot LLM always beating GNN by 30.1%",
                         size=17, color=MUTED, line_spacing=0.8)
            caveat.next_to(spread, DOWN, buff=0.35)
            self.play(FadeIn(spread), run_time=0.7)
            self.play(FadeIn(caveat), run_time=0.7)

        self.wait(1.0)

    # ----------------------------------------------------------------------
    def heatmap(self, n=5, cell=0.72):
        """Lưới 2 chiều: trục ngang local homophily, trục dọc relative degree.
        Góc thấp–thấp đỏ (GNN khó), góc cao–cao xanh (GNN thuận lợi)."""
        grid = VGroup()
        for i in range(n):          # cột: homophily
            for j in range(n):      # hàng: relative degree
                t = (i / (n - 1)) * 0.7 + (j / (n - 1)) * 0.3
                square = Square(
                    side_length=cell, stroke_width=1, stroke_color=BG,
                    fill_color=interpolate_color(C_BAD, C_GOOD, t), fill_opacity=0.85,
                )
                square.move_to(RIGHT * i * cell + UP * j * cell)
                grid.add(square)
        grid.move_to(LEFT * 3.2 + DOWN * 0.3)

        x_lab = txt("Local homophily →", size=17, color=MUTED)
        x_lab.next_to(grid, DOWN, buff=0.25)
        y_lab = txt("Relative degree →", size=17, color=MUTED).rotate(PI / 2)
        y_lab.next_to(grid, LEFT, buff=0.25)
        corner_lo = txt("hard for GNN", size=15, color=C_BAD)
        corner_lo.next_to(grid, DOWN, buff=0.25).align_to(grid, LEFT).shift(DOWN * 0.4)
        corner_hi = txt("favorable for GNN", size=15, color=C_GOOD)
        corner_hi.next_to(grid, UP, buff=0.2).align_to(grid, RIGHT)
        return grid, VGroup(x_lab, y_lab, corner_lo, corner_hi)


class S3_04_EstimatedHomophily(GlanceScene):
    """Cảnh 4 — Từ true homophily đến estimated homophily."""

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        # Tiêu đề ghép chữ với MathTex để "h_v" ra đúng chỉ số dưới, thay vì hiện
        # nguyên dấu gạch dưới như khi viết bằng txt().
        head = VGroup(
            heading("Problem:", color=ACCENT),
            MathTex(r"h_v", font_size=46, color=ACCENT),
            heading("requires true labels", color=ACCENT),
        ).arrange(RIGHT, buff=0.24).to_edge(UP, buff=0.75)

        true_h = MathTex(
            r"h_v = \frac{1}{|\mathcal{N}(v)|}\sum_{u \in \mathcal{N}(v)}"
            r"\mathbf{1}[", r"y_u", r"=", r"y_v", r"]",
            font_size=40,
        )
        true_h.move_to(UP * 1.4)
        if true_h.width > 8.0:
            true_h.scale_to_fit_width(8.0)

        # Nhãn thật biến thành dấu hỏi.
        q_u = txt("?", size=34, color=C_BAD, weight=BOLD).move_to(true_h[1])
        q_v = txt("?", size=34, color=C_BAD, weight=BOLD).move_to(true_h[3])

        lock = VGroup(
            cross(color=C_BAD, size=0.2),
            txt("Requires ground-truth labels", size=22, color=C_BAD),
        ).arrange(RIGHT, buff=0.25)
        lock.next_to(true_h, DOWN, buff=0.9)
        lock_frame = panel(lock, color=C_BAD, buff=0.3)

        with self.voiceover(text=VO["eh_problem"]):
            self.play(Write(head), run_time=1.2)
            self.play(Write(true_h), run_time=1.6)
            self.play(
                true_h[1].animate.set_opacity(0), true_h[3].animate.set_opacity(0),
                FadeIn(q_u, scale=0.6), FadeIn(q_v, scale=0.6), run_time=1.1,
            )
            self.play(FadeIn(lock_frame), FadeIn(lock), run_time=0.9)

        # --- MLP Q dự đoán nhãn tạm thời ---
        # Hai đầu là ký hiệu toán nên dựng bằng MathTex; "MLP Q" là tên khối, giữ
        # chữ thường.
        flow = pipeline(
            [
                (MathTex(r"x_v", font_size=32, color=MUTED), MUTED),
                ("MLP Q", C_ROUTER),
                (MathTex(r"\hat{y}_v", font_size=32, color=C_HIGHLIGHT), C_HIGHLIGHT),
            ],
            box_w=1.9, box_h=0.85, buff=0.5, text_size=20,
        )
        flow.next_to(head, DOWN, buff=0.7)

        # Node thật giữ viền xám, ruột là nhãn dự đoán.
        demo = VGroup()
        for i, pred in enumerate([C_GNN, C_GNN, C_BAD, C_GNN]):
            dot = Dot(radius=0.19, color=pred)
            ring = Circle(radius=0.26, color=MUTED, stroke_width=2.5).move_to(dot)
            demo.add(VGroup(ring, dot))
        demo.arrange(RIGHT, buff=0.5).next_to(flow, DOWN, buff=0.7)
        demo_note = txt("gray outline = true node · fill = predicted label",
                        size=17, color=MUTED).next_to(demo, DOWN, buff=0.3)

        with self.voiceover(text=VO["eh_mlp"]):
            self.play(FadeOut(VGroup(true_h, q_u, q_v, lock, lock_frame)), run_time=0.6)
            self.play(LaggedStart(*[GrowFromCenter(b) for b in flow.boxes],
                                  lag_ratio=0.25), run_time=1.2)
            self.play(*[GrowArrow(a) for a in flow.arrows], run_time=0.6)
            self.play(LaggedStart(*[FadeIn(d, scale=0.7) for d in demo],
                                  lag_ratio=0.15), run_time=1.2)
            self.play(FadeIn(demo_note), run_time=0.6)

        # --- Công thức estimated homophily ---
        est_h = MathTex(
            r"\hat{h}_v = \frac{1}{|\mathcal{N}(v)|}\sum_{u \in \mathcal{N}(v)}"
            r"\mathbf{1}[\hat{y}_u = \hat{y}_v]",
            font_size=40, color=C_ROUTER,
        )
        est_h.next_to(demo_note, DOWN, buff=0.7)
        if est_h.width > 8.0:
            est_h.scale_to_fit_width(8.0)

        with self.voiceover(text=VO["eh_estimate"]):
            self.play(Write(est_h), run_time=1.8)
            self.play(Indicate(est_h, color=C_ROUTER, scale_factor=1.05), run_time=1.0)

        # --- Bảng xếp hạng rút gọn ---
        rows = [
            ("h_v", "1.03", "unavailable at inference", MUTED),
            ("ĥ_v", "3.22", "best label-free signal", C_GOOD),
            ("uncertainty", "3.28", "label-free", MUTED),
        ]
        # Ba cột căn theo mốc x cố định để thẳng hàng, thay vì ép bề rộng ô.
        table = VGroup()
        for name, rank, note, color in rows:
            row = VGroup(
                txt(name, size=22, color=color),
                txt(rank, size=22, color=color, weight=BOLD),
                txt(note, size=18, color=MUTED),
            )
            row[1].move_to(row[0], aligned_edge=LEFT).shift(RIGHT * 2.4)
            row[2].move_to(row[0], aligned_edge=LEFT).shift(RIGHT * 3.6)
            table.add(row)
        table.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        table.move_to(DOWN * 0.35)
        title_row = txt("Mean rank under NCS routing (lower is better)",
                        size=20, color=INK, weight=BOLD)
        title_row.next_to(table, UP, buff=0.55).align_to(table, LEFT)
        highlight = panel(table[1], color=C_GOOD, buff=0.18)
        rank_head = heading("Routing signal ranking", color=ACCENT).move_to(head)

        with self.voiceover(text=VO["eh_rank"]):
            self.play(FadeOut(VGroup(flow, demo, demo_note, est_h)), run_time=0.6)
            self.play(FadeTransform(head, rank_head), run_time=0.8)
            self.play(FadeIn(title_row), run_time=0.6)
            self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in table],
                                  lag_ratio=0.3), run_time=1.6)
            self.play(Create(highlight), run_time=0.9)

        self.wait(1.0)


class S3_05_Bridge(GlanceScene):
    """Cảnh kết — chuyển sang Task 4."""

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()

        sig_h = labeled_box("Local homophily", C_HIGHLIGHT, width=3.4, height=0.85)
        sig_d = labeled_box("Relative degree", C_LLM, width=3.4, height=0.85)
        signals = VGroup(sig_h, sig_d).arrange(DOWN, buff=0.8).to_edge(LEFT, buff=0.9)
        for box in signals:
            box[1].scale_to_fit_width(min(box[1].width, 3.0))
            box[1].move_to(box[0])

        difficulty = labeled_box("Structural difficulty", C_ROUTER, width=3.6, height=1.0)
        difficulty[1].scale_to_fit_width(3.2)
        difficulty[1].move_to(difficulty[0])
        difficulty.move_to(ORIGIN + LEFT * 0.2)

        arrows_in = VGroup(*[
            Arrow(box.get_right(), difficulty.get_left(), buff=0.15,
                  stroke_width=3, color=MUTED, max_tip_length_to_length_ratio=0.09)
            for box in signals
        ])

        gnn_box = labeled_box("GNN", C_GNN, width=2.0, height=0.8)
        llm_box = labeled_box("LLM", C_LLM, width=2.0, height=0.8)
        models = VGroup(gnn_box, llm_box).arrange(DOWN, buff=0.9).to_edge(RIGHT, buff=1.2)
        arrows_out = VGroup(*[
            Arrow(difficulty.get_right(), box.get_left(), buff=0.15,
                  stroke_width=3, color=MUTED, max_tip_length_to_length_ratio=0.09)
            for box in models
        ])
        note = txt("Does not predict labels: only identifies nodes hard for GNN",
                   size=20, color=MUTED).to_edge(DOWN, buff=0.75)

        with self.voiceover(text=VO["end_summary"]):
            self.play(FadeIn(signals, shift=RIGHT * 0.2), run_time=1.0)
            self.play(GrowArrow(arrows_in[0]), GrowArrow(arrows_in[1]),
                      FadeIn(difficulty, scale=0.8), run_time=1.3)
            self.play(GrowArrow(arrows_out[0]), GrowArrow(arrows_out[1]),
                      FadeIn(models), run_time=1.2)
            self.play(FadeIn(note), run_time=0.7)

        # --- Ngưỡng cố định bị gạch bỏ, tín hiệu đi vào router học được ---
        threshold = VGroup(
            txt("Fixed threshold", size=22, color=MUTED),
            MathTex(r"h_v < 0.5 \;\Rightarrow\; \text{query LLM}",
                    font_size=27, color=MUTED),
        ).arrange(DOWN, buff=0.2)
        thr_frame = panel(threshold, color=MUTED, buff=0.3)
        thr_group = VGroup(thr_frame, threshold).move_to(difficulty)
        strike = Line(thr_frame.get_corner(DL), thr_frame.get_corner(UR),
                      color=C_BAD, stroke_width=6)

        # Cùng bề rộng với khối difficulty để mũi tên đã vẽ vẫn chạm đúng mép.
        router = labeled_box("Learnable Router", C_ROUTER, width=3.6, height=1.1)
        router[1].scale_to_fit_width(3.1)
        router[1].move_to(router[0])
        router.move_to(difficulty)

        with self.voiceover(text=VO["end_router"]):
            self.play(FadeOut(VGroup(models, arrows_out, note, difficulty)), run_time=0.6)
            self.play(FadeIn(thr_group), run_time=0.8)
            self.play(Create(strike), run_time=0.8)
            self.play(FadeOut(VGroup(thr_group, strike)), run_time=0.6)
            self.play(FadeIn(router, scale=0.85), run_time=1.0)
            self.play(*[Indicate(a, color=C_ROUTER, scale_factor=1.05) for a in arrows_in],
                      run_time=1.0)
            self.play(*self.pulses(signals, router), run_time=1.6)

        # --- Dẫn sang phần năm routing signals (vẫn trong section này) ---
        next_line = txt("Next: the five signals the router reads from each node",
                        size=22, color=C_ROUTER, weight=BOLD)
        if next_line.width > 9.5:
            next_line.scale_to_fit_width(9.5)

        with self.voiceover(text=VO["end_next"]):
            self.play(FadeOut(VGroup(signals, arrows_in)), run_time=0.5)
            self.play(router.animate.move_to(UP * 0.6), run_time=0.8)
            next_line.next_to(router, DOWN, buff=0.9)
            self.play(FadeIn(next_line, shift=UP * 0.15), run_time=0.9)
            self.play(FadeOut(VGroup(router, next_line)), run_time=0.8)

        self.wait(0.6)

    # ----------------------------------------------------------------------
    def pulses(self, signals, target):
        """Tín hiệu chạy từ hai khối bên trái vào router."""
        return [
            ShowPassingFlash(
                Line(box.get_right(), target.get_left(), stroke_width=6, color=C_ROUTER),
                time_width=0.5,
            )
            for box in signals
        ]


# ==========================================================================
# Phần bổ sung — Step 1: năm routing signals (§5.1.1, tr.5–6)
#
# Helper dùng chung cho các cảnh 6–12. Giữ ở đây thay vì glance_style.py vì
# chỉ phần này dùng tới; cùng quy ước với spokes() ở trên.
# ==========================================================================

def signal_stack(width=3.5, height=0.62, buff=0.24, text_size=20):
    """Cột năm khối signal — dùng lại ở cảnh mở đầu và cảnh kết."""
    stack = VGroup()
    for name, color, _ in SIGNALS:
        box = labeled_box(name, color, width=width, height=height)
        box[1].set(font_size=text_size)
        if box[1].width > width - 0.3:
            box[1].scale_to_fit_width(width - 0.3)
        box[1].move_to(box[0])
        stack.add(box)
    stack.arrange(DOWN, buff=buff)
    return stack


def step_head(scene, number, title):
    """Header đánh số cho các cảnh 6–19 (cùng ngôn ngữ hình với section 4).

    Không phải class: `build.sh` tìm scene bằng cách grep `^class`, nên mọi thứ
    dùng chung phải là hàm thường.
    """
    head = step_header(number, title)
    scene.play(FadeIn(head, shift=DOWN * 0.08), run_time=0.42)
    return head


class S3_06_FiveSignals(GlanceScene):
    """Cảnh 6 — từ phân tích sang kiến trúc: năm routing signals."""

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()

        v_dot = Dot(LEFT * 4.9 + DOWN * 0.25, radius=0.26, color=INK)
        v_lab = txt("v", size=24, color=INK).next_to(v_dot, DOWN, buff=0.2)

        stack = signal_stack().move_to(RIGHT * 0.1 + DOWN * 0.25)
        links = VGroup(*[
            Line(v_dot.get_center(), box[0].get_left(), buff=0.32,
                 stroke_width=1.8, color=C_EDGE, z_index=-1)
            for box in stack
        ])

        with self.voiceover(text=VO["fs_open"]):
            step_head(self, 6, "Step 1: five routing signals")
            self.play(GrowFromCenter(v_dot), FadeIn(v_lab), run_time=0.9)
            for box, link in zip(stack, links):
                self.play(Create(link), FadeIn(box, shift=RIGHT * 0.15), run_time=0.62)

        # Mỗi signal trả lời một câu hỏi khác nhau về node.
        roles = VGroup()
        for box, (_, color, role) in zip(stack, SIGNALS):
            roles.add(txt(role, size=19, color=color).next_to(box, RIGHT, buff=0.5))

        with self.voiceover(text=VO["fs_roles"]):
            self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in roles],
                                  lag_ratio=0.25), run_time=2.4)
            self.play(*[
                ShowPassingFlash(
                    Line(v_dot.get_center(), box[0].get_left(),
                         stroke_width=4, color=color),
                    time_width=0.5,
                )
                for box, (_, color, _) in zip(stack, SIGNALS)
            ], run_time=1.2)

        self.wait(0.8)


class S3_07_ThreeSources(GlanceScene):
    """Cảnh 7 — ba nguồn thông tin nuôi năm signal (nguyên S4_03)."""

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        step_head(self, 7, "Three information sources for Node A")

        node_A = avatar_node("A", target=True, radius=0.38).move_to(LEFT * 5.30)
        node_label = txt("NODE A", 21, MUTED, BOLD).next_to(node_A, DOWN, buff=0.20)
        cards = VGroup(
            equation_card(r"z_G(A),\ p_{H,A},\ u_A", "GNN: graph + node features", 5.75, 1.16, True),
            equation_card(r"p_{Q,A}=Q(x_A)", "MLP Q: node feature only", 5.75, 1.16),
            equation_card(r"\mathcal I_A^{\mathrm{direct}}=(x_A,d_A)", "direct information", 5.75, 1.16),
        )
        cards.arrange(DOWN, buff=0.24).move_to(RIGHT * 2.25)
        branch_x = -3.70
        trunk_in = Line(node_A.get_right(), [branch_x, 0, 0], color=MUTED, stroke_width=2.1)
        trunk = Line([branch_x, cards[2].get_center()[1], 0], [branch_x, cards[0].get_center()[1], 0],
                     color=MUTED, stroke_width=2.0)
        branches = VGroup(*[
            small_arrow([branch_x, card.get_center()[1], 0], card.get_left(),
                        color=MUTED, stroke_width=2.0, buff=0.08)
            for card in cards
        ])

        with self.voiceover(text=VO["ts_intro"]):
            self.play(GrowFromCenter(node_A), run_time=0.4)
            self.play(FadeIn(node_label), Create(trunk_in), Create(trunk), run_time=0.65)

        for branch, card, key in zip(branches, cards, ("ts_gnn", "ts_mlp", "ts_direct")):
            with self.voiceover(text=VO[key]):
                self.play(GrowArrow(branch), FadeIn(card, shift=RIGHT * 0.08), run_time=0.52)

        with self.voiceover(text=VO["ts_close"]):
            pass
        self.wait(0.6)


class S3_08_InitialState(GlanceScene):
    """Cảnh 8 — trạng thái ban đầu h_A^(0) = x_A (nguyên S4_04)."""

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        step_head(self, 8, "The initial state as a substitution")

        equation = mt(r"h_A^{(0)}=x_A", 68).move_to(UP * 0.45)
        step_label = txt("DEFINITION", 22, MUTED, BOLD).next_to(equation, DOWN, buff=0.35)
        timeline_line = Line(LEFT * 1.25, RIGHT * 1.25, color=C_EDGE, stroke_width=2.0).move_to(DOWN * 1.15)
        dots = VGroup(*[
            Circle(radius=0.13, stroke_color=MUTED, stroke_width=1.7,
                   fill_color=INK if i == 0 else BG, fill_opacity=1)
            for i in range(3)
        ]).arrange(RIGHT, buff=0.85).move_to(timeline_line)
        step_numbers = VGroup(*[
            txt(str(i), 17, BG if i == 1 else MUTED, BOLD).move_to(dot)
            for i, dot in enumerate(dots, start=1)
        ])

        with self.voiceover(text=VO["is_layer0"]):
            self.play(
                Write(equation), FadeIn(step_label), Create(timeline_line),
                FadeIn(dots), FadeIn(step_numbers),
                run_time=0.85,
            )

        feature_example = mt(r"x_A=[0.8,-0.1,0.5]", 62).move_to(equation)
        feature_label = txt("EXAMPLE FEATURE", 22, MUTED, BOLD).move_to(step_label)
        with self.voiceover(text=VO["is_example"]):
            self.play(
                FadeOut(equation, shift=UP * 0.06),
                Transform(step_label, feature_label),
                dots[0].animate.set_fill(BG), dots[1].animate.set_fill(INK),
                step_numbers[0].animate.set_color(MUTED), step_numbers[1].animate.set_color(BG),
                run_time=0.45,
            )
            self.play(FadeIn(feature_example, shift=UP * 0.06), run_time=0.45)
        equation = feature_example

        substituted = mt(r"h_A^{(0)}=[0.8,-0.1,0.5]", 62).move_to(equation)
        result_label = txt("INITIAL HIDDEN STATE", 22, INK, BOLD).move_to(step_label)
        with self.voiceover(text=VO["is_noneighbor"]):
            self.play(
                FadeOut(equation, shift=UP * 0.06),
                Transform(step_label, result_label),
                dots[1].animate.set_fill(BG), dots[2].animate.set_fill(INK),
                step_numbers[1].animate.set_color(MUTED), step_numbers[2].animate.set_color(BG),
                run_time=0.48,
            )
            self.play(FadeIn(substituted, shift=UP * 0.06), run_time=0.47)

        note = takeaway_chip("At layer 0, the hidden state equals the original text feature")
        self.play(FadeIn(note, shift=UP * 0.08), run_time=0.42)
        self.wait(0.9)


class S3_09_Aggregate(GlanceScene):
    """Cảnh 9 — AGGREGATE gộp hàng xóm (nguyên S4_05)."""

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        step_head(self, 9, "AGGREGATE: combine the neighbors")

        summary = fit_width(mt(
            r"m_A^{(\ell)}=\operatorname{AGGREGATE}^{(\ell)}"
            r"\!\left(\{h_u^{(\ell-1)}\mid u\in N(A)\}\right)",
            46,
        ), 11.8).move_to(UP * 0.20)
        with self.voiceover(text=VO["ag_open"]):
            self.play(Write(summary), run_time=1.0)
        self.wait(0.35)
        self.play(summary.animate.scale(0.76).move_to(DOWN * 2.35), run_time=0.65)

        state_specs = [("B", r"[1,0]"), ("C", r"[0,1]"), ("D", r"[1,1]"), ("E", r"[0,0]")]
        states = VGroup(*[
            VGroup(
                avatar_node(label, radius=0.21),
                mt(rf"h_{{{label}}}^{{(\ell-1)}}={value}", 34),
            ).arrange(RIGHT, buff=0.24)
            for label, value in state_specs
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.24).move_to(LEFT * 4.65 + UP * 0.35)
        aggregate = module_box("AGGREGATE", "example: mean", width=2.65, height=1.12,
                               emphasized=True).move_to(LEFT * 0.40 + UP * 0.30)
        message = equation_card(r"m_A^{(\ell)}=[0.5,0.5]", "neighbor message", 3.35, 1.12,
                                True).move_to(RIGHT * 4.35 + UP * 0.30)
        in_arrows = VGroup(*[
            small_arrow(state.get_right(), aggregate.get_left(), color=C_EDGE, stroke_width=1.5, buff=0.09)
            for state in states
        ])
        out_arrow = small_arrow(aggregate.get_right(), message.get_left(), color=MUTED,
                                stroke_width=2.1, buff=0.10)

        with self.voiceover(text=VO["ag_collect"]):
            self.play(LaggedStart(*[FadeIn(state, shift=RIGHT * 0.08) for state in states],
                                  lag_ratio=0.10), run_time=0.75)
        with self.voiceover(text=VO["ag_combine"]):
            self.play(*[GrowArrow(arrow) for arrow in in_arrows], FadeIn(aggregate), run_time=0.72)
            self.play(GrowArrow(out_arrow), FadeIn(message, shift=RIGHT * 0.08), run_time=0.58)

        detailed = fit_width(mt(
            r"m_A^{(\ell)}=\frac{[1,0]+[0,1]+[1,1]+[0,0]}{4}=[0.5,0.5]",
            38,
        ), 11.4).move_to(DOWN * 2.28)
        with self.voiceover(text=VO["ag_math"]):
            self.play(TransformMatchingTex(summary, detailed), run_time=1.0)
        self.wait(0.9)


class S3_10_Update(GlanceScene):
    """Cảnh 10 — UPDATE gộp trạng thái cũ với thông điệp mới (nguyên S4_06)."""

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        step_head(self, 10, "UPDATE: combine old state and new message")

        old_state = equation_card(r"h_A^{(\ell-1)}=[0.2,0.8]", "state before update",
                                  3.75, 1.10).move_to(LEFT * 4.55 + UP * 1.00)
        message = equation_card(r"m_A^{(\ell)}=[0.6,0.4]", "neighbor message",
                                3.75, 1.10).move_to(LEFT * 4.55 + DOWN * 0.95)
        update = module_box("UPDATE", "combine two inputs", width=2.75, height=1.15,
                            emphasized=True).move_to(LEFT * 0.25)
        new_state = equation_card(r"h_A^{(\ell)}=[0.4,0.6]", "illustrative result",
                                  3.65, 1.12, True).move_to(RIGHT * 4.25)
        arrows = VGroup(
            small_arrow(old_state.get_right(), update.get_left(), color=C_EDGE, buff=0.10),
            small_arrow(message.get_right(), update.get_left(), color=C_EDGE, buff=0.10),
            small_arrow(update.get_right(), new_state.get_left(), color=MUTED, stroke_width=2.2, buff=0.10),
        )

        with self.voiceover(text=VO["up_intro"]):
            self.play(FadeIn(old_state), FadeIn(message), run_time=0.55)
        with self.voiceover(text=VO["up_example"]):
            self.play(GrowArrow(arrows[0]), GrowArrow(arrows[1]), FadeIn(update), run_time=0.7)
        with self.voiceover(text=VO["up_result"]):
            self.play(GrowArrow(arrows[2]), FadeIn(new_state, shift=RIGHT * 0.08), run_time=0.6)

        update_eq = fit_width(mt(
            r"h_A^{(\ell)}=\operatorname{UPDATE}^{(\ell)}"
            r"\!\left(h_A^{(\ell-1)},m_A^{(\ell)}\right)",
            42,
        ), 10.8).move_to(DOWN * 2.05)
        caveat = txt("The numeric output illustrates the role of UPDATE; "
                     "learned parameters determine the real value.", 19, MUTED)
        caveat.next_to(update_eq, DOWN, buff=0.20)
        with self.voiceover(text=VO["up_caveat"]):
            self.play(Write(update_eq), run_time=0.85)
            self.play(FadeIn(caveat), run_time=0.45)
        self.wait(0.9)


class S3_11_BeforeAfter(GlanceScene):
    """Cảnh 11 — biểu diễn của A trước và sau UPDATE (nguyên S4_07)."""

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        step_head(self, 11, "How Node A changes after UPDATE")

        before_node = avatar_node("A", target=True, radius=0.38)
        before = VGroup(
            txt("BEFORE UPDATE", 22, MUTED, BOLD),
            before_node,
            mt(r"h_A^{(\ell-1)}=[0.2,0.8]", 39),
            txt("current representation", 21, MUTED),
        ).arrange(DOWN, buff=0.24).move_to(LEFT * 3.65 + DOWN * 0.05)
        after_node = avatar_node("A", target=True, radius=0.38)
        after = VGroup(
            txt("AFTER UPDATE", 22, INK, BOLD),
            after_node,
            mt(r"h_A^{(\ell)}=[0.4,0.6]", 39),
            txt("includes neighbor evidence", 21, MUTED),
        ).arrange(DOWN, buff=0.24).move_to(RIGHT * 3.65 + DOWN * 0.05)
        transition = small_arrow(LEFT * 1.55, RIGHT * 1.55, color=MUTED, stroke_width=2.4, buff=0.0)
        update_label = txt("UPDATE", 24, INK, BOLD).next_to(transition, UP, buff=0.20)
        message_label = mt(r"+\ m_A^{(\ell)}", 33, MUTED).next_to(transition, DOWN, buff=0.18)

        with self.voiceover(text=VO["ba_identity"]):
            self.play(FadeIn(before, shift=RIGHT * 0.08), run_time=0.65)
        with self.voiceover(text=VO["ba_before"]):
            self.play(GrowArrow(transition), FadeIn(update_label), Write(message_label), run_time=0.7)
        with self.voiceover(text=VO["ba_after"]):
            self.play(TransformFromCopy(before_node, after_node), FadeIn(after[0]),
                      Write(after[2]), FadeIn(after[3]), run_time=0.85)

        identity = takeaway_chip("The paper is still Node A; only its learned representation changes")
        with self.voiceover(text=VO["ba_repeat"]):
            self.play(FadeIn(identity, shift=UP * 0.08), run_time=0.45)
        self.wait(0.9)


class S3_12_NodeEmbedding(GlanceScene):
    """Cảnh 12 — Signal 1: z_G(A), tách khỏi dự đoán p_H,A (nguyên S4_08).

    p_{H,A} vẫn lên hình nhưng được ghi rõ là dự đoán được lưu lại, không phải
    một thành phần của f_A. Mở cảnh bằng `demo_tag()` — đồ thị 12 node dùng
    chung cả video (plan.md, "Shared Elements") — để section 3 vẫn giữ motif đó;
    node 4 là hub homophily cao, ở đây đóng vai node A.
    """

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        step_head(self, 12, "Signal 1: the GNN node embedding")

        graph = demo_tag(radius=0.13, scale=0.62).move_to(LEFT * 3.70 + DOWN * 0.35)
        a_lab = txt("A", 19, INK, BOLD).next_to(graph.nodes[4], DOWN, buff=0.16)
        ring = ego_ring(graph, 4, [0, 1, 2, 3], color=C_GNN)
        # Nhãn đặt phía trên vòng: bên dưới vòng là node 10 của demo graph.
        ring_lab = txt("k-hop neighborhood", 17, C_GNN).next_to(ring, UP, buff=0.18)

        gnn = module_box("GNN", "backbone", width=2.5, height=1.35, emphasized=True)
        gnn.move_to(RIGHT * 3.10)
        feed = small_arrow(graph.get_right(), gnn.get_left(), color=MUTED,
                           stroke_width=2.1, buff=0.30)

        with self.voiceover(text=VO["ep_graph"]):
            self.play(FadeIn(graph), FadeIn(a_lab), run_time=0.9)
            self.play(Create(ring), FadeIn(ring_lab), run_time=0.7)
            self.play(GrowArrow(feed), FadeIn(gnn), run_time=0.8)

        embedding_title = txt("NODE EMBEDDING", 21, MUTED, BOLD).move_to(LEFT * 0.5 + UP * 1.35)
        prediction_title = txt("INITIAL PREDICTION", 21, MUTED, BOLD).move_to(LEFT * 0.5 + DOWN * 1.10)
        emb = feature_strip(r"z_G(A)", n=10, cell_size=0.31, math_label=True).move_to(RIGHT * 3.55 + UP * 1.35)
        pred = probability_bars(r"p_{H,A}", [0.45, 0.40, 0.15], width=3.0,
                                math_label=True).move_to(RIGHT * 3.45 + DOWN * 1.10)

        with self.voiceover(text=VO["ep_two"]):
            self.play(
                FadeOut(VGroup(graph, a_lab, ring, ring_lab, feed)),
                gnn.animate.move_to(LEFT * 4.75),
                run_time=0.9,
            )

        # Dựng mũi tên sau khi khối GNN đã về chỗ, nếu không đầu mũi tên lệch.
        arr1 = small_arrow(gnn.get_right(), embedding_title.get_left(), color=MUTED, stroke_width=2.1, buff=0.18)
        arr2 = small_arrow(gnn.get_right(), prediction_title.get_left(), color=MUTED, stroke_width=2.1, buff=0.18)

        router_tag = txt("ROUTER SIGNAL", 17, C_ROUTER, BOLD).next_to(emb, DOWN, buff=0.22)
        with self.voiceover(text=VO["ep_embedding"]):
            self.play(GrowArrow(arr1), FadeIn(embedding_title), run_time=0.6)
            self.play(FadeIn(emb, shift=RIGHT * 0.10), run_time=0.65)
            self.play(FadeIn(router_tag), run_time=0.4)

        with self.voiceover(text=VO["ep_prediction"]):
            self.play(GrowArrow(arr2), FadeIn(prediction_title), run_time=0.55)
            self.play(FadeIn(pred, shift=RIGHT * 0.10), run_time=0.65)

        stored_tag = txt("STORED GNN PREDICTION · NOT PART OF THE ROUTING FEATURE",
                         17, MUTED, BOLD)
        stored_tag = fit_width(stored_tag, 6.4).next_to(pred, DOWN, buff=0.22)
        formula = mt(r"p_{H,A}=\operatorname{softmax}\!\left(H(z_G(A))\right)",
                     34).move_to(DOWN * 2.62 + LEFT * 2.90)
        with self.voiceover(text=VO["ep_head"]):
            self.play(Write(formula), run_time=0.8)
            self.play(FadeIn(stored_tag), run_time=0.45)
        self.wait(0.8)


class S3_13_Uncertainty(GlanceScene):
    """Cảnh 13 — Signal 2: u_A ước lượng qua nhiều lượt dropout (nguyên S4_09)."""

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        step_head(self, 13, "Signal 2: GNN uncertainty from dropout passes")

        gnn = module_box("GNN + dropout", "same Node A", width=2.8, height=1.25,
                         emphasized=True).move_to(LEFT * 4.60)
        passes = VGroup(*[
            probability_bars(f"pass {idx + 1}", values, width=2.1).scale(0.90)
            for idx, values in enumerate([
                [0.45, 0.40, 0.15],
                [0.38, 0.47, 0.15],
                [0.49, 0.36, 0.15],
            ])
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.28).move_to(LEFT * 0.30)
        pass_arrows = VGroup(*[
            small_arrow(gnn.get_right(), p.get_left(), color=C_EDGE, stroke_width=1.7, buff=0.10)
            for p in passes
        ])

        with self.voiceover(text=VO["uc_stable"]):
            self.play(FadeIn(gnn), run_time=0.45)
        with self.voiceover(text=VO["uc_dropout"]):
            self.play(
                LaggedStart(*[AnimationGroup(GrowArrow(a), FadeIn(p))
                              for a, p in zip(pass_arrows, passes)], lag_ratio=0.16),
                run_time=1.0,
            )

        uncertainty = math_module_box(r"u_A", "variation across passes", width=3.0, height=1.10,
                                      emphasized=True).move_to(RIGHT * 4.65)
        with self.voiceover(text=VO["uc_high"]):
            self.play(ReplacementTransform(VGroup(passes, pass_arrows), uncertainty), run_time=0.8)

        note = txt("Larger variation means higher uncertainty", 25, MUTED, BOLD).move_to(DOWN * 2.10)
        caveat = VGroup(
            txt("The source does not define a unique closed-form equation for", 19, MUTED),
            MathTex(r"u_A", font_size=25, color=MUTED),
        ).arrange(RIGHT, buff=0.16).next_to(note, DOWN, buff=0.16)
        with self.voiceover(text=VO["uc_signal"]):
            self.play(FadeIn(note), FadeIn(caveat), run_time=0.65)
        self.wait(0.8)


class S3_14_MLPQ(GlanceScene):
    """Cảnh 14 — MLP Q chạy trên đặc trưng nót, không dùng cạnh (nguyên S4_10)."""

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        step_head(self, 14, "MLP Q uses node features only")

        mlp_frame = RoundedRectangle(
            width=6.4, height=3.85, corner_radius=0.18,
            stroke_color=MUTED, stroke_width=1.6, fill_color=BG, fill_opacity=1,
        ).move_to(LEFT * 0.90 + UP * 0.25)
        mlp_label = txt("MLP Q", 26, INK, BOLD).move_to(mlp_frame.get_top() + DOWN * 0.38)
        with self.voiceover(text=VO["mq_intro"]):
            self.play(Create(mlp_frame), FadeIn(mlp_label), run_time=0.5)

        layer_xs = [-2.8, -1.0, 0.8]
        counts = [4, 5, 3]
        neuron_layers = VGroup()
        for x, count in zip(layer_xs, counts):
            layer = VGroup(*[
                Circle(radius=0.12, stroke_color=MUTED, stroke_width=1.4, fill_color=BG, fill_opacity=1)
                for _ in range(count)
            ]).arrange(DOWN, buff=0.27).move_to(RIGHT * x + DOWN * 0.05)
            neuron_layers.add(layer)
        connections = VGroup()
        for left_layer, right_layer in zip(neuron_layers[:-1], neuron_layers[1:]):
            for left_n in left_layer:
                for right_n in right_layer:
                    connections.add(Line(left_n.get_center(), right_n.get_center(),
                                         buff=0.12, color=C_EDGE, stroke_width=0.75))
        with self.voiceover(text=VO["mq_nostructure"]):
            self.play(Create(connections), FadeIn(neuron_layers), run_time=0.8)

        input_y = neuron_layers[0].get_center()[1]
        output_y = neuron_layers[-1].get_center()[1]
        input_label = mt(r"x_A", 36).move_to([mlp_frame.get_left()[0] - 0.75, input_y, 0])
        output_label = mt(r"p_{Q,A}", 36).move_to([mlp_frame.get_right()[0] + 0.90, output_y, 0])
        input_arrow = small_arrow(
            [input_label.get_right()[0], input_y, 0],
            [neuron_layers[0].get_left()[0], input_y, 0],
            color=MUTED, stroke_width=2.1, buff=0.08,
        )
        output_arrow = small_arrow(
            [neuron_layers[-1].get_right()[0], output_y, 0],
            [output_label.get_left()[0], output_y, 0],
            color=MUTED, stroke_width=2.1, buff=0.08,
        )
        with self.voiceover(text=VO["mq_output"]):
            self.play(Write(input_label), GrowArrow(input_arrow), run_time=0.5)
            self.play(*[n.animate.set_fill(INK) for layer in neuron_layers for n in layer], run_time=0.55)
            self.play(GrowArrow(output_arrow), Write(output_label), run_time=0.5)

        outputs = VGroup(*[
            probability_bars(rf"p_{{Q,{label}}}", vals, width=1.20, math_label=True).scale(0.76)
            for label, vals in zip("ABCDE", [
                [0.20, 0.55, 0.25], [0.28, 0.50, 0.22], [0.36, 0.45, 0.19],
                [0.44, 0.40, 0.16], [0.52, 0.35, 0.13],
            ])
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.16).move_to(RIGHT * 5.25 + DOWN * 0.15)
        with self.voiceover(text=VO["mq_shared"]):
            self.play(ReplacementTransform(output_label.copy(), outputs[0]), run_time=0.42)
            for idx, label in enumerate("BCDE", start=1):
                new_input = mt(rf"x_{{{label}}}", 31, MUTED).move_to(input_label)
                self.play(Transform(input_label, new_input),
                          FadeIn(outputs[idx], shift=RIGHT * 0.08), run_time=0.35)

        formula_q = mt(r"p_{Q,v}=Q(x_v)", 38).move_to(DOWN * 2.02 + LEFT * 0.85)
        note_q = txt("No graph structure - No message passing", 20, MUTED, BOLD).next_to(
            formula_q, DOWN, buff=0.14)
        with self.voiceover(text=VO["mq_purpose"]):
            self.play(Write(formula_q), FadeIn(note_q), run_time=0.7)
        self.wait(0.8)


class S3_15_NeighborAverage(GlanceScene):
    """Cảnh 15 — trung bình phân phối của hàng xóm (nguyên S4_11)."""

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        step_head(self, 15, "Average one prediction from each neighbor")

        node_A = avatar_node("A", target=True, radius=0.32).move_to(UP * 0.55)
        positions = {
            "B": UP * 1.75,
            "C": LEFT * 1.75 + UP * 0.55,
            "D": RIGHT * 1.75 + UP * 0.55,
            "E": DOWN * 0.65,
        }
        neighbors = {label: avatar_node(label, radius=0.22).move_to(pos) for label, pos in positions.items()}
        edges = VGroup(*[
            Line(node_A.get_center(), neighbors[label].get_center(), buff=0.28,
                 color=C_EDGE, stroke_width=1.8)
            for label in positions
        ])
        prediction_data = {
            "B": r"p_{Q,B}=[.20,.55,.25]",
            "C": r"p_{Q,C}=[.25,.50,.25]",
            "D": r"p_{Q,D}=[.30,.47,.23]",
            "E": r"p_{Q,E}=[.35,.40,.25]",
        }
        prediction_positions = {
            "B": UP * 2.35,
            "C": LEFT * 4.35 + UP * 0.55,
            "D": RIGHT * 4.35 + UP * 0.55,
            "E": DOWN * 1.18,
        }
        with self.voiceover(text=VO["na_collect"]):
            self.play(Create(edges), FadeIn(node_A), FadeIn(VGroup(*neighbors.values())), run_time=0.7)
            self.bring_to_front(node_A, *neighbors.values())
            predictions = VGroup()
            for label in "BCDE":
                prediction = mt(prediction_data[label], 27, MUTED).move_to(prediction_positions[label])
                predictions.add(prediction)
                self.play(
                    FadeIn(prediction,
                           shift=0.08 * (prediction.get_center() - neighbors[label].get_center())),
                    run_time=0.42,
                )
        graph_group = VGroup(edges, node_A, *neighbors.values())

        sum_definition = MathTex(
            r"S_A", r":=", r"\sum_{u\in N(A)}p_{Q,u}",
            font_size=52, color=INK,
        )
        sum_definition[0].move_to(LEFT * 5.65 + UP * 0.55)
        VGroup(sum_definition[1], sum_definition[2]).arrange(RIGHT, buff=0.12).next_to(
            sum_definition[0], RIGHT, buff=0.16,
        )
        sum_symbol = sum_definition[0]
        current_sum_rhs = VGroup(sum_definition[1], sum_definition[2])
        with self.voiceover(text=VO["na_sum"]):
            self.play(FadeOut(graph_group), FadeOut(predictions), run_time=0.72)
            self.play(Write(sum_symbol), Write(current_sum_rhs), run_time=0.70)

        sum_expansion = fit_width(
            MathTex(
                r"S_A", r"=",
                r"[.20,.55,.25]", r"+", r"[.25,.50,.25]", r"+",
                r"[.30,.47,.23]", r"+", r"[.35,.40,.25]",
                font_size=42, color=INK,
            ),
            12.0,
        )
        expansion_rhs = VGroup(*sum_expansion[1:]).next_to(sum_symbol, RIGHT, buff=0.16)
        with self.voiceover(text=VO["na_divide"]):
            self.play(FadeOut(current_sum_rhs), run_time=0.24)
            self.play(FadeIn(expansion_rhs, shift=UP * 0.04), run_time=0.52)
            current_sum_rhs = expansion_rhs
            self.wait(0.20)

            sum_value = MathTex(
                r"S_A", r"=", r"[1.10,1.92,0.98]",
                font_size=55, color=INK,
            )
            value_rhs = VGroup(sum_value[1], sum_value[2])
            value_symbol_guide = sum_symbol.copy()
            VGroup(value_symbol_guide, value_rhs).arrange(RIGHT, buff=0.16).move_to(UP * 0.35)
            symbol_value_target = value_symbol_guide.get_center().copy()
            self.play(FadeOut(current_sum_rhs), run_time=0.24)
            self.play(
                sum_symbol.animate.move_to(symbol_value_target),
                FadeIn(value_rhs),
                run_time=0.55,
            )

        mean_prefix = MathTex(
            r"\bar p_{Q,N(A)}", r"=", r"\frac{1}{|N(A)|}",
            font_size=49, color=INK,
        )
        with self.voiceover(text=VO["na_average"]):
            self.play(
                FadeOut(value_rhs),
                sum_symbol.animate.move_to(ORIGIN),
                run_time=0.48,
            )
            mean_prefix.next_to(sum_symbol, LEFT, buff=0.14)
            mean_prefix_target = mean_prefix.get_center().copy()
            mean_prefix.move_to(mean_prefix_target + DOWN * 0.85).set_opacity(0)
            self.add(mean_prefix)
            self.play(
                mean_prefix.animate.move_to(mean_prefix_target).set_opacity(1),
                run_time=0.72,
                rate_func=smooth,
            )

            substitution = MathTex(
                r"=", r"\frac{1}{4}", r"[1.10,1.92,0.98]",
                font_size=43, color=MUTED,
            ).next_to(sum_symbol, RIGHT, buff=0.14)
            self.play(FadeIn(substitution, shift=RIGHT * 0.12), run_time=0.58)
            self.wait(0.2)

            final_average = MathTex(
                r"\bar p_{Q,N(A)}", r"=", r"[0.275,0.480,0.245]",
                font_size=55, color=INK,
            ).move_to(ORIGIN)
            self.play(
                FadeOut(VGroup(mean_prefix, sum_symbol, substitution), shift=UP * 0.04),
                FadeIn(final_average, shift=UP * 0.04),
                run_time=0.65,
            )

        result_note = takeaway_chip("Final average neighborhood distribution")
        with self.voiceover(text=VO["na_meaning"]):
            self.play(FadeIn(result_note, shift=UP * 0.08), run_time=0.42)
        self.wait(0.9)


class S3_16_SoftHomophily(GlanceScene):
    """Cảnh 16 — Signal 3: h mũ A bằng tích vô hướng (nguyên S4_12).

    Đoạn cuối giữ lại bảng hard vs soft của bản S3_09 cũ: phiên bản mềm còn giữ
    được mức độ chắc chắn, thay vì chỉ 0 hoặc 1.
    """

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        step_head(self, 16, "Signal 3: compare Node A with its neighborhood")

        p_a = probability_bars(r"p_{Q,A}", [0.56, 0.28, 0.16], width=2.45, math_label=True)
        p_mean = probability_bars(r"\bar p_{Q,N(A)}", [0.28, 0.48, 0.24], width=2.45, math_label=True)
        p_a.move_to(LEFT * 3.20 + UP * 1.40)
        p_mean.move_to(RIGHT * 2.20 + UP * 1.40)
        dot = mt(r"\cdot", 52).move_to((p_a.get_right() + p_mean.get_left()) / 2)
        with self.voiceover(text=VO["sh_compare"]):
            self.play(FadeIn(p_a, shift=UP * 0.08), FadeIn(p_mean, shift=UP * 0.08), run_time=0.65)
            self.play(Write(dot), run_time=0.35)

        formula_h = mt(
            r"\hat h_A=p_{Q,A}\cdot\bar p_{Q,N(A)}"
            r"=p_{Q,A}\cdot\left(\frac{1}{|N(A)|}\sum_{u\in N(A)}p_{Q,u}\right)",
            38,
        ).move_to(UP * 0.30)
        with self.voiceover(text=VO["sh_dot"]):
            self.play(Write(formula_h), run_time=1.0)

        result = VGroup(
            math_module_box(r"\hat h_A", "estimated local homophily", width=3.2, height=1.05,
                            emphasized=True),
            mt(r"\hat h_A\in[0,1]", 38),
        ).arrange(RIGHT, buff=0.65).move_to(DOWN * 1.35 + RIGHT * 0.35)
        with self.voiceover(text=VO["sh_meaning"]):
            self.play(TransformFromCopy(VGroup(p_a, p_mean), result[0]), Write(result[1]), run_time=0.8)

        # --- Bản cứng chỉ có 0/1, bản mềm giữ được mức độ chắc chắn (từ S3_09 cũ) ---
        compare = VGroup(
            VGroup(txt("hard", 20, MUTED, BOLD),
                   txt("0  or  1", 22, MUTED)).arrange(RIGHT, buff=0.55),
            VGroup(txt("soft", 20, C_HIGHLIGHT, BOLD),
                   txt("0.82   0.56   0.31", 22, C_HIGHLIGHT)).arrange(RIGHT, buff=0.55),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.32)
        compare_frame = panel(compare, color=C_EDGE, buff=0.32)
        compare_group = VGroup(compare_frame, compare).move_to(DOWN * 1.30)
        compare_head = txt("The soft version keeps how confident MLP Q is",
                           20, INK, BOLD).next_to(compare_group, UP, buff=0.38)

        with self.voiceover(text=VO["sh_soft"]):
            self.play(FadeOut(VGroup(p_a, p_mean, dot, formula_h)), run_time=0.5)
            self.play(result.animate.move_to(UP * 1.85), run_time=0.6)
            self.play(FadeIn(compare_head), FadeIn(compare_frame), FadeIn(compare[0]), run_time=0.7)
            self.play(FadeIn(compare[1], shift=RIGHT * 0.2), run_time=0.7)

        prior = takeaway_chip("Estimated homophily is a routing prior")
        with self.voiceover(text=VO["sh_prior"]):
            self.play(FadeIn(prior, shift=UP * 0.08), run_time=0.42)
        self.wait(0.8)


class S3_17_NodeFeatures(GlanceScene):
    """Cảnh 17 — Signal 4: đặc trưng gốc x_A (nửa trái của S4_13 cũ)."""

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        step_head(self, 17, "Signal 4: the original node feature")

        raw_tag = VGroup(txt("RAW TEXT", 20, MUTED, BOLD), mt(r"t_A", 29, MUTED)).arrange(RIGHT, buff=0.14)
        raw_title = fit_width(
            txt('"Improving Graph Neural Networks\nunder Heterophily"', 28, INK, BOLD), 6.0)
        x_vector = feature_strip(r"x_A", n=9, cell_size=0.33, math_label=True)
        # buff rộng để mũi tên "encode text" giữa tiêu đề và vector còn chỗ thở.
        text_column = VGroup(raw_tag, raw_title, x_vector).arrange(DOWN, buff=0.62)
        text_column.move_to(UP * 0.95)
        text_arrow = small_arrow(raw_title.get_bottom(), x_vector.get_top(),
                                 color=MUTED, stroke_width=2.1, buff=0.12)
        encode_label = txt("encode text", 17, MUTED).next_to(text_arrow, RIGHT, buff=0.22)

        with self.voiceover(text=VO["nf_keep"]):
            self.play(FadeIn(raw_tag), Write(raw_title), run_time=0.7)
        with self.voiceover(text=VO["nf_vector"]):
            self.play(GrowArrow(text_arrow), FadeIn(encode_label), run_time=0.42)
            self.play(TransformFromCopy(raw_title, x_vector), run_time=0.75)

        cards = VGroup(
            equation_card(r"x_A", "ego information only", 5.05, 1.12, True),
            equation_card(r"z_G(A)", "ego + neighborhood aggregation", 5.05, 1.12),
        ).arrange(RIGHT, buff=0.60, aligned_edge=UP).move_to(DOWN * 2.05)
        with self.voiceover(text=VO["nf_ego"]):
            self.play(FadeIn(cards[0], shift=UP * 0.08), run_time=0.6)
            self.play(FadeIn(cards[1], shift=UP * 0.08), run_time=0.6)
            self.play(Indicate(cards[0], color=C_LLM, scale_factor=1.04), run_time=0.8)
        self.wait(0.8)


class S3_18_Degree(GlanceScene):
    """Cảnh 18 — Signal 5: bậc thô d_A (nửa phải của S4_13 cũ).

    Cuối cảnh giữ cảnh báo của S3_11 cũ: router dùng d_v, còn bậc tương đối
    d ngang v chỉ xuất hiện trong phần phân tích thực nghiệm §4.2.1.
    """

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        step_head(self, 18, "Signal 5: the degree of Node A")

        degree_A = avatar_node("A", target=True, radius=0.29)
        degree_neighbors = VGroup(
            avatar_node("B", radius=0.19).move_to(UP * 1.0),
            avatar_node("C", radius=0.19).move_to(LEFT * 1.15),
            avatar_node("D", radius=0.19).move_to(RIGHT * 1.15),
            avatar_node("E", radius=0.19).move_to(DOWN * 1.0),
        )
        degree_edges = VGroup(*[
            Line(degree_A.get_center(), n.get_center(), buff=0.25, color=C_EDGE, stroke_width=1.8)
            for n in degree_neighbors
        ])
        degree_graph = VGroup(degree_edges, degree_A, degree_neighbors)
        degree_eq = mt(r"d_A=|N(A)|=4", 42)
        degree_column = VGroup(
            txt("CITATION NEIGHBORHOOD", 20, MUTED, BOLD), degree_graph, degree_eq,
        ).arrange(DOWN, buff=0.30).move_to(LEFT * 3.55 + UP * 0.75)

        recall = VGroup(
            txt("FROM THE PREVIOUS STEP", 20, MUTED, BOLD),
            feature_strip(r"x_A", n=9, cell_size=0.30, math_label=True),
        ).arrange(DOWN, buff=0.34).move_to(RIGHT * 3.55 + UP * 0.95)

        with self.voiceover(text=VO["dg_degree"]):
            self.play(FadeIn(degree_column[0]), FadeIn(degree_A), run_time=0.4)
            self.play(FadeIn(degree_neighbors), Create(degree_edges), run_time=0.65)
            self.bring_to_front(degree_A, degree_neighbors)
        with self.voiceover(text=VO["dg_count"]):
            self.play(Write(degree_eq), run_time=0.55)

        direct_eq = equation_card(
            r"\mathcal I_A^{\mathrm{direct}}=(x_A,d_A)",
            "semantic feature + structural degree",
            width=6.2, height=1.22, emphasized=True,
        ).move_to(DOWN * 2.15)
        with self.voiceover(text=VO["dg_direct"]):
            self.play(FadeIn(recall, shift=LEFT * 0.08), run_time=0.6)
            self.play(TransformFromCopy(VGroup(recall[1], degree_eq), direct_eq), run_time=0.8)

        # --- d_v của router khác hẳn bậc tương đối ở §4.2.1 (giữ từ S3_11 cũ) ---
        rows = VGroup(
            VGroup(mt(r"\bar d_v", 30, C_LLM),
                   txt("4.2.1 analysis: compare v with its neighbors", 21, MUTED)
                   ).arrange(RIGHT, buff=0.40),
            VGroup(mt(r"d_v", 30, C_HIGHLIGHT),
                   txt("GLANCE router: directly count the neighbors", 21, INK)
                   ).arrange(RIGHT, buff=0.40),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.40)
        rows[1][0].align_to(rows[0][0], LEFT)
        rows[1][1].align_to(rows[0][1], LEFT)
        rows.move_to(DOWN * 0.35)
        rows_frame = panel(rows, color=C_EDGE, buff=0.38)
        rows_head = txt("Two distinct quantities", 24, INK, BOLD).next_to(rows_frame, UP, buff=0.45)

        with self.voiceover(text=VO["dg_vs_rd"]):
            self.play(FadeOut(VGroup(degree_column, recall, direct_eq)), run_time=0.6)
            self.play(FadeIn(rows_head), FadeIn(rows_frame), run_time=0.7)
            self.play(FadeIn(rows[0], shift=RIGHT * 0.2), run_time=0.8)
            self.play(FadeIn(rows[1], shift=RIGHT * 0.2), run_time=0.8)

        note = takeaway_chip("Degree: how much neighborhood information can the GNN use?")
        self.play(FadeIn(note, shift=UP * 0.08), run_time=0.42)
        self.wait(0.9)


class S3_19_RoutingFeature(GlanceScene):
    """Cảnh 19 — ghép năm signal thành f_A rồi bàn giao sang section 4.

    Section 3 dừng tại đây: không tính routing score, không xếp hạng, không
    top-k — toàn bộ phần đó thuộc section 4.
    """

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        step_head(self, 19, "Build the routing feature")

        cards = VGroup(
            equation_card(r"z_G(A)", "GNN embedding", 2.15, 0.90, True),
            equation_card(r"u_A", "uncertainty", 2.15, 0.90),
            equation_card(r"\hat h_A", "homophily", 2.15, 0.90),
            equation_card(r"x_A", "original feature", 2.15, 0.90),
            equation_card(r"d_A", "degree", 2.15, 0.90),
        ).arrange(RIGHT, buff=0.17)
        cards.scale_to_fit_width(12.0).move_to(UP * 1.35)
        with self.voiceover(text=VO["rf_cards"]):
            self.play(
                LaggedStart(*[FadeIn(card, shift=DOWN * 0.08) for card in cards], lag_ratio=0.10),
                run_time=0.95,
            )

        formulas = [
            r"f_A=[z_G(A)]",
            r"f_A=[z_G(A),u_A]",
            r"f_A=[z_G(A),u_A,\hat h_A]",
            r"f_A=[z_G(A),u_A,\hat h_A,x_A]",
            r"f_A=[z_G(A),u_A,\hat h_A,x_A,d_A]",
        ]
        with self.voiceover(text=VO["rf_five"]):
            current_formula = mt(formulas[0], 46).move_to(DOWN * 0.25)
            self.play(TransformFromCopy(cards[0], current_formula), run_time=0.58)
            for index, formula in enumerate(formulas[1:], start=1):
                next_formula = mt(formula, 46).move_to(current_formula)
                self.play(
                    cards[index][0].animate.set_stroke(INK),
                    TransformMatchingTex(current_formula, next_formula),
                    run_time=0.55,
                )
                current_formula = next_formula

        note = VGroup(
            txt("FIVE COMPLEMENTARY SIGNALS", 22, INK, BOLD),
            txt("No single signal decides routing", 21, MUTED),
        ).arrange(DOWN, buff=0.12).move_to(DOWN * 1.55)
        with self.voiceover(text=VO["rf_note"]):
            self.play(FadeIn(note, shift=UP * 0.08), run_time=0.48)

        # --- Bàn giao sang section 4: f_A đã xong, quyết định thì chưa ---
        next_card = VGroup(
            txt("GLANCE Architecture", 30, C_ROUTER, BOLD),
            txt("Section 4", 22, MUTED),
        ).arrange(DOWN, buff=0.25)
        next_frame = panel(next_card, color=C_ROUTER, buff=0.45)
        handoff = VGroup(next_frame, next_card).move_to(DOWN * 1.35)

        with self.voiceover(text=VO["rf_close"]):
            self.play(FadeOut(VGroup(cards, note)), run_time=0.6)
            self.play(current_formula.animate.move_to(UP * 1.35), run_time=0.7)
            self.play(FadeIn(handoff, scale=0.9), run_time=0.9)
            self.play(handoff.animate.scale(1.08), run_time=0.7)
            self.play(FadeOut(VGroup(current_formula, handoff)), run_time=0.8)

        self.wait(0.8)
