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
SECTION_NAME = "Training objective & thực nghiệm"
OWNER = "Thiên Lâm"
ACCENT = SECTION_COLORS.get(SECTION, C_HIGHLIGHT)


# ---------------------------------------------------------------------------
# Khối xây dựng nhỏ dùng riêng cho section này — chỉ ghép từ txt()/màu có sẵn
# trong glance_style.py, không tự chế thêm màu hay helper dùng chung mới.
# ---------------------------------------------------------------------------

def pill(text, color, width=None, size=SMALL_SIZE):
    """Nhãn viên thuốc: khung bo tròn viền màu quanh một dòng chữ ngắn."""
    label = txt(text, size=size, color=color, weight=BOLD)
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
        "Vì phép chọn tốp ca không liên tục, gờ ra điên không truyền được xuyên qua nó — "
        "hàm mất mát cuối không thể dạy trực tiếp cho bộ định tuyến."
    ),
    # --- S5_03 Counterfactual ---
    "cf_intro": "Thay vì đạo hàm qua tốp ca, gờ lans chấm kết quả của từng quyết định bằng phần thưởng.",
    "cf_branch": (
        "Với một nốt được định tuyến, gờ lans dựng hai thế giới đối chứng: thế giới không gọi lờ lờ mờ, "
        "dùng đầu dự đoán H có sẵn của gờ nờ nờ; và thế giới đã gọi lờ lờ mờ, đi qua bộ tinh chỉnh xi."
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
        "hàm mất mát dự đoán rẽ nhánh theo việc nốt có nằm trong tốp ca hay không: nốt được định tuyến "
        "dùng hàm mất mát của nhánh gờ nờ nờ cộng lờ lờ mờ, nốt còn lại dùng hàm mất mát của riêng gờ nờ nờ."
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
        "không phẩy một, không phẩy hai, không phẩy ba. Ngân sách ca giảm dần theo lịch, "
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
        "ác xíp dia và ô gi bi pró đắc."
    ),
    "setup_baseline": (
        "Đối thủ đều mạnh: các gờ nờ nờ kinh điển gờ xê en, gráp xây giơ, gờ xê en hai chạy trên "
        "ba chiến lược khác nhau; thêm nhóm gờ nờ nờ chuyên xử lý dị phối gồm ép a gờ xê en, "
        "gờ gờ xê en, gờ bê ca gờ en en."
    ),
    "setup_budget": (
        "Mấu chốt: mặc định gờ lans chỉ gọi lờ lờ mờ cho mười hai trên ba mươi hai nốt mỗi bát — "
        "nó phải thắng trong khi gọi lờ lờ mờ ít hơn hẳn đối thủ."
    ),
    # --- S5_07 Balanced results ---
    "res_overall": (
        "Về độ chính xác tổng thể, gờ lans dẫn đầu cả ba bộ: cô ra tám mươi chín phẩy năm, pắp mét "
        "chín mươi hai phẩy sáu, ác xíp hai ba tám mươi hai phẩy một — trung bình hơn mô hình tốt "
        "kế tiếp khoảng không phẩy năm phần trăm."
    ),
    "res_margin": "Nhưng khoảng cách tổng thể chỉ dưới một điểm, nên đó chưa phải điều quan trọng nhất.",
    "res_hardbin": (
        "Chia nốt theo hô mô phi li cục bộ thành các nhóm, ở nhóm khó nhất của cô ra gờ lans đạt "
        "bốn mươi sáu phẩy bốn — cao hơn mô hình tốt kế tiếp tới mười ba điểm."
    ),
    "res_rank": (
        "Trung bình trên toàn bộ các nhóm, gờ lans xếp hạng hai phẩy bốn — tốt nhất, bỏ xa á quân "
        "bốn phẩy bảy, mà nhóm dễ vẫn giữ gần như tuyệt đối."
    ),
    "res_verdict": "Con số tổng thể che chênh lệch ở nốt khó; hô mô phi li làm nó lộ ra.",
    # --- S5_08 Router learned ---
    "router_question": "Vậy bộ định tuyến có thật sự học đúng chỗ không?",
    "router_hist": (
        "Khi soi các nốt được định tuyến, khối lượng dồn hẳn về vùng hô mô phi li thấp — đúng vùng mà "
        "gờ nờ nờ hay sai còn lờ lờ mờ có thể sửa."
    ),
    "router_graph": (
        "Nhìn trên đồ thị mẫu, nốt chín — hô mô phi li thấp, hàng xóm khác lớp — là kiểu nốt "
        "bộ định tuyến ưu tiên gọi lờ lờ mờ; nốt bốn thì hầu như không cần."
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
    "ctrl_intro": "Bằng chứng mạnh nhất không phải là thêm lờ lờ mờ, mà là chọn đúng nốt để gọi.",
    "ctrl_all": (
        "định tuyến hết mọi nốt trên pắp mét: hai nhóm khó tăng, tổng thể thậm chí nhích lên cộng một "
        "phẩy năm điểm — nhưng đổi lại, hai nhóm dễ sụp gần hai mươi điểm; con số tổng che mất cái giá "
        "phải trả đó."
    ),
    "ctrl_random": (
        "Giữ nguyên lờ lờ mờ và bộ tinh chỉnh nhưng định tuyến ngẫu nhiên trên cô ra: chỉ còn tám mươi sáu "
        "phẩy bốn, thua cả bây xơ lai gờ xê en hai tám mươi bảy phẩy bảy."
    ),
    "ctrl_same_set": (
        "Trên đúng tập nốt mà bộ định tuyến đã chọn, nhánh gờ nờ nờ cộng lờ lờ mờ qua bộ tinh chỉnh đạt tám "
        "mươi bảy phẩy sáu — cao hơn hẳn nếu để gờ xê en hai tự xử lý."
    ),
    "ctrl_verdict": "định tuyến hết thì hại nốt dễ; định tuyến bừa thì thua bây xơ lai — giá trị nằm ở sự chọn lọc học được.",
    # --- S5_10 Scale ---
    "scale_setup": (
        "Trên ô gi bi pró đắc — hai phẩy bốn lăm triệu nốt, gần sáu mươi hai triệu cạnh — gờ lans "
        "chỉ gọi lờ lờ mờ cho khoảng một phẩy sáu phần trăm nốt, tức một nốt trong mỗi sáu mươi tư."
    ),
    "scale_result": (
        "Vậy mà vẫn dẫn đầu: tám mươi hai phẩy ba, cao hơn gờ xê en hai tám mươi mốt phẩy tám, "
        "còn gờ gờ xê en thì hết bộ nhớ. Trên ác xíp dia, gờ lans đạt bốn mươi chín phẩy tám."
    ),
    "scale_verdict": "Chọn lọc học được không chỉ cân bằng và chính xác, mà còn rẻ và mở rộng tới quy mô triệu nốt.",
    # --- S5_11 Callout ---
    "final_reconnect": (
        "Ở đầu đoạn phim, câu hỏi đặt ra là: có cách nào kết hợp gờ, nờ, nờ và lờ, lờ, mờ mà biết tính "
        "chi phí không? Đây là câu trả lời của gờ lans, gói trong năm ý."
    ),
    "final_1": "Một: gờ, nờ, nờ và lờ, lờ, mờ giỏi ở những nốt khác nhau; hô mô phi li cục bộ dự báo ai sẽ thắng.",
    "final_2": "Hai: vì tốp ca không khả vi, phần thưởng chấm điểm từng quyết định để dạy bộ định tuyến.",
    "final_3": "Ba: chỉ bộ định tuyến và bộ tinh chỉnh được huấn luyện; gờ, nờ, nờ và lờ, lờ, mờ đóng băng.",
    "final_4": "Bốn: kết quả là mô hình cân bằng nhất và dẫn đầu tổng thể, nhờ sự chọn lọc học được.",
    "final_5": "Năm: chỉ định tuyến một phần nhỏ nốt, gờ lans vẫn mở rộng tới đồ thị hàng triệu nốt.",
    "final_punch": "Tất cả gói trong một câu — đừng dùng nhiều lờ, lờ, mờ hơn, hãy dùng lờ, lờ, mờ đúng chỗ.",
}


class S5_01_Title(GlanceScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        card = title_card(
            f"{SECTION} — {SECTION_NAME}",
            "Vì sao GLANCE học được, và vì sao kết quả chứng minh điều đó",
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
        head = heading("Vấn đề cốt lõi — top-K không khả vi", color=ACCENT).to_edge(UP, buff=0.85)

        budget = pill("NGÂN SÁCH CỨNG  ·  K = 2", C_LLM, width=4.4).move_to([0, 1.9, 0])

        labels = ["A", "B", "C", "D", "E", "F"]
        scores = [0.91, 0.82, 0.79, 0.61, 0.44, 0.20]
        nodes = VGroup(*[labeled_box(l, C_ROUTER, width=1.05, height=0.85) for l in labels])
        nodes.arrange(RIGHT, buff=0.35).move_to([0, 0.9, 0])
        score_texts = VGroup(*[
            txt(f"{s:.2f}", size=SMALL_SIZE, color=MUTED, weight=BOLD).next_to(n, DOWN, buff=0.12)
            for n, s in zip(nodes, scores)
        ])
        tickets = VGroup(*[check(color=C_LLM).next_to(n, UP, buff=0.14) for n in nodes[:2]])

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
        jump_label = txt("đổi hạng → quyết định nhảy", size=SMALL_SIZE - 4, color=C_BAD)
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

        # Điểm B tụt nhẹ từ 0.82 xuống 0.78 — thấp hơn C (0.79) — nên đổi hạng:
        # B và C hoán đổi vị trí, "vé" đi theo C chứ không theo B.
        b_center = nodes[1].get_center().copy()
        c_center = nodes[2].get_center().copy()
        score_078 = txt("0.78", size=SMALL_SIZE - 5, color=C_BAD, weight=BOLD).move_to(score_texts[2])
        score_079_moved = score_texts[2].copy().move_to(score_texts[1])
        nodes[1].generate_target()
        nodes[1].target.move_to(c_center)
        nodes[2].generate_target()
        nodes[2].target.move_to(b_center)
        self.play(
            Transform(score_texts[1], score_078),
            Transform(score_texts[2], score_079_moved),
            MoveToTarget(nodes[1]), MoveToTarget(nodes[2]),
            tickets[1].animate.move_to(b_center + UP * 0.55),
            marker.animate.move_to(step_axis.c2p(2.65, 1)),
            run_time=1.6,
        )
        self.play(Flash(marker, color=C_BAD, flash_radius=0.35), run_time=0.6)
        self.wait(0.5)

        chain = pipeline(
            [("ROUTER π", C_ROUTER), ("TOP-K", C_BAD), ("LOSS CUỐI", C_GOOD)],
        ).move_to([0, -1.1, 0])
        blocked = cross(color=C_BAD, size=0.5).move_to(chain.boxes[1])
        grad_arrow = Arrow(
            chain.boxes[2].get_left(), chain.boxes[1].get_right(),
            buff=0.10, color=YELLOW, stroke_width=5,
        )

        with self.voiceover(text=VO["topk_block"]) as tracker:
            self.play(
                FadeOut(VGroup(nodes, score_texts, step_axis, step, cut, jump_label, marker, tickets[1])),
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
        head = heading("Cách giải — thay gradient bằng reward", color=C_GOOD).to_edge(UP, buff=0.85)
        self.add(head)

        node = labeled_box("v", C_ROUTER, width=0.9, height=0.9).move_to([-5.6, 0, 0])
        route_tag = pill("ROUTE", C_LLM, width=1.7).next_to(node, UP, buff=0.25)

        with self.voiceover(text=VO["cf_intro"]):
            self.play(GrowFromCenter(node), FadeIn(route_tag, shift=DOWN * 0.15), run_time=1.2)

        upper = panel(Rectangle(width=7.0, height=1.5)).move_to([0.1, 1.0, 0])
        lower = panel(Rectangle(width=7.0, height=1.5), color=C_LLM).move_to([0.1, -0.7, 0])
        up_text = txt("KHÔNG GỌI LLM  ·  GNN → đầu H → p_H  ·  lᴳ = CE(yᵥ, p_H)",
                       size=SMALL_SIZE - 3, color=C_GNN).move_to(upper).scale_to_fit_width(6.4)
        low_text = txt("ĐÃ GỌI LLM  ·  GNN + LLM → refiner ξ → p_ξ  ·  lᴸ = CE(yᵥ, p_ξ)",
                        size=SMALL_SIZE - 3, color=C_LLM).move_to(lower).scale_to_fit_width(6.4)
        arrow_up = Arrow(node.get_right(), upper.get_left(), buff=0.1, color=C_GNN, stroke_width=3)
        arrow_down = Arrow(node.get_right(), lower.get_left(), buff=0.1, color=C_LLM, stroke_width=3)

        # Bản sao mờ của v "bay" vào mỗi nhánh — cùng một node đi hai đường.
        ghost_up = node.copy().scale(0.6).set_opacity(0.9)
        ghost_down = node.copy().scale(0.6).set_opacity(0.9)

        # Đồng hồ loss bên phải mỗi nhánh: số chạy sống + thanh dài dần tới giá trị thật.
        gnn_value, llm_value = ValueTracker(0.0), ValueTracker(0.0)
        gnn_num = DecimalNumber(0, num_decimal_places=2, color=C_GNN, font_size=BODY_SIZE - 4)
        gnn_num.add_updater(lambda m: m.set_value(gnn_value.get_value())).move_to([5.9, 1.0, 0])
        llm_num = DecimalNumber(0, num_decimal_places=2, color=C_LLM, font_size=BODY_SIZE - 4)
        llm_num.add_updater(lambda m: m.set_value(llm_value.get_value())).move_to([5.9, -0.7, 0])
        gnn_track = RoundedRectangle(width=1.5, height=0.20, corner_radius=0.05,
                                      stroke_color=C_GNN, stroke_width=1.4, fill_opacity=0).move_to([4.55, 1.0, 0])
        llm_track = RoundedRectangle(width=1.5, height=0.20, corner_radius=0.05,
                                      stroke_color=C_LLM, stroke_width=1.4, fill_opacity=0).move_to([4.55, -0.7, 0])
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

        truth = txt("cùng nhãn thật  yᵥ", size=SMALL_SIZE - 3, color=C_GOOD, weight=BOLD)
        truth.move_to([-5.6, -0.9, 0])
        with self.voiceover(text=VO["cf_same_label"]) as tracker:
            self.play(FadeIn(truth, scale=0.95), run_time=0.9)
            self.play(Indicate(up_text, color=C_GNN), Indicate(low_text, color=C_LLM),
                      run_time=min(1.6, tracker.duration))
        banner = txt(
            "lᴸ LÀ LOSS CỦA CẢ NHÁNH GNN + LLM + REFINER — KHÔNG PHẢI LLM ĐỨNG MỘT MÌNH",
            size=SMALL_SIZE - 4, color=C_LLM, weight=BOLD,
        ).move_to([0.1, -2.1, 0]).scale_to_fit_width(11.5)
        self.play(FadeIn(banner, shift=UP * 0.1), run_time=0.7)
        self.wait(0.6)


class S5_04_Reward(GlanceScene):
    """Reward là lợi ích ròng của việc gọi LLM, trừ chi phí beta."""

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        head = heading("Reward — một lần gọi LLM có đáng không?", color=C_GOOD).to_edge(UP, buff=0.85)
        self.add(head)

        row1 = VGroup(
            pill("lᴳ = 2.30", C_GNN, width=2.2),
            txt("−", size=BODY_SIZE, color=MUTED),
            pill("lᴸ = 0.30", C_LLM, width=2.2),
            txt("=", size=BODY_SIZE, color=MUTED),
            pill("gain 2.00", C_GOOD, width=2.3),
        ).arrange(RIGHT, buff=0.25).move_to([0, 1.3, 0])
        route_label = txt("NẾU ROUTE", size=SMALL_SIZE, color=C_LLM, weight=BOLD).next_to(row1, UP, buff=0.3)

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
        note = txt("SỐ MINH HOẠ", size=SMALL_SIZE - 5, color=MUTED).next_to(row2, RIGHT, buff=0.4)
        beta_note = txt(
            "β lớn → router dè dặt hơn   ·   β nhỏ → router gọi LLM nhiều hơn",
            size=SMALL_SIZE - 3, color=MUTED,
        ).move_to([0, -0.35, 0])

        counter_row = txt(
            "VD: gain 0.05 − β 0.10 = reward −0.05  →  vẫn âm dù có route",
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
            txt("NẾU SKIP", size=SMALL_SIZE, color=MUTED, weight=BOLD),
            pill("reward = −lᴳ", C_BAD, width=3.0),
        ).arrange(RIGHT, buff=0.4).move_to([0, -1.4, 0])

        with self.voiceover(text=VO["reward_skip"]) as tracker:
            self.play(FadeIn(skip_row, shift=UP * 0.1), run_time=min(1.4, tracker.duration))

        banner = txt("ROUTE:  rᵥ = lᴳ − lᴸ − β        SKIP:  rᵥ = −lᴳ",
                      size=BODY_SIZE - 2, color=C_ROUTER, weight=BOLD).move_to([0, -2.3, 0])
        self.play(FadeIn(banner, shift=UP * 0.1), run_time=0.8)
        self.wait(0.6)


class S5_05_JointObjective(GlanceScene):
    """Router loss + prediction loss = loss tổng; chỉ train router và refiner."""

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        head = heading("Học từ reward — loss tổng và ai được cập nhật", color=C_ROUTER).to_edge(UP, buff=0.85)
        self.add(head)

        chain = pipeline(
            [("reward rᵥ", C_GOOD), ("log π(fᵥ)", C_ROUTER), ("router loss", C_BAD)],
        ).scale(0.85).move_to([0, 1.75, 0])
        good_rule = VGroup(
            txt("rᵥ > 0", size=SMALL_SIZE - 2, color=C_GOOD, weight=BOLD),
            txt("→", size=SMALL_SIZE - 2, color=MUTED),
            txt("π(fᵥ) tăng", size=SMALL_SIZE - 2, color=C_GOOD, weight=BOLD),
        ).arrange(RIGHT, buff=0.16)
        bad_rule = VGroup(
            txt("rᵥ < 0", size=SMALL_SIZE - 2, color=C_BAD, weight=BOLD),
            txt("→", size=SMALL_SIZE - 2, color=MUTED),
            txt("π(fᵥ) giảm", size=SMALL_SIZE - 2, color=C_BAD, weight=BOLD),
        ).arrange(RIGHT, buff=0.16)
        rules = VGroup(good_rule, bad_rule).arrange(RIGHT, buff=1.0).move_to([0, 1.0, 0])

        with self.voiceover(text=VO["obj_policy"]) as tracker:
            self.play(FadeIn(chain.boxes[0], scale=0.9), run_time=0.6)
            self.play(GrowArrow(chain.arrows[0]), FadeIn(chain.boxes[1]), run_time=0.7)
            self.play(GrowArrow(chain.arrows[1]), FadeIn(chain.boxes[2]), run_time=0.7)
            self.play(FadeIn(rules, shift=UP * 0.08), run_time=min(1.2, tracker.duration))
        self.play(FadeOut(rules), chain.animate.move_to([0, 1.5, 0]), run_time=0.5)

        formula = txt(
            "lʳᵒᵘᵗᵉ = −rᵥ · log π(fᵥ)  −  λ_ent · H[π(fᵥ)]",
            size=BODY_SIZE - 4, color=INK, weight=BOLD,
        ).move_to([0, 0.55, 0])
        with self.voiceover(text=VO["obj_entropy"]) as tracker:
            self.play(Write(formula), run_time=min(1.6, tracker.duration))

        pred_card = panel(Rectangle(width=5.2, height=1.1), color=C_GNN).move_to([-3.0, -0.55, 0])
        route_card = panel(Rectangle(width=5.2, height=1.1), color=C_ROUTER).move_to([3.0, -0.55, 0])
        pred_text = txt("PREDICTION LOSS  ·  top-K dùng lᴸ, còn lại dùng lᴳ",
                         size=SMALL_SIZE - 4, color=C_GNN).move_to(pred_card).scale_to_fit_width(4.8)
        route_text = txt("λ × ROUTER LOSS  ·  học phân bổ ngân sách",
                          size=SMALL_SIZE - 4, color=C_ROUTER).move_to(route_card).scale_to_fit_width(4.8)
        with self.voiceover(text=VO["obj_pred"]) as tracker:
            self.play(FadeIn(pred_card), FadeIn(pred_text), run_time=min(1.6, tracker.duration))

        total = pill("LOSS TỔNG", INK, width=2.6).move_to([0, -1.75, 0])
        pred_to_total = Arrow(
            pred_card.get_bottom(), total.get_top() + LEFT * 0.45,
            buff=0.12, color=C_GNN, stroke_width=3,
        )
        route_to_total = Arrow(
            route_card.get_bottom(), total.get_top() + RIGHT * 0.45,
            buff=0.12, color=C_ROUTER, stroke_width=3,
        )
        with self.voiceover(text=VO["obj_total"]) as tracker:
            self.play(FadeIn(route_card), FadeIn(route_text), run_time=1.0)
            self.play(
                GrowArrow(pred_to_total), GrowArrow(route_to_total),
                FadeIn(total, shift=UP * 0.1),
                run_time=min(1.2, tracker.duration),
            )

        modules = VGroup(
            labeled_box("GNN  F", C_GNN, width=2.1, height=0.75),
            labeled_box("LLM  L", C_LLM, width=2.1, height=0.75),
            labeled_box("REFINER  ξ", C_GOOD, width=2.1, height=0.75),
            labeled_box("ROUTER  π", C_ROUTER, width=2.1, height=0.75),
        ).arrange(RIGHT, buff=0.3).move_to([0, -2.35, 0])
        update_label = pill("LOSS TỔNG  →  CẬP NHẬT THAM SỐ", C_GOOD, width=4.8)
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
            self.play(freeze(modules[0]), freeze(modules[1]),
                      Indicate(modules[2], color=C_GOOD), Indicate(modules[3], color=C_ROUTER),
                      run_time=min(1.6, tracker.duration))
            self.play(
                FadeOut(VGroup(update_label, to_refiner, to_router)),
                modules.animate.move_to([0, -0.55, 0]),
                run_time=0.7,
            )

        hparam = VGroup(
            txt("batch 32  ·  route top-12 mỗi batch  ·  β = {0.1, 0.2, 0.3}",
                size=SMALL_SIZE - 4, color=MUTED),
            txt("lịch giảm ngân sách: K từ 32 xuống 8, hệ số r = 0.5",
                size=SMALL_SIZE - 5, color=MUTED),
        ).arrange(DOWN, buff=0.12).move_to([0, -2.25, 0])
        with self.voiceover(text=VO["obj_hparam"]) as tracker:
            self.play(FadeIn(hparam, shift=UP * 0.06), run_time=min(1.6, tracker.duration))
        self.add(source("Appendix C.4, tr.17"))

        with self.voiceover(text=VO["obj_question"]) as tracker:
            self.wait(tracker.duration)
        self.wait(0.4)


class S5_06_Setup(GlanceScene):
    """Bối cảnh thực nghiệm: câu hỏi trung tâm, dữ liệu, đối thủ, ngân sách."""

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        head = heading("Bối cảnh thực nghiệm", color=C_GNN).to_edge(UP, buff=0.85)
        self.add(head)

        row = VGroup(
            labeled_box("GNN", C_GNN, width=2.0), txt("+", size=HEAD_SIZE, color=MUTED),
            labeled_box("LLM", C_LLM, width=2.0),
        ).arrange(RIGHT, buff=0.3).move_to([-2.0, 1.3, 0])
        goal = pill("MỘT MÔ HÌNH?", C_ROUTER, width=3.0).move_to([2.8, 1.3, 0])
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
        strat = VGroup(*[pill(n, MUTED, width=2.7) for n in ["đặc trưng gốc", "tăng cường LLM", "LOGIN"]]).arrange(DOWN, buff=0.18)
        hetero = VGroup(*[pill(n, C_ROUTER, width=2.3) for n in ["FAGCN", "GGCN", "GBK-GNN"]]).arrange(DOWN, buff=0.18)
        baselines = VGroup(classic, strat, hetero).arrange(RIGHT, buff=0.6).move_to([0, -1.0, 0])
        with self.voiceover(text=VO["setup_baseline"]) as tracker:
            self.play(FadeOut(datasets, shift=UP * 0.1), run_time=0.5)
            self.play(FadeIn(baselines, shift=UP * 0.1), run_time=min(2.0, tracker.duration))

        dots = VGroup(*[Dot(radius=0.075, color=MUTED, fill_opacity=0.4) for _ in range(32)])
        dots.arrange_in_grid(rows=4, cols=8, buff=0.16).move_to([-3.1, -1.0, 0])
        for i in range(12):
            dots[i].set_color(C_LLM).set_fill(opacity=1)
        budget = metric_card("NGÂN SÁCH GỌI LLM", "12 / 32", C_LLM, note="mỗi batch", width=3.4)
        budget.move_to([2.6, -1.0, 0])
        with self.voiceover(text=VO["setup_budget"]) as tracker:
            self.play(FadeOut(baselines, shift=UP * 0.1), run_time=0.5)
            self.play(
                LaggedStart(*[FadeIn(d, scale=0.5) for d in dots], lag_ratio=0.02),
                run_time=1.2,
            )
            self.play(FadeIn(budget, shift=LEFT * 0.1), run_time=min(1.4, tracker.duration))
        self.add(source("§6.1, tr.7"))
        self.wait(0.5)


class S5_07_BalancedResults(GlanceScene):
    """Accuracy tổng thể (Bảng 4) và cân bằng theo homophily (Bảng 3)."""

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        head = heading("Cân bằng & tổng thể", color=C_ROUTER).to_edge(UP, buff=0.85)
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

        margin = pill("KHOẢNG CÁCH TỔNG THỂ CHỈ DƯỚI 1 ĐIỂM", C_LLM, width=7.0).move_to([0, -0.9, 0])
        with self.voiceover(text=VO["res_margin"]) as tracker:
            self.play(FadeIn(margin, scale=0.96), run_time=min(1.2, tracker.duration))

        hard_chart = bar_chart(
            [33.4, 46.4], ["Á quân", "GLANCE"], colors=[MUTED, C_ROUTER],
            y_range=(0, 50, 10), width=4.2, height=2.4, value_fmt="{:.1f}",
        ).move_to([-3.3, -2.0, 0])
        hard_title = txt("CORA · NHÓM KHÓ NHẤT (h_v < 0.25)", size=SMALL_SIZE - 5, color=C_BAD)
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

        rank = metric_card("AVERAGE RANK", "2.4", C_ROUTER, note="á quân: 4.7", width=3.4)
        rank.move_to([2.9, -0.9, 0])
        easy = pill("NHÓM DỄ VẪN GẦN TUYỆT ĐỐI", C_GNN, width=4.2).move_to([2.9, -2.0, 0])
        with self.voiceover(text=VO["res_rank"]) as tracker:
            self.play(FadeIn(rank, shift=LEFT * 0.1), run_time=0.9)
            self.play(FadeIn(easy, shift=UP * 0.1), run_time=min(1.3, tracker.duration))

        banner = txt("CÂN BẰNG NHẤT  ≠  THẮNG MỌI NHÓM", size=BODY_SIZE - 2, color=C_ROUTER, weight=BOLD)
        banner.move_to([0, -1.0, 0])
        with self.voiceover(text=VO["res_verdict"]) as tracker:
            self.play(
                FadeOut(VGroup(hard_chart, hard_title, rank, easy, gain_arrow, gain_label), shift=UP * 0.15),
                run_time=0.5,
            )
            self.play(FadeIn(banner, shift=UP * 0.1), run_time=min(1.2, tracker.duration))
        self.add(source("Bảng 3–4, tr.8"))
        self.wait(0.4)


class S5_08_RouterLearned(GlanceScene):
    """Router học đúng tín hiệu: phân bố route + sensitivity K + ablation (§6.3)."""

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        head = heading("Router có học đúng chỗ không?", color=C_LLM).to_edge(UP, buff=0.85)
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
        hist_note = txt("SỐ NỐT ĐƯỢC ROUTE, theo h_v cục bộ", size=SMALL_SIZE - 5, color=INK)
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
            txt("K: 8→12 +3.4%  ·  12→16 thêm +3.0%  (Pubmed, Arxiv23)  ·  Cora +12.3% ở K=16",
                size=SMALL_SIZE - 5, color=MUTED),
            txt("vùng h_v > 0.75 hầu như không đổi (−0.06%)", size=SMALL_SIZE - 5, color=MUTED),
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
        overall_title = txt("TẮT 1 FEATURE (TRUNG BÌNH)", size=SMALL_SIZE - 6, color=MUTED)
        overall_title.next_to(overall_chart, UP, buff=0.35)
        homophily_chart = bar_chart(
            [-6.5, -6.3, -2.0], ["Cora", "Pubmed", "Arxiv23"],
            colors=[C_BAD, C_BAD, C_BAD], y_range=(-8, 1, 2),
            width=4.6, height=2.0, value_fmt="{:.1f}",
        ).move_to([2.2, -1.0, 0])
        homophily_title = txt("TẮT HOMOPHILY (BIN h_v < 0.5)", size=SMALL_SIZE - 6, color=C_BAD)
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

        banner = txt("HOMOPHILY DẠY ROUTER GỌI ĐÚNG LÚC", size=BODY_SIZE - 2, color=C_LLM, weight=BOLD)
        banner.move_to([0, -3.2, 0])
        with self.voiceover(text=VO["router_verdict"]) as tracker:
            self.play(FadeIn(banner, shift=UP * 0.1), run_time=min(1.2, tracker.duration))
        self.add(source("§6.3, tr.8–9"))
        self.wait(0.4)


class S5_09_RoutingControls(GlanceScene):
    """Route hết và route ngẫu nhiên: hai đối chứng khép lập luận."""

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        head = heading("Route hết · route bừa — hai đối chứng", color=C_LLM).to_edge(UP, buff=0.85)
        with self.voiceover(text=VO["ctrl_intro"]):
            self.play(Write(head), run_time=1.4)

        left = panel(Rectangle(width=5.6, height=2.7), color=C_BAD).move_to([-3.2, 0.3, 0])
        left_title = txt("ROUTE HẾT · PUBMED", size=SMALL_SIZE - 4, color=C_BAD, weight=BOLD)
        left_title.next_to(left, UP, buff=0.12)
        hard_row = VGroup(pill("+10.9", C_GOOD, width=1.4), pill("+13.3", C_GOOD, width=1.4)).arrange(RIGHT, buff=0.2)
        easy_row = VGroup(pill("−18.3", C_BAD, width=1.4), pill("−19.7", C_BAD, width=1.4)).arrange(RIGHT, buff=0.2)
        overall_pill = pill("Δ TỔNG THỂ  +1.5  (bị che bởi nhóm dễ sụp)", C_LLM, width=5.0, size=SMALL_SIZE - 6)
        left_body = VGroup(
            txt("nhóm khó", size=SMALL_SIZE - 5, color=MUTED), hard_row,
            txt("nhóm dễ", size=SMALL_SIZE - 5, color=MUTED), easy_row,
            overall_pill,
        ).arrange(DOWN, buff=0.12).move_to(left)

        with self.voiceover(text=VO["ctrl_all"]) as tracker:
            self.play(FadeIn(left), FadeIn(left_title), run_time=0.8)
            self.play(FadeIn(left_body, shift=UP * 0.1), run_time=min(1.8, tracker.duration))

        right = panel(Rectangle(width=5.6, height=2.7), color=C_ROUTER).move_to([3.2, 0.3, 0])
        right_title = txt("ROUTE NGẪU NHIÊN · CORA", size=SMALL_SIZE - 4, color=C_ROUTER, weight=BOLD)
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
            note = txt("trên đúng tập nốt mà router đã chọn", size=SMALL_SIZE - 4, color=MUTED)
            note.next_to(comparison, DOWN, buff=0.3)
            self.play(FadeIn(comparison, scale=0.96), FadeIn(note), run_time=min(1.8, tracker.duration))

        banner = txt("GIÁ TRỊ NẰM Ở SỰ CHỌN LỌC HỌC ĐƯỢC", size=BODY_SIZE - 2, color=C_GOOD, weight=BOLD)
        banner.move_to([0, -1.6, 0])
        with self.voiceover(text=VO["ctrl_verdict"]) as tracker:
            self.play(FadeIn(banner, shift=UP * 0.1), run_time=min(1.4, tracker.duration))
        self.add(source("Bảng 10–12, Phụ lục F"))
        self.wait(0.4)


class S5_10_Scale(GlanceScene):
    """Quy mô lớn: route rất ít vẫn hiệu quả trên đồ thị triệu nốt (Bảng 5)."""

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        head = heading("Quy mô lớn — route rất ít, hiệu quả vẫn cao", color=C_GOOD).to_edge(UP, buff=0.85)
        self.add(head)

        dots = VGroup(*[Dot(radius=0.07, color=MUTED, fill_opacity=0.4) for _ in range(64)])
        dots.arrange_in_grid(rows=8, cols=8, buff=0.13).move_to([-4.3, 0.4, 0])
        # ~1.6% = K=1 trên batch 64 → đúng một chấm sáng trong lưới 8×8.
        dots[27].set_color(C_LLM).set_fill(opacity=1).scale(1.5)
        cloud_label = txt("2.45M NỐT · ~62M CẠNH", size=SMALL_SIZE - 4, color=INK, weight=BOLD)
        cloud_label.next_to(dots, UP, buff=0.25)
        rate = metric_card("TỶ LỆ ROUTE", "~1.6%", C_LLM, note="K=1, batch 64", width=3.0)
        rate.move_to([-0.3, 0.4, 0])

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
        arrow = Arrow(rate.get_right(), result.get_left(), buff=0.12, color=MUTED, stroke_width=3)

        with self.voiceover(text=VO["scale_result"]) as tracker:
            self.play(GrowArrow(arrow), FadeIn(result, shift=RIGHT * 0.1), run_time=1.0)
            self.play(FadeIn(oom, shift=LEFT * 0.1), FadeIn(arxiv_year, shift=UP * 0.1),
                      run_time=min(1.8, tracker.duration))

        banner = txt("RẺ  ·  CÂN BẰNG  ·  MỞ RỘNG TRIỆU NỐT", size=BODY_SIZE - 2, color=C_GOOD, weight=BOLD)
        banner.move_to([0, -2.7, 0])
        with self.voiceover(text=VO["scale_verdict"]) as tracker:
            self.play(FadeIn(banner, shift=UP * 0.1), run_time=min(1.2, tracker.duration))
        self.add(source("Bảng 5, tr.9"))
        self.wait(0.4)


class S5_11_Callout(GlanceScene):
    """Chốt lại toàn bộ mạch GLANCE, nối lại câu hỏi mở đầu Section 1."""

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        head = heading("Chốt lại — GLANCE trong năm ý", color=C_ROUTER).to_edge(UP, buff=0.85)
        with self.voiceover(text=VO["final_reconnect"]) as tracker:
            self.play(Write(head), run_time=min(2.2, tracker.duration))

        items = [
            (VO["final_1"], C_GNN), (VO["final_2"], C_ROUTER), (VO["final_3"], C_LLM),
            (VO["final_4"], C_GOOD), (VO["final_5"], C_LLM),
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
            not_more = txt("KHÔNG PHẢI NHIỀU LLM HƠN", size=HEAD_SIZE - 4, color=C_BAD, weight=BOLD)
            not_more.move_to([0, 0.6, 0])
            strike = Line(not_more.get_left(), not_more.get_right(), color=C_BAD, stroke_width=6)
            final_line = txt("MÀ LÀ LLM ĐÚNG CHỖ HƠN.", size=TITLE_SIZE - 6, color=C_GOOD, weight=BOLD)
            final_line.move_to([0, -0.4, 0])
            self.play(Write(not_more), run_time=1.0)
            self.play(Create(strike), run_time=0.5)
            self.play(Write(final_line), Flash(final_line, color=C_GOOD, flash_radius=1.0),
                      run_time=min(1.6, tracker.duration))
        self.wait(0.8)
