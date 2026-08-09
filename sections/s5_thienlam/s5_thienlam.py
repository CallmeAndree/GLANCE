"""Section 5 — Training objective (§5.2) và Thực nghiệm (§6, §7, Appendix C.4).

Owner: Thiên Lâm. Đặc tả đầy đủ ở TASK.md trong thư mục này.

Render thử:
    conda activate graphdm
    manim -ql sections/s5_thienlam/s5_thienlam.py -a
    manim -ql sections/s5_thienlam/s5_thienlam.py S5_02_TopKProblem
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from glance_style import *  # noqa: E402,F403

SECTION = "5"
SECTION_NAME = "Training objective & experiments"
OWNER = "Thiên Lâm"
ACCENT = SECTION_COLORS.get(SECTION, C_HIGHLIGHT)


# ---------------------------------------------------------------------------
# Khối xây dựng nhỏ dùng riêng cho section này — chỉ ghép từ txt()/màu có sẵn
# trong glance_style.py, không tự chế thêm màu hay helper dùng chung mới.
# ---------------------------------------------------------------------------

def pill(text, color, width=None, size=SMALL_SIZE):
    """Nhãn viên thuốc: khung bo tròn viền màu quanh một dòng chữ ngắn."""
    # `text` cũng nhận một mobject, dùng khi nhãn là công thức (MathTex).
    label = text if isinstance(text, Mobject) else txt(
        text, size=size, color=color, weight=BOLD
    )
    if width and label.width > width - 0.4:
        label.scale_to_fit_width(width - 0.4)
    box = RoundedRectangle(
        corner_radius=0.18,
        width=width or (label.width + 0.5),
        height=label.height + 0.34,
        stroke_color=color, stroke_width=2,
        fill_color=color, fill_opacity=0.10,
    )
    label.move_to(box)
    return VGroup(box, label)


def metric_card(label, value, color, note=None, width=3.0):
    """Thẻ số liệu: nhãn nhỏ phía trên, con số lớn, chú thích nhỏ phía dưới."""
    lab = txt(label, size=SMALL_SIZE - 4, color=MUTED, weight=BOLD)
    val = txt(value, size=HEAD_SIZE, color=color, weight=BOLD)
    parts = [lab, val]
    if note:
        parts.append(txt(note, size=SMALL_SIZE - 5, color=MUTED))
    body = VGroup(*parts).arrange(DOWN, buff=0.10)
    box = RoundedRectangle(
        corner_radius=0.16, width=width, height=body.height + 0.5,
        stroke_color=color, stroke_width=2, fill_color=color, fill_opacity=0.08,
    )
    body.move_to(box)
    return VGroup(box, body)


def freeze(mobj):
    """Animation làm mờ một khối để biểu thị 'đóng băng, không cập nhật'."""
    return mobj.animate.set_opacity(0.35)


def fit_box_label(box_group, width, pad=0.3):
    """labeled_box() không tự co chữ theo width — nhãn dài (vd "REFINER  C")
    tràn ra ngoài khung và đè lên khung bên cạnh. Co lại cho vừa."""
    label = box_group[1]
    if label.width > width - pad:
        label.scale_to_fit_width(width - pad)
    return box_group


# ---------------------------------------------------------------------------
# VO — mọi lời thuyết minh gom một chỗ. Đã viết theo cách ĐỌC LÊN và phiên âm
# thuật ngữ tiếng Anh theo bảng chung trong glance_style.py / SKILL.md, vì
# backend TTS mặc định (timed API) không tự bọc SSML cho tiếng Anh.
# ---------------------------------------------------------------------------

VO = {
    "title_intro": (
        "Phần năm: cách gờ lans được huấn luyện, và kết quả thực nghiệm chứng minh "
        "cách huấn luyện đó đúng."
    ),
    # --- S5_02 TopK ---
    "topk_setup": "Bộ định tuyến chỉ có ca tấm vé gọi lờ lờ mờ. tốp ca giữ số lần gọi cố định trong mỗi bát.",
    "topk_jump": (
        "Nhưng điểm đổi nhẹ thì tập tốp ca vẫn giữ nguyên; đến đúng lúc đổi hạng, "
        "quyết định lại nhảy đột ngột từ có sang không."
    ),
    "topk_block": (
        "Vì phép chọn tốp ca không liên tục, gra-đi-en không truyền được xuyên qua nó — "
        "hàm mất mát cuối không thể dạy trực tiếp cho bộ định tuyến."
    ),
    # --- S5_03 Counterfactual ---
    "cf_intro": "Thay vì đạo hàm qua tốp ca, gờ lans chấm kết quả của từng quyết định bằng phần thưởng.",
    "cf_branch": (
        "Với một nót được định tuyến, gờ lans dựng hai thế giới đối chứng: thế giới không gọi lờ lờ mờ, "
        "dùng đầu dự đoán hắc có sẵn của gờ nờ nờ; và thế giới đã gọi lờ lờ mờ, đi qua bộ tinh chỉnh xi."
    ),
    "cf_same_label": (
        "Cả hai hàm mất mát đều là en-trô-pi chéo so với cùng một nhãn thật — hàm mất mát càng thấp thì dự đoán "
        "càng tốt. Hàm mất mát thế giới đã gọi lờ lờ mờ không phải của riêng lờ lờ mờ, mà là của cả nhánh "
        "gờ nờ nờ cộng lờ lờ mờ cộng bộ tinh chỉnh."
    ),
    # --- S5_04 Reward ---
    "reward_route": (
        "Nếu định tuyến: phần thưởng bằng mức lờ lờ mờ giúp hàm mất mát giảm bao nhiêu, trừ đi bê ta — "
        "chi phí quy đổi của một lần gọi lờ lờ mờ."
    ),
    "reward_beta": (
        "Bê ta lớn thì bộ định tuyến dè dặt hơn, chỉ định tuyến khi lợi ích thật rõ ràng; bê ta nhỏ thì bộ định tuyến "
        "sẵn sàng gọi lờ lờ mờ nhiều hơn. Nếu mức cải thiện nhỏ hơn bê ta, phần thưởng vẫn âm."
    ),
    "reward_skip": (
        "Nếu bỏ qua: không có hàm mất mát của lờ lờ mờ để so sánh, nên gờ lans dùng âm hàm mất mát của gờ nờ nờ "
        "để chấm quyết định bỏ qua."
    ),
    # --- S5_05 Joint objective ---
    "obj_policy": (
        "Phần thưởng tốt thì bộ định tuyến lặp lại hành động vừa chọn; phần thưởng xấu thì hành động đó bị giảm "
        "ưu tiên — đây chính là gra-đi-en chính sách."
    ),
    "obj_entropy": (
        "hàm mất mát của bộ định tuyến gồm gra-đi-en chính sách cộng một số hạng en-trô-pi, giữ cho bộ định tuyến chưa chốt "
        "quá sớm, còn khám phá các lựa chọn khác."
    ),
    "obj_pred": (
        "hàm mất mát dự đoán rẽ nhánh theo việc nót có nằm trong tốp ca hay không: nót được định tuyến "
        "dùng hàm mất mát của nhánh gờ nờ nờ cộng lờ lờ mờ, nót còn lại dùng hàm mất mát của riêng gờ nờ nờ."
    ),
    "obj_total": (
        "hàm mất mát tổng cộng gộp hàm mất mát dự đoán với hàm mất mát của bộ định tuyến có trọng số — vừa dạy dự đoán đúng, "
        "vừa dạy phân bổ ngân sách gọi lờ lờ mờ."
    ),
    "obj_freeze": (
        "Chỉ bộ định tuyến pi và bộ tinh chỉnh xi được cập nhật; gờ nờ nờ và lờ lờ mờ bị đóng băng hoàn toàn — "
        "Gờ lans không huấn luyện lại hai mô hình nền."
    ),
    "obj_hparam": (
        "Cấu hình mặc định: bát ba mươi hai, định tuyến tốp mười hai mỗi bát, bê ta thử ở "
        "không chấm một, không chấm hai, không chấm ba. Ngân sách ca giảm dần theo lịch, "
        "từ ba mươi hai xuống còn tám."
    ),
    "obj_question": "Nhưng liệu cách huấn luyện này có thật sự tạo ra một bộ định tuyến học đúng không?",
    # --- S5_06 Setup ---
    "setup_question": (
        "Câu hỏi trung tâm của phần thực nghiệm: gờ lans có gộp được điểm mạnh của gờ nờ nờ và "
        "lờ lờ mờ trong cùng một mô hình không?"
    ),
    "setup_data": (
        "Sân thử gồm ba đồ thị chuẩn — cô ra, pắp mét, ác xíp hai ba — cùng hai đồ thị cực lớn: "
        "ác xíp ia và ô gi bi pró đắc."
    ),
    "setup_baseline": (
        "Đối thủ đều mạnh: các gờ nờ nờ kinh điển gờ xê en, gráp xây giơ, gờ xê en hai chạy trên "
        "ba chiến lược khác nhau; thêm nhóm gờ nờ nờ chuyên xử lý dị phối gồm ép a gờ xê en, "
        "gờ gờ xê en, gờ bê ca gờ en en."
    ),
    "setup_budget": (
        "Mấu chốt: mặc định gờ lans chỉ gọi lờ lờ mờ cho mười hai trên ba mươi hai nót mỗi bát — "
        "nó phải thắng trong khi gọi lờ lờ mờ ít hơn hẳn đối thủ."
    ),
    # --- S5_07 Balanced results ---
    "res_overall": (
        "Về độ chính xác tổng thể, gờ lans dẫn đầu cả ba bộ: cô ra tám mươi chín chấm năm, pắp mét "
        "chín mươi hai chấm sáu, ác xíp hai ba tám mươi hai chấm một — trung bình hơn mô hình tốt "
        "kế tiếp khoảng không chấm năm phần trăm."
    ),
    "res_margin": "Nhưng khoảng cách tổng thể chỉ dưới một điểm, nên đó chưa phải điều quan trọng nhất.",
    "res_hardbin": (
        "Chia nót theo hô mô phi li cục bộ thành các nhóm, ở nhóm khó nhất của cô ra gờ lans đạt "
        "bốn mươi sáu chấm bốn — cao hơn mô hình tốt kế tiếp tới mười ba điểm."
    ),
    "res_rank": (
        "Trung bình trên toàn bộ các nhóm, gờ lans xếp hạng hai chấm bốn — tốt nhất, bỏ xa á quân "
        "bốn chấm bảy, mà nhóm dễ vẫn giữ gần như tuyệt đối."
    ),
    "res_verdict": "Con số tổng thể che chênh lệch ở nót khó; hô mô phi li làm nó lộ ra.",
    # --- S5_08 Router learned ---
    "router_question": "Vậy bộ định tuyến có thật sự học đúng chỗ không?",
    "router_hist": (
        "Khi soi các nót được định tuyến, khối lượng dồn hẳn về vùng hô mô phi li thấp — đúng vùng mà "
        "gờ nờ nờ hay sai còn lờ lờ mờ có thể sửa."
    ),
    "router_graph": (
        "Nhìn trên đồ thị mẫu, nót chín — hô mô phi li thấp, hàng xóm khác lớp — là kiểu nót "
        "bộ định tuyến ưu tiên gọi lờ lờ mờ; nót bốn thì hầu như không cần."
    ),
    "router_budget": (
        "Tăng ngân sách ca giúp nhiều nhất ở vùng hô mô phi li thấp; vùng hô mô phi li cao gần như "
        "không đổi — ngân sách chỉ có giá trị đúng chỗ khó."
    ),
    "router_ablation": (
        "Cắt bỏ lần lượt từng đặc trưng định tuyến đều làm độ chính xác giảm; bỏ đặc trưng hô mô phi "
        "li ước lượng gây thiệt hại lớn nhất."
    ),
    "router_verdict": "Chính tín hiệu hô mô phi li dạy bộ định tuyến biết khi nào nên gọi lờ lờ mờ.",
    # --- S5_09 Controls ---
    "ctrl_intro": "Bằng chứng mạnh nhất không phải là thêm lờ lờ mờ, mà là chọn đúng nót để gọi.",
    "ctrl_all": (
        "định tuyến hết mọi nót trên cô ra: nhóm khó nhất tăng nhẹ, nhóm giữa tăng mạnh tới mười bốn "
        "chấm năm điểm — nhưng nhóm dễ lại giảm, kéo tổng thể tụt một chấm hai điểm dù tốn gần gấp ba "
        "số lượt gọi lờ lờ mờ."
    ),
    "ctrl_random": (
        "Giữ nguyên lờ lờ mờ và bộ tinh chỉnh nhưng định tuyến ngẫu nhiên trên cô ra: chỉ còn tám mươi sáu "
        "chấm bốn, thua cả bây xơ lai gờ xê en hai tám mươi bảy chấm bảy."
    ),
    "ctrl_same_set": (
        "Trên đúng tập nót mà bộ định tuyến đã chọn, nhánh gờ nờ nờ cộng lờ lờ mờ qua bộ tinh chỉnh đạt tám "
        "mươi bảy chấm sáu — cao hơn hẳn nếu để gờ xê en hai tự xử lý."
    ),
    "ctrl_verdict": "định tuyến hết thì hại nót dễ; định tuyến bừa thì thua bây xơ lai — giá trị nằm ở sự chọn lọc học được.",
    # --- S5_10 Scale ---
    "scale_setup": (
        "Trên ô gi bi pró đắc — hai chấm bốn năm triệu nót, gần sáu mươi hai triệu cạnh — gờ lans "
        "chỉ gọi lờ lờ mờ cho khoảng một chấm sáu phần trăm nót, tức một nót trong mỗi sáu mươi tư."
    ),
    "scale_result": (
        "Vậy mà vẫn dẫn đầu: tám mươi hai chấm ba, cao hơn gờ xê en hai tám mươi mốt chấm tám, "
        "còn gờ gờ xê en thì hết bộ nhớ. Trên ác xíp ia, gờ lans đạt bốn mươi chín chấm tám."
    ),
    "scale_verdict": "Chọn lọc học được không chỉ cân bằng và chính xác, mà còn rẻ và mở rộng tới quy mô triệu nót.",
    # --- S5_11 Callout ---
    "final_reconnect": (
        "Ở đầu vi đi eo, câu hỏi đặt ra là: có cách nào kết hợp gờ nờ nờ và lờ lờ mờ mà biết tính "
        "chi phí không? Đây là câu trả lời của gờ lans, gói trong năm ý."
    ),
    "final_1": "Một: gờ nờ nờ và lờ lờ mờ giỏi ở những nót khác nhau; hô mô phi li cục bộ dự báo ai sẽ thắng.",
    "final_2": "Hai: vì tốp ca không khả vi, phần thưởng chấm điểm từng quyết định để dạy bộ định tuyến.",
    "final_3": "Ba: chỉ bộ định tuyến và bộ tinh chỉnh được huấn luyện; gờ nờ nờ và lờ lờ mờ đóng băng.",
    "final_4": "Bốn: kết quả là mô hình cân bằng nhất và dẫn đầu tổng thể, nhờ sự chọn lọc học được.",
    "final_5": "Năm: chỉ định tuyến một phần nhỏ nót, gờ lans vẫn mở rộng tới đồ thị hàng triệu nót.",
    "final_punch": "Tất cả gói trong một câu — đừng dùng nhiều lờ lờ mờ hơn, hãy dùng lờ lờ mờ đúng chỗ.",
}


class S5_01_Title(GlanceScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        card = title_card(
            f"{SECTION} — {SECTION_NAME}",
            "Why GLANCE learns, and why the results validate it",
            OWNER,
            accent=ACCENT,
        )
        with self.voiceover(text=VO["title_intro"]):
            self.play(FadeIn(card, shift=UP * 0.3), run_time=1.4)
        self.play(FadeOut(card), run_time=0.6)


class S5_02_TopKProblem(GlanceScene):
    """Vấn đề cốt lõi: chọn top-K không khả vi, chặn đường gradient."""

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        head = heading("Core problem: top-K is non-differentiable", color=ACCENT).to_edge(UP, buff=0.85)

        # Pill ngân sách nâng cao hẳn và nhỏ lại; hàng node hạ xuống, để hàng
        # dấu tick (đặt trên node) không chạm mép dưới pill như bản trước.
        budget = pill("FIXED BUDGET  ·  K = 2", C_LLM, width=4.0).move_to([0, 2.15, 0])

        labels = ["A", "B", "C", "D", "E", "F"]
        scores = [0.91, 0.82, 0.79, 0.61, 0.44, 0.20]
        nodes = VGroup(*[labeled_box(l, C_ROUTER, width=1.05, height=0.85) for l in labels])
        nodes.arrange(RIGHT, buff=0.35).move_to([0, 0.55, 0])
        score_texts = VGroup(*[
            txt(f"{s:.2f}", size=SMALL_SIZE, color=MUTED, weight=BOLD).next_to(n, DOWN, buff=0.12)
            for n, s in zip(nodes, scores)
        ])
        # buff nhỏ lại rồi hạ thêm 0.15: đỉnh dấu tick không còn chạm mép dưới
        # của pill ngân sách. Vị trí `budget` và `nodes` giữ nguyên.
        tickets = VGroup(*[check(color=C_LLM, size=0.30).next_to(n, UP, buff=0.10) for n in nodes[:2]])
        tickets.shift(DOWN * 0.15)

        with self.voiceover(text=VO["topk_setup"]) as tracker:
            self.play(Write(head), FadeIn(budget, scale=0.92), run_time=1.0)
            self.play(
                LaggedStart(*[GrowFromCenter(n) for n in nodes], lag_ratio=0.12),
                run_time=1.4,
            )
            self.play(
                LaggedStart(*[FadeIn(t, shift=UP * 0.06) for t in score_texts], lag_ratio=0.1),
                FadeIn(tickets, shift=DOWN * 0.14),
                run_time=min(1.6, max(0.6, tracker.duration - 2.4)),
            )

        step_axis = Axes(
            x_range=[0, 6, 1], y_range=[0, 1, 1], x_length=8.5, y_length=1.8,
            tips=False, axis_config={"color": C_EDGE, "include_ticks": False},
        ).move_to([0, -1.1, 0])
        step = VMobject(color=C_ROUTER, stroke_width=4)
        step.set_points_as_corners([
            step_axis.c2p(0, 0), step_axis.c2p(2.5, 0),
            step_axis.c2p(2.5, 1), step_axis.c2p(6, 1),
        ])
        cut = DashedLine(step_axis.c2p(2.5, -0.15), step_axis.c2p(2.5, 1.15), color=C_BAD, stroke_width=2)
        # Dựng bằng ba mobject rồi arrange: một lần txt() cho cả câu khiến các
        # cụm từ dính vào nhau ở cỡ chữ này.
        jump_label = VGroup(
            txt("rank swap", size=SMALL_SIZE - 4, color=C_BAD),
            txt("→", size=SMALL_SIZE - 4, color=C_BAD),
            txt("decision jumps", size=SMALL_SIZE - 4, color=C_BAD),
        ).arrange(RIGHT, buff=0.12)
        jump_label.next_to(cut, DOWN, buff=0.55)
        marker = Dot(step_axis.c2p(2.35, 0), radius=0.09, color=YELLOW)

        with self.voiceover(text=VO["topk_jump"]) as tracker:
            self.play(FadeOut(tickets), FadeOut(budget), run_time=0.3)
            self.play(
                nodes.animate.scale(0.75).to_edge(UP, buff=1.7),
                score_texts.animate.scale(0.75).next_to(nodes.copy().scale(0.75).to_edge(UP, buff=1.7), DOWN),
                Create(step_axis), Create(step),
                run_time=1.6,
            )
            self.play(Create(cut), FadeIn(jump_label, shift=UP * 0.1), FadeIn(marker, scale=0.6),
                      run_time=min(1.4, tracker.duration))

        # Điểm B tụt nhẹ từ 0.82 xuống 0.78 — thấp hơn C (0.79) — nên đổi hạng.
        # Giữ nguyên vị trí các ô (không hoán đổi B/C): trong không gian hẹp,
        # cho hai ô bay qua nhau từng đè lên nhau giữa đường đi. Chỉ cần đổi
        # số điểm của B và chuyển "vé" sang C là đủ thể hiện quyết định nhảy.
        score_078 = txt("0.78", size=SMALL_SIZE - 5, color=C_BAD, weight=BOLD).move_to(score_texts[1])
        # Đặt tick bên DƯỚI dòng điểm số, không phải phía trên node — lúc này
        # hàng node đã bị thu nhỏ/đẩy sát lên đỉnh khung hình (gần banner tiêu
        # đề), đặt phía trên sẽ đè lên chữ tiêu đề.
        new_ticket = check(color=C_LLM, size=0.30).next_to(score_texts[2], DOWN, buff=0.22)
        self.play(
            Transform(score_texts[1], score_078),
            Indicate(nodes[1], color=C_BAD, scale_factor=1.08),
            marker.animate.move_to(step_axis.c2p(2.65, 1)),
            run_time=1.2,
        )
        self.play(FadeIn(new_ticket, scale=0.7), run_time=0.5)
        self.play(Flash(marker, color=C_BAD, flash_radius=0.35), run_time=0.6)
        self.wait(0.5)

        chain = pipeline(
            [("ROUTER π", C_ROUTER), ("TOP-K", C_BAD), ("FINAL LOSS", C_GOOD)],
        ).move_to([0, -1.1, 0])
        blocked = cross(color=C_BAD, size=0.5).move_to(chain.boxes[1])
        grad_arrow = Arrow(
            chain.boxes[2].get_left(), chain.boxes[1].get_right(),
            buff=0.10, color=YELLOW, stroke_width=5,
        )

        with self.voiceover(text=VO["topk_block"]) as tracker:
            self.play(
                FadeOut(VGroup(nodes, score_texts, step_axis, step, cut, jump_label, marker, new_ticket)),
                run_time=0.5,
            )
            self.play(FadeIn(chain), run_time=1.0)
            self.play(GrowArrow(grad_arrow), run_time=0.7)
            self.play(FadeIn(blocked, scale=1.4), Flash(chain.boxes[1], color=C_BAD, flash_radius=0.7),
                      run_time=min(1.2, tracker.duration))
        banner = txt("LOSS  ×→  TOP-K  ×→  ROUTER", size=BODY_SIZE, color=C_BAD, weight=BOLD)
        banner.next_to(chain, DOWN, buff=0.7)
        self.play(FadeIn(banner, shift=UP * 0.1), run_time=0.6)
        self.wait(0.6)


class S5_03_CounterfactualLoss(GlanceScene):
    """Một nốt route, hai thế giới đối chứng, hai loss cùng nhãn thật."""

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        head = heading("Solution: replace gradients with rewards", color=C_GOOD).to_edge(UP, buff=0.85)
        self.add(head)

        node = labeled_box("v", C_ROUTER, width=0.9, height=0.9).move_to([-5.6, 0, 0])
        route_tag = pill("ROUTE", C_LLM, width=1.7).next_to(node, UP, buff=0.25)

        with self.voiceover(text=VO["cf_intro"]):
            self.play(GrowFromCenter(node), FadeIn(route_tag, shift=DOWN * 0.15), run_time=1.2)

        # panel() bọc thêm buff=0.4 quanh Rectangle, nên hai khung 1.5 cao đặt
        # ở y=±0.7 (bản cũ) thực chất chồng lên nhau ở dải giữa. Thu buff còn
        # 0.26 và tách tâm ra ±1.15 để hai panel rời hẳn, không đè.
        upper = panel(Rectangle(width=7.0, height=1.35), buff=0.26).move_to([-0.1, 1.15, 0])
        lower = panel(Rectangle(width=7.0, height=1.35), color=C_LLM, buff=0.26).move_to([-0.1, -0.95, 0])
        up_text = MathTex(r"\text{NO LLM CALL}\;\cdot\;\text{GNN}\to\text{head }H\to p_H"
                          r"\;\cdot\;\ell_v^{GNN}=\mathrm{CE}(y_v,\,p_H)",
                          font_size=30, color=C_GNN).move_to(upper).scale_to_fit_width(6.4)
        low_text = MathTex(r"\text{LLM CALLED}\;\cdot\;\text{GNN}+\text{LLM}\to\text{refiner }C\to p_C"
                           r"\;\cdot\;\ell_v^{LLM}=\mathrm{CE}(y_v,\,p_C)",
                           font_size=30, color=C_LLM).move_to(lower).scale_to_fit_width(6.4)
        arrow_up = Arrow(node.get_right(), upper.get_left(), buff=0.1, color=C_GNN, stroke_width=3)
        arrow_down = Arrow(node.get_right(), lower.get_left(), buff=0.1, color=C_LLM, stroke_width=3)

        # Bản sao mờ của v "bay" vào mỗi nhánh — cùng một node đi hai đường.
        ghost_up = node.copy().scale(0.6).set_opacity(0.9)
        ghost_down = node.copy().scale(0.6).set_opacity(0.9)

        # Đồng hồ loss bên phải mỗi nhánh: số chạy sống + thanh dài dần tới giá trị thật.
        gnn_value, llm_value = ValueTracker(0.0), ValueTracker(0.0)
        gnn_num = DecimalNumber(0, num_decimal_places=2, color=C_GNN, font_size=BODY_SIZE - 4)
        # Cột thanh loss đẩy hẳn sang phải (track x=5.0, số x=6.3) để không dính
        # vào mép phải panel (mép ~3.66 sau khi panel lùi trái).
        gnn_num.add_updater(lambda m: m.set_value(gnn_value.get_value())).move_to([6.3, 1.15, 0])
        llm_num = DecimalNumber(0, num_decimal_places=2, color=C_LLM, font_size=BODY_SIZE - 4)
        llm_num.add_updater(lambda m: m.set_value(llm_value.get_value())).move_to([6.3, -0.95, 0])
        gnn_track = RoundedRectangle(width=1.5, height=0.20, corner_radius=0.05,
                                      stroke_color=C_GNN, stroke_width=1.4, fill_opacity=0).move_to([5.0, 1.15, 0])
        llm_track = RoundedRectangle(width=1.5, height=0.20, corner_radius=0.05,
                                      stroke_color=C_LLM, stroke_width=1.4, fill_opacity=0).move_to([5.0, -0.95, 0])
        gnn_fill = RoundedRectangle(width=1.5 * 2.30 / 2.50, height=0.20, corner_radius=0.05,
                                     fill_color=C_GNN, fill_opacity=0.85, stroke_width=0)
        gnn_fill.move_to(gnn_track.get_center()).align_to(gnn_track, LEFT)
        llm_fill = RoundedRectangle(width=1.5 * 0.30 / 2.50, height=0.20, corner_radius=0.05,
                                     fill_color=C_LLM, fill_opacity=0.85, stroke_width=0)
        llm_fill.move_to(llm_track.get_center()).align_to(llm_track, LEFT)

        with self.voiceover(text=VO["cf_branch"]) as tracker:
            self.play(
                Create(arrow_up), Create(arrow_down),
                FadeIn(upper), FadeIn(lower),
                ghost_up.animate.move_to(upper.get_left() + RIGHT * 0.35).set_opacity(0),
                ghost_down.animate.move_to(lower.get_left() + RIGHT * 0.35).set_opacity(0),
                run_time=1.4,
            )
            self.remove(ghost_up, ghost_down)
            self.play(
                FadeIn(up_text), FadeIn(low_text), FadeIn(gnn_track), FadeIn(llm_track),
                run_time=0.8,
            )
            self.play(
                gnn_value.animate.set_value(2.30), GrowFromEdge(gnn_fill, LEFT), FadeIn(gnn_num),
                llm_value.animate.set_value(0.30), GrowFromEdge(llm_fill, LEFT), FadeIn(llm_num),
                run_time=min(1.8, tracker.duration),
            )

        truth = MathTex(r"\text{same true label }y_v", font_size=30, color=C_GOOD)
        truth.move_to([-5.6, -0.9, 0])
        with self.voiceover(text=VO["cf_same_label"]) as tracker:
            self.play(FadeIn(truth, scale=0.95), run_time=0.9)
            self.play(Indicate(up_text, color=C_GNN), Indicate(low_text, color=C_LLM),
                      run_time=min(1.6, tracker.duration))
        banner = txt(
            "ℓᵥᴸᴸᴹ IS THE LOSS OF THE FULL GNN + LLM + REFINER C BRANCH, NOT THE LLM ALONE",
            size=SMALL_SIZE - 4, color=C_LLM, weight=BOLD,
        ).move_to([0.1, -2.35, 0]).scale_to_fit_width(11.5)
        self.play(FadeIn(banner, shift=UP * 0.1), run_time=0.7)
        self.wait(0.6)


class S5_04_Reward(GlanceScene):
    """Reward là lợi ích ròng của việc gọi LLM, trừ chi phí beta."""

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        head = heading("Reward: Is an LLM call worth it?", color=C_GOOD).to_edge(UP, buff=0.85)
        self.add(head)

        row1 = VGroup(
            pill(MathTex(r"\ell_v^{GNN}=2.30", font_size=30, color=C_GNN), C_GNN, width=2.5),
            txt("−", size=BODY_SIZE, color=MUTED),
            pill(MathTex(r"\ell_v^{LLM}=0.30", font_size=30, color=C_LLM), C_LLM, width=2.5),
            txt("=", size=BODY_SIZE, color=MUTED),
            pill("gain 2.00", C_GOOD, width=2.3),
        ).arrange(RIGHT, buff=0.25).move_to([0, 1.3, 0])
        route_label = txt("IF ROUTED", size=SMALL_SIZE, color=C_LLM, weight=BOLD).next_to(row1, UP, buff=0.3)

        with self.voiceover(text=VO["reward_route"]) as tracker:
            self.play(FadeIn(route_label), run_time=0.6)
            self.play(LaggedStart(*[FadeIn(m, shift=UP * 0.08) for m in row1], lag_ratio=0.16),
                      run_time=min(1.8, tracker.duration))

        row2 = VGroup(
            row1[4].copy(),
            txt("−", size=BODY_SIZE, color=MUTED),
            pill("β = 0.10", C_LLM, width=1.9),
            txt("=", size=BODY_SIZE, color=MUTED),
            pill("reward = +1.90", C_GOOD, width=2.9),
        ).arrange(RIGHT, buff=0.25).move_to([0, 0.4, 0])
        note = txt("ILLUSTRATIVE VALUES", size=SMALL_SIZE - 5, color=MUTED).next_to(row2, RIGHT, buff=0.4)
        beta_note = txt(
            "larger β → more cautious router   ·   smaller β → more LLM calls",
            size=SMALL_SIZE - 3, color=MUTED,
        ).move_to([0, -0.35, 0])

        counter_row = txt(
            "EXAMPLE: gain 0.05 − β 0.10 = reward −0.05  →  remains negative even when routed",
            size=SMALL_SIZE - 5, color=C_BAD,
        ).move_to([0, -0.85, 0])

        with self.voiceover(text=VO["reward_beta"]) as tracker:
            self.play(TransformFromCopy(row1[4], row2[0]), run_time=0.7)
            self.play(
                LaggedStart(*[FadeIn(m) for m in row2[1:]], lag_ratio=0.16),
                FadeIn(note),
                run_time=1.2,
            )
            self.play(FadeIn(beta_note, shift=UP * 0.08), run_time=0.8)
            self.play(FadeIn(counter_row, shift=UP * 0.06), run_time=min(1.0, tracker.duration))

        skip_row = VGroup(
            txt("IF SKIPPED", size=SMALL_SIZE, color=MUTED, weight=BOLD),
            pill(MathTex(r"\text{reward}=-\ell_v^{GNN}", font_size=30, color=C_BAD), C_BAD, width=3.2),
        ).arrange(RIGHT, buff=0.4).move_to([0, -1.4, 0])

        with self.voiceover(text=VO["reward_skip"]) as tracker:
            self.play(FadeIn(skip_row, shift=UP * 0.1), run_time=min(1.4, tracker.duration))

        banner = MathTex(r"\text{ROUTE:}\;r_v=\ell_v^{GNN}-\ell_v^{LLM}-\beta"
                          r"\qquad\text{SKIP:}\;r_v=-\ell_v^{GNN}",
                          font_size=36, color=C_ROUTER).move_to([0, -2.3, 0])
        self.play(FadeIn(banner, shift=UP * 0.1), run_time=0.8)
        self.wait(0.6)


class S5_05_JointObjective(GlanceScene):
    """Router loss + prediction loss = loss tổng; chỉ train router và refiner."""

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        head = heading("Learning from rewards: total loss and trainable modules", color=C_ROUTER).to_edge(UP, buff=0.85)
        self.add(head)

        chain = pipeline(
            [("reward rᵥ", C_GOOD), ("log π(fᵥ)", C_ROUTER), ("ℓᵥʳᵒᵘᵗᵉ", C_BAD)],
        ).scale(0.85).move_to([0, 1.75, 0])
        good_rule = VGroup(
            MathTex(r"r_v>0", font_size=32, color=C_GOOD),
            txt("→", size=SMALL_SIZE - 2, color=MUTED),
            MathTex(r"\pi(f_v)\ \text{increases}", font_size=32, color=C_GOOD),
        ).arrange(RIGHT, buff=0.16)
        bad_rule = VGroup(
            MathTex(r"r_v<0", font_size=32, color=C_BAD),
            txt("→", size=SMALL_SIZE - 2, color=MUTED),
            MathTex(r"\pi(f_v)\ \text{decreases}", font_size=32, color=C_BAD),
        ).arrange(RIGHT, buff=0.16)
        rules = VGroup(good_rule, bad_rule).arrange(RIGHT, buff=1.0).move_to([0, 1.0, 0])

        with self.voiceover(text=VO["obj_policy"]) as tracker:
            self.play(FadeIn(chain.boxes[0], scale=0.9), run_time=0.6)
            self.play(GrowArrow(chain.arrows[0]), FadeIn(chain.boxes[1]), run_time=0.7)
            self.play(GrowArrow(chain.arrows[1]), FadeIn(chain.boxes[2]), run_time=0.7)
            self.play(FadeIn(rules, shift=UP * 0.08), run_time=min(1.2, tracker.duration))
        self.play(FadeOut(rules), chain.animate.move_to([0, 1.5, 0]), run_time=0.5)

        formula = MathTex(
            r"\ell_v^{route}=-r_v\cdot\log\pi(f_v)\;-\;\lambda_H\cdot H[\pi(f_v)]",
            font_size=34, color=INK,
        ).move_to([0, 0.75, 0])
        with self.voiceover(text=VO["obj_entropy"]) as tracker:
            self.play(Write(formula), run_time=min(1.6, tracker.duration))

        # panel() bọc thêm buff quanh Rectangle. Bản cũ width 5.2 + buff 0.4 =
        # 6.0, đặt ở x=±3.0 nên hai khung chạm nhau ngay tại tâm. Thu nhỏ khung
        # và buff, tách tâm để có khe rõ giữa hai card.
        pred_card = panel(Rectangle(width=4.5, height=1.0), color=C_GNN, buff=0.28).move_to([-2.7, -0.45, 0])
        route_card = panel(Rectangle(width=4.5, height=1.0), color=C_ROUTER, buff=0.28).move_to([2.7, -0.45, 0])
        pred_text = MathTex(r"\text{PREDICTION LOSS}\;\cdot\;\text{top-}k\!:\ \ell_v^{LLM},"
                            r"\ \text{all others }\ell_v^{GNN}",
                            font_size=28, color=C_GNN).move_to(pred_card).scale_to_fit_width(4.7)
        route_text = MathTex(r"\lambda_{router}\times\text{ROUTER LOSS}"
                             r"\;\cdot\;\text{learns budget allocation}",
                             font_size=28, color=C_ROUTER).move_to(route_card).scale_to_fit_width(4.7)
        with self.voiceover(text=VO["obj_pred"]) as tracker:
            self.play(FadeIn(pred_card), FadeIn(pred_text), run_time=min(1.6, tracker.duration))

        # Hai mũi tên gộp về TOTAL LOSS: đối xứng qua trục giữa, xuất phát từ
        # đáy tâm mỗi card, chụm vào hai góc trên của pill. Hạ pill xuống đủ sâu
        # để mũi tên dốc hẳn, không còn nằm ngang lệch như bản trước.
        total = pill("TOTAL LOSS", INK, width=3.0).move_to([0, -2.6, 0])
        pred_to_total = Arrow(
            pred_card.get_bottom(), total.get_top() + LEFT * 0.75,
            buff=0.14, color=C_GNN, stroke_width=4, max_tip_length_to_length_ratio=0.14,
        )
        route_to_total = Arrow(
            route_card.get_bottom(), total.get_top() + RIGHT * 0.75,
            buff=0.14, color=C_ROUTER, stroke_width=4, max_tip_length_to_length_ratio=0.14,
        )
        with self.voiceover(text=VO["obj_total"]) as tracker:
            self.play(FadeIn(route_card), FadeIn(route_text), run_time=1.0)
            self.play(
                GrowArrow(pred_to_total), GrowArrow(route_to_total),
                FadeIn(total, shift=UP * 0.1),
                run_time=min(1.2, tracker.duration),
            )

        modules = VGroup(
            fit_box_label(labeled_box("GNN  F", C_GNN, width=2.1, height=0.75), 2.1),
            fit_box_label(labeled_box("LLM  L", C_LLM, width=2.1, height=0.75), 2.1),
            fit_box_label(labeled_box("REFINER  C", C_GOOD, width=2.1, height=0.75), 2.1),
            fit_box_label(labeled_box("ROUTER  π", C_ROUTER, width=2.1, height=0.75), 2.1),
        ).arrange(RIGHT, buff=0.3).move_to([0, -2.35, 0])
        status_labels = VGroup(
            pill("FREEZE", MUTED, width=1.45, size=SMALL_SIZE - 5),
            pill("FREEZE", MUTED, width=1.45, size=SMALL_SIZE - 5),
            pill("UPDATE", C_GOOD, width=1.45, size=SMALL_SIZE - 5),
            pill("UPDATE", C_ROUTER, width=1.45, size=SMALL_SIZE - 5),
        )
        for status, module in zip(status_labels, modules):
            status.next_to(module, DOWN, buff=0.18)
        update_label = pill("TOTAL LOSS  →  UPDATE PARAMETERS", C_GOOD, width=4.8)
        update_label.move_to([0, 0.35, 0])
        to_refiner = Arrow(
            update_label.get_bottom() + LEFT * 0.8,
            modules[2].get_top(), buff=0.12, color=C_GOOD, stroke_width=3,
        )
        to_router = Arrow(
            update_label.get_bottom() + RIGHT * 0.8,
            modules[3].get_top(), buff=0.12, color=C_ROUTER, stroke_width=3,
        )

        with self.voiceover(text=VO["obj_freeze"]) as tracker:
            self.play(
                FadeOut(VGroup(
                    chain, formula, pred_card, pred_text, route_card, route_text,
                    total, pred_to_total, route_to_total,
                )),
                FadeIn(update_label), FadeIn(modules),
                run_time=0.8,
            )
            self.play(GrowArrow(to_refiner), GrowArrow(to_router), run_time=0.8)
            # scale_factor mặc định của Indicate (~1.2) khiến 2 khối liền kề
            # (buff=0.3) phình to đè lên nhau — ép nhỏ lại để không chạm nhau.
            self.play(freeze(modules[0]), freeze(modules[1]),
                      Indicate(modules[2], color=C_GOOD, scale_factor=1.08),
                      Indicate(modules[3], color=C_ROUTER, scale_factor=1.08),
                      run_time=min(1.6, tracker.duration))
            # Đặt vị trí status_labels TĨNH trước khi play. Nếu vừa
            # `.animate.move_to` vừa `FadeIn` cùng một mobject trong một play,
            # hai animation xung đột: move_to bị bỏ qua, các pill kẹt ở vị trí
            # cũ dưới đáy còn dòng hparam chèn vào giữa. Đặt tĩnh rồi chỉ FadeIn
            # thì pill về đúng ngay dưới module (y=-1.12).
            status_labels.move_to([0, -1.12, 0])
            self.play(
                FadeOut(VGroup(update_label, to_refiner, to_router)),
                modules.animate.move_to([0, -0.25, 0]),
                FadeIn(status_labels, shift=UP * 0.1),
                run_time=0.7,
            )

        hparam = VGroup(
            txt("batch 32  ·  route top-12 per batch  ·  β = {0.1, 0.2, 0.3}",
                size=SMALL_SIZE - 4, color=MUTED),
            txt("budget schedule: K decreases from 32 to 8, factor r = 0.5",
                size=SMALL_SIZE - 5, color=MUTED),
        ).arrange(DOWN, buff=0.12).move_to([0, -2.25, 0])
        with self.voiceover(text=VO["obj_hparam"]) as tracker:
            self.play(FadeIn(hparam, shift=UP * 0.06), run_time=min(1.6, tracker.duration))

        with self.voiceover(text=VO["obj_question"]) as tracker:
            self.wait(tracker.duration)
        self.wait(0.4)


class S5_06_Setup(GlanceScene):
    """Bối cảnh thực nghiệm: câu hỏi trung tâm, dữ liệu, đối thủ, ngân sách."""

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        head = heading("Experimental setup", color=C_GNN).to_edge(UP, buff=0.85)
        self.add(head)

        row = VGroup(
            labeled_box("GNN", C_GNN, width=2.0), txt("+", size=HEAD_SIZE, color=MUTED),
            labeled_box("LLM", C_LLM, width=2.0),
        ).arrange(RIGHT, buff=0.3).move_to([-2.0, 1.3, 0])
        goal = pill("ONE MODEL?", C_ROUTER, width=3.0).move_to([2.8, 1.3, 0])
        arrow = Arrow(row.get_right(), goal.get_left(), buff=0.15, color=MUTED, stroke_width=3)
        with self.voiceover(text=VO["setup_question"]) as tracker:
            self.play(FadeIn(row), run_time=0.9)
            self.play(GrowArrow(arrow), FadeIn(goal, scale=0.9), run_time=min(1.4, tracker.duration))

        std = VGroup(*[
            metric_card(n, c, C_GNN, width=2.3)
            for n, c in [("CORA", "2.7K"), ("PUBMED", "19.7K"), ("ARXIV23", "19.6K")]
        ]).arrange(RIGHT, buff=0.3)
        big = VGroup(*[
            metric_card(n, c, C_GOOD, width=2.6)
            for n, c in [("ARXIV-YEAR", "169K"), ("OGB-PRODUCTS", "2.45M")]
        ]).arrange(RIGHT, buff=0.3)
        datasets = VGroup(std, big).arrange(RIGHT, buff=0.6).move_to([0, 0.0, 0])
        with self.voiceover(text=VO["setup_data"]) as tracker:
            self.play(FadeOut(VGroup(row, goal, arrow)), run_time=0.5)
            self.play(FadeIn(datasets, shift=UP * 0.1), run_time=min(1.8, tracker.duration))

        classic = VGroup(*[pill(n, C_GNN, width=2.3) for n in ["GCN", "GraphSAGE", "GCNII"]]).arrange(DOWN, buff=0.18)
        strat = VGroup(*[pill(n, MUTED, width=2.7) for n in ["original features", "LLM-enhanced", "LOGIN"]]).arrange(DOWN, buff=0.18)
        hetero = VGroup(*[pill(n, C_ROUTER, width=2.3) for n in ["FAGCN", "GGCN", "GBK-GNN"]]).arrange(DOWN, buff=0.18)
        baselines = VGroup(classic, strat, hetero).arrange(RIGHT, buff=0.6).move_to([0, -1.0, 0])
        with self.voiceover(text=VO["setup_baseline"]) as tracker:
            self.play(FadeOut(datasets, shift=UP * 0.1), run_time=0.5)
            self.play(FadeIn(baselines, shift=UP * 0.1), run_time=min(2.0, tracker.duration))

        dots = VGroup(*[Dot(radius=0.075, color=MUTED, fill_opacity=0.4) for _ in range(32)])
        dots.arrange_in_grid(rows=4, cols=8, buff=0.16).move_to([-3.1, -1.0, 0])
        for i in range(12):
            dots[i].set_color(C_LLM).set_fill(opacity=1)
        budget = metric_card("LLM QUERY BUDGET", "12 / 32", C_LLM, note="per batch", width=3.4)
        budget.move_to([2.6, -1.0, 0])
        with self.voiceover(text=VO["setup_budget"]) as tracker:
            self.play(FadeOut(baselines, shift=UP * 0.1), run_time=0.5)
            self.play(
                LaggedStart(*[FadeIn(d, scale=0.5) for d in dots], lag_ratio=0.02),
                run_time=1.2,
            )
            self.play(FadeIn(budget, shift=LEFT * 0.1), run_time=min(1.4, tracker.duration))
        self.wait(0.5)


class S5_07_BalancedResults(GlanceScene):
    """Accuracy tổng thể (Bảng 4) và cân bằng theo homophily (Bảng 3)."""

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        head = heading("Balance & overall accuracy", color=C_ROUTER).to_edge(UP, buff=0.85)
        self.add(head)

        chart = bar_chart(
            [89.5, 92.6, 82.1], ["Cora", "Pubmed", "Arxiv23"],
            colors=[C_ROUTER, C_ROUTER, C_ROUTER], y_range=(0, 100, 20),
            width=8.0, height=2.6, value_fmt="{:.1f}",
        ).move_to([0, 0.9, 0])
        with self.voiceover(text=VO["res_overall"]) as tracker:
            self.play(Create(chart.axes), run_time=0.6)
            self.play(
                LaggedStart(*[FadeIn(b, shift=UP * 0.12) for b in chart.bars], lag_ratio=0.2),
                run_time=min(2.0, tracker.duration),
            )

        margin = pill("OVERALL MARGIN IS BELOW 1 POINT", C_LLM, width=7.0).move_to([0, -1.15, 0])
        with self.voiceover(text=VO["res_margin"]) as tracker:
            self.play(FadeIn(margin, scale=0.96), run_time=min(1.2, tracker.duration))

        hard_chart = bar_chart(
            [33.4, 46.4], ["Runner-up", "GLANCE"], colors=[MUTED, C_ROUTER],
            y_range=(0, 50, 10), width=4.2, height=2.4, value_fmt="{:.1f}",
        ).move_to([-3.3, -1.45, 0])
        hard_title = MathTex(r"\text{CORA}\;\cdot\;\text{HARDEST GROUP }(h_v<0.25)",
                            font_size=26, color=C_BAD)
        hard_title.next_to(hard_chart, UP, buff=0.45)
        gain_arrow = DoubleArrow(
            hard_chart.bars[0][0].get_top() + UP * 0.45,
            hard_chart.bars[1][0].get_top() + UP * 0.45,
            buff=0, color=C_GOOD, stroke_width=2.5, tip_length=0.12,
        )
        gain_label = txt("+13.0", size=SMALL_SIZE - 3, color=C_GOOD, weight=BOLD)
        gain_label.next_to(gain_arrow, UP, buff=0.06)

        with self.voiceover(text=VO["res_hardbin"]) as tracker:
            self.play(FadeOut(VGroup(chart, margin)), run_time=0.5)
            self.play(FadeIn(hard_title), Create(hard_chart.axes), run_time=0.6)
            self.play(
                LaggedStart(*[FadeIn(b, shift=UP * 0.1) for b in hard_chart.bars], lag_ratio=0.25),
                run_time=1.0,
            )
            self.play(
                Create(gain_arrow), FadeIn(gain_label),
                run_time=min(1.2, tracker.duration),
            )

        rank = metric_card("AVERAGE RANK", "2.4", C_ROUTER, note="runner-up: 4.7", width=3.4)
        rank.move_to([2.9, -0.55, 0])
        easy = pill("EASY GROUPS REMAIN NEAR-PERFECT", C_GNN, width=4.2).move_to([2.9, -1.65, 0])
        with self.voiceover(text=VO["res_rank"]) as tracker:
            self.play(FadeIn(rank, shift=LEFT * 0.1), run_time=0.9)
            self.play(FadeIn(easy, shift=UP * 0.1), run_time=min(1.3, tracker.duration))

        banner = txt("MOST BALANCED  ≠  BEST IN EVERY GROUP", size=BODY_SIZE - 2, color=C_ROUTER, weight=BOLD)
        banner.move_to([0, -1.0, 0])
        with self.voiceover(text=VO["res_verdict"]) as tracker:
            self.play(
                FadeOut(VGroup(hard_chart, hard_title, rank, easy, gain_arrow, gain_label), shift=UP * 0.15),
                run_time=0.5,
            )
            self.play(FadeIn(banner, shift=UP * 0.1), run_time=min(1.2, tracker.duration))
        self.wait(0.4)


class S5_08_RouterLearned(GlanceScene):
    """Router học đúng tín hiệu: phân bố route + sensitivity K + ablation (§6.3)."""

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        head = heading("Does the router learn the right nodes?", color=C_LLM).to_edge(UP, buff=0.85)
        with self.voiceover(text=VO["router_question"]):
            self.play(Write(head), run_time=1.2)

        axis = Line([-5.0, -1.2, 0], [-0.6, -1.2, 0], color=MUTED, stroke_width=1.6)
        heights = [1.5, 1.0, 0.55, 0.28]
        xs = [-4.4, -3.3, -2.2, -1.1]
        bin_labels = ["0–.25", ".25–.5", ".5–.75", ".75–1"]
        hist = VGroup()
        for x, h, bl in zip(xs, heights, bin_labels):
            color = C_LLM if h > 0.8 else MUTED
            bar = Rectangle(width=0.65, height=h, fill_color=color, fill_opacity=0.85, stroke_width=0)
            bar.move_to([x, -1.2 + h / 2, 0])
            lab = txt(bl, size=SMALL_SIZE - 6, color=MUTED).next_to(bar, DOWN, buff=0.1)
            hist.add(VGroup(bar, lab))
        hist_note = MathTex(r"\text{ROUTED NODE COUNT by local }h_v", font_size=26, color=INK)
        hist_note.next_to(hist, UP, buff=0.3)

        with self.voiceover(text=VO["router_hist"]) as tracker:
            self.play(Create(axis), FadeIn(hist_note), run_time=0.6)
            self.play(
                LaggedStart(*[GrowFromEdge(b[0], DOWN) for b in hist], lag_ratio=0.2),
                LaggedStart(*[FadeIn(b[1]) for b in hist], lag_ratio=0.2),
                run_time=min(1.8, tracker.duration),
            )

        graph = demo_tag().scale(0.7).move_to([3.3, -0.3, 0])
        ring = ego_ring(graph, 9, [2, 8, 10, 11], color=C_LLM)
        with self.voiceover(text=VO["router_graph"]) as tracker:
            self.play(FadeIn(graph), run_time=1.0)
            self.play(Create(ring), Flash(graph.nodes[9], color=C_LLM, flash_radius=0.35),
                      run_time=min(1.4, tracker.duration))

        sens = VGroup(
            txt("K: 8→12 +3.4%  ·  12→16 another +3.0%  (Pubmed, Arxiv23)  ·  Cora +12.3% at K=16",
                size=SMALL_SIZE - 5, color=MUTED),
            MathTex(r"h_v>0.75\ \text{region is nearly unchanged }(-0.06\%)",
                    font_size=26, color=MUTED),
        ).arrange(DOWN, buff=0.1).move_to([0, -2.5, 0])
        with self.voiceover(text=VO["router_budget"]) as tracker:
            self.play(FadeOut(VGroup(graph, ring)), run_time=0.4)
            self.play(FadeIn(sens, shift=UP * 0.08), run_time=min(1.6, tracker.duration))

        # Hai tầng ablation (§6.3, tr.9): trung bình mọi feature (nhỏ) và riêng
        # bin homophily thấp khi bỏ đặc trưng homophily (lớn hơn hẳn) — không
        # được gộp lẫn, kẻo trông như cùng một phép đo.
        overall_chart = bar_chart(
            [-0.38, -1.07, -0.65], ["Cora", "Pubmed", "Arxiv23"],
            colors=[MUTED, MUTED, MUTED], y_range=(-8, 1, 2),
            width=4.6, height=2.0, value_fmt="{:.2f}",
        ).move_to([-3.9, -1.0, 0])
        overall_title = txt("REMOVE 1 FEATURE (AVERAGE)", size=SMALL_SIZE - 6, color=MUTED)
        overall_title.next_to(overall_chart, UP, buff=0.35)
        homophily_chart = bar_chart(
            [-6.5, -6.3, -2.0], ["Cora", "Pubmed", "Arxiv23"],
            colors=[C_BAD, C_BAD, C_BAD], y_range=(-8, 1, 2),
            width=4.6, height=2.0, value_fmt="{:.1f}",
        ).move_to([2.2, -1.0, 0])
        homophily_title = MathTex(r"\text{REMOVE HOMOPHILY (BIN }h_v<0.5)", font_size=24, color=C_BAD)
        homophily_title.next_to(homophily_chart, UP, buff=0.35)
        divider = DashedLine([-0.85, -0.2, 0], [-0.85, -2.2, 0], color=C_EDGE, stroke_width=1.5)

        with self.voiceover(text=VO["router_ablation"]) as tracker:
            self.play(FadeOut(VGroup(hist, hist_note, axis, sens)), run_time=0.5)
            self.play(
                FadeIn(overall_title), FadeIn(homophily_title), Create(divider),
                Create(overall_chart.axes), Create(homophily_chart.axes),
                run_time=0.7,
            )
            self.play(
                LaggedStart(*[FadeIn(b, shift=UP * 0.08) for b in overall_chart.bars], lag_ratio=0.2),
                LaggedStart(*[FadeIn(b, shift=UP * 0.08) for b in homophily_chart.bars], lag_ratio=0.2),
                run_time=min(1.8, tracker.duration),
            )

        banner = txt("HOMOPHILY TEACHES THE ROUTER WHEN TO CALL", size=BODY_SIZE - 2, color=C_LLM, weight=BOLD)
        banner.move_to([0, -3.2, 0])
        with self.voiceover(text=VO["router_verdict"]) as tracker:
            self.play(FadeIn(banner, shift=UP * 0.1), run_time=min(1.2, tracker.duration))
        self.wait(0.4)


class S5_09_RoutingControls(GlanceScene):
    """Route hết và route ngẫu nhiên: hai đối chứng khép lập luận."""

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        head = heading("Route all · route randomly: two controls", color=C_LLM).to_edge(UP, buff=0.85)
        with self.voiceover(text=VO["ctrl_intro"]):
            self.play(Write(head), run_time=1.4)

        # panel() bọc thêm buff quanh Rectangle: width 5.6 + buff 0.4 = 6.4 ở
        # x=±3.2 khiến hai khung chạm nhau tại tâm. Thu khung + buff, tách tâm
        # ra ±3.35 để có khe rõ giữa hai đối chứng.
        left = panel(Rectangle(width=5.2, height=2.7), color=C_BAD, buff=0.3).move_to([-3.35, 0.3, 0])
        left_title = txt("ROUTE ALL · CORA", size=SMALL_SIZE - 4, color=C_BAD, weight=BOLD)
        left_title.next_to(left, UP, buff=0.12)
        hard_row = VGroup(pill("+2.8", C_GOOD, width=1.4), pill("+14.5", C_GOOD, width=1.4)).arrange(RIGHT, buff=0.2)
        easy_row = VGroup(pill("−2.8", C_BAD, width=1.4), pill("−1.2", C_BAD, width=1.4)).arrange(RIGHT, buff=0.2)
        overall_pill = pill("OVERALL Δ  −1.2  (negative despite mid-group gains)", C_LLM, width=5.0, size=SMALL_SIZE - 6)
        left_body = VGroup(
            txt("hard groups", size=SMALL_SIZE - 5, color=MUTED), hard_row,
            txt("easy groups", size=SMALL_SIZE - 5, color=MUTED), easy_row,
            overall_pill,
        ).arrange(DOWN, buff=0.12).move_to(left)

        with self.voiceover(text=VO["ctrl_all"]) as tracker:
            self.play(FadeIn(left), FadeIn(left_title), run_time=0.8)
            self.play(FadeIn(left_body, shift=UP * 0.1), run_time=min(1.8, tracker.duration))

        right = panel(Rectangle(width=5.2, height=2.7), color=C_ROUTER, buff=0.3).move_to([3.35, 0.3, 0])
        right_title = txt("RANDOM ROUTING · CORA", size=SMALL_SIZE - 4, color=C_ROUTER, weight=BOLD)
        right_title.next_to(right, UP, buff=0.12)
        ranking = VGroup(
            pill("RANDOM  86.4", C_BAD, width=3.0),
            pill("GCNII  87.7", C_GNN, width=3.0),
            pill("GLANCE  89.5", C_ROUTER, width=3.0),
        ).arrange(DOWN, buff=0.16).move_to(right)

        with self.voiceover(text=VO["ctrl_random"]) as tracker:
            self.play(FadeIn(right), FadeIn(right_title), run_time=0.8)
            self.play(
                LaggedStart(*[FadeIn(r, shift=LEFT * 0.1) for r in ranking], lag_ratio=0.2),
                run_time=min(1.8, tracker.duration),
            )

        with self.voiceover(text=VO["ctrl_same_set"]) as tracker:
            self.play(
                FadeOut(VGroup(left, left_title, left_body, right, right_title, ranking)),
                run_time=0.7,
            )
            comparison = VGroup(
                pill("GNN + LLM + REFINER  87.6", C_GOOD, width=4.8),
                txt(">", size=HEAD_SIZE, color=INK, weight=BOLD),
                pill("GCNII  82.7", C_GNN, width=2.6),
            ).arrange(RIGHT, buff=0.3).move_to([0, 0.3, 0])
            note = txt("on the exact node set selected by the router", size=SMALL_SIZE - 4, color=MUTED)
            note.next_to(comparison, DOWN, buff=0.3)
            self.play(FadeIn(comparison, scale=0.96), FadeIn(note), run_time=min(1.8, tracker.duration))

        banner = txt("VALUE COMES FROM LEARNED SELECTIVITY", size=BODY_SIZE - 2, color=C_GOOD, weight=BOLD)
        banner.move_to([0, -1.6, 0])
        with self.voiceover(text=VO["ctrl_verdict"]) as tracker:
            self.play(FadeIn(banner, shift=UP * 0.1), run_time=min(1.4, tracker.duration))
        self.wait(0.4)


class S5_10_Scale(GlanceScene):
    """Quy mô lớn: route rất ít vẫn hiệu quả trên đồ thị triệu nốt (Bảng 5)."""

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        head = heading("Large scale: route very little, remain effective", color=C_GOOD).to_edge(UP, buff=0.85)
        self.add(head)

        dots = VGroup(*[Dot(radius=0.07, color=MUTED, fill_opacity=0.4) for _ in range(64)])
        dots.arrange_in_grid(rows=8, cols=8, buff=0.13).move_to([-4.3, 0.4, 0])
        # ~1.6% = K=1 trên batch 64 → đúng một chấm sáng trong lưới 8×8.
        dots[27].set_color(C_LLM).set_fill(opacity=1).scale(1.5)
        cloud_label = txt("2.45M NODES · ~62M EDGES", size=SMALL_SIZE - 4, color=INK, weight=BOLD)
        cloud_label.next_to(dots, UP, buff=0.25)
        # Đưa card tỷ lệ về ĐÚNG cao độ với card kết quả (y=0.9) và lùi sang
        # trái, để mũi tên rate → result là một đường ngang thẳng, đủ dài — bản
        # cũ hai card gần nhau và lệch cao độ nên mũi tên ngắn, méo.
        rate = metric_card("ROUTING RATE", "~1.6%", C_LLM, note="K=1, batch 64", width=3.0)
        rate.move_to([-1.4, 0.9, 0])

        with self.voiceover(text=VO["scale_setup"]) as tracker:
            self.play(
                LaggedStart(*[FadeIn(d, scale=0.5) for d in dots], lag_ratio=0.01),
                run_time=1.6,
            )
            self.play(FadeIn(cloud_label), FadeIn(rate, shift=RIGHT * 0.1), run_time=0.8)
            self.play(Flash(dots[27], color=C_LLM, flash_radius=0.30), run_time=min(0.8, tracker.duration))

        result = metric_card("OGB-PRODUCTS", "82.3", C_GOOD, note="GCNII: 81.8", width=3.0)
        result.move_to([2.8, 0.9, 0])
        oom = pill("GGCN · OOM", C_BAD, width=2.3).move_to([2.8, -0.3, 0])
        arxiv_year = metric_card("ARXIV-YEAR", "49.8", C_GOOD, width=2.6).move_to([2.8, -1.5, 0])
        arrow = Arrow(rate.get_right(), result.get_left(), buff=0.18, color=MUTED,
                      stroke_width=4, max_tip_length_to_length_ratio=0.22)

        with self.voiceover(text=VO["scale_result"]) as tracker:
            self.play(GrowArrow(arrow), FadeIn(result, shift=RIGHT * 0.1), run_time=1.0)
            self.play(FadeIn(oom, shift=LEFT * 0.1), FadeIn(arxiv_year, shift=UP * 0.1),
                      run_time=min(1.8, tracker.duration))

        banner = txt("CHEAP  ·  BALANCED  ·  SCALES TO MILLIONS OF NODES", size=BODY_SIZE - 2, color=C_GOOD, weight=BOLD)
        banner.move_to([0, -2.7, 0])
        with self.voiceover(text=VO["scale_verdict"]) as tracker:
            self.play(FadeIn(banner, shift=UP * 0.1), run_time=min(1.2, tracker.duration))
        self.wait(0.4)


class S5_11_Callout(GlanceScene):
    """Chốt lại toàn bộ mạch GLANCE, nối lại câu hỏi mở đầu Section 1."""

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        head = heading("Takeaways: GLANCE in five points", color=C_ROUTER).to_edge(UP, buff=0.85)
        with self.voiceover(text=VO["final_reconnect"]) as tracker:
            self.play(Write(head), run_time=min(2.2, tracker.duration))

        items = [
            ("GNNs and LLMs excel on different nodes; local homophily predicts who wins.", C_GNN),
            ("Top-K is non-differentiable, so rewards train the router decision by decision.", C_ROUTER),
            ("Only the router and refiner are trained; the GNN and LLM remain frozen.", C_LLM),
            ("Learned selectivity delivers the best balance and overall accuracy.", C_GOOD),
            ("Routing only a small fraction of nodes still scales to million-node graphs.", C_LLM),
        ]

        def numbered_row(index, text, color):
            badge = VGroup(
                Circle(radius=0.22, fill_color=color, fill_opacity=0.18, stroke_color=color, stroke_width=2),
                txt(str(index), size=SMALL_SIZE - 2, color=color, weight=BOLD),
            )
            label = txt(text, size=SMALL_SIZE - 3, color=INK)
            if label.width > 9.3:
                label.scale_to_fit_width(9.3)
            return VGroup(badge, label).arrange(RIGHT, buff=0.3)

        rows = VGroup(*[numbered_row(i + 1, t, c) for i, (t, c) in enumerate(items)])
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.26)
        rows.move_to([0, 0.1, 0])

        for i, (row, (_, color)) in enumerate(zip(rows, items)):
            key = f"final_{i + 1}"
            with self.voiceover(text=VO[key]) as tracker:
                self.play(FadeIn(row, shift=RIGHT * 0.15), run_time=min(1.0, tracker.duration))

        with self.voiceover(text=VO["final_punch"]) as tracker:
            self.play(FadeOut(VGroup(head, rows), shift=UP * 0.2), run_time=0.6)
            not_more = txt("NOT MORE LLM", size=HEAD_SIZE - 4, color=C_BAD, weight=BOLD)
            not_more.move_to([0, 0.6, 0])
            strike = Line(not_more.get_left(), not_more.get_right(), color=C_BAD, stroke_width=6)
            final_line = txt("USE THE LLM IN THE RIGHT PLACES.", size=TITLE_SIZE - 6, color=C_GOOD, weight=BOLD)
            final_line.move_to([0, -0.4, 0])
            self.play(Write(not_more), run_time=1.0)
            self.play(Create(strike), run_time=0.5)
            self.play(Write(final_line), Flash(final_line, color=C_GOOD, flash_radius=1.0),
                      run_time=min(1.6, tracker.duration))
        self.wait(0.8)
