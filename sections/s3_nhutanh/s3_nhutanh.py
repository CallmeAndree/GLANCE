"""Section 3 — Structural signal.  Owner: Nhựt Anh.

Nguồn trong paper: §4.2.1 (tr.4) — định nghĩa local homophily.
Kịch bản chi tiết: sections/s3_nhutanh/TASK.md

Cảnh 1 — Local homophily. Năm nhịp theo storyboard của nhóm:
    1. giới thiệu tín hiệu, node v + 4 hàng xóm
    2. kiểm tra từng hàng xóm, dựng công thức
    3. thay số, h_v = 0.75
    4. homophily cao  → message nhất quán → GNN đúng
    5. homophily thấp → neighborhood heterophilous → GNN sai

Cảnh 6–12 — phần bổ sung: năm routing signals của Step 1 (§5.1.1, tr.5–6).
Nối tiếp ngay sau cảnh cầu nối, giải thích từng signal mà router nhận vào:
node embedding, uncertainty, soft homophily estimation, node features, degree.
Lưu ý: signal thứ năm trong kiến trúc là **degree thô** d_v, không phải relative
degree đã phân tích ở cảnh 2 — xem cảnh S3_11_Degree.

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
# "h_v" đọc thành "h của v", "3/4" đọc thành "ba phần tư". Đổi text ở đây là
# audio tự sinh lại; giữ nguyên text thì dùng bản đã cache, render nhanh.
VO = {
    "intro": (
        "Tín hiệu đầu tiên là độ đồng nhất cục bộ. "
        "Nó đo mức độ tương đồng về nhãn giữa một nót và các hàng xóm trực tiếp của nó."
    ),
    "check": (
        "Cụ thể, với mỗi hàng xóm u, ta kiểm tra liệu nhãn của u "
        "có giống nhãn của v hay không. "
        "Sau đó lấy tỷ lệ trên toàn bộ tập hàng xóm."
    ),
    "value": (
        "Trong ví dụ này, ba trong bốn hàng xóm cùng nhãn với v, "
        "vì vậy h của v bằng ba phần tư, tức không phẩy bảy lăm."
    ),
    "high": (
        "Khi độ đồng nhất cục bộ cao, thông tin từ hàng xóm thường nhất quán với nót trung tâm. "
        "Vì gi en en học bằng cách tổng hợp thông tin lân cận, "
        "quá trình truyền thông điệp thường có lợi trong trường hợp này."
    ),
    "low": (
        "Ngược lại, khi độ đồng nhất cục bộ thấp, phần lớn hàng xóm thuộc lớp khác. "
        "Việc tổng hợp các biểu diễn này có thể đưa tín hiệu không phù hợp "
        "vào nót trung tâm, và khiến gi en en dự đoán sai."
    ),
    # --- Cảnh 2: relative degree ---
    "rd_intro": (
        "Tín hiệu thứ hai là bậc tương đối. "
        "Bậc thông thường chỉ cho biết nót có bao nhiêu cạnh. "
        "Bậc tương đối đặt giá trị đó trong bối cảnh của chính tập hàng xóm."
    ),
    "rd_formula": (
        "Với mỗi hàng xóm u, tác giả so sánh bậc của v với bậc của u, "
        "rồi lấy trung bình trên tất cả hàng xóm."
    ),
    "rd_scale": (
        "Nếu bậc tương đối lớn hơn một, nót v có xu hướng kết nối nhiều hơn các hàng xóm. "
        "Nếu nhỏ hơn một, nó kết nối ít hơn các nót xung quanh."
    ),
    "rd_value": (
        "Trong ví dụ này, bậc của v thấp hơn cả hai hàng xóm, "
        "nên bậc tương đối xấp xỉ không phẩy bảy chín, nhỏ hơn một."
    ),
    # --- Cảnh 3: GNN và LLM bổ sung nhau ---
    "cp_setup": (
        "Sau đó, tác giả chia các nót thành từng nhóm theo độ đồng nhất cục bộ "
        "và bậc tương đối, rồi so sánh độ chính xác của gi en en với eo eo em trong mỗi nhóm."
    ),
    "cp_trend": (
        "Kết quả cho thấy một xu hướng bổ sung rõ rệt. "
        "Gi en en hoạt động tốt ở những vùng có độ đồng nhất cao và được kết nối tốt. "
        "Nhưng khi độ đồng nhất hoặc bậc tương đối giảm, lợi thế của eo eo em tăng lên."
    ),
    "cp_gain": (
        "Trên Cô-ra, ở nhóm nót khó, eo eo em đạt mức cải thiện tới hai mươi phẩy bốn phần trăm "
        "so với mô hình tốt tiếp theo là gi xi en hai sử dụng đặc trưng được eo eo em tăng cường."
    ),
    "cp_interact": (
        "Hai tín hiệu này còn tương tác với nhau. "
        "Khi đồng thời phân nhóm theo cả độ đồng nhất và bậc, "
        "chênh lệch hiệu năng giữa các nhóm cấu trúc có thể lên tới ba mươi phẩy một phần trăm."
    ),
    # --- Cảnh 4: true -> estimated homophily ---
    "eh_problem": (
        "Độ đồng nhất cục bộ có vẻ là một tín hiệu định tuyến rất tốt. "
        "Tuy nhiên, công thức này cần nhãn thật của nót và hàng xóm, "
        "đúng vào những thông tin không có sẵn đối với các nót cần dự đoán."
    ),
    "eh_mlp": (
        "Để giải quyết vấn đề này, tác giả huấn luyện một em eo pi khiu "
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
        "Chúng giúp nhận diện những nót có cấu trúc bất lợi đối với gi en en, "
        "và nơi eo eo em có khả năng tạo thêm giá trị."
    ),
    "end_router": (
        "Tuy nhiên, kết quả cũng cho thấy không có một tín hiệu đơn lẻ nào "
        "đủ ổn định để quyết định định tuyến trong mọi trường hợp. "
        "Vì vậy, gờ lans không sử dụng một ngưỡng cố định. "
        "Thay vào đó, nó kết hợp các tín hiệu này trong một bộ định tuyến "
        "được học thích nghi cho từng nót."
    ),
    "end_next": (
        "Cụ thể bộ định tuyến này hoạt động như thế nào sẽ được trình bày trong phần tiếp theo."
    ),
    # ------------------------------------------------------------------
    # Phần bổ sung — năm routing signals của Step 1 (§5.1.1, tr.5–6).
    # ------------------------------------------------------------------
    "fs_open": (
        "Phân tích trước đó cho thấy không một quy tắc kinh nghiệm đơn lẻ nào đủ ổn định "
        "để quyết định nót nào cần eo eo em. Vì vậy, gờ lans không chỉ sử dụng độ đồng nhất, "
        "mà mô tả mỗi nót bằng năm tín hiệu định tuyến bổ sung cho nhau."
    ),
    "fs_roles": (
        "Mỗi tín hiệu phản ánh một khía cạnh khác nhau: thông tin gi en en đã học được, "
        "mức độ tin cậy của gi en en, sự nhất quán với hàng xóm, "
        "nội dung riêng của nót, và lượng thông tin cấu trúc sẵn có."
    ),
    # --- Signal 1: node embedding ---
    "ne_intro": (
        "Tín hiệu đầu tiên là véc-tơ biểu diễn của nót, "
        "do một gi en en đã được huấn luyện trước tạo ra."
    ),
    "ne_build": (
        "Gi en en tổng hợp đặc trưng của nót v với thông tin từ vùng lân cận trong phạm vi ca bước, "
        "tạo thành véc-tơ biểu diễn z của v. "
        "Véc-tơ này mã hoá những gì gi en en đã hiểu về cả nội dung "
        "và vị trí cấu trúc của nót."
    ),
    "ne_not_pred": (
        "Đây không phải là nhãn dự đoán cuối cùng. "
        "Nó là biểu diễn trung gian giàu thông tin, giúp bộ định tuyến nhận biết "
        "những kiểu vùng lân cận mà gi en en thường xử lý tốt hoặc gặp khó khăn."
    ),
    # --- Signal 2: node uncertainty ---
    "un_intro": (
        "Tín hiệu thứ hai là độ bất định của nót: "
        "mức độ không chắc chắn của gi en en đối với nót đang xét."
    ),
    "un_dropout": (
        "Gờ lans sử dụng kỹ thuật loại bỏ ngẫu nhiên khi suy luận để tạo nhiều dự đoán. "
        "Nếu các lần chạy đều đưa ra phân phối gần giống nhau, gi en en tương đối chắc chắn. "
        "Nếu kết quả thay đổi mạnh, độ bất định sẽ cao."
    ),
    "un_caveat": (
        "Độ bất định cao là một dấu hiệu nót có thể khó đối với gi en en, "
        "nhưng không tự động có nghĩa eo eo em sẽ tốt hơn. "
        "Vì vậy, gờ lans chỉ dùng nó như một tín hiệu trong tổ hợp."
    ),
    # --- Signal 3: soft homophily estimation ---
    "sh_intro": (
        "Tín hiệu thứ ba xuất phát trực tiếp từ phân tích các tín hiệu cấu trúc: "
        "độ đồng nhất cục bộ ước lượng. "
        "Tuy nhiên, gờ lans sử dụng một phiên bản mềm giàu thông tin hơn."
    ),
    "sh_dist": (
        "Em eo pi khiu không chỉ trả về lớp dự đoán, "
        "mà trả về toàn bộ phân phối xác suất trên các lớp, "
        "cho nót v và cho từng hàng xóm."
    ),
    "sh_dot": (
        "Gờ lans lấy tích vô hướng giữa phân phối của nót trung tâm "
        "và phân phối trung bình của các hàng xóm. "
        "Hai phân phối càng tương đồng, độ đồng nhất ước lượng càng cao."
    ),
    "sh_example": (
        "Trong ví dụ này, tích vô hướng cho giá trị không phẩy ba tám. "
        "Giá trị tương đối thấp cho thấy lớp tiềm năng của nót v "
        "không phù hợp với xu hướng chung của vùng lân cận."
    ),
    "sh_soft": (
        "So với việc chỉ kiểm tra hai nhãn dự đoán có giống nhau hay không, "
        "phiên bản mềm còn giữ lại mức độ chắc chắn của em eo pi."
    ),
    # --- Signal 4: original node features ---
    "nf_intro": (
        "Tín hiệu thứ tư là đặc trưng ban đầu của nót, ký hiệu x của v. "
        "Đây là biểu diễn nội dung vốn có của nót, "
        "trước khi gi en en tổng hợp thông tin từ hàng xóm."
    ),
    "nf_compare": (
        "Véc-tơ biểu diễn của nót cho biết gi en en đã biến đổi thông tin như thế nào, "
        "còn đặc trưng ban đầu giúp bộ định tuyến vẫn truy cập trực tiếp "
        "vào tín hiệu nội tại của nót."
    ),
    "nf_conflict": (
        "Điều này đặc biệt hữu ích khi đặc trưng nót nhiễu, mơ hồ, "
        "hoặc xung đột với thông tin được tổng hợp từ vùng lân cận."
    ),
    # --- Signal 5: degree ---
    "dg_intro": (
        "Tín hiệu cuối cùng là bậc, ký hiệu d của v: "
        "số hàng xóm trực tiếp của nót v."
    ),
    "dg_context": (
        "Bậc cho biết gi en en có bao nhiêu nguồn thông tin lân cận để tổng hợp. "
        "Nót có bậc thấp thường nhận được ít ngữ cảnh cấu trúc hơn."
    ),
    "dg_caveat": (
        "Tuy nhiên, nhiều hàng xóm chưa chắc đã tốt nếu các hàng xóm không liên quan. "
        "Vì vậy, bậc phải được xét cùng độ đồng nhất, độ bất định "
        "và các tín hiệu còn lại."
    ),
    "dg_vs_rd": (
        "Cần phân biệt rõ với phần phân tích lúc nãy: ở đó ta dùng bậc tương đối "
        "để so sánh nót với hàng xóm, còn bộ định tuyến của gờ lans dùng bậc thô, "
        "tức trực tiếp số lượng hàng xóm."
    ),
    # --- Cảnh kết: kết hợp năm signals ---
    "cb_concat": (
        "Năm tín hiệu sau đó được kết hợp thành véc-tơ đặc trưng định tuyến f của v. "
        "Không tín hiệu nào tự mình quyết định nót có được gửi tới eo eo em hay không."
    ),
    "cb_score": (
        "Bộ định tuyến học trọng số cho các tín hiệu, tính điểm định tuyến a của v, "
        "và đưa giá trị này qua một hàm kích hoạt dạng chữ ét. "
        "Điểm càng cao, nót càng có khả năng hưởng lợi từ eo eo em."
    ),
    "cb_topk": (
        "Cuối cùng, gờ lans chọn ca nót có điểm cao nhất trong mỗi lô nhỏ. "
        "Các nót còn lại tiếp tục sử dụng dự đoán gi en en, "
        "nhờ đó duy trì một ngân sách eo eo em cố định."
    ),
    "cb_close": (
        "Năm tín hiệu lần lượt cho bộ định tuyến biết gi en en đã học được gì, tin tưởng đến đâu, "
        "nót có phù hợp với vùng lân cận không, bản thân nót chứa gì, "
        "và có bao nhiêu ngữ cảnh cấu trúc. "
        "Bộ định tuyến học cách kết hợp chúng, thay vì phụ thuộc vào một quy tắc kinh nghiệm cố định."
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

# Hai lớp trong ví dụ, cùng quy ước màu với demo_tag().
CLS_A, CLS_B = C_GNN, C_LLM

SRC_ARCH = "§5.1.1 & Hình 2, tr.5–6"


class S3_01_LocalHomophily(GlanceScene):
    """Cảnh 1 — Local homophily."""

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()

        # ------------------------------------------------------------------
        # Nhịp 1 — Giới thiệu tín hiệu. Node v và bốn hàng xóm.
        # ------------------------------------------------------------------
        head = heading("Tín hiệu 1 — Local homophily", color=ACCENT).to_edge(UP, buff=0.75)
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
            VGroup(Dot(radius=0.1, color=C_GNN), txt("cùng nhãn với v", size=17, color=INK)
                   ).arrange(RIGHT, buff=0.2),
            VGroup(Dot(radius=0.1, color=C_BAD), txt("khác nhãn", size=17, color=INK)
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
            # Từng hàng xóm sáng lên: cùng nhãn -> 1, khác nhãn -> 0.
            for dot, digit, same in zip(u_dots, digits, SAME_LABEL):
                self.play(
                    Indicate(dot, color=C_GOOD if same else C_BAD, scale_factor=1.5),
                    FadeIn(digit, scale=0.6),
                    run_time=0.9,
                )
                self.wait(0.3)
            self.play(Write(formula[4]), run_time=1.1)
            self.play(Write(formula[3]), run_time=0.9)
            self.play(Write(formula[2]), run_time=0.9)

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

        self.add(source("§4.2.1, tr.4"))
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
        head = heading("Tín hiệu 2 — Relative degree", color=ACCENT).to_edge(UP, buff=0.75)

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

        v_deg = txt("d_v = 2", size=21, color=C_HIGHLIGHT).next_to(v_dot, LEFT, buff=0.25)
        u1_deg = txt("d = 5", size=19, color=INK).next_to(u1_dot, UP, buff=0.55)
        u2_deg = txt("d = 3", size=19, color=INK).next_to(u2_dot, DOWN, buff=0.55)

        note = txt("Không chỉ hỏi “node có bao nhiêu cạnh?”", size=21, color=MUTED)
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
        less = txt("kết nối ít hơn hàng xóm", size=16, color=C_BAD)
        less.next_to(scale_line.n2p(0.62), UP, buff=0.45)
        more = txt("kết nối nhiều hơn", size=16, color=C_GOOD)
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

        caveat = txt("Relative degree thấp ≠ degree tuyệt đối thấp",
                     size=19, color=MUTED).to_edge(DOWN, buff=0.75)

        with self.voiceover(text=VO["rd_value"]):
            self.play(TransformMatchingTex(formula, numeric), run_time=1.5)
            self.play(marker.animate.move_to(scale_line.n2p(0.79)),
                      Indicate(numeric[4], color=C_BAD, scale_factor=1.2), run_time=1.2)
            self.play(FadeIn(caveat, shift=UP * 0.15), run_time=0.8)

        self.add(source("§4.2.1, tr.4"))
        self.wait(1.0)


class S3_03_Complementary(GlanceScene):
    """Cảnh 3 — GNN và LLM bổ sung cho nhau."""

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        head = heading("GNN và LLM mạnh ở hai vùng khác nhau", color=ACCENT)
        head.to_edge(UP, buff=0.7)

        chart = line_chart(
            H_SERIES, H_BINS, y_range=(0.0, 1.0, 0.25),
            width=7.4, height=3.5, bars=H_COUNTS, bar_label="Số node",
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
        tag_gnn = txt("GNN thắng", size=20, color=C_GNN)
        tag_llm = txt("LLM thắng", size=20, color=C_LLM)

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
        gain_note = txt("chỉ ở nhóm node khó trên Cora — không phải kết quả toàn dataset",
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
            caveat = txt("là chênh lệch GIỮA các nhóm cấu trúc,\nkhông phải LLM luôn hơn GNN 30.1%",
                         size=17, color=MUTED, line_spacing=0.8)
            caveat.next_to(spread, DOWN, buff=0.35)
            self.play(FadeIn(spread), run_time=0.7)
            self.play(FadeIn(caveat), run_time=0.7)

        self.add(source("Hình 1, tr.4 & Phụ lục E.5"))
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
        corner_lo = txt("khó cho GNN", size=15, color=C_BAD)
        corner_lo.next_to(grid, DOWN, buff=0.25).align_to(grid, LEFT).shift(DOWN * 0.4)
        corner_hi = txt("thuận lợi cho GNN", size=15, color=C_GOOD)
        corner_hi.next_to(grid, UP, buff=0.2).align_to(grid, RIGHT)
        return grid, VGroup(x_lab, y_lab, corner_lo, corner_hi)


class S3_04_EstimatedHomophily(GlanceScene):
    """Cảnh 4 — Từ true homophily đến estimated homophily."""

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        head = heading("Vấn đề: h_v cần nhãn thật", color=ACCENT).to_edge(UP, buff=0.75)

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
        flow = pipeline(
            [("x_v", MUTED), ("MLP Q", C_ROUTER), ("ŷ_v", C_HIGHLIGHT)],
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
        demo_note = txt("viền xám = node thật · ruột = nhãn dự đoán",
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
            ("h_v", "1.03", "không dùng được khi inference", MUTED),
            ("ĥ_v", "3.22", "tốt nhất trong nhóm label-free", C_GOOD),
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
        title_row = txt("Mean rank khi route bằng NCS (thấp = tốt)",
                        size=20, color=INK, weight=BOLD)
        title_row.next_to(table, UP, buff=0.55).align_to(table, LEFT)
        highlight = panel(table[1], color=C_GOOD, buff=0.18)
        rank_head = heading("Xếp hạng tín hiệu routing", color=ACCENT).move_to(head)

        with self.voiceover(text=VO["eh_rank"]):
            self.play(FadeOut(VGroup(flow, demo, demo_note, est_h)), run_time=0.6)
            self.play(FadeTransform(head, rank_head), run_time=0.8)
            self.play(FadeIn(title_row), run_time=0.6)
            self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in table],
                                  lag_ratio=0.3), run_time=1.6)
            self.play(Create(highlight), run_time=0.9)

        self.add(source("§4.2.2 & Bảng 2, tr.5"))
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
        note = txt("Không dự đoán nhãn — chỉ cho biết node nào khó với GNN",
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
            txt("Ngưỡng cố định", size=22, color=MUTED),
            txt("if h_v < 0.5 → gọi LLM", size=19, color=MUTED),
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

        # --- Chuyển sang Task 4 ---
        next_card = VGroup(
            txt("GLANCE Architecture", size=30, color=C_ROUTER, weight=BOLD),
            txt("Task 4", size=22, color=MUTED),
        ).arrange(DOWN, buff=0.25)
        next_frame = panel(next_card, color=C_ROUTER, buff=0.45)
        card = VGroup(next_frame, next_card).move_to(ORIGIN)

        with self.voiceover(text=VO["end_next"]):
            self.play(FadeOut(VGroup(signals, arrows_in)), run_time=0.5)
            self.play(ReplacementTransform(router, card), run_time=1.0)
            self.play(card.animate.scale(1.15), run_time=0.8)
            self.play(FadeOut(card), run_time=0.8)

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


def vector_row(n=10, color=C_GNN, cell=0.32):
    """Vector biểu diễn: một hàng ô cùng màu, đậm nhạt khác nhau."""
    cells = VGroup()
    for i in range(n):
        t = 0.25 + 0.65 * (((i * 7) % n) / max(n - 1, 1))
        cells.add(Square(
            side_length=cell, stroke_width=1.2, stroke_color=color,
            fill_color=interpolate_color(BG, color, t), fill_opacity=1,
        ))
    cells.arrange(RIGHT, buff=0)
    return cells


def prob_bars(values, colors=None, width=0.85, height=0.7):
    """Biểu đồ cột nhỏ cho một phân phối xác suất trên các lớp."""
    colors = colors or [CLS_A, CLS_B]
    base = Line(LEFT * width / 2, RIGHT * width / 2, stroke_width=1.6, color=C_EDGE)
    bars = VGroup()
    n = len(values)
    bar_w = width / n * 0.52
    for i, (val, color) in enumerate(zip(values, colors)):
        h = max(val * height, 0.02)
        bar = Rectangle(width=bar_w, height=h, stroke_width=0,
                        fill_color=color, fill_opacity=0.9)
        bar.move_to(RIGHT * (-width / 2 + width * (i + 0.5) / n) + UP * h / 2)
        bars.add(bar)
    group = VGroup(base, bars)
    group.bars = bars
    return group


def mlp_net(sizes=(3, 4, 3), x_gap=1.0, y_gap=0.5, color=C_GNN, radius=0.09):
    """Mạng nhỏ để minh hoạ dropout. `.layers` là list các lớp neuron."""
    layers = []
    for i, count in enumerate(sizes):
        col = VGroup(*[Dot(radius=radius, color=color) for _ in range(count)])
        col.arrange(DOWN, buff=y_gap - 2 * radius)
        col.move_to(RIGHT * (i - (len(sizes) - 1) / 2) * x_gap)
        layers.append(col)
    links = VGroup()
    for a, b in zip(layers[:-1], layers[1:]):
        for p in a:
            for q in b:
                links.add(Line(p.get_center(), q.get_center(),
                               stroke_width=1.0, color=C_EDGE, z_index=-1))
    net = VGroup(links, *layers)
    net.layers = layers
    net.links = links
    return net


def star(center, count, hub_color=C_HIGHLIGHT, leaf_color=MUTED,
         length=0.95, radius=0.15, angle_offset=PI / 6):
    """Node trung tâm + `count` hàng xóm toả đều quanh nó."""
    center = np.array(center, dtype=float)
    arms, leaves = VGroup(), VGroup()
    for i in range(count):
        angle = TAU * i / max(count, 1) + angle_offset
        tip = center + np.array([np.cos(angle), np.sin(angle), 0.0]) * length
        arms.add(Line(center, tip, stroke_width=2.2, color=C_EDGE, z_index=-1))
        leaves.add(Dot(tip, radius=radius * 0.72, color=leaf_color))
    hub = Dot(center, radius=radius, color=hub_color)
    group = VGroup(arms, leaves, hub)
    group.arms, group.leaves, group.hub = arms, leaves, hub
    return group


def punch(text, color=INK):
    """Dòng “điểm cần nhấn” chốt mỗi cảnh signal.

    Bề rộng và buff chọn sao cho không đụng stamp source ở góc dưới phải.
    """
    line = txt(text, size=22, color=color, weight=BOLD)
    if line.width > 6.6:
        line.scale_to_fit_width(6.6)
    return line.to_edge(DOWN, buff=0.62)


def flashes(starts, target, color=C_ROUTER, width=6):
    """Xung tín hiệu chạy từ nhiều điểm về một đích."""
    return [
        ShowPassingFlash(
            Line(start, target, stroke_width=width, color=color), time_width=0.5,
        )
        for start in starts
    ]


class S3_06_FiveSignals(GlanceScene):
    """Cảnh 6 — từ phân tích sang kiến trúc: năm routing signals."""

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        head = heading("Step 1 — Năm routing signals", color=ACCENT)
        head.to_edge(UP, buff=0.7)

        v_dot = Dot(LEFT * 4.9 + DOWN * 0.25, radius=0.26, color=INK)
        v_lab = txt("v", size=24, color=INK).next_to(v_dot, DOWN, buff=0.2)

        stack = signal_stack().move_to(RIGHT * 0.1 + DOWN * 0.25)
        links = VGroup(*[
            Line(v_dot.get_center(), box[0].get_left(), buff=0.32,
                 stroke_width=1.8, color=C_EDGE, z_index=-1)
            for box in stack
        ])

        with self.voiceover(text=VO["fs_open"]):
            self.play(Write(head), run_time=1.3)
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

        self.add(source(SRC_ARCH))
        self.wait(0.8)


class S3_07_NodeEmbedding(GlanceScene):
    """Cảnh 7 — Signal 1: node embedding z_G(v)."""

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        head = heading("Signal 1 — Node embedding", color=C_GNN).to_edge(UP, buff=0.7)

        # Dùng lại đúng đồ thị demo của cả video; node 4 đóng vai node v.
        graph = demo_tag(radius=0.13, scale=0.62)
        graph.move_to(LEFT * 4.3 + DOWN * 0.4)
        v_node = graph.nodes[4]
        v_lab = txt("v", size=20, color=INK).next_to(v_node, DOWN, buff=0.14)
        ring = ego_ring(graph, 4, [0, 1, 2, 3], color=C_GNN)
        # Nhãn đặt phía trên vòng: bên dưới là node 10 của demo graph.
        ring_lab = txt("k-hop neighborhood", size=16, color=C_GNN)
        ring_lab.next_to(ring, UP, buff=0.15)

        gnn_box = labeled_box("GNN", C_GNN, width=2.0, height=0.85)
        gnn_box.move_to(RIGHT * 1.2 + UP * 1.9)
        feed = Arrow(graph.get_right(), gnn_box.get_left(), buff=0.25,
                     stroke_width=3, color=MUTED,
                     max_tip_length_to_length_ratio=0.07)

        hops = [graph.nodes[i].get_center() for i in (0, 1, 2, 3)]

        with self.voiceover(text=VO["ne_intro"]):
            self.play(Write(head), run_time=1.2)
            self.play(FadeIn(graph), FadeIn(v_lab), run_time=1.0)
            self.play(Create(ring), FadeIn(ring_lab), run_time=0.9)
            self.play(FadeIn(gnn_box), GrowArrow(feed), run_time=0.9)

        # --- Tổng hợp neighborhood thành một vector ---
        mapping = MathTex(
            r"\{\mathbf{x}_u : u \in \mathcal{N}_k(v)\}",
            r"\;\xrightarrow{\;F\;}\;",
            r"\mathbf{z}_G(v)",
            font_size=32,
        )
        mapping[2].set_color(C_GNN)
        mapping.move_to(RIGHT * 3.0 + UP * 0.35)
        if mapping.width > 6.4:
            mapping.scale_to_fit_width(6.4)

        vec = vector_row(10, color=C_GNN).move_to(RIGHT * 3.0 + DOWN * 1.3)
        vec_lab = MathTex(r"\mathbf{z}_G(v)", font_size=28, color=C_GNN)
        vec_lab.next_to(vec, DOWN, buff=0.25)

        with self.voiceover(text=VO["ne_build"]):
            self.play(*flashes(hops, v_node.get_center(), color=C_GNN, width=5),
                      run_time=1.4)
            self.play(Write(mapping), run_time=1.8)
            self.play(LaggedStart(*[FadeIn(c, scale=0.6) for c in vec],
                                  lag_ratio=0.06), run_time=1.3)
            self.play(FadeIn(vec_lab), run_time=0.6)

        # --- Không phải nhãn dự đoán: vector đi vào router, head là nhánh khác ---
        pred_box = labeled_box("GNN prediction head", MUTED, width=3.6, height=0.8)
        pred_box[1].set(font_size=19)
        pred_box[1].move_to(pred_box[0])
        pred_box.move_to(RIGHT * 2.7 + UP * 2.0)
        y_hat = MathTex(r"\hat y_v", font_size=30, color=MUTED)
        y_hat.next_to(pred_box, RIGHT, buff=0.45)

        router_box = labeled_box("Router", C_ROUTER, width=2.6, height=0.85)
        router_box.move_to(RIGHT * 2.7 + DOWN * 0.9)

        neq = MathTex(r"\mathbf{z}_G(v) \neq \hat y_v", font_size=30)
        neq[0][:7].set_color(C_GNN)

        with self.voiceover(text=VO["ne_not_pred"]):
            self.play(FadeOut(VGroup(graph, v_lab, ring, ring_lab, feed,
                                     gnn_box, mapping)), run_time=0.7)
            self.play(VGroup(vec, vec_lab).animate.move_to(LEFT * 3.6 + UP * 0.5),
                      run_time=0.9)
            neq.next_to(vec_lab, DOWN, buff=0.55)
            self.play(FadeIn(router_box, scale=0.85),
                      GrowArrow(Arrow(vec.get_right(), router_box.get_left(), buff=0.3,
                                      stroke_width=3, color=C_ROUTER,
                                      max_tip_length_to_length_ratio=0.09)),
                      run_time=1.1)
            self.play(FadeIn(pred_box),
                      GrowArrow(Arrow(vec.get_right(), pred_box.get_left(), buff=0.3,
                                      stroke_width=3, color=MUTED,
                                      max_tip_length_to_length_ratio=0.09)),
                      FadeIn(y_hat), run_time=1.1)
            self.play(Write(neq), run_time=1.0)
            self.play(FadeIn(punch(
                "Node embedding = GNN đã nhìn thấy gì trong neighborhood?",
                color=C_GNN)), run_time=0.8)

        self.add(source(SRC_ARCH))
        self.wait(1.0)


class S3_08_Uncertainty(GlanceScene):
    """Cảnh 8 — Signal 2: node uncertainty qua dropout."""

    section, section_name = SECTION, SECTION_NAME

    # Neuron bị tắt ở từng lần chạy (chỉ số trong lớp ẩn 4 neuron).
    DROPOUT = [(1,), (0, 3), (2,), (1, 3), (0,)]
    # Phân phối thu được: ổn định (uncertainty thấp) vs dao động (uncertainty cao).
    STABLE = [[0.86, 0.14], [0.82, 0.18], [0.88, 0.12], [0.84, 0.16], [0.87, 0.13]]
    UNSTABLE = [[0.75, 0.25], [0.30, 0.70], [0.55, 0.45], [0.25, 0.75], [0.65, 0.35]]

    def construct(self):
        self.banner()
        head = heading("Signal 2 — Node uncertainty", color=C_BAD).to_edge(UP, buff=0.7)

        v_dot = Dot(LEFT * 6.2 + UP * 0.4, radius=0.2, color=INK)
        net = mlp_net().move_to(LEFT * 4.5 + UP * 0.4)
        feed = Arrow(v_dot.get_right(), net.get_left(), buff=0.2, stroke_width=2.5,
                     color=MUTED, max_tip_length_to_length_ratio=0.14)
        drop_lab = txt("dropout khi suy luận", size=17, color=C_BAD)
        drop_lab.next_to(net, DOWN, buff=0.4)

        with self.voiceover(text=VO["un_intro"]):
            self.play(Write(head), run_time=1.2)
            self.play(GrowFromCenter(v_dot), GrowArrow(feed), run_time=0.7)
            self.play(FadeIn(net), run_time=1.1)
            self.play(FadeIn(drop_lab), run_time=0.6)

        # --- Năm lần chạy: hai kịch bản phân phối ---
        hidden = net.layers[1]
        rows, labels = VGroup(), VGroup()
        for values, y, color, name in (
            (self.STABLE, 1.45, C_GOOD, "Low uncertainty"),
            (self.UNSTABLE, -1.05, C_BAD, "High uncertainty"),
        ):
            row = VGroup(*[prob_bars(v) for v in values])
            row.arrange(RIGHT, buff=0.4).move_to(RIGHT * 1.9 + UP * y)
            rows.add(row)
            lab = txt(name, size=22, color=color)
            lab.next_to(row, DOWN, buff=0.35)
            labels.add(lab)

        legend = VGroup(
            VGroup(Square(0.16, stroke_width=0, fill_color=CLS_A, fill_opacity=0.9),
                   txt("lớp A", size=15, color=MUTED)).arrange(RIGHT, buff=0.15),
            VGroup(Square(0.16, stroke_width=0, fill_color=CLS_B, fill_opacity=0.9),
                   txt("lớp B", size=15, color=MUTED)).arrange(RIGHT, buff=0.15),
        ).arrange(RIGHT, buff=0.5)
        legend.next_to(rows[0], UP, buff=0.4)

        with self.voiceover(text=VO["un_dropout"]):
            self.play(FadeIn(legend), run_time=0.5)
            for i, off in enumerate(self.DROPOUT):
                dropped = VGroup(*[hidden[j] for j in off])
                self.play(dropped.animate.set_opacity(0.15), run_time=0.28)
                self.play(FadeIn(rows[0][i], scale=0.7),
                          FadeIn(rows[1][i], scale=0.7), run_time=0.42)
                self.play(dropped.animate.set_opacity(1.0), run_time=0.22)
            self.play(FadeIn(labels[0], shift=UP * 0.15),
                      FadeIn(labels[1], shift=UP * 0.15), run_time=0.9)

        # --- Uncertainty cao chỉ là một signal, không phải lệnh gọi LLM ---
        question = txt("?", size=40, color=C_BAD, weight=BOLD)
        question.next_to(labels[1], RIGHT, buff=0.35)

        chip = txt("unc_v cao", size=21, color=C_BAD)
        chip_frame = panel(chip, color=C_BAD, buff=0.25)
        chip_group = VGroup(chip_frame, chip).move_to(LEFT * 4.5 + UP * 1.7)
        router_box = labeled_box("Router", C_ROUTER, width=2.4, height=0.8)
        router_box.move_to(LEFT * 4.5 + UP * 0.1)
        heads = VGroup(
            labeled_box("GNN", C_GNN, width=1.5, height=0.65),
            labeled_box("LLM", C_LLM, width=1.5, height=0.65),
        ).arrange(RIGHT, buff=0.5).move_to(LEFT * 4.5 + DOWN * 1.6)
        for box in heads:
            box[1].set(font_size=20)
            box[1].move_to(box[0])
        wire_in = Arrow(chip_group.get_bottom(), router_box.get_top(), buff=0.12,
                        stroke_width=3, color=C_ROUTER,
                        max_tip_length_to_length_ratio=0.2)
        wires_out = VGroup(*[
            Arrow(router_box.get_bottom(), box.get_top(), buff=0.12, stroke_width=2.6,
                  color=MUTED, max_tip_length_to_length_ratio=0.2)
            for box in heads
        ])
        note = txt("không đi thẳng tới LLM", size=17, color=MUTED)
        note.next_to(heads, DOWN, buff=0.3)

        with self.voiceover(text=VO["un_caveat"]):
            self.play(FadeIn(question, scale=0.6), run_time=0.6)
            self.play(FadeOut(VGroup(v_dot, feed, net, drop_lab)), run_time=0.6)
            self.play(FadeIn(chip_group), run_time=0.7)
            self.play(GrowArrow(wire_in), FadeIn(router_box, scale=0.85), run_time=1.0)
            self.play(*[GrowArrow(w) for w in wires_out], FadeIn(heads), run_time=1.0)
            self.play(FadeIn(note), run_time=0.6)
            self.play(FadeIn(punch(
                "Uncertainty = GNN có ổn định với dự đoán của mình không?",
                color=C_BAD)), run_time=0.8)

        self.add(source(SRC_ARCH))
        self.wait(1.0)


class S3_09_SoftHomophily(GlanceScene):
    """Cảnh 9 — Signal 3: soft homophily estimation (phương trình 1)."""

    section, section_name = SECTION, SECTION_NAME

    P_V = [0.8, 0.2]
    P_NB = [[0.2, 0.8], [0.4, 0.6], [0.3, 0.7]]   # trung bình = [0.3, 0.7]
    P_MEAN = [0.3, 0.7]

    def construct(self):
        self.banner()
        head = heading("Signal 3 — Soft homophily estimation", color=C_GOOD)
        head.to_edge(UP, buff=0.7)

        # --- Bản cứng của §4.2.2, để đối chiếu ---
        hard = MathTex(
            r"\hat h_v", r"=", r"\frac{1}{|\mathcal{N}(v)|}\sum_{u \in \mathcal{N}(v)}",
            r"\mathbf{1}[\hat y_u = \hat y_v]",
            font_size=32,
        )
        hard[0].set_color(C_GOOD)
        hard.move_to(RIGHT * 2.6 + UP * 1.7)
        if hard.width > 6.6:
            hard.scale_to_fit_width(6.6)
        hard_tag = txt("bản cứng — chỉ so hai nhãn", size=17, color=MUTED)
        hard_tag.next_to(hard, DOWN, buff=0.3)
        soft_tag = txt("bản mềm — dùng cả phân phối xác suất", size=17, color=C_GOOD)
        soft_tag.move_to(hard_tag)

        with self.voiceover(text=VO["sh_intro"]):
            self.play(Write(head), run_time=1.3)
            self.play(Write(hard), run_time=1.6)
            self.play(FadeIn(hard_tag), run_time=0.6)
            self.play(Indicate(hard[3], color=C_GOOD, scale_factor=1.15), run_time=0.9)
            self.play(FadeTransform(hard_tag, soft_tag), run_time=0.8)

        # --- MLP Q trả về phân phối cho v và cho từng hàng xóm ---
        q_box = labeled_box("MLP Q", C_ROUTER, width=1.9, height=0.55)
        q_box[1].set(font_size=19)
        q_box[1].move_to(q_box[0])
        q_box.move_to(LEFT * 4.3 + UP * 2.35)

        row_v = VGroup(
            prob_bars(self.P_V),
            MathTex(r"\mathbf{p}_{Q,v} = [0.8,\, 0.2]", font_size=26, color=INK),
        ).arrange(RIGHT, buff=0.35).move_to(LEFT * 4.3 + UP * 1.5)

        nbs = VGroup()
        for i, p in enumerate(self.P_NB):
            nbs.add(VGroup(
                prob_bars(p),
                MathTex(rf"\mathbf{{p}}_{{Q,u_{i + 1}}}", font_size=22, color=MUTED),
            ).arrange(DOWN, buff=0.14))
        nbs.arrange(RIGHT, buff=0.45).move_to(LEFT * 4.3 + DOWN * 0.3)

        mean_row = VGroup(
            prob_bars(self.P_MEAN),
            MathTex(r"\overline{\mathbf{p}}_{Q,\mathcal{N}(v)} = [0.3,\, 0.7]",
                    font_size=24, color=INK),
        ).arrange(RIGHT, buff=0.35).move_to(LEFT * 4.3 + DOWN * 2.1)
        mean_arrow = Arrow(nbs.get_bottom(), mean_row.get_top(), buff=0.15,
                           stroke_width=2.6, color=MUTED,
                           max_tip_length_to_length_ratio=0.22)
        mean_lab = txt("trung bình", size=15, color=MUTED)
        mean_lab.next_to(mean_arrow, RIGHT, buff=0.15)

        with self.voiceover(text=VO["sh_dist"]):
            self.play(FadeIn(q_box), run_time=0.6)
            self.play(FadeIn(row_v, shift=UP * 0.15), run_time=0.9)
            self.play(LaggedStart(*[FadeIn(n, shift=UP * 0.15) for n in nbs],
                                  lag_ratio=0.25), run_time=1.4)
            self.play(GrowArrow(mean_arrow), FadeIn(mean_lab), run_time=0.7)
            self.play(FadeIn(mean_row, shift=UP * 0.15), run_time=0.9)

        # --- Phương trình 1 ---
        eq = MathTex(
            r"\hat h_v", r"=", r"\mathbf{p}_{Q,v}", r"\cdot",
            r"\left(\frac{1}{|\mathcal{N}_1(v)|}"
            r"\sum_{u \in \mathcal{N}_1(v)} \mathbf{p}_{Q,u}\right)",
            font_size=34,
        )
        eq[0].set_color(C_GOOD)
        eq.move_to(RIGHT * 2.6 + UP * 1.7)
        if eq.width > 6.8:
            eq.scale_to_fit_width(6.8)
        eq_note = txt("hai phân phối càng giống nhau → giá trị càng cao",
                      size=17, color=MUTED)
        eq_note.next_to(eq, DOWN, buff=0.32)

        with self.voiceover(text=VO["sh_dot"]):
            self.play(FadeOut(soft_tag), run_time=0.3)
            self.play(TransformMatchingTex(hard, eq), run_time=1.6)
            self.play(Indicate(eq[2], color=C_GOOD, scale_factor=1.2),
                      Indicate(row_v[0], color=C_GOOD, scale_factor=1.15), run_time=1.1)
            self.play(Indicate(eq[4], color=C_GOOD, scale_factor=1.05),
                      Indicate(mean_row[0], color=C_GOOD, scale_factor=1.15),
                      run_time=1.1)
            self.play(FadeIn(eq_note), run_time=0.6)

        # --- Thay số cho chính ví dụ bên trái ---
        numeric = MathTex(r"\hat h_v", r"=", r"0.8(0.3) + 0.2(0.7)", r"=", r"0.38",
                          font_size=34)
        numeric[0].set_color(C_GOOD)
        numeric[4].set_color(C_BAD)
        numeric.move_to(RIGHT * 2.6 + DOWN * 0.4)
        if numeric.width > 6.6:
            numeric.scale_to_fit_width(6.6)
        low_note = txt("thấp → node không hợp xu hướng của neighborhood",
                       size=17, color=C_BAD)
        low_note.next_to(numeric, DOWN, buff=0.3)

        with self.voiceover(text=VO["sh_example"]):
            self.play(Write(numeric), run_time=1.6)
            self.play(Indicate(numeric[4], color=C_BAD, scale_factor=1.25), run_time=1.0)
            self.play(FadeIn(low_note), run_time=0.7)

        # --- Cứng chỉ có 0/1, mềm giữ được mức độ chắc chắn ---
        compare = VGroup(
            VGroup(txt("hard", size=19, color=MUTED),
                   txt("0  hoặc  1", size=21, color=MUTED)).arrange(RIGHT, buff=0.45),
            VGroup(txt("soft", size=19, color=C_GOOD),
                   txt("0.82   0.56   0.31", size=21, color=C_GOOD)
                   ).arrange(RIGHT, buff=0.45),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        compare.move_to(RIGHT * 2.6 + DOWN * 2.3)
        compare_frame = panel(compare, color=C_EDGE, buff=0.28)

        with self.voiceover(text=VO["sh_soft"]):
            self.play(FadeIn(compare_frame), FadeIn(compare[0]), run_time=0.9)
            self.play(FadeIn(compare[1], shift=RIGHT * 0.2), run_time=0.9)
            self.play(FadeIn(punch(
                "Homophily estimation = Node có phù hợp với neighborhood không?",
                color=C_GOOD)), run_time=0.8)

        self.add(source("§5.1.1, tr.5"))
        self.wait(1.0)


class S3_10_NodeFeatures(GlanceScene):
    """Cảnh 10 — Signal 4: original node features x_v."""

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        head = heading("Signal 4 — Original node features", color=C_LLM)
        head.to_edge(UP, buff=0.7)

        v_dot = Dot(LEFT * 4.3 + UP * 2.0, radius=0.22, color=C_LLM)
        v_lab = txt("v", size=20, color=INK).next_to(v_dot, LEFT, buff=0.2)
        chip = text_chip("Attention Is All You Need\n"
                         "We propose the Transformer, a new\n"
                         "network architecture based solely...", width=4.2)
        chip.move_to(LEFT * 4.3 + UP * 0.75)
        open_arrow = Arrow(v_dot.get_bottom(), chip.get_top(), buff=0.12,
                           stroke_width=2.4, color=MUTED,
                           max_tip_length_to_length_ratio=0.25)

        x_vec = vector_row(8, color=C_LLM).move_to(RIGHT * 2.6 + UP * 0.75)
        x_lab = MathTex(r"\mathbf{x}_v", font_size=30, color=C_LLM)
        x_lab.next_to(x_vec, DOWN, buff=0.25)
        encode = Arrow(chip.get_right(), x_vec.get_left(), buff=0.35, stroke_width=3,
                       color=MUTED, max_tip_length_to_length_ratio=0.07)
        encode_lab = txt("mã hoá text", size=16, color=MUTED)
        encode_lab.next_to(encode, UP, buff=0.15)

        with self.voiceover(text=VO["nf_intro"]):
            self.play(Write(head), run_time=1.3)
            self.play(GrowFromCenter(v_dot), FadeIn(v_lab), run_time=0.7)
            self.play(GrowArrow(open_arrow), FadeIn(chip, shift=DOWN * 0.15),
                      run_time=1.0)
            self.play(GrowArrow(encode), FadeIn(encode_lab), run_time=0.8)
            self.play(LaggedStart(*[FadeIn(c, scale=0.6) for c in x_vec],
                                  lag_ratio=0.07), run_time=1.1)
            self.play(FadeIn(x_lab), run_time=0.5)

        # --- x_v là ego, z_G(v) là ego + neighborhood ---
        cards = VGroup()
        for label, tag, color in (
            (r"\mathbf{x}_v", "Ego information", C_LLM),
            (r"\mathbf{z}_G(v)", "Ego + neighborhood aggregation", C_GNN),
        ):
            body = VGroup(
                MathTex(label, font_size=30, color=color),
                txt(tag, size=18, color=INK),
            ).arrange(DOWN, buff=0.25)
            if body.width > 4.4:
                body.scale_to_fit_width(4.4)
            cards.add(VGroup(panel(body, color=color, buff=0.3), body))
        cards.arrange(RIGHT, buff=0.9, aligned_edge=UP).move_to(DOWN * 2.1)

        with self.voiceover(text=VO["nf_compare"]):
            self.play(FadeIn(cards[0], shift=UP * 0.2), run_time=1.0)
            self.play(FadeIn(cards[1], shift=UP * 0.2), run_time=1.0)
            self.play(Indicate(cards[0], color=C_LLM, scale_factor=1.04), run_time=0.9)

        # --- Khi text của node xung đột với neighborhood ---
        conflict = star(LEFT * 4.6 + DOWN * 0.2, 4, hub_color=C_LLM,
                        leaf_color=C_HIGHLIGHT)
        ego_note = txt("text của node → lớp A", size=17, color=C_LLM)
        ego_note.next_to(conflict, UP, buff=0.3)
        nb_note = txt("hàng xóm → lớp B", size=17, color=C_HIGHLIGHT)
        nb_note.next_to(conflict, DOWN, buff=0.3)

        chips = VGroup(
            VGroup(vector_row(6, color=C_LLM, cell=0.26),
                   MathTex(r"\mathbf{x}_v", font_size=24, color=C_LLM)
                   ).arrange(RIGHT, buff=0.3),
            VGroup(vector_row(6, color=C_GNN, cell=0.26),
                   MathTex(r"\mathbf{z}_G(v)", font_size=24, color=C_GNN)
                   ).arrange(RIGHT, buff=0.3),
        ).arrange(DOWN, buff=1.1).move_to(RIGHT * 0.5 + DOWN * 0.2)

        router_box = labeled_box("Router", C_ROUTER, width=2.4, height=0.85)
        router_box.move_to(RIGHT * 4.6 + DOWN * 0.2)
        wires = VGroup(*[
            Arrow(c.get_right(), router_box.get_left(), buff=0.25, stroke_width=2.6,
                  color=MUTED, max_tip_length_to_length_ratio=0.1)
            for c in chips
        ])

        with self.voiceover(text=VO["nf_conflict"]):
            self.play(FadeOut(VGroup(v_dot, v_lab, chip, open_arrow, encode,
                                     encode_lab, x_vec, x_lab, cards)), run_time=0.7)
            self.play(FadeIn(conflict), FadeIn(ego_note), FadeIn(nb_note), run_time=1.1)
            self.play(FadeIn(chips), run_time=0.8)
            self.play(*[GrowArrow(w) for w in wires], FadeIn(router_box, scale=0.85),
                      run_time=1.0)
            self.play(FadeIn(punch("Node features = Bản thân node chứa thông tin gì?",
                                   color=C_LLM)), run_time=0.8)

        self.add(source(SRC_ARCH))
        self.wait(1.0)


class S3_11_Degree(GlanceScene):
    """Cảnh 11 — Signal 5: degree thô d_v (không phải relative degree)."""

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        head = heading("Signal 5 — Degree", color=C_HIGHLIGHT).to_edge(UP, buff=0.7)

        # angle_offset = PI/2 để không cạnh nào chĩa thẳng xuống chỗ đặt nhãn "v".
        node = star(LEFT * 4.4 + UP * 0.9, 3, hub_color=C_HIGHLIGHT,
                    angle_offset=PI / 2)
        v_lab = txt("v", size=20, color=INK).next_to(node.hub, DOWN, buff=0.22)
        counter = MathTex(r"d_v = |\mathcal{N}(v)| = 3", font_size=34, color=C_HIGHLIGHT)
        counter.move_to(LEFT * 4.4 + DOWN * 0.75)

        with self.voiceover(text=VO["dg_intro"]):
            self.play(Write(head), run_time=1.2)
            self.play(GrowFromCenter(node.hub), FadeIn(v_lab), run_time=0.7)
            for arm, leaf in zip(node.arms, node.leaves):
                self.play(Create(arm), GrowFromCenter(leaf), run_time=0.45)
            self.play(Write(counter), run_time=1.1)

        # --- Ít hàng xóm = ít context để tổng hợp ---
        low = star(RIGHT * 0.9 + UP * 0.3, 1, hub_color=C_HIGHLIGHT, length=0.85)
        high = star(RIGHT * 4.6 + UP * 0.3, 6, hub_color=C_HIGHLIGHT, length=0.85)
        low_lab = MathTex(r"d_v = 1", font_size=26, color=MUTED)
        low_lab.next_to(low, UP, buff=0.25)
        high_lab = MathTex(r"d_v = 6", font_size=26, color=MUTED)
        high_lab.next_to(high, UP, buff=0.25)

        # Hai thanh đo đặt cùng một cao độ (next_to sẽ lệch vì hai star cao khác nhau).
        meters = VGroup()
        for x, frac in ((0.9, 0.18), (4.6, 0.85)):
            track = Rectangle(width=2.2, height=0.2, stroke_width=1.4,
                              stroke_color=C_EDGE, fill_opacity=0)
            track.move_to(RIGHT * x + DOWN * 1.35)
            fill = Rectangle(width=2.2 * frac, height=0.2, stroke_width=0,
                             fill_color=C_HIGHLIGHT, fill_opacity=0.85)
            fill.align_to(track, LEFT).set_y(track.get_y())
            meters.add(VGroup(track, fill))
        meter_lab = txt("Neighborhood context", size=17, color=MUTED)
        meter_lab.next_to(meters, DOWN, buff=0.3)

        with self.voiceover(text=VO["dg_context"]):
            self.play(FadeIn(VGroup(low, low_lab)), run_time=0.8)
            self.play(FadeIn(VGroup(high, high_lab)), run_time=0.8)
            self.play(Create(meters[0][0]), Create(meters[1][0]), run_time=0.6)
            self.play(GrowFromEdge(meters[0][1], LEFT),
                      GrowFromEdge(meters[1][1], LEFT), run_time=1.1)
            self.play(FadeIn(meter_lab), run_time=0.6)

        # --- Nhiều hàng xóm nhưng khác lớp thì không giúp được gì ---
        warn = cross(color=C_BAD, size=0.34).next_to(high, RIGHT, buff=0.35)
        warn_note = txt("degree cao nhưng hàng xóm khác lớp", size=17, color=C_BAD)
        warn_note.next_to(meter_lab, DOWN, buff=0.35)

        with self.voiceover(text=VO["dg_caveat"]):
            self.play(*[leaf.animate.set_color(C_LLM) for leaf in high.leaves],
                      run_time=1.0)
            self.play(FadeIn(warn, scale=0.6), FadeIn(warn_note), run_time=0.9)
            self.play(Indicate(meters[1][1], color=C_BAD, scale_factor=1.05),
                      run_time=1.0)

        # --- Đừng lẫn với relative degree của §4.2.1 ---
        rows = VGroup(
            VGroup(MathTex(r"\bar d_v", font_size=28, color=C_LLM),
                   txt("phân tích §4.2.1 — so v với hàng xóm", size=19, color=MUTED)
                   ).arrange(RIGHT, buff=0.35),
            VGroup(MathTex(r"d_v", font_size=28, color=C_HIGHLIGHT),
                   txt("router GLANCE — đếm thẳng số hàng xóm", size=19, color=INK)
                   ).arrange(RIGHT, buff=0.35),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        rows[1][0].align_to(rows[0][0], LEFT)
        rows[1][1].align_to(rows[0][1], LEFT)
        rows.move_to(DOWN * 0.4)
        rows_frame = panel(rows, color=C_EDGE, buff=0.35)
        rows_head = txt("Hai đại lượng khác nhau", size=21, color=INK, weight=BOLD)
        rows_head.next_to(rows_frame, UP, buff=0.35)

        with self.voiceover(text=VO["dg_vs_rd"]):
            self.play(FadeOut(VGroup(node, v_lab, counter, low, low_lab, high,
                                     high_lab, meters, meter_lab, warn, warn_note)),
                      run_time=0.7)
            self.play(FadeIn(rows_head), FadeIn(rows_frame), run_time=0.8)
            self.play(FadeIn(rows[0], shift=RIGHT * 0.2), run_time=0.9)
            self.play(FadeIn(rows[1], shift=RIGHT * 0.2), run_time=0.9)
            self.play(FadeIn(punch(
                "Degree = GNN có bao nhiêu thông tin lân cận để sử dụng?",
                color=C_HIGHLIGHT)), run_time=0.8)

        self.add(source(SRC_ARCH))
        self.wait(1.0)


class S3_12_Combine(GlanceScene):
    """Cảnh 12 — router ghép năm signals, tính score và chọn top-k."""

    section, section_name = SECTION, SECTION_NAME

    SCORES = [0.12, 0.78, 0.31, 0.91, 0.22, 0.64, 0.08, 0.85]
    K = 3

    def construct(self):
        self.banner()
        head = heading("Router: kết hợp năm signals", color=C_ROUTER)
        head.to_edge(UP, buff=0.7)

        stack = signal_stack(width=3.1, height=0.55, buff=0.2, text_size=18)
        stack.move_to(LEFT * 4.4 + DOWN * 0.2)

        # f_v ghép nối: mỗi đoạn giữ màu của signal tương ứng.
        segs = VGroup()
        for (_, color, _), count in zip(SIGNALS, (6, 1, 1, 6, 1)):
            seg = VGroup(*[
                Square(side_length=0.28, stroke_width=1.1, stroke_color=BG,
                       fill_color=color, fill_opacity=0.85)
                for _ in range(count)
            ]).arrange(RIGHT, buff=0)
            segs.add(seg)
        segs.arrange(RIGHT, buff=0.09).move_to(RIGHT * 2.3 + UP * 1.1)

        concat = MathTex(
            r"\mathbf{f}_v", r"=",
            r"[\,\mathbf{z}_G(v)\,\|\,\mathrm{unc}_v\,\|\,\hat h_v"
            r"\,\|\,\mathbf{x}_v\,\|\,d_v\,]",
            font_size=30,
        )
        concat[0].set_color(C_ROUTER)
        concat.next_to(segs, DOWN, buff=0.45)
        if concat.width > 6.8:
            concat.scale_to_fit_width(6.8)

        with self.voiceover(text=VO["cb_concat"]):
            self.play(Write(head), run_time=1.2)
            self.play(FadeIn(stack, shift=RIGHT * 0.15), run_time=1.0)
            for box, seg in zip(stack, segs):
                self.play(*flashes([box[0].get_right()], seg.get_center(),
                                   color=box[0].get_stroke_color(), width=4),
                          FadeIn(seg, scale=0.7), run_time=0.4)
            self.play(Write(concat), run_time=1.4)

        # --- Routing score qua sigmoid ---
        score_eq = MathTex(r"a_v", r"=", r"\pi(\mathbf{f}_v)", r"=",
                           r"\sigma(\mathbf{w}^\top \mathbf{f}_v)", font_size=34)
        score_eq[0].set_color(C_ROUTER)
        score_eq.move_to(RIGHT * 2.3 + DOWN * 1.1)

        gauge = NumberLine(x_range=[0, 1, 0.25], length=4.6, include_numbers=True,
                           font_size=18, color=C_EDGE,
                           decimal_number_config={"num_decimal_places": 2})
        gauge.next_to(score_eq, DOWN, buff=0.8)
        marker = Dot(gauge.n2p(0.0), radius=0.12, color=C_ROUTER)
        gauge_lab = txt("score cao → nhiều khả năng hưởng lợi từ LLM",
                        size=17, color=MUTED)
        gauge_lab.next_to(gauge, DOWN, buff=0.3)

        with self.voiceover(text=VO["cb_score"]):
            self.play(Write(score_eq), run_time=1.5)
            self.play(Create(gauge), FadeIn(marker), run_time=0.9)
            self.play(marker.animate.move_to(gauge.n2p(0.88)), run_time=1.2)
            self.play(FadeIn(gauge_lab), run_time=0.7)

        # --- Top-k trong mini-batch ---
        order = sorted(range(len(self.SCORES)), key=lambda i: -self.SCORES[i])
        routed = set(order[:self.K])

        batch = VGroup()
        for i, s in enumerate(self.SCORES):
            dot = Dot(radius=0.17, color=MUTED)
            lab = txt(f"{s:.2f}", size=16, color=MUTED).next_to(dot, DOWN, buff=0.18)
            batch.add(VGroup(dot, lab))
        batch.arrange(RIGHT, buff=0.62).move_to(UP * 1.5)
        batch_lab = txt("một mini-batch", size=18, color=MUTED)
        batch_lab.next_to(batch, UP, buff=0.35)

        llm_box = labeled_box("LLM", C_LLM, width=2.2, height=0.85)
        llm_box.move_to(RIGHT * 3.4 + DOWN * 1.6)
        gnn_box = labeled_box("GNN", C_GNN, width=2.2, height=0.85)
        gnn_box.move_to(LEFT * 3.4 + DOWN * 1.6)
        budget = txt("top-k cố định mỗi batch → ngân sách LLM không đổi",
                     size=18, color=MUTED)
        budget.next_to(VGroup(gnn_box, llm_box), DOWN, buff=0.5)

        with self.voiceover(text=VO["cb_topk"]):
            self.play(FadeOut(VGroup(stack, segs, concat, score_eq, gauge, marker,
                                     gauge_lab)), run_time=0.7)
            self.play(FadeIn(batch), FadeIn(batch_lab), run_time=0.8)
            self.play(FadeIn(llm_box), FadeIn(gnn_box), run_time=0.6)
            self.play(*[
                batch[i][0].animate.set_color(C_LLM if i in routed else C_GNN)
                for i in range(len(self.SCORES))
            ], *[
                batch[i][1].animate.set_color(C_LLM if i in routed else MUTED)
                for i in range(len(self.SCORES))
            ], run_time=1.0)
            self.play(
                *flashes([batch[i][0].get_center() for i in routed],
                         llm_box.get_top(), color=C_LLM, width=5),
                *flashes([batch[i][0].get_center() for i in range(len(self.SCORES))
                          if i not in routed],
                         gnn_box.get_top(), color=C_GNN, width=4),
                run_time=1.6,
            )
            self.play(FadeIn(budget), run_time=0.7)

        # --- Câu chốt: năm câu hỏi mà router nhận được câu trả lời ---
        questions = VGroup()
        for (name, color, _), question in zip(SIGNALS, (
            "GNN đã học được gì?",
            "GNN tin tưởng đến đâu?",
            "Node có hợp với neighborhood không?",
            "Bản thân node chứa gì?",
            "Có bao nhiêu context cấu trúc?",
        )):
            row = VGroup(
                txt(name, size=19, color=color),
                txt(question, size=19, color=INK),
            )
            row[1].move_to(row[0], aligned_edge=LEFT).shift(RIGHT * 4.3)
            questions.add(row)
        questions.arrange(DOWN, aligned_edge=LEFT, buff=0.32).move_to(UP * 0.55)
        closing = txt("Router học cách kết hợp — không dùng heuristic cố định.",
                      size=22, color=C_ROUTER, weight=BOLD)
        closing.next_to(questions, DOWN, buff=0.75)

        with self.voiceover(text=VO["cb_close"]):
            self.play(FadeOut(VGroup(batch, batch_lab, llm_box, gnn_box, budget)),
                      run_time=0.7)
            self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in questions],
                                  lag_ratio=0.3), run_time=3.2)
            self.play(FadeIn(closing, shift=UP * 0.15), run_time=1.2)

        self.add(source(SRC_ARCH))
        self.wait(1.2)
