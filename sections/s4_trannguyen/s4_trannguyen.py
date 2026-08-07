"""GLANCE architecture: router, LLM-on-demand context, and the refiner.

Nguồn: paper §5.1 và Hình 2 (tr.5-6); chi tiết prompt ở Phụ lục B.3 (tr.15-16).
Dựng lại đúng 3 bước trong Hình 2: routing features -> LLM đọc neighborhood
được route -> refiner hợp nhất embedding. Mỗi beat là một Scene riêng để
build.sh render và ghép theo thứ tự khai báo.

Điểm cắt với section 3: section 3 dựng đủ năm signal và dừng ở f_v; section 4
NHẬN f_v rồi mới bắt đầu (f_v -> a_v -> top-k -> LLM -> refiner). Các beat
S4_03…S4_14 cũ (ba nguồn thông tin, message passing, MLP Q, soft homophily,
feature gốc, degree, ghép f_A) đã chuyển nguyên sang s3_nhutanh.py thành
S3_07…S3_19; ở đây S4_02 chỉ nhắc lại f_v thành một bundle. Số trên pill header
đã dồn liên tục 1…13 sau khi chuyển; tên class giữ nguyên để không mất cache
media và thứ tự ghép.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from glance_style import *

import numpy as np

SECTION, SECTION_NAME, OWNER = "4", "GLANCE architecture", "Trần Nguyên"
ACCENT = SECTION_COLORS.get(SECTION, C_HIGHLIGHT)

CLASS_NAMES = ["Machine Learning", "Graph Mining", "Data Management"]

# S4 dùng chung bảng màu "Deep Graph" của glance_style (GNN xanh dương, LLM cam,
# Router tím, tín hiệu cyan...). Trước đây file này tự ghi đè màu cục bộ (kể cả
# LLM = xanh lá, lệch quy ước); đã bỏ để mọi section đồng nhất một bảng màu.


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
STEP1_BOX = (5.20, 2.80, np.array([-2.80, 1.45, 0.0]))
STEP2_BOX = (5.20, 2.80, np.array([3.00, 1.45, 0.0]))
STEP3_BOX = (11.20, 2.45, np.array([0.10, -2.00, 0.0]))
CORRIDOR_Y = -0.50
TEXT_LINE_Y = -0.60
# Left compartment of the step 3 frame, reserved for the un-routed branch.
NO_LLM_X = -4.55
NO_LLM_PREDICTION_POS = np.array([-3.75, -1.90, 0.0])
# The divider only draws the split; it deliberately does NOT drive the sizes
# below, so nudging it leaves both compartments' contents where they are.
NO_LLM_DIVIDER_X = -2.45
STEP3_CONTENT_W = 8.10
STEP3_CONTENT_X = 1.85
REFINER_SHRINK = 0.92
# Straight drop from the step 2 strips into Z_L(A): nudged right of Z_L(A)'s
# axis, and held clear of both embeddings so it reads as a link, not a stem.
LLM_ARROW_DX = 0.10
LLM_ARROW_GAP = 0.13


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


def _mini_strip(color, n=4, cell=0.17):
    return VGroup(*[
        Square(
            side_length=cell, stroke_color=MUTED, stroke_width=0.9,
            fill_color=color, fill_opacity=0.95 if index % 2 == 0 else 0.65,
        )
        for index in range(n)
    ]).arrange(RIGHT, buff=0.025)


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
        number=6, title="Shared LLM encoder: ego embedding",
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
        number=7, title="Shared LLM encoder: 1-hop embedding",
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
    header26 = step_header(9, "Merge the three LLM embeddings")
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
            text="Đầu vào của bài toán là một đồ thị có thuộc tính văn bản, được ký hiệu là gờ bằng vê, e và tê."
        ) as tracker:
            self.play(FadeIn(statement), Write(graph_eq), run_time=0.85)

        with self.voiceover(
            text="Trong ví dụ đồ thị trích dẫn này, mỗi nót đại diện cho một bài báo khoa học."
        ) as tracker:
            self.play(FadeIn(node_def, shift=UP * 0.08), run_time=0.5)

        with self.voiceover(text="Các cạnh thể hiện quan hệ trích dẫn giữa các bài báo.") as tracker:
            self.play(FadeIn(edge_def, shift=UP * 0.08), run_time=0.5)

        with self.voiceover(
            text="Ngoài cấu trúc đồ thị, mỗi nót còn có nội dung văn bản, chẳng hạn như tiêu đề hoặc phần tóm tắt."
        ) as tracker:
            self.play(FadeIn(text_def, shift=UP * 0.08), run_time=0.5)

        self.say(
            "Như vậy, mỗi nót đồng thời có hai nguồn thông tin: nội dung của chính nó và mối quan hệ với các nót khác."
        )
        self.wait(0.4)


class S4_02_EndToEnd(GlanceMovingScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        _clear_except(self)
        _banner(self)
        _show_header(self, 2, "From a complex graph to Node A's label")

        positions = [
            ORIGIN,
            LEFT * 5.35 + UP * 2.05, LEFT * 4.15 + UP * 0.15, LEFT * 5.15 + DOWN * 1.60,
            LEFT * 2.75 + UP * 2.15, LEFT * 2.9 + UP * 0.95, LEFT * 3.3 + DOWN * 0.95,
            LEFT * 3.3 + DOWN * 1.85, LEFT * 1.05 + UP * 1.55, LEFT * 0.95 + DOWN * 1.30,
            RIGHT * 1.35 + UP * 1.65, RIGHT * 1.7 + UP * 0.55, RIGHT * 1.2 + DOWN * 1.60,
            RIGHT * 3.2 + UP * 2.00, RIGHT * 3.1 + UP * 0.45, RIGHT * 3.4 + DOWN * 1.20,
            RIGHT * 5.1 + UP * 1.35, RIGHT * 4.8 + DOWN * 0.25, RIGHT * 5.25 + DOWN * 1.85,
            # Hàng dưới cùng: lấp dải trống ~2 đơn vị dưới đáy đồ thị, giữ mật độ
            # cạnh tương đương phần trên để đồ thị vẫn đọc ra là một khối liền.
            LEFT * 3.95 + DOWN * 2.85, LEFT * 1.40 + DOWN * 2.95,
            RIGHT * 0.45 + DOWN * 2.60, RIGHT * 2.50 + DOWN * 2.95,
            RIGHT * 4.60 + DOWN * 2.75,
        ]
        target_A = avatar_node("A", target=True, radius=0.34).move_to(positions[0])
        # Nót A có mặt trong đồ thị ngay từ đầu dưới dạng một nót thường, nên tám
        # cạnh ở tâm không chụm vào một lỗ trống. Nhãn "A" và màu nhấn để dành cho
        # nhịp sau: lúc đó nót chỉ được tô sáng lên chứ không mọc ra từ chỗ trống.
        node_A, label_A = target_A
        node_A.set_fill(C_EDGE, opacity=1).set_stroke(color=MUTED, width=1.5, opacity=1)
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
            (3, 19), (7, 19), (19, 20), (7, 20), (9, 20), (20, 21), (12, 21),
            (21, 22), (15, 22), (22, 23), (18, 23),
        ]
        dense_edges = VGroup(*[
            Line(all_centers[i], all_centers[j], buff=0.17 if i and j else 0.27, color=C_EDGE, stroke_width=1.55)
            for i, j in edge_pairs
        ])
        graph_group = VGroup(dense_edges, other_nodes, target_A).move_to(DOWN * 0.05)
        graph_label = VGroup(
            txt("COMPLEX TEXT-ATTRIBUTED GRAPH", 18, MUTED, BOLD),
            txt("target: node A", 19, INK, BOLD),
        ).arrange(DOWN, buff=0.15).next_to(graph_group, DOWN, buff=0.20)

        # Đồ thị đứng sẵn ở dạng phác nhạt ngay từ đầu, rồi được tô màu quét từ
        # trái sang phải. Khán giả thấy trọn hình dạng đồ thị trước khi nó sáng
        # lên, thay vì phải chờ từng nót mọc ra từ khung trống.
        for edge in dense_edges:
            edge.set_stroke(color=MUTED, opacity=0.16)
        for node in [*other_nodes, node_A]:
            node.set_fill(C_EDGE, opacity=0.10).set_stroke(color=MUTED, opacity=0.30)
        self.add(dense_edges, other_nodes, node_A)

        def paint(mob):
            if isinstance(mob, Line):
                return mob.animate.set_stroke(color=C_EDGE, opacity=1.0)
            return mob.animate.set_fill(C_EDGE, opacity=1.0).set_stroke(color=MUTED, opacity=1.0)

        # Quét theo hoành độ nên nét tô chạy thành một làn liên tục.
        sweep = sorted([*dense_edges, *other_nodes, node_A], key=lambda m: m.get_center()[0])
        with self.voiceover(
            text="Từ một đồ thị tương đối phức tạp, mục tiêu của gờ lans là dự đoán nhãn cho từng nót."
        ) as tracker:
            self.play(
                LaggedStart(*[paint(m) for m in sweep], lag_ratio=0.012),
                run_time=min(2.4, tracker.duration),
            )
        with self.voiceover(text="Ở đây, chúng ta tập trung vào nót a.") as tracker:
            self.play(
                node_A.animate.set_fill(C_HIGHLIGHT, opacity=1).set_stroke(color=C_HIGHLIGHT, opacity=1),
                FadeIn(label_A),
                FadeIn(graph_label),
                run_time=0.55,
            )
        self.wait(0.3)

        # Input -> GLANCE -> output, narrated fully before the pipeline
        # detour: talk about the input, then the GLANCE box, then the
        # output, in that order.
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
            text="Sau khi đi qua toàn bộ hệ thống, gờ lans tạo ra một phân phối xác suất trên các lớp."
        ) as tracker:
            self.play(
                FadeOut(graph_label),
                graph_group.animate.scale(0.38).move_to(LEFT * Xg + UP * 0.15),
                run_time=0.85,
            )
        graph_to_glance = small_arrow(graph_group.get_right(), glance.get_left(), color=MUTED, stroke_width=2.1, buff=0.14)
        glance_to_p = small_arrow(glance.get_right(), probability.get_left(), color=MUTED, stroke_width=2.1, buff=0.14)
        self.play(GrowArrow(graph_to_glance), FadeIn(glance), run_time=0.62)
        pulse = Dot(graph_to_glance.get_start(), radius=0.07, color=INK)
        self.add(pulse)
        self.play(MoveAlongPath(pulse, graph_to_glance), run_time=0.55, rate_func=linear)
        with self.voiceover(
            text="Ví dụ, xác suất của nót a lần lượt là không chấm một hai, không chấm bảy ba và không chấm một năm."
        ) as tracker:
            self.play(
                FadeOut(pulse), GrowArrow(glance_to_p), FadeIn(probability, shift=RIGHT * 0.10),
                run_time=0.7,
            )
        self.wait(0.3)

        # ----------------------------------------------------------------
        # Reach the final label right here, while the black-box output is
        # still on screen -- Step 3 lands on this same [0.12, 0.73, 0.15],
        # so re-deriving "class 2" a second time after the pipeline walk-
        # through would just repeat this beat with extra ceremony.
        # ----------------------------------------------------------------
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

        self.say("Do đó, trong ví dụ này, nót a được dự đoán thuộc lớp thứ hai.")
        self.wait(0.6)

        # ----------------------------------------------------------------
        # Now pull back and cut into the full pipeline. The intro graph is
        # never morphed mid-scene; the pipeline gets its own fresh copy for
        # the TAG input.
        # ----------------------------------------------------------------
        self.camera.frame.save_state()
        with self.voiceover(
            text="Bên trong gờ lans không phải là một hộp đen: hệ thống lần lượt định tuyến, đọc văn bản, rồi tinh chỉnh dự đoán."
        ) as tracker:
            self.play(
                self.camera.frame.animate.scale(1.08),
                FadeOut(p_equation), FadeOut(decision),
                run_time=0.75,
            )
        self.camera.frame.restore()

        tag_icon = graph_group.copy().scale_to_fit_width(1.10).move_to([INPUT_X, 1.95, 0.0])
        graph_caption = txt("TAG", 16, MUTED, BOLD).move_to([INPUT_X, 1.42, 0.0])
        raw_text = VGroup(*[doc_icon(0.75) for _ in range(3)]).arrange(RIGHT, buff=0.08)
        raw_text.move_to([INPUT_X, 0.62, 0.0])
        raw_text_caption = txt("NODE TEXT", 13, MUTED, BOLD).move_to([INPUT_X, 0.14, 0.0])
        self.play(
            FadeIn(tag_icon), FadeIn(graph_caption), FadeIn(raw_text, shift=UP * 0.06), FadeIn(raw_text_caption),
            run_time=0.50,
        )

        # --- Step 1: the routing feature handed over by section 3 ---------
        # Năm signal đã được dựng đủ ở section 3 (S3_07…S3_19), nên ở đây chỉ
        # nhắc lại f_v thành một bundle rồi đi thẳng sang router.
        step1_w, step1_h, step1_c = STEP1_BOX
        step1_box = _dashed_box(step1_w, step1_h).move_to(step1_c)
        step1_title = txt("STEP 1 · ROUTING FEATURES", 16, MUTED, BOLD)

        bundle = equation_card(
            r"f_v=[z_G(v)\Vert u_v\Vert\hat h_v\Vert x_v\Vert d_v]",
            "five routing signals, built in section 3",
            width=4.55, height=1.20, emphasized=True,
        )
        router = router_glyph().scale(0.52)
        router_score = mt(r"a_v\in[0,1]", 19)
        router_column = VGroup(router, router_score).arrange(DOWN, buff=0.14)

        step1_visual = VGroup(bundle, router_column).arrange(RIGHT, buff=0.62)
        step1_content = VGroup(step1_title, step1_visual).arrange(DOWN, buff=0.30)
        _fit_into(step1_content, step1_w - 0.40, step1_h - 0.40).move_to(step1_c)

        merge_arrow = small_arrow(bundle.get_right(), router.get_left(), color=MUTED, stroke_width=1.7, buff=0.12)

        input_right_x = max(tag_icon.get_right()[0], raw_text.get_right()[0])
        input_mid_y = (tag_icon.get_center()[1] + raw_text_caption.get_center()[1]) / 2
        branch_x = input_right_x + 0.55
        tag_trunk_in = Line([input_right_x + 0.12, input_mid_y, 0.0], [branch_x, input_mid_y, 0.0], color=MUTED, stroke_width=1.9)
        tag_trunk = Line(
            [branch_x, input_mid_y, 0.0],
            [branch_x, bundle.get_center()[1], 0.0],
            color=MUTED, stroke_width=1.9,
        )
        tag_branches = VGroup(
            small_arrow([branch_x, bundle.get_center()[1], 0.0], bundle.get_left(),
                        color=MUTED, stroke_width=1.6, buff=0.08),
        )

        with self.voiceover(
            text="Bước một: từ năm tín hiệu đã dựng ở phần trước, mỗi nót đã có một đặc trưng định tuyến "
            "ép phẩy vê. Gờ lans học một bộ định tuyến ánh xạ ép phẩy vê thành lợi ích dự kiến "
            "của việc gọi lờ lờ mờ."
        ) as tracker:
            self.play(Create(step1_box), FadeIn(step1_title), run_time=0.55)
            self.play(Create(tag_trunk_in), Create(tag_trunk), run_time=0.40)
            self.play(
                LaggedStart(*[GrowArrow(b) for b in tag_branches], lag_ratio=0.16),
                FadeIn(bundle, shift=RIGHT * 0.06),
                run_time=0.80,
            )
            self.play(GrowArrow(merge_arrow), FadeIn(router, scale=0.85), run_time=0.50)
            self.play(Write(router_score), run_time=0.42)

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
        step2_body = VGroup(prompts, llm, strips).arrange(RIGHT, buff=0.56)
        step2_equation = mt(r"Z_L(A)=[z_{L,0}\Vert z_{L,1}\Vert z_{L,2}]", 19)
        step2_content = VGroup(step2_title, step2_body, step2_equation).arrange(DOWN, buff=0.24)
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
        # Just `v ∈ R`: the word ROUTE sat on top of the router glyph.
        route_label = mt(r"v\in R", 18).next_to(route_arrow, UP, buff=0.14)
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
            text="Bước hai: nót được định tuyến sẽ được gửi sang một lờ lờ mờ dùng chung, đọc ngữ cảnh "
            "ở ba mức nót trung tâm, một-hop và hai-hop."
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

        # --- Step 3: refine the GNN prediction ----------------------------
        # Mirrors the paper figure's right-to-left reading: routed embeddings
        # on the right feed the refiner, whose output sits on the left.
        step3_w, step3_h, step3_c = STEP3_BOX
        step3_box = _dashed_box(step3_w, step3_h).move_to(step3_c)
        step3_title = txt("STEP 3 · REFINE THE GNN PREDICTION", 16, MUTED, BOLD)
        gnn_side = _emb_below(r"z_G(A)", [C_GNN], 4, cell_size=0.17)
        llm_side = _emb_below(r"Z_L(A)", [C_LLM_LIGHT, C_LLM, C_LLM_DEEP], 2, cell_size=0.17)
        fusion_inputs = VGroup(gnn_side, llm_side).arrange(RIGHT, buff=0.50)
        refiner = module_box("Refiner MLP", "late fusion", width=2.35, height=0.95, emphasized=True)
        refined = probability_bars(r"p_{C,A}", [0.12, 0.73, 0.15], width=1.35, math_label=True)
        step3_row = VGroup(refined, refiner, fusion_inputs).arrange(RIGHT, buff=0.92)
        step3_equation = mt(r"p_{C,A}=\operatorname{softmax}\!\left(C([z_G(A)\Vert Z_L(A)])\right)", 23)
        step3_content = VGroup(step3_title, step3_row, step3_equation).arrange(DOWN, buff=0.24)
        # The frame is split: a left compartment for the un-routed branch, and
        # the refiner pipeline in the wider right one.
        _fit_into(step3_content, STEP3_CONTENT_W, step3_h - 0.40)
        step3_content.move_to([STEP3_CONTENT_X, step3_c[1], 0.0])
        # Shrunk after arranging, not before: changing its declared width would
        # re-flow the whole row and undo the placement above. The connecting
        # arrows are built from its edges below, so they lengthen to suit.
        refiner.scale(REFINER_SHRINK)
        no_llm_divider = Line(
            [NO_LLM_DIVIDER_X, step3_c[1] + step3_h / 2 - 0.22, 0.0],
            [NO_LLM_DIVIDER_X, step3_c[1] - step3_h / 2 + 0.22, 0.0],
            color=C_EDGE, stroke_width=1.5,
        )
        no_llm_label = txt("NO LLM", 15, MUTED, BOLD).move_to(
            [NO_LLM_X, step3_c[1] + step3_h / 2 - 0.30, 0.0]
        )
        # The un-routed branch is not a dead end: it keeps the GNN head's own
        # prediction p_{H,A}, so show that outcome instead of an empty box.
        # Same numbers as S4_08's initial prediction, so the two scenes agree.
        no_llm_prediction = probability_bars(
            r"p_{H,A}", [0.45, 0.40, 0.15], width=1.20, math_label=True,
        ).scale(0.92)
        no_llm_prediction.move_to(NO_LLM_PREDICTION_POS)
        no_llm_caption = txt("GNN-only prediction", 12, MUTED).next_to(
            no_llm_prediction, DOWN, buff=0.16
        )
        step3_inner_arrows = VGroup(
            small_arrow(fusion_inputs.get_left(), refiner.get_right(), color=MUTED, stroke_width=1.7, buff=0.14),
            small_arrow(refiner.get_left(), refined.get_right(), color=MUTED, stroke_width=1.7, buff=0.14),
        )

        # Un-routed nodes bypass the LLM entirely: the arrow lands in the empty
        # left compartment rather than in the refiner's input row.
        skip_arrow = _corner_arrow(
            [
                tuple(router.get_bottom()),
                (router.get_center()[0], CORRIDOR_Y, 0.0),
                (NO_LLM_X + 0.55, CORRIDOR_Y, 0.0),
                (NO_LLM_X + 0.55, step3_c[1] + step3_h / 2 - 0.10, 0.0),
            ],
            color=MUTED, stroke_width=2.0, tip="down",
        )
        # Labels sit beside their arrow's vertical segment, not centered on
        # it -- centering put the line through the text (it runs the full
        # height from the box above down to CORRIDOR_Y).
        skip_label = VGroup(
            txt("KEEP GNN", 12, MUTED, BOLD), mt(r"v\notin R", 16, MUTED),
        ).arrange(RIGHT, buff=0.10)
        skip_label.move_to([router.get_center()[0], CORRIDOR_Y + 0.30, 0.0])
        skip_label.shift(LEFT * (skip_label.width / 2 + 0.18))

        # One straight drop, not a dog-leg: the strips sit right of Z_L(A)'s
        # axis, so the line runs just right of it and still starts well
        # inside the strips' own width.
        llm_arrow_x = llm_side.get_center()[0] + LLM_ARROW_DX
        llm_arrow = _corner_arrow(
            [
                (llm_arrow_x, strips.get_bottom()[1] - LLM_ARROW_GAP, 0.0),
                (llm_arrow_x, llm_side.get_top()[1] + LLM_ARROW_GAP, 0.0),
            ],
            color=MUTED, stroke_width=2.0, tip="down",
        )

        with self.voiceover(
            text="Bước ba: bộ tinh chỉnh kết hợp véc-tơ biểu diễn của gờ nờ nờ với véc-tơ biểu diễn của lờ lờ mờ để tạo ra "
            "một dự đoán đã được tinh chỉnh."
        ) as tracker:
            self.play(
                Create(step3_box), FadeIn(step3_title),
                Create(no_llm_divider), FadeIn(no_llm_label),
                run_time=0.55,
            )
            self.play(
                Create(skip_arrow), FadeIn(skip_label),
                Create(llm_arrow),
                run_time=0.55,
            )
            self.play(
                FadeIn(no_llm_prediction, shift=UP * 0.06), FadeIn(no_llm_caption),
                run_time=0.45,
            )
            self.play(
                LaggedStart(FadeIn(gnn_side, shift=UP * 0.06), FadeIn(llm_side, shift=UP * 0.06), lag_ratio=0.25),
                run_time=0.62,
            )
            self.play(GrowArrow(step3_inner_arrows[0]), FadeIn(refiner), run_time=0.50)
            self.play(GrowArrow(step3_inner_arrows[1]), FadeIn(refined, shift=LEFT * 0.08), run_time=0.55)
            self.play(Write(step3_equation), run_time=0.55)
        self.wait(0.5)

class S4_15_RouterScore(GlanceMovingScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        _clear_except(self)
        _banner(self)
        _show_header(self, 3, "Router: from feature vector to routing score")

        feature = mt(r"f_A", 50).move_to(LEFT * 4.75)
        router = router_glyph(radius=0.74).move_to(ORIGIN)
        router_name = txt("ROUTER", 22, INK, BOLD).next_to(router, UP, buff=0.28)
        score = mt(r"a_A", 50).move_to(RIGHT * 4.75)
        arrows = VGroup(
            small_arrow(feature.get_right(), router.get_left(), stroke_width=2.4),
            small_arrow(router.get_right(), score.get_left(), stroke_width=2.4),
        )
        with self.voiceover(
            text="Bây giờ ta đi vào chi tiết bước một. Đặc trưng định tuyến ép phẩy a "
            "được đưa vào một bộ định tuyến rất nhẹ."
        ) as tracker:
            self.play(Write(feature), run_time=0.32)

        equation = mt(r"a_A=\pi(f_A)=\sigma(w^\top f_A)", 47).move_to(DOWN * 1.25)
        with self.voiceover(
            text="Bộ định tuyến gồm một lớp tuyến tính và hàm xích-moi, tạo ra điểm định tuyến a phẩy a nằm trong "
            "khoảng từ không đến một."
        ) as tracker:
            self.play(GrowArrow(arrows[0]), FadeIn(router), FadeIn(router_name), run_time=0.58)
            self.play(GrowArrow(arrows[1]), Write(score), run_time=0.52)
            self.play(TransformFromCopy(VGroup(feature, router, score), equation), run_time=0.78)

        score_states = [r"a_D=0.25", r"a_E=0.81", r"a_B=0.12", r"a_A=0.86"]
        with self.voiceover(
            text="điểm cao cho thấy nót a có khả năng nhận được lợi ích khi sử dụng lờ lờ mờ. điểm thấp "
            "cho thấy dự đoán hiện tại của gờ nờ nờ có thể đã đủ tốt."
        ) as tracker:
            current_score = mt(score_states[0], 37).move_to(DOWN * 2.05)
            self.play(Write(current_score), run_time=0.32)
            for state in score_states[1:]:
                next_score = mt(state, 37).move_to(current_score)
                self.play(TransformMatchingTex(current_score, next_score), run_time=0.36)
                current_score = next_score

        warning = txt(
            "Routing score is not a class probability", 19, MUTED, BOLD,
        ).move_to(RIGHT * 4.15 + UP * 1.75)
        with self.voiceover(
            text="Cần phân biệt rằng đây không phải xác suất lớp. Nó chỉ biểu diễn mức độ nên gửi nót "
            "sang nhánh lờ lờ mờ."
        ) as tracker:
            self.play(FadeIn(warning, shift=UP * 0.08), run_time=0.40)
        self.wait(0.8)


class S4_16_TopK(GlanceMovingScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        _clear_except(self)
        _banner(self)
        _show_header(self, 4, "Rank routing scores and select Top-K")

        data = [("D", 0.25), ("A", 0.86), ("B", 0.12), ("E", 0.81), ("C", 0.74)]
        rows = {label: score_row(label, value) for label, value in data}
        initial_rows = VGroup(*rows.values()).arrange(DOWN, buff=0.17).move_to(LEFT * 2.35)
        with self.voiceover(text="Gờ lans không sử dụng một ngưỡng cố định cho từng nót.") as tracker:
            self.play(
                LaggedStart(*[FadeIn(row, shift=RIGHT * 0.08) for row in initial_rows], lag_ratio=0.10),
                run_time=0.85,
            )
        sorted_data = sorted(data, key=lambda item: item[1], reverse=True)
        targets = [LEFT * 2.35 + UP * (1.35 - 0.77 * index) for index in range(len(sorted_data))]
        with self.voiceover(
            text="Thay vào đó, hệ thống xếp hạng điểm định tuyến của tất cả nót trong bát."
        ) as tracker:
            self.play(
                *[rows[label].animate.move_to(target) for (label, _), target in zip(sorted_data, targets)],
                run_time=1.0,
            )

        third_bottom = rows[sorted_data[2][0]].get_bottom()[1]
        fourth_top = rows[sorted_data[3][0]].get_top()[1]
        cutoff_y = (third_bottom + fourth_top) / 2
        top_line = Line(LEFT * 4.05, LEFT * 0.65, color=INK, stroke_width=1.8)
        top_line.set_y(cutoff_y)
        top_label = txt("TOP-3", 20, INK, BOLD).next_to(top_line, RIGHT, buff=0.22)
        with self.voiceover(
            text="Ví dụ, các nót a, e và xê có ba điểm cao nhất nên được chọn vào tốp ba."
        ) as tracker:
            self.play(Create(top_line), FadeIn(top_label), run_time=0.48)
            for label, _ in sorted_data[3:]:
                self.play(rows[label].animate.set_opacity(0.38), run_time=0.20)

        topk_equation = fit_width(
            mt(r"R=\operatorname{TopK}\!\left(\{a_v:v\in B\}\right)", 41),
            6.2,
        ).move_to(RIGHT * 3.25 + UP * 0.80)
        with self.voiceover(text="Chỉ đúng ca nót được gửi sang lờ lờ mờ.") as tracker:
            self.play(Write(topk_equation), run_time=0.62)
        selected = mt(r"A\in R\Longrightarrow r_A=1", 39).move_to(RIGHT * 3.25 + DOWN * 0.45)
        budget = VGroup(
            txt("SELECT EXACTLY K NODES", 22, INK, BOLD),
            txt("Fixed LLM compute budget", 20, MUTED),
        ).arrange(DOWN, buff=0.12).move_to(RIGHT * 3.25 + DOWN * 1.65)
        with self.voiceover(
            text="Nhờ vậy, gờ lans kiểm soát chính xác ngân sách tính toán và tránh tình trạng số lần gọi "
            "lờ lờ mờ tăng ngoài dự kiến."
        ) as tracker:
            self.play(Write(selected), FadeIn(budget), run_time=0.62)
            self.play(
                Create(SurroundingRectangle(rows["A"], color=INK, buff=0.07, stroke_width=2)),
                run_time=0.40,
            )
        self.wait(0.8)


class S4_17_TwoFlows(GlanceMovingScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        _banner(self)
        header17 = _show_header(self, 5, "Router branches into two inference flows")
        (router, router_label, with_node, without_node,
         with_title, without_title, branch_arrows, overview) = _router_overview(self)

        with self.voiceover(text="Sau bước tốp ca, quy trình được chia thành hai nhánh rõ ràng.") as tracker:
            self.play(FadeIn(router), FadeIn(router_label), run_time=0.45)
        with self.voiceover(
            text="Nhánh thứ nhất dành cho những nót thuộc tập định tuyến rời, tức là các nót được sử dụng "
            "lờ lờ mờ. Nhánh thứ hai dành cho những nót không thuộc rời."
        ) as tracker:
            self.play(
                LaggedStart(*[GrowArrow(arrow) for arrow in branch_arrows], lag_ratio=0.16),
                FadeIn(with_node), FadeIn(without_node),
                FadeIn(with_title), FadeIn(without_title),
                run_time=0.82,
            )
        with self.voiceover(
            text="Việc tách hai nhánh này là cơ sở giúp gờ lans vừa tận dụng sức mạnh ngữ nghĩa của lờ lờ mờ, "
            "vừa duy trì chi phí xử lý hợp lý."
        ):
            pass
        self.wait(0.55)


class S4_18_WithoutLLM(GlanceMovingScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        _banner(self)
        header17 = step_header(5, "Router branches into two inference flows")
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

        highlight_ring = Circle(
            radius=without_node.width / 2 + 0.14, stroke_color=INK, stroke_width=2.6,
        ).move_to(without_node)
        with self.voiceover(text="Trước tiên là nhánh đơn giản hơn.") as tracker:
            self.play(Create(highlight_ring), run_time=0.35)
            self.play(FadeOut(header17), run_time=0.25)
            self.play(
                self.camera.frame.animate.move_to(flow_center).set(width=12.0),
                overview.animate.set_opacity(0.0),
                FadeOut(highlight_ring),
                run_time=0.90,
            )
            self.play(FadeIn(detail_node), FadeIn(detail_title), run_time=0.32)

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
            text="Nếu một nót không được định tuyến, gờ lans bỏ qua toàn bộ bước tạo câu lệnh, gọi lờ lờ mờ và "
            "bộ tinh chỉnh. Phân phối cuối cùng của nót được giữ nguyên bằng bê hắc phẩy vê, tức dự đoán "
            "ban đầu của gờ nờ nờ."
        ) as tracker:
            self.play(GrowArrow(direct_arrows[0]), FadeIn(gnn_prediction), run_time=0.55)
            self.play(GrowArrow(direct_arrows[1]), Write(decision), run_time=0.58)
        with self.voiceover(
            text="Sau đó, hệ thống lấy lớp có xác suất lớn nhất. Nhờ vậy, các nót dễ không phải chịu "
            "thêm chi phí và cũng không bị lờ lờ mờ làm thay đổi một dự đoán vốn đã chính xác."
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
        header17 = step_header(5, "Router branches into two inference flows")
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

        highlight_ring = Circle(
            radius=with_node.width / 2 + 0.14, stroke_color=INK, stroke_width=2.6,
        ).move_to(with_node)
        with self.voiceover(
            text="Với nót a được định tuyến, gờ lans khai thác văn bản ở ba mức ngữ cảnh."
        ) as tracker:
            self.play(Create(highlight_ring), run_time=0.35)
            self.play(FadeOut(header17), run_time=0.25)
            self.play(
                self.camera.frame.animate.move_to(with_node).set(width=9.2),
                overview.animate.set_opacity(0.0),
                FadeOut(highlight_ring),
                run_time=0.90,
            )

        with self.voiceover(text="Mức đầu tiên là văn bản của nót trung tâm, chỉ chứa nội dung của chính nót a.") as tracker:
            self.play(GrowFromCenter(center_A), run_time=0.38)

        with self.voiceover(
            text="Mức thứ hai là 1-hop ngữ cảnh, bổ sung nội dung từ các nót trích dẫn trực tiếp."
        ) as tracker:
            self.play(
                Create(ring_1), Create(hop1_edges),
                LaggedStart(*[FadeIn(neighbor) for neighbor in hop1_nodes], lag_ratio=0.10),
                run_time=0.72,
            )
            self.bring_to_front(center_A, hop1_nodes)

        with self.voiceover(
            text="Mức cuối cùng là ngữ cảnh hai bước, cung cấp ngữ cảnh rộng hơn từ các nót cách a hai cạnh."
        ) as tracker:
            self.play(
                Create(ring_2), Create(hop2_edges),
                LaggedStart(*[FadeIn(neighbor) for neighbor in hop2_nodes], lag_ratio=0.10),
                run_time=0.82,
            )
            self.bring_to_front(center_A, hop1_nodes, hop2_nodes)

        context_cards = VGroup(
            equation_card(r"P_0(A)=t_A", "0-hop · ego text", width=4.25, height=0.88, emphasized=True),
            equation_card(r"P_1(A)=\operatorname{Serialize}(t_A,N_1(A))", "1-hop · direct citations", width=4.25, height=0.88),
            equation_card(r"P_2(A)=\operatorname{Serialize}(t_A,N_2(A))", "2-hop · wider context", width=4.25, height=0.88),
        ).arrange(DOWN, buff=0.28).move_to(RIGHT * 3.95 + UP * 1.52)
        with self.voiceover(text="Ba mức được xử lý riêng thay vì gộp tất cả thành một câu lệnh rất dài.") as tracker:
            self.play(
                LaggedStart(*[FadeIn(card, shift=LEFT * 0.08) for card in context_cards], lag_ratio=0.18),
                run_time=0.92,
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
        header = _show_header(self, 6, "Shared LLM encoder: ego embedding")

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

        with self.voiceover(text="câu lệnh đầu tiên chỉ chứa văn bản của nót trung tâm của nót a.") as tracker:
            self.play(Write(equation), run_time=0.50)
            self.play(FadeIn(prompt, shift=DOWN * 0.08), run_time=0.42)
        with self.voiceover(
            text="câu lệnh này được đưa vào quy en ba em-bét tám bi, đóng vai trò dùng chung véc-tơ biểu diễn bộ mã hóa."
        ) as tracker:
            self.play(GrowArrow(prompt_arrow), FadeIn(llm, shift=DOWN * 0.08), run_time=0.55)
            self.play(FadeIn(details, shift=LEFT * 0.08), run_time=0.48)
        with self.voiceover(
            text="Đầu ra không phải là một câu trả lời hay nhãn lớp, mà là véc-tơ biểu diễn dét lờ phẩy không của a."
        ) as tracker:
            self.play(GrowArrow(output_arrow), FadeIn(output, shift=DOWN * 0.08), run_time=0.66)

        legend = txt("LIGHT AMBER · EGO CONTEXT EMBEDDING", 19, C_LLM_LIGHT, BOLD).next_to(output, DOWN, buff=0.20)
        with self.voiceover(
            text="véc-tơ biểu diễn này biểu diễn thông tin ngữ nghĩa từ chính nội dung của nót a."
        ) as tracker:
            self.play(FadeIn(legend), run_time=0.34)
        self.wait(0.5)


class S4_24_OneHopEmbedding(GlanceMovingScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        _banner(self)
        header, equation, prompt, llm, output, details, prompt_arrow, output_arrow, legend = _llm_stage(self, 0)
        self.add(header, equation, prompt, llm, output, details, prompt_arrow, output_arrow, legend)

        header_1 = step_header(7, "Shared LLM encoder: 1-hop embedding")
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
            text="Ở bước tiếp theo, câu lệnh được mở rộng bằng nội dung của các nót hàng xóm trực tiếp. "
            "Câu lệnh mới vẫn đi qua cùng một bộ mã hóa lờ lờ mờ, chứ không phải một mô hình khác. Đầu ra là "
            "dét lờ phẩy một của a. véc-tơ biểu diễn này bổ sung bối cảnh từ các bài báo có quan hệ trực tiếp "
            "với nót a."
        ) as tracker:
            self.play(
                Transform(header, header_1),
                TransformMatchingTex(equation, equation_1),
                Transform(prompt, prompt_1),
                Transform(output, output_1),
                ReplacementTransform(details, details_1),
                Transform(legend, legend_1),
                output_arrow.animate.set_color(C_LLM),
                run_time=0.88,
            )
        self.wait(0.5)


class S4_25_TwoHopEmbedding(GlanceMovingScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        _banner(self)
        header, equation, prompt, llm, output, details, prompt_arrow, output_arrow, legend = _llm_stage(self, 1)
        self.add(header, equation, prompt, llm, output, details, prompt_arrow, output_arrow, legend)

        header_2 = step_header(8, "Shared LLM encoder: 2-hop embedding")
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
            text="Tương tự, câu lệnh thứ ba đưa thêm ngữ cảnh ở khoảng cách hai bước. Nó giúp mô hình quan "
            "sát một vùng rộng hơn của đồ thị trích dẫn và nhận biết chủ đề tổng quát xung quanh nót a. "
            "câu lệnh tiếp tục sử dụng bộ mã hóa lờ lờ mờ dùng chung và tạo véc-tơ biểu diễn dét lờ phẩy hai của a. Như vậy, "
            "một bộ mã hóa được tái sử dụng cho ba phiên bản câu lệnh khác nhau."
        ) as tracker:
            self.play(
                Transform(header, header_2),
                TransformMatchingTex(equation, equation_2),
                Transform(prompt, prompt_2),
                Transform(output, output_2),
                ReplacementTransform(details, details_2),
                Transform(legend, legend_2),
                output_arrow.animate.set_color(C_LLM_DEEP),
                run_time=0.88,
            )
        self.wait(0.5)


class S4_26_MergeEmbeddings(GlanceMovingScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        _banner(self)
        header26 = _show_header(self, 9, "Merge the three LLM embeddings")

        z0 = named_embedding_strip(r"z_{L,0}(A)", C_LLM_LIGHT, n=7, cell_size=0.25)
        z1 = named_embedding_strip(r"z_{L,1}(A)", C_LLM, n=7, cell_size=0.25)
        z2 = named_embedding_strip(r"z_{L,2}(A)", C_LLM_DEEP, n=7, cell_size=0.25)
        source_row = VGroup(z0, z1, z2).arrange(RIGHT, buff=0.90).move_to(UP * 0.25)
        with self.voiceover(text="Ba véc-tơ biểu diễn vừa tạo được nối lại với nhau.") as tracker:
            self.play(
                LaggedStart(*[FadeIn(item, shift=UP * 0.08) for item in source_row], lag_ratio=0.12),
                run_time=0.82,
            )

        z0_cells, z1_cells, z2_cells = z0[1], z1[1], z2[1]
        individual_labels = VGroup(z0[0], z1[0], z2[0])
        close_guides = VGroup(
            z0_cells.copy(), z1_cells.copy(), z2_cells.copy(),
        ).arrange(RIGHT, buff=0.055).scale(1.18).move_to(UP * 0.25)
        moving_parts = [z0_cells, z1_cells, z2_cells]
        with self.voiceover(
            text="Kết quả là dét lờ a, đại diện cho toàn bộ thông tin ngữ nghĩa mà lờ lờ mờ thu được."
        ) as tracker:
            self.play(
                FadeOut(individual_labels, shift=UP * 0.06),
                *[
                    part.animate.move_to(guide.get_center()).scale(1.18)
                    for part, guide in zip(moving_parts, close_guides)
                ],
                run_time=0.92,
            )

        z_l_row = VGroup(z0_cells, z1_cells, z2_cells)
        merged_label = mt(r"Z_L(A)", 39).next_to(z_l_row, UP, buff=0.28)
        with self.voiceover(
            text="véc-tơ này giữ riêng ba thành phần: nội dung của chính nót, ngữ cảnh trực tiếp và "
            "ngữ cảnh xa hơn."
        ) as tracker:
            self.play(FadeIn(merged_label, shift=UP * 0.08), run_time=0.42)
        z_l_visual = VGroup(merged_label, z_l_row)

        merge_equation = fit_width(
            mt(r"Z_L(A)=\left[z_{L,0}(A)\Vert z_{L,1}(A)\Vert z_{L,2}(A)\right]", 39), 11.3,
        ).move_to(DOWN * 1.65)
        with self.voiceover(
            text="lờ lờ mờ biểu diễn vẫn chưa phải là kết quả phân loại cuối cùng. Nó sẽ được kết hợp "
            "tiếp với biểu diễn đồ thị từ gờ nờ nờ."
        ) as tracker:
            self.play(Write(merge_equation), run_time=0.68)
        self.wait(0.78)


class S4_27_FusedRepresentation(GlanceMovingScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        _banner(self)
        (header26, z0_cells, z1_cells, z2_cells,
         merged_label, z_l_visual, merge_equation) = _merged_llm_embedding(self)
        self.add(header26, z_l_visual, merge_equation)

        header27 = step_header(10, "The fused representation combines structure and semantics")
        z_g = named_embedding_strip(r"z_G(A)", C_GNN, n=8, cell_size=0.26).scale(0.85)
        z_g.move_to(LEFT * 3.25 + UP * 0.22)
        with self.voiceover(
            text="véc-tơ biểu diễn dét gờ a từ gờ nờ nờ chứa thông tin về đặc trưng và cấu trúc đồ thị."
        ) as tracker:
            self.play(Transform(header26, header27), FadeOut(merge_equation), run_time=0.58)
            self.play(z_l_visual.animate.scale(0.72).move_to(RIGHT * 3.25 + UP * 0.22), run_time=0.72)
            self.play(FadeIn(z_g, shift=RIGHT * 0.35), run_time=0.52)

        fusion_parts = [z_g[1], z0_cells, z1_cells, z2_cells]
        fusion_guides = VGroup(*[part.copy() for part in fusion_parts])
        fusion_guides.arrange(RIGHT, buff=0.055).scale(1.16).move_to(UP * 0.20)
        fusion_label = mt(r"[z_G(A)\Vert Z_L(A)]", 39).next_to(fusion_guides, UP, buff=0.28)
        with self.voiceover(
            text="Trong khi đó, dét lờ a chứa thông tin ngữ nghĩa được trích từ ba mức câu lệnh. gờ lans "
            "gờ lans nối hai véc-tơ này thành một biểu diễn hợp nhất."
        ) as tracker:
            self.play(
                FadeOut(VGroup(z_g[0], merged_label), shift=UP * 0.05),
                *[
                    part.animate.move_to(guide.get_center()).scale(1.16)
                    for part, guide in zip(fusion_parts, fusion_guides)
                ],
                FadeIn(fusion_label, shift=UP * 0.08),
                run_time=0.94,
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
            text="Có thể hiểu phần bên trái đại diện cho thông tin cấu trúc từ gờ nờ nờ, còn ba phần "
            "bên phải đại diện cho ngữ nghĩa ngữ cảnh từ lờ lờ mờ."
        ) as tracker:
            self.play(FadeIn(left_note), FadeIn(right_note), run_time=0.50)

        with self.voiceover(text="véc-tơ kết hợp này là đầu vào trực tiếp của bộ tinh chỉnh."):
            pass
        self.wait(0.6)


class S4_28_RefinerMLP(GlanceMovingScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        _clear_except(self)
        _banner(self)
        _show_header(self, 11, "Refiner MLP: structure and output")

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
            text="bộ tinh chỉnh là một mờ lờ bê có nhiệm vụ kết hợp hai nguồn bằng chứng."
        ) as tracker:
            self.play(Write(equation), run_time=0.60)
            self.play(FadeIn(fusion_input, shift=DOWN * 0.06), run_time=0.42)

        with self.voiceover(
            text="Biểu diễn hợp nhất lần lượt đi qua các lớp tuyến tính, ri-lu, đờ-róp-ao và lớp đầu ra."
        ) as tracker:
            self.play(
                GrowArrow(
                    small_arrow(
                        fusion_input.get_bottom(),
                        network.get_top(),
                        buff=0.12,
                    )
                ),
                run_time=0.40,
            )
            self.play(
                LaggedStart(
                    *[FadeIn(layer, scale=0.85) for layer in layers],
                    lag_ratio=0.12,
                ),
                run_time=0.75,
            )
            self.play(
                LaggedStart(
                    *[Create(edge) for edge in edges],
                    lag_ratio=0.01,
                ),
                run_time=0.60,
            )
            self.bring_to_front(*layers)

            stage_names = ["Input", "Linear + ReLU", "Dropout + Linear", "Softmax"]
            self.play(
                FadeIn(stage_label),
                layers[0].animate.set_stroke(INK).set_fill(INK, opacity=1.0),
                run_time=0.36,
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
                    run_time=0.42,
                )

        with self.voiceover(text="Cuối cùng, sóp mác tạo ra phân phối lớp mới bê xê phẩy a.") as tracker:
            self.play(
                GrowArrow(
                    small_arrow(
                        network.get_bottom(),
                        output_symbol.get_top(),
                        buff=0.10,
                    )
                ),
                Write(output_symbol),
                run_time=0.55,
            )

        self.say(
            "bộ tinh chỉnh không thay thế gờ nờ nờ hoặc lờ lờ mờ. Nó học cách cân bằng thông tin cấu trúc từ gờ nờ nờ "
            "với thông tin ngữ nghĩa từ lờ lờ mờ để tạo ra dự đoán phù hợp hơn cho được định tuyến nót."
        )
        self.wait(0.8)


class S4_29_RefinedDistribution(GlanceMovingScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        _clear_except(self)
        _banner(self)
        _show_header(self, 12, "LLM context refines the class distribution")

        transition_equation = mt(
            r"p_{H,A}\xrightarrow{\ +\,Z_L(A)\ }p_{C,A}", 45,
        ).move_to(UP * 1.92)

        # Keep both distributions on one centered baseline and preserve a clear
        # transition corridor between the two panels. Dropped closer to the
        # frame's optical centre -- the original placement left dead space
        # under the panels.
        before = probability_chart(
            [0.45, 0.40, 0.15], r"p_{H,A}", CLASS_NAMES, width=6.15,
        ).scale(0.79).move_to(LEFT * 3.28 + DOWN * 0.35)
        after = probability_chart(
            [0.15, 0.80, 0.05], r"p_{C,A}", CLASS_NAMES, width=6.15,
        ).scale(0.79).move_to(RIGHT * 3.28 + DOWN * 0.35)

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
            text="Trước khi sử dụng lờ lờ mờ, gờ nờ nờ tạo phân phối ban đầu là không chấm bốn năm, không chấm bốn không và không chấm một năm. Phân phối "
            "này chưa thể hiện sự khác biệt rõ ràng giữa hai lớp đầu tiên."
        ) as tracker:
            self.play(Write(transition_equation), run_time=0.48)
            self.play(FadeIn(before, shift=UP * 0.08), FadeIn(before_note), run_time=0.62)
        with self.voiceover(
            text="Sau khi bổ sung lờ lờ mờ ngữ cảnh và đi qua bộ tinh chỉnh, phân phối chuyển thành không chấm một năm, không chấm tám không "
            "và không chấm không năm."
        ) as tracker:
            self.play(GrowArrow(comparison_arrow), run_time=0.38)
            self.play(FadeIn(after, shift=UP * 0.08), FadeIn(after_note), run_time=0.68)
        highlight = SurroundingRectangle(
            after[1][1][1], color=INK, buff=0.08, stroke_width=2,
        )
        with self.voiceover(text="Xác suất tập trung mạnh hơn vào lớp khai phá đồ thị.") as tracker:
            self.play(Create(highlight), run_time=0.40)
        with self.voiceover(
            text="Ví dụ này minh họa cách ngữ cảnh văn bản có thể giúp điều chỉnh một dự đoán còn "
            "chưa chắc chắn của gờ nờ nờ."
        ):
            pass
        self.wait(0.6)


class S4_30_FinalPrediction(GlanceMovingScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        _clear_except(self)
        _banner(self)
        _show_header(self, 13, "Final prediction and the two GLANCE flows")

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
            text="Cuối cùng, gờ lans xác định phân phối được sử dụng tùy theo kết quả định tuyến."
        ) as tracker:
            self.play(Write(final_equation), run_time=0.82)

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
            text="Nếu nót thuộc tập rời, hệ thống sử dụng phân phối đã tinh chỉnh là bê xê phẩy vê. Nếu nót "
            "không thuộc rời, hệ thống giữ nguyên phân phối gờ nờ nờ là bê hắc phẩy vê."
        ) as tracker:
            self.play(
                FadeIn(with_llm, shift=UP * 0.08),
                FadeIn(without_llm, shift=UP * 0.08),
                run_time=0.70,
            )

        result = VGroup(
            avatar_node("A", target=True, radius=0.29),
            mt(r"\longrightarrow", 35),
            txt("Graph Mining", 31, INK, BOLD),
        ).arrange(RIGHT, buff=0.28).move_to(DOWN * 2.00)
        with self.voiceover(
            text="Với nót a trong ví dụ, a được định tuyến nên sử dụng kết quả của bộ tinh chỉnh. Lớp có xác "
            "suất lớn nhất là khai phá đồ thị, vì vậy đây là nhãn cuối cùng của nót a."
        ) as tracker:
            self.play(FadeIn(result, shift=UP * 0.08), run_time=0.50)

        self.say(
            "Tóm lại, gờ lans có thể được mô tả bằng ba ý chính: gờ nờ nờ được sử dụng trước để xử lý "
            "toàn bộ đồ thị. bộ định tuyến lựa chọn những nót thực sự cần hỗ trợ. Và lờ lờ mờ chỉ được gọi theo "
            "nhu cầu để bổ sung thông tin ngữ nghĩa cho các trường hợp khó. Thiết kế này giúp gờ lans "
            "kết hợp được khả năng khai thác cấu trúc của gờ nờ nờ với khả năng hiểu văn bản của lờ lờ mờ, "
            "nhưng vẫn kiểm soát được chi phí tính toán."
        )

        self.wait(0.6)
        # Required section-closing transition line, per TASK.md.
        self.say(
            "bộ định tuyến không khả vi. Vậy huấn luyện nó kiểu gì, và có thật sự hiệu quả?"
        )
        self.say(
            "bộ định tuyến không khả vi. Vậy huấn luyện nó kiểu gì, và có thật sự hiệu quả?"
        )
