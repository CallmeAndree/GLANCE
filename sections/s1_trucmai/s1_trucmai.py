"""GLANCE Task 1: Core Problem (Rebuilt v3)"""

import os
import sys
import pathlib
import textwrap
from contextlib import contextmanager

from manim import *
from manim_voiceover import VoiceoverScene

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
import glance_style as gs

USE_VOICEOVER = os.environ.get("S1_USE_VOICEOVER", "1").strip().lower() not in {"0", "false", "no"}
# Giọng đọc dùng API của nhóm, cấu hình trong .env ở gốc repo. Xem README.md và
# plan.md ở gốc: đó là tài liệu chuẩn. Section 1 không tự chọn service riêng nữa.
SHOW_VISUAL_SUBTITLES = os.environ.get("S1_VISUAL_SUBTITLES", "0").strip().lower() in {"1", "true", "yes"}

BG = gs.BG
BRIGHT = gs.C_HIGHLIGHT
LIGHT = gs.INK
MID = gs.MUTED
DIM = gs.C_EDGE
DARK = gs.C_EDGE
INK = gs.INK
PANEL_2 = gs.BG

def t(text, size=26, color=LIGHT, weight=NORMAL, **kwargs):
    return gs.txt(text, size=size, color=color, weight=weight, **kwargs)

def mt(formula, size=42, color=LIGHT):
    """Giữ lại làm lớp mỏng vì mặc định size khác bản dùng chung (42 so với 32).

    Ruột đã chuyển sang gs.mt() để chỉ còn một nơi dựng MathTex. LIGHT ở đây
    chính là gs.INK nên màu không đổi.
    """
    return gs.mt(formula, size=size, color=color)

def fit(mobject, max_width=12.2, max_height=None):
    if mobject.width > max_width:
        mobject.scale_to_fit_width(max_width)
    if max_height is not None and mobject.height > max_height:
        mobject.scale_to_fit_height(max_height)
    return mobject

def panel(width, height, stroke=DIM, fill=PANEL_2, opacity=0.64):
    return RoundedRectangle(
        width=width,
        height=height,
        corner_radius=0.12,
        stroke_color=stroke,
        stroke_width=1.6,
        fill_color=fill,
        fill_opacity=opacity,
    )

def module(title, subtitle="", width=2.45, height=1.05, emphasized=False):
    stroke = BRIGHT if emphasized else DIM
    box = panel(width, height, stroke=stroke, fill=BG, opacity=0.88)
    title_m = fit(t(title, 21, BRIGHT if emphasized else LIGHT, BOLD), width - 0.28)
    parts = VGroup(title_m)
    if subtitle:
        parts.add(fit(t(subtitle, 14, MID), width - 0.28))
    parts.arrange(DOWN, buff=0.07).move_to(box)
    return VGroup(box, parts)

def small_arrow(start, end, color=LIGHT, stroke_width=2.0, buff=0.10, dashed=False):
    if dashed:
        return DashedLine(start, end, dash_length=0.09, color=color, stroke_width=stroke_width)
    return Arrow(start, end, buff=buff, color=color, stroke_width=stroke_width, tip_length=0.11)

def node(label="", target=False, radius=0.20):
    circle = Circle(
        radius=radius,
        stroke_color=BRIGHT if target else LIGHT,
        stroke_width=2.6 if target else 1.5,
        fill_color=BRIGHT if target else BG,
        fill_opacity=0.22 if target else 1,
    )
    
    parts = VGroup()
    if target:
        bg_circle = Circle(radius=radius, fill_color=BG, fill_opacity=1, stroke_width=0)
        parts.add(bg_circle)
    parts.add(circle)
    
    if label:
        label_m = fit(t(str(label), max(11, int(radius * 60)), LIGHT, BOLD), radius * 1.2)
        label_m.move_to(circle)
        parts.add(label_m)
        
    return parts

def doc_icon(title="Document", lines=None, width=3.0, height=2.0, emphasized=False):
    lines = lines or ["Title and abstract", "Methods and evidence", "Topic and context"]
    box = RoundedRectangle(
        width=width,
        height=height,
        corner_radius=0.08,
        stroke_color=BRIGHT if emphasized else DIM,
        stroke_width=1.8,
        fill_color=BG,
        fill_opacity=0.92,
    )
    fold = Polygon(
        box.get_corner(UR) + LEFT * 0.34,
        box.get_corner(UR) + DOWN * 0.34,
        box.get_corner(UR),
        stroke_color=DIM,
        fill_color=BG,
        fill_opacity=1,
    )
    heading = fit(t(title, 20, BRIGHT if emphasized else LIGHT, BOLD), width - 0.48)
    body = VGroup(*[fit(t(line, 16, LIGHT), width - 0.52) for line in lines])
    body.arrange(DOWN, aligned_edge=LEFT, buff=0.14)
    content = VGroup(heading, body).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
    content.move_to(box).shift(LEFT * 0.04)
    result = VGroup(box, fold, content)
    result.heading = heading
    result.lines = body
    return result

def custom_feature_vector(label, values, color=BRIGHT, width=3.0, height=0.6):
    """Creates a feature vector representation like [ ▮ ▯ ▮ ▮ ]"""
    cells = VGroup()
    num_cells = len(values)
    cell_width = (width - 0.2) / num_cells
    for val in values:
        rect = Rectangle(width=cell_width, height=height-0.2, stroke_color=DIM, stroke_width=1.5, fill_color=color, fill_opacity=val)
        cells.add(rect)
    cells.arrange(RIGHT, buff=0)
    
    bracket_l = t("[", size=40, color=LIGHT, weight=BOLD)
    bracket_r = t("]", size=40, color=LIGHT, weight=BOLD)
    
    vector = VGroup(bracket_l, cells, bracket_r).arrange(RIGHT, buff=0.1)
    label_m = t(label, 18, color, BOLD).next_to(vector, DOWN, buff=0.35)
    
    group = VGroup(vector, label_m)
    group.cells = cells
    return group

def probability_vector(label, values, width=2.8, emphasized_index=None):
    title = t(label, 18, LIGHT, BOLD)
    bar_width = width - 1.0
    rows = VGroup()
    for index, value in enumerate(values):
        track = Line(ORIGIN, RIGHT * bar_width, color=DARK, stroke_width=5)
        fill_color = BRIGHT if index == emphasized_index else MID
        fill = Line(track.get_start(), track.point_from_proportion(value), color=fill_color, stroke_width=5)
        number = t(f"{value:.2f}", 13, LIGHT)
        rows.add(VGroup(VGroup(track, fill), number).arrange(RIGHT, buff=0.09))
    rows.arrange(DOWN, aligned_edge=LEFT, buff=0.11)
    content = VGroup(title, rows).arrange(DOWN, buff=0.14)
    box = panel(width, content.height + 0.34, stroke=DIM, fill=BG, opacity=0.82)
    content.move_to(box)
    return VGroup(box, content)

def cross_mark(size=0.18, color=BRIGHT):
    return VGroup(
        Line(UL, DR, color=color, stroke_width=3),
        Line(DL, UR, color=color, stroke_width=3),
    ).scale(size)

def create_tag_graph(scale=1.0):
    positions = {
        "A": ORIGIN,
        "B": LEFT * 2.25 + UP * 1.35,
        "C": LEFT * 2.60 + DOWN * 0.75,
        "D": LEFT * 0.85 + UP * 2.0,
        "E": LEFT * 0.90 + DOWN * 1.70,
        "F": RIGHT * 1.0 + UP * 1.85,
        "G": RIGHT * 2.45 + UP * 1.05,
        "H": RIGHT * 2.30 + DOWN * 0.65,
        "I": RIGHT * 0.95 + DOWN * 1.85,
    }
    positions = {key: value * scale for key, value in positions.items()}
    pairs = [
        ("A", "B"), ("A", "C"), ("A", "D"), ("A", "E"), ("A", "F"), ("A", "H"), ("A", "I"),
        ("B", "C"), ("B", "D"), ("C", "E"), ("D", "F"), ("F", "G"), ("F", "H"), ("G", "H"), ("H", "I"),
    ]
    edges = VGroup(*[
        Line(positions[u], positions[v], buff=0.19 * scale, color=DARK, stroke_width=1.6)
        for u, v in pairs
    ])
    nodes = {
        key: node(key, target=key == "A", radius=(0.26 if key == "A" else 0.18) * scale).move_to(pos)
        for key, pos in positions.items()
    }
    nodes_vgroup = VGroup(*nodes.values()).set_z_index(5)
    graph = VGroup(edges, nodes_vgroup)
    graph.edges = edges
    graph.nodes = nodes
    return graph

def create_target_neighborhood(kind="clean", label="A", scale=1.0):
    target = node(label, target=True, radius=0.28 * scale)
    positions = [UP * 1.35, UL * 1.15, LEFT * 1.55, DL * 1.10, DOWN * 1.35, DR * 1.10, RIGHT * 1.55, UR * 1.15]
    positions = [p * scale for p in positions]
    neighbors = VGroup()
    for index, pos in enumerate(positions):
        conflicting = kind == "noisy" and index in {1, 2, 5, 7}
        shape = Square(side_length=0.32 * scale).rotate(PI / 4) if conflicting else Circle(radius=0.17 * scale)
        shape.set_stroke(LIGHT, 1.6).set_fill(BG, 1).move_to(pos)
        neighbors.add(shape)
    edges = VGroup(*[
        (DashedLine if kind == "noisy" and index in {1, 5} else Line)(
            target.get_center(), neighbor.get_center(), buff=0.26 * scale, color=DARK, stroke_width=1.6
        )
        for index, neighbor in enumerate(neighbors)
    ])
    target.set_z_index(5)
    group = VGroup(edges, neighbors, target)
    group.edges = edges
    group.neighbors = neighbors
    group.target = target
    return group

def create_message_vector(start, end, color=BRIGHT, dashed=False):
    arrow = Arrow(start=start, end=end, color=color, buff=0.35, max_stroke_width_to_length_ratio=0, max_tip_length_to_length_ratio=0.15)
    arrow.set_z_index(-1)
    if dashed:
        arrow = DashedVMobject(arrow, num_dashes=15)
        arrow.set_z_index(-1)
    return arrow

def create_text_document(title, lines, width=4.0, height=2.35, emphasized=False):
    return doc_icon(title, lines, width=width, height=height, emphasized=emphasized)

def highlight_keywords(document, indices):
    return AnimationGroup(*[
        document.lines[index].animate.set_color(BRIGHT).scale(1.05)
        for index in indices
    ], lag_ratio=0.18)


class Task1GLANCERebuilt(VoiceoverScene, MovingCameraScene):
    # Bộ chọn giọng dùng chung đọc ba thuộc tính này, giữ đúng mặc định của
    # GlanceScene để section 1 ra cùng giọng với phần còn lại của video.
    voice_lang = "vi"
    azure_voice = "en-US-AvaMultilingualNeural"
    _multilingual = False

    def setup(self):
        MovingCameraScene.setup(self)
        VoiceoverScene.setup(self)
        self.camera.background_color = gs.BG
        self._init_tts()
        self.current_subtitle = None
        # self.debug_safe_zones()  # uncomment during preview debugging

    def _init_tts(self):
        """Dùng chung bộ chọn giọng của cả video (glance_style.GlanceScene).

        Nhóm đã thống nhất backend là timed TTS API, cấu hình trong .env ở gốc
        repo. Chọn backend bằng GLANCE_TTS, không hard-code service ở đây nữa,
        để giọng section 1 khớp với các section còn lại.
        """
        if not USE_VOICEOVER:
            return
        self.set_speech_service(
            gs.GlanceScene.speech_service(self), create_subcaption=True
        )

    def create_subtitle_box(self, text, max_width=12.4): 
        label = Text(text, font=gs.FONT_MAIN, font_size=20, color=WHITE, weight="SEMIBOLD", stroke_width=1, stroke_color=BLACK)
        if label.width > max_width:
            raise ValueError(f"Subtitle cue exceeds max width of {max_width}: '{text}'")
        if "\n" in text:
            raise ValueError(f"Subtitle cue contains a line break: '{text}'")
            
        bg = RoundedRectangle(
            width=label.width + 0.42,
            height=label.height + 0.18,
            corner_radius=0.15,
            fill_color=BLACK,
            fill_opacity=0.6,
            stroke_width=0,
        )
        box = VGroup(bg, label)
        box.move_to(DOWN * 3.66)
        return box

    def debug_safe_zones(self):
        # Header Safe Zone
        header_zone = Rectangle(width=14.22, height=1.5, stroke_color=RED, stroke_width=2, fill_opacity=0).to_edge(UP, buff=0)
        # Subtitle Safe Zone (bottom 15%)
        sub_zone = Rectangle(width=14.22, height=1.2, stroke_color=GREEN, stroke_width=2, fill_opacity=0).to_edge(DOWN, buff=0)
        self.add(header_zone, sub_zone)

    @contextmanager
    def narrated_caption(self, text_segments):
        """
        text_segments: single string or list of strings.
        If list, they are treated as sequential cues for a single voiceover generation.
        We now use manim-voiceover's native subcaption generation to ensure exact 
        word-level synchronization and prevent subtitles from disappearing prematurely.
        """
        if isinstance(text_segments, str):
            text_segments = [text_segments]
            
        full_text = " ".join(text_segments)
        
        if USE_VOICEOVER:
            with self.voiceover(text=full_text) as tracker:
                yield tracker
        else:
            yield None
            self.wait(1.5)

    def stage_punchline(self, mobjects, hold=1.5, animate_last_index=-1):
        overlay = Rectangle(width=25, height=15, fill_color=BLACK, fill_opacity=0.85, stroke_width=0).set_z_index(40)
        punch_group = VGroup(*mobjects).arrange(DOWN, buff=0.4).set_z_index(50)
        
        self.play(FadeIn(overlay), run_time=0.5)
        
        if animate_last_index != -1 and animate_last_index is not None:
            others = [m for i, m in enumerate(mobjects) if i != animate_last_index]
            last = mobjects[animate_last_index]
            self.play(AnimationGroup(*[FadeIn(m, shift=UP*0.2) for m in others], lag_ratio=0.2), run_time=1.0)
            self.wait(0.2)
            self.play(Write(last), run_time=0.8)
        else:
            others = mobjects[:-1]
            last = mobjects[-1]
            if others:
                self.play(AnimationGroup(*[FadeIn(m, shift=UP*0.2) for m in others], lag_ratio=0.2), run_time=1.0)
                self.wait(0.2)
            self.play(Write(last), run_time=0.8)
            
        self.wait(hold)
        self.play(FadeOut(overlay), FadeOut(punch_group), run_time=0.5)

    def construct(self):
        self.section_1_opening()
        self.section_2_tag()
        self.section_3_two_sources()
        self.section_4_cost_gain_paradox()
        self.section_5_two_paradigms()
        self.section_6_static_fusion()
        self.section_7_node_comparison()
        self.section_8_bc_comparison()
        self.section_9_aggregate_accuracy()
        self.section_10_glance_question()

    # ─────────────────────────────────────────────────────────
    # SECTION 1 — Opening: GLANCE and the Fusion Problem
    # ─────────────────────────────────────────────────────────
    def section_1_opening(self):
        title = t("GLANCE", size=64, color=BRIGHT, weight=BOLD)
        subtitle = t("Graph + Language: A New Kind of Challenge", size=32, color=MID)
        VGroup(title, subtitle).arrange(DOWN, buff=0.45).move_to(ORIGIN)

        with self.narrated_caption(["Xin chào mọi người.", "Trong đoạn phim này, chúng ta sẽ tìm hiểu bài báo gờ lans,"]):
            self.play(Write(title), run_time=1.0)
            self.play(FadeIn(subtitle, shift=UP * 0.2), run_time=0.8)

        # GNN side – small graph on left
        mini_graph = create_tag_graph(scale=0.55).move_to(LEFT * 4.0 + UP * 0.8)
        gnn_label = t("Structure", size=22, color=MID).next_to(mini_graph, DOWN, buff=0.15)
        gnn_msg1 = Arrow(mini_graph.nodes["B"].get_center(), mini_graph.nodes["A"].get_center(),
                         buff=0.22, color=BRIGHT, stroke_width=2, tip_length=0.10)
        gnn_msg2 = Arrow(mini_graph.nodes["C"].get_center(), mini_graph.nodes["A"].get_center(),
                         buff=0.22, color=BRIGHT, stroke_width=2, tip_length=0.10)

        # LLM side – doc card on right
        doc_right = doc_icon("Node Text", ["Graph learning", "Heterophily", "Node features"],
                             width=2.8, height=1.8).move_to(RIGHT * 4.0 + UP * 0.8)
        sem_vec = custom_feature_vector("", [0.2, 0.9, 0.4, 0.8, 0.3, 0.7], color=BRIGHT, width=2.6)
        sem_vec.next_to(doc_right, DOWN, buff=0.25)
        llm_label = t("Semantics", size=22, color=MID).next_to(sem_vec, DOWN, buff=0.1)

        with self.narrated_caption(["một nghiên cứu về kết hợp mạng nơ-ron đồ thị", "và mô hình ngôn ngữ lớn."]):
            self.play(
                title.animate.scale(0.5).to_corner(UL),
                FadeOut(subtitle),
                FadeIn(mini_graph, shift=RIGHT * 0.3),
                FadeIn(gnn_label),
                run_time=1.0
            )
            self.play(GrowArrow(gnn_msg1), GrowArrow(gnn_msg2), run_time=0.8)

        with self.narrated_caption(["gờ nờ nờ khai thác cấu trúc đồ thị.", "lờ lờ mờ khai thác ngữ nghĩa văn bản."]):
            self.play(FadeIn(doc_right, shift=LEFT * 0.3), run_time=0.7)
            self.play(
                AnimationGroup(*[FadeIn(c) for c in sem_vec.cells], lag_ratio=0.07),
                FadeIn(sem_vec[0][0]), FadeIn(sem_vec[0][2]), FadeIn(sem_vec[1]),
                run_time=0.9
            )
            self.play(FadeIn(llm_label), run_time=0.4)

        # Bring both toward center to show fusion – but show cost/question mark
        fusion_q = t("But combining them is harder than it looks.", size=28, color=MID).move_to(DOWN * 2.3)
        with self.narrated_caption(["Kết hợp hai mô hình nghe rất hợp lý.", "Nhưng thực tế phức tạp hơn ta nghĩ."]):
            self.play(
                mini_graph.animate.shift(RIGHT * 1.2),
                gnn_label.animate.shift(RIGHT * 1.2),
                doc_right.animate.shift(LEFT * 1.2),
                sem_vec.animate.shift(LEFT * 1.2),
                llm_label.animate.shift(LEFT * 1.2),
                gnn_msg1.animate.shift(RIGHT * 1.2),
                gnn_msg2.animate.shift(RIGHT * 1.2),
                run_time=0.8
            )
            self.play(FadeIn(fusion_q, shift=UP * 0.15), run_time=0.7)

        # Transition: fade out fusion view, keep title corner, flow into TAG
        tag_title = t("Text-Attributed Graph (TAG)", size=38, color=BRIGHT, weight=BOLD).to_edge(UP, buff=0.35)
        with self.narrated_caption(["Để hiểu vấn đề, trước tiên cần hiểu", "loại dữ liệu mà bài báo đang xử lý:"]):
            self.play(
                FadeOut(mini_graph), FadeOut(gnn_label), FadeOut(gnn_msg1), FadeOut(gnn_msg2),
                FadeOut(doc_right), FadeOut(sem_vec), FadeOut(llm_label), FadeOut(fusion_q),
                run_time=0.4
            )
            self.play(FadeIn(tag_title, shift=UP * 0.2), run_time=0.4)

        self.glance_title = title
        self.tag_title = tag_title

    # ─────────────────────────────────────────────────────────
    # SECTION 2 — Text-Attributed Graphs (TAG)
    # ─────────────────────────────────────────────────────────
    def section_2_tag(self):
        doc1 = doc_icon("Paper A", ["ML methods", "Graph theory", "Experiments"], width=2.4, height=1.8).move_to(LEFT * 4.2 + UP * 0.3)
        doc2 = doc_icon("Paper B", ["Deep learning", "Node features", "Benchmarks"], width=2.4, height=1.8).move_to(ORIGIN + UP * 0.3)
        doc3 = doc_icon("Paper C", ["NLP models", "Embeddings", "Classification"], width=2.4, height=1.8).move_to(RIGHT * 4.2 + UP * 0.3)

        # Citation arrows between docs
        cite_AB = Arrow(doc1.get_right(), doc2.get_left(), buff=0.1, color=MID, stroke_width=2, tip_length=0.12)
        cite_BC = Arrow(doc2.get_right(), doc3.get_left(), buff=0.1, color=MID, stroke_width=2, tip_length=0.12)
        cite_AC = Arrow(doc1.get_top() + UP * 0.1, doc3.get_top() + UP * 0.1, path_arc=-1.2, color=DIM, stroke_width=1.5, tip_length=0.10)

        with self.narrated_caption(["đồ thị có thuộc tính văn bản, hay ti ây gi.", "Trong thực tế, văn bản hiếm khi đứng một mình."]):
            self.play(FadeIn(doc1, shift=UP * 0.3), FadeIn(doc2, shift=UP * 0.3), FadeIn(doc3, shift=UP * 0.3), lag_ratio=0.2, run_time=1.2)

        with self.narrated_caption(["Bài báo trích dẫn nhau,", "và bài đăng tương tác với nhau."]):
            self.play(GrowArrow(cite_AB), run_time=0.5)
            self.play(GrowArrow(cite_BC), run_time=0.5)
            self.play(Create(cite_AC), run_time=0.4)

        # Target positions for nodes
        graph = create_tag_graph(scale=1.1).move_to(DOWN * 0.3)
        node_A = graph.nodes["A"]
        node_B = graph.nodes["B"]
        node_C = graph.nodes["C"]

        with self.narrated_caption(["Mỗi tài liệu trở thành một nót,"]):
            self.play(
                ReplacementTransform(doc1, node_A),
                ReplacementTransform(doc2, node_B),
                ReplacementTransform(doc3, node_C),
                FadeOut(cite_AB), FadeOut(cite_BC), FadeOut(cite_AC),
                run_time=1.2
            )

        with self.narrated_caption(["và mỗi mối liên hệ trở thành một cạnh."]):
            self.play(Create(graph.edges), run_time=0.8)
            other_nodes = VGroup(*[n for k, n in graph.nodes.items() if k not in ["A", "B", "C"]])
            self.play(FadeIn(other_nodes, lag_ratio=0.1), run_time=0.7)

        with self.narrated_caption(["Khi mỗi nót có cả nội dung văn bản", "lẫn kết nối với nót khác,"]):
            # Briefly highlight node A to show text+connections
            self.play(node_A.animate.set_stroke(BRIGHT, width=3.5), run_time=0.8)

        with self.narrated_caption(["ta gọi cấu trúc đó là đồ thị có thuộc tính văn bản."]):
            # Punchline overlaid on graph (not replacing it)
            punch = t("TEXT + CONNECTIONS = ONE GRAPH", size=44, color=BRIGHT, weight=BOLD).set_z_index(100)
            blackout_tag = Rectangle(width=20, height=15, fill_color=BLACK, fill_opacity=0.85).set_z_index(99)
            self.play(FadeIn(blackout_tag), FadeIn(punch, shift=UP * 0.15), run_time=0.7)
            self.wait(1.0)
            self.play(FadeOut(punch), FadeOut(blackout_tag), run_time=0.5)

        self.tag_graph = graph

    # ─────────────────────────────────────────────────────────
    # SECTION 3 — Complementary Strengths
    # ─────────────────────────────────────────────────────────
    def section_3_two_sources(self):
        graph = self.tag_graph
        node_A = graph.nodes["A"]

        with self.narrated_caption(["Để phân loại một nót, ta có hai nguồn bằng chứng."]):
            self.play(FadeOut(self.tag_title), run_time=0.4)
            # Zoom into node A
            self.play(
                self.camera.frame.animate.scale(0.65).move_to(node_A),
                node_A.animate.set_fill(BRIGHT, 0.4),
                run_time=1.0
            )

        with self.narrated_caption(["Vùng lân cận cung cấp thông tin cấu trúc.", "Nội dung văn bản cung cấp thông tin ngữ nghĩa."]):
            self.play(
                self.camera.frame.animate.scale(1 / 0.65).move_to(ORIGIN),
                FadeOut(graph.edges),
                FadeOut(VGroup(*[n for k, n in graph.nodes.items() if k != "A"])),
                node_A.animate.move_to(ORIGIN),
                run_time=1.0
            )
            struct_label = t("NEIGHBORHOOD", size=22, color=MID).move_to(LEFT * 3.6 + UP * 2.1)
            sem_label = t("NODE TEXT", size=22, color=MID).move_to(RIGHT * 3.6 + UP * 2.1)
            neighborhood = create_target_neighborhood(kind="clean", label="Target", scale=0.85).move_to(LEFT * 3.6 + UP * 0.4)
            doc = create_text_document("Node A", ["Graph Learning", "Methods", "Embedding"], width=2.6, height=1.6).move_to(RIGHT * 3.6 + UP * 0.4)
            self.play(FadeIn(struct_label), FadeIn(sem_label), run_time=0.4)
            self.play(
                ReplacementTransform(node_A, neighborhood.target),
                FadeIn(neighborhood.neighbors), FadeIn(neighborhood.edges),
                FadeIn(doc),
                run_time=1.0
            )

        with self.narrated_caption(["gờ nờ nờ học thông tin cấu trúc", "bằng cách truyền thông tin qua các cạnh."]):
            gnn_module = module("GNN", width=1.8, height=0.7).move_to(LEFT * 3.6 + DOWN * 1.3)
            down_arr1 = small_arrow(neighborhood.get_bottom(), gnn_module.get_top())
            self.play(FadeIn(gnn_module), GrowArrow(down_arr1), run_time=0.7)
            msgs = VGroup(*[create_message_vector(n.get_center(), neighborhood.target.get_center()) for n in neighborhood.neighbors]).set_stroke(width=2)
            self.play(AnimationGroup(*[GrowArrow(m) for m in msgs], lag_ratio=0.1), run_time=1.0)

        with self.narrated_caption(["Các tín hiệu từ hàng xóm được tổng hợp", "thành một véc-tơ biểu diễn cấu trúc."]):
            self.play(FadeOut(msgs), run_time=0.4)
            struct_vec = custom_feature_vector("STRUCTURAL EMBEDDING", [0.8, 0.2, 0.9, 0.7, 0.3, 0.6, 0.1, 0.8], color=BRIGHT, width=3.2).move_to(LEFT * 3.6 + DOWN * 2.3)
            arr2 = small_arrow(gnn_module.get_bottom(), struct_vec.get_top())
            self.play(GrowArrow(arr2), run_time=0.4)
            self.play(FadeIn(struct_vec[0][0]), FadeIn(struct_vec[0][2]), FadeIn(struct_vec[1]), run_time=0.3)
            self.play(AnimationGroup(*[FadeIn(c) for c in struct_vec.cells], lag_ratio=0.08), run_time=0.9)

        with self.narrated_caption(["lờ lờ mờ đọc văn bản, nhận ra các từ khóa quan trọng,"]):
            self.play(highlight_keywords(doc, [0, 1]), run_time=0.8)
            llm_module = module("LLM", width=1.8, height=0.7, emphasized=True).move_to(RIGHT * 3.6 + DOWN * 1.3)
            arr3 = small_arrow(doc.get_bottom(), llm_module.get_top())
            self.play(FadeIn(llm_module), GrowArrow(arr3), run_time=0.7)

        with self.narrated_caption(["rồi tạo ra một véc-tơ biểu diễn ngữ nghĩa."]):
            sem_vec = custom_feature_vector("SEMANTIC EMBEDDING", [0.2, 0.9, 0.4, 0.2, 0.8, 0.3, 0.7, 0.9], color=BRIGHT, width=3.2).move_to(RIGHT * 3.6 + DOWN * 2.3)
            arr4 = small_arrow(llm_module.get_bottom(), sem_vec.get_top())
            self.play(GrowArrow(arr4), run_time=0.4)
            self.play(FadeIn(sem_vec[0][0]), FadeIn(sem_vec[0][2]), FadeIn(sem_vec[1]), run_time=0.3)
            self.play(AnimationGroup(*[FadeIn(c) for c in sem_vec.cells], lag_ratio=0.08), run_time=0.9)

        with self.narrated_caption(["gờ nờ nờ hiểu nót qua kết nối.", "lờ lờ mờ hiểu nót qua nội dung.", "Hai mô hình bổ sung cho nhau."]):
            blackout = Rectangle(width=20, height=15, fill_color=BLACK, fill_opacity=0.85).set_z_index(99)
            comp = t("STRUCTURE + SEMANTICS", size=48, color=BRIGHT, weight=BOLD).set_z_index(100)
            self.play(FadeIn(blackout), FadeIn(comp, shift=UP * 0.2), run_time=0.8)
            self.wait(0.5)
            
        self.play(
            FadeOut(struct_label), FadeOut(sem_label), FadeOut(neighborhood),
            FadeOut(doc), FadeOut(gnn_module), FadeOut(down_arr1), FadeOut(arr2), FadeOut(struct_vec),
            FadeOut(llm_module), FadeOut(arr3), FadeOut(arr4), FadeOut(sem_vec),
            FadeOut(blackout), FadeOut(comp),
            run_time=0.8
        )

    # ─────────────────────────────────────────────────────────
    # SECTION 4 — Cost–Gain Paradox
    # ─────────────────────────────────────────────────────────
    def section_4_cost_gain_paradox(self):
        # Show a graph with many nodes, route all to LLM
        mini_nodes = VGroup()
        positions = [LEFT*3+UP*1.5, LEFT*1.5+UP*2, ORIGIN+UP*2.2, RIGHT*1.5+UP*1.5,
                     LEFT*3+ORIGIN, LEFT*1.5+UP*0.5, ORIGIN+UP*0.5, RIGHT*1.5+ORIGIN,
                     LEFT*2+DOWN*1.5, ORIGIN+DOWN*1.5, RIGHT*2+DOWN*1.5]
        for i, pos in enumerate(positions):
            n = node(str(i+1), radius=0.22).move_to(pos)
            mini_nodes.add(n)

        llm_box = module("LLM", width=2.2, height=0.9, emphasized=True).move_to(RIGHT * 4.5 + UP * 0.5)

        with self.narrated_caption(["Nhưng ở đây xuất hiện một nghịch lý.", "Giả sử ta gọi lờ lờ mờ cho mọi nót trong đồ thị."]):
            self.play(FadeIn(mini_nodes, lag_ratio=0.05), run_time=1.0)
            self.play(FadeIn(llm_box), run_time=0.5)

        # Animate query arrows from nodes to LLM, with cost counter
        cost_label = t("LLM Calls: 0", size=28, color=LIGHT).to_corner(UR).shift(DOWN * 0.5)
        self.play(FadeIn(cost_label), run_time=0.3)

        llm_arrows = VGroup()
        with self.narrated_caption(["Mỗi nót gửi một yêu cầu.", "Chi phí tăng lên nhanh chóng."]):
            for i, n in enumerate(mini_nodes[:6]):
                arr = Arrow(n.get_right(), llm_box.get_left(), buff=0.1, color=MID, stroke_width=1.5, tip_length=0.10)
                llm_arrows.add(arr)
                new_label = t(f"LLM Calls: {i+1}", size=28, color=BRIGHT if i >= 3 else LIGHT).to_corner(UR).shift(DOWN * 0.5)
                self.play(GrowArrow(arr), ReplacementTransform(cost_label, new_label), run_time=0.3)
                cost_label = new_label

        with self.narrated_caption(["Nhưng độ chính xác tổng thể", "chỉ tăng một chút."]):
            # Cost HIGH, gain LOW
            cost_row_label = t("LLM Cost:", size=32, color=LIGHT)
            cost_row_val = t("HIGH", size=48, color=RED, weight=BOLD)
            cost_row = VGroup(cost_row_label, cost_row_val).arrange(RIGHT, buff=0.3).move_to(LEFT * 2 + UP * 0.5)

            gain_row_label = t("Accuracy Gain:", size=32, color=LIGHT)
            gain_row_val = t("LOW", size=32, color=MID, weight=BOLD)
            gain_row = VGroup(gain_row_label, gain_row_val).arrange(RIGHT, buff=0.3).move_to(LEFT * 2 + DOWN * 0.3)

            self.play(FadeOut(mini_nodes), FadeOut(cost_label), FadeOut(llm_arrows), run_time=0.5)
            self.play(FadeIn(cost_row), run_time=0.6)
            self.play(cost_row_val.animate.scale(1.25), run_time=0.4)
            self.play(cost_row_val.animate.scale(1/1.25), run_time=0.3)
            self.play(FadeIn(gain_row, shift=UP * 0.1), run_time=0.5)
            self.play(gain_row_val.animate.set_opacity(0.5), run_time=0.4)

        with self.narrated_caption(["Có thể lờ lờ mờ không vô ích.", "Có thể nó đang được dùng trên sai nót."]):
            q1 = t("IS THE LLM USELESS?", size=40, color=LIGHT, weight=BOLD).move_to(UP * 0.5)
            q2 = t("OR ARE WE USING IT ON THE WRONG NODES?", size=36, color=BRIGHT, weight=BOLD).move_to(DOWN * 0.5)
            self.play(FadeOut(llm_box), ReplacementTransform(VGroup(cost_row, gain_row), q1), run_time=0.8)
            self.wait(0.3)
            self.play(FadeIn(q2, shift=UP * 0.15), run_time=0.7)
            self.wait(0.8)
            self.play(FadeOut(q1), FadeOut(q2), run_time=0.7)

    # ─────────────────────────────────────────────────────────
    # SECTION 5 — Two Existing GNN–LLM Paradigms
    # ─────────────────────────────────────────────────────────
    def section_5_two_paradigms(self):
        if getattr(self, "glance_title", None) is not None and self.glance_title in self.mobjects:
            self.remove(self.glance_title)

        title = t("TWO GNN–LLM FUSION PARADIGMS", size=34, color=BRIGHT, weight=BOLD).to_edge(UP, buff=0.38)

        enhancer_title = t("LLM-AS-ENHANCER", size=26, color=LIGHT, weight=BOLD)
        enh_p = VGroup(module("Text", width=1.7), module("LLM", width=1.7, emphasized=True),
                       module("GNN", width=1.7), module("Predict", width=1.7)).arrange(DOWN, buff=0.35)
        enh_arrows = VGroup(*[small_arrow(enh_p[i].get_bottom(), enh_p[i+1].get_top()) for i in range(3)])
        enh_group = VGroup(enhancer_title, VGroup(enh_p, enh_arrows)).arrange(DOWN, buff=0.35).scale(0.88).move_to(LEFT * 3.5 + UP * 0.1)

        predictor_title = t("LLM-AS-PREDICTOR", size=26, color=LIGHT, weight=BOLD)
        pred_p = VGroup(module("Text+Graph", width=2.2), module("Prompt", width=2.2),
                        module("LLM", width=2.2, emphasized=True), module("Predict", width=2.2)).arrange(DOWN, buff=0.35)
        pred_arrows = VGroup(*[small_arrow(pred_p[i].get_bottom(), pred_p[i+1].get_top()) for i in range(3)])
        pred_group = VGroup(predictor_title, VGroup(pred_p, pred_arrows)).arrange(DOWN, buff=0.35).scale(0.88).move_to(RIGHT * 3.5 + UP * 0.1)

        with self.narrated_caption(["Các phương pháp hiện nay chia thành hai hướng:", "lờ lờ mờ làm bộ tăng cường và lờ lờ mờ-as-Predictor."]):
            self.play(Write(title), run_time=0.7)
            self.play(FadeIn(enh_group), FadeIn(pred_group), run_time=1.0)

        # Enhancer deep-dive
        noisy_nbhd = create_target_neighborhood(kind="noisy", scale=0.9).move_to(RIGHT * 2.8 + DOWN * 0.2)
        with self.narrated_caption(["lờ lờ mờ làm bộ tăng cường tạo véc-tơ ngữ nghĩa giàu hơn,", "rồi gờ nờ nờ tiếp tục truyền thông tin và dự đoán."]):
            self.play(
                FadeOut(pred_group),
                enh_group.animate.scale(1.08).shift(RIGHT * 1.2),
                title.animate.scale(0.55).to_corner(UR),
                FadeIn(noisy_nbhd.target), FadeIn(noisy_nbhd.neighbors), FadeIn(noisy_nbhd.edges),
                run_time=0.8
            )
            self.wait(1.5)
            noisy_msgs = VGroup(*[create_message_vector(
                n.get_center(), noisy_nbhd.target.get_center(),
                color=DARK if i not in {1, 2, 5, 7} else BRIGHT
            ) for i, n in enumerate(noisy_nbhd.neighbors)])
            self.play(AnimationGroup(*[GrowArrow(m) for m in noisy_msgs], lag_ratio=0.08), run_time=1.0)

        with self.narrated_caption(["Tuy nhiên, dù véc-tơ ngữ nghĩa tốt hơn,", "gờ nờ nờ vẫn có thể bị kéo lệch bởi các hàng xóm nhiễu."]):
            # Emphasize the noisy neighbors (indices 1, 2, 5, 7)
            noisy_nodes = VGroup(*[noisy_nbhd.neighbors[i] for i in {1, 2, 5, 7}])
            noisy_arrows = VGroup(*[noisy_msgs[i] for i in {1, 2, 5, 7}])
            
            self.wait(1.8)
            
            # Flash the noisy arrows and wiggle the target node
            self.play(
                noisy_nodes.animate.set_color(gs.C_BAD),
                noisy_arrows.animate.set_color(gs.C_BAD),
                noisy_nbhd.target.animate.shift(RIGHT * 0.1).set_color(gs.C_BAD),
                rate_func=there_and_back,
                run_time=0.8
            )
            self.play(noisy_nbhd.target.animate.shift(LEFT * 0.1), rate_func=there_and_back, run_time=0.4)
            
            self.wait(0.8) # Wait to let the visual sink in
            
            # Punchline ON TOP of the diagram
            bias_text = t("BETTER TEXT ≠ NO STRUCTURAL BIAS", size=44, color=BRIGHT, weight=BOLD).set_z_index(100)
            blackout2 = Rectangle(width=20, height=15, fill_color=BLACK, fill_opacity=0.85).set_z_index(99)
            self.play(
                FadeIn(blackout2),
                FadeIn(bias_text, shift=UP * 0.1), 
                run_time=0.5
            )
            self.wait(0.5)
            
        # Predictor deep-dive
        token_text = t("Prompt Token Count: 128", size=30, color=MID).move_to(LEFT * 2.8 + DOWN * 0.4)
        with self.narrated_caption(["lờ lờ mờ-as-Predictor đổi toàn bộ thông tin", "thành một câu lệnh văn bản dài."]):
            pred_group.move_to(RIGHT * 2.5 + DOWN * 0.1).scale(1.08)
            self.play(
                FadeOut(noisy_nbhd), FadeOut(noisy_msgs), FadeOut(blackout2), FadeOut(bias_text),
                FadeOut(enh_group),
                FadeIn(pred_group),
                run_time=0.8
            )
            self.play(Write(token_text), run_time=0.4)

        with self.narrated_caption(["Vùng lân cận càng lớn, câu lệnh càng dài.", "Cấu trúc đồ thị dần biến mất trong chuỗi đơn vị từ."]):
            # Token counter escalates live
            for count, col in [(256, MID), (512, BRIGHT), (1024, RED), (2048, RED)]:
                new_token = t(f"Prompt Token Count: {count}{'!!!' if count >= 1024 else '...'}", size=30, color=col).move_to(LEFT * 2.8 + DOWN * 0.4)
                self.play(ReplacementTransform(token_text, new_token), run_time=0.25)
                token_text = new_token

            l1 = t("GRAPH STRUCTURE", size=46, color=BRIGHT, weight=BOLD)
            l2 = mt(r"\downarrow", size=55, color=gs.C_BAD)
            l3 = t("LONG TEXT SEQUENCE", size=46, color=BRIGHT, weight=BOLD)
            graph_loss = VGroup(l1, l2, l3).arrange(DOWN, buff=0.25).set_z_index(100)
            
            blackout3 = Rectangle(width=20, height=15, fill_color=BLACK, fill_opacity=0.85).set_z_index(99)
            self.play(FadeIn(blackout3), FadeIn(graph_loss, shift=UP * 0.1), run_time=0.5)
            
            # Note: Do not fade out here, let it remain until audio finishes
            self.sec5_objects = VGroup(pred_group, token_text, blackout3, graph_loss, title)

    # ─────────────────────────────────────────────────────────
    # SECTION 6 — Uniform Static Fusion
    # ─────────────────────────────────────────────────────────
    def section_6_static_fusion(self):
        self.play(FadeOut(self.sec5_objects), run_time=0.5)
        
        node_a = node("A", radius=0.38).move_to(LEFT * 5 + UP * 2.0)
        node_b = node("B", radius=0.38).move_to(LEFT * 5 + ORIGIN)
        node_c = node("C", radius=0.38).move_to(LEFT * 5 + DOWN * 2.0)
        strategy_box = module("Same Fusion Strategy", width=5.2, height=2.6).move_to(RIGHT * 0.8)
        arr_a = small_arrow(node_a.get_right(), strategy_box.get_left() + UP * 0.55)
        arr_b = small_arrow(node_b.get_right(), strategy_box.get_left())
        arr_c = small_arrow(node_c.get_right(), strategy_box.get_left() + DOWN * 0.55)

        with self.narrated_caption(["Dù dùng bộ tăng cường hay bộ dự đoán,", "nhiều phương pháp áp cùng một chiến lược kết hợp cho mọi nót."]):
            self.play(FadeIn(node_a), FadeIn(node_b), FadeIn(node_c), run_time=0.7)
            self.play(FadeIn(strategy_box), run_time=0.6)
            self.play(GrowArrow(arr_a), GrowArrow(arr_b), GrowArrow(arr_c), run_time=0.8)

        with self.narrated_caption(["Bài báo gọi đây là static fusion, hay kết hợp tĩnh."]):
            stamp = t("STATIC FUSION", size=42, color=BRIGHT, weight=BOLD).move_to(strategy_box.get_center())
            self.play(ReplacementTransform(strategy_box[1], stamp), run_time=0.7)
            self.wait(0.6)

        # Transition: keep nodes, morph into section_7 layout
        self.static_nodes = VGroup(node_a, node_b, node_c)
        self.static_objects = VGroup(strategy_box, arr_a, arr_b, arr_c, stamp)

    # ─────────────────────────────────────────────────────────
    # SECTION 7 — Node A, B, C Comparison
    # ─────────────────────────────────────────────────────────
    def section_7_node_comparison(self):
        # Fade out static fusion elements, keep nodes briefly
        self.play(FadeOut(self.static_objects), run_time=0.6)
        node_a, node_b, node_c = self.static_nodes[0], self.static_nodes[1], self.static_nodes[2]

        # ── NODE A ──────────────────────────────────────────
        group_A = create_target_neighborhood(kind="clean", label="A", scale=0.95).move_to(LEFT * 4 + UP * 0.4)
        title_A = t("Node A: Clear Structure", size=34, color=BRIGHT, weight=BOLD).to_edge(UP, buff=0.35)
        doc_A = create_text_document("Node A", ["Topic 1", "Topic 2", "Topic 3"], width=3.2, height=1.6).move_to(RIGHT * 3.5 + UP * 1.8)
        gnn_bar_A = probability_vector("GNN Prediction", [0.85, 0.10, 0.05], emphasized_index=0).move_to(RIGHT * 3.5 + DOWN * 0.2).scale(1.2)

        with self.narrated_caption(["Ba nót có thể rất khác nhau.", "Nót A được gờ nờ nờ xử lý tốt."]):
            self.play(FadeOut(node_b), FadeOut(node_c), run_time=0.5)
            self.play(ReplacementTransform(node_a, group_A.target), run_time=0.8)
            self.play(Write(title_A), FadeIn(group_A.neighbors), FadeIn(group_A.edges), FadeIn(doc_A), run_time=1.0)

        with self.narrated_caption(["Hàng xóm đồng thuận, gờ nờ nờ tạo véc-tơ ổn định."]):
            msgs_A = VGroup(*[create_message_vector(n.get_center(), group_A.target.get_center(), color=LIGHT)
                               for n in group_A.neighbors])
            self.play(AnimationGroup(*[GrowArrow(m) for m in msgs_A], lag_ratio=0.1), run_time=1.0)
            self.play(FadeIn(gnn_bar_A), run_time=0.7)

        with self.narrated_caption(["gờ nờ nờ dự đoán đúng. Gọi lờ lờ mờ là không cần thiết."]):
            skip_label = t("[SKIP LLM]", size=34, color=gs.C_GOOD, weight=BOLD).next_to(gnn_bar_A, DOWN, buff=0.4)
            self.play(FadeIn(skip_label, shift=UP * 0.1), run_time=0.6)
            self.wait(0.4)

        # ── NODE B ──────────────────────────────────────────
        title_B = t("Node B: Noisy Structure, Clear Text", size=34, color=BRIGHT, weight=BOLD).to_edge(UP, buff=0.35)
        group_B = create_target_neighborhood(kind="noisy", label="B", scale=0.95).move_to(LEFT * 4 + UP * 0.4)
        doc_B = create_text_document("Node B", ["Graph Learning", "Heterophily", "Node Classification"], width=3.2, height=1.6).move_to(RIGHT * 3.5 + UP * 1.8)
        gnn_bar_B = probability_vector("GNN Prediction", [0.20, 0.65, 0.15], emphasized_index=1).move_to(RIGHT * 1.8 + DOWN * 0.8).scale(1.1)

        with self.narrated_caption(["Nót B có vùng lân cận chứa nhiều loại khác nhau."]):
            self.play(
                FadeOut(title_A),
                FadeIn(title_B),
                ReplacementTransform(group_A.neighbors, group_B.neighbors),
                ReplacementTransform(group_A.target, group_B.target),
                ReplacementTransform(group_A.edges, group_B.edges),
                ReplacementTransform(doc_A, doc_B),
                FadeOut(skip_label), FadeOut(msgs_A),
                run_time=1.1
            )

        with self.narrated_caption(["Các tín hiệu kéo nhiều hướng, gờ nờ nờ dự đoán sai."]):
            msgs_B = VGroup(*[create_message_vector(
                n.get_center(), group_B.target.get_center(),
                color=DARK if i not in {1, 2, 5, 7} else BRIGHT
            ) for i, n in enumerate(group_B.neighbors)])
            self.play(AnimationGroup(*[GrowArrow(m) for m in msgs_B], lag_ratio=0.1), run_time=1.0)
            self.play(ReplacementTransform(gnn_bar_A, gnn_bar_B), run_time=0.7)
            wrong_B = t("GNN: WRONG", color=gs.C_BAD, weight=BOLD, size=24).next_to(gnn_bar_B, DOWN, buff=0.15)
            self.play(FadeIn(wrong_B), run_time=0.4)

        with self.narrated_caption(["Nhưng văn bản nót B rất rõ ràng.", "lờ lờ mờ sửa lại dự đoán thành công."]):
            self.play(highlight_keywords(doc_B, [0, 1, 2]), run_time=0.8)
            llm_bar_B = probability_vector("LLM Corrected", [0.90, 0.05, 0.05], emphasized_index=0).move_to(RIGHT * 5.2 + DOWN * 0.8).scale(1.1)
            self.play(FadeIn(llm_bar_B), run_time=0.7)
            correct_B = t("LLM: CORRECT", color=gs.C_GOOD, weight=BOLD, size=24).next_to(llm_bar_B, DOWN, buff=0.15)
            self.play(FadeIn(correct_B), run_time=0.4)

        # Save Node B state for section 8
        self.node_B_state = {
            "title": title_B, "group": group_B, "doc": doc_B,
            "gnn_bar": gnn_bar_B, "llm_bar": llm_bar_B,
            "wrong": wrong_B, "correct": correct_B, "msgs": msgs_B
        }

        # ── NODE C ──────────────────────────────────────────
        title_C = t("Node C: Noisy Structure, Ambiguous Text", size=32, color=BRIGHT, weight=BOLD).to_edge(UP, buff=0.35)
        group_C = create_target_neighborhood(kind="noisy", label="C", scale=0.95).move_to(LEFT * 4 + UP * 0.4)
        doc_C = create_text_document("Node C", ["Some words...", "General text...", "Vague description"], width=3.2, height=1.6).move_to(RIGHT * 3.5 + UP * 1.8)

        with self.narrated_caption(["Nót C cũng khó với gờ nờ nờ.", "Nhưng văn bản lại rất mơ hồ."]):
            llm_bar_C = probability_vector("LLM Output", [0.33, 0.34, 0.33], emphasized_index=None).move_to(RIGHT * 5.2 + DOWN * 0.8).scale(1.1)
            wrong_C = t("LLM: UNCERTAIN", color=gs.C_BAD, weight=BOLD, size=24).next_to(llm_bar_C, DOWN, buff=0.15)
            self.play(
                FadeOut(title_B),
                FadeIn(title_C),
                ReplacementTransform(group_B.target, group_C.target),
                ReplacementTransform(group_B.neighbors, group_C.neighbors),
                ReplacementTransform(group_B.edges, group_C.edges),
                ReplacementTransform(doc_B, doc_C),
                ReplacementTransform(llm_bar_B, llm_bar_C),
                FadeOut(correct_B),
                FadeOut(msgs_B),
                run_time=1.1
            )
            self.play(FadeIn(wrong_C), run_time=0.4)

        with self.narrated_caption(["lờ lờ mờ không đủ bằng chứng để sửa kết quả.", "Cả hai mô hình đều thất bại."]):
            self.wait(0.6)
            # For Node C, GNN was also wrong. We just update the label for Node C's GNN
            gnn_bar_C = probability_vector("GNN Prediction", [0.10, 0.20, 0.70], emphasized_index=2).move_to(RIGHT * 1.8 + DOWN * 0.8).scale(1.1)
            wrong_gnn_C = t("GNN: WRONG", color=gs.C_BAD, weight=BOLD, size=24).next_to(gnn_bar_C, DOWN, buff=0.15)
            self.play(ReplacementTransform(gnn_bar_B, gnn_bar_C), FadeOut(wrong_B), FadeIn(wrong_gnn_C), run_time=0.7)

        # Save Node C state for section 8
        self.node_C_state = {
            "title": title_C, "group": group_C, "doc": doc_C,
            "gnn_bar": gnn_bar_C, "llm_bar": llm_bar_C,
            "wrong_gnn": wrong_gnn_C, "wrong_llm": wrong_C, "msgs": msgs_B
        }

    # ─────────────────────────────────────────────────────────
    # SECTION 8 — Direct B vs C Comparison
    # ─────────────────────────────────────────────────────────
    def section_8_bc_comparison(self):
        b = self.node_B_state
        c = self.node_C_state

        b_title = t("Node B (Clear Text)", size=34, color=gs.C_GOOD, weight=BOLD).move_to(LEFT * 3.5 + UP * 2.0)
        c_title = t("Node C (Ambiguous)", size=34, color=gs.C_BAD, weight=BOLD).move_to(RIGHT * 3.5 + UP * 2.0)
        
        b_gnn = t("GNN: WRONG", size=30, color=gs.C_BAD, weight=BOLD).move_to(LEFT * 3.5 + UP * 0.5)
        b_llm = t("LLM: CORRECT", size=30, color=gs.C_GOOD, weight=BOLD).move_to(LEFT * 3.5 + DOWN * 0.5)

        c_gnn = t("GNN: WRONG", size=30, color=gs.C_BAD, weight=BOLD).move_to(RIGHT * 3.5 + UP * 0.5)
        c_llm = t("LLM: UNCERTAIN", size=30, color=gs.C_BAD, weight=BOLD).move_to(RIGHT * 3.5 + DOWN * 0.5)
        
        vs = t("VS", size=48, color=MID, weight=BOLD).move_to(UP * 0.5)

        with self.narrated_caption(["Nót B và Nót C đều khó với gờ nờ nờ.", "Nhưng chỉ Nót B nhận được lợi ích từ lờ lờ mờ."]):
            self.play(
                FadeOut(c["title"]), FadeOut(c["group"]), FadeOut(c["doc"]),
                FadeOut(c["gnn_bar"]), FadeOut(c["llm_bar"]),
                FadeOut(c["wrong_gnn"]), FadeOut(c["wrong_llm"]),
                run_time=0.7
            )
            
            l1 = t("SAME GNN DIFFICULTY", size=44, color=BRIGHT, weight=BOLD)
            l2 = t("DIFFERENT LLM VALUE", size=44, color=BRIGHT, weight=BOLD)
            compare_heading = VGroup(l1, l2).arrange(DOWN, buff=0.3).set_z_index(100)
            blackout4 = Rectangle(width=20, height=15, fill_color=BLACK, fill_opacity=0.85).set_z_index(99)
            
            self.play(FadeIn(blackout4), FadeIn(compare_heading, shift=UP * 0.2), run_time=0.9)
            self.wait(0.5)
            self.play(FadeOut(compare_heading), FadeOut(blackout4), run_time=0.5)
            
            self.play(
                FadeIn(b_title), FadeIn(c_title),
                FadeIn(b_gnn), FadeIn(c_gnn),
                FadeIn(b_llm), FadeIn(c_llm),
                FadeIn(vs),
                run_time=0.9
            )

        conclusion = t("GNN DIFFICULTY ≠ LLM BENEFIT", size=44, color=gs.C_GOOD, weight=BOLD).set_z_index(100)
        blackout5 = Rectangle(width=20, height=15, fill_color=BLACK, fill_opacity=0.85).set_z_index(99)
        with self.narrated_caption(["Đây là điểm mấu chốt của bài báo."]):
            self.play(FadeIn(blackout5), FadeIn(conclusion, shift=UP * 0.2), run_time=0.8)
            self.wait(0.6)

        # Store for morph into section 9
        self.comparison_objects = VGroup(
            b_title, c_title, b_gnn, b_llm, c_gnn, c_llm, vs, blackout4, blackout5, conclusion
        )

    # ─────────────────────────────────────────────────────────
    # SECTION 9 — Aggregate Accuracy
    # ─────────────────────────────────────────────────────────
    def section_9_aggregate_accuracy(self):
        # Morph from comparison directly into population diagram
        illustrative = t("ILLUSTRATIVE EXAMPLE", size=26, color=MID).to_corner(UR).shift(DOWN * 0.3)
        with self.narrated_caption(["Sự khác biệt này giải thích vì sao", "độ chính xác tổng thể có thể tăng rất ít."]):
            self.play(
                FadeOut(self.comparison_objects, shift=UP * 0.3),
                FadeIn(illustrative),
                run_time=0.8
            )

        with self.narrated_caption(["Giả sử chín mươi phần trăm là các nót dễ,", "còn mười phần trăm là các nót khó."]):
            easy_group = VGroup(
                t("90% Easy Nodes", size=38, color=BRIGHT, weight=BOLD),
                t("GNN: 95%  ->  Fusion: 94%", size=26, color=LIGHT)
            ).arrange(DOWN, buff=0.2).move_to(LEFT * 3.2 + UP * 1.4)
            hard_group = VGroup(
                t("10% Hard Nodes", size=38, color=BRIGHT, weight=BOLD),
                t("GNN: 40%  ->  Fusion: 53%", size=26, color=LIGHT)
            ).arrange(DOWN, buff=0.2).move_to(RIGHT * 3.2 + UP * 1.4)
            self.play(FadeIn(easy_group, shift=UP * 0.2), FadeIn(hard_group, shift=UP * 0.2), run_time=1.0)

        with self.narrated_caption(["Trên nhóm khó, lờ lờ mờ giúp tăng mười ba điểm phần trăm."]):
            gnn_eq = mt(r"\text{GNN: } 0.9{\times}95\% + 0.1{\times}40\% = 89.5\%", size=38).move_to(DOWN * 0.5)
            self.play(Write(gnn_eq), run_time=0.9)
            gain_hard = t("Hard-node gain: +13%", size=28, color=gs.C_GOOD, weight=BOLD).next_to(hard_group, DOWN, buff=0.4)
            self.play(FadeIn(gain_hard, shift=UP * 0.1), run_time=0.6)

        with self.narrated_caption(["Nhưng trên toàn đồ thị, tổng thể chỉ tăng 0.4 điểm."]):
            fusion_eq = mt(r"\text{Fusion: } 0.9{\times}94\% + 0.1{\times}53\% = 89.9\%", size=38).next_to(gnn_eq, DOWN, buff=0.4)
            self.play(TransformFromCopy(gnn_eq, fusion_eq), run_time=0.9)
            self.play(gnn_eq.animate.set_opacity(0.3), run_time=0.4)
            gain_overall = t("Overall gain: +0.4 percentage points", size=28, color=MID).next_to(fusion_eq, DOWN, buff=0.3)
            self.play(FadeIn(gain_overall), run_time=0.5)

        with self.narrated_caption(["Lợi ích lớn ở một nhóm nhỏ trông rất nhỏ khi tính tổng."]):
            takeaway = t("LARGE SUBGROUP GAINS CAN LOOK SMALL IN AGGREGATE", size=30, color=BRIGHT, weight=BOLD).move_to(DOWN * 3.2)
            self.play(FadeIn(takeaway, shift=UP * 0.1), run_time=0.7)
            self.wait(0.8)

        self.sec9_objects = VGroup(illustrative, easy_group, hard_group, gnn_eq, fusion_eq, gain_hard, gain_overall, takeaway)

    # ─────────────────────────────────────────────────────────
    # SECTION 10 — GLANCE Research Question & Task 2
    # ─────────────────────────────────────────────────────────
    def section_10_glance_question(self):
        with self.narrated_caption(["Tóm lại, khó với gờ nờ nờ chưa chắc có lợi từ lờ lờ mờ."]):
            self.play(FadeOut(self.sec9_objects, shift=UP * 0.3), run_time=0.7)
            beat1 = VGroup(
                t("GNN DIFFICULTY", size=46, color=LIGHT, weight=BOLD),
                t("≠", size=70, color=gs.C_BAD, weight=BOLD),
                t("LLM BENEFIT", size=46, color=BRIGHT, weight=BOLD),
            ).arrange(DOWN, buff=0.38)
            self.play(FadeIn(beat1, shift=UP * 0.2), run_time=0.8)
            self.wait(0.5)

        with self.narrated_caption(["Vậy nót nào thực sự đáng để gọi lờ lờ mờ?"]):
            self.play(FadeOut(beat1), run_time=0.6)
            q = t("WHICH NODES SHOULD QUERY THE LLM?", size=44, color=gs.C_GOOD, weight=BOLD)
            self.play(Write(q), run_time=0.9)

            # Router pipeline fades in below question
            router = VGroup(
                module("Node").scale(1.15), module("GNN").scale(1.15), module("Router", emphasized=True).scale(1.15)
            ).arrange(RIGHT, buff=0.75).move_to(LEFT * 2.2 + DOWN * 1.0)
            r_arrows = VGroup(*[small_arrow(router[i].get_right(), router[i+1].get_left()) for i in range(2)])
            keep_gnn = module("Keep GNN", width=2.4).scale(1.1).move_to(router[2].get_center() + RIGHT * 3.0 + UP * 1.3)
            query_llm = module("Query LLM", width=2.4, emphasized=True).scale(1.1).move_to(router[2].get_center() + RIGHT * 3.0 + DOWN * 1.3)
            a_up = small_arrow(router[2].get_right() + UP * 0.15, keep_gnn.get_left())
            a_dn = small_arrow(router[2].get_right() + DOWN * 0.15, query_llm.get_left())

            self.play(q.animate.to_edge(UP).scale(0.75), run_time=0.6)
            self.play(FadeIn(router[0:2]), FadeIn(r_arrows), run_time=1.5)
            self.play(FadeIn(router[2]), run_time=1.2)
            self.play(FadeIn(keep_gnn), GrowArrow(a_up), FadeIn(query_llm), GrowArrow(a_dn), run_time=1.5)

        with self.narrated_caption([
            "Vậy hiện nay, các phương pháp dùng những quy tắc kinh nghiệm nào",
            "để quyết định gọi lờ lờ mờ?",
            "Đó là nội dung của phần hai."
        ]):
            circle_hl = Ellipse(width=query_llm.width + 0.4, height=query_llm.height + 0.4, color=gs.C_BAD, stroke_width=4)
            circle_hl.move_to(query_llm)
            question_mark = t("?", size=60, color=gs.C_BAD, weight=BOLD).next_to(circle_hl, RIGHT, buff=0.3)
            
            self.play(Create(circle_hl), run_time=0.8)
            self.play(FadeIn(question_mark, shift=LEFT*0.2), run_time=0.6)
            
            self.wait(2.5)
            self.play(
                FadeOut(q), FadeOut(router), FadeOut(r_arrows),
                FadeOut(keep_gnn), FadeOut(query_llm), FadeOut(a_up), FadeOut(a_dn),
                FadeOut(circle_hl), FadeOut(question_mark),
                run_time=0.7
            )
            task2_title = t("TASK 2", size=64, color=BRIGHT, weight=BOLD)
            task2_sub = t("EXISTING ROUTING HEURISTICS", size=44, color=LIGHT)
            task2_hint = t("Degree · Centrality · Uncertainty", size=28, color=MID)
            t2_group = VGroup(task2_title, task2_sub, task2_hint).arrange(DOWN, buff=0.45)
            self.play(FadeIn(t2_group, shift=UP * 0.2), run_time=1.0)
            # Keep card on screen — DO NOT fade out
            self.wait(2.0)
