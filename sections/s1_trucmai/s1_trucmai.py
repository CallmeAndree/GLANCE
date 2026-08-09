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
        ).set_z_index(-1)
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
    arrow.set_z_index(2)
    if dashed:
        arrow = DashedVMobject(arrow, num_dashes=15)
        arrow.set_z_index(2)
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

    def tear_down(self):
        # Xem chú thích ở GlanceScene.tear_down: video phải dài hơn audio, nếu
        # không `build.sh` (-shortest) sẽ cắt mất đuôi câu cuối scene.
        self.wait(0.5)
        super().tear_down()
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
    def narrated_caption(self, text_segments, speed=None):
        """
        text_segments: single string or list of strings.
        If list, they are treated as sequential cues for a single voiceover generation.
        We now use manim-voiceover's native subcaption generation to ensure exact
        word-level synchronization and prevent subtitles from disappearing prematurely.

        speed: tốc độ đọc riêng cho đúng câu này, ví dụ 1.15 cho các chuỗi chữ
        cái đọc rời rạc. Audio được SINH ở tốc độ đó (không kéo giãn bản cũ) và
        tốc độ nằm trong cache key nên TTS thật sự được gọi lại.
        """
        if isinstance(text_segments, str):
            text_segments = [text_segments]

        full_text = " ".join(text_segments)

        if USE_VOICEOVER:
            override = getattr(self.speech_service, "speed_override", None)
            if speed is not None and override is not None:
                with override(speed):
                    with self.voiceover(text=full_text) as tracker:
                        yield tracker
            else:
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
        # Nhãn nằm ngay dưới nót mục tiêu, tức đúng chỗ hai cạnh chéo dưới chụm
        # lại — để chữ trần thì bị cạnh gạch ngang qua và không đọc được. Đặt
        # chữ trên một chip nền mờ và cho z-index cao hơn lớp cạnh; căn theo
        # target_ring (vòng ngoài) chứ không theo avatar, vì vòng rộng hơn.
        target_caption = t("TARGET USER", size=14, color=gs.C_ROUTER, weight=BOLD)
        target_chip = panel(
            target_caption.width + 0.26, target_caption.height + 0.18,
            stroke=gs.C_ROUTER, fill=BG, opacity=0.95,
        )
        target_caption.move_to(target_chip)
        target_label = VGroup(target_chip, target_caption)
        target_label.next_to(target_ring, DOWN, buff=0.12).set_z_index(8)

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
            # Callout "Paper B" là chỗ khán giả phải đọc chữ trong khung; giữ nó
            # đứng yên một nhịp trước khi fade, không đổi run_time của animation nào.
            self.wait(1.0)
            self.play(FadeOut(callout), FadeOut(link), node_B.animate.set_stroke(LIGHT, width=1.5), run_time=0.5)

        # ── Beat 3: cấu trúc này được gọi là TAG; cả mạng sáng lên ──
        # Câu này kết bằng chuỗi chữ cái rời "ti ây gi" nên giọng đọc bị khựng.
        # Thêm "viết tắt là" để có đà trước khi đánh vần, và sinh lại ở 1.15x
        # như các chỗ đọc acronym khác.
        with self.narrated_caption([
            "Cấu trúc kết hợp giữa văn bản và quan hệ này",
            "được gọi là đồ thị có thuộc tính văn bản, viết tắt là ti ây gi.",
        ], speed=1.15):
            # Thứ tự kể: NỘI DUNG (nót, màu LLM) trước, QUAN HỆ (cạnh, màu GNN)
            # sau — khớp thứ tự đọc của chú thích bên dưới. Chú thích cũng hiện
            # theo hai nhịp đó thay vì bật cả cụm một lúc.
            legend_nodes = t("Node = Textual content", 22, gs.C_LLM)
            legend_sep = t("·", 22, MID)
            legend_edges = t("Edge = Relationship", 22, gs.C_GNN)
            legend = VGroup(legend_nodes, legend_sep, legend_edges)\
                .arrange(RIGHT, buff=0.4)
            fit(legend, 11.5)
            legend.next_to(graph, DOWN, buff=0.3)

            self.play(
                LaggedStart(
                    *[Indicate(n, color=gs.C_LLM, scale_factor=1.18)
                      for n in graph.nodes.values()],
                    lag_ratio=0.06,
                ),
                FadeIn(legend_nodes, shift=UP * 0.15),
                run_time=0.8,
            )
            self.play(
                graph.edges.animate.set_stroke(gs.C_GNN, width=1.9),   # cạnh = GNN/xanh dương
                Flash(node_A, color=gs.C_GNN, line_length=0.22, num_lines=14, flash_radius=0.55),
                FadeIn(VGroup(legend_sep, legend_edges), shift=UP * 0.15),
                run_time=0.7,
            )

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
            "Bài toán đặt ra là làm thế nào để dự đoán nhãn",
            "của những nót chưa biết lớp?",
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
            # Dọn dứt điểm phần còn lại của section 2: legend, callout và các
            # object trung gian không nằm trong tag_punch/tag_blackout vẫn còn
            # sống dưới lớp phủ và lộ mờ ra ở cảnh sau. Giữ đúng `graph` vì
            # section 3 dùng tiếp nó.
            leftovers = [m for m in self.mobjects if m is not graph and graph not in m.get_family()]
            if leftovers:
                self.remove(*leftovers)
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

        # ── Beat 4: hai expert song song — cấu trúc (xanh) và ngữ nghĩa (cam) ──
        #
        # Bố cục hai hàng, mỗi hàng một nhánh. Các mobject trong cùng một hàng
        # được ép về CÙNG tung độ trước khi tạo mũi tên, nên mũi tên nằm ngang
        # tuyệt đối — bản cũ nối box lệch cao độ nên mũi tên bị xéo.
        ROW_SEM, ROW_STRUCT = 1.55, -1.45

        sem_rep = custom_feature_vector("Semantic representation", [0.7, 0.85, 0.6, 0.9, 0.75],
                                        color=gs.C_LLM, width=2.8).scale(0.78)
        struct_rep = custom_feature_vector("Structural representation", [0.75, 0.5, 0.85, 0.45, 0.7],
                                           color=gs.C_GNN, width=2.8).scale(0.78)
        sem_rep.move_to(RIGHT * 4.35 + UP * ROW_SEM)
        struct_rep.move_to(RIGHT * 4.35 + UP * ROW_STRUCT)
        # Mũi tên cắm vào KHUNG véc-tơ (phần [0]), không phải cả group kèm nhãn,
        # nên lấy đúng tung độ của khung làm trục của cả hàng.
        y_sem = sem_rep[0].get_center()[1]
        y_struct = struct_rep[0].get_center()[1]

        llm_mod = module("LLM", "reads node text", width=2.9, height=0.9,
                         emphasized=True).move_to(RIGHT * 0.55).set_y(y_sem)
        llm_mod[0].set_stroke(gs.C_LLM)
        llm_mod[1][0].set_color(gs.C_LLM)

        with self.narrated_caption([
            "Sự phát triển của các mô hình ngôn ngữ lớn",
            "mở ra một nguồn thông tin bổ sung cho việc học trên đồ thị.",
            "Nếu gờ nờ nờ học từ cấu trúc và các nót lân cận,",
            "thì lờ lờ mờ có thể khai thác trực tiếp nội dung văn bản",
            "để tạo ra những biểu diễn ngữ nghĩa giàu thông tin.",
        ]):
            # MỘT đồ thị duy nhất ở bên trái rẽ làm hai nhánh: lên lờ lờ mờ (đọc
            # văn bản của nót) và xuống gờ nờ nờ (tổng hợp hàng xóm). Đồ thị ở
            # lại trên màn hình suốt beat, để thấy hai năng lực cùng khai thác
            # một nguồn dữ liệu chứ không phải hai đầu vào rời nhau.
            self.play(
                FadeOut(VGroup(tfidf, static, shallow_label, arr_in, struct_tag, sem_tag)),
                graph.animate.scale(0.66).move_to(LEFT * 4.7),
                gnn_mod.animate.move_to(RIGHT * 0.55).set_y(y_struct),
                run_time=0.9,
            )
            # Hai nhánh xuất phát từ mép phải đồ thị, ở hai cao độ khác nhau.
            branch_up = small_arrow(graph.get_right() + UP * 0.35, llm_mod.get_left(),
                                    color=gs.C_LLM, buff=0.18)
            branch_dn = small_arrow(graph.get_right() + DOWN * 0.35, gnn_mod.get_left(),
                                    color=gs.C_GNN, buff=0.18)
            branch_up_lbl = t("node text", size=15, color=gs.C_LLM)
            branch_up_lbl.next_to(branch_up.get_center(), UL, buff=0.20)
            branch_dn_lbl = t("neighbors", size=15, color=gs.C_GNN)
            branch_dn_lbl.next_to(branch_dn.get_center(), DL, buff=0.20)

            arr_ls = small_arrow(llm_mod.get_right(), sem_rep[0].get_left(), color=gs.C_LLM)
            arr_gs = small_arrow(gnn_mod.get_right(), struct_rep[0].get_left(), color=gs.C_GNN)

            # Nhánh ngữ nghĩa: văn bản của nót đi lên lờ lờ mờ.
            self.play(GrowArrow(branch_up), FadeIn(branch_up_lbl), run_time=0.6)
            self.play(FadeIn(llm_mod), run_time=0.5)
            self.play(GrowArrow(arr_ls), FadeIn(sem_rep, shift=LEFT * 0.12), run_time=0.7)

            # Nhánh cấu trúc: message chạy dọc cạnh rồi mới xuống gờ nờ nờ.
            self.play(
                LaggedStart(*[ShowPassingFlash(e.copy().set_stroke(gs.C_GNN, 4), time_width=0.5)
                              for e in graph.edges], lag_ratio=0.05),
                run_time=0.9,
            )
            self.play(GrowArrow(branch_dn), FadeIn(branch_dn_lbl), run_time=0.6)
            self.play(GrowArrow(arr_gs), FadeIn(struct_rep, shift=LEFT * 0.12), run_time=0.7)
            branch_labels = VGroup(branch_up_lbl, branch_dn_lbl)

        # ── Beat 5: hợp nhất là hướng tự nhiên, nhưng áp đồng loạt thì sao? ──
        with self.narrated_caption([
            "Vì hai mô hình khai thác những nguồn thông tin khác nhau,",
            "một hướng tự nhiên là kết hợp chúng trong cùng một kiến trúc.",
            "Tuy nhiên, phần lớn các phương pháp hiện tại",
            "áp dụng cùng một chiến lược hợp nhất cho mọi nót,",
            "khiến lờ lờ mờ vẫn được gọi ngay cả khi gờ nờ nờ đã xử lý tốt nót đó.",
            "Vậy, có thực sự cần gọi lờ lờ mờ cho tất cả các nót?",
        ]):
            fusion = module("GNN–LLM Fusion", "one strategy for every node",
                            width=3.7, height=1.05, emphasized=True).move_to(RIGHT * 4.35)
            fusion[0].set_stroke(gs.C_ROUTER)
            fusion[1][0].set_color(gs.C_ROUTER)
            to_fusion_sem = small_arrow(sem_rep.get_bottom(), fusion.get_top() + LEFT * 0.5,
                                        color=gs.C_LLM, buff=0.14)
            to_fusion_struct = small_arrow(struct_rep.get_top(), fusion.get_bottom() + LEFT * 0.5,
                                           color=gs.C_GNN, buff=0.14)
            self.play(
                FadeOut(VGroup(branch_up, branch_dn, branch_labels, arr_ls, arr_gs,
                               llm_mod, gnn_mod)),
                run_time=0.6,
            )
            self.play(FadeIn(fusion), GrowArrow(to_fusion_sem), GrowArrow(to_fusion_struct),
                      run_time=0.9)
            self.play(Flash(fusion, color=gs.C_ROUTER, line_length=0.18, num_lines=12,
                            flash_radius=0.9), run_time=0.6)

            # Cùng chiến lược đó áp cho MỌI nót: đưa đồ thị ra giữa và phóng to,
            # rồi cho từng nót sáng lên lần lượt. Không dùng mũi tên — chín mũi
            # tên chụm về một khối chỉ tạo ra một bó nét, còn việc "nót nào cũng
            # bị gọi" thì chính các nót lần lượt đổi màu đã nói đủ.
            node_list = list(graph.nodes.values())
            # Đồ thị lệch sang phải, khối hợp nhất lùi hẳn về góc trên trái, số
            # đếm xuống góc dưới phải: ba thứ chiếm ba vùng riêng nên không đè
            # nhau như bản đặt tất cả vào giữa.
            self.play(
                FadeOut(VGroup(sem_rep, struct_rep, to_fusion_sem, to_fusion_struct)),
                graph.animate.scale(1.5).move_to(RIGHT * 1.5 + DOWN * 0.15),
                fusion.animate.scale(0.8).to_corner(UL, buff=0.6),
                run_time=0.9,
            )
            queries = ValueTracker(0)
            counter = always_redraw(
                lambda: t(f"LLM queries: {int(queries.get_value())} / {len(node_list)}",
                          size=22,
                          color=gs.C_LLM if queries.get_value() > 0 else MID,
                          weight=BOLD).to_corner(DR, buff=0.7)
            )
            self.add(counter)
            self.play(
                LaggedStart(*[
                    AnimationGroup(
                        Flash(n, color=gs.C_LLM, line_length=0.14, num_lines=10,
                              flash_radius=0.34),
                        n.animate.set_color(gs.C_LLM),
                    )
                    for n in node_list
                ], lag_ratio=0.16),
                queries.animate.set_value(len(node_list)),
                run_time=2.0,
            )

            # Một nót dễ mà GNN đã đúng vẫn bị gọi — đó là chỗ tốn kém.
            easy_node = graph.nodes["G"]
            # Nhãn có nền riêng và lùi hẳn lên trên nót: bản cũ đặt sát nót nên
            # chữ chạy đè lên chính nót đó và lên các cạnh quanh nó.
            easy_inner = VGroup(
                gs.check(color=gs.C_GOOD, size=0.18),
                t("GNN correct · 96% confidence", size=16, color=gs.C_GOOD, weight=BOLD),
            ).arrange(RIGHT, buff=0.25)
            easy_bg = RoundedRectangle(
                width=easy_inner.width + 0.32, height=easy_inner.height + 0.24,
                corner_radius=0.12, fill_color=gs.BG, fill_opacity=0.95,
                stroke_color=gs.C_GOOD, stroke_width=1.6,
            )
            easy_inner.move_to(easy_bg)
            easy_tag = VGroup(easy_bg, easy_inner).set_z_index(30)
            easy_tag.next_to(easy_node, UP, buff=0.85)
            # Nót G nằm gần mép phải nên nhãn dễ tràn ra ngoài khung: kéo lại cho
            # nằm trọn trong khung hình.
            limit_x = 6.45 - easy_tag.width / 2
            easy_tag.set_x(min(max(easy_tag.get_x(), -limit_x), limit_x))
            self.play(
                easy_node.animate.set_color(gs.C_GOOD),
                FadeIn(easy_tag, shift=UP * 0.1),
                run_time=0.8,
            )
            self.wait(0.4)
            # Chốt số đếm lại: để nguyên updater thì mobject vẫn tự dựng lại mỗi
            # frame và không fade out cùng phần còn lại được.
            counter.clear_updaters()

            # Kết bằng câu hỏi routing, không kết bằng "hybrid là lời giải".
            # Câu hỏi gom về MỘT góc (dưới trái) thay vì nằm giữa đè lên đồ thị;
            # lớp phủ cũng nhẹ đi để vẫn thấy các nót vừa sáng phía sau.
            dim = Rectangle(width=25, height=15, fill_color=BLACK,
                            fill_opacity=0.35, stroke_width=0).set_z_index(60)
            question = t("Does every node really need the LLM?",
                         size=30, color=INK, weight=BOLD).set_z_index(70)
            cost_line = t("Accuracy <-> Computational cost",
                          size=24, color=gs.C_ROUTER).set_z_index(70)
            closing = VGroup(question, cost_line).arrange(DOWN, aligned_edge=LEFT, buff=0.26)
            fit(closing, 6.4)
            closing.to_corner(DL, buff=0.8)
            self.play(FadeIn(dim), FadeIn(question, shift=UP * 0.12), run_time=0.8)
            self.play(FadeIn(cost_line), run_time=0.5)

        # Dọn NGOÀI khối voiceover: nếu fade ngay trong khối thì khối còn phải
        # chờ nốt phần audio dư và khán giả nhìn màn hình trống mấy giây.
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)

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

        # Ba khối dưới đây đọc tên hai paradigm bằng phiên âm rời rạc; sinh ở
        # 1.15x cho liền mạch, chỉ ba khối này chứ không cả section.
        # Ở 1.15x câu này bị đọc thành ngữ điệu ngân nga; hạ về 1.05 để giọng ổn
        # định trở lại (API bỏ qua tham số temperature nên tốc độ là đòn bẩy duy
        # nhất phía dịch vụ).
        with self.narrated_caption(["các phương pháp hiện nay chia thành hai hướng:", "lờ lờ mờ ass èn han xờ và lờ lờ mờ ass prì đích tờ."], speed=1.05):
            self.play(Write(title), run_time=0.7)
            self.play(FadeIn(enh_group), FadeIn(pred_group), run_time=1.0)

        # Enhancer deep-dive
        hetero_nbhd = create_target_neighborhood(kind="noisy", scale=0.9).move_to(RIGHT * 2.8 + DOWN * 0.2)
        with self.narrated_caption(["lờ lờ mờ ass èn han xờ tạo véc-tơ ngữ nghĩa giàu hơn,", "rồi gờ nờ nờ tiếp tục truyền thông tin và dự đoán."], speed=1.25):
            self.play(
                FadeOut(pred_group),
                enh_group.animate.scale(1.08).shift(RIGHT * 1.2),
                # Tiêu đề rời hẳn màn hình thay vì thu nhỏ nằm lại ở góc: chữ nhỏ
                # đó không còn nhiệm vụ gì trong các nhịp sau, chỉ làm rối khung.
                FadeOut(title),
                FadeIn(hetero_nbhd.target), FadeIn(hetero_nbhd.neighbors), FadeIn(hetero_nbhd.edges),
                run_time=0.8
            )
            
            # Show vector enhancement for target node
            vec_raw = custom_feature_vector("Raw", [0.2, 0.3, 0.1, 0.2], color=DIM, width=1.5).move_to(RIGHT * 2.8 + UP * 2.6)
            vec_rich = custom_feature_vector("Enhanced", [0.9, 0.8, 0.9, 0.7], color=gs.C_LLM, width=1.6).move_to(vec_raw)
            
            self.play(FadeIn(vec_raw, shift=DOWN*0.1), run_time=0.5)
            self.play(ReplacementTransform(vec_raw, vec_rich), run_time=0.8)
            self.wait(0.25)
            
            inject_arr = small_arrow(vec_rich.get_bottom(), hetero_nbhd.target.get_top())
            self.play(GrowArrow(inject_arr), run_time=0.8)
            self.play(hetero_nbhd.target[0].animate.set_stroke(gs.C_LLM), hetero_nbhd.target[1].animate.set_color(gs.C_LLM), run_time=0.8)
            self.wait(0.6)
            self.play(FadeOut(vec_rich), FadeOut(inject_arr), run_time=0.6)
            conflicting_msgs = VGroup(*[create_message_vector(
                n.get_center(), hetero_nbhd.target.get_center(),
                color=DARK if i not in {1, 2, 5, 7} else gs.C_BAD
            ) for i, n in enumerate(hetero_nbhd.neighbors)])
            self.play(AnimationGroup(*[GrowArrow(m) for m in conflicting_msgs], lag_ratio=0.08), run_time=1.0)

        # ── Ngữ nghĩa tốt hơn KHÔNG chữa được thiên lệch cấu trúc ──
        #
        # Kể theo chuỗi nhân quả: đặc trưng ngữ nghĩa tốt → các tín hiệu xung đột
        # → AGGREGATE → biểu diễn dịch chuyển → dự đoán đổi. Không dùng "nhiễu"
        # cho hàng xóm dị phối, và không rung nót (rung không nói lên điều gì).
        with self.narrated_caption([
            "Tuy nhiên, biểu diễn ngữ nghĩa tốt hơn",
            "không giải quyết được vấn đề cấu trúc.",
            "Khi vùng lân cận chứa nhiều tín hiệu xung đột với nót trung tâm,",
            "gờ nờ nờ vẫn tổng hợp các tín hiệu này.",
            "Kết quả là biểu diễn của nót có thể bị kéo sang một vùng khác",
            "trong không gian đặc trưng, và dẫn đến dự đoán sai.",
        ]):
            conflicting_nodes = VGroup(*[hetero_nbhd.neighbors[i] for i in {1, 2, 5, 7}])
            aligned_msgs = VGroup(*[conflicting_msgs[i] for i in range(8) if i not in {1, 2, 5, 7}])
            conflicting_arrows = VGroup(*[conflicting_msgs[i] for i in {1, 2, 5, 7}])

            # Cột paradigm lùi hẳn về mép trái và nhỏ lại: nó vẫn neo bối cảnh
            # "đang nói về nhánh enhancer", nhưng nhường dải giữa cho khối
            # AGGREGATE và trục tiềm ẩn — bản đầu đặt chồng lên nhau.
            self.play(enh_group.animate.scale(0.78).to_edge(LEFT, buff=0.3), run_time=0.6)

            # Message cùng lớp xanh, message xung đột coral.
            self.play(
                aligned_msgs.animate.set_color(gs.C_GNN),
                conflicting_nodes.animate.set_color(gs.C_BAD),
                conflicting_arrows.animate.set_color(gs.C_BAD),
                run_time=0.8,
            )

            # Việc tổng hợp được KỂ bằng chuyển động: từng hàng xóm gửi một chấm
            # chạy dọc cạnh vào a, chấm xung đột màu coral, chấm cùng lớp màu
            # xanh. Sau khi chúng dồn vào nơi, a đỏ dần lên. Cách này thay cho
            # khối AGGREGATE tĩnh — khối hộp không cho thấy "bị kéo lệch".
            agg_dots = VGroup(*[
                Dot(radius=0.07,
                    color=gs.C_BAD if index in {1, 2, 5, 7} else gs.C_GNN).move_to(neighbor)
                for index, neighbor in enumerate(hetero_nbhd.neighbors)
            ]).set_z_index(8)
            self.add(agg_dots)
            self.play(
                LaggedStart(*[
                    MoveAlongPath(dot, Line(dot.get_center(), hetero_nbhd.target.get_center()))
                    for dot in agg_dots
                ], lag_ratio=0.11),
                run_time=1.0,
            )
            self.play(
                FadeOut(agg_dots, scale=0.3),
                hetero_nbhd.target[0].animate.set_stroke(gs.C_BAD),
                hetero_nbhd.target[1].animate.set_color(gs.C_BAD),
                run_time=0.8,
            )

            # Trục tiềm ẩn: h_v trước → sau, vượt qua ranh giới quyết định.
            axis = Line(LEFT * 2.2, RIGHT * 2.2, color=DIM, stroke_width=2)
            axis.move_to(LEFT * 2.5 + DOWN * 2.25)
            boundary = DashedLine(axis.get_center() + UP * 0.42, axis.get_center() + DOWN * 0.42,
                                  dash_length=0.08, color=MID, stroke_width=2)
            class_a = t("class A", size=15, color=gs.C_GOOD).next_to(axis.get_left(), DOWN, buff=0.22)
            class_b = t("class B", size=15, color=gs.C_BAD).next_to(axis.get_right(), DOWN, buff=0.22)
            h_before = Dot(axis.get_left() + RIGHT * 0.7, radius=0.09, color=gs.C_GNN)
            h_before_lbl = MathTex(r"h_v\ \text{before}", font_size=22, color=gs.C_GNN).next_to(h_before, UP, buff=0.16)
            self.play(Create(axis), Create(boundary), FadeIn(class_a), FadeIn(class_b),
                      FadeIn(h_before), FadeIn(h_before_lbl), run_time=0.8)

            h_after = h_before.copy().set_color(gs.C_BAD).move_to(axis.get_right() + LEFT * 0.7)
            h_after_lbl = MathTex(r"h_v\ \text{after}", font_size=22, color=gs.C_BAD).next_to(h_after, UP, buff=0.16)
            drift = small_arrow(h_before.get_center() + UP * 0.03, h_after.get_center() + UP * 0.03,
                                color=gs.C_BAD, buff=0.16)
            self.play(GrowArrow(drift), run_time=0.5)
            self.play(FadeIn(h_after), FadeIn(h_after_lbl), run_time=0.7)

            # Dự đoán đổi theo — ghi rõ là ví dụ minh hoạ, không phải số đo.
            shift_rows = VGroup(
                t("A:  0.78  ->  0.39", size=20, color=gs.C_BAD, weight=BOLD),
                t("B:  0.17  ->  0.55", size=20, color=gs.C_BAD, weight=BOLD),
                t("Schematic example", size=13, color=MID),
            ).arrange(DOWN, buff=0.14).move_to(RIGHT * 4.75 + DOWN * 2.35)
            self.play(FadeIn(shift_rows, shift=UP * 0.1), run_time=0.7)
            self.wait(0.4)

            # Punchline KHÔNG kèm lớp phủ: hình bên dưới giữ nguyên độ sáng, câu
            # chốt nằm ở dải trên cùng nên không cần làm mờ gì cả.
            bias_text = VGroup(
                t("BETTER SEMANTICS ≠ RELIABLE AGGREGATION", size=34, color=INK, weight=BOLD),
                t("Message passing still depends on neighbors", size=20, color=gs.C_BAD),
            ).arrange(DOWN, buff=0.22).move_to(UP * 2.55).set_z_index(100)
            self.play(FadeIn(bias_text, shift=UP * 0.1), run_time=1.0)
            self.wait(0.7)
            self.aggregation_debris = VGroup(
                axis, boundary, class_a, class_b,
                h_before, h_before_lbl, h_after, h_after_lbl, drift, shift_rows,
            )
            
        # ── Predictor deep-dive: mở rộng vùng lân cận → chuỗi dài → chi phí ──
        with self.narrated_caption([
            "Với lờ lờ mờ ass prì đích tờ, thông tin của nót và vùng lân cận",
            "phải được tuần tự hoá thành một chuỗi văn bản để mô hình xử lý.",
        ], speed=1.15):
            pred_group.move_to(RIGHT * 2.5 + DOWN * 0.1).scale(1.08)
            self.play(
                FadeOut(hetero_nbhd), FadeOut(conflicting_msgs), FadeOut(bias_text),
                FadeOut(self.aggregation_debris),
                FadeOut(enh_group),
                run_time=0.8
            )
            # Quy trình dựng dần: hộp → mũi tên → hộp kế tiếp, thay vì bật cả
            # sơ đồ một lúc. Khán giả thấy được thứ tự các bước.
            pred_title, pred_body = pred_group[0], pred_group[1]
            pred_boxes, pred_links = pred_body[0], pred_body[1]
            self.play(FadeIn(pred_title), run_time=0.4)
            chain_steps = []
            for index, box in enumerate(pred_boxes):
                chain_steps.append(FadeIn(box, shift=UP * 0.12))
                if index < len(pred_links):
                    chain_steps.append(GrowArrow(pred_links[index]))
            self.play(LaggedStart(*chain_steps, lag_ratio=0.6), run_time=2.2)
            self.wait(0.3)

        # Lớp phủ nhẹ hơn (0.72): vẫn thấy đồ thị, chuỗi và card phía sau punchline.
        blackout3 = Rectangle(width=25, height=15, fill_color=BLACK, fill_opacity=0.72).set_z_index(80)

        graph_center = LEFT * 3.75 + DOWN * 0.15
        # Ba bán kính vòng lân cận khai báo một chỗ, dùng chung cho cả nót lẫn
        # vòng pulse, để hai thứ luôn khớp nhau.
        RING_1, RING_2, RING_3 = 0.72, 1.38, 1.98
        # Dải chuỗi neo theo MÉP TRÁI cố định, không căn theo tâm: mỗi lần thêm
        # ô mà căn tâm thì dải nở về cả hai phía, mép trái trườn lên đầu mũi tên
        # và chữ 'Serialize'.
        SEQ_LEFT_X, SEQ_Y = -0.55, 0.35
        # Card nằm dưới hàng tiêu đề và trên chuỗi: cao hơn thì đè tiêu đề góc,
        # thấp hơn thì chạm ô đầu tiên của chuỗi.
        CARD_POS = RIGHT * 4.75 + UP * 1.75

        def ring_nodes(labels, radius, color, center, angle_offset=0.0):
            """Một vòng lân cận: nót xếp đều trên đường tròn bán kính `radius`.

            `angle_offset` xoay VỊ TRÍ các nót trên vòng. Trước đây đợt thứ hai
            được tạo rồi gọi .rotate() lên cả nhóm, khiến chữ trong nót bị quay
            ngược (chữ N thành И, K thành Ʞ).
            """
            nodes, edges = VGroup(), VGroup()
            angle_step = TAU / len(labels)
            for i, lbl in enumerate(labels):
                angle = i * angle_step + angle_offset
                pos = center + radius * np.array([np.cos(angle), np.sin(angle), 0])
                n = node(lbl, radius=0.17).move_to(pos)
                n[0].set_stroke(color)
                n[1].set_color(color)
                nodes.add(n)
                edges.add(Line(center, pos, color=DIM, stroke_width=1.4).set_z_index(85))
            nodes.set_z_index(90)
            return nodes, edges

        def seq_box(label, color):
            """Một ô của chuỗi: nhãn nót + hai vạch gợi ý Title/Abstract đi kèm,
            để chuỗi đọc ra là VĂN BẢN đã tuần tự hoá chứ không phải danh sách id."""
            box = panel(0.42, 0.54, fill=BG, stroke=color).set_opacity(0.85)
            head = t(label, size=13, color=color, weight=BOLD)
            stripes = VGroup(*[
                Line(ORIGIN, RIGHT * 0.26, color=color, stroke_width=1.6).set_opacity(0.55)
                for _ in range(2)
            ]).arrange(DOWN, buff=0.07)
            VGroup(head, stripes).arrange(DOWN, buff=0.07).move_to(box)
            return VGroup(box, head, stripes).set_z_index(90)

        seq_items = []

        def grow_sequence(new_items, run_time=0.9, from_nodes=None):
            """Kéo dài chuỗi theo chiều ngang: ô cũ dịch sang, ô mới bay từ nót."""
            seq_items.extend(new_items)
            ghost = VGroup(*[m.copy() for m in seq_items])
            ghost.arrange(RIGHT, buff=0.07)
            ghost.align_to(np.array([SEQ_LEFT_X, 0.0, 0.0]), LEFT).set_y(SEQ_Y)
            anims = []
            for item, target in zip(seq_items, ghost):
                if item in new_items:
                    item.move_to(target)
                else:
                    anims.append(item.animate.move_to(target))
            for index, item in enumerate(new_items):
                source = from_nodes[index] if from_nodes else None
                anims.append(TransformFromCopy(source, item) if source else FadeIn(item, scale=0.6))
            self.play(LaggedStart(*anims, lag_ratio=0.05), run_time=run_time)

        def context_card(nodes_value, prompt_value, prompt_color=LIGHT):
            col_left = VGroup(
                t("Nodes", size=18, color=MID),
                t("Prompt", size=18, color=MID)
            ).arrange(DOWN, buff=0.15, aligned_edge=LEFT)
            
            col_right = VGroup(
                t(nodes_value, size=18, color=LIGHT, weight=BOLD),
                t(prompt_value, size=18, color=prompt_color, weight=BOLD)
            ).arrange(DOWN, buff=0.15, aligned_edge=LEFT)
            
            grid = VGroup(col_left, col_right).arrange(RIGHT, buff=0.4)
            
            rows = VGroup(
                t("CONTEXT SIZE", size=16, color=MID, weight=BOLD),
                grid,
                t("Schematic example", size=12, color=MID),
            ).arrange(DOWN, buff=0.15)
            frame = panel(rows.width + 0.5, rows.height + 0.4, fill=BG, stroke=DIM)
            rows.move_to(frame)
            return VGroup(frame, rows).move_to(CARD_POS).set_z_index(92)

        target_A = node("A", radius=0.24).move_to(graph_center).set_z_index(90)
        target_A[0].set_stroke(gs.C_GNN)
        target_A[1].set_color(gs.C_GNN)
        serialize_arr = small_arrow(
            graph_center + RIGHT * 2.35,
            np.array([SEQ_LEFT_X - 0.28, SEQ_Y, 0.0]),
        ).set_z_index(90)
        serialize_txt = t("Serialize", size=19, color=LIGHT).next_to(serialize_arr, UP, buff=0.1).set_z_index(90)
        hop_label = t("1-hop context", size=19, color=MID).move_to(graph_center + DOWN * 3.0).set_z_index(90)
        card = context_card("5", "~80")

        # ── Stage 1: target trước, vòng lân cận thứ nhất bật lần lượt ──
        with self.narrated_caption([
            "Với vòng lân cận thứ nhất, câu lệnh chỉ cần chứa nót trung tâm",
            "và một nhóm nhỏ các hàng xóm.",
        ]):
            # Cột pipeline của paradigm rời sân khấu ở đây: nó nằm đúng chỗ chuỗi
            # tuần tự hoá chạy qua, để lại thì hai thứ chồng lên nhau.
            self.play(FadeIn(blackout3), FadeOut(pred_group), run_time=0.4)
            self.play(FadeIn(target_A, scale=0.7), run_time=0.5)
            pulse = Circle(radius=RING_1, color=gs.C_GNN, stroke_width=2.5).move_to(graph_center).set_z_index(86)
            self.play(GrowFromCenter(pulse), run_time=0.5)
            self.play(pulse.animate.set_stroke(opacity=0.25), FadeIn(hop_label), run_time=0.4)

            nodes_1, edges_1 = ring_nodes(["B", "C", "D", "E"], RING_1, MID, graph_center)
            self.play(
                LaggedStart(*[AnimationGroup(Create(e), GrowFromCenter(n))
                              for n, e in zip(nodes_1, edges_1)], lag_ratio=0.22),
                run_time=1.1,
            )
            self.play(GrowArrow(serialize_arr), FadeIn(serialize_txt), run_time=0.5)
            grow_sequence([seq_box("A", gs.C_GNN)], run_time=0.5, from_nodes=[target_A])
            grow_sequence([seq_box(l, MID) for l in ["B", "C", "D", "E"]],
                          run_time=1.0, from_nodes=list(nodes_1))
            self.play(FadeIn(card, shift=LEFT * 0.1), run_time=0.5)

        # ── Stage 2: vòng nở ra, nót vòng hai bật theo đợt ──
        with self.narrated_caption([
            "Nhưng khi mở rộng sang vòng lân cận thứ hai,",
            "số nót cần mô tả tăng nhanh,",
            "kéo theo lượng văn bản trong câu lệnh cũng phình ra.",
        ]):
            hop_label_2 = t("2-hop context", size=19, color=LIGHT).move_to(hop_label).set_z_index(90)
            nodes_2, edges_2 = ring_nodes(["F", "G", "H", "I", "J", "K", "L", "M"], RING_2, LIGHT, graph_center)
            self.play(
                pulse.animate.scale(RING_2 / RING_1).set_stroke(opacity=0.5),
                ReplacementTransform(hop_label, hop_label_2),
                run_time=0.7,
            )
            self.play(
                LaggedStart(*[AnimationGroup(Create(e), GrowFromCenter(n))
                              for n, e in zip(nodes_2, edges_2)], lag_ratio=0.10),
                run_time=1.3,
            )
            grow_sequence([seq_box(l, MID) for l in ["F", "G", "H", "I"]],
                          run_time=1.0, from_nodes=list(nodes_2[:4]))
            grow_sequence([t("...", size=22, color=LIGHT).set_z_index(90)], run_time=0.4)
            card_2 = context_card("18", "~420")
            self.play(ReplacementTransform(card, card_2), run_time=0.5)

        # ── Stage 3: hai đợt nữa; chi phí chuyển amber rồi mới sang đỏ ──
        with self.narrated_caption([
            "Nếu tiếp tục mở rộng vùng lân cận, số lượng nót có thể tăng rất nhanh.",
            "Mỗi nót lại mang theo văn bản riêng,",
            "khiến câu lệnh ngày càng dài và tốn kém để xử lý.",
        ]):
            hop_label_3 = t("3-hop context", size=19, color=gs.C_LLM).move_to(hop_label).set_z_index(90)
            wave_a, edges_a = ring_nodes(["N", "O", "P", "Q", "R", "S"], RING_3, MID, graph_center)
            wave_b, edges_b = ring_nodes(["T", "U", "V", "W", "X", "Y"], RING_3, MID,
                                         graph_center, angle_offset=TAU / 12)

            self.play(
                pulse.animate.scale(RING_3 / RING_2).set_stroke(opacity=0.35),
                ReplacementTransform(hop_label_2, hop_label_3),
                run_time=0.6,
            )
            self.play(
                LaggedStart(*[AnimationGroup(Create(e), GrowFromCenter(n))
                              for n, e in zip(wave_a, edges_a)], lag_ratio=0.08),
                run_time=1.0,
            )
            grow_sequence([seq_box("N", MID)], run_time=0.5, from_nodes=[wave_a[0]])
            card_3 = context_card("34", "~760", prompt_color=gs.C_LLM)
            self.play(ReplacementTransform(card_2, card_3), run_time=0.4)

            self.play(
                LaggedStart(*[AnimationGroup(Create(e), GrowFromCenter(n))
                              for n, e in zip(wave_b, edges_b)], lag_ratio=0.08),
                run_time=1.0,
            )
            grow_sequence([seq_box("Y", MID)], run_time=0.5, from_nodes=[wave_b[0]])
            card_4 = context_card("52", "~1.3k", prompt_color=gs.C_LLM)
            self.play(ReplacementTransform(card_3, card_4), run_time=0.4)
            # Đỏ đến SAU một nhịp, không đỏ ngay từ lúc số nhảy.
            self.wait(0.4)
            self.play(card_4[1][2][1].animate.set_color(gs.C_BAD), run_time=0.5)

        with self.narrated_caption([
            "Vì vậy, càng đưa nhiều ngữ cảnh đồ thị vào lờ lờ mờ,",
            "chi phí cho mỗi lần gọi càng lớn.",
            "Và nếu làm điều này cho mọi nót thì sao?",
        ]):
            punch_group = VGroup(
                t("MORE NEIGHBORS  ->  MORE TEXT  ->  MORE LLM COST",
                  size=30, color=BRIGHT, weight=BOLD),
                t("each query carries the whole neighborhood", size=20, color=gs.C_BAD),
            # Punchline nằm ở khoảng trống bên PHẢI, dưới dải chuỗi: đặt giữa
            # khung thì chữ cắt ngang đúng vòng nót bên trái.
            ).arrange(DOWN, buff=0.22).set_z_index(100)
            fit(punch_group, 6.7)
            punch_group.move_to(RIGHT * 3.0 + DOWN * 1.75)
            blackout_punch = Rectangle(width=20, height=15, fill_color=BLACK,
                                       fill_opacity=0.55).set_z_index(95)
            self.play(FadeIn(blackout_punch), FadeIn(punch_group, shift=UP * 0.2), run_time=1.0)
            self.wait(0.7)
            
            # Không liệt kê tay từng nhóm nữa: cách cũ bỏ sót enh_group,
            # hetero_nbhd, conflicting_msgs, bias_text và các seq/counter
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
        node_a = node("A", radius=0.28).move_to(LEFT * 4.6 + UP * 2.0)
        node_b = node("B", radius=0.28).move_to(LEFT * 4.6 + ORIGIN)
        node_c = node("C", radius=0.28).move_to(LEFT * 4.6 + DOWN * 2.0)
        nodes = VGroup(node_a, node_b, node_c)

        fusion = module("Static Fusion", "one rule for every node", width=3.5, height=1.25,
                        emphasized=True).move_to(RIGHT * 1.5 + UP * 0.1)
        fusion[0].set_stroke(gs.C_ROUTER)
        fusion[1][0].set_color(gs.C_ROUTER)
        src = VGroup(
            t("GNN", size=18, color=gs.C_GNN, weight=BOLD),
            t("+", size=18, color=INK),
            t("LLM", size=18, color=gs.C_LLM, weight=BOLD),
        ).arrange(RIGHT, buff=0.22).next_to(fusion, UP, buff=0.22)
        # Ba mũi tên cắm vào ba cao độ RỜI NHAU trên cạnh trái của khối, với buff
        # rõ ở cả hai đầu và đầu tên nhỏ lại — bản cũ để ba đầu tên tụ vào cùng
        # một vùng nên trông như một chùm đầu nhọn, không chỉ rõ nót nào đi đâu.
        # Không sửa small_arrow() vì các cảnh khác đang dùng đúng đầu tên đó.
        arrows = VGroup(*[
            Arrow(n.get_right(), fusion.get_left() + UP * offset,
                  buff=0.20, color=MID, stroke_width=1.8, tip_length=0.09,
                  max_tip_length_to_length_ratio=0.08)
            for n, offset in zip(nodes, [0.45, 0.0, -0.45])
        ])
        # Cả cụm to lên và căn vào giữa khung: bản cũ hàng nót dạt sát mép trái
        # còn khối hợp nhất lệch phải, nhìn trống một bên.
        VGroup(nodes, fusion, src, arrows).scale(1.14).move_to(LEFT * 0.0 + UP * 0.1)
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
        need_a = t("needs GNN", size=16, color=gs.C_GNN).next_to(node_a, UP, buff=0.16)
        need_c = t("needs LLM", size=16, color=gs.C_LLM).next_to(node_c, DOWN, buff=0.16)
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

        # ── Beat 5 (0:34–0:42): Fixed Fusion -> Node-Aware Router + câu hỏi ──
        with self.narrated_caption([
            "Vậy làm thế nào để quyết định, ở cấp độ từng nót,",
            "khi nào nên tận dụng lờ lờ mờ?",
        ]):
            left_part = VGroup(nodes, arrows, fusion, need_a, need_c)
            self.play(FadeOut(src), FadeOut(same_rule),
                      left_part.animate.scale(0.85).shift(LEFT * 1.5),
                      run_time=0.8)

            router = module("Node-Aware Router", "decide per node", width=3.8, height=1.3, emphasized=True)
            router[0].set_stroke(gs.C_ROUTER)
            router[1][0].set_color(gs.C_ROUTER)

            r_arr_g = small_arrow(router.get_right() + UP * 0.22,
                                  router.get_right() + RIGHT * 1.2 + UP * 0.6, color=gs.C_GNN)
            r_arr_l = small_arrow(router.get_right() + DOWN * 0.22,
                                  router.get_right() + RIGHT * 1.2 + DOWN * 0.6, color=gs.C_LLM)
            r_g = t("Keep GNN", size=18, color=gs.C_GNN, weight=BOLD).next_to(r_arr_g.get_end(), RIGHT, buff=0.18)
            r_l = t("Query LLM", size=18, color=gs.C_LLM, weight=BOLD).next_to(r_arr_l.get_end(), RIGHT, buff=0.18)
            r_refine = t("refine GNN", size=14, color=gs.C_ROUTER).next_to(r_l, DOWN, buff=0.12, aligned_edge=LEFT)

            # Khối bên trái đang có scale tổng là 1.14 * 0.85 = 0.969
            right_part = VGroup(router, r_arr_g, r_arr_l, r_g, r_l, r_refine).scale(1.14 * 0.85)
            right_part.shift(fusion.get_center() - router.get_center())

            center = VGroup(
                t("Different nodes", size=26, color=INK, weight=BOLD),
                mt(r"\Rightarrow", size=32, color=gs.C_ROUTER),
                t("Different model utility", size=26, color=gs.C_ROUTER, weight=BOLD),
            ).arrange(RIGHT, buff=0.28).to_edge(DOWN, buff=1.1)

            self.play(ReplacementTransform(fusion, router), run_time=0.6)
            self.play(GrowArrow(r_arr_g), GrowArrow(r_arr_l),
                      FadeIn(r_g), FadeIn(r_l), FadeIn(r_refine), run_time=0.7)
            self.play(FadeOut(warn, shift=UP*0.1), FadeIn(center, shift=UP*0.1), run_time=0.7)
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

        with self.narrated_caption([
            "gờ nờ nờ đã đủ tốt cho nót a,",
            "nên ta giữ dự đoán này và không tốn thêm một lần gọi lờ lờ mờ.",
        ]):
            # Không chỉ hiện dòng chữ [SKIP LLM]: dựng thành một QUYẾT ĐỊNH giữ
            # nhánh GNN — dấu ✓, thông điệp chính "KEEP GNN", nhãn phụ nhỏ.
            keep_rows = VGroup(
                VGroup(
                    gs.check(color=gs.C_GOOD, size=0.22),
                    t("KEEP GNN", size=26, color=gs.C_GOOD, weight=BOLD),
                ).arrange(RIGHT, buff=0.18),
                t("No LLM call needed", size=16, color=MID),
                t("[SKIP LLM]", size=13, color=DIM),
            ).arrange(DOWN, buff=0.13)
            skip_card = panel(keep_rows.width + 0.6, keep_rows.height + 0.42,
                              stroke=gs.C_GOOD, fill=BG, opacity=0.9)
            keep_rows.move_to(skip_card)
            skip_label = VGroup(skip_card, keep_rows).next_to(gnn_bar_A, DOWN, buff=0.38)
            decision_arrow = small_arrow(gnn_bar_A.get_bottom(), skip_card.get_top(),
                                         color=gs.C_GOOD, buff=0.12)

            self.play(
                Indicate(group_A.target, color=gs.C_GOOD, scale_factor=1.25),
                Indicate(gnn_bar_A, color=gs.C_GOOD, scale_factor=1.04),
                run_time=0.7,
            )
            self.play(GrowArrow(decision_arrow), run_time=0.4)
            self.play(FadeIn(skip_label, scale=0.94), run_time=0.6)
            self.wait(0.4)
            skip_label = VGroup(skip_label, decision_arrow)

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

        # Câu ngắn bắt đầu bằng chữ thường và kết ngay sau chuỗi "gờ nờ nờ" bị
        # đọc méo. Viết hoa đầu câu cho giọng có ngữ điệu chuẩn và tách mệnh đề
        # thành hai vế rõ ràng; đổi text nên TTS sinh lại bản mới.
        with self.narrated_caption([
            "Các tín hiệu kéo về nhiều hướng khác nhau,",
            "nên gờ nờ nờ dự đoán sai.",
        ], speed=1.05):
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
        # Cả section neo vào MỘT hình: quần thể 100 nót. Bản cũ fade sạch màn
        # hình ngay nhịp đầu rồi để lời đọc chạy trên nền trống mấy giây.
        HARD_INDICES = [7, 16, 23, 38, 44, 51, 66, 72, 85, 93]

        with self.narrated_caption([
            "Xét một ví dụ cụ thể.",
            "Nó cho thấy vì sao độ chính xác tổng thể có thể tăng rất ít.",
        ]):
            self.play(FadeOut(self.comparison_objects, shift=UP * 0.3), run_time=0.6)
            head9 = t("100 NODES  ·  SCHEMATIC EXAMPLE", size=23, color=MID, weight=BOLD)
            head9.to_edge(UP, buff=0.6)
            population = VGroup(*[Dot(radius=0.085, color=gs.C_GNN) for _ in range(100)])
            population.arrange_in_grid(rows=10, cols=10, buff=0.17)
            population.move_to(LEFT * 3.9 + DOWN * 0.35)
            hard_dots = VGroup(*[population[i] for i in HARD_INDICES])
            hard_dots.set_color(gs.C_BAD)
            self.play(FadeIn(head9), run_time=0.4)
            self.play(
                LaggedStart(*[FadeIn(d, scale=0.55) for d in population], lag_ratio=0.012),
                run_time=1.7,
            )

        with self.narrated_caption([
            "giả sử chín mươi phần trăm là các nót dễ,",
            "còn mười phần trăm là các nót khó.",
        ]):
            easy_group = VGroup(
                t("90 easy nodes", size=30, color=gs.C_GNN, weight=BOLD),
                t("GNN 95%   ->   Fusion 94%", size=22, color=LIGHT),
            ).arrange(DOWN, buff=0.16).move_to(RIGHT * 3.15 + UP * 2.05)
            hard_group = VGroup(
                t("10 hard nodes", size=30, color=gs.C_BAD, weight=BOLD),
                t("GNN 40%   ->   Fusion 53%", size=22, color=LIGHT),
            ).arrange(DOWN, buff=0.16).move_to(RIGHT * 3.15 + UP * 0.55)
            self.play(FadeIn(easy_group, shift=UP * 0.15), run_time=0.7)
            self.play(
                FadeIn(hard_group, shift=UP * 0.15),
                LaggedStart(*[Indicate(d, color=gs.C_BAD, scale_factor=1.8)
                              for d in hard_dots], lag_ratio=0.07),
                run_time=1.0,
            )

        with self.narrated_caption(["trên nhóm khó, lờ lờ mờ giúp tăng mười ba điểm phần trăm."]):
            # Chính mười chấm coral đổi sang xanh: thấy ngay phần được cải thiện
            # chỉ là một góc nhỏ của quần thể.
            gain_hard = t("hard-node gain:  +13 pts", size=23, color=gs.C_GOOD, weight=BOLD)
            gain_hard.next_to(hard_group, DOWN, buff=0.35)
            self.play(
                LaggedStart(*[d.animate.set_color(gs.C_GOOD) for d in hard_dots], lag_ratio=0.07),
                FadeIn(gain_hard, shift=UP * 0.1),
                run_time=1.1,
            )
            gnn_eq = mt(r"\text{GNN: } 0.9{\times}95\% + 0.1{\times}40\% = 89.5\%", size=30)
            fit(gnn_eq, 6.4)
            gnn_eq.move_to(RIGHT * 3.15 + DOWN * 1.35)
            self.play(Write(gnn_eq), run_time=0.9)

        with self.narrated_caption(["nhưng trên toàn đồ thị, tổng thể chỉ tăng không chấm bốn điểm."]):
            fusion_eq = mt(r"\text{Fusion: } 0.9{\times}94\% + 0.1{\times}53\% = 89.9\%", size=30)
            fit(fusion_eq, 6.4)
            fusion_eq.next_to(gnn_eq, DOWN, buff=0.32)
            self.play(TransformFromCopy(gnn_eq, fusion_eq), run_time=0.9)
            self.play(gnn_eq.animate.set_opacity(0.35), run_time=0.4)
            gain_overall = t("overall gain:  +0.4 pts", size=23, color=MID)
            gain_overall.next_to(fusion_eq, DOWN, buff=0.28)
            self.play(FadeIn(gain_overall), run_time=0.5)

        with self.narrated_caption(["lợi ích lớn ở một nhóm nhỏ trông rất nhỏ khi tính tổng."]):
            # Câu chốt dạng chữ đã bỏ: lời thoại nói đúng ý đó rồi, và dải chữ
            # rộng bằng khung hình chỉ chen vào giữa lưới nót với hai công thức.
            # Thay bằng một nhịp nhấn chính mười chấm đã đổi màu.
            self.play(
                LaggedStart(*[Indicate(d, color=gs.C_GOOD, scale_factor=1.6)
                              for d in hard_dots], lag_ratio=0.06),
                run_time=1.0,
            )
            self.wait(0.6)

        self.sec9_objects = VGroup(head9, population, easy_group, hard_group,
                                   gnn_eq, fusion_eq, gain_hard, gain_overall)

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
        # Tách điểm xuất phát của hai nhánh để không chồng gốc lên nhau; đầu vẫn
        # cắm đúng cạnh trái của box đích.
        a_up = small_arrow(router.get_right() + UP * 0.22, keep.get_left(), color=gs.C_GNN, buff=0.14)
        a_dn = small_arrow(router.get_right() + DOWN * 0.22, query.get_left(), color=gs.C_LLM, buff=0.14)

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
