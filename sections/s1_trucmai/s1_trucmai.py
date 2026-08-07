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
ASSET_DIR = pathlib.Path(__file__).resolve().parent / "assets"

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

def probability_vector(label, values, width=2.8, emphasized_index=None,
                       color=None, class_names=None, true_index=None):
    """Thanh xác suất theo lớp. Truyền class_names + true_index để hiện tên lớp và
    nhãn đúng (ground truth), nếu không WRONG/CORRECT sẽ không có căn cứ trực quan.
    color = màu thanh nhấn (C_GNN cho GNN, C_LLM cho LLM); mặc định BRIGHT."""
    color = color if color is not None else BRIGHT
    box_width = width + (0.62 if class_names else 0.0)
    title = t(label, 18, LIGHT, BOLD)
    bar_width = width - 1.0
    rows = VGroup()
    for index, value in enumerate(values):
        track = Line(ORIGIN, RIGHT * bar_width, color=DARK, stroke_width=5)
        fill_color = color if index == emphasized_index else MID
        fill = Line(track.get_start(), track.point_from_proportion(value), color=fill_color, stroke_width=5)
        number = t(f"{value:.2f}", 13, LIGHT)
        parts = []
        if class_names:
            is_true = index == true_index
            parts.append(t(class_names[index], 12,
                           INK if is_true else MID, weight=BOLD if is_true else NORMAL))
        parts += [VGroup(track, fill), number]
        rows.add(VGroup(*parts).arrange(RIGHT, buff=0.12))
    rows.arrange(DOWN, aligned_edge=LEFT, buff=0.13)
    stack = [title, rows]
    if class_names and true_index is not None:
        stack.append(t(f"True: {class_names[true_index]}", 13, gs.C_GOOD))
    content = VGroup(*stack).arrange(DOWN, buff=0.14)
    box = panel(box_width, content.height + 0.34, stroke=DIM, fill=BG, opacity=0.82)
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
            self.wait(0.7)

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
        """Opening: dữ liệu không tồn tại độc lập (18–22 giây).

        Bốn nhịp theo kịch bản:
          0:00–0:06  các hồ sơ người dùng rời rạc trên nền tối
          0:06–0:12  bài đăng hiện trên hồ sơ, liên kết xã hội dần hình thành
          0:12–0:17  nội dung và tín hiệu tổng hợp từ đồ thị chạy về trung tâm
          0:17–0:22  hai luồng hội tụ -> tiêu đề + poster

        Opening chỉ tạo bối cảnh chung. Mọi khái niệm kỹ thuật (TAG, GNN,
        LLM, router, nót dễ/khó) để các section sau giới thiệu.
        Gradient nhận diện: Content = LLM cam, Graph Structure = GNN xanh,
        điểm hội tụ = Router tím.
        """
        # ── Nhịp 1 (0:00–0:06): các hồ sơ mạng xã hội xuất hiện riêng lẻ ──
        card_specs = [
            ("User A", LEFT * 4.3 + UP * 1.15, gs.C_GNN),
            ("User B", RIGHT * 0.15 + UP * 1.55, gs.C_LLM),
            ("User C", RIGHT * 4.4 + UP * 0.95, gs.C_ROUTER),
            ("User D", LEFT * 3.1 + DOWN * 1.75, gs.C_SIGNAL),
            ("User E", RIGHT * 2.9 + DOWN * 1.85, gs.C_GOOD),
        ]
        cards = VGroup()
        for name, pos, accent in card_specs:
            box = RoundedRectangle(
                width=2.25, height=1.35, corner_radius=0.12,
                stroke_color=gs.C_EDGE, stroke_width=2.0,
                fill_color=gs.C_PANEL, fill_opacity=0.92,
            )
            avatar_ring = Circle(
                radius=0.25,
                stroke_color=accent,
                stroke_width=2.2,
                fill_color=accent,
                fill_opacity=0.13,
            )
            avatar_head = Dot(radius=0.065, color=accent).shift(UP * 0.075)
            avatar_body = Arc(
                radius=0.125,
                start_angle=0,
                angle=PI,
                color=accent,
                stroke_width=3.0,
            ).shift(DOWN * 0.105)
            avatar = VGroup(avatar_ring, avatar_head, avatar_body)
            avatar.move_to(box.get_left() + RIGHT * 0.42 + UP * 0.28)

            head = t(name, size=20, color=accent, weight=BOLD)
            head.next_to(avatar, RIGHT, buff=0.16)
            head.align_to(avatar, UP)
            card = VGroup(box, avatar, head).move_to(pos)
            card.head = head
            cards.add(card)
        cards.set_z_index(2)

        with self.narrated_caption([
            "Trong thế giới thực,",
            "thông tin hiếm khi tồn tại một cách độc lập.",
        ]):
            self.play(
                LaggedStart(
                    *[FadeIn(c, scale=0.88) for c in cards],
                    lag_ratio=0.22,
                ),
                run_time=2.6,
            )

        # ── Nhịp 2 (0:06–0:12): bài đăng hiện trên hồ sơ, liên kết hình thành ──
        # Các vạch văn bản tượng trưng cho bài đăng riêng của từng người dùng.
        contents = VGroup()
        for card in cards:
            lines = VGroup()
            for i, w in enumerate((1.55, 1.30, 1.00)):
                lines.add(Line(
                    ORIGIN, RIGHT * w,
                    stroke_width=3.2,
                    color=gs.C_LLM if i == 0 else gs.C_EDGE,
                ))
            lines.arrange(DOWN, buff=0.13, aligned_edge=LEFT)
            lines.move_to(card[0].get_center() + DOWN * 0.34)
            lines.align_to(card[0].get_left() + RIGHT * 0.22, LEFT)
            contents.add(lines)
        contents.set_z_index(3)

        link_pairs = [(0, 1), (1, 2), (0, 3), (1, 4), (3, 4), (2, 4)]
        links = VGroup(*[
            Line(
                cards[a].get_center(), cards[b].get_center(),
                stroke_width=2.2, color=gs.C_GNN,
            ).set_opacity(0.55)
            for a, b in link_pairs
        ])
        links.set_z_index(1)

        with self.narrated_caption([
            "Mỗi đối tượng vừa mang nội dung riêng,",
            "vừa được kết nối với nhiều đối tượng khác.",
        ]):
            self.play(
                LaggedStart(
                    *[Write(c) for c in contents],
                    lag_ratio=0.16,
                ),
                run_time=1.7,
            )
            self.play(
                LaggedStart(
                    *[Create(l) for l in links],
                    lag_ratio=0.13,
                ),
                run_time=1.9,
            )

        # ── Nhịp 3 (0:12–0:17): khai thác nội dung và cấu trúc đồ thị ──
        network = VGroup(cards, contents, links)

        core = Dot(radius=0.15, color=gs.C_ROUTER).set_z_index(6)
        core.move_to(ORIGIN)

        # Bên trái: nội dung của một người dùng được tách khỏi mạng xã hội.
        # Dùng bản sao của chính hồ sơ User B để giữ mạch hình liên tục.
        content_source = VGroup(cards[1].copy(), contents[1].copy())
        content_source.scale(1.12).move_to(LEFT * 4.45 + DOWN * 0.10).set_z_index(6)
        lbl_content = t("TEXT CONTENT", size=24, color=gs.C_LLM, weight=BOLD)
        lbl_content.next_to(content_source, UP, buff=0.35).set_z_index(6)

        # Bên phải: ego-network của User B. Các avatar hàng xóm truyền thông tin
        # dọc theo cạnh vào user mục tiêu, thay vì chỉ hiện một nhãn Relationships.
        graph_center = RIGHT * 4.45 + DOWN * 0.10
        graph_positions = [
            graph_center,
            graph_center + LEFT * 1.25 + UP * 1.05,
            graph_center + RIGHT * 1.25 + UP * 0.95,
            graph_center + LEFT * 1.15 + DOWN * 1.20,
            graph_center + RIGHT * 1.20 + DOWN * 1.15,
        ]
        graph_card_indices = [1, 0, 2, 3, 4]
        graph_nodes = VGroup(*[
            cards[index][1].copy().scale(0.82).move_to(pos)
            for index, pos in zip(graph_card_indices, graph_positions)
        ]).set_z_index(6)
        target_node = graph_nodes[0]
        target_ring = Circle(
            radius=0.34,
            stroke_color=gs.C_ROUTER,
            stroke_width=2.6,
        ).move_to(target_node).set_z_index(5)
        target_label = t("TARGET USER", size=13, color=gs.C_ROUTER, weight=BOLD)
        target_label.next_to(target_node, DOWN, buff=0.22).set_z_index(6)

        graph_edges = VGroup(*[
            Line(
                graph_nodes[index].get_center(), target_node.get_center(),
                color=gs.C_EDGE, stroke_width=2.4,
            )
            for index in range(1, len(graph_nodes))
        ]).set_z_index(4)
        # Hai cạnh phụ giữ cảm giác đây là một mạng, không phải bốn input độc lập.
        graph_edges.add(
            Line(graph_nodes[1].get_center(), graph_nodes[3].get_center(),
                 color=gs.C_EDGE, stroke_width=1.8),
            Line(graph_nodes[2].get_center(), graph_nodes[4].get_center(),
                 color=gs.C_EDGE, stroke_width=1.8),
        )
        graph_focus = VGroup(graph_edges, graph_nodes, target_ring, target_label)
        lbl_rel = t("GRAPH STRUCTURE", size=24, color=gs.C_GNN, weight=BOLD)
        lbl_rel.move_to(graph_center + UP * 1.95).set_z_index(6)

        arr_content = small_arrow(
            content_source.get_right(), core.get_left(), color=gs.C_LLM, buff=0.30
        ).set_z_index(5)
        arr_rel = small_arrow(
            target_node.get_left(), core.get_right(), color=gs.C_GNN, buff=0.30
        ).set_z_index(5)

        with self.narrated_caption([
            "Việc khai thác đồng thời hai nguồn thông tin này",
            "mở ra nhiều cơ hội,",
            "nhưng cũng đặt ra những thách thức mới.",
        ]):
            self.play(network.animate.set_opacity(0.08), run_time=0.6)
            self.play(
                FadeIn(content_source, shift=RIGHT * 0.25),
                FadeIn(lbl_content, shift=DOWN * 0.12),
                FadeIn(graph_focus),
                FadeIn(lbl_rel, shift=DOWN * 0.12),
                run_time=0.8,
            )

            # Hàng xóm sáng tuần tự, sau đó message chạy dọc các cạnh về target.
            active_edges = graph_edges[:4]
            self.play(
                LaggedStart(
                    *[edge.animate.set_color(gs.C_GNN).set_stroke(width=3.2)
                      for edge in active_edges],
                    lag_ratio=0.16,
                ),
                LaggedStart(
                    *[Indicate(node_m, color=gs.C_GNN, scale_factor=1.10)
                      for node_m in graph_nodes[1:]],
                    lag_ratio=0.16,
                ),
                run_time=0.8,
            )
            graph_messages = VGroup(*[
                Dot(radius=0.065, color=gs.C_GNN).move_to(node_m)
                for node_m in graph_nodes[1:]
            ]).set_z_index(7)
            self.add(graph_messages)
            self.play(
                LaggedStart(
                    *[
                        MoveAlongPath(
                            message,
                            Line(message.get_center(), target_node.get_center()),
                        )
                        for message in graph_messages
                    ],
                    lag_ratio=0.10,
                ),
                run_time=0.9,
            )
            self.play(
                FadeOut(graph_messages, scale=0.4),
                Indicate(target_ring, color=gs.C_ROUTER, scale_factor=1.12),
                GrowArrow(arr_content),
                GrowArrow(arr_rel),
                run_time=0.7,
            )

            # Hai tín hiệu đã được trích xuất cùng chạy về điểm hội tụ.
            p_content = Dot(radius=0.09, color=gs.C_LLM).set_z_index(7)
            p_rel = Dot(radius=0.09, color=gs.C_GNN).set_z_index(7)
            p_content.move_to(arr_content.get_start())
            p_rel.move_to(arr_rel.get_start())
            self.play(
                MoveAlongPath(p_content, Line(arr_content.get_start(), core.get_center())),
                MoveAlongPath(p_rel, Line(arr_rel.get_start(), core.get_center())),
                run_time=0.8,
            )
            self.play(
                FadeOut(p_content, scale=0.4), FadeOut(p_rel, scale=0.4),
                FadeIn(core, scale=0.5),
                run_time=0.4,
            )

        # ── Nhịp 4 (0:17–0:22): hội tụ -> tiêu đề + poster ──
        title = t("GLANCE for Context", size=46, color=gs.C_ROUTER, weight=BOLD)
        title.set_color_by_gradient(gs.C_GNN, gs.C_ROUTER, gs.C_LLM)  # gradient nhận diện GLANCE
        subtitle = t(
            "Learning When to Leverage LLMs\nfor Node-Aware GNN-LLM Fusion",
            size=25,
            color=MID,
            line_spacing=0.8,
        )
        subtitle.scale_to_fit_width(6.4)
        title_block = VGroup(title, subtitle).arrange(DOWN, buff=0.34)
        title_block.to_edge(LEFT, buff=0.8).set_z_index(8)

        poster = ImageMobject(str(ASSET_DIR / "iclr_2026_poster.png"))
        poster.scale_to_fit_width(5.9).to_edge(RIGHT, buff=0.6)
        if poster.height > 6.2:
            poster.scale_to_fit_height(6.2).to_edge(RIGHT, buff=0.6)
        poster_border = SurroundingRectangle(poster, color=gs.C_EDGE, buff=0.08, stroke_width=2)
        poster_group = Group(poster, poster_border).set_z_index(8)

        with self.narrated_caption([
            "Trong vi đi ô này, chúng ta sẽ cùng tìm hiểu",
            "cách gờ lans for context tiếp cận bài toán đó.",
        ]) as tracker:
            # Hai luồng hội tụ vào tâm rồi bung ra thành tiêu đề.
            self.play(
                FadeOut(arr_content), FadeOut(arr_rel),
                FadeOut(content_source), FadeOut(graph_focus),
                lbl_content.animate.move_to(core.get_center()).set_opacity(0),
                lbl_rel.animate.move_to(core.get_center()).set_opacity(0),
                run_time=0.8,
            )
            # Giữ nền ở 0.12 chứ không tắt hẳn: ở 0.07 khung hình gần như đen
            # trong lúc core đang biến thành title, tạo một nhịp trống thấy rõ.
            self.play(
                Flash(core, color=gs.C_ROUTER, line_length=0.28,
                      num_lines=14, flash_radius=0.55),
                network.animate.set_opacity(0.12),
                run_time=0.7,
            )
            # Title và poster vào cùng lúc để không có khoảng trống giữa hai nhịp.
            self.play(
                FadeOut(core, scale=1.8),
                FadeIn(title, scale=0.88),
                FadeIn(poster_group, shift=LEFT * 0.25),
                run_time=0.9,
            )
            self.play(FadeIn(subtitle, shift=UP * 0.2), run_time=0.6)
            # Title card phải đứng lại tới hết câu thoại, nếu không cảnh bị cắt
            # sớm và khán giả chưa kịp đọc tên bài báo. Bù đúng phần audio còn
            # lại thay vì đoán bằng self.wait() cố định.
            if tracker is not None:
                self.wait(max(0.6, tracker.duration - 4.0))
            else:
                self.wait(0.8)

        # Dọn sạch để section 2 mở trên nền trống.
        self.play(
            FadeOut(network), FadeOut(title), FadeOut(subtitle),
            FadeOut(poster_group), FadeOut(lbl_content), FadeOut(lbl_rel),
            run_time=0.7,
        )

        self.glance_title = title
    # ─────────────────────────────────────────────────────────
    # SECTION 2 — Text-Attributed Graphs (TAG)
    # ─────────────────────────────────────────────────────────
    def section_2_tag(self):
        # ── Beat 1: một tài liệu văn bản, rồi lộ ra cả một mạng lưới ──
        paper = create_text_document(
            "Paper A",
            ["Title: A GNN survey", "Abstract: methods, graphs,", "benchmarks and results"],
            width=4.1, height=2.4, emphasized=True,
        ).move_to(UP * 0.05)
        paper.heading.set_color(gs.C_LLM)     # văn bản = LLM/amber
        paper[0].set_stroke(gs.C_LLM)

        doc1 = doc_icon("Paper A", ["Title", "Abstract"], width=2.3, height=1.45).move_to(LEFT * 4.3 + UP * 0.35)
        doc2 = doc_icon("Paper B", ["Title", "Abstract"], width=2.3, height=1.45).move_to(UP * 0.35)
        doc3 = doc_icon("Paper C", ["Title", "Abstract"], width=2.3, height=1.45).move_to(RIGHT * 4.3 + UP * 0.35)

        with self.narrated_caption([
            "Hãy hình dung một mạng lưới học thuật kết nối bằng các trích dẫn.",
            "Mỗi bài báo có tiêu đề và tóm tắt riêng,",
            "và được nối với những bài báo mà nó trích dẫn.",
        ]):
            self.play(FadeIn(paper, shift=UP * 0.25), run_time=1.0)
            # "camera thu nhỏ": tài liệu co lại, lộ ra các tài liệu khác quanh nó
            self.play(ReplacementTransform(paper, doc1), run_time=0.7)
            self.play(FadeIn(doc2, shift=UP * 0.2), FadeIn(doc3, shift=UP * 0.2), lag_ratio=0.2, run_time=0.8)

        # ── Beat 2: mỗi tài liệu thành một nót, mỗi trích dẫn thành một cạnh ──
        cite_AB = Arrow(doc1.get_right(), doc2.get_left(), buff=0.1, color=MID, stroke_width=2, tip_length=0.12)
        cite_BC = Arrow(doc2.get_right(), doc3.get_left(), buff=0.1, color=MID, stroke_width=2, tip_length=0.12)
        cite_AC = Arrow(doc1.get_top() + UP * 0.1, doc3.get_top() + UP * 0.1, path_arc=-1.2, color=DIM, stroke_width=1.5, tip_length=0.10)

        graph = create_tag_graph(scale=1.1).move_to(DOWN * 0.35)
        node_A = graph.nodes["A"]
        node_B = graph.nodes["B"]
        node_C = graph.nodes["C"]
        other_nodes = VGroup(*[n for k, n in graph.nodes.items() if k not in ["A", "B", "C"]])

        with self.narrated_caption([
            "Các bài báo trích dẫn lẫn nhau.",
            "Mỗi bài trở thành một nót, mỗi trích dẫn thành một cạnh.",
        ]):
            self.play(GrowArrow(cite_AB), GrowArrow(cite_BC), Create(cite_AC), run_time=0.8)
            self.play(
                ReplacementTransform(doc1, node_A),
                ReplacementTransform(doc2, node_B),
                ReplacementTransform(doc3, node_C),
                FadeOut(cite_AB), FadeOut(cite_BC), FadeOut(cite_AC),
                run_time=1.1,
            )
            self.play(Create(graph.edges), FadeIn(other_nodes, lag_ratio=0.1), run_time=1.0)
            # "chạm vào một nót thì văn bản của nó bung ra"
            callout = doc_icon("Paper B", ["Title", "Abstract"], width=2.4, height=1.3).move_to(LEFT * 4.5 + UP * 1.35)
            link = small_arrow(callout.get_right(), node_B.get_left(), color=DIM, buff=0.12)
            callout.heading.set_color(gs.C_LLM)   # văn bản node = amber
            self.play(node_B.animate.set_stroke(gs.C_GNN, width=3.0), GrowArrow(link),
                      FadeIn(callout, shift=RIGHT * 0.15), run_time=1.0)
            self.play(FadeOut(callout), FadeOut(link), node_B.animate.set_stroke(LIGHT, width=1.5), run_time=0.5)

        # ── Beat 3: cấu trúc này được gọi là TAG; cả mạng sáng lên ──
        with self.narrated_caption([
            "Cấu trúc kết hợp giữa văn bản và quan hệ này",
            "được gọi là đồ thị có thuộc tính văn bản, hay ti ây gi.",
        ]):
            self.play(
                graph.edges.animate.set_stroke(gs.C_GNN, width=1.9),   # cạnh = GNN/xanh dương
                Flash(node_A, color=gs.C_GNN, line_length=0.22, num_lines=14, flash_radius=0.55),
                run_time=0.8,
            )
            legend = VGroup(
                t("Node = Textual content", 22, gs.C_LLM),
                t("·", 22, MID),
                t("Edge = Relationship", 22, gs.C_GNN),
            ).arrange(RIGHT, buff=0.4).next_to(graph, DOWN, buff=0.3)
            self.play(FadeIn(legend, shift=UP * 0.15), run_time=0.6)

        self.tag_graph = graph

        # ── Beat 4: hai nguồn thông tin hội tụ vào nót trung tâm ──
        blackout = Rectangle(width=25, height=15, fill_color=BLACK, fill_opacity=0.9, stroke_width=0).set_z_index(90)

        with self.narrated_caption([
            "Ti ây gi cho phép mô hình suy luận từ hai nguồn cùng lúc:",
            "nót đang nói về điều gì,",
            "và nót đó kết nối với những ai.",
        ]):
            self.play(FadeOut(legend), FadeIn(blackout), run_time=0.5)
            hub = node("A", target=True, radius=0.34).move_to(DOWN * 0.15).set_z_index(96)
            hub[1].set_stroke(gs.C_ROUTER).set_fill(gs.C_ROUTER, 0.22)  # hub = điểm fusion/tím
            content = doc_icon("CONTENT", ["Title", "Abstract"], width=2.9, height=1.5,
                               emphasized=True).move_to(LEFT * 4.2 + DOWN * 0.15).set_z_index(96)
            content.heading.set_color(gs.C_LLM)     # content = LLM/amber
            content[0].set_stroke(gs.C_LLM)
            structure = create_target_neighborhood("clean", "A", scale=0.5).move_to(RIGHT * 4.2 + DOWN * 0.15).set_z_index(96)
            struct_label = t("STRUCTURE", 20, gs.C_GNN, BOLD).next_to(structure, UP, buff=0.28).set_z_index(96)
            arr_c = small_arrow(content.get_right(), hub.get_left(), color=gs.C_LLM, buff=0.2)
            arr_s = small_arrow(structure.get_left(), hub.get_right(), color=gs.C_GNN, buff=0.2)
            self.play(FadeIn(content, shift=RIGHT * 0.2), FadeIn(structure, shift=LEFT * 0.2),
                      FadeIn(struct_label), FadeIn(hub), run_time=0.9)
            self.play(GrowArrow(arr_c), GrowArrow(arr_s), run_time=0.6)
            self.play(Flash(hub, color=gs.C_ROUTER, line_length=0.2, num_lines=12, flash_radius=0.5), run_time=0.6)

        # ── Câu chuyển sang node classification ──
        formula = t("TAG = Textual Content + Graph Structure", 30, BRIGHT, BOLD).to_edge(UP, buff=1.15).set_z_index(96)
        pred = probability_vector("Predicted label", [0.12, 0.71, 0.17], width=2.9,
                                  emphasized_index=1).next_to(hub, DOWN, buff=0.45).set_z_index(96)

        with self.narrated_caption([
            "Từ hai nguồn thông tin này,",
            "bài toán tiếp theo là dự đoán nhãn",
            "của những nót chưa biết lớp.",
        ]):
            self.play(FadeIn(formula, shift=DOWN * 0.15), run_time=0.7)
            self.play(FadeIn(pred, shift=UP * 0.15), run_time=0.7)
            self.wait(0.6)

        # Handoff cho section_3: graph nằm dưới lớp phủ; punch gom mọi thứ overlay.
        self.tag_blackout = blackout
        self.tag_punch = VGroup(content, structure, struct_label, arr_c, arr_s, hub, formula, pred)

    # ─────────────────────────────────────────────────────────
    # SECTION 3 — Hybrid Systems
    # ─────────────────────────────────────────────────────────
    def section_3_hybrid_systems(self):
        """Timeline trái→phải: shallow text features → GNN → hybrid GNN–LLM.

        Màu: đặc trưng nông = xám (MUTED); GNN / cấu trúc = xanh (C_GNN);
        LLM / ngữ nghĩa = cam (C_LLM); kiến trúc lai = tím (C_ROUTER).
        """
        graph = self.tag_graph

        # ── Beat 1 (0:00–0:08): shallow text features (xám) ──
        with self.narrated_caption([
            "Trước đây, nội dung văn bản của mỗi nót",
            "thường được biểu diễn bằng các đặc trưng tương đối nông,",
            "như tê ép y đê ép hoặc véc-tơ biểu diễn tĩnh.",
        ]):
            self.play(FadeOut(self.tag_punch), FadeOut(self.tag_blackout), run_time=0.4)
            self.play(graph.animate.scale(0.62).to_edge(LEFT, buff=0.6).shift(DOWN * 0.2),
                      run_time=0.8)
            tfidf = custom_feature_vector("TF-IDF", [0.2, 0.8, 0.3, 0.6, 0.15],
                                          color=MID, width=2.5).scale(0.82)
            static = custom_feature_vector("Static embeddings", [0.5, 0.35, 0.7, 0.3, 0.6],
                                           color=MID, width=2.5).scale(0.82)
            VGroup(tfidf, static).arrange(DOWN, buff=0.55).move_to(RIGHT * 1.0 + UP * 0.35)
            shallow_label = t("Shallow Text Features", size=23, color=MID, weight=BOLD)\
                .next_to(VGroup(tfidf, static), UP, buff=0.35)
            self.play(FadeIn(shallow_label), run_time=0.4)
            self.play(FadeIn(tfidf, shift=LEFT * 0.2), FadeIn(static, shift=LEFT * 0.2),
                      lag_ratio=0.3, run_time=1.1)

        # ── Beat 2 (0:08–0:17): đưa vào GNN, message passing xanh ──
        gnn_mod = module("GNN", "structural learning", width=3.0, height=0.95,
                         emphasized=True).move_to(RIGHT * 4.6 + UP * 0.35)
        gnn_mod[0].set_stroke(gs.C_GNN)
        gnn_mod[1][0].set_color(gs.C_GNN)
        arr_in = small_arrow(VGroup(tfidf, static).get_right(), gnn_mod.get_left(), color=gs.C_GNN)
        with self.narrated_caption([
            "Các véc-tơ này sau đó được đưa vào gờ nờ nờ",
            "để tổng hợp thông tin từ những nót lân cận.",
        ]):
            self.play(GrowArrow(arr_in), FadeIn(gnn_mod), run_time=0.8)
            self.play(graph.edges.animate.set_stroke(gs.C_GNN, width=2.2), run_time=0.5)
            hub = graph.nodes["A"]
            flashes = [ShowPassingFlash(e.copy().set_stroke(gs.C_GNN, 4), time_width=0.5)
                       for e in graph.edges]
            self.play(LaggedStart(*flashes, lag_ratio=0.06), run_time=1.3)
            self.play(Indicate(hub, color=gs.C_GNN, scale_factor=1.4), run_time=0.7)

        # ── Beat 3 (0:17–0:24): cấu trúc tốt, ngữ nghĩa hạn chế ──
        with self.narrated_caption([
            "Cách này khai thác tốt cấu trúc đồ thị,",
            "nhưng khả năng nắm bắt ngữ cảnh và ý nghĩa sâu của văn bản còn hạn chế.",
        ]):
            struct_tag = VGroup(gs.check(), t("Structure", size=22, color=gs.C_GNN, weight=BOLD))\
                .arrange(RIGHT, buff=0.18).next_to(gnn_mod, DOWN, buff=0.55)
            # KHÔNG dùng ✗: TF-IDF / static embeddings vẫn có chút ngữ nghĩa. Dùng
            # thanh ngắn (một phần) + nhãn "Limited semantics" để không nói quá.
            sem_bar = VGroup(
                Line(ORIGIN, RIGHT * 0.95, color=DIM, stroke_width=6),
                Line(ORIGIN, RIGHT * 0.32, color=gs.C_BAD, stroke_width=6),
            )
            sem_tag = VGroup(sem_bar, t("Limited semantics", size=20, color=gs.C_BAD))\
                .arrange(RIGHT, buff=0.22).next_to(struct_tag, DOWN, buff=0.32)
            self.play(FadeIn(struct_tag, shift=UP * 0.1), run_time=0.6)
            self.play(FadeIn(sem_tag, shift=UP * 0.1),
                      VGroup(tfidf, static).animate.set_opacity(0.4), run_time=0.8)

        # ── Beat 4 (0:24–0:32): LLM (cam) đọc văn bản ──
        with self.narrated_caption([
            "Gần đây, sự phát triển của các mô hình ngôn ngữ lớn",
            "đã mở ra một hướng tiếp cận mới.",
        ]):
            self.play(
                FadeOut(VGroup(tfidf, static, shallow_label, arr_in, struct_tag, sem_tag)),
                gnn_mod.animate.move_to(LEFT * 3.6 + DOWN * 1.6),
                FadeOut(graph),
                run_time=0.8,
            )
            doc = doc_icon("Node text", ["Title", "Abstract"], width=2.6, height=1.5)\
                .move_to(LEFT * 3.3 + UP * 1.4)
            doc.heading.set_color(gs.C_LLM)
            doc[0].set_stroke(gs.C_LLM)
            llm_mod = module("LLM", "semantic reasoning", width=3.0, height=0.95,
                             emphasized=True).move_to(RIGHT * 0.2 + UP * 1.4)
            llm_mod[0].set_stroke(gs.C_LLM)
            llm_mod[1][0].set_color(gs.C_LLM)
            sem_rep = custom_feature_vector("Semantic representation", [0.7, 0.85, 0.6, 0.9, 0.75],
                                            color=gs.C_LLM, width=2.8).scale(0.82)\
                .move_to(RIGHT * 4.4 + UP * 1.4)
            arr_dl = small_arrow(doc.get_right(), llm_mod.get_left(), color=gs.C_LLM)
            arr_ls = small_arrow(llm_mod.get_right(), sem_rep[0].get_left(), color=gs.C_LLM)
            self.play(FadeIn(doc, shift=RIGHT * 0.15), run_time=0.6)
            self.play(GrowArrow(arr_dl), FadeIn(llm_mod), run_time=0.7)
            self.play(GrowArrow(arr_ls), FadeIn(sem_rep, shift=LEFT * 0.15), run_time=0.7)

        # ── Beat 5 (0:32–0:40): hai luồng hợp nhất → Hybrid (tím) ──
        with self.narrated_caption([
            "Các kiến trúc lai kết hợp khả năng suy luận ngữ nghĩa của lờ lờ mờ",
            "với khả năng học cấu trúc của gờ nờ nờ,",
            "nhằm khai thác đầy đủ cả nội dung và quan hệ trong ti ây gi.",
        ]):
            self.play(
                FadeOut(VGroup(doc, arr_dl, arr_ls, sem_rep)),
                llm_mod.animate.move_to(LEFT * 3.6 + UP * 0.9),
                run_time=0.7,
            )
            hybrid = module("Hybrid GNN–LLM", "graph learning", width=3.6, height=1.05,
                            emphasized=True).move_to(RIGHT * 2.6)
            hybrid[0].set_stroke(gs.C_ROUTER)
            hybrid[1][0].set_color(gs.C_ROUTER)
            arr_g = small_arrow(gnn_mod.get_right(), hybrid.get_left() + DOWN * 0.22, color=gs.C_GNN)
            arr_l = small_arrow(llm_mod.get_right(), hybrid.get_left() + UP * 0.22, color=gs.C_LLM)
            self.play(GrowArrow(arr_g), GrowArrow(arr_l), FadeIn(hybrid), run_time=0.9)

            eq = VGroup(
                t("LLM", size=30, color=gs.C_LLM, weight=BOLD),
                t("+", size=30, color=INK),
                t("GNN", size=30, color=gs.C_GNN, weight=BOLD),
                t("=", size=30, color=INK),
                t("Hybrid graph learning", size=30, color=gs.C_ROUTER, weight=BOLD),
            ).arrange(RIGHT, buff=0.28).to_edge(DOWN, buff=1.15)
            subs = VGroup(
                t("Semantic reasoning", size=15, color=MID).next_to(eq[0], DOWN, buff=0.14),
                t("Structural learning", size=15, color=MID).next_to(eq[2], DOWN, buff=0.14),
            )
            self.play(FadeIn(eq, shift=UP * 0.15), run_time=0.8)
            self.play(FadeIn(subs), run_time=0.5)
            self.wait(0.5)
            self.play(FadeOut(VGroup(gnn_mod, llm_mod, hybrid, arr_g, arr_l, eq, subs)),
                      run_time=0.5)

    # ─────────────────────────────────────────────────────────
    # SECTION 5 — Two Existing GNN–LLM Paradigms
    # ─────────────────────────────────────────────────────────
    def section_5_two_paradigms(self):
        if getattr(self, "glance_title", None) is not None and self.glance_title in self.mobjects:
            self.remove(self.glance_title)

        title = t("TWO GNN–LLM FUSION PARADIGMS", size=34, color=INK, weight=BOLD).to_edge(UP, buff=0.38)

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
            vec_rich = custom_feature_vector("Enhanced", [0.9, 0.8, 0.9, 0.7], color=gs.C_LLM, width=1.6).move_to(vec_raw)
            
            self.play(FadeIn(vec_raw, shift=DOWN*0.1), run_time=0.5)
            self.play(ReplacementTransform(vec_raw, vec_rich), run_time=0.8)
            self.wait(0.25)
            
            inject_arr = small_arrow(vec_rich.get_bottom(), noisy_nbhd.target.get_top())
            self.play(GrowArrow(inject_arr), run_time=0.8)
            self.play(noisy_nbhd.target[0].animate.set_stroke(gs.C_LLM), noisy_nbhd.target[1].animate.set_color(gs.C_LLM), run_time=0.8)
            self.wait(0.6)
            self.play(FadeOut(vec_rich), FadeOut(inject_arr), run_time=0.6)
            noisy_msgs = VGroup(*[create_message_vector(
                n.get_center(), noisy_nbhd.target.get_center(),
                color=DARK if i not in {1, 2, 5, 7} else gs.C_BAD
            ) for i, n in enumerate(noisy_nbhd.neighbors)])
            self.play(AnimationGroup(*[GrowArrow(m) for m in noisy_msgs], lag_ratio=0.08), run_time=1.0)

        with self.narrated_caption(["tuy nhiên, dù véc-tơ ngữ nghĩa tốt hơn,", "gờ nờ nờ vẫn có thể bị kéo lệch bởi các hàng xóm nhiễu."]):
            # Emphasize the noisy neighbors (indices 1, 2, 5, 7)
            noisy_nodes = VGroup(*[noisy_nbhd.neighbors[i] for i in {1, 2, 5, 7}])
            noisy_arrows = VGroup(*[noisy_msgs[i] for i in {1, 2, 5, 7}])
            
            self.wait(0.7)
            
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
            
            self.wait(0.7) # Wait to let the visual sink in
            
            # Punchline ON TOP of the diagram
            bias_text = t("BETTER TEXT ≠ NO STRUCTURAL BIAS", size=40, color=INK, weight=BOLD).set_z_index(100)
            blackout2 = Rectangle(width=20, height=15, fill_color=BLACK, fill_opacity=0.85).set_z_index(99)
            self.play(
                FadeIn(blackout2),
                FadeIn(bias_text, shift=UP * 0.1), 
                run_time=1.0
            )
            self.wait(0.7)
            
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
            blackout3 = Rectangle(width=25, height=15, fill_color=BLACK, fill_opacity=0.95).set_z_index(80)
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
            target_A[0].set_stroke(gs.C_GNN)
            target_A[1].set_color(gs.C_GNN)

            # Stage 1
            nodes_1, edges_1 = create_hop_nodes(["B", "C", "D", "E"], 0.8, MID, graph_center)
            lbl_1 = t("1-hop context", size=20, color=MID).move_to(graph_center + DOWN * 2.9).set_z_index(90)
            seq_1 = make_sequence(["A", "B", "C", "D", "E"], [gs.C_GNN] + [MID]*4).move_to(RIGHT * 3.0 + UP * 0.5)
            
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
            seq_2 = make_sequence(["A", "B", "C", "D", "E", "F", "G", "H", "I"], [gs.C_GNN] + [MID]*4 + [MID]*4, show_dots=True).move_to(RIGHT * 3.0 + UP * 0.5)
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
            seq_3 = make_sequence(["A", "B", "C", "D", "E", "F", "G", "H", "I"], [gs.C_GNN] + [MID]*4 + [MID]*4, show_dots=True, final_node="N", final_color=MID).move_to(RIGHT * 3.0 + UP * 0.5)
            c3_nodes = t("Graph nodes: 52", size=22, color=LIGHT)
            c3_toks = t("Text tokens: 1,300", size=22, color=gs.C_BAD)
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
            punchline2 = t("More tokens, higher LLM cost", size=26, color=gs.C_BAD)
            punch_group = VGroup(punchline1, punchline2).arrange(DOWN, buff=0.2).move_to(ORIGIN).set_z_index(100)
            
            blackout_punch = Rectangle(width=20, height=15, fill_color=BLACK, fill_opacity=0.85).set_z_index(95)
            
            self.play(FadeIn(blackout_punch), FadeIn(punch_group, shift=UP*0.2), run_time=1.0)
            self.wait(0.7)
            
            # Không liệt kê tay từng nhóm nữa: cách cũ bỏ sót enh_group,
            # noisy_nbhd, noisy_msgs, blackout2, bias_text và các seq/counter
            # trung gian, nên chúng còn sống dưới lớp blackout rồi lộ ra ở
            # cảnh sau. Gom mọi mobject đang có mặt để dọn dứt điểm.
            # Giữ nguyên nhịp: vẫn không fade out ở đây, để audio chạy hết.
            self.sec5_objects = Group(*self.mobjects)

    # ─────────────────────────────────────────────────────────
    # SECTION 6 — Uniform Static Fusion
    # ─────────────────────────────────────────────────────────
    def section_6_static_fusion(self):
        """Fixed Fusion: cùng một cơ chế hợp nhất cho MỌI nót → đặt câu hỏi nghiên cứu.

        Không ám chỉ hệ cũ luôn gọi LLM lãng phí — chỉ nhấn: cùng một chiến lược
        hợp nhất cho mọi nót, trong khi nhu cầu mỗi nót lại khác nhau.
        """
        self.play(FadeOut(self.sec5_objects), run_time=0.5)

        # ── Beat 1 (0:00–0:08): mọi nót đi qua cùng một khối Fixed Fusion ──
        node_a = node("A", radius=0.34).move_to(LEFT * 5.4 + UP * 2.0)
        node_b = node("B", radius=0.34).move_to(LEFT * 5.4 + ORIGIN)
        node_c = node("C", radius=0.34).move_to(LEFT * 5.4 + DOWN * 2.0)
        nodes = VGroup(node_a, node_b, node_c)

        fusion = module("Static Fusion", "one rule for every node", width=3.5, height=1.25,
                        emphasized=True).move_to(RIGHT * 2.3 + UP * 0.1)
        fusion[0].set_stroke(gs.C_ROUTER)
        fusion[1][0].set_color(gs.C_ROUTER)
        src = VGroup(
            t("GNN", size=18, color=gs.C_GNN, weight=BOLD),
            t("+", size=18, color=INK),
            t("LLM", size=18, color=gs.C_LLM, weight=BOLD),
        ).arrange(RIGHT, buff=0.22).next_to(fusion, UP, buff=0.22)
        arrows = VGroup(*[
            small_arrow(n.get_right(), fusion.get_left() + UP * (0.4 - 0.4 * i), color=MID)
            for i, n in enumerate(nodes)
        ])
        with self.narrated_caption([
            "Tuy nhiên, phần lớn các hệ thống lai hiện nay",
            "vẫn áp dụng một chiến lược hợp nhất duy nhất cho tất cả các nót trong đồ thị.",
        ]):
            self.play(LaggedStart(*[FadeIn(n) for n in nodes], lag_ratio=0.2), run_time=0.7)
            self.play(FadeIn(fusion), FadeIn(src), run_time=0.6)
            self.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.2), run_time=0.9)

        # ── Beat 2 (0:08–0:17): cùng một công thức Fuse, bất kể từng nót ──
        formula = mt(r"z_v = \mathrm{Fuse}(z_v^{G},\, z_v^{L})", size=30)\
            .next_to(fusion, DOWN, buff=0.55)
        with self.narrated_caption([
            "Đầu ra của gờ nờ nờ và lờ lờ mờ được kết hợp theo cùng một cơ chế,",
            "bất kể đặc điểm riêng của từng nót.",
        ]):
            self.play(FadeIn(formula, shift=UP * 0.15), run_time=0.7)
            self.play(Indicate(fusion, color=gs.C_ROUTER, scale_factor=1.06), run_time=0.8)

        # ── Beat 3 (0:17–0:27): nhu cầu mỗi nót khác nhau ──
        need_a = t("needs GNN", size=15, color=gs.C_GNN).next_to(node_a, UP, buff=0.16)
        need_c = t("needs LLM", size=15, color=gs.C_LLM).next_to(node_c, DOWN, buff=0.16)
        with self.narrated_caption([
            "Nhưng các nót không giống nhau: có nót được gờ nờ nờ xử lý tốt nhờ cấu trúc lân cận rõ ràng,",
            "trong khi nót khác hưởng lợi nhiều hơn từ khả năng suy luận ngữ nghĩa của lờ lờ mờ.",
        ]):
            self.play(FadeOut(formula), run_time=0.3)
            self.play(node_a.animate.set_stroke(gs.C_GNN, width=3.5),
                      FadeIn(need_a, shift=RIGHT * 0.1), run_time=0.6)
            self.play(node_c.animate.set_stroke(gs.C_LLM, width=3.5),
                      FadeIn(need_c, shift=RIGHT * 0.1), run_time=0.6)

        # ── Beat 4 (0:27–0:34): cùng một luật cho mọi nót, dù nhu cầu khác ──
        # Không vẽ thanh "fusion weight" (dễ hiểu nhầm mọi phương pháp cũ đều dùng
        # một trọng số tuyến tính cố định). Paper chỉ nói: CÙNG một luật cho mọi nót.
        same_rule = t("same rule applied to A, B and C", size=16, color=gs.C_ROUTER)\
            .next_to(fusion, DOWN, buff=0.45)
        warn = t("Same fusion, different needs", size=22, color=gs.C_BAD, weight=BOLD)\
            .to_edge(DOWN, buff=1.15)
        with self.narrated_caption([
            "Một cơ chế hợp nhất đồng nhất vì thế",
            "không phản ánh được mức độ hữu ích khác nhau của hai mô hình với từng nót.",
        ]):
            self.play(FadeIn(same_rule, shift=UP * 0.1), run_time=0.5)
            self.play(Indicate(fusion, color=gs.C_ROUTER, scale_factor=1.04), run_time=0.6)
            self.play(FadeIn(warn, shift=UP * 0.1), run_time=0.6)

        # ── Beat 5 (0:34–0:42): Fixed Fusion → Node-Aware Router + câu hỏi ──
        router = module("Node-Aware Router", "decide per node", width=3.6, height=1.25,
                        emphasized=True).move_to(fusion)
        router[0].set_stroke(gs.C_ROUTER)
        router[1][0].set_color(gs.C_ROUTER)
        r_arr_g = small_arrow(router.get_right(), router.get_right() + RIGHT * 0.8 + UP * 0.5, color=gs.C_GNN)
        r_arr_l = small_arrow(router.get_right(), router.get_right() + RIGHT * 0.8 + DOWN * 0.5, color=gs.C_LLM)
        r_g = t("Keep GNN", size=15, color=gs.C_GNN, weight=BOLD).next_to(r_arr_g.get_end(), RIGHT, buff=0.1)
        r_l = t("Query LLM", size=15, color=gs.C_LLM, weight=BOLD).next_to(r_arr_l.get_end(), RIGHT, buff=0.1)
        # GLANCE dùng LLM để TINH CHỈNH dự đoán GNN, không thay bằng LLM thuần.
        r_refine = t("refine GNN", size=12, color=gs.C_ROUTER).next_to(r_l, DOWN, buff=0.12, aligned_edge=LEFT)
        center = VGroup(
            t("Different nodes", size=26, color=INK, weight=BOLD),
            mt(r"\Rightarrow", size=32, color=gs.C_ROUTER),
            t("Different model utility", size=26, color=gs.C_ROUTER, weight=BOLD),
        ).arrange(RIGHT, buff=0.28).to_edge(DOWN, buff=1.1)
        with self.narrated_caption([
            "Vậy làm thế nào để quyết định, ở cấp độ từng nót,",
            "khi nào nên tận dụng lờ lờ mờ?",
        ]):
            self.play(FadeOut(src), FadeOut(same_rule),
                      ReplacementTransform(fusion, router), run_time=0.8)
            self.play(GrowArrow(r_arr_g), GrowArrow(r_arr_l),
                      FadeIn(r_g), FadeIn(r_l), FadeIn(r_refine), run_time=0.7)
            self.play(ReplacementTransform(warn, center), run_time=0.7)
            self.wait(0.4)

        # Handoff cho section_7: giữ 3 nót, gom phần còn lại để fade.
        self.static_nodes = nodes
        self.static_objects = VGroup(router, arrows, r_arr_g, r_arr_l, r_g, r_l, r_refine,
                                     need_a, need_c, center)

    # ─────────────────────────────────────────────────────────
    # SECTION 7 — Node A, B, C Comparison
    # ─────────────────────────────────────────────────────────
    def section_7_node_comparison(self):
        # Fade out static fusion elements, keep nodes briefly
        self.play(FadeOut(self.static_objects), run_time=0.6)
        node_a, node_b, node_c = self.static_nodes[0], self.static_nodes[1], self.static_nodes[2]

        # ── NODE A ──────────────────────────────────────────
        group_A = create_target_neighborhood(kind="clean", label="A", scale=0.95).move_to(LEFT * 4 + UP * 0.4)
        title_A = t("Node A: Clear Structure", size=34, color=INK, weight=BOLD).to_edge(UP, buff=0.35)
        doc_A = create_text_document("Node A", ["Topic 1", "Topic 2", "Topic 3"], width=3.2, height=1.6).move_to(RIGHT * 3.5 + UP * 1.8)
        gnn_bar_A = probability_vector("GNN Prediction", [0.85, 0.10, 0.05], emphasized_index=0, color=gs.C_GNN, class_names=["C1", "C2", "C3"], true_index=0).move_to(RIGHT * 3.5 + DOWN * 0.2).scale(1.2)

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
        title_B = t("Node B: Noisy Structure, Clear Text", size=34, color=INK, weight=BOLD).to_edge(UP, buff=0.35)
        group_B = create_target_neighborhood(kind="noisy", label="B", scale=0.95).move_to(LEFT * 4 + UP * 0.4)
        doc_B = create_text_document("Node B", ["Graph Learning", "Heterophily", "Node Classification"], width=3.2, height=1.6).move_to(RIGHT * 3.5 + UP * 1.8)
        gnn_bar_B = probability_vector("GNN Prediction", [0.20, 0.65, 0.15], emphasized_index=1, color=gs.C_GNN, class_names=["C1", "C2", "C3"], true_index=0).move_to(RIGHT * 1.8 + DOWN * 0.8).scale(0.9)

        with self.narrated_caption(["nót bê có vùng lân cận chứa nhiều loại khác nhau."]):
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
                color=DARK if i not in {1, 2, 5, 7} else gs.C_BAD
            ) for i, n in enumerate(group_B.neighbors)])
            self.play(AnimationGroup(*[GrowArrow(m) for m in msgs_B], lag_ratio=0.1), run_time=1.0)
            self.play(ReplacementTransform(gnn_bar_A, gnn_bar_B), run_time=0.7)
            wrong_B = t("GNN: WRONG", color=gs.C_BAD, weight=BOLD, size=24).next_to(gnn_bar_B, DOWN, buff=0.25)
            self.play(FadeIn(wrong_B), run_time=0.4)

        with self.narrated_caption(["nhưng văn bản nót bê rất rõ ràng.", "lờ lờ mờ sửa lại dự đoán thành công."]):
            self.play(highlight_keywords(doc_B, [0, 1, 2]), run_time=0.8)
            llm_bar_B = probability_vector("LLM Corrected", [0.90, 0.05, 0.05], emphasized_index=0, color=gs.C_LLM, class_names=["C1", "C2", "C3"], true_index=0).move_to(RIGHT * 5.2 + DOWN * 0.8).scale(0.9)
            self.play(FadeIn(llm_bar_B), run_time=0.7)
            correct_B = t("LLM: CORRECT", color=gs.C_GOOD, weight=BOLD, size=24).next_to(llm_bar_B, DOWN, buff=0.25)
            self.play(FadeIn(correct_B), run_time=0.4)

        # Save Node B state for section 8
        self.node_B_state = {
            "title": title_B, "group": group_B, "doc": doc_B,
            "gnn_bar": gnn_bar_B, "llm_bar": llm_bar_B,
            "wrong": wrong_B, "correct": correct_B, "msgs": msgs_B
        }

        # ── NODE C ──────────────────────────────────────────
        title_C = t("Node C: Noisy Structure, Ambiguous Text", size=32, color=INK, weight=BOLD).to_edge(UP, buff=0.35)
        group_C = create_target_neighborhood(kind="noisy", label="C", scale=0.95).move_to(LEFT * 4 + UP * 0.4)
        doc_C = create_text_document("Node C", ["Some words...", "General text...", "Vague description"], width=3.2, height=1.6).move_to(RIGHT * 3.5 + UP * 1.8)

        with self.narrated_caption(["nót xê cũng khó với gờ nờ nờ.", "nhưng văn bản lại rất mơ hồ."]):
            llm_bar_C = probability_vector("LLM Output", [0.33, 0.34, 0.33], emphasized_index=None, color=gs.C_LLM, class_names=["C1", "C2", "C3"], true_index=0).move_to(RIGHT * 5.2 + DOWN * 0.8).scale(0.9)
            wrong_C = t("LLM: UNCERTAIN", color=YELLOW, weight=BOLD, size=24).next_to(llm_bar_C, DOWN, buff=0.25)
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
            gnn_bar_C = probability_vector("GNN Prediction", [0.10, 0.20, 0.70], emphasized_index=2, color=gs.C_GNN, class_names=["C1", "C2", "C3"], true_index=0).move_to(RIGHT * 1.8 + DOWN * 0.8).scale(0.9)
            wrong_gnn_C = t("GNN: WRONG", color=gs.C_BAD, weight=BOLD, size=24).next_to(gnn_bar_C, DOWN, buff=0.25)
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
        c = self.node_C_state

        with self.narrated_caption(["nót bê và nót xê đều khó với gờ nờ nờ.", "nhưng chỉ nót bê nhận được lợi ích từ lờ lờ mờ."]):
            # Fade out ONLY the elements from Node C (Node B was already removed in section 7)
            self.play(
                FadeOut(c["title"]), FadeOut(c["group"]), FadeOut(c["doc"]),
                FadeOut(c["gnn_bar"]), FadeOut(c["llm_bar"]),
                FadeOut(c["wrong_gnn"]), FadeOut(c["wrong_llm"]),
                run_time=0.5
            )

            # TOP ROW: Node B
            node_b_label = t("Node B", size=32, color=INK, weight=BOLD).move_to(LEFT * 5.0 + UP * 1.5)
            
            text_b = t("Clear Text:\n'Graph Learning...'", size=28, color=INK).next_to(node_b_label, RIGHT, buff=1.0)
            
            arrow_b = Arrow(text_b.get_right(), text_b.get_right() + RIGHT * 1.2, buff=0.15, color=gs.C_EDGE, stroke_width=4, tip_length=0.2)
            
            result_b = VGroup(
                t("GNN: WRONG", size=28, color=gs.C_BAD),
                VGroup(
                    t("LLM: CORRECT", size=28, color=gs.C_GOOD, weight=BOLD),
                    gs.check(color=gs.C_GOOD, size=0.35)
                ).arrange(RIGHT, buff=0.15)
            ).arrange(DOWN, aligned_edge=LEFT).next_to(arrow_b, RIGHT, buff=0.15)
            
            row_b = VGroup(node_b_label, text_b, arrow_b, result_b)

            # BOTTOM ROW: Node C
            node_c_label = t("Node C", size=32, color=INK, weight=BOLD).move_to(LEFT * 5.0 + DOWN * 1.5)
            
            text_c = t("Vague Text:\n'Some words...'", size=28, color=INK).next_to(node_c_label, RIGHT, buff=1.0)
            text_c.align_to(text_b, LEFT)
            
            arrow_c = Arrow(text_c.get_right(), text_c.get_right() + RIGHT * 1.2, buff=0.15, color=gs.C_EDGE, stroke_width=4, tip_length=0.2)
            arrow_c.align_to(arrow_b, LEFT)

            result_c = VGroup(
                t("GNN: WRONG", size=28, color=gs.C_BAD),
                t("LLM: UNCERTAIN", size=28, color=YELLOW, weight=BOLD)
            ).arrange(DOWN, aligned_edge=LEFT).next_to(arrow_c, RIGHT, buff=0.15)
            
            row_c = VGroup(node_c_label, text_c, arrow_c, result_c)

            # Align horizontally
            VGroup(row_b, row_c).set_x(0)

            # Animations
            self.play(FadeIn(row_b, shift=RIGHT * 0.3), run_time=0.8)
            self.play(FadeIn(row_c, shift=RIGHT * 0.3), run_time=0.8)
            self.wait(0.5)

        conclusion = VGroup(
            t("GNN DIFFICULTY", size=42, color=gs.C_GNN, weight=BOLD),
            t("≠", size=56, color=gs.C_BAD, weight=BOLD),
            t("GUARANTEED LLM BENEFIT", size=42, color=gs.C_LLM, weight=BOLD),
        ).arrange(DOWN, buff=0.28).set_z_index(100)
        blackout5 = Rectangle(width=20, height=15, fill_color=BLACK, fill_opacity=0.85).set_z_index(99)
        with self.narrated_caption(["Nói cách khác, khó với gờ nờ nờ", "chưa chắc hưởng lợi từ lờ lờ mờ."]):
            self.play(FadeIn(blackout5), FadeIn(conclusion, shift=UP * 0.2), run_time=0.8)
            self.wait(0.6)

        # Store for morph into section 9
        self.comparison_objects = VGroup(conclusion, blackout5, row_b, row_c)

    # ─────────────────────────────────────────────────────────
    # SECTION 9 — Aggregate Accuracy
    # ─────────────────────────────────────────────────────────
    def section_9_aggregate_accuracy(self):
        with self.narrated_caption(["Xét một ví dụ minh họa.", "Nó cho thấy vì sao độ chính xác tổng thể có thể tăng rất ít."]):
            self.play(
                FadeOut(self.comparison_objects, shift=UP * 0.3),
                run_time=0.8
            )

        with self.narrated_caption(["giả sử chín mươi phần trăm là các nót dễ,", "còn mười phần trăm là các nót khó."]):
            easy_group = VGroup(
                t("90% Easy Nodes", size=38, color=gs.C_GNN, weight=BOLD),
                t("GNN: 95%  ->  Fusion: 94%", size=26, color=LIGHT)
            ).arrange(DOWN, buff=0.2).move_to(LEFT * 3.2 + UP * 1.4)
            hard_group = VGroup(
                t("10% Hard Nodes", size=38, color=gs.C_BAD, weight=BOLD),
                t("GNN: 40%  ->  Fusion: 53%", size=26, color=LIGHT)
            ).arrange(DOWN, buff=0.2).move_to(RIGHT * 3.2 + UP * 1.4)
            self.play(FadeIn(easy_group, shift=UP * 0.2), FadeIn(hard_group, shift=UP * 0.2), run_time=1.0)

        with self.narrated_caption(["trên nhóm khó, lờ lờ mờ giúp tăng mười ba điểm phần trăm."]):
            gnn_eq = mt(r"\text{GNN: } 0.9{\times}95\% + 0.1{\times}40\% = 89.5\%", size=38).move_to(DOWN * 0.5)
            self.play(Write(gnn_eq), run_time=0.9)
            gain_hard = t("Hard-node gain: +13 pts", size=26, color=gs.C_GOOD, weight=BOLD).next_to(hard_group, DOWN, buff=0.4)
            self.play(FadeIn(gain_hard, shift=UP * 0.1), run_time=0.6)

        with self.narrated_caption(["nhưng trên toàn đồ thị, tổng thể chỉ tăng không chấm bốn điểm."]):
            fusion_eq = mt(r"\text{Fusion: } 0.9{\times}94\% + 0.1{\times}53\% = 89.9\%", size=38).next_to(gnn_eq, DOWN, buff=0.4)
            self.play(TransformFromCopy(gnn_eq, fusion_eq), run_time=0.9)
            self.play(gnn_eq.animate.set_opacity(0.3), run_time=0.4)
            gain_overall = t("Overall gain: +0.4 percentage points", size=28, color=MID).next_to(fusion_eq, DOWN, buff=0.3)
            self.play(FadeIn(gain_overall), run_time=0.5)

        with self.narrated_caption(["lợi ích lớn ở một nhóm nhỏ trông rất nhỏ khi tính tổng."]):
            takeaway = t("LARGE SUBGROUP GAINS CAN LOOK SMALL IN AGGREGATE", size=28, color=gs.C_ROUTER, weight=BOLD).move_to(DOWN * 2.45)
            self.play(FadeIn(takeaway, shift=UP * 0.1), run_time=0.7)
            self.wait(0.8)

        self.sec9_objects = VGroup(easy_group, hard_group, gnn_eq, fusion_eq, gain_hard, gain_overall, takeaway)

    # ─────────────────────────────────────────────────────────
    # SECTION 10 — GLANCE Research Question & Task 2
    # ─────────────────────────────────────────────────────────
    def section_10_glance_question(self):
        with self.narrated_caption([
            "Như vậy, độ khó với gờ nờ nờ",
            "chưa đủ để quyết định.",
        ]):
            self.play(FadeOut(self.sec9_objects, shift=UP * 0.3), run_time=0.7)
            self.wait(0.3)

        # GLANCE = quyết định định tuyến từng nót: giữ GNN, hoặc gọi LLM để tinh chỉnh.
        node = module("Node", width=1.9).move_to(LEFT * 4.6 + DOWN * 0.1)
        gnn = module("GNN", width=1.9).move_to(LEFT * 2.0 + DOWN * 0.1)
        gnn[0].set_stroke(gs.C_GNN); gnn[1][0].set_color(gs.C_GNN)
        router = module("Router", "per node", width=2.3, height=1.0, emphasized=True)\
            .move_to(RIGHT * 0.7 + DOWN * 0.1)
        router[0].set_stroke(gs.C_ROUTER); router[1][0].set_color(gs.C_ROUTER)
        keep = module("Keep GNN", width=2.4).move_to(RIGHT * 4.4 + UP * 1.05)
        keep[0].set_stroke(gs.C_GNN); keep[1][0].set_color(gs.C_GNN)
        query = module("Query LLM", "refine GNN", width=2.4, emphasized=True)\
            .move_to(RIGHT * 4.4 + DOWN * 1.25)
        query[0].set_stroke(gs.C_LLM); query[1][0].set_color(gs.C_LLM)
        arr1 = small_arrow(node.get_right(), gnn.get_left())
        arr2 = small_arrow(gnn.get_right(), router.get_left(), color=gs.C_GNN)
        a_up = small_arrow(router.get_right(), keep.get_left(), color=gs.C_GNN)
        a_dn = small_arrow(router.get_right(), query.get_left(), color=gs.C_LLM)

        with self.narrated_caption([
            "gờ lans biến việc này thành một quyết định định tuyến cho từng nót:",
            "giữ dự đoán của gờ nờ nờ, hoặc gọi lờ lờ mờ để tinh chỉnh nó.",
        ]):
            self.play(FadeIn(VGroup(node, gnn, router)), GrowArrow(arr1), GrowArrow(arr2),
                      run_time=1.0)
            self.play(FadeIn(keep), FadeIn(query), GrowArrow(a_up), GrowArrow(a_dn),
                      run_time=1.0)

        # Bridge sang section 2 — câu chốt trong plan.md, đọc y nguyên.
        with self.narrated_caption([
            "Nếu phải chọn nót để gọi lờ lờ mờ,",
            "người ta đã chọn bằng cách nào?",
        ]):
            self.play(Indicate(router, color=gs.C_ROUTER, scale_factor=1.06), run_time=0.8)
            self.wait(0.3)
            self.play(
                FadeOut(VGroup(node, gnn, router, keep, query, arr1, arr2, a_up, a_dn)),
                run_time=0.6,
            )
