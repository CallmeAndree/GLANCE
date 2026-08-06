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
        self.section_3_hybrid_systems()
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

        with self.narrated_caption(["xin chào mọi người.", "trong đoạn phim này, chúng ta sẽ tìm hiểu bài báo gờ lans,"]):
            self.play(Write(title), run_time=1.0)
            self.play(FadeIn(subtitle, shift=UP * 0.2), run_time=0.8)

        with self.narrated_caption(["một nghiên cứu về kết hợp mạng nơ-ron đồ thị", "và mô hình ngôn ngữ lớn."]):
            self.play(
                title.animate.scale(0.5).to_corner(UL),
                FadeOut(subtitle),
                run_time=1.0
            )

        tag_title = t("Text-Attributed Graph (TAG)", size=38, color=BRIGHT, weight=BOLD).to_edge(UP, buff=0.35)
        with self.narrated_caption(["để hiểu vấn đề, trước tiên cần hiểu", "loại dữ liệu mà bài báo đang xử lý:"]):
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

        with self.narrated_caption(["đồ thị có thuộc tính văn bản, hay ti ây gi.", "trong thực tế, văn bản hiếm khi đứng một mình."]):
            self.play(FadeIn(doc1, shift=UP * 0.3), FadeIn(doc2, shift=UP * 0.3), FadeIn(doc3, shift=UP * 0.3), lag_ratio=0.2, run_time=1.2)

        with self.narrated_caption(["bài báo trích dẫn nhau,", "và bài đăng tương tác với nhau."]):
            self.play(GrowArrow(cite_AB), run_time=0.5)
            self.play(GrowArrow(cite_BC), run_time=0.5)
            self.play(Create(cite_AC), run_time=0.4)

        # Target positions for nodes
        graph = create_tag_graph(scale=1.1).move_to(DOWN * 0.3)
        node_A = graph.nodes["A"]
        node_B = graph.nodes["B"]
        node_C = graph.nodes["C"]

        with self.narrated_caption(["mỗi tài liệu trở thành một nót,"]):
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

        with self.narrated_caption(["khi mỗi nót có cả nội dung văn bản", "lẫn kết nối với nót khác,"]):
            # Briefly highlight node A to show text+connections
            self.play(node_A.animate.set_stroke(BRIGHT, width=3.5), run_time=0.8)

        with self.narrated_caption(["ta gọi cấu trúc đó là đồ thị có thuộc tính văn bản."]):
            # Punchline overlaid on graph (not replacing it)
            punch = t("TEXT + CONNECTIONS = ONE GRAPH", size=44, color=BRIGHT, weight=BOLD).set_z_index(100)
            blackout_tag = Rectangle(width=20, height=15, fill_color=BLACK, fill_opacity=0.85).set_z_index(99)
            self.play(FadeIn(blackout_tag), FadeIn(punch, shift=UP * 0.15), run_time=0.7)
            self.wait(1.0) # wait briefly before ending section

        self.tag_graph = graph
        self.tag_punch = punch
        self.tag_blackout = blackout_tag

    # ─────────────────────────────────────────────────────────
    # SECTION 3 — Hybrid Systems
    # ─────────────────────────────────────────────────────────
    def section_3_hybrid_systems(self):
        graph = self.tag_graph
        
        with self.narrated_caption(["trước đây, ti ây gi thường được xử lý", "bằng cách đưa các đặc trưng văn bản đơn giản,"]):
            self.play(FadeOut(self.tag_title), FadeOut(self.tag_punch), FadeOut(self.tag_blackout), run_time=0.4)
            self.play(graph.animate.scale(0.85).move_to(LEFT * 3.5 + UP * 0.5), run_time=0.8)
            
        with self.narrated_caption(["chẳng hạn như tê ép y đê ép", "hoặc véc-tơ biểu diễn tĩnh, vào gờ nờ nờ."]):
            tfidf = t("TF-IDF", size=32, color=LIGHT, weight=BOLD).move_to(RIGHT * 2.5 + UP * 2.0)
            static_we = t("Static Word Embeddings", size=32, color=LIGHT, weight=BOLD).move_to(RIGHT * 2.5 + UP * 1.3)
            self.play(FadeIn(tfidf, shift=LEFT * 0.2), run_time=1.0)
            self.wait(0.8)
            self.play(FadeIn(static_we, shift=LEFT * 0.2), run_time=1.0)
            self.wait(1.2)
            
            simple_text = module("Simple Text Features", width=3.8, height=0.8, emphasized=False).move_to(RIGHT * 2.5 + UP * 1.65)
            self.play(ReplacementTransform(VGroup(tfidf, static_we), simple_text), run_time=1.0)
            
            gnn_mod = module("GNN", width=2.0, height=0.8).move_to(RIGHT * 2.5 + UP * 0.1)
            arr1 = small_arrow(simple_text.get_bottom(), gnn_mod.get_top())
            pred_mod = module("Node Predictions", width=2.5, height=0.8).move_to(RIGHT * 2.5 + DOWN * 1.5)
            arr2 = small_arrow(gnn_mod.get_bottom(), pred_mod.get_top())
            
            self.play(GrowArrow(arr1), FadeIn(gnn_mod), run_time=0.7)
            self.play(GrowArrow(arr2), FadeIn(pred_mod), run_time=0.7)

        with self.narrated_caption(["gần đây, thành công của các mô hình ngôn ngữ lớn", "đã thúc đẩy sự phát triển của", "các kiến trúc lai. sử dụng lờ lờ mờ cho học trên đồ thị."]):
            self.play(
                FadeOut(graph), FadeOut(simple_text), FadeOut(gnn_mod),
                FadeOut(arr1), FadeOut(pred_mod), FadeOut(arr2),
                run_time=0.8
            )
            hybrid_title = t("HYBRID GNN-LLM SYSTEMS", size=48, color=BRIGHT, weight=BOLD)
            self.play(Write(hybrid_title), run_time=1.0)
            self.wait(2.5)
            self.play(FadeOut(hybrid_title), run_time=0.5)

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

        with self.narrated_caption(["các phương pháp hiện nay chia thành hai hướng:", "lờ lờ mờ làm bộ tăng cường và lờ lờ mờ-as-predictor."]):
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
            
            # Show vector enhancement for target node
            vec_raw = custom_feature_vector("Raw", [0.2, 0.3, 0.1, 0.2], color=DIM, width=1.5).move_to(RIGHT * 2.8 + UP * 2.6)
            vec_rich = custom_feature_vector("Enhanced", [0.9, 0.8, 0.9, 0.7], color=BRIGHT, width=1.6).move_to(vec_raw)
            
            self.play(FadeIn(vec_raw, shift=DOWN*0.1), run_time=1.0)
            self.wait(1.5)
            self.play(ReplacementTransform(vec_raw, vec_rich), run_time=1.5)
            self.wait(1.5)
            
            inject_arr = small_arrow(vec_rich.get_bottom(), noisy_nbhd.target.get_top())
            self.play(GrowArrow(inject_arr), run_time=0.8)
            self.play(noisy_nbhd.target[0].animate.set_stroke(BRIGHT), noisy_nbhd.target[1].animate.set_color(BRIGHT), run_time=0.8)
            self.wait(1.0)
            self.play(FadeOut(vec_rich), FadeOut(inject_arr), run_time=0.6)
            noisy_msgs = VGroup(*[create_message_vector(
                n.get_center(), noisy_nbhd.target.get_center(),
                color=DARK if i not in {1, 2, 5, 7} else BRIGHT
            ) for i, n in enumerate(noisy_nbhd.neighbors)])
            self.play(AnimationGroup(*[GrowArrow(m) for m in noisy_msgs], lag_ratio=0.08), run_time=1.0)

        with self.narrated_caption(["tuy nhiên, dù véc-tơ ngữ nghĩa tốt hơn,", "gờ nờ nờ vẫn có thể bị kéo lệch bởi các hàng xóm nhiễu."]):
            # Emphasize the noisy neighbors (indices 1, 2, 5, 7)
            noisy_nodes = VGroup(*[noisy_nbhd.neighbors[i] for i in {1, 2, 5, 7}])
            noisy_arrows = VGroup(*[noisy_msgs[i] for i in {1, 2, 5, 7}])
            
            self.wait(1.8)
            
            # Flash the noisy arrows and target node permanently
            self.play(
                noisy_nodes.animate.set_color(gs.C_BAD),
                noisy_arrows.animate.set_color(gs.C_BAD),
                noisy_nbhd.target[0].animate.set_stroke(gs.C_BAD),
                noisy_nbhd.target[1].animate.set_color(gs.C_BAD),
                run_time=0.8
            )
            # Wiggle it back and forth
            self.play(noisy_nbhd.target.animate.shift(RIGHT * 0.15), rate_func=there_and_back, run_time=0.4)
            self.play(noisy_nbhd.target.animate.shift(LEFT * 0.15), rate_func=there_and_back, run_time=0.4)
            
            self.wait(1.5) # Wait to let the visual sink in
            
            # Punchline ON TOP of the diagram
            bias_text = t("BETTER TEXT ≠ NO STRUCTURAL BIAS", size=44, color=BRIGHT, weight=BOLD).set_z_index(100)
            blackout2 = Rectangle(width=20, height=15, fill_color=BLACK, fill_opacity=0.85).set_z_index(99)
            self.play(
                FadeIn(blackout2),
                FadeIn(bias_text, shift=UP * 0.1), 
                run_time=1.0
            )
            self.wait(1.5)
            
        # Predictor deep-dive
        token_text = t("Prompt Token Count: 128", size=30, color=MID).move_to(LEFT * 2.8 + DOWN * 0.4)
        with self.narrated_caption(["lờ lờ mờ-as-predictor đổi toàn bộ thông tin", "thành một câu lệnh văn bản dài."]):
            pred_group.move_to(RIGHT * 2.5 + DOWN * 0.1).scale(1.08)
            self.play(
                FadeOut(noisy_nbhd), FadeOut(noisy_msgs), FadeOut(blackout2), FadeOut(bias_text),
                FadeOut(enh_group),
                FadeIn(pred_group),
                run_time=0.8
            )
            self.play(Write(token_text), run_time=0.4)

        with self.narrated_caption(["vùng lân cận càng mở rộng,", "chuỗi văn bản càng dài và đắt đỏ hơn."]):
            blackout3 = Rectangle(width=25, height=15, fill_color=BLACK, fill_opacity=0.85).set_z_index(80)
            self.play(FadeIn(blackout3), run_time=0.5)

            # Helpers for visualization
            def create_hop_nodes(labels, radius, color, center):
                nodes = VGroup()
                edges = VGroup()
                angle_step = TAU / len(labels)
                for i, lbl in enumerate(labels):
                    pos = center + radius * np.array([np.cos(i * angle_step), np.sin(i * angle_step), 0])
                    n = node(lbl, radius=0.18).move_to(pos)
                    n[0].set_stroke(color)
                    n[1].set_color(color)
                    e = Line(center, pos, color=DIM, stroke_width=1.5).set_z_index(85)
                    nodes.add(n)
                    edges.add(e)
                nodes.set_z_index(90)
                return nodes, edges

            def make_sequence(labels, colors, show_dots=False, final_node=None, final_color=None):
                boxes = VGroup()
                for lbl, col in zip(labels, colors):
                    b = panel(0.4, 0.4, fill=BG, stroke=col).set_opacity(0.8)
                    t_lbl = t(lbl, size=14, color=col).move_to(b)
                    boxes.add(VGroup(b, t_lbl))
                if show_dots:
                    boxes.add(t("...", size=24, color=LIGHT))
                if final_node:
                    b = panel(0.4, 0.4, fill=BG, stroke=final_color).set_opacity(0.8)
                    t_lbl = t(final_node, size=14, color=final_color).move_to(b)
                    boxes.add(VGroup(b, t_lbl))
                boxes.arrange(RIGHT, buff=0.08)
                return boxes.set_z_index(90)

            graph_center = LEFT * 3.5 + UP * 0.5
            target_A = node("A", radius=0.25).move_to(graph_center).set_z_index(90)
            target_A[0].set_stroke(BRIGHT)
            target_A[1].set_color(BRIGHT)

            # Stage 1
            nodes_1, edges_1 = create_hop_nodes(["B", "C", "D", "E"], 0.8, WHITE, graph_center)
            lbl_1 = t("1-hop context", size=20, color=WHITE).move_to(graph_center + DOWN * 2.9).set_z_index(90)
            seq_1 = make_sequence(["A", "B", "C", "D", "E"], [BRIGHT] + [WHITE]*4).move_to(RIGHT * 3.0 + UP * 0.5)
            
            c1_nodes = t("Graph nodes: 5", size=22, color=LIGHT)
            c1_toks = t("Text tokens: 80", size=22, color=LIGHT)
            counters = VGroup(c1_nodes, c1_toks).arrange(DOWN, aligned_edge=LEFT).to_corner(UR, buff=0.6).set_z_index(90)
            
            serialize_arr = small_arrow(LEFT * 1.0 + UP * 0.5, RIGHT * 0.5 + UP * 0.5).set_z_index(90)
            serialize_txt = t("Serialize", size=20, color=LIGHT).next_to(serialize_arr, UP, buff=0.1).set_z_index(90)

            self.play(
                FadeIn(target_A), FadeIn(nodes_1), FadeIn(edges_1), FadeIn(lbl_1),
                GrowArrow(serialize_arr), FadeIn(serialize_txt),
                FadeIn(seq_1), FadeIn(counters),
                run_time=1.0
            )
            self.wait(0.5)

            # Stage 2
            nodes_2, edges_2 = create_hop_nodes(["F", "G", "H", "I", "J", "K", "L", "M"], 1.6, LIGHT, graph_center)
            lbl_2 = t("2-hop context", size=20, color=LIGHT).move_to(lbl_1).set_z_index(90)
            seq_2 = make_sequence(["A", "B", "C", "D", "E", "F", "G", "H", "I"], [BRIGHT] + [WHITE]*4 + [LIGHT]*4, show_dots=True).move_to(RIGHT * 3.0 + UP * 0.5)
            c2_nodes = t("Graph nodes: 18", size=22, color=LIGHT)
            c2_toks = t("Text tokens: 420", size=22, color=LIGHT)
            counters_2 = VGroup(c2_nodes, c2_toks).arrange(DOWN, aligned_edge=LEFT).to_corner(UR, buff=0.6).set_z_index(90)

            self.play(
                FadeOut(lbl_1), FadeIn(lbl_2),
                FadeIn(nodes_2), FadeIn(edges_2),
                ReplacementTransform(seq_1, seq_2),
                ReplacementTransform(counters, counters_2),
                run_time=1.0
            )
            self.wait(0.5)

            # Stage 3
            nodes_3, edges_3 = create_hop_nodes(["N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y"], 2.4, MID, graph_center)
            lbl_3 = t("3-hop context", size=20, color=MID).move_to(lbl_1).set_z_index(90)
            seq_3 = make_sequence(["A", "B", "C", "D", "E", "F", "G", "H", "I"], [BRIGHT] + [WHITE]*4 + [LIGHT]*4, show_dots=True, final_node="N", final_color=MID).move_to(RIGHT * 3.0 + UP * 0.5)
            c3_nodes = t("Graph nodes: 52", size=22, color=LIGHT)
            c3_toks = t("Text tokens: 1,300", size=22, color=RED)
            counters_3 = VGroup(c3_nodes, c3_toks).arrange(DOWN, aligned_edge=LEFT).to_corner(UR, buff=0.6).set_z_index(90)

            self.play(
                FadeOut(lbl_2), FadeIn(lbl_3),
                FadeIn(nodes_3), FadeIn(edges_3),
                ReplacementTransform(seq_2, seq_3),
                ReplacementTransform(counters_2, counters_3),
                run_time=1.0
            )
            
            # Highlight counter
            self.play(c3_toks.animate.scale(1.2), run_time=0.4, rate_func=there_and_back)
            
            # Punchline
            punchline1 = t("Larger graph context -> Longer text sequence", size=32, color=BRIGHT, weight=BOLD)
            punchline2 = t("More tokens, higher LLM cost", size=26, color=RED)
            punch_group = VGroup(punchline1, punchline2).arrange(DOWN, buff=0.2).move_to(ORIGIN).set_z_index(100)
            
            blackout_punch = Rectangle(width=20, height=15, fill_color=BLACK, fill_opacity=0.85).set_z_index(95)
            
            self.play(FadeIn(blackout_punch), FadeIn(punch_group, shift=UP*0.2), run_time=1.0)
            self.wait(1.5)
            
            graph_loss = VGroup(target_A, nodes_1, edges_1, nodes_2, edges_2, nodes_3, edges_3, lbl_3, serialize_arr, serialize_txt, seq_3, counters_3, blackout_punch, punch_group)
            
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

        with self.narrated_caption(["dù dùng bộ tăng cường hay bộ dự đoán,", "nhiều phương pháp áp cùng một chiến lược kết hợp cho mọi nót."]):
            self.play(FadeIn(node_a), FadeIn(node_b), FadeIn(node_c), run_time=0.7)
            self.play(FadeIn(strategy_box), run_time=0.6)
            self.play(GrowArrow(arr_a), GrowArrow(arr_b), GrowArrow(arr_c), run_time=0.8)

        with self.narrated_caption(["bài báo gọi đây là static fusion, hay kết hợp tĩnh."]):
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

        with self.narrated_caption(["ba nót có thể rất khác nhau.", "nót a được gờ nờ nờ xử lý tốt."]):
            self.play(FadeOut(node_b), FadeOut(node_c), run_time=0.5)
            self.play(ReplacementTransform(node_a, group_A.target), run_time=0.8)
            self.play(Write(title_A), FadeIn(group_A.neighbors), FadeIn(group_A.edges), FadeIn(doc_A), run_time=1.0)

        with self.narrated_caption(["hàng xóm đồng thuận, gờ nờ nờ tạo véc-tơ ổn định."]):
            msgs_A = VGroup(*[create_message_vector(n.get_center(), group_A.target.get_center(), color=LIGHT)
                               for n in group_A.neighbors])
            self.play(AnimationGroup(*[GrowArrow(m) for m in msgs_A], lag_ratio=0.1), run_time=1.0)
            self.play(FadeIn(gnn_bar_A), run_time=0.7)

        with self.narrated_caption(["gờ nờ nờ dự đoán đúng. gọi lờ lờ mờ là không cần thiết."]):
            skip_label = t("[SKIP LLM]", size=34, color=gs.C_GOOD, weight=BOLD).next_to(gnn_bar_A, DOWN, buff=0.4)
            self.play(FadeIn(skip_label, shift=UP * 0.1), run_time=0.6)
            self.wait(0.4)

        # ── NODE B ──────────────────────────────────────────
        title_B = t("Node B: Noisy Structure, Clear Text", size=34, color=BRIGHT, weight=BOLD).to_edge(UP, buff=0.35)
        group_B = create_target_neighborhood(kind="noisy", label="B", scale=0.95).move_to(LEFT * 4 + UP * 0.4)
        doc_B = create_text_document("Node B", ["Graph Learning", "Heterophily", "Node Classification"], width=3.2, height=1.6).move_to(RIGHT * 3.5 + UP * 1.8)
        gnn_bar_B = probability_vector("GNN Prediction", [0.20, 0.65, 0.15], emphasized_index=1).move_to(RIGHT * 1.8 + DOWN * 0.8).scale(1.1)

        with self.narrated_caption(["nót b có vùng lân cận chứa nhiều loại khác nhau."]):
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

        with self.narrated_caption(["các tín hiệu kéo nhiều hướng, gờ nờ nờ dự đoán sai."]):
            msgs_B = VGroup(*[create_message_vector(
                n.get_center(), group_B.target.get_center(),
                color=DARK if i not in {1, 2, 5, 7} else BRIGHT
            ) for i, n in enumerate(group_B.neighbors)])
            self.play(AnimationGroup(*[GrowArrow(m) for m in msgs_B], lag_ratio=0.1), run_time=1.0)
            self.play(ReplacementTransform(gnn_bar_A, gnn_bar_B), run_time=0.7)
            wrong_B = t("GNN: WRONG", color=gs.C_BAD, weight=BOLD, size=24).next_to(gnn_bar_B, DOWN, buff=0.15)
            self.play(FadeIn(wrong_B), run_time=0.4)

        with self.narrated_caption(["nhưng văn bản nót b rất rõ ràng.", "lờ lờ mờ sửa lại dự đoán thành công."]):
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

        with self.narrated_caption(["nót c cũng khó với gờ nờ nờ.", "nhưng văn bản lại rất mơ hồ."]):
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

        with self.narrated_caption(["lờ lờ mờ không đủ bằng chứng để sửa kết quả.", "cả hai mô hình đều thất bại."]):
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

        with self.narrated_caption(["nót b và nót c đều khó với gờ nờ nờ.", "nhưng chỉ nót b nhận được lợi ích từ lờ lờ mờ."]):
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
        with self.narrated_caption(["đây là điểm mấu chốt của bài báo."]):
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
        with self.narrated_caption(["sự khác biệt này giải thích vì sao", "độ chính xác tổng thể có thể tăng rất ít."]):
            self.play(
                FadeOut(self.comparison_objects, shift=UP * 0.3),
                run_time=0.8
            )

        with self.narrated_caption(["giả sử chín mươi phần trăm là các nót dễ,", "còn mười phần trăm là các nót khó."]):
            easy_group = VGroup(
                t("90% Easy Nodes", size=38, color=BRIGHT, weight=BOLD),
                t("GNN: 95%  ->  Fusion: 94%", size=26, color=LIGHT)
            ).arrange(DOWN, buff=0.2).move_to(LEFT * 3.2 + UP * 1.4)
            hard_group = VGroup(
                t("10% Hard Nodes", size=38, color=BRIGHT, weight=BOLD),
                t("GNN: 40%  ->  Fusion: 53%", size=26, color=LIGHT)
            ).arrange(DOWN, buff=0.2).move_to(RIGHT * 3.2 + UP * 1.4)
            self.play(FadeIn(easy_group, shift=UP * 0.2), FadeIn(hard_group, shift=UP * 0.2), run_time=1.0)

        with self.narrated_caption(["trên nhóm khó, lờ lờ mờ giúp tăng mười ba điểm phần trăm."]):
            gnn_eq = mt(r"\text{GNN: } 0.9{\times}95\% + 0.1{\times}40\% = 89.5\%", size=38).move_to(DOWN * 0.5)
            self.play(Write(gnn_eq), run_time=0.9)
            gain_hard = t("Hard-node gain: +13%", size=28, color=gs.C_GOOD, weight=BOLD).next_to(hard_group, DOWN, buff=0.4)
            self.play(FadeIn(gain_hard, shift=UP * 0.1), run_time=0.6)

        with self.narrated_caption(["nhưng trên toàn đồ thị, tổng thể chỉ tăng 0.4 điểm."]):
            fusion_eq = mt(r"\text{Fusion: } 0.9{\times}94\% + 0.1{\times}53\% = 89.9\%", size=38).next_to(gnn_eq, DOWN, buff=0.4)
            self.play(TransformFromCopy(gnn_eq, fusion_eq), run_time=0.9)
            self.play(gnn_eq.animate.set_opacity(0.3), run_time=0.4)
            gain_overall = t("Overall gain: +0.4 percentage points", size=28, color=MID).next_to(fusion_eq, DOWN, buff=0.3)
            self.play(FadeIn(gain_overall), run_time=0.5)

        with self.narrated_caption(["lợi ích lớn ở một nhóm nhỏ trông rất nhỏ khi tính tổng."]):
            takeaway = t("LARGE SUBGROUP GAINS CAN LOOK SMALL IN AGGREGATE", size=30, color=BRIGHT, weight=BOLD).move_to(DOWN * 3.2)
            self.play(FadeIn(takeaway, shift=UP * 0.1), run_time=0.7)
            self.wait(0.8)

        self.sec9_objects = VGroup(easy_group, hard_group, gnn_eq, fusion_eq, gain_hard, gain_overall, takeaway)

    # ─────────────────────────────────────────────────────────
    # SECTION 10 — GLANCE Research Question & Task 2
    # ─────────────────────────────────────────────────────────
    def section_10_glance_question(self):
        with self.narrated_caption(["tóm lại, khó với gờ nờ nờ chưa chắc có lợi từ lờ lờ mờ."]):
            self.play(FadeOut(self.sec9_objects, shift=UP * 0.3), run_time=0.7)
            beat1 = VGroup(
                t("GNN DIFFICULTY", size=46, color=LIGHT, weight=BOLD),
                t("≠", size=70, color=gs.C_BAD, weight=BOLD),
                t("LLM BENEFIT", size=46, color=BRIGHT, weight=BOLD),
            ).arrange(DOWN, buff=0.38)
            self.play(FadeIn(beat1, shift=UP * 0.2), run_time=0.8)
            self.wait(0.5)

        with self.narrated_caption(["vậy nót nào thực sự đáng để gọi lờ lờ mờ?"]):
            self.play(FadeOut(beat1), run_time=0.6)
            q = t("WHICH NODES SHOULD QUERY THE LLM?", size=44, color=gs.C_GOOD, weight=BOLD)
            self.play(Write(q), run_time=0.9)

            # Router pipeline fades in below question
            router = VGroup(
                module("Node"), module("GNN"), module("Router", emphasized=True)
            ).arrange(RIGHT, buff=0.6).move_to(LEFT * 1.5 + DOWN * 1.0)
            r_arrows = VGroup(*[small_arrow(router[i].get_right(), router[i+1].get_left()) for i in range(2)])
            keep_gnn = module("Keep GNN", width=2.4).move_to(router[2].get_center() + RIGHT * 2.6 + UP * 1.0)
            query_llm = module("Query LLM", width=2.4, emphasized=True).move_to(router[2].get_center() + RIGHT * 2.6 + DOWN * 1.0)
            a_up = small_arrow(router[2].get_right() + UP * 0.15, keep_gnn.get_left())
            a_dn = small_arrow(router[2].get_right() + DOWN * 0.15, query_llm.get_left())

            self.play(q.animate.to_edge(UP).scale(0.75), run_time=0.6)
            self.play(FadeIn(router[0:2]), FadeIn(r_arrows), run_time=1.5)
            self.play(FadeIn(router[2]), run_time=1.2)
            self.play(FadeIn(keep_gnn), GrowArrow(a_up), FadeIn(query_llm), GrowArrow(a_dn), run_time=1.5)

        with self.narrated_caption([
            "vậy hiện nay, các phương pháp dùng những quy tắc kinh nghiệm nào",
            "để quyết định gọi lờ lờ mờ?",
            "đó là nội dung của phần hai."
        ]):
            box_hl = SurroundingRectangle(query_llm, color=gs.C_GOOD, buff=0.15, corner_radius=0.1)
            question_mark = t("?", size=48, color=gs.C_GOOD, weight=BOLD).next_to(box_hl, RIGHT, buff=0.25)
            
            self.play(Create(box_hl), run_time=0.8)
            self.play(FadeIn(question_mark, shift=LEFT*0.2), run_time=0.6)
            
            self.wait(2.5)
            self.play(
                FadeOut(q), FadeOut(router), FadeOut(r_arrows),
                FadeOut(keep_gnn), FadeOut(query_llm), FadeOut(a_up), FadeOut(a_dn),
                FadeOut(box_hl), FadeOut(question_mark),
                run_time=0.7
            )
            task2_title = t("TASK 2", size=64, color=BRIGHT, weight=BOLD)
            task2_sub = t("EXISTING ROUTING HEURISTICS", size=44, color=LIGHT)
            task2_hint = t("Degree · Centrality · Uncertainty", size=28, color=MID)
            t2_group = VGroup(task2_title, task2_sub, task2_hint).arrange(DOWN, buff=0.45)
            self.play(FadeIn(t2_group, shift=UP * 0.2), run_time=1.0)
            # Keep card on screen — DO NOT fade out
            self.wait(2.0)
