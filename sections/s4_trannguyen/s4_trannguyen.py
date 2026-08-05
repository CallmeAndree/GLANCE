"""Section 4 — Kiến trúc GLANCE.  Owner: Trần Nguyên.

Nguồn trong paper: §5.1 + Hình 2 (tr.5–6), Phụ lục B (tr.14–16)
Nhiệm vụ chi tiết: sections/s4_trannguyen/TASK.md

Render:  manim -ql sections/s4_trannguyen/s4_trannguyen.py -a
"""

import pathlib
import sys

# Cho phép import glance_style.py ở thư mục gốc repo.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from glance_style import *  # noqa: E402,F403

SECTION = "4"
SECTION_NAME = "Kiến trúc GLANCE"
OWNER = "Trần Nguyên"
ACCENT = SECTION_COLORS.get(SECTION, C_HIGHLIGHT)

# --------------------------------------------------------------------------
# Style riêng của section này — giữ nguyên bảng màu đơn sắc của bản gốc.
# BG / INK cố tình đè hằng số cùng tên của glance_style (khai báo sau import).
# --------------------------------------------------------------------------
BG = "#08090B"
PANEL = "#111317"
PANEL_2 = "#191C21"
BRIGHT = "#F2F2F2"
LIGHT = "#A8A8A8"
MID = "#777777"
DIM = "#555555"
DARK = "#25272B"
INK = "#08090B"
# Giữ "Segoe UI" làm lựa chọn đầu; máy nào không có (macOS/Linux) thì rơi về
# font tiếng Việt của repo thay vì để Pango tự chọn bừa.
FONT = "Segoe UI" if "Segoe UI" in set(manimpango.list_fonts()) else FONT_MAIN

# Lời thuyết minh gom một chỗ theo quy ước repo. Nội dung lấy nguyên văn từ
# các add_subcaption trong bản gốc, không sửa chữ.
VO = {
    "k1": "GLANCE dự đoán nhãn cho mỗi node trong một Text-Attributed Graph.",
    "k2": "Từ đây, ta chỉ theo dõi Node A xuyên suốt pipeline.",
    "k3": "GNN, MLP Q và thông tin trực tiếp cung cấp ba góc nhìn bổ sung về A.",
    "k4": "Mỗi layer gom representation hàng xóm rồi cập nhật representation của A.",
    "k5": "GLANCE có thể dùng nhiều backbone khác nhau, "
          "miễn tạo được representation cho A.",
    "k6": "GNN cho embedding, prediction ban đầu và uncertainty; "
          "chưa có routing score.",
    "k7": "Cùng một MLP Q tạo phân phối mềm cho A và từng hàng xóm.",
    "k8": "Giá trị cao cho thấy A giống neighborhood; giá trị thấp gợi ý heterophily.",
    "k9": "x A vẫn được giữ trực tiếp; video dừng trước bước ghép routing feature.",
}


def t(text, size=28, color=BRIGHT, weight=NORMAL, line_spacing=-1):
    return Text(
        text,
        font=FONT,
        font_size=size,
        color=color,
        weight=weight,
        line_spacing=line_spacing,
    )


def mt(tex, size=32, color=BRIGHT):
    """Typeset mathematical notation with LaTeX rather than plain text."""
    return MathTex(tex, font_size=size, color=color)


def fit(mob, width):
    if mob.width > width:
        mob.scale_to_fit_width(width)
    return mob


def panel(width, height, stroke=LIGHT, fill=PANEL, radius=0.18):
    return RoundedRectangle(
        width=width,
        height=height,
        corner_radius=radius,
        stroke_color=stroke,
        stroke_width=1.6,
        fill_color=fill,
        fill_opacity=1,
    )


def node(label, target=False, radius=0.30):
    circle = Circle(
        radius=radius,
        fill_color=BRIGHT if target else DIM,
        fill_opacity=1,
        stroke_color=BRIGHT if target else LIGHT,
        stroke_width=2,
    )
    label_mob = t(label, 20, INK if target else BRIGHT, BOLD).move_to(circle)
    return VGroup(circle, label_mob)


def phase_header(number, title):
    number_mob = t(f"{number:02d}", 20, INK, BOLD)
    pill = RoundedRectangle(
        width=0.62,
        height=0.38,
        corner_radius=0.10,
        fill_color=BRIGHT,
        fill_opacity=1,
        stroke_width=0,
    )
    number_mob.move_to(pill)
    title_mob = fit(t(title, 34, BRIGHT, BOLD), 10.7)
    head = VGroup(VGroup(pill, number_mob), title_mob).arrange(RIGHT, buff=0.22)
    head.to_corner(UL, buff=0.32)
    rule = Line(LEFT * 6.7, RIGHT * 6.7, color=DARK, stroke_width=1.5)
    rule.to_edge(UP, buff=0.98)
    return VGroup(head, rule)


def caption(text_value):
    body = fit(t(text_value, 21, LIGHT, BOLD), 11.8)
    bg = RoundedRectangle(
        width=max(body.width + 0.45, 4.8),
        height=body.height + 0.25,
        corner_radius=0.10,
        fill_color=BG,
        fill_opacity=0.94,
        stroke_color=DIM,
        stroke_width=1,
    )
    body.move_to(bg)
    return VGroup(bg, body).to_edge(DOWN, buff=0.18)


def doc_icon(scale=1.0):
    page = RoundedRectangle(
        width=0.36,
        height=0.46,
        corner_radius=0.04,
        fill_color=PANEL_2,
        fill_opacity=1,
        stroke_color=LIGHT,
        stroke_width=1.2,
    )
    lines = VGroup(*[
        Line(LEFT * 0.11, RIGHT * 0.11, color=LIGHT, stroke_width=1)
        for _ in range(3)
    ]).arrange(DOWN, buff=0.06).move_to(page)
    return VGroup(page, lines).scale(scale)


def module(title, subtitle, width=4.5, height=1.05, emphasized=False):
    outer = panel(
        width,
        height,
        stroke=BRIGHT if emphasized else DIM,
        fill=PANEL_2 if emphasized else PANEL,
    )
    title_mob = fit(t(title, 24, BRIGHT if emphasized else LIGHT, BOLD), width - 0.35)
    subtitle_mob = fit(t(subtitle, 17, LIGHT if emphasized else MID), width - 0.35)
    content = VGroup(title_mob, subtitle_mob).arrange(DOWN, buff=0.08)
    content.move_to(outer)
    return VGroup(outer, content)


def feature_vector(label, n=7, cell_size=0.34, math_label=False):
    cells = VGroup(*[
        Square(
            side_length=cell_size,
            stroke_color=LIGHT,
            stroke_width=1.2,
            fill_color=BRIGHT if i % 3 == 0 else (MID if i % 3 == 1 else DIM),
            fill_opacity=0.92,
        )
        for i in range(n)
    ]).arrange(RIGHT, buff=0.035)
    label_mob = mt(label, 28, BRIGHT) if math_label else t(label, 22, BRIGHT, BOLD)
    return VGroup(label_mob, cells).arrange(RIGHT, buff=0.18)


def probability_vector(label, values, width=2.25, math_label=False):
    label_mob = mt(label, 25, BRIGHT) if math_label else t(label, 19, BRIGHT, BOLD)
    bars = VGroup()
    for value in values:
        track = RoundedRectangle(
            width=width,
            height=0.17,
            corner_radius=0.04,
            fill_color=DARK,
            fill_opacity=1,
            stroke_width=0,
        )
        fill_bar = RoundedRectangle(
            width=max(width * value, 0.05),
            height=0.17,
            corner_radius=0.04,
            fill_color=LIGHT,
            fill_opacity=1,
            stroke_width=0,
        ).align_to(track, LEFT)
        bars.add(VGroup(track, fill_bar))
    bars.arrange(DOWN, buff=0.07)
    return VGroup(label_mob, bars).arrange(RIGHT, buff=0.15)


def math_module(tex, subtitle, width=4.0, height=0.95, emphasized=False):
    outer = panel(
        width,
        height,
        stroke=BRIGHT if emphasized else DIM,
        fill=PANEL_2 if emphasized else PANEL,
    )
    title_mob = fit(mt(tex, 30, BRIGHT if emphasized else LIGHT), width - 0.35)
    subtitle_mob = fit(t(subtitle, 17, LIGHT if emphasized else MID), width - 0.35)
    content = VGroup(title_mob, subtitle_mob).arrange(DOWN, buff=0.08)
    content.move_to(outer)
    return VGroup(outer, content)


class S4_01_Architecture(GlanceScene):
    """Bản gốc: GLANCE9Keyframes(MovingCameraScene).

    Đổi base class sang GlanceScene để có nền, thuyết minh và phụ đề chung
    của repo; nội dung nine keyframes giữ nguyên.
    """

    section, section_name = SECTION, SECTION_NAME

    def clear_except(self, *keepers, run_time=0.45):
        keep_ids = {id(m) for m in keepers}
        removable = [m for m in list(self.mobjects) if id(m) not in keep_ids]
        if removable:
            self.play(*[FadeOut(m) for m in removable], run_time=run_time)

    def show_header(self, number, title):
        head = phase_header(number, title)
        self.play(FadeIn(head, shift=DOWN * 0.08), run_time=0.45)
        return head

    def construct(self):
        self.camera.background_color = BG

        # One and only one Node A object is reused through all nine keyframes.
        node_A = node("A", target=True, radius=0.32)

        # ------------------------------------------------------------------ 1
        self.next_section("Keyframe 1 — Problem overview")
        self.show_header(1, "Node classification on a Text-Attributed Graph")
        frame = panel(10.5, 4.55, stroke=LIGHT)
        frame.shift(DOWN * 0.20)
        input_tag = t("INPUT", 21, LIGHT, BOLD)
        graph_eq = mt(r"G=(V,E,T)", 46)
        definitions = VGroup(
            t("V   set of nodes", 23, LIGHT),
            t("E   set of edges", 23, LIGHT),
            t("T   raw texts of nodes", 23, LIGHT),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        node_info = VGroup(
            t("Each node v has", 20, MID, BOLD),
            t("raw text  tᵥ", 25, BRIGHT),
            t("node feature  xᵥ", 25, BRIGHT),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.13)
        divider = Line(UP * 1.0, DOWN * 1.0, color=DIM, stroke_width=1.5)
        output_tag = t("OUTPUT", 21, LIGHT, BOLD)
        output = VGroup(
            t("predicted label", 23, BRIGHT, BOLD),
            mt(r"\hat y_v=\underset{k\in\{1,\ldots,C\}}{\arg\max}\ p_{v,k}", 29),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.10)
        left = VGroup(input_tag, graph_eq, definitions).arrange(DOWN, aligned_edge=LEFT, buff=0.27)
        right = VGroup(node_info, output_tag, output).arrange(DOWN, aligned_edge=LEFT, buff=0.28)
        content = VGroup(left, divider, right).arrange(RIGHT, buff=0.65)
        content.move_to(frame)
        self.play(Create(frame), run_time=0.65)
        self.play(FadeIn(input_tag), Write(graph_eq), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(row, shift=RIGHT * 0.12) for row in definitions], lag_ratio=0.18), run_time=0.9)
        self.play(FadeIn(node_info, shift=UP * 0.10), Create(divider), run_time=0.7)
        self.play(FadeIn(output_tag), Write(output), run_time=0.7)
        node_A.move_to(DOWN * 2.30 + LEFT * 1.0)
        question = VGroup(t("→", 28, BRIGHT, BOLD), mt(r"\hat y_A=?", 35)).arrange(RIGHT, buff=0.16)
        question.next_to(node_A, RIGHT, buff=0.18)
        self.play(GrowFromCenter(node_A), Write(question), run_time=0.8)
        self.say(VO["k1"])
        self.wait(1.0)

        # ------------------------------------------------------------------ 2
        self.next_section("Keyframe 2 — Concrete TAG")
        self.clear_except(node_A)
        self.show_header(2, "Một citation graph cụ thể")
        self.play(node_A.animate.move_to(LEFT * 1.35 + DOWN * 0.10), run_time=0.7)
        positions = {
            "B": LEFT * 1.35 + UP * 1.65,
            "C": LEFT * 3.25 + DOWN * 0.05,
            "D": RIGHT * 0.55 + DOWN * 0.05,
            "E": LEFT * 1.10 + DOWN * 1.72,
        }
        neighbors = {label: node(label).move_to(node_A) for label in positions}
        self.add(*neighbors.values())
        self.play(*[neighbors[k].animate.move_to(pos) for k, pos in positions.items()], run_time=1.0)
        edges = VGroup(*[
            Line(node_A.get_center(), neighbors[k].get_center(), color=DIM, stroke_width=3)
            for k in positions
        ])
        self.play(Create(edges), run_time=0.8)
        self.bring_to_front(node_A)
        icons = VGroup()
        for label, mob in neighbors.items():
            icon = doc_icon(0.75).next_to(mob, UR, buff=0.03)
            icons.add(icon)
        icon_A = doc_icon(0.82).next_to(node_A, UR, buff=0.03)
        icons.add(icon_A)
        self.play(LaggedStart(*[FadeIn(icon, shift=UP * 0.08) for icon in icons], lag_ratio=0.12), run_time=0.9)
        pulse_ring = Circle(radius=0.47, color=BRIGHT, stroke_width=2).move_to(node_A)
        self.play(Create(pulse_ring), pulse_ring.animate.scale(1.35).set_opacity(0), run_time=0.75)
        self.remove(pulse_ring)
        self.play(*[mob.animate.set_opacity(0.58) for mob in neighbors.values()], run_time=0.5)
        legend = VGroup(
            t("Node = paper", 23, BRIGHT, BOLD),
            t("Edge = citation", 23, LIGHT),
            t("Text = title or abstract", 23, LIGHT),
            mt(r"N(A)=\{B,C,D,E\}", 29, LIGHT),
            mt(r"d_A=|N(A)|=4", 29, LIGHT),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.20).move_to(RIGHT * 3.65 + UP * 0.20)
        self.play(LaggedStart(*[FadeIn(row, shift=LEFT * 0.1) for row in legend], lag_ratio=0.12), run_time=1.0)
        cap = caption("Target: Predict the class of Node A")
        self.play(FadeIn(cap, shift=UP * 0.08), run_time=0.5)
        self.say(VO["k2"])
        self.wait(0.9)

        # ------------------------------------------------------------------ 3
        self.next_section("Keyframe 3 — Three information sources")
        self.clear_except(node_A)
        self.show_header(3, "Ba nguồn thông tin dùng cho Node A")
        self.play(node_A.animate.move_to(LEFT * 5.2 + DOWN * 0.15), run_time=0.65)
        trunk = Line(node_A.get_right(), LEFT * 3.95 + DOWN * 0.15, color=LIGHT, stroke_width=2.4)
        branch_x = -3.4
        targets_y = [1.25, -0.15, -1.55]
        branch_lines = VGroup()
        for y in targets_y:
            branch_lines.add(
                VMobject(color=LIGHT, stroke_width=2.2).set_points_as_corners([
                    [branch_x, -0.15, 0], [branch_x, y, 0], [-2.65, y, 0]
                ])
            )
        self.play(Create(trunk), LaggedStart(*[Create(line) for line in branch_lines], lag_ratio=0.16), run_time=0.9)
        blocks = VGroup(
            module("GNN backbone", "graph structure + node features", width=5.2, emphasized=True),
            module("MLP Q", "node feature xᵥ only", width=5.2),
            module("Direct node information", "x_A and d_A  ·  not a neural network", width=5.2),
        )
        for block, y in zip(blocks, targets_y):
            block.move_to(RIGHT * 0.25 + UP * y)
        self.play(FadeIn(blocks[0], shift=RIGHT * 0.2), run_time=0.6)
        self.play(FadeIn(blocks[1], shift=RIGHT * 0.2), run_time=0.6)
        self.play(FadeIn(blocks[2], shift=RIGHT * 0.2), run_time=0.6)
        equations = VGroup(
            mt(r"(G,X)\longrightarrow z_G(A),\ p_{H,A},\ u_A", 25, BRIGHT),
            mt(r"x_v\longrightarrow p_{Q,v}", 25, LIGHT),
            mt(r"x_A,\quad d_A", 25, LIGHT),
        )
        for eq, block in zip(equations, blocks):
            eq.next_to(block, RIGHT, buff=0.25)
        self.play(LaggedStart(*[Write(eq) for eq in equations], lag_ratio=0.18), run_time=1.0)
        self.say(VO["k3"])
        self.wait(0.8)

        # ------------------------------------------------------------------ 4
        self.next_section("Keyframe 4 — Message passing")
        self.clear_except(node_A)
        self.show_header(4, "Bên trong GNN: aggregate rồi update")
        self.play(node_A.animate.move_to(LEFT * 4.2 + DOWN * 0.10), run_time=0.65)
        gnn_frame = panel(12.2, 5.45, stroke=LIGHT, fill=BG)
        gnn_frame.shift(DOWN * 0.18)
        frame_label = t("GNN", 18, LIGHT, BOLD).move_to(gnn_frame.get_corner(UL) + RIGHT * 0.38 + DOWN * 0.28)
        self.play(Create(gnn_frame), FadeIn(frame_label), run_time=0.65)
        self.bring_to_front(node_A)
        mp_positions = [LEFT * 5.35 + UP * 1.25, LEFT * 5.55 + DOWN * 1.15, LEFT * 2.95 + UP * 1.55, LEFT * 2.80 + DOWN * 1.40]
        mp_neighbors = VGroup(*[node(lbl, radius=0.24).move_to(pos) for lbl, pos in zip("BCDE", mp_positions)])
        mp_edges = VGroup(*[Line(m.get_center(), node_A.get_center(), color=DIM, stroke_width=2.5) for m in mp_neighbors])
        self.play(FadeIn(mp_neighbors), Create(mp_edges), run_time=0.8)
        self.bring_to_front(node_A)
        init_eq = mt(r"h_A^{(0)}=x_A", 38).move_to(RIGHT * 3.1 + UP * 1.65)
        self.play(Write(init_eq), run_time=0.65)
        messages = VGroup()
        paths = []
        for edge, n in zip(mp_edges, mp_neighbors):
            dot = Dot(n.get_center(), radius=0.07, color=BRIGHT)
            messages.add(dot)
            paths.append(Line(n.get_center(), node_A.get_center()))
        self.add(messages)
        self.play(*[MoveAlongPath(dot, path) for dot, path in zip(messages, paths)], run_time=1.0, rate_func=linear)
        self.play(FadeOut(messages), run_time=0.2)
        aggregate = fit(
            mt(
                r"m_A^{(\ell)}=\operatorname{AGGREGATE}^{(\ell)}"
                r"\!\left(\left\{h_u^{(\ell-1)}\mid u\in N(A)\right\}\right)",
                31,
            ),
            6.0,
        ).move_to(RIGHT * 2.75 + UP * 0.30)
        self.play(Write(aggregate), run_time=1.0)
        update = fit(
            mt(
                r"h_A^{(\ell)}=\operatorname{UPDATE}^{(\ell)}"
                r"\!\left(h_A^{(\ell-1)},m_A^{(\ell)}\right)",
                33,
            ),
            5.8,
        ).move_to(RIGHT * 2.75 + DOWN * 0.75)
        self.play(TransformFromCopy(aggregate, update), run_time=0.9)
        layer_counter = t("layer  1  →  2  →  …  →  L", 22, LIGHT, BOLD).move_to(RIGHT * 3.25 + DOWN * 1.72)
        final_embed = mt(r"z_G(A)=h_A^{(L)}", 38).next_to(layer_counter, DOWN, buff=0.22)
        self.play(Write(layer_counter), run_time=0.65)
        self.play(Write(final_embed), run_time=0.7)
        self.say(VO["k4"])
        self.wait(0.8)

        # ------------------------------------------------------------------ 5
        self.next_section("Keyframe 5 — Visual GNN backbone")
        self.clear_except(node_A)
        self.show_header(5, "Cấu trúc trực quan của GNN backbone")
        self.play(node_A.animate.move_to(LEFT * 5.55 + DOWN * 1.75).scale(0.78), run_time=0.6)
        input_block = module("Inputs", "node features X  ·  graph edges E", width=1.85, height=1.08, emphasized=True)
        layers = VGroup(*[
            module(f"MP layer {label}", "aggregate  ·  update", width=1.85, height=1.08, emphasized=(i == 0))
            for i, label in enumerate(["1", "2", "L"])
        ])
        z_vector = feature_vector(r"z_G(A)", n=6, cell_size=0.27, math_label=True)
        chain = VGroup(input_block, *layers, z_vector).arrange(RIGHT, buff=0.36)
        chain.scale_to_fit_width(12.15).move_to(UP * 0.35)
        arrows = VGroup(*[
            Arrow(chain[i].get_right(), chain[i + 1].get_left(), buff=0.10, color=LIGHT, stroke_width=2.5, max_tip_length_to_length_ratio=0.18)
            for i in range(len(chain) - 1)
        ])
        self.play(FadeIn(input_block), run_time=0.45)
        for arrow, layer in zip(arrows[:3], layers):
            self.play(GrowArrow(arrow), FadeIn(layer, shift=RIGHT * 0.12), run_time=0.48)
            self.play(layer[0].animate.set_stroke(BRIGHT).set_fill(PANEL_2), run_time=0.25)
        self.play(GrowArrow(arrows[-1]), FadeIn(z_vector, shift=RIGHT * 0.12), run_time=0.6)
        backbone_note = t("Backbone can be replaced", 20, LIGHT).move_to(UP * 2.05)
        backbone_name = t("GCN", 30, BRIGHT, BOLD).next_to(backbone_note, DOWN, buff=0.15)
        self.play(FadeIn(backbone_note), Write(backbone_name), run_time=0.55)
        for name in ["GraphSAGE", "GCNII", "GNN backbone"]:
            replacement = t(name, 30, BRIGHT, BOLD).move_to(backbone_name)
            self.play(Transform(backbone_name, replacement), run_time=0.48)
        self.say(VO["k5"])
        self.wait(0.8)

        # Restore Node A scale before the next keyframe.
        self.play(node_A.animate.scale(1 / 0.78), run_time=0.2)

        # ------------------------------------------------------------------ 6
        self.next_section("Keyframe 6 — GNN signals")
        self.clear_except(node_A)
        self.show_header(6, "GNN cung cấp ba tín hiệu về Node A")
        self.play(node_A.animate.move_to(LEFT * 5.45 + DOWN * 2.1), run_time=0.45)
        gnn = module("GNN", "backbone", width=2.5, height=1.35, emphasized=True).move_to(LEFT * 4.65 + UP * 0.15)
        self.play(FadeIn(gnn, shift=RIGHT * 0.12), run_time=0.5)
        branch_titles = VGroup(
            t("Node embedding", 22, LIGHT, BOLD),
            t("Initial prediction", 22, LIGHT, BOLD),
            t("GNN uncertainty", 22, LIGHT, BOLD),
        )
        branch_titles[0].move_to(LEFT * 0.6 + UP * 1.75)
        branch_titles[1].move_to(LEFT * 0.6 + DOWN * 0.05)
        branch_titles[2].move_to(LEFT * 0.6 + DOWN * 1.80)
        branch_arrows = VGroup(*[
            Arrow(gnn.get_right(), title.get_left(), buff=0.18, color=LIGHT, stroke_width=2.3)
            for title in branch_titles
        ])
        embedding = feature_vector(r"z_G(A)", n=9, cell_size=0.30, math_label=True).move_to(RIGHT * 3.75 + UP * 1.75)
        prediction = probability_vector(r"p_{H,A}", [0.45, 0.40, 0.15], width=2.5, math_label=True).move_to(RIGHT * 3.55 + DOWN * 0.05)
        uncertainty = math_module(r"u_A", "variation across dropout passes", width=3.25, height=0.95, emphasized=True).move_to(RIGHT * 3.55 + DOWN * 1.80)
        self.play(GrowArrow(branch_arrows[0]), FadeIn(branch_titles[0]), run_time=0.45)
        self.play(FadeIn(embedding, shift=RIGHT * 0.12), run_time=0.65)
        self.play(GrowArrow(branch_arrows[1]), FadeIn(branch_titles[1]), run_time=0.45)
        self.play(FadeIn(prediction, shift=RIGHT * 0.12), run_time=0.65)
        self.play(GrowArrow(branch_arrows[2]), FadeIn(branch_titles[2]), run_time=0.45)
        passes = VGroup(*[
            probability_vector(f"pass {i + 1}", values, width=1.25).scale(0.72)
            for i, values in enumerate([[0.45, 0.40, 0.15], [0.38, 0.47, 0.15], [0.49, 0.36, 0.15]])
        ]).arrange(RIGHT, buff=0.18).move_to(RIGHT * 3.35 + DOWN * 1.75)
        self.play(LaggedStart(*[FadeIn(p, shift=UP * 0.08) for p in passes], lag_ratio=0.18), run_time=0.9)
        self.play(ReplacementTransform(passes, uncertainty), run_time=0.75)
        formula = fit(mt(r"p_{H,A}=\operatorname{softmax}\!\left(H(z_G(A))\right)", 30, LIGHT), 5.5)
        formula.move_to(RIGHT * 3.25 + DOWN * 2.65)
        self.play(Write(formula), run_time=0.55)
        self.say(VO["k6"])
        self.wait(0.8)

        # ------------------------------------------------------------------ 7
        self.next_section("Keyframe 7 — MLP Q")
        self.clear_except(node_A)
        self.show_header(7, "Bên trong MLP Q: chỉ dùng node feature")
        self.play(node_A.animate.move_to(LEFT * 5.55 + DOWN * 2.05), run_time=0.45)
        mlp_frame = panel(7.0, 4.7, stroke=LIGHT, fill=BG).move_to(LEFT * 0.75 + DOWN * 0.15)
        mlp_label = t("MLP  Q", 26, BRIGHT, BOLD).move_to(mlp_frame.get_top() + DOWN * 0.38)
        self.play(Create(mlp_frame), FadeIn(mlp_label), run_time=0.55)
        layer_xs = [-2.8, -0.8, 1.2]
        neuron_counts = [4, 5, 3]
        neuron_layers = VGroup()
        for x, count in zip(layer_xs, neuron_counts):
            layer = VGroup(*[
                Circle(radius=0.12, stroke_color=LIGHT, stroke_width=1.5, fill_color=PANEL_2, fill_opacity=1)
                for _ in range(count)
            ]).arrange(DOWN, buff=0.28).move_to(RIGHT * x + DOWN * 0.10)
            neuron_layers.add(layer)
        connections = VGroup()
        for left_layer, right_layer in zip(neuron_layers[:-1], neuron_layers[1:]):
            for left_n in left_layer:
                for right_n in right_layer:
                    connections.add(Line(left_n.get_center(), right_n.get_center(), color=DIM, stroke_width=0.8))
        self.play(Create(connections), LaggedStart(*[FadeIn(layer) for layer in neuron_layers], lag_ratio=0.18), run_time=0.9)
        input_label = mt(r"x_A", 34).next_to(mlp_frame, LEFT, buff=0.30)
        input_arrow = Arrow(input_label.get_right(), neuron_layers[0].get_left(), buff=0.10, color=BRIGHT, stroke_width=2.5)
        output_label = mt(r"p_{Q,A}", 34).next_to(mlp_frame, RIGHT, buff=0.30)
        output_arrow = Arrow(neuron_layers[-1].get_right(), output_label.get_left(), buff=0.10, color=BRIGHT, stroke_width=2.5)
        self.play(Write(input_label), GrowArrow(input_arrow), run_time=0.55)
        for layer in neuron_layers:
            self.play(*[n.animate.set_fill(BRIGHT) for n in layer], run_time=0.28)
        self.play(GrowArrow(output_arrow), Write(output_label), run_time=0.55)
        outputs = VGroup()
        for idx, label in enumerate("ABCDE"):
            out = probability_vector(
                rf"p_{{Q,{label}}}",
                [0.20 + idx * 0.08, 0.55 - idx * 0.05, 0.25 - idx * 0.03],
                width=1.25,
                math_label=True,
            ).scale(0.78)
            outputs.add(out)
        outputs.arrange(DOWN, aligned_edge=LEFT, buff=0.18).move_to(RIGHT * 5.1 + DOWN * 0.20)
        self.play(ReplacementTransform(output_label.copy(), outputs[0]), run_time=0.45)
        for idx in range(1, 5):
            new_input = mt(rf"x_{{{'BCDE'[idx - 1]}}}", 31, LIGHT).move_to(input_label)
            self.play(Transform(input_label, new_input), FadeIn(outputs[idx], shift=RIGHT * 0.1), run_time=0.40)
        no_graph = t("No graph structure · No message passing", 20, LIGHT, BOLD).move_to(DOWN * 2.72 + LEFT * 0.7)
        formula_q = mt(r"p_{Q,v}=Q(x_v)", 32).next_to(no_graph, UP, buff=0.16)
        self.play(Write(formula_q), FadeIn(no_graph), run_time=0.65)
        self.say(VO["k7"])
        self.wait(0.8)

        # ------------------------------------------------------------------ 8
        self.next_section("Keyframe 8 — Estimated local homophily")
        self.clear_except(node_A)
        self.show_header(8, "Tính estimated local homophily")
        self.play(node_A.animate.move_to(RIGHT * 4.45 + UP * 0.35), run_time=0.55)
        q_box = module("MLP Q", "node feature only", width=2.55, height=1.15, emphasized=True).move_to(LEFT * 5.0 + UP * 0.35)
        self.play(FadeIn(q_box), run_time=0.45)
        h_positions = [RIGHT * 4.45 + UP * 1.75, RIGHT * 2.95 + UP * 0.35, RIGHT * 5.95 + UP * 0.35, RIGHT * 4.45 + DOWN * 1.10]
        h_neighbors = VGroup(*[node(lbl, radius=0.23).move_to(pos) for lbl, pos in zip("BCDE", h_positions)])
        h_edges = VGroup(*[Line(node_A.get_center(), n.get_center(), color=DIM, stroke_width=2.0) for n in h_neighbors])
        self.play(FadeIn(h_neighbors), Create(h_edges), run_time=0.6)
        self.bring_to_front(node_A)
        neighbor_vectors = VGroup(*[
            probability_vector(rf"p_{{Q,{lbl}}}", vals, width=1.05, math_label=True).scale(0.66)
            for lbl, vals in zip("BCDE", [[0.20, 0.55, 0.25], [0.25, 0.50, 0.25], [0.30, 0.47, 0.23], [0.35, 0.40, 0.25]])
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to(LEFT * 2.2 + UP * 0.45)
        arrows_to_sum = VGroup(*[
            Arrow(q_box.get_right(), vec.get_left(), buff=0.10, color=DIM, stroke_width=1.6)
            for vec in neighbor_vectors
        ])
        self.play(LaggedStart(*[FadeIn(vec, shift=RIGHT * 0.08) for vec in neighbor_vectors], lag_ratio=0.12), run_time=0.75)
        sigma = mt(r"\sum_{u\in N(A)}p_{Q,u}", 32).move_to(LEFT * 0.05 + UP * 0.45)
        self.play(*[vec.animate.scale(0.75).move_to(sigma) for vec in neighbor_vectors], run_time=0.75)
        self.play(ReplacementTransform(neighbor_vectors, sigma), run_time=0.55)
        mean = mt(r"\bar p_{Q,N(A)}", 36).move_to(RIGHT * 1.35 + UP * 0.45)
        self.play(TransformMatchingShapes(sigma, mean), run_time=0.65)
        p_a = probability_vector(r"p_{Q,A}", [0.56, 0.28, 0.16], width=1.65, math_label=True).move_to(LEFT * 1.0 + DOWN * 1.35)
        mean_vec = probability_vector(r"\bar p_{Q,N(A)}", [0.28, 0.48, 0.24], width=1.65, math_label=True).move_to(RIGHT * 2.25 + DOWN * 1.35)
        self.play(ReplacementTransform(mean.copy(), mean_vec), FadeIn(p_a), run_time=0.7)
        dot = t("·", 42, BRIGHT, BOLD).move_to((p_a.get_right() + mean_vec.get_left()) / 2)
        result = mt(r"\hat h_A", 46).move_to(RIGHT * 5.55 + DOWN * 1.35)
        equals = mt(r"=", 38, LIGHT).next_to(result, LEFT, buff=0.28)
        self.play(Write(dot), run_time=0.35)
        self.play(Write(equals), TransformFromCopy(VGroup(p_a, mean_vec), result), run_time=0.75)
        formula_h = mt(
            r"\hat h_A=p_{Q,A}\cdot\left(\frac{1}{|N(A)|}"
            r"\sum_{u\in N(A)}p_{Q,u}\right)\qquad \hat h_A\in[0,1]",
            31,
        ).move_to(DOWN * 2.47)
        prior = caption("Estimated homophily is a routing prior")
        self.play(Write(formula_h), run_time=0.65)
        self.play(FadeIn(prior, shift=UP * 0.08), run_time=0.45)
        self.say(VO["k8"])
        self.wait(0.8)

        # ------------------------------------------------------------------ 9
        self.next_section("Keyframe 9 — Original node feature")
        self.clear_except(node_A)
        self.show_header(9, "Original node feature x_A được dùng để làm gì?")
        self.play(node_A.animate.move_to(LEFT * 5.65 + DOWN * 2.25), run_time=0.45)
        feature_frame = panel(12.1, 5.25, stroke=LIGHT, fill=BG).shift(DOWN * 0.18)
        label = t("NODE FEATURE", 18, LIGHT, BOLD).move_to(feature_frame.get_corner(UL) + RIGHT * 0.75 + DOWN * 0.28)
        self.play(Create(feature_frame), FadeIn(label), run_time=0.6)
        self.bring_to_front(node_A)
        raw_tag = t("Raw text  t_A", 21, LIGHT, BOLD).move_to(LEFT * 3.85 + UP * 1.55)
        title = fit(t("“Improving Graph Neural Networks\nunder Heterophily”", 28, BRIGHT, BOLD), 4.55)
        title.next_to(raw_tag, DOWN, buff=0.20)
        self.play(FadeIn(raw_tag), Write(title), run_time=0.9)
        keyword_1 = SurroundingRectangle(title, color=BRIGHT, buff=0.08, stroke_width=1.5)
        keyword_2 = t("semantic information", 18, LIGHT, BOLD).next_to(keyword_1, DOWN, buff=0.12)
        self.play(Create(keyword_1), FadeIn(keyword_2), run_time=0.55)
        x_vector = feature_vector(r"x_A", n=10, cell_size=0.34, math_label=True).move_to(LEFT * 0.25 + UP * 0.35)
        arrow_text = Arrow(title.get_right(), x_vector.get_left(), buff=0.25, color=LIGHT, stroke_width=2.5)
        self.play(GrowArrow(arrow_text), TransformFromCopy(title, x_vector), run_time=0.85)
        self.play(FadeOut(keyword_1), FadeOut(keyword_2), run_time=0.35)
        roles = VGroup(
            math_module(r"h_A^{(0)}=x_A", "initial representation in GNN", width=4.0, height=0.95, emphasized=True),
            math_module(r"p_{Q,A}=Q(x_A)", "independent input to MLP Q", width=4.0, height=0.95),
            math_module(r"x_A\ \text{ kept directly}", "direct routing information later", width=4.0, height=0.95),
        ).arrange(DOWN, buff=0.28).move_to(RIGHT * 4.05 + DOWN * 0.05)
        role_arrows = VGroup(*[
            Arrow(x_vector.get_right(), role.get_left(), buff=0.12, color=LIGHT if i == 0 else DIM, stroke_width=2.1)
            for i, role in enumerate(roles)
        ])
        for arrow, role in zip(role_arrows, roles):
            self.play(GrowArrow(arrow), FadeIn(role, shift=RIGHT * 0.10), run_time=0.55)
        semantic_note = t(
            "Giữ semantic trực tiếp của Node A,\nkể cả khi graph signals chưa phản ánh đầy đủ.",
            19,
            LIGHT,
            BOLD,
        )
        semantic_note.move_to(LEFT * 3.15 + DOWN * 1.52)
        self.play(FadeIn(semantic_note, shift=UP * 0.08), run_time=0.55)
        signals = VGroup(*[
            math_module(name, subtitle, width=2.25, height=0.76, emphasized=(name == r"x_A"))
            for name, subtitle in [
                (r"z_G(A)", "embedding"),
                (r"u_A", "uncertainty"),
                (r"\hat h_A", "homophily"),
                (r"x_A", "original feature"),
            ]
        ]).arrange(RIGHT, buff=0.24).move_to(DOWN * 2.42 + RIGHT * 0.55)
        self.play(LaggedStart(*[FadeIn(sig, shift=UP * 0.10) for sig in signals], lag_ratio=0.14), run_time=0.9)
        stop = caption("Dừng tại đây · chưa ghép f_A · chưa routing · chưa Top-K · chưa LLM")
        self.play(FadeIn(stop, shift=UP * 0.08), run_time=0.5)
        self.say(VO["k9"])
        self.wait(2.0)
