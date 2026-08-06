"""Section 2 — Đánh giá các routing heuristic hiện có.  Owner: Hoàng Phan.

Nguồn trong paper: §4 mở đầu, §4.1 + Bảng 1 (tr.3–4)
Nhiệm vụ chi tiết: sections/s2_hoangphan/TASK.md

Chữ trên hình: tiếng Anh. Phụ đề: tiếng Việt (kịch bản thu tiếng).

Render:  manim -ql sections/s2_hoangphan/s2_hoangphan.py -a
"""

import pathlib
import sys

# Cho phép import glance_style.py ở thư mục gốc repo.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from glance_style import *  # noqa: E402,F403

SECTION = "2"
SECTION_NAME = "Routing heuristic"
OWNER = "Hoàng Phan"
ACCENT = SECTION_COLORS.get(SECTION, C_HIGHLIGHT)

SRC_T1 = "Bảng 1, tr.4"

# --------------------------------------------------------------------------
# Nhịp thuyết minh
#
# Mỗi nhịp là một khối `self.voiceover()`: audio do backend TTS sinh, nhịp hình
# bám theo `tracker.duration` chứ không ước bằng tay nữa. Khối `with` tự chờ nốt
# phần audio còn thừa khi animation ngắn hơn câu đọc, nên không cần canh run_time.
# Phụ đề .srt cũng do plugin sinh thẳng từ `text`, không add_subcaption thủ công.
#
# Lời thoại viết theo cách ĐỌC LÊN, dùng phiên âm đã chốt trong plan.md:
#   "LLM" -> "eo eo em"   "GNN" -> "gi en en"   "node" -> "nót"
# --------------------------------------------------------------------------


def beat(scene, text, *anims, run_time=1.0):
    """Một nhịp nói: chạy animation trong lúc đọc, rồi giữ hình cho hết câu."""
    with scene.voiceover(text=text) as tracker:
        if anims:
            scene.play(*anims, run_time=min(run_time, tracker.duration))


# --------------------------------------------------------------------------
# Bảng 1 (tr.4), cột Enhanced features. Không làm tròn lại.
# Thứ tự cột: Cora 10/15/20 · Pubmed 10/15/20 · Arxiv23 10/15/20
# --------------------------------------------------------------------------

STRATS = ["Random", "C-density", "Degree", "Uncertainty"]
T1 = {
    "GCN": {
        "Random":      [-0.02, -0.06, -0.04, 0.06, 0.05, 0.04, 0.05, 0.04, 0.04],
        "C-density":   [-0.02, -0.03, -0.03, 0.05, 0.06, 0.05, 0.07, 0.07, 0.06],
        "Degree":      [-0.04, -0.01, -0.02, 0.04, 0.04, 0.04, 0.04, 0.05, 0.05],
        "Uncertainty": [-0.09, -0.03, -0.01, 0.20, 0.18, 0.17, 0.15, 0.13, 0.13],
    },
    "GCNII": {
        "Random":      [0.00, 0.01, -0.01, 0.01, 0.01, 0.01, -0.01, 0.00, 0.00],
        "C-density":   [0.00, -0.03, -0.03, 0.02, 0.02, 0.02, 0.03, 0.03, 0.03],
        "Degree":      [-0.03, -0.03, -0.02, 0.03, 0.03, 0.03, -0.03, -0.02, -0.01],
        "Uncertainty": [-0.04, -0.02, -0.03, 0.09, 0.08, 0.08, 0.05, 0.04, 0.05],
    },
}
DATASETS = ["Cora", "Pubmed", "Arxiv23"]
KS = ["10%", "15%", "20%"]


def ncs_color(value, cap=0.22):
    """Thang đỏ → nền → xanh cho heatmap Bảng 1. Chỉ pha từ màu có sẵn."""
    t = max(-1.0, min(1.0, value / cap))
    end = C_GOOD if t >= 0 else C_BAD
    return interpolate_color(ManimColor(BG), ManimColor(end), abs(t) ** 0.75)


# --------------------------------------------------------------------------
# Đồ thị dùng trong section
#
# demo_tag() là đồ thị 12 node dùng chung cả video. Nó hợp với phần degree một
# cách may mắn: node 7 degree 2 nhưng cả hai hàng xóm cùng class (dễ), node 9
# degree 4 nhưng homophily 0.25 (khó). Đúng hai phản ví dụ cần cho heuristic
# degree, nên giữ nguyên đồ thị chung thay vì vẽ đồ thị riêng.
# --------------------------------------------------------------------------

DEG = {n: sum(1 for u, v in DEMO_EDGES if n in (u, v)) for n in DEMO_POS}
LOW_DEGREE = [7, 10, 11]      # degree 2, tập mà degree-based routing chọn
EASY_LOW_DEG = 7              # degree 2, homophily 1.0 → GNN vốn đã đúng
HARD_HIGH_DEG = 9             # degree 4, homophily 0.25 → GNN sai, không được route


def neighbors_of(n):
    out = []
    for u, v in DEMO_EDGES:
        if u == n:
            out.append(v)
        elif v == n:
            out.append(u)
    return out


def deg_label(graph, n, color=ACCENT):
    return mono(f"deg {DEG[n]}", size=17, color=color).next_to(
        graph.nodes[n], UP, buff=0.18).set_z_index(4)


# ===========================================================================
class S2_01_Title(GlanceScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        card = title_card(
            f"{SECTION} — {SECTION_NAME}",
            "Do existing heuristics pick the right nodes?",
            OWNER,
            accent=ACCENT,
        )
        beat(self, "Nếu chỉ gọi eo eo em cho một phần nót, ta chọn nót nào?",
             FadeIn(card, shift=UP * 0.3), run_time=1.2)
        beat(self, "Phần này đánh giá ba tiêu chí đã được dùng trước gờ lans.")
        self.play(FadeOut(card), run_time=0.6)


# ===========================================================================
class S2_02_TwoQuestions(GlanceScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()

        def qcard(tag, text, color):
            t = txt(tag, size=SMALL_SIZE, color=color, weight=BOLD)
            b = txt(text, size=BODY_SIZE, color=INK, line_spacing=0.85)
            inner = VGroup(t, b).arrange(DOWN, buff=0.28, aligned_edge=LEFT)
            return VGroup(panel(inner, color=color, buff=0.42), inner)

        q1 = qcard("QUESTION 1", "Which nodes look HARD\nfor the GNN?", C_GNN)
        q2 = qcard("QUESTION 2", "Which nodes ACTUALLY\nimprove with an LLM?", C_LLM)
        VGroup(q1, q2).arrange(RIGHT, buff=0.8, aligned_edge=UP).shift(UP * 0.5)

        beat(self, "Để đánh giá các quy tắc kinh nghiệm, cần tách bạch hai câu hỏi.",
             FadeIn(q1, shift=RIGHT * 0.3), run_time=0.9)
        beat(self, "Câu thứ nhất: nót nào có vẻ khó đối với gi en en?")
        beat(self, "Câu thứ hai: nót nào thực sự được cải thiện nhờ eo eo em?",
             FadeIn(q2, shift=LEFT * 0.3), run_time=0.9)

        # --- Venn: hai tập không trùng nhau -----------------------------------
        c1 = Circle(radius=1.55, stroke_color=C_GNN, stroke_width=3.2).set_fill(C_GNN, 0.12)
        c2 = Circle(radius=1.55, stroke_color=C_LLM, stroke_width=3.2).set_fill(C_LLM, 0.12)
        c1.move_to(LEFT * 0.9 + DOWN * 0.6)
        c2.move_to(RIGHT * 0.9 + DOWN * 0.6)
        lens = Intersection(c1, c2, fill_color=C_ROUTER, fill_opacity=0.55, stroke_width=0)
        n1 = txt("GNN difficulty", size=SMALL_SIZE, color=C_GNN).next_to(c1, LEFT, buff=0.2)
        n2 = txt("LLM advantage", size=SMALL_SIZE, color=C_LLM).next_to(c2, RIGHT, buff=0.2)
        core = txt("the overlap: nodes worth routing", size=SMALL_SIZE,
                   color=C_ROUTER, weight=BOLD).next_to(VGroup(c1, c2), DOWN, buff=0.4)

        self.play(FadeOut(q1, shift=UP * 0.3), FadeOut(q2, shift=UP * 0.3), run_time=0.6)
        beat(self, "Hai câu hỏi nghe giống nhau, nhưng tập nót thì không trùng.",
             Create(c1), Create(c2), FadeIn(n1), FadeIn(n2), run_time=1.2)
        beat(self, "Chỉ phần giao mới đáng để trả chi phí gọi eo eo em.",
             FadeIn(lens), Write(core), run_time=1.0)
        beat(self, "Các quy tắc kinh nghiệm trước gờ lans chủ yếu chỉ trả lời câu thứ nhất.",
             c1.animate.set_fill(C_GNN, 0.4), run_time=1.0)

        # --- ba heuristic ------------------------------------------------------
        cards = VGroup(
            self._hcard("Node degree", "E-LLaGNN"),
            self._hcard("Clustering density", "LLM-GNN"),
            self._hcard("GNN uncertainty", "LOGIN"),
        ).arrange(RIGHT, buff=0.5).shift(DOWN * 0.2)
        head = txt("Three representative signals", size=BODY_SIZE,
                   color=INK).next_to(cards, UP, buff=0.9)

        self.play(FadeOut(VGroup(c1, c2, lens, n1, n2, core), shift=DOWN * 0.4), run_time=0.6)
        beat(self, "bài báo xem xét ba tín hiệu đại diện.", FadeIn(head), run_time=0.6)
        for card, line in zip(cards, [
            "Node degree, dùng trong E-LLaGNN.",
            "Clustering density, dùng trong LLM-GNN.",
            "Và GNN uncertainty, dùng trong LOGIN.",
        ]):
            beat(self, line, FadeIn(card, shift=DOWN * 0.25), run_time=0.7)
        beat(self, "Ta sẽ lần lượt đem cả ba ra thử.")
        self.clear_scene()

    @staticmethod
    def _hcard(name, method):
        n = txt(name, size=22, color=ACCENT, weight=BOLD)
        m = mono(method, size=17, color=MUTED)
        inner = VGroup(n, m).arrange(DOWN, buff=0.2)
        return VGroup(panel(inner, buff=0.34), inner)


# ===========================================================================
class S2_03_Degree(GlanceScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        head = heading("Heuristic 1: Node degree", color=ACCENT).to_edge(UP, buff=0.85)
        sub = mono("E-LLaGNN  ·  route the lowest-degree nodes", size=18,
                   color=MUTED).next_to(head, DOWN, buff=0.18)
        g = demo_tag().scale(1.05).shift(DOWN * 0.55)

        beat(self, "quy tắc kinh nghiệm đầu tiên là nót bậc.", FadeIn(head), FadeIn(sub), run_time=0.8)
        beat(self, "bậc là số hàng xóm nối với nót đó.")
        beat(self, "nót bậc thấp nhận ít thông tin qua truyền thông điệp.")
        beat(self, "Nên gi en en có thể gặp khó, và ta ưu tiên định tuyến chúng sang eo eo em.",
             Create(g.edges),
             LaggedStart(*[GrowFromCenter(d) for d in g.nodes.values()], lag_ratio=0.06),
             run_time=1.8)
        beat(self, "Màu nót là lớp thật của nó.")

        # --- tập được route -----------------------------------------------------
        rings = VGroup(*[
            Circle(radius=0.3, color=C_ROUTER, stroke_width=3).move_to(g.nodes[n])
            for n in LOW_DEGREE
        ])
        tags = VGroup(*[deg_label(g, n, C_ROUTER) for n in LOW_DEGREE])
        chip = VGroup(panel(txt("Routed to the LLM", size=19, color=C_ROUTER), buff=0.26),
                      txt("Routed to the LLM", size=19, color=C_ROUTER))
        chip.to_corner(UR, buff=0.6)

        beat(self, "Đây là các nót bậc thấp nhất, chúng sẽ được định tuyến.",
             LaggedStart(*[Create(r) for r in rings], lag_ratio=0.12),
             LaggedStart(*[FadeIn(t) for t in tags], lag_ratio=0.12),
             FadeIn(chip), run_time=1.6)

        # --- phản ví dụ 1: degree thấp nhưng dễ ----------------------------------
        keep = {EASY_LOW_DEG, *neighbors_of(EASY_LOW_DEG)}
        dim_nodes = VGroup(*[d for i, d in g.nodes.items() if i not in keep])
        dim_edges = VGroup(*[
            m for (u, v), m in zip(DEMO_EDGES, g.edges) if not ({u, v} <= keep)
        ])
        dim_rings = VGroup(*[r for n, r in zip(LOW_DEGREE, rings) if n != EASY_LOW_DEG])
        dim_tags = VGroup(*[t for n, t in zip(LOW_DEGREE, tags) if n != EASY_LOW_DEG])
        ok = check(size=0.5).next_to(g.nodes[EASY_LOW_DEG], RIGHT, buff=0.5).set_z_index(4)
        msg1 = txt("Both neighbors share its class. The GNN was already right.",
                   size=21, color=C_GOOD).to_edge(DOWN, buff=0.5)

        beat(self, "Nhưng hãy nhìn kỹ nót này. Nó chỉ có hai hàng xóm.",
             dim_nodes.animate.set_opacity(0.15), dim_edges.animate.set_opacity(0.15),
             dim_rings.animate.set_opacity(0.15), dim_tags.animate.set_opacity(0.15),
             run_time=1.2)
        beat(self, "Cả hai hàng xóm đều cùng lớp với nó.",
             Create(ok), run_time=0.8)
        beat(self, "truyền thông điệp chỉ đưa vào tín hiệu đồng thuận.", FadeIn(msg1), run_time=0.6)
        beat(self, "gi en en vốn đã đúng ở đây. Gọi eo eo em chỉ là lãng phí tiền.")

        self.play(dim_nodes.animate.set_opacity(1), dim_edges.animate.set_opacity(1),
                  dim_rings.animate.set_opacity(1), dim_tags.animate.set_opacity(1),
                  FadeOut(ok), FadeOut(msg1), run_time=0.7)

        # --- phản ví dụ 2: degree cao nhưng khó ----------------------------------
        hub_nb = neighbors_of(HARD_HIGH_DEG)
        keep2 = {HARD_HIGH_DEG, *hub_nb}
        dim2_nodes = VGroup(*[d for i, d in g.nodes.items() if i not in keep2])
        dim2_edges = VGroup(*[
            m for (u, v), m in zip(DEMO_EDGES, g.edges) if not ({u, v} <= keep2)
        ])
        hub_edges = VGroup(*[
            m for (u, v), m in zip(DEMO_EDGES, g.edges) if HARD_HIGH_DEG in (u, v)
        ])
        hub_tag = VGroup(
            panel(mono("degree = 4", size=17, color=C_BAD), buff=0.18, fill_opacity=0.95),
            mono("degree = 4", size=17, color=C_BAD),
        ).next_to(g.nodes[HARD_HIGH_DEG], DOWN, buff=0.4).set_z_index(4)
        bad = cross(size=0.42).next_to(g.nodes[HARD_HIGH_DEG], RIGHT, buff=0.55).set_z_index(4)
        msg2 = txt("Degree 4, but 3 of 4 neighbors are a different class.",
                   size=21, color=C_BAD).to_edge(DOWN, buff=0.5)

        beat(self, "Bây giờ ngược lại, hãy nhìn nót này.",
             dim2_nodes.animate.set_opacity(0.15), dim2_edges.animate.set_opacity(0.15),
             rings.animate.set_opacity(0.15), tags.animate.set_opacity(0.15),
             FadeIn(hub_tag), run_time=1.2)
        beat(self, "bậc của nó cao gấp đôi, nên quy tắc kinh nghiệm bỏ qua.")
        beat(self, "Nhưng ba trong bốn hàng xóm lại khác lớp với nó.",
             hub_edges.animate.set_stroke(color=C_BAD, width=3.2),
             FadeIn(msg2), run_time=1.2)
        beat(self, "truyền thông điệp trộn tín hiệu mâu thuẫn, gi en en dự đoán sai.",
             Create(bad), run_time=0.8)
        beat(self, "Đây mới đúng là nót cần eo eo em, nhưng nó không được chọn.")

        # --- chốt --------------------------------------------------------------
        self.clear_scene()
        punch = VGroup(
            txt("Degree measures the AMOUNT of structural information,", size=24, color=INK),
            txt("not the QUALITY of that information.", size=24, color=ACCENT, weight=BOLD),
        ).arrange(DOWN, buff=0.26)
        beat(self, "bậc chỉ đo số lượng thông tin cấu trúc.", Write(punch), run_time=1.6)
        beat(self, "Nó không đo chất lượng của thông tin đó.")
        beat(self, "bậc thấp cũng không đảm bảo văn bản của nót đủ rõ cho eo eo em.")


# ===========================================================================
class S2_04_Density(GlanceScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        head = heading("Heuristic 2: Clustering density", color=ACCENT).to_edge(UP, buff=0.85)
        sub = mono("LLM-GNN  ·  route the lowest-density nodes", size=18,
                   color=MUTED).next_to(head, DOWN, buff=0.18)
        g = demo_tag().scale(1.05).shift(DOWN * 0.55)
        self.add(head, sub, g)

        beat(self, "quy tắc kinh nghiệm thứ hai là mật độ phân cụm.")
        beat(self, "Nó đo xem các hàng xóm của một nót có nối với nhau không.")
        beat(self, "Tức nót đó nằm trong một cụm chặt chẽ tới mức nào.")
        beat(self, "Giả định: nót ở vùng thưa thì gi en en khó mô hình hoá.")

        # Cụm tam giác 0-1-4 / 0-3-4: dày đặc và toàn class A.
        tri = VGroup(
            Polygon(*[g.nodes[i].get_center() for i in (0, 1, 4)],
                    fill_color=C_HIGHLIGHT, fill_opacity=0.16, stroke_width=0),
            Polygon(*[g.nodes[i].get_center() for i in (0, 3, 4)],
                    fill_color=C_HIGHLIGHT, fill_opacity=0.16, stroke_width=0),
            Polygon(*[g.nodes[i].get_center() for i in (1, 2, 4)],
                    fill_color=C_HIGHLIGHT, fill_opacity=0.16, stroke_width=0),
        ).set_z_index(-2)
        dense_tag = mono("high density", size=17, color=C_HIGHLIGHT).next_to(
            g.nodes[4], UP, buff=0.55).set_z_index(4)

        beat(self, "Vùng này nhiều tam giác nên mật độ cao, quy tắc kinh nghiệm bỏ qua.",
             FadeIn(tri), FadeIn(dense_tag), run_time=1.3)
        beat(self, "Và ở đây quy tắc kinh nghiệm đúng: cả cụm cùng một lớp, gi en en xử lý tốt.")

        # Node 2: density thấp (1/6) nhưng homophily 0.75 → dễ, vẫn bị route.
        ring2 = Circle(radius=0.3, color=C_ROUTER, stroke_width=3).move_to(g.nodes[2])
        tag2 = mono("low density", size=17, color=C_ROUTER).next_to(
            g.nodes[2], RIGHT, buff=0.3).set_z_index(4)
        msg = txt("Sparse neighborhood, but 3 of 4 neighbors still share its class.",
                  size=21, color=C_GOOD).to_edge(DOWN, buff=0.5)

        beat(self, "Nhưng nhìn nót này: hàng xóm của nó gần như không nối với nhau.",
             FadeOut(tri), FadeOut(dense_tag), Create(ring2), FadeIn(tag2), run_time=1.2)
        beat(self, "mật độ thấp nên nó bị định tuyến.")
        beat(self, "Vậy mà ba trên bốn hàng xóm vẫn cùng lớp với nó.",
             FadeIn(msg), run_time=0.8)
        beat(self, "Thưa, nhưng vẫn dễ. Một lời gọi eo eo em nữa bị phí.")

        self.clear_scene()
        punch = VGroup(
            txt("Density describes the SHAPE of a neighborhood.", size=24, color=INK),
            txt("It says nothing about the LABELS of the neighbors.", size=24,
                color=ACCENT, weight=BOLD),
        ).arrange(DOWN, buff=0.26)
        beat(self, "mật độ chỉ mô tả hình dạng của vùng lân cận.", Write(punch), run_time=1.6)
        beat(self, "Nó không nói gì về nhãn của các hàng xóm.")
        beat(self, "Cũng chỉ là một tín hiệu thay thế gián tiếp cho độ khó.")


# ===========================================================================
class S2_05_Uncertainty(GlanceScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        bnr = self.banner()
        head = heading("Heuristic 3: GNN uncertainty", color=ACCENT).to_edge(UP, buff=0.85)
        sub = mono("LOGIN  ·  route the highest-uncertainty nodes", size=18,
                   color=MUTED).next_to(head, DOWN, buff=0.18)

        base = RIGHT * 2.9 + DOWN * 1.5
        bar_w, gap, unit = 0.7, 0.4, 2.9
        cols = [C_GNN, C_LLM, C_ROUTER]

        def make_bars(vals):
            grp = VGroup()
            for i, (v, c) in enumerate(zip(vals, cols)):
                r = Rectangle(width=bar_w, height=max(v, 0.004) * unit,
                              fill_color=c, fill_opacity=0.9, stroke_width=0)
                r.move_to(base + RIGHT * (i - 1) * (bar_w + gap), aligned_edge=DOWN)
                grp.add(r)
            return grp

        axis = Line(base + LEFT * 1.9, base + RIGHT * 1.9, stroke_color=C_EDGE, stroke_width=2)
        ticks = VGroup(*[
            mono(n, size=17, color=cols[i]).next_to(
                base + RIGHT * (i - 1) * (bar_w + gap), DOWN, buff=0.2)
            for i, n in enumerate(["A", "B", "C"])
        ])
        ylab = mono("P(class)", size=16, color=MUTED).next_to(base + LEFT * 1.9, UP, buff=1.5)
        passes = [[0.42, 0.38, 0.20], [0.24, 0.55, 0.21], [0.51, 0.30, 0.19], [0.29, 0.34, 0.37]]
        bars = make_bars(passes[0])
        node = Dot(LEFT * 3.2 + DOWN * 0.6, radius=0.26, color=C_GNN)
        nlab = mono("node v", size=17, color=MUTED).next_to(node, DOWN, buff=0.28)
        counter = mono("forward pass 1 / 4", size=18, color=MUTED)
        counter.next_to(VGroup(axis, ylab), UP, buff=0.4)
        arrow = Arrow(node.get_right(), axis.get_left() + LEFT * 0.15, buff=0.3,
                      stroke_width=3, color=C_EDGE, max_tip_length_to_length_ratio=0.12)

        beat(self, "quy tắc kinh nghiệm thứ ba là gi en en độ bất định.", FadeIn(head), FadeIn(sub), run_time=0.8)
        beat(self, "Mô hình chạy nhiều lần lượt truyền xuôi với đờ-róp-ao bật.",
             GrowFromCenter(node), FadeIn(nlab), GrowArrow(arrow), Create(axis),
             FadeIn(ticks), FadeIn(ylab), FadeIn(counter), FadeIn(bars), run_time=1.3)
        beat(self, "Mỗi lần, một phần neuron bị tắt ngẫu nhiên.")
        for i, vals in enumerate(passes[1:], start=2):
            self.play(Transform(bars, make_bars(vals)),
                      Transform(counter, mono(f"forward pass {i} / 4", size=18,
                                              color=MUTED).move_to(counter)),
                      run_time=0.7)
        beat(self, "Dự đoán dao động nhiều thì nót đó bị coi là không chắc chắn.")

        verdict = VGroup(panel(txt("high uncertainty", size=20, color=ACCENT), buff=0.24),
                         txt("high uncertainty", size=20, color=ACCENT))
        verdict.next_to(VGroup(axis, ticks), DOWN, buff=0.7)
        beat(self, "So với bậc và mật độ, độ bất định trực tiếp hơn hẳn.",
             FadeIn(verdict), run_time=0.7)
        beat(self, "Vì nó phản ánh trạng thái của chính mô hình gi en en.")
        beat(self, "Nhưng độ bất định cao chỉ nói rằng gi en en đang gặp khó.")
        beat(self, "Nó không đảm bảo eo eo em sẽ làm tốt hơn.")

        self.clear_scene(keep=(bnr,))

        # --- hai node cùng uncertainty, hai kết cục ------------------------------
        def case(tag, snippet, outcome, color, mark):
            # text_chip() chỉ dựng một dòng rồi co lại cho vừa bề rộng, trích dẫn
            # dài sẽ nhỏ tới mức không đọc được. Dựng bằng txt() nhiều dòng + panel().
            t = txt(tag, size=17, color=MUTED, weight=BOLD)
            quote = txt(snippet, size=18, color=INK, line_spacing=0.9)
            quote_box = VGroup(panel(quote, color=C_EDGE, buff=0.28, fill_opacity=0.5), quote)
            res = VGroup(mark, txt(outcome, size=21, color=color, weight=BOLD)).arrange(
                RIGHT, buff=0.28)
            inner = VGroup(t, quote_box, res).arrange(DOWN, buff=0.3)
            return VGroup(panel(inner, color=color, buff=0.36), inner)

        left = case("NODE 1 · CLEAR TEXT",
                    '"Support vector machines for\ntext categorization: we propose\n'
                    'a kernel-based classifier..."',
                    "LLM fixes it", C_GOOD, check())
        right = case("NODE 2 · VAGUE TEXT",
                     '"A note on the complexity\nof the problem."',
                     "LLM fails too", C_BAD, cross())
        cases = VGroup(left, right).arrange(RIGHT, buff=0.6, aligned_edge=UP).shift(DOWN * 0.3)
        same = VGroup(panel(txt("Same high uncertainty", size=20, color=ACCENT), buff=0.24),
                      txt("Same high uncertainty", size=20, color=ACCENT))
        same.next_to(cases, DOWN, buff=0.4)

        beat(self, "Hãy xét hai nót có cùng mức độ bất định cao.")
        beat(self, "nót thứ nhất: cấu trúc nhiễu, nhưng phần tóm tắt nói rất rõ chủ đề.",
             FadeIn(left, shift=RIGHT * 0.3), run_time=1.0)
        beat(self, "eo eo em đọc đoạn văn bản này và sửa được dự đoán.")
        beat(self, "nót thứ hai: cấu trúc nhiễu y hệt, nhưng văn bản ngắn và mơ hồ.",
             FadeIn(right, shift=LEFT * 0.3), run_time=1.0)
        beat(self, "Ở đây eo eo em cũng không đủ thông tin, gọi thêm chỉ tốn tiền.")
        beat(self, "Cùng một tín hiệu độ bất định, hai kết cục khác hẳn nhau.",
             FadeIn(same), run_time=0.7)

        self.clear_scene(keep=(bnr,))

        # --- rủi ro rewiring của LOGIN -------------------------------------------
        a = Dot(LEFT * 1.5 + DOWN * 0.2, radius=0.24, color=C_GNN)
        b = Dot(RIGHT * 1.5 + DOWN * 0.2, radius=0.24, color=C_LLM)
        e = Line(a.get_center(), b.get_center(), stroke_color=C_EDGE, stroke_width=4)
        elab = mono("heterophilous edge", size=17, color=MUTED).next_to(e, UP, buff=0.25)
        cut = cross(size=0.4).move_to(e).set_z_index(4)
        warn = txt("Cutting hard edges can cut useful information too.",
                   size=22, color=C_BAD).next_to(e, DOWN, buff=1.0)

        beat(self, "Ngoài ra, lô gin còn dùng eo eo em để nối lại cạnh đồ thị.",
             Create(e), GrowFromCenter(a), GrowFromCenter(b), FadeIn(elab), run_time=1.0)
        beat(self, "Tức là chỉnh sửa hoặc loại bỏ những cạnh khó.")
        beat(self, "Việc này có rủi ro riêng.", Create(cut),
             e.animate.set_stroke(color=C_BAD, opacity=0.25), run_time=0.8)
        beat(self, "Nó có thể xoá nhầm cạnh dị phối vẫn đang mang thông tin.",
             FadeIn(warn), run_time=0.7)

        self.clear_scene()
        punch = VGroup(
            txt("Uncertainty reads the state of the GNN.", size=24, color=INK),
            txt("But it cannot read the LLM.", size=24, color=ACCENT, weight=BOLD),
        ).arrange(DOWN, buff=0.26)
        beat(self, "độ bất định đọc được trạng thái của gi en en.", Write(punch), run_time=1.5)
        beat(self, "Nhưng nó không đọc được eo eo em.")


# ===========================================================================
class S2_06_Setup(GlanceScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        head = heading("How do we evaluate a heuristic fairly?",
                       color=ACCENT).to_edge(UP, buff=0.9)

        beat(self, "Vậy đánh giá một định tuyến quy tắc kinh nghiệm thế nào cho công bằng?",
             Write(head), run_time=1.4)
        beat(self, "bài báo không chỉ nhìn độ chính xác của gi en en trên nhóm nót bị coi là khó.")
        beat(self, "Thay vào đó, kiểm tra thẳng điều gì xảy ra sau khi định tuyến.")

        flow = pipeline([
            ("Graph", C_EDGE),
            ("Heuristic", C_ROUTER),
            ("Top-k% nodes", C_LLM),
            ("LLM", C_LLM),
            ("Compare vs GNN", C_GOOD),
        ], box_w=2.25, box_h=0.9, buff=0.4).shift(UP * 0.65)
        frozen = mono("both GNN and LLM are frozen", size=18,
                      color=C_GNN).next_to(flow, DOWN, buff=0.55)

        beat(self, "Từ đồ thị, quy tắc kinh nghiệm chọn ra tốp ca phần trăm nót.",
             LaggedStart(*[FadeIn(b, shift=RIGHT * 0.2) for b in flow.boxes], lag_ratio=0.16),
             LaggedStart(*[GrowArrow(a) for a in flow.arrows], lag_ratio=0.16), run_time=2.0)
        beat(self, "Những nót đó đi qua eo eo em, rồi so với dự đoán gốc của gi en en.")
        beat(self, "Quan trọng: cả gi en en lẫn eo eo em đều được đóng băng.", FadeIn(frozen), run_time=0.7)
        beat(self, "Nên mọi khác biệt chỉ đến từ việc quy tắc kinh nghiệm đã chọn tập nót nào.")

        def chips(label, items, color):
            lab = mono(label, size=17, color=MUTED)
            row = VGroup()
            for i in items:
                t = txt(i, size=19, color=color)
                row.add(VGroup(panel(t, buff=0.18), t))
            row.arrange(RIGHT, buff=0.22)
            return VGroup(lab, row).arrange(DOWN, buff=0.22)

        cfg = VGroup(
            chips("DATASET", DATASETS, INK),
            chips("BACKBONE", ["GCN", "GCNII"], C_GNN),
            chips("FEATURES", ["original", "enhanced"], C_LLM),
            chips("BUDGET", KS, C_ROUTER),
        ).arrange(RIGHT, buff=0.55).next_to(frozen, DOWN, buff=0.6)
        cfg.scale_to_fit_width(12.2)

        beat(self, "Thí nghiệm chạy trên cô ra, pắp mét và ác xíp hai ba.",
             FadeIn(cfg[0]), run_time=0.7)
        beat(self, "Hai mô hình nền: gờ xê en là mô hình cơ sở, gờ xê en hai mạnh hơn.",
             FadeIn(cfg[1]), run_time=0.7)
        beat(self, "Hai loại đặc trưng: gốc, và tăng cường sinh bởi quy en ba tám bi.",
             FadeIn(cfg[2]), run_time=0.7)
        beat(self, "Mỗi quy tắc kinh nghiệm định tuyến tốp mười, mười lăm, rồi hai mươi phần trăm.",
             FadeIn(cfg[3]), run_time=0.7)

        self.clear_scene()
        rules = bullets([
            "Degree-based: pick the LOWEST-degree nodes",
            "Density-based: pick the LOWEST-density nodes",
            "Uncertainty-based: pick the HIGHEST-uncertainty nodes",
            "Random routing: the baseline to beat",
        ], size=23, dot_color=ACCENT, width=9.0)

        beat(self, "Cụ thể: cách dựa trên bậc chọn nót có bậc thấp nhất.",
             FadeIn(rules[0], shift=RIGHT * 0.2), run_time=0.7)
        beat(self, "Cách dựa trên mật độ chọn nót có mật độ phân cụm thấp nhất.",
             FadeIn(rules[1], shift=RIGHT * 0.2), run_time=0.7)
        beat(self, "Cách dựa trên độ bất định chọn nót có độ bất định cao nhất.",
             FadeIn(rules[2], shift=RIGHT * 0.2), run_time=0.7)
        beat(self, "Và ngẫu nhiên định tuyến làm mốc so sánh.",
             FadeIn(rules[3], shift=RIGHT * 0.2), run_time=0.7)
        beat(self, "Đây là cái mốc mà mọi quy tắc kinh nghiệm ít nhất phải vượt qua.",
             Circumscribe(rules[3], color=MUTED, buff=0.16), run_time=1.4)


# ===========================================================================
class S2_07_NCS(GlanceScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        head = heading("Net Correction Score", color=ACCENT).to_edge(UP, buff=0.85)
        sub = mono("NCS  ·  the net benefit of routing", size=18,
                   color=MUTED).next_to(head, DOWN, buff=0.18)

        def defn(tag, desc, color, mark):
            t = VGroup(mark, mono(tag, size=20, color=color)).arrange(RIGHT, buff=0.26)
            d = txt(desc, size=20, color=INK, line_spacing=0.9)
            inner = VGroup(t, d).arrange(DOWN, buff=0.24, aligned_edge=LEFT)
            return VGroup(panel(inner, color=color, buff=0.34), inner)

        wc = defn("WC  (wrong to correct)",
                  "GNN wrong, LLM makes it right.\nA BENEFICIAL correction.", C_GOOD, check())
        cw = defn("CW  (correct to wrong)",
                  "GNN right, LLM makes it wrong.\nA HARMFUL correction.", C_BAD, cross())
        defs = VGroup(wc, cw).arrange(RIGHT, buff=0.6, aligned_edge=UP).shift(DOWN * 0.3)

        beat(self, "Để đo chất lượng tập nót được định tuyến, bài báo dùng điểm sửa ròng.",
             FadeIn(head), FadeIn(sub), run_time=0.9)
        beat(self, "Viết tắt là en xi ét. Ý tưởng rất trực quan.")
        beat(self, "gi en en sai mà eo eo em sửa thành đúng: một lần sửa có lợi.",
             FadeIn(wc, shift=RIGHT * 0.3), run_time=1.0)
        beat(self, "Tập này gọi là đắp-bờ-liu xi, sai thành đúng.")
        beat(self, "gi en en đúng mà eo eo em làm thành sai: một lần sửa có hại.",
             FadeIn(cw, shift=LEFT * 0.3), run_time=1.0)
        beat(self, "Tập này gọi là xi đắp-bờ-liu, đúng thành sai.")

        formula = MathTex(r"\mathrm{NCS} \;=\; \frac{|WC| - |CW|}{|R|}",
                          color=INK).scale(1.15).shift(DOWN * 0.3)
        self.play(FadeOut(defs), run_time=0.5)
        beat(self, "en xi ét bằng số nót trong đắp-bờ-liu xi trừ số nót trong xi đắp-bờ-liu.",
             Write(formula), run_time=1.6)
        beat(self, "Rồi chia cho tổng số nót được định tuyến.")

        # --- ví dụ 100 node ------------------------------------------------------
        self.play(formula.animate.scale(0.62).to_edge(RIGHT, buff=1.2).shift(UP * 0.6),
                  run_time=0.8)
        cells = VGroup()
        for i in range(100):
            cells.add(Square(side_length=0.26, fill_color=C_EDGE, fill_opacity=0.35,
                             stroke_color=C_EDGE, stroke_width=1.0)
                      .move_to(RIGHT * (i % 10) * 0.32 + DOWN * (i // 10) * 0.32))
        cells.move_to(LEFT * 3.2 + DOWN * 0.3)
        glab = mono("100 routed nodes", size=18, color=MUTED).next_to(cells, UP, buff=0.32)
        t_wc = VGroup(mono("WC", size=20, color=C_GOOD),
                      mono("25", size=28, color=C_GOOD)).arrange(RIGHT, buff=0.3)
        t_cw = VGroup(mono("CW", size=20, color=C_BAD),
                      mono("10", size=28, color=C_BAD)).arrange(RIGHT, buff=0.3)
        tallies = VGroup(t_wc, t_cw).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        tallies.next_to(formula, DOWN, buff=0.8)
        result = MathTex(r"\mathrm{NCS}=\frac{25-10}{100}=0.15",
                         color=INK).scale(0.9).next_to(tallies, DOWN, buff=0.6)

        beat(self, "Ví dụ, giả sử ta định tuyến một trăm nót.",
             LaggedStart(*[FadeIn(c) for c in cells], lag_ratio=0.006),
             FadeIn(glab), run_time=1.3)
        beat(self, "eo eo em sửa đúng được hai mươi lăm nót.",
             LaggedStart(*[c.animate.set_fill(C_GOOD, 0.9).set_stroke(C_GOOD)
                           for c in cells[:25]], lag_ratio=0.02),
             FadeIn(t_wc), run_time=1.4)
        beat(self, "Nhưng đồng thời làm hỏng mười nót.",
             LaggedStart(*[c.animate.set_fill(C_BAD, 0.9).set_stroke(C_BAD)
                           for c in cells[25:35]], lag_ratio=0.04),
             FadeIn(t_cw), run_time=1.3)
        beat(self, "en xi ét bằng hai mươi lăm trừ mười, chia một trăm, tức không phẩy mười lăm.",
             Write(result), run_time=1.2)

        # --- thang đo -------------------------------------------------------------
        self.clear_scene()
        axis = NumberLine(x_range=[-1, 1, 0.5], length=9.2, include_numbers=True,
                          decimal_number_config={"num_decimal_places": 1},
                          color=C_EDGE, font_size=24).shift(DOWN * 0.2)
        axis.numbers.set_color(MUTED)
        neg = Line(axis.n2p(-1), axis.n2p(0), stroke_color=C_BAD, stroke_width=7)
        pos = Line(axis.n2p(0), axis.n2p(1), stroke_color=C_GOOD, stroke_width=7)
        shead = txt("How to read an NCS value", size=24,
                    color=INK).next_to(axis, UP, buff=1.4)
        l_pos = txt("LLM yields net benefit", size=20,
                    color=C_GOOD).next_to(axis.n2p(0.5), DOWN, buff=0.8)
        l_zero = txt("break-even: paid for nothing", size=20,
                     color=MUTED).next_to(axis.n2p(0), UP, buff=0.5)
        l_neg = txt("more harm than good", size=20,
                    color=C_BAD).next_to(axis.n2p(-0.5), DOWN, buff=0.8)

        beat(self, "Cách đọc en xi ét như sau.", FadeIn(shead), Create(axis), run_time=1.1)
        beat(self, "en xi ét dương nghĩa là eo eo em tạo ra lợi ích ròng.",
             Create(pos), FadeIn(l_pos), run_time=0.9)
        beat(self, "en xi ét bằng không: số nót sửa được đúng bằng số nót bị làm hỏng.",
             FadeIn(l_zero), run_time=0.7)
        beat(self, "Toàn bộ chi phí gọi eo eo em coi như đổ sông đổ biển.")
        beat(self, "Còn en xi ét âm nghĩa là định tuyến gây hại nhiều hơn có lợi.",
             Create(neg), FadeIn(l_neg), run_time=0.9)

        self.clear_scene()
        punch = VGroup(
            txt("NCS does not reward finding hard nodes.", size=24, color=INK),
            txt("It rewards only the nodes the LLM actually fixes.", size=24,
                color=ACCENT, weight=BOLD),
        ).arrange(DOWN, buff=0.26)
        beat(self, "Điểm hay của en xi ét nằm ở đây.", Write(punch), run_time=1.6)
        beat(self, "Nó không thưởng cho việc tìm ra nót khó.")
        beat(self, "Nó chỉ thưởng khi eo eo em thật sự sửa được nót đó.")


# ===========================================================================
CELL_W, CELL_H = 0.74, 0.42


def build_heatmap():
    """Bảng 1 dưới dạng heatmap. Trả VGroup kèm .cell / .row / .block."""
    grid = VGroup()
    cell, row, row_lab, block_lab = {}, {}, {}, {}
    y = 0.0
    for backbone in ["GCN", "GCNII"]:
        bl = mono(f"{backbone} · Enh.", size=18, color=ACCENT)
        bl.move_to([-CELL_W * 4.5 - 1.5, y, 0], aligned_edge=LEFT)
        block_lab[backbone] = bl
        grid.add(bl)
        y -= CELL_H * 0.95
        for strat in STRATS:
            cells = VGroup()
            for c, v in enumerate(T1[backbone][strat]):
                rect = Rectangle(width=CELL_W, height=CELL_H, fill_color=ncs_color(v),
                                 fill_opacity=1.0, stroke_color=BG, stroke_width=1.2)
                rect.move_to([(c - 4) * CELL_W, y, 0])
                cells.add(VGroup(rect, mono(f"{v:.2f}", size=14, color=INK).move_to(rect)))
                cell[(backbone, strat, c)] = cells[-1]
            lab = mono(strat, size=17, color=MUTED if strat == "Random" else INK)
            lab.next_to(cells, LEFT, buff=0.28)
            row[(backbone, strat)] = cells
            row_lab[(backbone, strat)] = lab
            grid.add(cells, lab)
            y -= CELL_H
        y -= CELL_H * 0.5

    header = VGroup()
    for i, ds in enumerate(DATASETS):
        header.add(txt(ds, size=21, color=INK, weight=BOLD)
                   .move_to([(i * 3 + 1 - 4) * CELL_W, CELL_H * 2.0, 0]))
        header.add(Line([(i * 3 - 4.5) * CELL_W + 0.05, CELL_H * 1.5, 0],
                        [(i * 3 + 2.5) * CELL_W - 0.05, CELL_H * 1.5, 0],
                        stroke_color=C_EDGE, stroke_width=2))
    for c in range(9):
        header.add(mono(KS[c % 3], size=14, color=MUTED)
                   .move_to([(c - 4) * CELL_W, CELL_H * 1.05, 0]))

    g = VGroup(header, grid)
    g.cell, g.row, g.row_lab, g.block_lab, g.header = cell, row, row_lab, block_lab, header
    g.block = lambda bb: VGroup(block_lab[bb], *[row[(bb, s)] for s in STRATS],
                                *[row_lab[(bb, s)] for s in STRATS])
    g.cols = lambda ds: range(DATASETS.index(ds) * 3, DATASETS.index(ds) * 3 + 3)
    return g


class S2_08_Table1(GlanceScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        head = heading("Table 1 · NCS per routing strategy", color=ACCENT)
        head.scale_to_fit_width(min(head.width, 11.0)).to_edge(UP, buff=0.8)
        sub = mono("greener = more benefit  ·  redder = more harm", size=17,
                   color=MUTED).next_to(head, DOWN, buff=0.16)
        hm = build_heatmap().scale(0.88).move_to(LEFT * 0.9 + DOWN * 0.7)
        stamp = source(SRC_T1)

        beat(self, "Đây là Bảng 1 của bài báo, trình bày lại dưới dạng bản đồ nhiệt.",
             FadeIn(head), FadeIn(sub), run_time=0.9)
        beat(self, "Mỗi ô là một giá trị en xi ét.",
             FadeIn(hm.header), FadeIn(stamp), run_time=0.7)
        beat(self, "Ô càng xanh thì lợi ích càng cao, càng đỏ thì càng gây hại.",
             LaggedStart(*[FadeIn(hm.block(bb)) for bb in ["GCN", "GCNII"]], lag_ratio=0.3),
             run_time=1.7)
        beat(self, "Bốn hàng là bốn chiến lược, chín cột là ba bộ dữ liệu nhân ba mức định tuyến.")

        good = VGroup(*[hm.cell[(bb, "Uncertainty", c)] for bb in ["GCN", "GCNII"]
                        for ds in ["Pubmed", "Arxiv23"] for c in hm.cols(ds)])
        frames = VGroup(*[
            SurroundingRectangle(
                VGroup(*[hm.cell[(bb, "Uncertainty", c)] for bb in ["GCN", "GCNII"]
                         for c in hm.cols(ds)]),
                color=C_LLM, stroke_width=3, buff=0.05, corner_radius=0.04)
            for ds in ["Pubmed", "Arxiv23"]
        ])
        star = hm.cell[("GCN", "Uncertainty", 3)]

        # Phóng to ô tại chỗ sẽ che ô bên cạnh. Thay bằng viền nhấn + số đọc lại
        # ở lề phải, chỗ đang trống vì heatmap đã dịch sang trái.
        star_ring = SurroundingRectangle(star, color=C_GOOD, stroke_width=3.5,
                                         buff=0.03, corner_radius=0.03)
        readout = VGroup(
            mono("Pubmed · GCN Enh. · k = 10%", size=14, color=MUTED),
            txt("0.20", size=42, color=C_GOOD, weight=BOLD),
        ).arrange(DOWN, buff=0.16)
        readout.move_to([4.3, star.get_center()[1], 0])
        lead = Line(star_ring.get_right(), readout.get_left(), buff=0.18,
                    stroke_color=C_GOOD, stroke_width=2)

        beat(self, "Hãy nhìn pắp mét và ác xíp hai ba trước.",
             Create(frames), Indicate(good, color=C_LLM, scale_factor=1.04), run_time=1.4)
        beat(self, "Ở đây độ bất định là quy tắc kinh nghiệm tốt nhất trong mọi thiết lập.")
        beat(self, "Với gờ xê en dùng đặc trưng tăng cường trên pắp mét, en xi ét đạt không phẩy hai mươi.",
             Create(star_ring), Create(lead), FadeIn(readout, shift=LEFT * 0.2), run_time=1.0)
        beat(self, "Nghĩa là cứ một trăm nót được định tuyến, eo eo em tạo hai mươi lần sửa có lợi.")
        beat(self, "Sau khi đã trừ đi những nót bị làm sai. Đây là kết quả tốt.")

        self.play(FadeOut(frames), FadeOut(star_ring), FadeOut(lead), FadeOut(readout),
                  run_time=0.6)

        f_cora = SurroundingRectangle(
            VGroup(*[hm.cell[(bb, s, c)] for bb in ["GCN", "GCNII"]
                     for s in STRATS for c in hm.cols("Cora")]),
            color=C_BAD, stroke_width=3, buff=0.05, corner_radius=0.04)
        c_unc = hm.cell[("GCN", "Uncertainty", 0)]
        c_rand = hm.cell[("GCN", "Random", 0)]
        callout_inner = VGroup(
            VGroup(mono("uncertainty", size=18, color=ACCENT),
                   mono("-0.09", size=26, color=C_BAD)).arrange(RIGHT, buff=0.35),
            VGroup(mono("random", size=18, color=MUTED),
                   mono("-0.02", size=26, color=MUTED)).arrange(RIGHT, buff=0.35),
        ).arrange(DOWN, buff=0.26, aligned_edge=LEFT)
        callout = VGroup(panel(callout_inner, buff=0.3), callout_inner)
        callout.to_edge(RIGHT, buff=0.4).shift(UP * 0.1)

        # Viền nhấn thay cho phóng to: callout bên phải đã hiện sẵn hai con số cỡ lớn.
        unc_ring = SurroundingRectangle(c_unc, color=C_BAD, stroke_width=3.5,
                                        buff=0.03, corner_radius=0.03)
        rand_ring = SurroundingRectangle(c_rand, color=MUTED, stroke_width=3,
                                         buff=0.03, corner_radius=0.03)

        beat(self, "Nhưng bây giờ nhìn sang cô ra.", Create(f_cora), run_time=0.9)
        beat(self, "Cùng quy tắc kinh nghiệm đó, cùng mô hình nền đó, en xi ét rơi xuống âm không phẩy không chín.",
             Create(unc_ring), run_time=0.9)
        beat(self, "Và đây mới là điều đáng chú ý nhất.",
             Create(rand_ring), FadeIn(callout), run_time=0.9)
        beat(self, "Định tuyến ngẫu nhiên trên cô ra chỉ là âm không phẩy không hai.")
        beat(self, "Chọn kỹ nót mà gi en en không chắc chắn còn hại hơn chọn ngẫu nhiên.",
             Circumscribe(callout, color=C_BAD, buff=0.1), run_time=1.5)

        self.clear_scene()
        punch = VGroup(
            txt("GNN uncertainty does not always", size=24, color=INK),
            txt("reflect LLM advantage.", size=24, color=C_BAD, weight=BOLD),
        ).arrange(DOWN, buff=0.24)
        beat(self, "Kết luận rất rõ: gi en en độ bất định không phải lúc nào cũng phản ánh eo eo em lợi thế.",
             Write(punch), run_time=1.7)


# ===========================================================================
class S2_09_PubmedVsCora(GlanceScene):
    """Đối chiếu trực tiếp Pubmed và Cora bằng bar_chart (gợi ý trong TASK.md)."""

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        head = heading("Uncertainty routing: Pubmed vs Cora",
                       color=ACCENT).to_edge(UP, buff=0.8)
        sub = mono("GCN · enhanced features · NCS at k = 10 / 15 / 20%", size=17,
                   color=MUTED).next_to(head, DOWN, buff=0.16)

        pub = T1["GCN"]["Uncertainty"][3:6]
        cora = T1["GCN"]["Uncertainty"][0:3]
        chart = bar_chart(
            pub + cora,
            ["10%", "15%", "20%", "10%", "15%", "20%"],
            colors=[C_GOOD] * 3 + [C_BAD] * 3,
            y_range=(-0.15, 0.25, 0.1),
            width=8.6, height=3.9,
        ).shift(DOWN * 0.55)
        # Cột Cora đều âm, next_to(..., UP) sẽ dán nhãn ngay trên trục 0 nhìn rất lệch.
        # Ghim cả hai nhãn lên cùng một độ cao, phía trên khung trục.
        pub_bars = VGroup(*[chart.bars[i] for i in range(3)])
        cora_bars = VGroup(*[chart.bars[i] for i in range(3, 6)])
        lab_y = chart.axes.get_top()[1] + 0.34
        lab_pub = txt("Pubmed", size=21, color=C_GOOD, weight=BOLD)
        lab_cora = txt("Cora", size=21, color=C_BAD, weight=BOLD)
        lab_pub.move_to([pub_bars.get_center()[0], lab_y, 0])
        lab_cora.move_to([cora_bars.get_center()[0], lab_y, 0])
        stamp = source(SRC_T1)

        beat(self, "Đặt hai bộ dữ liệu cạnh nhau thì kết luận bật ra ngay.",
             FadeIn(head), FadeIn(sub), FadeIn(chart.axes), FadeIn(stamp), run_time=1.0)
        beat(self, "Trên pắp mét, cùng một quy tắc kinh nghiệm cho en xi ét dương ở cả ba mức.",
             LaggedStart(*[GrowFromEdge(chart.bars[i], DOWN) for i in range(3)],
                         lag_ratio=0.15), FadeIn(lab_pub), run_time=1.5)
        beat(self, "Trên cô ra, cũng quy tắc kinh nghiệm đó, cả ba mức đều âm.",
             LaggedStart(*[GrowFromEdge(chart.bars[i], DOWN) for i in range(3, 6)],
                         lag_ratio=0.15), FadeIn(lab_cora), run_time=1.5)
        beat(self, "Không phải kém đi một chút, mà đổi hẳn dấu.")
        beat(self, "Cùng một luật chọn nót, hai bộ dữ liệu cho hai kết quả trái ngược.")

        self.clear_scene()
        punch = VGroup(
            txt("Same rule, opposite sign.", size=26, color=INK),
            txt("The heuristic is dataset-dependent.", size=26, color=ACCENT, weight=BOLD),
        ).arrange(DOWN, buff=0.26)
        beat(self, "Cùng một luật, ngược dấu. quy tắc kinh nghiệm này phụ thuộc bộ dữ liệu.",
             Write(punch), run_time=1.6)


# ===========================================================================
class S2_10_DegreeDensity(GlanceScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        head = heading("What about degree and density?", color=ACCENT).to_edge(UP, buff=0.8)
        hm = build_heatmap().scale(0.88).move_to(LEFT * 0.9 + DOWN * 0.7)
        stamp = source(SRC_T1)
        self.add(head, hm, stamp)

        unc = VGroup(*[hm.row[(bb, "Uncertainty")] for bb in ["GCN", "GCNII"]],
                     *[hm.row_lab[(bb, "Uncertainty")] for bb in ["GCN", "GCNII"]])
        cmp_rows = VGroup(*[hm.row[(bb, s)] for bb in ["GCN", "GCNII"]
                            for s in ["Random", "C-density", "Degree"]])

        beat(self, "Còn bậc và mật độ phân cụm thì sao?")
        beat(self, "Tạm bỏ hàng độ bất định sang một bên.",
             unc.animate.set_opacity(0.12), run_time=0.9)
        beat(self, "Chỉ so ba hàng còn lại với nhau.",
             Indicate(cmp_rows, color=MUTED, scale_factor=1.02), run_time=1.4)
        beat(self, "Trong phần lớn thiết lập, en xi ét của chúng chỉ xấp xỉ ngẫu nhiên định tuyến.")
        beat(self, "Có trường hợp còn thấp hơn cả ngẫu nhiên.")

        f = SurroundingRectangle(
            VGroup(*[hm.cell[("GCNII", "Degree", c)] for c in range(3)]),
            color=C_BAD, stroke_width=3, buff=0.05, corner_radius=0.04)
        tag_inner = txt("negative at all three budgets", size=19, color=C_BAD)
        tag = VGroup(panel(tag_inner, buff=0.22), tag_inner)
        tag.to_edge(RIGHT, buff=0.4).align_to(f, UP)

        beat(self, "Ví dụ, trên cô ra với mô hình nền gờ xê en hai.")
        beat(self, "Cách dựa trên bậc cho en xi ét âm ở cả ba mức định tuyến.",
             Create(f), FadeIn(tag), run_time=1.3)
        beat(self, "Trên pắp mét và ác xíp hai ba đôi khi có lợi ích dương.")
        beat(self, "Nhưng mức cải thiện rất nhỏ và không hề nhất quán.")

        self.clear_scene()
        punch = VGroup(
            txt("Simple structural properties can help sometimes,", size=24, color=INK),
            txt("but cannot pin down which nodes need the LLM.", size=24,
                color=ACCENT, weight=BOLD),
        ).arrange(DOWN, buff=0.26)
        beat(self, "Thuộc tính cấu trúc đơn giản có thể hữu ích đôi lúc.",
             Write(punch), run_time=1.6)
        beat(self, "Nhưng không đủ để xác định chắc chắn nót nào cần eo eo em.")


# ===========================================================================
class S2_11_Backbone(GlanceScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        head = heading("Change the backbone, routing changes too",
                       color=ACCENT).to_edge(UP, buff=0.8)
        sub = mono("Pubmed · uncertainty routing", size=17,
                   color=MUTED).next_to(head, DOWN, buff=0.16)

        gcn = T1["GCN"]["Uncertainty"][3:6]
        gcnii = T1["GCNII"]["Uncertainty"][3:6]
        chart = bar_chart(
            gcn + gcnii,
            ["10%", "15%", "20%", "10%", "15%", "20%"],
            colors=[C_GNN] * 3 + [C_ROUTER] * 3,
            y_range=(0, 0.25, 0.1),
            width=8.6, height=3.6,
        ).shift(DOWN * 0.5)
        l_gcn = txt("GCN", size=22, color=C_GNN, weight=BOLD)
        l_gcnii = txt("GCNII", size=22, color=C_ROUTER, weight=BOLD)
        l_gcn.next_to(VGroup(*[chart.bars[i] for i in range(3)]), UP, buff=0.75)
        l_gcnii.next_to(VGroup(*[chart.bars[i] for i in range(3, 6)]), UP, buff=0.75)
        stamp = source(SRC_T1)

        beat(self, "Còn một quan sát nữa, và nó khá tinh tế.",
             FadeIn(head), FadeIn(sub), FadeIn(chart.axes), FadeIn(stamp), run_time=1.0)
        beat(self, "Hiệu quả định tuyến thay đổi khi mô hình nền thay đổi.")
        beat(self, "Trên pắp mét, độ bất định với gờ xê en đạt en xi ét từ không phẩy mười bảy đến không phẩy hai mươi.",
             LaggedStart(*[GrowFromEdge(chart.bars[i], DOWN) for i in range(3)],
                         lag_ratio=0.15), FadeIn(l_gcn), run_time=1.5)
        beat(self, "Nhưng đổi sang mô hình nền mạnh hơn là gờ xê en hai.",
             LaggedStart(*[GrowFromEdge(chart.bars[i], DOWN) for i in range(3, 6)],
                         lag_ratio=0.15), FadeIn(l_gcnii), run_time=1.5)
        beat(self, "Cùng quy tắc kinh nghiệm đó chỉ còn khoảng 0.08 đến 0.09. Giảm hơn một nửa.")
        beat(self, "Lý do có thể hiểu thế này.")
        beat(self, "gờ xê en hai đã tự xử lý được một phần nót khó.")
        beat(self, "Nên phần còn lại cho eo eo em sửa cũng co hẹp theo.")
        beat(self, "Một nót khó với gờ xê en chưa chắc còn khó với gờ xê en hai.")

        self.clear_scene()
        punch = VGroup(
            txt("Routing heuristics depend not only on the DATASET,", size=23, color=INK),
            txt("but also on the BACKBONE in use.", size=23, color=ACCENT, weight=BOLD),
        ).arrange(DOWN, buff=0.26)
        beat(self, "định tuyến quy tắc kinh nghiệm không chỉ phụ thuộc bộ dữ liệu.", Write(punch), run_time=1.6)
        beat(self, "Mà còn phụ thuộc cả mô hình nền đang dùng.")


# ===========================================================================
class S2_12_Limits(GlanceScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        head = heading("Three limitations of existing heuristics",
                       color=ACCENT).to_edge(UP, buff=0.85)

        def limit(n, text, color):
            num = txt(n, size=20, color=BG, weight=BOLD)
            disc = Circle(radius=0.26, fill_color=color, fill_opacity=1,
                          stroke_width=0).move_to(num)
            label = txt(text, size=22, color=INK)
            return VGroup(VGroup(disc, num), label).arrange(RIGHT, buff=0.38)

        lims = VGroup(
            limit("1", "DATASET-dependent: what helps on Pubmed can hurt on Cora.", C_GNN),
            limit("2", "BACKBONE-dependent: a new GNN, a new set of hard nodes.", C_GNN),
            limit("3", "All of them are only proxies for GNN DIFFICULTY.", C_ROUTER),
        ).arrange(DOWN, buff=0.5, aligned_edge=LEFT).shift(DOWN * 0.3)

        beat(self, "Tổng hợp lại, bài báo chỉ ra ba hạn chế chính.", Write(head), run_time=1.3)
        beat(self, "Thứ nhất, chúng phụ thuộc bộ dữ liệu.",
             FadeIn(lims[0], shift=RIGHT * 0.25), run_time=0.8)
        beat(self, "Tín hiệu tốt trên pắp mét có thể gây hại trên cô ra.")
        beat(self, "Thứ hai, chúng phụ thuộc mô hình nền.",
             FadeIn(lims[1], shift=RIGHT * 0.25), run_time=0.8)
        beat(self, "Đổi gi en en thì tập nót khó cũng đổi theo.")
        beat(self, "Và thứ ba, quan trọng nhất.",
             FadeIn(lims[2], shift=RIGHT * 0.25), run_time=0.8)
        beat(self, "Cả ba đều chỉ là tín hiệu thay thế cho gi en en độ khó.",
             Circumscribe(lims[2], color=C_ROUTER, buff=0.18), run_time=1.4)

        adv = MathTex(r"\text{LLM advantage}", r"\;=\;",
                      r"\mathcal{L}_{\text{GNN}}", r"\;-\;",
                      r"\mathcal{L}_{\text{LLM}}", color=INK).scale(1.05)
        adv[0].set_color(C_ROUTER)
        adv[2].set_color(C_GNN)
        adv[4].set_color(C_LLM)
        note = txt("the loss saved by calling the LLM, versus the GNN alone",
                   size=20, color=MUTED)
        grp = VGroup(adv, note).arrange(DOWN, buff=0.4)

        self.play(FadeOut(lims), FadeOut(head), run_time=0.6)
        beat(self, "Trong khi đó, thứ bộ định tuyến thật sự cần ước lượng là eo eo em lợi thế.",
             Write(adv), run_time=1.8)
        beat(self, "Tức phần hàm mất mát tiết kiệm được khi dùng eo eo em so với chỉ dùng gi en en.",
             FadeIn(note), run_time=0.7)

        self.play(grp.animate.scale(0.75).to_edge(UP, buff=1.0), run_time=0.8)
        cost_inner = txt("The gain must be large enough to pay for that call.",
                         size=22, color=INK)
        cost = VGroup(panel(cost_inner, buff=0.3), cost_inner).shift(DOWN * 0.4)
        beat(self, "Và còn một yếu tố nữa: chi phí.", FadeIn(cost), run_time=0.8)
        beat(self, "nót đáng định tuyến không chỉ vì gi en en làm chưa tốt.")
        beat(self, "Mà vì eo eo em phải cải thiện đủ nhiều để bù lại giá của lời gọi đó.")

        self.clear_scene()
        punch = VGroup(
            txt("Existing heuristics: usable as a FEATURE or a PRIOR.", size=23, color=INK),
            txt("Not reliable enough to be a ROUTING POLICY on their own.", size=23,
                color=C_BAD, weight=BOLD),
        ).arrange(DOWN, buff=0.26)
        beat(self, "Kết luận của bài báo: quy tắc kinh nghiệm hiện có vẫn dùng được.",
             Write(punch), run_time=1.8)
        beat(self, "Nhưng chỉ ở vai trò đặc trưng hoặc tín hiệu ban đầu đưa vào bộ định tuyến.")
        beat(self, "Chúng không đủ tin cậy để tự làm một chính sách định tuyến.")


# ===========================================================================
class S2_13_Bridge(GlanceScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        line1 = txt("Hand-picked heuristics are unstable.", size=28, color=INK)
        line2 = txt("So which signal is the right one?", size=28, color=ACCENT, weight=BOLD)
        grp = VGroup(line1, line2).arrange(DOWN, buff=0.32)

        # Câu cầu nối chốt trong plan.md, đọc y nguyên.
        beat(self, "quy tắc kinh nghiệm thủ công không ổn định.", Write(line1), run_time=1.3)
        beat(self, "Vậy tín hiệu nào mới đúng?", Write(line2), run_time=1.3)
        self.wait(0.8)
        self.play(FadeOut(grp), run_time=0.8)
