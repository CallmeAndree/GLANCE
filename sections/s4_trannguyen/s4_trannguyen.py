"""GLANCE architecture: router, LLM-on-demand context, and the refiner.

Nguồn: paper §5.1 và Hình 2 (tr.5-6); chi tiết prompt ở Phụ lục B.3 (tr.15-16).
Dựng lại đúng 3 bước trong Hình 2: routing features -> LLM đọc neighborhood
được route -> refiner hợp nhất embedding. 27 beat (bỏ 3 bản nháp prompt cũ,
đã gộp vào S4_19) nối tiếp nhau, mỗi beat là một Scene riêng để build.sh render
và ghép theo thứ tự khai báo.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from glance_style import *

import numpy as np

SECTION, SECTION_NAME, OWNER = "4", "GLANCE architecture", "Trần Nguyên"
ACCENT = SECTION_COLORS.get(SECTION, C_HIGHLIGHT)

CLASS_NAMES = ["Machine Learning", "Graph Mining", "Data Management"]


# mt() dùng chung từ glance_style, mặc định y như bản cục bộ trước đây
# (size=32, color=INK) nên 65 chỗ gọi bên dưới không đổi hành vi.


# Not a class: build.sh discovers renderable scenes by grepping `^class` in
# this file, so any shared behaviour used by S4_* below must be a plain
# function, not an intermediate base class (which build.sh would also try to
# render as its own clip).

def _show_header(self, number, title):
    head = step_header(number, title)
    self.play(FadeIn(head, shift=DOWN * 0.08), run_time=0.42)
    return head


def _clear_except(self, *keepers, run_time=0.45):
    keep_ids = {id(mob) for mob in keepers}
    removable = [mob for mob in list(self.mobjects) if id(mob) not in keep_ids]
    if removable:
        self.play(*[FadeOut(mob) for mob in removable], run_time=run_time)


def _banner(self):
    """Section banner. `step_header` (used as `_show_header` below) already
    starts clear of the top-left corner, so the default UL banner placement
    from GlanceScene.banner() needs no adjustment here."""
    return GlanceMovingScene.banner(self)


# --------------------------------------------------------------------------
# Private layout helpers, used only by S4_02's full-pipeline overview.
# --------------------------------------------------------------------------

INPUT_X = -6.15
STEP1_BOX = (5.20, 2.70, np.array([-2.80, 1.55, 0.0]))
STEP2_BOX = (5.20, 2.60, np.array([3.00, 1.60, 0.0]))
STEP3_BOX = (11.20, 2.25, np.array([0.10, -1.875, 0.0]))
CORRIDOR_Y = -0.32
TEXT_LINE_Y = -0.60


def _dashed_box(width, height, color=C_EDGE, stroke_width=1.7):
    """Dashed grouping frame, matching the paper figure's step containers."""
    return DashedVMobject(
        RoundedRectangle(
            width=width, height=height, corner_radius=0.16,
            stroke_color=color, stroke_width=stroke_width, fill_opacity=0,
        ),
        num_dashes=64, dashed_ratio=0.55,
    )


def _fit_into(mob, width, height):
    """Shrink content until it clears the padding of its dashed container."""
    factor = min(width / mob.width, height / mob.height, 1.0)
    if factor < 1.0:
        mob.scale(factor)
    return mob


def _corner_arrow(points, color=MUTED, stroke_width=1.8, tip="right"):
    """Orthogonal connector with an explicit tip direction."""
    path = VMobject(color=color, stroke_width=stroke_width)
    path.set_points_as_corners([np.array(p, dtype=float) for p in points])
    angles = {"right": -PI / 2, "left": PI / 2, "up": 0.0, "down": PI}
    head = Triangle(fill_color=color, fill_opacity=1, stroke_width=0)
    head.scale(0.052).rotate(angles[tip]).move_to(points[-1])
    return VGroup(path, head)


def _feature_row(text_value):
    marker = Square(side_length=0.09, fill_color=MUTED, fill_opacity=1, stroke_width=0)
    return VGroup(marker, txt(text_value, 14, MUTED)).arrange(RIGHT, buff=0.12)


def _mini_strip(color, n=4, cell=0.17):
    return VGroup(*[
        Square(
            side_length=cell, stroke_color=MUTED, stroke_width=0.9,
            fill_color=color, fill_opacity=0.95 if index % 2 == 0 else 0.65,
        )
        for index in range(n)
    ]).arrange(RIGHT, buff=0.025)


def _mini_module(name):
    box = RoundedRectangle(
        width=1.0, height=0.40, corner_radius=0.07,
        stroke_color=MUTED, stroke_width=1.6, fill_color=BG, fill_opacity=1,
    )
    label = fit_width(txt(name, 14, INK, BOLD), box.width - 0.14)
    label.move_to(box)
    return VGroup(box, label)


def _emb_below(label_tex, colors, cells_per_segment, cell_size=0.17):
    """Embedding strip with its name below the cells instead of beside them."""
    cells = VGroup()
    for color in colors:
        for index in range(cells_per_segment):
            cells.add(Square(
                side_length=cell_size, stroke_color=MUTED, stroke_width=1.0,
                fill_color=color, fill_opacity=0.95 if index % 2 == 0 else 0.65,
            ))
    cells.arrange(RIGHT, buff=0.025)
    label = mt(label_tex, 21)
    return VGroup(cells, label).arrange(DOWN, buff=0.12)


_LLM_STAGE_CONFIGS = {
    0: dict(
        number=23, title="Shared LLM encoder: ego embedding",
        equation=r"z_{L,0}(A)=L(P_0(A))", prompt=r"P_0(A)", subtitle="ego prompt",
        prompt_width=3.00, color=C_LLM_LIGHT, output=r"z_{L,0}(A)",
        panel_title="Prompt v0",
        lines=[
            "EGO ONLY",
            "Title: Improving graph neural networks under heterophily",
            "Question: what is the paper category?",
        ],
        legend="LIGHT AMBER · EGO CONTEXT EMBEDDING",
        panel_width=5.75, panel_height=2.55,
    ),
    1: dict(
        number=24, title="Shared LLM encoder: 1-hop embedding",
        equation=r"z_{L,1}(A)=L(P_1(A))", prompt=r"P_1(A)", subtitle="ego + direct neighbors",
        prompt_width=3.35, color=C_LLM, output=r"z_{L,1}(A)",
        panel_title="Prompt v1",
        lines=[
            "EGO + 1-HOP",
            "Title: Improving graph neural networks under heterophily",
            "Direct citations: graph LLMs; heterophily-aware GNNs",
        ],
        legend="BASE AMBER · 1-HOP CONTEXT EMBEDDING",
        panel_width=5.55, panel_height=2.65,
    ),
}


def _llm_stage(self, level):
    """Instantly-buildable ego/1-hop LLM-embedding stage: the starting point
    for S4_24 and S4_25, each of which continues the previous scene's visual
    (same fixed layout, only the prompt level and colour change)."""
    cfg = _LLM_STAGE_CONFIGS[level]
    header = step_header(cfg["number"], cfg["title"])
    equation = mt(cfg["equation"], 40, cfg["color"]).move_to(UP * 2.25)
    prompt = equation_card(
        cfg["prompt"], cfg["subtitle"], width=cfg["prompt_width"], height=0.95, emphasized=True,
    ).move_to(LEFT * 3.85 + UP * 1.15)
    llm = module_box(
        "Qwen3-Embed-8B", "shared embedding encoder", width=3.85, height=1.12, emphasized=True,
    ).move_to(LEFT * 3.85 + DOWN * 0.48)
    output = embedding_strip(
        cfg["output"], cfg["color"], n=9, cell_size=0.27, emphasized=True,
    ).move_to(LEFT * 3.85 + DOWN * 2.15)
    details = prompt_panel(
        cfg["panel_title"], cfg["lines"], width=cfg["panel_width"], height=cfg["panel_height"],
    ).move_to(RIGHT * 3.70 + DOWN * 0.36)
    prompt_arrow = small_arrow(prompt.get_bottom(), llm.get_top(), color=MUTED, buff=0.10)
    output_arrow = small_arrow(llm.get_bottom(), output.get_top(), color=cfg["color"], buff=0.10)
    legend = txt(cfg["legend"], 19, cfg["color"], BOLD).next_to(output, DOWN, buff=0.20)
    return header, equation, prompt, llm, output, details, prompt_arrow, output_arrow, legend


def _router_overview(self):
    """Instantly-buildable router-branch diagram: shared by S4_17, S4_18, S4_19."""
    self.camera.frame.save_state()
    router = router_glyph(radius=0.66).move_to(LEFT * 4.55)
    router_label = txt("ROUTER", 21, INK, BOLD).next_to(router, UP, buff=0.24)
    with_node = avatar_node("L", target=True, radius=0.38).move_to(RIGHT * 1.85 + UP * 1.55)
    without_node = avatar_node("G", radius=0.38).move_to(RIGHT * 1.85 + DOWN * 1.55)
    with_title = VGroup(
        txt("WITH LLM", 25, INK, BOLD), mt(r"v\in R", 27),
    ).arrange(DOWN, buff=0.12).next_to(with_node, RIGHT, buff=0.55)
    without_title = VGroup(
        txt("WITHOUT LLM", 25, MUTED, BOLD), mt(r"v\notin R", 27, MUTED),
    ).arrange(DOWN, buff=0.12).next_to(without_node, RIGHT, buff=0.55)
    branch_arrows = VGroup(
        small_arrow(router.get_right(), with_node.get_left(), stroke_width=2.3),
        small_arrow(router.get_right(), without_node.get_left(), color=C_EDGE, stroke_width=2.3),
    )
    overview = VGroup(
        router, router_label, with_node, without_node,
        with_title, without_title, branch_arrows,
    ).move_to(DOWN * 0.05)
    return router, router_label, with_node, without_node, with_title, without_title, branch_arrows, overview


def _merged_llm_embedding(self):
    """Instantly-buildable end state of S4_26: the merged Z_L(A) strip, the
    starting point for S4_27."""
    header26 = step_header(26, "Merge the three LLM embeddings")
    z0 = named_embedding_strip(r"z_{L,0}(A)", C_LLM_LIGHT, n=7, cell_size=0.25)
    z1 = named_embedding_strip(r"z_{L,1}(A)", C_LLM, n=7, cell_size=0.25)
    z2 = named_embedding_strip(r"z_{L,2}(A)", C_LLM_DEEP, n=7, cell_size=0.25)
    VGroup(z0, z1, z2).arrange(RIGHT, buff=0.90).move_to(UP * 0.25)
    z0_cells, z1_cells, z2_cells = z0[1], z1[1], z2[1]
    guides = VGroup(
        z0_cells.copy(), z1_cells.copy(), z2_cells.copy(),
    ).arrange(RIGHT, buff=0.055).scale(1.18).move_to(UP * 0.25)
    for part, guide in zip([z0_cells, z1_cells, z2_cells], guides):
        part.move_to(guide.get_center()).scale(1.18)
    z_l_row = VGroup(z0_cells, z1_cells, z2_cells)
    merged_label = mt(r"Z_L(A)", 39).next_to(z_l_row, UP, buff=0.28)
    z_l_visual = VGroup(merged_label, z_l_row)
    merge_equation = fit_width(
        mt(r"Z_L(A)=\left[z_{L,0}(A)\Vert z_{L,1}(A)\Vert z_{L,2}(A)\right]", 39), 11.3,
    ).move_to(DOWN * 1.65)
    return header26, z0_cells, z1_cells, z2_cells, merged_label, z_l_visual, merge_equation


class S4_01_TAG(GlanceMovingScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        _banner(self)
        _show_header(self, 1, "What is a text-attributed graph?")

        statement = txt("Citation structure and paper text in one graph", 28, INK, BOLD)
        graph_eq = mt(r"G=(V,E,T)", 62)
        node_def = VGroup(mt(r"V=\{A,B,C,D,E\}", 35), txt("nodes: scientific papers", 23, MUTED)).arrange(RIGHT, buff=0.45)
        edge_def = VGroup(mt(r"E=\{(B,A),(C,A),\ldots\}", 33), txt("edges: citations", 23, MUTED)).arrange(RIGHT, buff=0.45)
        text_def = VGroup(mt(r"T=\{t_A,t_B,\ldots\}", 34), txt("text: titles or abstracts", 23, MUTED)).arrange(RIGHT, buff=0.45)
        definitions = VGroup(node_def, edge_def, text_def).arrange(DOWN, buff=0.34)
        centered_layout = VGroup(statement, graph_eq, definitions).arrange(DOWN, buff=0.38)
        centered_layout.move_to(UP * 0.15)

        with self.voiceover(
            text="Đầu vào của bài toán là một Text-Attributed Graph, được ký hiệu là G bằng V, E, T."
        ) as tracker:
            self.play(FadeIn(statement), Write(graph_eq), run_time=max(0.85, tracker.duration))

        with self.voiceover(
            text="Trong ví dụ citation graph này, mỗi node đại diện cho một bài báo khoa học."
        ) as tracker:
            self.play(FadeIn(node_def, shift=UP * 0.08), run_time=max(0.5, tracker.duration))

        with self.voiceover(text="Các cạnh thể hiện quan hệ trích dẫn giữa các bài báo.") as tracker:
            self.play(FadeIn(edge_def, shift=UP * 0.08), run_time=max(0.5, tracker.duration))

        with self.voiceover(
            text="Ngoài cấu trúc graph, mỗi node còn có nội dung văn bản, chẳng hạn như tiêu đề hoặc abstract."
        ) as tracker:
            self.play(FadeIn(text_def, shift=UP * 0.08), run_time=max(0.5, tracker.duration))

        takeaway = takeaway_chip("Every paper has graph connections and a text attribute")
        with self.voiceover(
            text="Như vậy, mỗi node đồng thời có hai nguồn thông tin: nội dung của chính nó và mối quan hệ với các node khác."
        ) as tracker:
            self.play(FadeIn(takeaway, shift=UP * 0.08), run_time=max(0.45, tracker.duration))
        # Pinned above the takeaway chip, not a corner: the chip already spans
        # most of the frame's bottom edge, so any corner stamp would collide.
        self.add(source("§5.1 và Hình 2, tr.5-6").next_to(takeaway, UP, buff=0.16))
        self.wait(0.4)


class S4_02_EndToEnd(GlanceMovingScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        _clear_except(self)
        _banner(self)
        _show_header(self, 2, "From a complex graph to Node A's label")

        positions = [
            ORIGIN,
            LEFT * 5.2 + UP * 1.85, LEFT * 4.5 + UP * 0.45, LEFT * 5.0 + DOWN * 1.45,
            LEFT * 3.0 + UP * 2.10, LEFT * 2.8 + UP * 0.80, LEFT * 3.2 + DOWN * 0.75,
            LEFT * 2.3 + DOWN * 2.00, LEFT * 0.9 + UP * 1.75, LEFT * 0.8 + DOWN * 1.45,
            RIGHT * 1.2 + UP * 1.85, RIGHT * 1.5 + UP * 0.55, RIGHT * 1.2 + DOWN * 1.60,
            RIGHT * 3.2 + UP * 2.00, RIGHT * 3.1 + UP * 0.45, RIGHT * 3.4 + DOWN * 1.20,
            RIGHT * 5.1 + UP * 1.35, RIGHT * 4.8 + DOWN * 0.25, RIGHT * 5.25 + DOWN * 1.85,
        ]
        target_A = avatar_node("A", target=True, radius=0.34).move_to(positions[0])
        other_nodes = VGroup(*[
            Circle(radius=0.13, fill_color=C_EDGE, fill_opacity=1, stroke_color=MUTED, stroke_width=1.5).move_to(pos)
            for pos in positions[1:]
        ])
        all_centers = positions
        edge_pairs = [
            (0, 5), (0, 6), (0, 8), (0, 9), (0, 10), (0, 11), (0, 12), (0, 14),
            (1, 2), (1, 4), (2, 4), (2, 5), (2, 6), (2, 7), (3, 6), (3, 7),
            (4, 5), (4, 8), (5, 8), (5, 9), (6, 7), (6, 9), (8, 10), (8, 11),
            (9, 12), (10, 11), (10, 13), (11, 13), (11, 14), (11, 15), (12, 15),
            (13, 14), (13, 16), (14, 16), (14, 17), (15, 17), (15, 18), (16, 17), (17, 18),
        ]
        dense_edges = VGroup(*[
            Line(all_centers[i], all_centers[j], buff=0.17 if i and j else 0.27, color=C_EDGE, stroke_width=1.55)
            for i, j in edge_pairs
        ])
        graph_group = VGroup(dense_edges, other_nodes, target_A).move_to(DOWN * 0.05)
        graph_label = VGroup(
            txt("COMPLEX TEXT-ATTRIBUTED GRAPH", 22, MUTED, BOLD),
            txt("target: Node A", 23, INK, BOLD),
        ).arrange(DOWN, buff=0.15).next_to(graph_group, DOWN, buff=0.20)

        with self.voiceover(
            text="Từ một graph tương đối phức tạp, mục tiêu của GLANCE là dự đoán nhãn cho từng node."
        ) as tracker:
            self.play(
                Create(dense_edges),
                LaggedStart(*[GrowFromCenter(n) for n in other_nodes], lag_ratio=0.025),
                run_time=max(1.25, tracker.duration),
            )
        with self.voiceover(text="Ở đây, chúng ta tập trung vào Node A.") as tracker:
            self.play(GrowFromCenter(target_A), FadeIn(graph_label), run_time=max(0.55, tracker.duration))
        self.wait(0.3)

        glance = module_box("GLANCE", "graph + text evidence", width=2.65, height=1.25, emphasized=True).move_to(UP * 0.15)
        probability = probability_bars(r"p_A", [0.12, 0.73, 0.15], width=2.9, math_label=True)
        # Center GLANCE at true horizontal center and give both connecting
        # arrows the same length, so the whole assembly reads as symmetric.
        arrow_len = 1.35
        glance_half = glance[0].width / 2
        probe_graph_width = graph_group.copy().scale(0.38).width
        Xg = arrow_len + probe_graph_width / 2 + glance_half
        Xp = arrow_len + probability.width / 2 + glance_half
        probability.move_to(RIGHT * Xp + UP * 0.15)
        with self.voiceover(
            text="Sau khi đi qua toàn bộ hệ thống, GLANCE tạo ra một phân phối xác suất trên các lớp."
        ) as tracker:
            self.play(
                FadeOut(graph_label),
                graph_group.animate.scale(0.38).move_to(LEFT * Xg + UP * 0.15),
                run_time=max(0.85, tracker.duration),
            )
        graph_to_glance = small_arrow(graph_group.get_right(), glance.get_left(), color=MUTED, stroke_width=2.1, buff=0.14)
        glance_to_p = small_arrow(glance.get_right(), probability.get_left(), color=MUTED, stroke_width=2.1, buff=0.14)
        self.play(GrowArrow(graph_to_glance), FadeIn(glance), run_time=0.62)
        pulse = Dot(graph_to_glance.get_start(), radius=0.07, color=INK)
        self.add(pulse)
        self.play(MoveAlongPath(pulse, graph_to_glance), run_time=0.55, rate_func=linear)
        with self.voiceover(
            text="Ví dụ, xác suất của Node A lần lượt là 0.12, 0.73 và 0.15."
        ) as tracker:
            self.play(
                FadeOut(pulse), GrowArrow(glance_to_p), FadeIn(probability, shift=RIGHT * 0.10),
                run_time=max(0.7, tracker.duration),
            )
        self.wait(0.3)

        # ----------------------------------------------------------------
        # Middle beat: pull back slightly, then cut straight into the full
        # pipeline. The intro graph is never morphed mid-scene; the pipeline
        # gets its own fresh copy for the TAG input. This detour is bonus
        # visual content beyond the presentation script's Cảnh 2 text.
        # ----------------------------------------------------------------
        self.camera.frame.save_state()
        with self.voiceover(
            text="Bên trong GLANCE không phải là một hộp đen: hệ thống lần lượt định tuyến, đọc văn bản, rồi tinh chỉnh dự đoán."
        ) as tracker:
            self.play(
                self.camera.frame.animate.scale(1.08),
                FadeOut(graph_group), FadeOut(graph_to_glance), FadeOut(glance), FadeOut(glance_to_p), FadeOut(probability),
                run_time=max(0.75, tracker.duration),
            )
        self.camera.frame.restore()

        step_caption = takeaway_chip("Inside GLANCE: route, read, refine")
        self.play(FadeIn(step_caption, shift=UP * 0.08), run_time=0.42)

        tag_icon = graph_group.copy().scale_to_fit_width(1.10).move_to([INPUT_X, 1.95, 0.0])
        graph_caption = txt("TAG", 16, MUTED, BOLD).move_to([INPUT_X, 1.42, 0.0])
        raw_text = VGroup(*[doc_icon(0.75) for _ in range(3)]).arrange(RIGHT, buff=0.08)
        raw_text.move_to([INPUT_X, 0.62, 0.0])
        raw_text_caption = txt("NODE TEXT", 13, MUTED, BOLD).move_to([INPUT_X, 0.14, 0.0])
        self.play(
            FadeIn(tag_icon), FadeIn(graph_caption), FadeIn(raw_text, shift=UP * 0.06), FadeIn(raw_text_caption),
            run_time=0.50,
        )

        # --- Step 1: routing features, sourced from three modules ---------
        step1_w, step1_h, step1_c = STEP1_BOX
        step1_box = _dashed_box(step1_w, step1_h).move_to(step1_c)
        step1_title = txt("STEP 1 · ROUTING FEATURES", 16, MUTED, BOLD)

        gnn_rows = VGroup(*[
            _feature_row(name)
            for name in ["Node embedding", "Node uncertainty", "Homophily estimate"]
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        mlp_row = _feature_row("Node features")
        degree_row = _feature_row("Degree")
        feature_rows = VGroup(gnn_rows, mlp_row, degree_row).arrange(DOWN, aligned_edge=LEFT, buff=0.40)

        gnn_module = _mini_module("GNN").next_to(gnn_rows, LEFT, buff=0.50)
        mlp_module = _mini_module("MLP").next_to(mlp_row, LEFT, buff=0.50)
        graph_module = _mini_module("GRAPH").next_to(degree_row, LEFT, buff=0.50)
        mlp_module.align_to(gnn_module, LEFT)
        graph_module.align_to(gnn_module, LEFT)
        modules_col = VGroup(gnn_module, mlp_module, graph_module)

        module_arrows = VGroup(*[
            small_arrow(gnn_module.get_right(), row.get_left(), color=MUTED, stroke_width=1.3, buff=0.07)
            for row in gnn_rows
        ], small_arrow(mlp_module.get_right(), mlp_row.get_left(), color=MUTED, stroke_width=1.3, buff=0.07),
           small_arrow(graph_module.get_right(), degree_row.get_left(), color=MUTED, stroke_width=1.3, buff=0.07))

        router = router_glyph().scale(0.52)
        router_score = mt(r"a_v\in[0,1]", 19)
        router_column = VGroup(router, router_score).arrange(DOWN, buff=0.14)
        router_column.next_to(feature_rows, RIGHT, buff=0.55)
        router_column.set_y(feature_rows.get_center()[1])

        step1_visual = VGroup(modules_col, module_arrows, feature_rows, router_column)
        step1_content = VGroup(step1_title, step1_visual).arrange(DOWN, buff=0.20)
        _fit_into(step1_content, step1_w - 0.40, step1_h - 0.40).move_to(step1_c)

        merge_arrow = small_arrow(feature_rows.get_right(), router.get_left(), color=MUTED, stroke_width=1.7, buff=0.12)

        input_right_x = max(tag_icon.get_right()[0], raw_text.get_right()[0])
        input_mid_y = (tag_icon.get_center()[1] + raw_text_caption.get_center()[1]) / 2
        branch_x = input_right_x + 0.55
        tag_trunk_in = Line([input_right_x + 0.12, input_mid_y, 0.0], [branch_x, input_mid_y, 0.0], color=MUTED, stroke_width=1.9)
        tag_trunk = Line(
            [branch_x, gnn_module.get_center()[1], 0.0],
            [branch_x, graph_module.get_center()[1], 0.0],
            color=MUTED, stroke_width=1.9,
        )
        tag_branches = VGroup(*[
            small_arrow([branch_x, m.get_center()[1], 0.0], m.get_left(), color=MUTED, stroke_width=1.6, buff=0.08)
            for m in (gnn_module, mlp_module, graph_module)
        ])

        with self.voiceover(
            text="Bước một: GNN, MLP và cấu trúc graph cùng cung cấp đặc trưng cho bộ định tuyến, "
            "để tính ra một routing score."
        ) as tracker:
            self.play(Create(step1_box), FadeIn(step1_title), run_time=0.55)
            self.play(Create(tag_trunk_in), Create(tag_trunk), run_time=0.40)
            self.play(
                LaggedStart(*[GrowArrow(b) for b in tag_branches], lag_ratio=0.16),
                LaggedStart(*[FadeIn(m, scale=0.85) for m in modules_col], lag_ratio=0.16),
                run_time=0.65,
            )
            self.play(
                LaggedStart(*[GrowArrow(a) for a in module_arrows], lag_ratio=0.09),
                LaggedStart(*[FadeIn(row, shift=RIGHT * 0.06) for row in feature_rows], lag_ratio=0.09),
                run_time=0.85,
            )
            self.play(GrowArrow(merge_arrow), FadeIn(router, scale=0.85), run_time=0.50)
            self.play(Write(router_score), run_time=0.42)
        self.play(
            Transform(step_caption, takeaway_chip("Step 1 · GNN, MLP, and graph structure feed the router")),
            run_time=0.40,
        )

        # --- Step 2: LLM on routed neighborhoods -------------------------
        step2_w, step2_h, step2_c = STEP2_BOX
        step2_box = _dashed_box(step2_w, step2_h).move_to(step2_c)
        step2_title = txt("STEP 2 · LLM READS THE NEIGHBORHOOD", 16, MUTED, BOLD)
        prompts = VGroup(
            mt(r"P_0(A)", 20, C_LLM_LIGHT),
            mt(r"P_1(A)", 20, C_LLM),
            mt(r"P_2(A)", 20, C_LLM_DEEP),
        ).arrange(DOWN, buff=0.28)
        llm = module_box("Qwen3-Embed-8B", "frozen · shared", width=1.70, height=1.35, emphasized=True)
        strips = VGroup(
            _mini_strip(C_LLM_LIGHT),
            _mini_strip(C_LLM),
            _mini_strip(C_LLM_DEEP),
        ).arrange(DOWN, buff=0.28)
        step2_body = VGroup(prompts, llm, strips).arrange(RIGHT, buff=0.50)
        step2_equation = mt(r"Z_L(A)=[z_{L,0}\Vert z_{L,1}\Vert z_{L,2}]", 19)
        step2_content = VGroup(step2_title, step2_body, step2_equation).arrange(DOWN, buff=0.18)
        _fit_into(step2_content, step2_w - 0.40, step2_h - 0.40).move_to(step2_c)
        step2_inner_arrows = VGroup(
            small_arrow(prompts.get_right(), llm.get_left(), color=MUTED, stroke_width=1.7, buff=0.12),
            small_arrow(llm.get_right(), strips.get_left(), color=MUTED, stroke_width=1.7, buff=0.12),
        )

        route_arrow = small_arrow(
            router.get_right(),
            [step2_c[0] - step2_w / 2, router.get_center()[1], 0.0],
            color=INK,
            stroke_width=2.1,
            buff=0.06,
        )
        route_label = VGroup(txt("ROUTE", 14, INK, BOLD), mt(r"v\in R", 18)).arrange(RIGHT, buff=0.12)
        route_label.next_to(route_arrow, UP, buff=0.14)
        text_to_llm = _corner_arrow(
            [
                (raw_text.get_right()[0], raw_text.get_center()[1], 0.0),
                (input_right_x + 0.85, raw_text.get_center()[1], 0.0),
                (input_right_x + 0.85, TEXT_LINE_Y, 0.0),
                (2.10, TEXT_LINE_Y, 0.0),
                (2.10, step2_c[1] - step2_h / 2, 0.0),
            ],
            color=C_EDGE,
            stroke_width=1.5,
            tip="up",
        )

        with self.voiceover(
            text="Bước hai: node được định tuyến sẽ được gửi sang một LLM dùng chung, đọc ngữ cảnh "
            "ở ba mức ego, một-hop và hai-hop."
        ) as tracker:
            self.play(GrowArrow(route_arrow), FadeIn(route_label), run_time=0.50)
            self.play(Create(step2_box), FadeIn(step2_title), run_time=0.55)
            self.play(Create(text_to_llm), run_time=0.60)
            self.play(
                LaggedStart(*[FadeIn(prompt, shift=RIGHT * 0.06) for prompt in prompts], lag_ratio=0.14),
                run_time=0.62,
            )
            self.play(GrowArrow(step2_inner_arrows[0]), FadeIn(llm), run_time=0.50)
            self.play(
                GrowArrow(step2_inner_arrows[1]),
                LaggedStart(*[FadeIn(strip, shift=RIGHT * 0.06) for strip in strips], lag_ratio=0.14),
                run_time=0.60,
            )
            self.play(Write(step2_equation), run_time=0.48)
        self.play(
            Transform(step_caption, takeaway_chip("Step 2 · one shared LLM reads ego, 1-hop, and 2-hop text")),
            run_time=0.40,
        )

        # --- Step 3: refine the GNN prediction ----------------------------
        # Mirrors the paper figure's right-to-left reading: routed embeddings
        # on the right feed the refiner, whose output sits on the left.
        step3_w, step3_h, step3_c = STEP3_BOX
        step3_box = _dashed_box(step3_w, step3_h).move_to(step3_c)
        step3_title = txt("STEP 3 · REFINE THE GNN PREDICTION", 16, MUTED, BOLD)
        gnn_side = _emb_below(r"z_G(A)", [C_GNN], 4, cell_size=0.17)
        llm_side = _emb_below(r"Z_L(A)", [C_LLM_LIGHT, C_LLM, C_LLM_DEEP], 2, cell_size=0.17)
        fusion_inputs = VGroup(gnn_side, llm_side).arrange(RIGHT, buff=0.45)
        refiner = module_box("Refiner MLP", "late fusion", width=2.35, height=0.95, emphasized=True)
        refined = probability_bars(r"p_{C,A}", [0.12, 0.73, 0.15], width=1.35, math_label=True)
        step3_row = VGroup(refined, refiner, fusion_inputs).arrange(RIGHT, buff=0.85)
        step3_equation = mt(r"p_{C,A}=\operatorname{softmax}\!\left(C([z_G(A)\Vert Z_L(A)])\right)", 23)
        step3_content = VGroup(step3_title, step3_row, step3_equation).arrange(DOWN, buff=0.18)
        _fit_into(step3_content, step3_w - 0.40, step3_h - 0.40).move_to(step3_c)
        step3_inner_arrows = VGroup(
            small_arrow(fusion_inputs.get_left(), refiner.get_right(), color=MUTED, stroke_width=1.7, buff=0.14),
            small_arrow(refiner.get_left(), refined.get_right(), color=MUTED, stroke_width=1.7, buff=0.14),
        )

        skip_arrow = _corner_arrow(
            [
                tuple(router.get_bottom()),
                (router.get_center()[0], CORRIDOR_Y, 0.0),
                (gnn_side.get_center()[0], CORRIDOR_Y, 0.0),
                (gnn_side.get_center()[0], gnn_side.get_top()[1], 0.0),
            ],
            color=MUTED, stroke_width=2.0, tip="down",
        )
        skip_label = VGroup(
            txt("KEEP GNN", 12, MUTED, BOLD), mt(r"v\notin R", 16, MUTED),
        ).arrange(RIGHT, buff=0.10).move_to([router.get_center()[0], CORRIDOR_Y + 0.30, 0.0])

        llm_source = strips.get_bottom()
        llm_arrow = _corner_arrow(
            [
                tuple(llm_source),
                (llm_source[0], CORRIDOR_Y, 0.0),
                (llm_side.get_center()[0], CORRIDOR_Y, 0.0),
                (llm_side.get_center()[0], llm_side.get_top()[1], 0.0),
            ],
            color=MUTED, stroke_width=2.0, tip="down",
        )
        llm_label = txt("LLM EMBEDDINGS", 12, MUTED, BOLD).move_to([llm_source[0], CORRIDOR_Y + 0.30, 0.0])

        with self.voiceover(
            text="Bước ba: bộ Refiner kết hợp embedding của GNN với embedding của LLM để tạo ra "
            "một dự đoán đã được tinh chỉnh."
        ) as tracker:
            self.play(Create(step3_box), FadeIn(step3_title), run_time=0.55)
            self.play(
                Create(skip_arrow), FadeIn(skip_label),
                Create(llm_arrow), FadeIn(llm_label),
                run_time=0.55,
            )
            self.play(
                LaggedStart(FadeIn(gnn_side, shift=UP * 0.06), FadeIn(llm_side, shift=UP * 0.06), lag_ratio=0.25),
                run_time=0.62,
            )
            self.play(GrowArrow(step3_inner_arrows[0]), FadeIn(refiner), run_time=0.50)
            self.play(GrowArrow(step3_inner_arrows[1]), FadeIn(refined, shift=LEFT * 0.08), run_time=0.55)
            self.play(Write(step3_equation), run_time=0.55)
        self.play(
            Transform(step_caption, takeaway_chip("Step 3 · the refiner fuses GNN and LLM evidence")),
            run_time=0.40,
        )
        self.wait(0.5)

        # ----------------------------------------------------------------
        # Return to the simple page, then zoom into the output to continue.
        # ----------------------------------------------------------------
        pipeline_parts = [
            tag_icon, graph_caption, raw_text, raw_text_caption,
            tag_trunk_in, tag_trunk, tag_branches,
            step1_box, step1_content, merge_arrow,
            route_arrow, route_label, text_to_llm,
            step2_box, step2_content, step2_inner_arrows,
            step3_box, step3_content, step3_inner_arrows,
            skip_arrow, skip_label, llm_arrow, llm_label,
            step_caption,
        ]
        self.play(
            *[FadeOut(part) for part in pipeline_parts],
            FadeIn(graph_group), FadeIn(glance), FadeIn(graph_to_glance), FadeIn(glance_to_p), FadeIn(probability),
            run_time=0.95,
        )
        self.wait(0.3)

        self.camera.frame.save_state()
        self.play(
            self.camera.frame.animate.set(width=probability.width * 1.7).move_to(probability.get_center()),
            FadeOut(graph_group), FadeOut(graph_to_glance), FadeOut(glance),
            run_time=0.9,
        )

        p_equation = mt(r"p_A=[0.12,0.73,0.15]", 48).move_to(UP * 0.65)
        decision = mt(r"\hat y_A=\underset{k\in\{1,2,3\}}{\arg\max}\ p_{A,k}=2", 52).move_to(DOWN * 0.55)
        with self.voiceover(text="Hệ thống chọn lớp có xác suất lớn nhất bằng phép argmax.") as tracker:
            self.play(
                FadeOut(glance_to_p),
                self.camera.frame.animate.restore(),
                ReplacementTransform(probability, p_equation),
                run_time=0.85,
            )
            self.play(Write(decision), run_time=0.9)

        with self.voiceover(
            text="Do đó, trong ví dụ này, Node A được dự đoán thuộc lớp thứ hai."
        ) as tracker:
            prediction_note = takeaway_chip("Predicted label for Node A: class 2")
            self.play(FadeIn(prediction_note, shift=UP * 0.08), run_time=max(0.45, tracker.duration))
        self.wait(0.6)


class S4_03_ThreeSources(GlanceMovingScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        _clear_except(self)
        _banner(self)
        _show_header(self, 3, "Three information sources for Node A")

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
        trunk = Line([branch_x, cards[2].get_center()[1], 0], [branch_x, cards[0].get_center()[1], 0], color=MUTED, stroke_width=2.0)
        branches = VGroup(*[
            small_arrow([branch_x, card.get_center()[1], 0], card.get_left(), color=MUTED, stroke_width=2.0, buff=0.08)
            for card in cards
        ])

        with self.voiceover(text="Để đưa ra quyết định, GLANCE thu thập ba nhóm thông tin cho Node A.") as tracker:
            self.play(GrowFromCenter(node_A), run_time=max(0.4, tracker.duration * 0.4))
            self.play(FadeIn(node_label), Create(trunk_in), Create(trunk), run_time=max(0.65, tracker.duration * 0.6))

        narrations = [
            "Nhóm thứ nhất đến từ GNN, gồm embedding của node, dự đoán ban đầu và độ không chắc chắn.",
            "Nhóm thứ hai đến từ một MLP riêng, được gọi là Q, chỉ sử dụng feature của node để hỗ trợ ước lượng homophily.",
            "Nhóm cuối cùng là thông tin trực tiếp, gồm feature gốc và degree của node.",
        ]
        for branch, card, narration in zip(branches, cards, narrations):
            with self.voiceover(text=narration) as tracker:
                self.play(GrowArrow(branch), FadeIn(card, shift=RIGHT * 0.08), run_time=max(0.52, tracker.duration))

        with self.voiceover(
            text="Các nguồn thông tin này sẽ được kết hợp để Router quyết định có nên sử dụng LLM cho Node A hay không."
        ):
            pass
        self.wait(0.6)


class S4_04_InitialState(GlanceMovingScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        _clear_except(self)
        _banner(self)
        _show_header(self, 4, "The initial state as a substitution")

        equation = mt(r"h_A^{(0)}=x_A", 68).move_to(UP * 0.45)
        step_label = txt("DEFINITION", 22, MUTED, BOLD).next_to(equation, DOWN, buff=0.35)
        timeline_line = Line(LEFT * 1.25, RIGHT * 1.25, color=C_EDGE, stroke_width=2.0).move_to(DOWN * 1.15)
        dots = VGroup(*[
            Circle(radius=0.13, stroke_color=MUTED, stroke_width=1.7, fill_color=INK if i == 0 else BG, fill_opacity=1)
            for i in range(3)
        ]).arrange(RIGHT, buff=0.85).move_to(timeline_line)
        step_numbers = VGroup(*[txt(str(i), 17, BG if i == 1 else MUTED, BOLD).move_to(dot) for i, dot in enumerate(dots, start=1)])
        timeline = VGroup(timeline_line, dots, step_numbers)
        with self.voiceover(
            text="Đầu tiên, Node A được đưa vào GNN backbone. Ở layer số 0, hidden state của Node A "
            "chính là feature ban đầu của node. Nói cách khác, h A mũ 0 bằng x A."
        ) as tracker:
            self.play(
                Write(equation), FadeIn(step_label), Create(timeline_line), FadeIn(dots), FadeIn(step_numbers),
                run_time=max(0.85, tracker.duration),
            )

        feature_example = mt(r"x_A=[0.8,-0.1,0.5]", 62).move_to(equation)
        feature_label = txt("EXAMPLE FEATURE", 22, MUTED, BOLD).move_to(step_label)
        with self.voiceover(
            text="Ví dụ, nếu feature của Node A là vector 0.8, âm 0.1 và 0.5, thì hidden state ban đầu "
            "cũng nhận đúng vector này."
        ) as tracker:
            self.play(
                FadeOut(equation, shift=UP * 0.06),
                Transform(step_label, feature_label),
                dots[0].animate.set_fill(BG), dots[1].animate.set_fill(INK),
                step_numbers[0].animate.set_color(MUTED), step_numbers[1].animate.set_color(BG),
                run_time=max(0.45, tracker.duration * 0.5),
            )
            self.play(FadeIn(feature_example, shift=UP * 0.06), run_time=max(0.45, tracker.duration * 0.5))
        equation = feature_example

        substituted = mt(r"h_A^{(0)}=[0.8,-0.1,0.5]", 62).move_to(equation)
        result_label = txt("INITIAL HIDDEN STATE", 22, INK, BOLD).move_to(step_label)
        with self.voiceover(text="Ở bước này chưa có thông tin từ các node hàng xóm.") as tracker:
            self.play(
                FadeOut(equation, shift=UP * 0.06),
                Transform(step_label, result_label),
                dots[1].animate.set_fill(BG), dots[2].animate.set_fill(INK),
                step_numbers[1].animate.set_color(MUTED), step_numbers[2].animate.set_color(BG),
                run_time=max(0.48, tracker.duration * 0.5),
            )
            self.play(FadeIn(substituted, shift=UP * 0.06), run_time=max(0.47, tracker.duration * 0.5))
        equation = substituted
        note = takeaway_chip("At layer 0, the hidden state equals the original text feature")
        self.play(FadeIn(note, shift=UP * 0.08), run_time=0.42)
        self.wait(0.9)


class S4_05_Aggregate(GlanceMovingScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        _clear_except(self)
        _banner(self)
        _show_header(self, 5, "AGGREGATE: combine the neighbors")

        summary = fit_width(mt(
            r"m_A^{(\ell)}=\operatorname{AGGREGATE}^{(\ell)}"
            r"\!\left(\{h_u^{(\ell-1)}\mid u\in N(A)\}\right)",
            46,
        ), 11.8).move_to(UP * 0.20)
        with self.voiceover(text="Tiếp theo là bước Aggregate.") as tracker:
            self.play(Write(summary), run_time=max(1.0, tracker.duration))
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
        aggregate = module_box("AGGREGATE", "example: mean", width=2.65, height=1.12, emphasized=True).move_to(LEFT * 0.40 + UP * 0.30)
        message = equation_card(r"m_A^{(\ell)}=[0.5,0.5]", "neighbor message", 3.35, 1.12, True).move_to(RIGHT * 4.35 + UP * 0.30)
        in_arrows = VGroup(*[
            small_arrow(state.get_right(), aggregate.get_left(), color=C_EDGE, stroke_width=1.5, buff=0.09)
            for state in states
        ])
        out_arrow = small_arrow(aggregate.get_right(), message.get_left(), color=MUTED, stroke_width=2.1, buff=0.10)
        with self.voiceover(
            text="GNN thu thập hidden state của các node hàng xóm của A, ví dụ như B, C, D và E."
        ) as tracker:
            self.play(LaggedStart(*[FadeIn(state, shift=RIGHT * 0.08) for state in states], lag_ratio=0.10), run_time=max(0.75, tracker.duration))
        with self.voiceover(
            text="Sau đó, các vector này được tổng hợp thành một neighbor message. "
            "Trong animation, chúng ta sử dụng phép trung bình để minh họa."
        ) as tracker:
            self.play(*[GrowArrow(arrow) for arrow in in_arrows], FadeIn(aggregate), run_time=max(0.72, tracker.duration * 0.55))
            self.play(GrowArrow(out_arrow), FadeIn(message, shift=RIGHT * 0.08), run_time=max(0.58, tracker.duration * 0.45))

        detailed = fit_width(mt(
            r"m_A^{(\ell)}=\frac{[1,0]+[0,1]+[1,1]+[0,0]}{4}=[0.5,0.5]",
            38,
        ), 11.4).move_to(DOWN * 2.28)
        with self.voiceover(
            text="Bốn vector hàng xóm được cộng lại rồi chia cho bốn, tạo thành message mới là "
            "0.5, 0.5. Lưu ý rằng phép trung bình chỉ là một ví dụ; tùy GNN backbone, phép "
            "aggregate có thể được cài đặt theo cách khác."
        ) as tracker:
            self.play(TransformMatchingTex(summary, detailed), run_time=max(1.0, tracker.duration))
        self.wait(0.9)


class S4_06_Update(GlanceMovingScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        _clear_except(self)
        _banner(self)
        _show_header(self, 6, "UPDATE: combine old state and new message")

        old_state = equation_card(r"h_A^{(\ell-1)}=[0.2,0.8]", "state before update", 3.75, 1.10).move_to(LEFT * 4.55 + UP * 1.00)
        message = equation_card(r"m_A^{(\ell)}=[0.6,0.4]", "neighbor message", 3.75, 1.10).move_to(LEFT * 4.55 + DOWN * 0.95)
        update = module_box("UPDATE", "combine two inputs", width=2.75, height=1.15, emphasized=True).move_to(LEFT * 0.25)
        new_state = equation_card(r"h_A^{(\ell)}=[0.4,0.6]", "illustrative result", 3.65, 1.12, True).move_to(RIGHT * 4.25)
        arrows = VGroup(
            small_arrow(old_state.get_right(), update.get_left(), color=C_EDGE, buff=0.10),
            small_arrow(message.get_right(), update.get_left(), color=C_EDGE, buff=0.10),
            small_arrow(update.get_right(), new_state.get_left(), color=MUTED, stroke_width=2.2, buff=0.10),
        )
        with self.voiceover(
            text="Sau khi có neighbor message, GNN thực hiện bước Update. Bước này kết hợp trạng thái "
            "trước đó của Node A với thông tin vừa tổng hợp từ hàng xóm."
        ) as tracker:
            self.play(FadeIn(old_state), FadeIn(message), run_time=max(0.55, tracker.duration))
        with self.voiceover(
            text="Trong ví dụ minh họa, trạng thái cũ của A là 0.2, 0.8, còn neighbor message là 0.6, 0.4."
        ) as tracker:
            self.play(GrowArrow(arrows[0]), GrowArrow(arrows[1]), FadeIn(update), run_time=max(0.7, tracker.duration))
        with self.voiceover(text="Sau Update, ta thu được một biểu diễn mới là 0.4, 0.6.") as tracker:
            self.play(GrowArrow(arrows[2]), FadeIn(new_state, shift=RIGHT * 0.08), run_time=max(0.6, tracker.duration))

        update_eq = fit_width(mt(
            r"h_A^{(\ell)}=\operatorname{UPDATE}^{(\ell)}"
            r"\!\left(h_A^{(\ell-1)},m_A^{(\ell)}\right)",
            42,
        ), 10.8).move_to(DOWN * 2.05)
        caveat = txt("The numeric output illustrates the role of UPDATE; learned parameters determine the real value.", 19, MUTED)
        caveat.next_to(update_eq, DOWN, buff=0.20)
        with self.voiceover(
            text="Các con số này chỉ dùng để minh họa luồng xử lý. Trong mô hình thực tế, giá trị được "
            "quyết định bởi các tham số đã học."
        ) as tracker:
            self.play(Write(update_eq), run_time=max(0.85, tracker.duration * 0.65))
            self.play(FadeIn(caveat), run_time=max(0.45, tracker.duration * 0.35))
        self.wait(0.9)


class S4_07_BeforeAfter(GlanceMovingScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        _clear_except(self)
        _banner(self)
        _show_header(self, 7, "How Node A changes after UPDATE")

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
        with self.voiceover(
            text="Điểm cần lưu ý là Node A vẫn là cùng một bài báo. Thứ thay đổi không phải danh tính "
            "của node mà là biểu diễn của nó."
        ) as tracker:
            self.play(FadeIn(before, shift=RIGHT * 0.08), run_time=max(0.65, tracker.duration))
        with self.voiceover(text="Trước Update, vector chủ yếu chứa thông tin của chính Node A.") as tracker:
            self.play(GrowArrow(transition), FadeIn(update_label), Write(message_label), run_time=max(0.7, tracker.duration))
        with self.voiceover(text="Sau Update, vector đã tích hợp thêm bằng chứng từ neighborhood.") as tracker:
            self.play(TransformFromCopy(before_node, after_node), FadeIn(after[0]), Write(after[2]), FadeIn(after[3]), run_time=max(0.85, tracker.duration))
        identity = takeaway_chip("The paper is still Node A; only its learned representation changes")
        with self.voiceover(
            text="Quá trình Aggregate và Update có thể được lặp lại qua nhiều GNN layer để thu được "
            "biểu diễn cuối cùng."
        ) as tracker:
            self.play(FadeIn(identity, shift=UP * 0.08), run_time=max(0.45, tracker.duration))
        self.wait(0.9)


class S4_08_EmbeddingPrediction(GlanceMovingScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        _clear_except(self)
        _banner(self)
        _show_header(self, 8, "Two direct outputs: embedding and prediction")

        gnn = module_box("GNN", "backbone", width=2.5, height=1.35, emphasized=True).move_to(LEFT * 4.75)
        embedding_title = txt("NODE EMBEDDING", 21, MUTED, BOLD).move_to(LEFT * 0.5 + UP * 1.35)
        prediction_title = txt("INITIAL PREDICTION", 21, MUTED, BOLD).move_to(LEFT * 0.5 + DOWN * 1.10)
        emb = feature_strip(r"z_G(A)", n=10, cell_size=0.31, math_label=True).move_to(RIGHT * 3.55 + UP * 1.35)
        pred = probability_bars(r"p_{H,A}", [0.45, 0.40, 0.15], width=3.0, math_label=True).move_to(RIGHT * 3.45 + DOWN * 1.10)
        arr1 = small_arrow(gnn.get_right(), embedding_title.get_left(), color=MUTED, stroke_width=2.1, buff=0.18)
        arr2 = small_arrow(gnn.get_right(), prediction_title.get_left(), color=MUTED, stroke_width=2.1, buff=0.18)
        with self.voiceover(
            text="Sau các message-passing layer, GNN tạo ra hai đầu ra quan trọng."
        ) as tracker:
            self.play(FadeIn(gnn), run_time=max(0.3, tracker.duration))
        with self.voiceover(
            text="Đầu ra thứ nhất là node embedding z G của A. Embedding này tóm tắt cả feature của "
            "Node A và thông tin cấu trúc mà GNN đã học được."
        ) as tracker:
            self.play(GrowArrow(arr1), FadeIn(embedding_title), run_time=max(0.6, tracker.duration * 0.45))
            self.play(FadeIn(emb, shift=RIGHT * 0.10), run_time=max(0.65, tracker.duration * 0.55))
        with self.voiceover(
            text="Đầu ra thứ hai là dự đoán ban đầu p H phẩy A."
        ) as tracker:
            self.play(GrowArrow(arr2), FadeIn(prediction_title), run_time=max(0.55, tracker.duration * 0.45))
            self.play(FadeIn(pred, shift=RIGHT * 0.10), run_time=max(0.65, tracker.duration * 0.55))
        formula = mt(r"p_{H,A}=\operatorname{softmax}\!\left(H(z_G(A))\right)", 38).move_to(DOWN * 2.45 + RIGHT * 2.60)
        with self.voiceover(
            text="Prediction head nhận embedding, đi qua MLP và softmax để tạo xác suất trên các lớp. "
            "Đây cũng là dự đoán cuối cùng nếu Node A không được gửi sang LLM."
        ) as tracker:
            self.play(Write(formula), run_time=max(0.8, tracker.duration))
        self.wait(0.8)


class S4_09_Uncertainty(GlanceMovingScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        _clear_except(self)
        _banner(self)
        _show_header(self, 9, "GNN uncertainty from multiple dropout passes")

        gnn = module_box("GNN + dropout", "same Node A", width=2.8, height=1.25, emphasized=True).move_to(LEFT * 4.60)
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
        with self.voiceover(
            text="GLANCE không chỉ quan tâm GNN dự đoán lớp nào mà còn quan tâm dự đoán đó có ổn định "
            "hay không."
        ) as tracker:
            self.play(FadeIn(gnn), run_time=max(0.45, tracker.duration))
        with self.voiceover(
            text="Hệ thống thực hiện nhiều forward pass với dropout cho cùng một node. Nếu các lần chạy "
            "tạo ra phân phối gần giống nhau, GNN tương đối chắc chắn."
        ) as tracker:
            self.play(
                LaggedStart(*[AnimationGroup(GrowArrow(a), FadeIn(p)) for a, p in zip(pass_arrows, passes)], lag_ratio=0.16),
                run_time=max(1.0, tracker.duration),
            )
        uncertainty = math_module_box(r"u_A", "variation across passes", width=3.0, height=1.10, emphasized=True).move_to(RIGHT * 4.65)
        with self.voiceover(
            text="Ngược lại, nếu kết quả thay đổi nhiều giữa các lần chạy, uncertainty của node sẽ cao."
        ) as tracker:
            self.play(ReplacementTransform(VGroup(passes, pass_arrows), uncertainty), run_time=max(0.8, tracker.duration))
        note = txt("Larger variation means higher uncertainty", 25, MUTED, BOLD).move_to(DOWN * 2.10)
        caveat = txt("The source does not define a unique closed-form equation for u_A", 19, MUTED).next_to(note, DOWN, buff=0.16)
        with self.voiceover(
            text="Uncertainty là một tín hiệu cho thấy Node A có thể là trường hợp khó, nhưng nó không "
            "được sử dụng riêng lẻ để quyết định routing."
        ) as tracker:
            self.play(FadeIn(note), FadeIn(caveat), run_time=max(0.65, tracker.duration))
        self.wait(0.8)


class S4_10_MLPQ(GlanceMovingScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        _clear_except(self)
        _banner(self)
        _show_header(self, 10, "MLP Q uses node features only")

        mlp_frame = RoundedRectangle(
            width=6.4, height=3.85, corner_radius=0.18,
            stroke_color=MUTED, stroke_width=1.6, fill_color=BG, fill_opacity=1,
        ).move_to(LEFT * 0.90 + UP * 0.25)
        mlp_label = txt("MLP Q", 26, INK, BOLD).move_to(mlp_frame.get_top() + DOWN * 0.38)
        with self.voiceover(
            text="Song song với GNN, GLANCE sử dụng một MLP được ký hiệu là Q."
        ) as tracker:
            self.play(Create(mlp_frame), FadeIn(mlp_label), run_time=max(0.5, tracker.duration))
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
                    connections.add(Line(left_n.get_center(), right_n.get_center(), buff=0.12, color=C_EDGE, stroke_width=0.75))
        with self.voiceover(
            text="Khác với GNN, MLP này chỉ nhận node feature x v, không sử dụng cạnh và không thực "
            "hiện message passing."
        ) as tracker:
            self.play(Create(connections), FadeIn(neuron_layers), run_time=max(0.8, tracker.duration))

        input_y = neuron_layers[0].get_center()[1]
        output_y = neuron_layers[-1].get_center()[1]
        input_label = mt(r"x_A", 36).move_to([mlp_frame.get_left()[0] - 0.75, input_y, 0])
        output_label = mt(r"p_{Q,A}", 36).move_to([mlp_frame.get_right()[0] + 0.90, output_y, 0])
        input_arrow = small_arrow(
            [input_label.get_right()[0], input_y, 0],
            [neuron_layers[0].get_left()[0], input_y, 0],
            color=MUTED,
            stroke_width=2.1,
            buff=0.08,
        )
        output_arrow = small_arrow(
            [neuron_layers[-1].get_right()[0], output_y, 0],
            [output_label.get_left()[0], output_y, 0],
            color=MUTED,
            stroke_width=2.1,
            buff=0.08,
        )
        with self.voiceover(text="Với mỗi node, Q tạo ra một phân phối xác suất mềm p Q phẩy v.") as tracker:
            self.play(Write(input_label), GrowArrow(input_arrow), run_time=max(0.5, tracker.duration * 0.34))
            self.play(*[n.animate.set_fill(INK) for layer in neuron_layers for n in layer], run_time=max(0.55, tracker.duration * 0.33))
            self.play(GrowArrow(output_arrow), Write(output_label), run_time=max(0.5, tracker.duration * 0.33))

        outputs = VGroup(*[
            probability_bars(rf"p_{{Q,{label}}}", vals, width=1.20, math_label=True).scale(0.76)
            for label, vals in zip("ABCDE", [
                [0.20, 0.55, 0.25], [0.28, 0.50, 0.22], [0.36, 0.45, 0.19],
                [0.44, 0.40, 0.16], [0.52, 0.35, 0.13],
            ])
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.16).move_to(RIGHT * 5.25 + DOWN * 0.15)
        with self.voiceover(
            text="Cùng một MLP được áp dụng cho Node A và các node hàng xóm B, C, D, E."
        ) as tracker:
            self.play(ReplacementTransform(output_label.copy(), outputs[0]), run_time=max(0.42, tracker.duration * 0.2))
            for idx, label in enumerate("BCDE", start=1):
                new_input = mt(rf"x_{{{label}}}", 31, MUTED).move_to(input_label)
                self.play(Transform(input_label, new_input), FadeIn(outputs[idx], shift=RIGHT * 0.08), run_time=max(0.35, tracker.duration * 0.2))
        formula_q = mt(r"p_{Q,v}=Q(x_v)", 38).move_to(DOWN * 2.02 + LEFT * 0.85)
        note_q = txt("No graph structure - No message passing", 20, MUTED, BOLD).next_to(formula_q, DOWN, buff=0.14)
        with self.voiceover(
            text="Mục đích của các phân phối này không phải để thay thế dự đoán của GNN, mà để hỗ trợ "
            "ước lượng mức độ tương đồng giữa node và neighborhood."
        ) as tracker:
            self.play(Write(formula_q), FadeIn(note_q), run_time=max(0.7, tracker.duration))
        self.wait(0.8)


class S4_11_NeighborAverage(GlanceMovingScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        _clear_except(self)
        _banner(self)
        _show_header(self, 11, "Average one prediction from each neighbor")

        node_A = avatar_node("A", target=True, radius=0.32).move_to(UP * 0.55)
        positions = {
            "B": UP * 1.75,
            "C": LEFT * 1.75 + UP * 0.55,
            "D": RIGHT * 1.75 + UP * 0.55,
            "E": DOWN * 0.65,
        }
        neighbors = {label: avatar_node(label, radius=0.22).move_to(pos) for label, pos in positions.items()}
        edges = VGroup(*[
            Line(node_A.get_center(), neighbors[label].get_center(), buff=0.28, color=C_EDGE, stroke_width=1.8)
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
        with self.voiceover(
            text="Để đánh giá neighborhood của A, GLANCE lấy một phân phối từ mỗi node hàng xóm."
        ) as tracker:
            self.play(Create(edges), FadeIn(node_A), FadeIn(VGroup(*neighbors.values())), run_time=max(0.7, tracker.duration * 0.35))
            self.bring_to_front(node_A, *neighbors.values())
            predictions = VGroup()
            for label in "BCDE":
                prediction = mt(prediction_data[label], 27, MUTED).move_to(prediction_positions[label])
                predictions.add(prediction)
                self.play(FadeIn(prediction, shift=0.08 * (prediction.get_center() - neighbors[label].get_center())), run_time=max(0.42, tracker.duration * 0.16))
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
        with self.voiceover(text="Các phân phối của B, C, D và E được cộng lại thành S A.") as tracker:
            self.play(FadeOut(graph_group), FadeOut(predictions), run_time=max(0.72, tracker.duration * 0.5))
            self.play(Write(sum_symbol), Write(current_sum_rhs), run_time=max(0.70, tracker.duration * 0.5))

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
        with self.voiceover(text="Sau đó, tổng này được chia cho số lượng hàng xóm.") as tracker:
            self.play(FadeOut(current_sum_rhs), run_time=max(0.24, tracker.duration * 0.15))
            self.play(FadeIn(expansion_rhs, shift=UP * 0.04), run_time=max(0.52, tracker.duration * 0.35))
            current_sum_rhs = expansion_rhs
            self.wait(0.20)

            sum_value = MathTex(
                r"S_A", r"=", r"[1.10,1.92,0.98]",
                font_size=55, color=INK,
            )
            value_rhs = VGroup(sum_value[1], sum_value[2])
            value_symbol_guide = sum_symbol.copy()
            value_layout = VGroup(value_symbol_guide, value_rhs).arrange(RIGHT, buff=0.16).move_to(UP * 0.35)
            symbol_value_target = value_symbol_guide.get_center().copy()
            self.play(FadeOut(current_sum_rhs), run_time=max(0.24, tracker.duration * 0.15))
            self.play(
                sum_symbol.animate.move_to(symbol_value_target),
                FadeIn(value_rhs),
                run_time=max(0.55, tracker.duration * 0.35),
            )

        mean_prefix = MathTex(
            r"\bar p_{Q,N(A)}", r"=", r"\frac{1}{|N(A)|}",
            font_size=49, color=INK,
        )
        with self.voiceover(
            text="Trong ví dụ, Node A có bốn hàng xóm nên hệ thống chia cho bốn và thu được phân phối "
            "trung bình 0.275, 0.480, 0.245."
        ) as tracker:
            self.play(
                FadeOut(value_rhs),
                sum_symbol.animate.move_to(ORIGIN),
                run_time=max(0.48, tracker.duration * 0.15),
            )
            mean_prefix.next_to(sum_symbol, LEFT, buff=0.14)
            mean_prefix_target = mean_prefix.get_center().copy()
            mean_prefix.move_to(mean_prefix_target + DOWN * 0.85).set_opacity(0)
            self.add(mean_prefix)
            self.play(
                mean_prefix.animate.move_to(mean_prefix_target).set_opacity(1),
                run_time=max(0.72, tracker.duration * 0.25),
                rate_func=smooth,
            )

            substitution = MathTex(
                r"=", r"\frac{1}{4}", r"[1.10,1.92,0.98]",
                font_size=43, color=MUTED,
            ).next_to(sum_symbol, RIGHT, buff=0.14)
            self.play(FadeIn(substitution, shift=RIGHT * 0.12), run_time=max(0.58, tracker.duration * 0.25))
            self.wait(0.2)

            final_average = MathTex(
                r"\bar p_{Q,N(A)}", r"=", r"[0.275,0.480,0.245]",
                font_size=55, color=INK,
            ).move_to(ORIGIN)
            self.play(
                FadeOut(VGroup(mean_prefix, sum_symbol, substitution), shift=UP * 0.04),
                FadeIn(final_average, shift=UP * 0.04),
                run_time=max(0.65, tracker.duration * 0.35),
            )
        result_note = takeaway_chip("Final average neighborhood distribution")
        with self.voiceover(
            text="Vector này đại diện cho xu hướng lớp chung trong neighborhood của Node A."
        ) as tracker:
            self.play(FadeIn(result_note, shift=UP * 0.08), run_time=max(0.42, tracker.duration))
        self.wait(0.9)


class S4_12_HomophilyDot(GlanceMovingScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        _clear_except(self)
        _banner(self)
        _show_header(self, 12, "Compare Node A with its neighborhood")

        p_a = probability_bars(r"p_{Q,A}", [0.56, 0.28, 0.16], width=2.45, math_label=True)
        p_mean = probability_bars(r"\bar p_{Q,N(A)}", [0.28, 0.48, 0.24], width=2.45, math_label=True)
        p_a.move_to(LEFT * 3.20 + UP * 0.75)
        p_mean.move_to(RIGHT * 2.20 + UP * 0.75)
        dot = mt(r"\cdot", 52).move_to((p_a.get_right() + p_mean.get_left()) / 2)
        with self.voiceover(
            text="Tiếp theo, GLANCE so sánh phân phối của chính Node A với phân phối trung bình của các "
            "hàng xóm."
        ) as tracker:
            self.play(FadeIn(p_a, shift=UP * 0.08), FadeIn(p_mean, shift=UP * 0.08), run_time=max(0.65, tracker.duration * 0.65))
            self.play(Write(dot), run_time=max(0.35, tracker.duration * 0.35))

        formula_h = mt(
            r"\hat h_A=p_{Q,A}\cdot\bar p_{Q,N(A)}"
            r"=p_{Q,A}\cdot\left(\frac{1}{|N(A)|}\sum_{u\in N(A)}p_{Q,u}\right)",
            38,
        ).move_to(DOWN * 0.85)
        with self.voiceover(text="Phép so sánh được thực hiện bằng tích vô hướng.") as tracker:
            self.play(Write(formula_h), run_time=max(1.0, tracker.duration))
        result = VGroup(
            math_module_box(r"\hat h_A", "estimated local homophily", width=3.2, height=1.05, emphasized=True),
            mt(r"\hat h_A\in[0,1]", 38),
        ).arrange(RIGHT, buff=0.65).move_to(DOWN * 2.18 + RIGHT * 0.35)
        with self.voiceover(
            text="Nếu hai phân phối tương tự nhau, giá trị sẽ cao, cho thấy Node A có xu hướng giống "
            "neighborhood. Nếu hai phân phối khác nhau, giá trị này sẽ thấp và Node A có khả năng "
            "nằm trong vùng heterophilous."
        ) as tracker:
            self.play(TransformFromCopy(VGroup(p_a, p_mean), result[0]), Write(result[1]), run_time=max(0.8, tracker.duration))
        prior = takeaway_chip("Estimated homophily is a routing prior")
        with self.voiceover(
            text="Đây chỉ là một routing prior, nghĩa là một tín hiệu hỗ trợ Router, chứ không trực "
            "tiếp quyết định việc gọi LLM."
        ) as tracker:
            self.play(FadeIn(prior, shift=UP * 0.08), run_time=max(0.42, tracker.duration))
        self.wait(0.8)


class S4_13_OriginalInfo(GlanceMovingScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        _clear_except(self)
        _banner(self)
        _show_header(self, 13, "Original information retained for Node A")

        raw_tag = VGroup(txt("RAW TEXT", 20, MUTED, BOLD), mt(r"t_A", 29, MUTED)).arrange(RIGHT, buff=0.14)
        raw_title = fit_width(txt('"Improving Graph Neural Networks\nunder Heterophily"', 28, INK, BOLD), 5.2)
        x_vector = feature_strip(r"x_A", n=9, cell_size=0.33, math_label=True)
        text_column = VGroup(raw_tag, raw_title, x_vector).arrange(DOWN, buff=0.34).move_to(LEFT * 3.45 + UP * 0.35)
        text_arrow = small_arrow(raw_title.get_bottom(), x_vector.get_top(), color=MUTED, stroke_width=2.1, buff=0.12)

        degree_A = avatar_node("A", target=True, radius=0.29)
        degree_neighbors = VGroup(
            avatar_node("B", radius=0.19).move_to(UP * 1.0),
            avatar_node("C", radius=0.19).move_to(LEFT * 1.15),
            avatar_node("D", radius=0.19).move_to(RIGHT * 1.15),
            avatar_node("E", radius=0.19).move_to(DOWN * 1.0),
        )
        degree_edges = VGroup(*[Line(degree_A.get_center(), n.get_center(), buff=0.25, color=C_EDGE, stroke_width=1.8) for n in degree_neighbors])
        degree_graph = VGroup(degree_edges, degree_A, degree_neighbors)
        degree_eq = mt(r"d_A=|N(A)|=4", 42)
        degree_column = VGroup(txt("CITATION NEIGHBORHOOD", 20, MUTED, BOLD), degree_graph, degree_eq).arrange(DOWN, buff=0.30)
        degree_column.move_to(RIGHT * 3.45 + UP * 0.35)

        with self.voiceover(
            text="Ngoài các biểu diễn đã được học, GLANCE vẫn giữ lại thông tin gốc của Node A."
        ) as tracker:
            self.play(FadeIn(raw_tag), Write(raw_title), run_time=max(0.7, tracker.duration))
        with self.voiceover(
            text="Thành phần đầu tiên là x A, tức feature được trích xuất từ nội dung văn bản."
        ) as tracker:
            self.play(GrowArrow(text_arrow), TransformFromCopy(raw_title, x_vector), run_time=max(0.75, tracker.duration))
        with self.voiceover(
            text="Thành phần thứ hai là degree d A, thể hiện số lượng hàng xóm trực tiếp."
        ) as tracker:
            self.play(FadeIn(degree_column[0]), FadeIn(degree_A), run_time=max(0.4, tracker.duration * 0.4))
            self.play(FadeIn(degree_neighbors), Create(degree_edges), run_time=max(0.65, tracker.duration * 0.6))
            self.bring_to_front(degree_A, degree_neighbors)
        with self.voiceover(text="Trong ví dụ, A kết nối với bốn node nên degree bằng bốn.") as tracker:
            self.play(Write(degree_eq), run_time=max(0.55, tracker.duration))

        direct_eq = equation_card(
            r"\mathcal I_A^{\mathrm{direct}}=(x_A,d_A)",
            "semantic feature + structural degree",
            width=6.2,
            height=1.22,
            emphasized=True,
        ).move_to(DOWN * 2.25)
        with self.voiceover(
            text="Hai thông tin này giúp Router quan sát trực tiếp cả đặc điểm ngữ nghĩa ban đầu lẫn "
            "lượng thông tin cấu trúc mà GNN có thể khai thác."
        ) as tracker:
            self.play(TransformFromCopy(VGroup(x_vector, degree_eq), direct_eq), run_time=max(0.8, tracker.duration))
        self.wait(1.6)


class S4_14_RoutingFeature(GlanceMovingScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        _clear_except(self)
        _banner(self)
        _show_header(self, 14, "Build the routing feature")

        cards = VGroup(
            equation_card(r"z_G(A)", "GNN embedding", 2.15, 0.90, True),
            equation_card(r"u_A", "uncertainty", 2.15, 0.90),
            equation_card(r"\hat h_A", "homophily", 2.15, 0.90),
            equation_card(r"x_A", "original feature", 2.15, 0.90),
            equation_card(r"d_A", "degree", 2.15, 0.90),
        ).arrange(RIGHT, buff=0.17)
        cards.scale_to_fit_width(12.0).move_to(UP * 1.35)
        with self.voiceover(
            text="Đến đây, toàn bộ tín hiệu được ghép thành routing feature f A."
        ) as tracker:
            self.play(
                LaggedStart(*[FadeIn(card, shift=DOWN * 0.08) for card in cards], lag_ratio=0.10),
                run_time=max(0.95, tracker.duration),
            )

        formulas = [
            r"f_A=[z_G(A)]",
            r"f_A=[z_G(A),u_A]",
            r"f_A=[z_G(A),u_A,\hat h_A]",
            r"f_A=[z_G(A),u_A,\hat h_A,x_A]",
            r"f_A=[z_G(A),u_A,\hat h_A,x_A,d_A]",
        ]
        with self.voiceover(
            text="Vector này gồm năm thành phần: GNN embedding, uncertainty, estimated homophily, "
            "original feature và degree. Mỗi thành phần phản ánh một khía cạnh khác nhau của Node A."
        ) as tracker:
            current_formula = mt(formulas[0], 46).move_to(DOWN * 0.25)
            self.play(TransformFromCopy(cards[0], current_formula), run_time=max(0.58, tracker.duration * 0.2))
            for index, formula in enumerate(formulas[1:], start=1):
                next_formula = mt(formula, 46).move_to(current_formula)
                self.play(
                    cards[index][0].animate.set_stroke(INK),
                    TransformMatchingTex(current_formula, next_formula),
                    run_time=max(0.55, tracker.duration * 0.2),
                )
                current_formula = next_formula

        note = VGroup(
            txt("FIVE COMPLEMENTARY SIGNALS", 22, INK, BOLD),
            txt("No single signal decides routing", 21, MUTED),
        ).arrange(DOWN, buff=0.12).move_to(DOWN * 1.55)
        with self.voiceover(
            text="Quan trọng là không có một tín hiệu riêng lẻ nào tự quyết định routing. Router sẽ "
            "học cách xem xét tổ hợp của cả năm tín hiệu."
        ) as tracker:
            self.play(FadeIn(note, shift=UP * 0.08), run_time=max(0.48, tracker.duration))
        self.wait(0.8)


class S4_15_RouterScore(GlanceMovingScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        _clear_except(self)
        _banner(self)
        _show_header(self, 15, "Router: from feature vector to routing score")

        feature = mt(r"f_A", 50).move_to(LEFT * 4.75)
        router = router_glyph(radius=0.74).move_to(ORIGIN)
        router_name = txt("ROUTER", 22, INK, BOLD).next_to(router, UP, buff=0.28)
        score = mt(r"a_A", 50).move_to(RIGHT * 4.75)
        arrows = VGroup(
            small_arrow(feature.get_right(), router.get_left(), stroke_width=2.4),
            small_arrow(router.get_right(), score.get_left(), stroke_width=2.4),
        )
        with self.voiceover(text="Routing feature được đưa vào một Router rất nhẹ.") as tracker:
            self.play(Write(feature), run_time=max(0.32, tracker.duration))

        equation = mt(r"a_A=\pi(f_A)=\sigma(w^\top f_A)", 47).move_to(DOWN * 1.25)
        with self.voiceover(
            text="Router gồm một linear layer và hàm sigmoid, tạo ra routing score a A nằm trong "
            "khoảng từ 0 đến 1."
        ) as tracker:
            self.play(GrowArrow(arrows[0]), FadeIn(router), FadeIn(router_name), run_time=max(0.58, tracker.duration * 0.35))
            self.play(GrowArrow(arrows[1]), Write(score), run_time=max(0.52, tracker.duration * 0.3))
            self.play(TransformFromCopy(VGroup(feature, router, score), equation), run_time=max(0.78, tracker.duration * 0.35))

        score_states = [r"a_D=0.25", r"a_E=0.81", r"a_B=0.12", r"a_A=0.86"]
        with self.voiceover(
            text="Score cao cho thấy Node A có khả năng nhận được lợi ích khi sử dụng LLM. Score thấp "
            "cho thấy dự đoán hiện tại của GNN có thể đã đủ tốt."
        ) as tracker:
            current_score = mt(score_states[0], 37).move_to(DOWN * 2.05)
            self.play(Write(current_score), run_time=max(0.32, tracker.duration * 0.25))
            for state in score_states[1:]:
                next_score = mt(state, 37).move_to(current_score)
                self.play(TransformMatchingTex(current_score, next_score), run_time=max(0.36, tracker.duration * 0.25))
                current_score = next_score

        warning = txt(
            "Routing score is not a class probability", 19, MUTED, BOLD,
        ).move_to(RIGHT * 4.15 + UP * 1.75)
        with self.voiceover(
            text="Cần phân biệt rằng đây không phải xác suất lớp. Nó chỉ biểu diễn mức độ nên gửi node "
            "sang nhánh LLM."
        ) as tracker:
            self.play(FadeIn(warning, shift=UP * 0.08), run_time=max(0.40, tracker.duration))
        self.wait(0.8)


class S4_16_TopK(GlanceMovingScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        _clear_except(self)
        _banner(self)
        _show_header(self, 16, "Rank routing scores and select Top-K")

        data = [("D", 0.25), ("A", 0.86), ("B", 0.12), ("E", 0.81), ("C", 0.74)]
        rows = {label: score_row(label, value) for label, value in data}
        initial_rows = VGroup(*rows.values()).arrange(DOWN, buff=0.17).move_to(LEFT * 2.35)
        with self.voiceover(text="GLANCE không sử dụng một ngưỡng cố định cho từng node.") as tracker:
            self.play(
                LaggedStart(*[FadeIn(row, shift=RIGHT * 0.08) for row in initial_rows], lag_ratio=0.10),
                run_time=max(0.85, tracker.duration),
            )
        sorted_data = sorted(data, key=lambda item: item[1], reverse=True)
        targets = [LEFT * 2.35 + UP * (1.35 - 0.77 * index) for index in range(len(sorted_data))]
        with self.voiceover(
            text="Thay vào đó, hệ thống xếp hạng routing score của tất cả node trong batch."
        ) as tracker:
            self.play(
                *[rows[label].animate.move_to(target) for (label, _), target in zip(sorted_data, targets)],
                run_time=max(1.0, tracker.duration),
            )

        third_bottom = rows[sorted_data[2][0]].get_bottom()[1]
        fourth_top = rows[sorted_data[3][0]].get_top()[1]
        cutoff_y = (third_bottom + fourth_top) / 2
        top_line = Line(LEFT * 4.05, LEFT * 0.65, color=INK, stroke_width=1.8)
        top_line.set_y(cutoff_y)
        top_label = txt("TOP-3", 20, INK, BOLD).next_to(top_line, RIGHT, buff=0.22)
        with self.voiceover(
            text="Ví dụ, các node A, E và C có ba score cao nhất nên được chọn vào Top-3."
        ) as tracker:
            self.play(Create(top_line), FadeIn(top_label), run_time=max(0.48, tracker.duration * 0.5))
            for label, _ in sorted_data[3:]:
                self.play(rows[label].animate.set_opacity(0.38), run_time=max(0.20, tracker.duration * 0.25))

        topk_equation = fit_width(
            mt(r"R=\operatorname{TopK}\!\left(\{a_v:v\in B\}\right)", 41),
            6.2,
        ).move_to(RIGHT * 3.25 + UP * 0.80)
        with self.voiceover(text="Chỉ đúng K node được gửi sang LLM.") as tracker:
            self.play(Write(topk_equation), run_time=max(0.62, tracker.duration))
        selected = mt(r"A\in R\Longrightarrow r_A=1", 39).move_to(RIGHT * 3.25 + DOWN * 0.45)
        budget = VGroup(
            txt("SELECT EXACTLY K NODES", 22, INK, BOLD),
            txt("Fixed LLM compute budget", 20, MUTED),
        ).arrange(DOWN, buff=0.12).move_to(RIGHT * 3.25 + DOWN * 1.65)
        with self.voiceover(
            text="Nhờ vậy, GLANCE kiểm soát chính xác compute budget và tránh tình trạng số lần gọi "
            "LLM tăng ngoài dự kiến."
        ) as tracker:
            self.play(Write(selected), FadeIn(budget), run_time=max(0.62, tracker.duration * 0.6))
            self.play(
                Create(SurroundingRectangle(rows["A"], color=INK, buff=0.07, stroke_width=2)),
                run_time=max(0.40, tracker.duration * 0.4),
            )
        self.wait(0.8)


class S4_17_TwoFlows(GlanceMovingScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        _banner(self)
        header17 = _show_header(self, 17, "Router branches into two inference flows")
        (router, router_label, with_node, without_node,
         with_title, without_title, branch_arrows, overview) = _router_overview(self)

        with self.voiceover(text="Sau bước Top-K, pipeline được chia thành hai nhánh rõ ràng.") as tracker:
            self.play(FadeIn(router), FadeIn(router_label), run_time=max(0.45, tracker.duration))
        with self.voiceover(
            text="Nhánh thứ nhất dành cho những node thuộc tập routing R, tức là các node được sử dụng "
            "LLM. Nhánh thứ hai dành cho những node không thuộc R."
        ) as tracker:
            self.play(
                LaggedStart(*[GrowArrow(arrow) for arrow in branch_arrows], lag_ratio=0.16),
                FadeIn(with_node), FadeIn(without_node),
                FadeIn(with_title), FadeIn(without_title),
                run_time=max(0.82, tracker.duration),
            )
        with self.voiceover(
            text="Việc tách hai nhánh này là cơ sở giúp GLANCE vừa tận dụng sức mạnh ngữ nghĩa của LLM, "
            "vừa duy trì chi phí xử lý hợp lý."
        ):
            pass
        self.wait(0.55)


class S4_18_WithoutLLM(GlanceMovingScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        _banner(self)
        header17 = step_header(17, "Router branches into two inference flows")
        (router, router_label, with_node, without_node,
         with_title, without_title, branch_arrows, overview) = _router_overview(self)
        self.add(header17, overview)

        flow_center = RIGHT * 5.50 + DOWN * 1.30
        detail_node = without_node.copy()
        detail_title = VGroup(
            txt("WITHOUT LLM", 22, MUTED, BOLD),
            mt(r"v\notin R", 25, MUTED),
        ).arrange(DOWN, buff=0.10)
        gnn_prediction = probability_bars(
            r"p_{H,v}", [0.62, 0.25, 0.13], width=2.05, math_label=True,
        )
        decision = fit_width(
            mt(r"\hat y_v=\underset{k}{\operatorname{arg\,max}}\;p_{H,v,k}", 31), 3.45,
        )
        detail_modules = VGroup(
            detail_node, detail_title, gnn_prediction, decision,
        ).arrange(RIGHT, buff=0.64).move_to(flow_center)

        with self.voiceover(text="Trước tiên là nhánh đơn giản hơn.") as tracker:
            self.play(FadeOut(header17), run_time=max(0.25, tracker.duration * 0.2))
            self.play(
                self.camera.frame.animate.move_to(flow_center).set(width=12.0),
                overview.animate.set_opacity(0.0),
                run_time=max(0.90, tracker.duration * 0.5),
            )
            self.play(FadeIn(detail_node), FadeIn(detail_title), run_time=max(0.32, tracker.duration * 0.3))

        flow_y = flow_center[1]
        direct_arrows = VGroup(
            small_arrow(
                [detail_title.get_right()[0], flow_y, 0],
                [gnn_prediction.get_left()[0], flow_y, 0],
                color=C_EDGE,
            ),
            small_arrow(
                [gnn_prediction.get_right()[0], flow_y, 0],
                [decision.get_left()[0], flow_y, 0],
                color=C_EDGE,
            ),
        )
        without_detail = VGroup(detail_node, detail_title, gnn_prediction, decision, direct_arrows)
        with self.voiceover(
            text="Nếu một node không được route, GLANCE bỏ qua toàn bộ bước tạo prompt, gọi LLM và "
            "Refiner. Phân phối cuối cùng của node được giữ nguyên bằng p H phẩy v, tức prediction "
            "ban đầu của GNN."
        ) as tracker:
            self.play(GrowArrow(direct_arrows[0]), FadeIn(gnn_prediction), run_time=max(0.55, tracker.duration * 0.5))
            self.play(GrowArrow(direct_arrows[1]), Write(decision), run_time=max(0.58, tracker.duration * 0.5))
        with self.voiceover(
            text="Sau đó, hệ thống lấy lớp có xác suất lớn nhất. Nhờ vậy, các node dễ không phải chịu "
            "thêm chi phí và cũng không bị LLM làm thay đổi một dự đoán vốn đã chính xác."
        ):
            pass
        self.wait(0.4)

        self.play(FadeOut(without_detail), run_time=0.38)
        self.play(
            Restore(self.camera.frame),
            overview.animate.set_opacity(1),
            FadeIn(header17),
            run_time=0.90,
        )
        self.wait(0.42)


class S4_19_WithLLMContext(GlanceMovingScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        _banner(self)
        header17 = step_header(17, "Router branches into two inference flows")
        (router, router_label, with_node, without_node,
         with_title, without_title, branch_arrows, overview) = _router_overview(self)
        self.add(header17, overview)

        center_A = avatar_node("A", target=True, radius=0.28).move_to(LEFT * 0.35 + UP * 1.52)
        ring_1 = Circle(radius=1.08, stroke_color=MUTED, stroke_width=1.5).move_to(center_A)
        ring_2 = Circle(radius=1.82, stroke_color=C_EDGE, stroke_width=1.3).move_to(center_A)
        hop1_positions = [
            center_A.get_center() + UP * 0.72,
            center_A.get_center() + LEFT * 0.76,
            center_A.get_center() + RIGHT * 0.76,
            center_A.get_center() + DOWN * 0.72,
        ]
        hop1_nodes = VGroup(*[
            avatar_node(label, radius=0.21).move_to(position)
            for label, position in zip("BCDE", hop1_positions)
        ])
        hop2_positions = [
            center_A.get_center() + UP * 1.48 + LEFT * 0.35,
            center_A.get_center() + UP * 1.42 + RIGHT * 0.52,
            center_A.get_center() + LEFT * 1.52 + DOWN * 0.42,
            center_A.get_center() + RIGHT * 1.52 + DOWN * 0.42,
            center_A.get_center() + DOWN * 1.52,
        ]
        hop2_nodes = VGroup(*[
            avatar_node(label, radius=0.19).move_to(position)
            for label, position in zip("FGHIJ", hop2_positions)
        ])

        hop1_edges = VGroup(*[
            Line(center_A.get_center(), neighbor.get_center(), buff=0.27, color=INK, stroke_width=2.2)
            for neighbor in hop1_nodes
        ])
        hop2_parent_indices = [0, 0, 1, 2, 3]
        hop2_edges = VGroup(*[
            Line(
                hop1_nodes[parent_index].get_center(), neighbor.get_center(),
                buff=0.23, color=MUTED, stroke_width=1.8,
            )
            for parent_index, neighbor in zip(hop2_parent_indices, hop2_nodes)
        ])

        with self.voiceover(
            text="Với Node A được route, GLANCE khai thác văn bản ở ba mức ngữ cảnh."
        ) as tracker:
            self.play(FadeOut(header17), run_time=max(0.25, tracker.duration * 0.25))
            self.play(
                self.camera.frame.animate.move_to(with_node).set(width=9.2),
                overview.animate.set_opacity(0.0),
                run_time=max(0.90, tracker.duration * 0.75),
            )

        with self.voiceover(text="Mức đầu tiên là ego text, chỉ chứa nội dung của chính Node A.") as tracker:
            self.play(GrowFromCenter(center_A), run_time=max(0.38, tracker.duration))

        with self.voiceover(
            text="Mức thứ hai là 1-hop context, bổ sung nội dung từ các node trích dẫn trực tiếp."
        ) as tracker:
            self.play(
                Create(ring_1), Create(hop1_edges),
                LaggedStart(*[FadeIn(neighbor) for neighbor in hop1_nodes], lag_ratio=0.10),
                run_time=max(0.72, tracker.duration),
            )
            self.bring_to_front(center_A, hop1_nodes)

        with self.voiceover(
            text="Mức cuối cùng là 2-hop context, cung cấp ngữ cảnh rộng hơn từ các node cách A hai cạnh."
        ) as tracker:
            self.play(
                Create(ring_2), Create(hop2_edges),
                LaggedStart(*[FadeIn(neighbor) for neighbor in hop2_nodes], lag_ratio=0.10),
                run_time=max(0.82, tracker.duration),
            )
            self.bring_to_front(center_A, hop1_nodes, hop2_nodes)

        context_cards = VGroup(
            equation_card(r"P_0(A)=t_A", "0-hop · ego text", width=4.25, height=0.88, emphasized=True),
            equation_card(r"P_1(A)=\operatorname{Serialize}(t_A,N_1(A))", "1-hop · direct citations", width=4.25, height=0.88),
            equation_card(r"P_2(A)=\operatorname{Serialize}(t_A,N_2(A))", "2-hop · wider context", width=4.25, height=0.88),
        ).arrange(DOWN, buff=0.28).move_to(RIGHT * 3.95 + UP * 1.52)
        with self.voiceover(text="Ba mức được xử lý riêng thay vì gộp tất cả thành một prompt rất dài.") as tracker:
            self.play(
                LaggedStart(*[FadeIn(card, shift=LEFT * 0.08) for card in context_cards], lag_ratio=0.18),
                run_time=max(0.92, tracker.duration),
            )
        self.wait(0.5)

        self.play(
            Restore(self.camera.frame),
            FadeOut(VGroup(center_A, ring_1, ring_2, hop1_edges, hop2_edges, hop1_nodes, hop2_nodes, context_cards)),
            FadeOut(overview),
            run_time=0.85,
        )


class S4_23_EgoEmbedding(GlanceMovingScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        _banner(self)
        header = _show_header(self, 23, "Shared LLM encoder: ego embedding")

        equation = mt(r"z_{L,0}(A)=L(P_0(A))", 40, C_LLM_LIGHT).move_to(UP * 2.25)
        prompt = equation_card(
            r"P_0(A)", "ego prompt", width=3.00, height=0.95, emphasized=True,
        ).move_to(LEFT * 3.85 + UP * 1.15)
        llm = module_box(
            "Qwen3-Embed-8B", "shared embedding encoder", width=3.85, height=1.12, emphasized=True,
        ).move_to(LEFT * 3.85 + DOWN * 0.48)
        output = embedding_strip(
            r"z_{L,0}(A)", C_LLM_LIGHT, n=9, cell_size=0.27, emphasized=True,
        ).move_to(LEFT * 3.85 + DOWN * 2.15)
        details = prompt_panel(
            "Prompt v0",
            [
                "EGO ONLY",
                "Title: Improving graph neural networks under heterophily",
                "Question: what is the paper category?",
            ],
            width=5.75, height=2.55,
        ).move_to(RIGHT * 3.70 + DOWN * 0.36)

        prompt_arrow = small_arrow(prompt.get_bottom(), llm.get_top(), color=MUTED, buff=0.10)
        output_arrow = small_arrow(llm.get_bottom(), output.get_top(), color=C_LLM_LIGHT, buff=0.10)

        with self.voiceover(text="Prompt đầu tiên chỉ chứa ego text của Node A.") as tracker:
            self.play(Write(equation), run_time=max(0.50, tracker.duration * 0.55))
            self.play(FadeIn(prompt, shift=DOWN * 0.08), run_time=max(0.42, tracker.duration * 0.45))
        with self.voiceover(
            text="Prompt này được đưa vào Qwen3-Embed-8B, đóng vai trò shared embedding encoder."
        ) as tracker:
            self.play(GrowArrow(prompt_arrow), FadeIn(llm, shift=DOWN * 0.08), run_time=max(0.55, tracker.duration * 0.55))
            self.play(FadeIn(details, shift=LEFT * 0.08), run_time=max(0.48, tracker.duration * 0.45))
        with self.voiceover(
            text="Đầu ra không phải là một câu trả lời hay class label, mà là embedding z L phẩy 0 của A."
        ) as tracker:
            self.play(GrowArrow(output_arrow), FadeIn(output, shift=DOWN * 0.08), run_time=max(0.66, tracker.duration))

        legend = txt("LIGHT AMBER · EGO CONTEXT EMBEDDING", 19, C_LLM_LIGHT, BOLD).next_to(output, DOWN, buff=0.20)
        with self.voiceover(
            text="Embedding này biểu diễn thông tin ngữ nghĩa từ chính nội dung của Node A."
        ) as tracker:
            self.play(FadeIn(legend), run_time=max(0.34, tracker.duration))
        self.add(source("Phụ lục B.3, tr.15-16"))
        self.wait(0.5)


class S4_24_OneHopEmbedding(GlanceMovingScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        _banner(self)
        header, equation, prompt, llm, output, details, prompt_arrow, output_arrow, legend = _llm_stage(self, 0)
        self.add(header, equation, prompt, llm, output, details, prompt_arrow, output_arrow, legend)

        header_1 = step_header(24, "Shared LLM encoder: 1-hop embedding")
        equation_1 = mt(r"z_{L,1}(A)=L(P_1(A))", 40, C_LLM).move_to(equation)
        prompt_1 = equation_card(
            r"P_1(A)", "ego + direct neighbors", width=3.35, height=0.95, emphasized=True,
        ).move_to(prompt)
        output_1 = embedding_strip(r"z_{L,1}(A)", C_LLM, n=9, cell_size=0.27, emphasized=True).move_to(output)
        details_1 = prompt_panel(
            "Prompt v1",
            [
                "EGO + 1-HOP",
                "Title: Improving graph neural networks under heterophily",
                "Direct citations: graph LLMs; heterophily-aware GNNs",
            ],
            width=5.55, height=2.65,
        ).move_to(details)
        legend_1 = txt("BASE AMBER · 1-HOP CONTEXT EMBEDDING", 19, C_LLM, BOLD).move_to(legend)
        with self.voiceover(
            text="Ở bước tiếp theo, prompt được mở rộng bằng nội dung của các node hàng xóm trực tiếp. "
            "Prompt mới vẫn đi qua cùng một LLM encoder, chứ không phải một mô hình khác. Đầu ra là "
            "z L phẩy 1 của A. Embedding này bổ sung bối cảnh từ các bài báo có quan hệ trực tiếp "
            "với Node A."
        ) as tracker:
            self.play(
                Transform(header, header_1),
                TransformMatchingTex(equation, equation_1),
                Transform(prompt, prompt_1),
                Transform(output, output_1),
                ReplacementTransform(details, details_1),
                Transform(legend, legend_1),
                output_arrow.animate.set_color(C_LLM),
                run_time=max(0.88, tracker.duration),
            )
        self.wait(0.5)


class S4_25_TwoHopEmbedding(GlanceMovingScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        _banner(self)
        header, equation, prompt, llm, output, details, prompt_arrow, output_arrow, legend = _llm_stage(self, 1)
        self.add(header, equation, prompt, llm, output, details, prompt_arrow, output_arrow, legend)

        header_2 = step_header(25, "Shared LLM encoder: 2-hop embedding")
        equation_2 = mt(r"z_{L,2}(A)=L(P_2(A))", 40, C_LLM_DEEP).move_to(equation)
        prompt_2 = equation_card(
            r"P_2(A)", "ego + distance-two context", width=3.55, height=0.95, emphasized=True,
        ).move_to(prompt)
        output_2 = embedding_strip(r"z_{L,2}(A)", C_LLM_DEEP, n=9, cell_size=0.27, emphasized=True).move_to(output)
        details_2 = prompt_panel(
            "Prompt v2",
            [
                "EGO + 2-HOP",
                "Title: Improving graph neural networks under heterophily",
                "Wider context: GCNs; language embeddings; heterophily-aware GNNs",
            ],
            width=5.55, height=2.72,
        ).move_to(details)
        legend_2 = txt("DEEP AMBER · 2-HOP CONTEXT EMBEDDING", 19, C_LLM_DEEP, BOLD).move_to(legend)
        with self.voiceover(
            text="Tương tự, prompt thứ ba đưa thêm ngữ cảnh ở khoảng cách hai hop. Nó giúp mô hình quan "
            "sát một vùng rộng hơn của citation graph và nhận biết chủ đề tổng quát xung quanh Node A. "
            "Prompt tiếp tục sử dụng shared LLM encoder và tạo embedding z L phẩy 2 của A. Như vậy, "
            "một encoder được tái sử dụng cho ba phiên bản prompt khác nhau."
        ) as tracker:
            self.play(
                Transform(header, header_2),
                TransformMatchingTex(equation, equation_2),
                Transform(prompt, prompt_2),
                Transform(output, output_2),
                ReplacementTransform(details, details_2),
                Transform(legend, legend_2),
                output_arrow.animate.set_color(C_LLM_DEEP),
                run_time=max(0.88, tracker.duration),
            )
        self.wait(0.5)


class S4_26_MergeEmbeddings(GlanceMovingScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        _banner(self)
        header26 = _show_header(self, 26, "Merge the three LLM embeddings")

        z0 = named_embedding_strip(r"z_{L,0}(A)", C_LLM_LIGHT, n=7, cell_size=0.25)
        z1 = named_embedding_strip(r"z_{L,1}(A)", C_LLM, n=7, cell_size=0.25)
        z2 = named_embedding_strip(r"z_{L,2}(A)", C_LLM_DEEP, n=7, cell_size=0.25)
        source_row = VGroup(z0, z1, z2).arrange(RIGHT, buff=0.90).move_to(UP * 0.25)
        with self.voiceover(text="Ba embedding vừa tạo được nối lại với nhau.") as tracker:
            self.play(
                LaggedStart(*[FadeIn(item, shift=UP * 0.08) for item in source_row], lag_ratio=0.12),
                run_time=max(0.82, tracker.duration),
            )

        z0_cells, z1_cells, z2_cells = z0[1], z1[1], z2[1]
        individual_labels = VGroup(z0[0], z1[0], z2[0])
        close_guides = VGroup(
            z0_cells.copy(), z1_cells.copy(), z2_cells.copy(),
        ).arrange(RIGHT, buff=0.055).scale(1.18).move_to(UP * 0.25)
        moving_parts = [z0_cells, z1_cells, z2_cells]
        with self.voiceover(
            text="Kết quả là Z L của A, đại diện cho toàn bộ thông tin ngữ nghĩa mà LLM thu được."
        ) as tracker:
            self.play(
                FadeOut(individual_labels, shift=UP * 0.06),
                *[
                    part.animate.move_to(guide.get_center()).scale(1.18)
                    for part, guide in zip(moving_parts, close_guides)
                ],
                run_time=max(0.92, tracker.duration),
            )

        z_l_row = VGroup(z0_cells, z1_cells, z2_cells)
        merged_label = mt(r"Z_L(A)", 39).next_to(z_l_row, UP, buff=0.28)
        with self.voiceover(
            text="Vector này giữ riêng ba thành phần: nội dung của chính node, ngữ cảnh trực tiếp và "
            "ngữ cảnh xa hơn."
        ) as tracker:
            self.play(FadeIn(merged_label, shift=UP * 0.08), run_time=max(0.42, tracker.duration))
        z_l_visual = VGroup(merged_label, z_l_row)

        merge_equation = fit_width(
            mt(r"Z_L(A)=\left[z_{L,0}(A)\Vert z_{L,1}(A)\Vert z_{L,2}(A)\right]", 39), 11.3,
        ).move_to(DOWN * 1.65)
        with self.voiceover(
            text="LLM representation vẫn chưa phải là kết quả phân loại cuối cùng. Nó sẽ được kết hợp "
            "tiếp với biểu diễn graph từ GNN."
        ) as tracker:
            self.play(Write(merge_equation), run_time=max(0.68, tracker.duration))
        self.wait(0.78)


class S4_27_FusedRepresentation(GlanceMovingScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        _banner(self)
        (header26, z0_cells, z1_cells, z2_cells,
         merged_label, z_l_visual, merge_equation) = _merged_llm_embedding(self)
        self.add(header26, z_l_visual, merge_equation)

        header27 = step_header(27, "The fused representation combines structure and semantics")
        z_g = named_embedding_strip(r"z_G(A)", C_GNN, n=8, cell_size=0.26).scale(0.85)
        z_g.move_to(LEFT * 3.25 + UP * 0.22)
        with self.voiceover(
            text="Embedding z G của A từ GNN chứa thông tin về feature và cấu trúc graph."
        ) as tracker:
            self.play(Transform(header26, header27), FadeOut(merge_equation), run_time=max(0.58, tracker.duration * 0.3))
            self.play(z_l_visual.animate.scale(0.72).move_to(RIGHT * 3.25 + UP * 0.22), run_time=max(0.72, tracker.duration * 0.4))
            self.play(FadeIn(z_g, shift=RIGHT * 0.35), run_time=max(0.52, tracker.duration * 0.3))

        fusion_parts = [z_g[1], z0_cells, z1_cells, z2_cells]
        fusion_guides = VGroup(*[part.copy() for part in fusion_parts])
        fusion_guides.arrange(RIGHT, buff=0.055).scale(1.16).move_to(UP * 0.20)
        fusion_label = mt(r"[z_G(A)\Vert Z_L(A)]", 39).next_to(fusion_guides, UP, buff=0.28)
        with self.voiceover(
            text="Trong khi đó, Z L của A chứa thông tin semantic được trích từ ba mức prompt. GLANCE "
            "nối hai vector này thành một fused representation."
        ) as tracker:
            self.play(
                FadeOut(VGroup(z_g[0], merged_label), shift=UP * 0.05),
                *[
                    part.animate.move_to(guide.get_center()).scale(1.16)
                    for part, guide in zip(fusion_parts, fusion_guides)
                ],
                FadeIn(fusion_label, shift=UP * 0.08),
                run_time=max(0.94, tracker.duration),
            )

        left_note = VGroup(
            txt("TEAL", 20, C_GNN, BOLD),
            txt("GNN structure", 20, MUTED),
        ).arrange(DOWN, buff=0.08).move_to(LEFT * 3.85 + DOWN * 1.75)

        right_note = VGroup(
            txt("LIGHT / BASE / DEEP AMBER", 20, MUTED, BOLD),
            txt("LLM semantic context", 20, MUTED),
        ).arrange(DOWN, buff=0.08).move_to(RIGHT * 3.85 + DOWN * 1.75)
        with self.voiceover(
            text="Có thể hiểu phần bên trái đại diện cho structural information từ GNN, còn ba phần "
            "bên phải đại diện cho semantic context từ LLM."
        ) as tracker:
            self.play(FadeIn(left_note), FadeIn(right_note), run_time=max(0.50, tracker.duration))

        with self.voiceover(text="Vector kết hợp này là đầu vào trực tiếp của Refiner."):
            pass
        self.wait(0.6)


class S4_28_RefinerMLP(GlanceMovingScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        _clear_except(self)
        _banner(self)
        _show_header(self, 28, "Refiner MLP: structure and output")

        equation = fit_width(
            mt(
                r"p_{C,A}=\operatorname{softmax}"
                r"\!\left(C([z_G(A)\Vert Z_L(A)])\right)",
                39,
            ),
            11.0,
        ).move_to(UP * 2.05)

        fusion_input = segmented_embedding(
            r"[z_G(A)\Vert Z_L(A)]",
            [C_GNN, C_LLM_LIGHT, C_LLM, C_LLM_DEEP],
            cells_per_segment=3,
            cell_size=0.24,
        ).move_to(UP * 1.28)

        network, edges, layers = mlp_diagram(layer_sizes=(5, 6, 4, 3))
        network.scale(0.82).move_to(DOWN * 0.18)
        for layer in layers:
            layer.set_stroke(C_EDGE).set_fill(BG, opacity=1.0)

        stage_label = txt(
            "Input",
            23,
            INK,
            BOLD,
        ).move_to(RIGHT * 3.20 + DOWN * 0.18)

        output_symbol = mt(
            r"p_{C,A}",
            46,
        ).move_to(DOWN * 2.02)

        with self.voiceover(
            text="Refiner là một MLP có nhiệm vụ kết hợp hai nguồn bằng chứng."
        ) as tracker:
            self.play(Write(equation), run_time=max(0.60, tracker.duration * 0.6))
            self.play(FadeIn(fusion_input, shift=DOWN * 0.06), run_time=max(0.42, tracker.duration * 0.4))

        with self.voiceover(
            text="Fused representation lần lượt đi qua các linear layer, ReLU, dropout và lớp output."
        ) as tracker:
            self.play(
                GrowArrow(
                    small_arrow(
                        fusion_input.get_bottom(),
                        network.get_top(),
                        buff=0.12,
                    )
                ),
                run_time=max(0.40, tracker.duration * 0.14),
            )
            self.play(
                LaggedStart(
                    *[FadeIn(layer, scale=0.85) for layer in layers],
                    lag_ratio=0.12,
                ),
                run_time=max(0.75, tracker.duration * 0.2),
            )
            self.play(
                LaggedStart(
                    *[Create(edge) for edge in edges],
                    lag_ratio=0.01,
                ),
                run_time=max(0.60, tracker.duration * 0.2),
            )
            self.bring_to_front(*layers)

            stage_names = ["Input", "Linear + ReLU", "Dropout + Linear", "Softmax"]
            self.play(
                FadeIn(stage_label),
                layers[0].animate.set_stroke(INK).set_fill(INK, opacity=1.0),
                run_time=max(0.36, tracker.duration * 0.11),
            )
            for index, stage in enumerate(stage_names[1:], start=1):
                next_label = txt(
                    stage,
                    23,
                    INK,
                    BOLD,
                ).move_to(stage_label)
                self.play(
                    layers[index - 1].animate.set_stroke(C_EDGE).set_fill(BG, opacity=1.0),
                    layers[index].animate.set_stroke(INK).set_fill(INK, opacity=1.0),
                    Transform(stage_label, next_label),
                    run_time=max(0.42, tracker.duration * 0.117),
                )

        with self.voiceover(text="Cuối cùng, softmax tạo ra phân phối lớp mới p C phẩy A.") as tracker:
            self.play(
                GrowArrow(
                    small_arrow(
                        network.get_bottom(),
                        output_symbol.get_top(),
                        buff=0.10,
                    )
                ),
                Write(output_symbol),
                run_time=max(0.55, tracker.duration),
            )

        note = takeaway_chip("The Refiner MLP outputs the refined class distribution")
        with self.voiceover(
            text="Refiner không thay thế GNN hoặc LLM. Nó học cách cân bằng thông tin cấu trúc từ GNN "
            "với thông tin ngữ nghĩa từ LLM để tạo ra dự đoán phù hợp hơn cho routed node."
        ) as tracker:
            self.play(FadeIn(note, shift=UP * 0.08), run_time=max(0.38, tracker.duration))
        self.wait(0.8)


class S4_29_RefinedDistribution(GlanceMovingScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        _clear_except(self)
        _banner(self)
        _show_header(self, 29, "LLM context refines the class distribution")

        transition_equation = mt(
            r"p_{H,A}\xrightarrow{\ +\,Z_L(A)\ }p_{C,A}", 45,
        ).move_to(UP * 2.12)

        # Keep both distributions on one centered baseline and preserve a clear
        # transition corridor between the two panels.
        before = probability_chart(
            [0.45, 0.40, 0.15], r"p_{H,A}", CLASS_NAMES, width=6.15,
        ).scale(0.79).move_to(LEFT * 3.28 + DOWN * 0.15)
        after = probability_chart(
            [0.15, 0.80, 0.05], r"p_{C,A}", CLASS_NAMES, width=6.15,
        ).scale(0.79).move_to(RIGHT * 3.28 + DOWN * 0.15)

        before_note = txt("GNN-ONLY", 20, MUTED, BOLD).next_to(
            before, DOWN, buff=0.28,
        )
        after_note = VGroup(
            txt("REFINED", 20, INK, BOLD),
            txt("WITH LLM CONTEXT", 17, MUTED, BOLD),
        ).arrange(DOWN, buff=0.07).next_to(after, DOWN, buff=0.23)

        comparison_arrow = small_arrow(
            before.get_right(),
            after.get_left(),
            color=INK,
            stroke_width=2.4,
            buff=0.18,
        )

        with self.voiceover(
            text="Trước khi sử dụng LLM, GNN tạo phân phối ban đầu là 0.45, 0.40 và 0.15. Phân phối "
            "này chưa thể hiện sự khác biệt rõ ràng giữa hai lớp đầu tiên."
        ) as tracker:
            self.play(Write(transition_equation), run_time=max(0.48, tracker.duration * 0.4))
            self.play(FadeIn(before, shift=UP * 0.08), FadeIn(before_note), run_time=max(0.62, tracker.duration * 0.6))
        with self.voiceover(
            text="Sau khi bổ sung LLM context và đi qua Refiner, phân phối chuyển thành 0.15, 0.80 "
            "và 0.05."
        ) as tracker:
            self.play(GrowArrow(comparison_arrow), run_time=max(0.38, tracker.duration * 0.35))
            self.play(FadeIn(after, shift=UP * 0.08), FadeIn(after_note), run_time=max(0.68, tracker.duration * 0.65))
        highlight = SurroundingRectangle(
            after[1][1][1], color=INK, buff=0.08, stroke_width=2,
        )
        with self.voiceover(text="Xác suất tập trung mạnh hơn vào lớp Graph Mining.") as tracker:
            self.play(Create(highlight), run_time=max(0.40, tracker.duration))
        with self.voiceover(
            text="Ví dụ này minh họa cách ngữ cảnh văn bản có thể giúp điều chỉnh một dự đoán còn "
            "chưa chắc chắn của GNN."
        ):
            pass
        self.wait(0.6)


class S4_30_FinalPrediction(GlanceMovingScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        _clear_except(self)
        _banner(self)
        _show_header(self, 30, "Final prediction and the two GLANCE flows")

        final_equation = fit_width(
            mt(
                r"A\in R\Longrightarrow p_A=p_{C,A}"
                r"\Longrightarrow "
                r"\hat y_A=\underset{k}{\operatorname{arg\,max}}\ p_{A,k}"
                r"=\text{Graph Mining}",
                39,
            ),
            11.6,
        ).move_to(UP * 1.55)
        with self.voiceover(
            text="Cuối cùng, GLANCE xác định phân phối được sử dụng tùy theo kết quả routing."
        ) as tracker:
            self.play(Write(final_equation), run_time=max(0.82, tracker.duration))

        with_llm = equation_card(
            r"v\in R:\quad p_v=p_{C,v}",
            "WITH LLM · refined prediction",
            width=5.25,
            height=1.18,
            emphasized=True,
        ).move_to(LEFT * 3.10 + DOWN * 0.55)

        without_llm = equation_card(
            r"v\notin R:\quad p_v=p_{H,v}",
            "WITHOUT LLM · original GNN prediction",
            width=5.25,
            height=1.18,
        ).move_to(RIGHT * 3.10 + DOWN * 0.55)

        with self.voiceover(
            text="Nếu node thuộc tập R, hệ thống sử dụng phân phối đã refine là p C phẩy v. Nếu node "
            "không thuộc R, hệ thống giữ nguyên phân phối GNN là p H phẩy v."
        ) as tracker:
            self.play(
                FadeIn(with_llm, shift=UP * 0.08),
                FadeIn(without_llm, shift=UP * 0.08),
                run_time=max(0.70, tracker.duration),
            )

        result = VGroup(
            avatar_node("A", target=True, radius=0.29),
            mt(r"\longrightarrow", 35),
            txt("Graph Mining", 31, INK, BOLD),
        ).arrange(RIGHT, buff=0.28).move_to(DOWN * 2.00)
        with self.voiceover(
            text="Với Node A trong ví dụ, A được route nên sử dụng kết quả của Refiner. Lớp có xác "
            "suất lớn nhất là Graph Mining, vì vậy đây là nhãn cuối cùng của Node A."
        ) as tracker:
            self.play(FadeIn(result, shift=UP * 0.08), run_time=max(0.50, tracker.duration))

        closing = takeaway_chip(
            "GNN-first · LLM-on-demand · two explicit inference flows"
        )
        with self.voiceover(
            text="Tóm lại, GLANCE có thể được mô tả bằng ba ý chính: GNN được sử dụng trước để xử lý "
            "toàn bộ graph. Router lựa chọn những node thực sự cần hỗ trợ. Và LLM chỉ được gọi theo "
            "nhu cầu để bổ sung thông tin ngữ nghĩa cho các trường hợp khó. Thiết kế này giúp GLANCE "
            "kết hợp được khả năng khai thác cấu trúc của GNN với khả năng hiểu văn bản của LLM, "
            "nhưng vẫn kiểm soát được chi phí tính toán."
        ) as tracker:
            self.play(FadeIn(closing, shift=UP * 0.08), run_time=max(0.40, tracker.duration * 0.05))

        self.wait(0.6)
        self.say(
            "Router không khả vi. Vậy huấn luyện nó kiểu gì, và có thật sự hiệu quả?"
        )
