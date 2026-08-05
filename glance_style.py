"""Shared visual language for the GLANCE explainer video.

Every section imports from this module so the six independently-rendered
sections look like one video. Do NOT fork this file inside a section folder --
if you need a new helper, add it here and tell the team in the PR.

Usage inside sections/<yours>/<yours>.py:

    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
    from glance_style import *
"""

import os
import pathlib
import re

from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService

import manimpango

# --------------------------------------------------------------------------
# Fonts. Vietnamese diacritics need a font with full Latin Extended coverage.
# We pick the first installed font from the list instead of hard-coding one,
# so the same script renders on macOS, Linux and Windows machines.
# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# Trộn tiếng Anh vào lời thuyết minh tiếng Việt.
#
# Giọng vi-VN thường đọc thuật ngữ tiếng Anh theo âm Việt ("local homophily"
# thành "lô-can hô-mô-phi-ly"). Giọng multilingual của Azure đọc đúng cả hai,
# nhưng phải bọc từng đoạn trong thẻ <lang xml:lang="...">.
#
# Người viết scene KHÔNG phải gõ thẻ: cứ viết tiếng Việt xen thuật ngữ tiếng
# Anh như bình thường, GlanceScene tự bọc thẻ theo từ điển dưới đây trước khi
# gửi cho Azure, và tự gỡ thẻ ra khỏi phụ đề.
#
# Thêm thuật ngữ mới thì thêm vào đây, đừng viết thẻ SSML trong file section.
# --------------------------------------------------------------------------

EN_TERMS = [
    "large language model", "graph neural network", "embedding model",
    "LLM-as-Embedder", "LLM-as-Predictor", "RAG pipeline",
    "local homophily", "estimated homophily", "true homophily",
    "message passing", "relative degree", "structural difficulty",
    "learnable router", "label-free", "ground-truth", "low-shot",
    "text-attributed graph", "node classification", "heterophilous",
    "heterophily", "homophily", "neighborhood", "embedding", "router",
    "routing", "heuristic", "uncertainty", "clustering density",
    "degree", "node", "prompt", "token", "batch", "baseline", "accuracy",
    "dataset", "feature", "inference", "fine-tune", "enhanced",
    "routing score", "pipeline", "backbone", "representation", "prediction",
    "layer", "model",
]

# Acronym: viết cách chữ để giọng Anh đọc rời từng ký tự.
EN_ACRONYMS = {
    "GNN": "G N N", "GNNS": "G N Ns", "LLM": "L L M", "LLMS": "L L Ms",
    "MLP": "M L P", "NCS": "N C S", "GCN": "G C N", "GCNII": "G C N two",
    "SAGE": "sage", "TAG": "tag", "GLANCE": "Glance", "MOE": "M o E",
}

_EN_RE = re.compile(
    r"\b(" + "|".join(
        re.escape(t) for t in sorted(
            list(EN_ACRONYMS) + EN_TERMS, key=len, reverse=True
        )
    ) + r")\b",
    re.IGNORECASE,
)
_TAG_RE = re.compile(r"<[^>]+>")

# Các voice multilingual này có tên hợp lệ nhưng không hỗ trợ vi-VN. Azure có
# thể trả về audio rỗng thay vì một lỗi dễ hiểu, nên chặn sớm tại đây.
_VI_UNSUPPORTED_MULTILINGUAL_VOICES = {
    "en-us-jennymultilingualneural",
    "en-us-ryanmultilingualneural",
}


def azure_voice_supports_code_switch(voice):
    """Trả về True nếu voice Azure hỗ trợ code-switch vi-VN/en-US."""
    normalized = voice.strip().casefold()
    if normalized in _VI_UNSUPPORTED_MULTILINGUAL_VOICES:
        return False
    return (
        "multilingualneural" in normalized
        or normalized.endswith(":dragonhdlatestneural")
    )


def validate_azure_voice(voice):
    """Báo lỗi rõ ràng cho voice biết trước là không phát được tiếng Việt."""
    if voice.strip().casefold() in _VI_UNSUPPORTED_MULTILINGUAL_VOICES:
        raise ValueError(
            f"Azure voice {voice!r} không hỗ trợ vi-VN. "
            "Dùng en-US-AvaMultilingualNeural hoặc "
            "en-US-AndrewMultilingualNeural cho lời thoại Việt-Anh."
        )


def _xml_escape(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def ssml_mix(text, base_lang="vi-VN", en_lang="en-US"):
    """Bọc thuật ngữ tiếng Anh trong <lang> để giọng multilingual đọc đúng.

    Chỉ dùng được với giọng multilingual của Azure; giọng vi-VN thường không
    hỗ trợ phần tử <lang> và sẽ lỗi.
    """
    def tag(lang, chunk):
        return f'<lang xml:lang="{lang}">{_xml_escape(chunk)}</lang>'

    parts, last = [], 0
    for m in _EN_RE.finditer(text):
        before = text[last:m.start()]
        if before.strip():
            parts.append(tag(base_lang, before))
        elif before:
            parts.append(before)
        word = m.group(0)
        parts.append(tag(en_lang, EN_ACRONYMS.get(word.upper(), word)))
        last = m.end()
    tail = text[last:]
    if tail.strip():
        parts.append(tag(base_lang, tail))
    elif tail:
        parts.append(tail)
    return "".join(parts)


def strip_ssml(text):
    """Gỡ mọi thẻ để lấy chữ sạch cho phụ đề."""
    return re.sub(r"\s+", " ", _TAG_RE.sub("", text)).strip()


def _load_env():
    """Nạp .env ở thư mục gốc repo (key Azure). Chạy được cả khi render từ
    thư mục khác, vì đường dẫn tính theo vị trí file này."""
    env_path = pathlib.Path(__file__).resolve().parent / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _first_available(candidates, fallback="sans-serif"):
    installed = set(manimpango.list_fonts())
    for name in candidates:
        if name in installed:
            return name
    return fallback


FONT_MAIN = _first_available(
    ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans", "Liberation Sans"]
)
FONT_MONO = _first_available(
    ["Menlo", "SF Mono", "DejaVu Sans Mono", "Liberation Mono", "Courier New"]
)

# --------------------------------------------------------------------------
# Palette. Dark background, one accent per idea. Keep meanings stable:
#   GNN  -> teal        LLM -> amber        router -> violet
#   good / benefit -> green        failure / cost -> red
# --------------------------------------------------------------------------

# Bọc trong ManimColor để dùng được interpolate_color(), .lighter(), v.v.
BG = ManimColor("#0E1116")
INK = ManimColor("#E8ECF1")
MUTED = ManimColor("#8B97A8")

C_GNN = ManimColor("#3ECFB2")
C_LLM = ManimColor("#F2B441")
C_ROUTER = ManimColor("#A98BFF")
C_GOOD = ManimColor("#5BD97E")
C_BAD = ManimColor("#FF6B6B")
C_EDGE = ManimColor("#4A5468")
C_HIGHLIGHT = ManimColor("#6EA8FE")

# One accent per section, used for the section banner and key terms.
SECTION_COLORS = {
    "0": C_HIGHLIGHT,
    "1": C_BAD,
    "2": C_LLM,
    "3": C_GOOD,
    "4": C_ROUTER,
    "5": C_GNN,
}

TITLE_SIZE = 44
HEAD_SIZE = 34
BODY_SIZE = 26
SMALL_SIZE = 20


# --------------------------------------------------------------------------
# Text helpers
# --------------------------------------------------------------------------

def txt(s, size=BODY_SIZE, color=INK, weight=NORMAL, **kw):
    """Vietnamese-safe text."""
    return Text(s, font=FONT_MAIN, font_size=size, color=color, weight=weight, **kw)


def mono(s, size=SMALL_SIZE, color=MUTED, **kw):
    return Text(s, font=FONT_MONO, font_size=size, color=color, **kw)


def heading(s, color=INK):
    return txt(s, size=HEAD_SIZE, color=color, weight=BOLD)


def bullets(items, size=BODY_SIZE, buff=0.42, dot_color=C_HIGHLIGHT, width=9.5):
    """Left-aligned bullet list. `items` is a list of strings."""
    rows = VGroup()
    for item in items:
        marker = Dot(radius=0.055, color=dot_color)
        body = txt(item, size=size)
        if body.width > width:
            body.scale_to_fit_width(width)
        row = VGroup(marker, body).arrange(RIGHT, buff=0.28)
        marker.align_to(body, UP).shift(DOWN * 0.16)
        rows.add(row)
    rows.arrange(DOWN, aligned_edge=LEFT, buff=buff)
    return rows


def caption(s, size=SMALL_SIZE):
    """Small grey line, e.g. a paper reference. Pin it to the bottom yourself."""
    return txt(s, size=size, color=MUTED)


def source(ref):
    """Bottom-right provenance stamp: source('Table 1, tr.4')."""
    return caption(f"Nguồn: {ref}").to_corner(DR, buff=0.35)


# --------------------------------------------------------------------------
# Cards and banners
# --------------------------------------------------------------------------

def title_card(title, subtitle=None, owner=None, accent=C_HIGHLIGHT):
    """Opening card of a section."""
    parts = VGroup(heading(title, color=accent))
    if subtitle:
        parts.add(txt(subtitle, size=BODY_SIZE, color=INK))
    if owner:
        parts.add(txt(owner, size=SMALL_SIZE, color=MUTED))
    parts.arrange(DOWN, buff=0.35)
    rule = Line(LEFT * 3, RIGHT * 3, color=accent, stroke_width=3)
    rule.next_to(parts[0], DOWN, buff=0.22)
    return VGroup(parts, rule)


def section_banner(number, name, accent=None):
    """Persistent top-left marker, e.g. section_banner('3', 'Structural signal')."""
    accent = accent or SECTION_COLORS.get(str(number), C_HIGHLIGHT)
    tag = VGroup(
        RoundedRectangle(
            corner_radius=0.1, width=0.72, height=0.46,
            stroke_width=0, fill_color=accent, fill_opacity=1,
        ),
        txt(str(number), size=SMALL_SIZE, color=BG, weight=BOLD),
    )
    label = txt(name, size=SMALL_SIZE, color=MUTED)
    banner = VGroup(tag, label).arrange(RIGHT, buff=0.28)
    return banner.to_corner(UL, buff=0.35)


def panel(mobject, color=C_EDGE, buff=0.4, fill_opacity=0.06):
    """Rounded frame around content, for side-by-side comparisons."""
    return SurroundingRectangle(
        mobject, color=color, corner_radius=0.18, buff=buff,
        stroke_width=2, fill_color=color, fill_opacity=fill_opacity,
    )


def labeled_box(label, color, width=2.6, height=1.1):
    """A model block: labeled_box('GNN', C_GNN)."""
    box = RoundedRectangle(
        corner_radius=0.16, width=width, height=height,
        stroke_color=color, stroke_width=3,
        fill_color=color, fill_opacity=0.12,
    )
    return VGroup(box, txt(label, size=BODY_SIZE, color=color, weight=BOLD))


def pipeline(steps, direction=RIGHT, box_w=2.0, box_h=0.85, buff=0.55,
             arrow_color=MUTED, text_size=SMALL_SIZE):
    """A chain of labelled boxes joined by arrows.

    steps: list of (label, color) tuples.
    Returns a VGroup with `.boxes` (VGroup) and `.arrows` (VGroup).
    """
    boxes = VGroup()
    for label, color in steps:
        box = labeled_box(label, color, width=box_w, height=box_h)
        box[1].set(font_size=text_size)
        if box[1].width > box_w - 0.25:
            box[1].scale_to_fit_width(box_w - 0.25)
        box[1].move_to(box[0])
        boxes.add(box)
    boxes.arrange(direction, buff=buff)

    arrows = VGroup()
    for a, b in zip(boxes[:-1], boxes[1:]):
        arrows.add(Arrow(
            a.get_edge_center(direction), b.get_edge_center(-direction),
            buff=0.08, stroke_width=3, max_tip_length_to_length_ratio=0.22,
            color=arrow_color,
        ))

    g = VGroup(boxes, arrows)
    g.boxes = boxes
    g.arrows = arrows
    return g


def check(color=C_GOOD, size=0.42):
    mark = VGroup(
        Line(LEFT * 0.18 + DOWN * 0.02, DOWN * 0.16, stroke_width=6, color=color),
        Line(DOWN * 0.16, RIGHT * 0.22 + UP * 0.2, stroke_width=6, color=color),
    )
    return mark.scale(size / 0.42)


def cross(color=C_BAD, size=0.36):
    mark = VGroup(
        Line(UL, DR, stroke_width=6, color=color),
        Line(DL, UR, stroke_width=6, color=color),
    ).scale(size)
    return mark


# --------------------------------------------------------------------------
# Graph helpers. The TAG picture recurs in almost every section, so build it
# the same way everywhere.
# --------------------------------------------------------------------------

def tag_graph(edges, positions, labels=None, radius=0.16, scale=1.0,
              node_color=C_HIGHLIGHT, edge_color=C_EDGE):
    """Return a VGroup with `.nodes` (dict id -> Dot) and `.edges` (VGroup).

    edges:     list of (u, v) id pairs
    positions: dict id -> np.array / list of 3 floats (scene coordinates)
    labels:    optional dict id -> class label; nodes sharing a label share a colour
    """
    palette = [C_GNN, C_LLM, C_ROUTER, C_GOOD, C_BAD]
    label_color = {}
    if labels:
        for i, lab in enumerate(sorted(set(labels.values()))):
            label_color[lab] = palette[i % len(palette)]

    nodes = {}
    for nid, pos in positions.items():
        color = label_color[labels[nid]] if labels else node_color
        nodes[nid] = Dot(np.array(pos, dtype=float) * scale, radius=radius, color=color)

    edge_group = VGroup()
    for u, v in edges:
        edge_group.add(
            Line(nodes[u].get_center(), nodes[v].get_center(),
                 stroke_width=2.2, color=edge_color, z_index=-1)
        )

    g = VGroup(edge_group, VGroup(*nodes.values()))
    g.nodes = nodes
    g.edges = edge_group
    return g


# The recurring 12-node example graph. Same layout in every section so the
# audience recognises it. Node 4 is the homophilous hub, node 9 the heterophilous
# low-degree node -- those two carry the story.
DEMO_POS = {
    0: [-2.6, 1.5, 0], 1: [-1.4, 2.1, 0], 2: [-0.6, 1.0, 0],
    3: [-2.2, 0.2, 0], 4: [-1.3, 1.0, 0], 5: [0.7, 1.8, 0],
    6: [1.8, 1.1, 0], 7: [2.6, 2.0, 0], 8: [2.2, -0.2, 0],
    9: [0.5, -0.6, 0], 10: [-0.7, -1.3, 0], 11: [1.7, -1.5, 0],
}
DEMO_EDGES = [
    (0, 1), (0, 3), (0, 4), (1, 4), (2, 4), (3, 4), (1, 2),
    (2, 5), (5, 6), (5, 7), (6, 7), (6, 8),
    (9, 2), (9, 8), (9, 10), (9, 11), (10, 3), (11, 8),
]
# Two classes: 'A' = homophilous cluster on the left, 'B' = the right/bottom side.
DEMO_LABELS = {
    0: "A", 1: "A", 2: "A", 3: "A", 4: "A",
    5: "B", 6: "B", 7: "B", 8: "B", 9: "A", 10: "B", 11: "B",
}


def demo_tag(labels=True, **kw):
    """The shared 12-node example TAG. Node 4 = high homophily/degree hub,
    node 9 = low homophily node (class A surrounded mostly by class B)."""
    return tag_graph(
        DEMO_EDGES, DEMO_POS,
        labels=DEMO_LABELS if labels else None,
        **kw,
    )


def ego_ring(graph, center_id, hop_ids, color=C_LLM, buff=0.22):
    """Dashed circle around an ego node and its listed neighbours."""
    members = VGroup(graph.nodes[center_id], *[graph.nodes[i] for i in hop_ids])
    return DashedVMobject(
        Circle(radius=members.width / 2 + buff, color=color, stroke_width=2.5)
        .move_to(graph.nodes[center_id]),
        num_dashes=36,
    )


def text_chip(s, color=C_LLM, width=2.4):
    """A little 'raw text' card hanging off a node."""
    body = mono(s, size=15, color=INK)
    if body.width > width - 0.3:
        body.scale_to_fit_width(width - 0.3)
    card = RoundedRectangle(
        corner_radius=0.08, width=width, height=body.height + 0.32,
        stroke_color=color, stroke_width=1.6,
        fill_color=BG, fill_opacity=0.9,
    )
    return VGroup(card, body)


# --------------------------------------------------------------------------
# Charts. Hand-rolled so every bar chart in the video matches.
# --------------------------------------------------------------------------

def bar_chart(values, labels, colors=None, y_range=(0, 1, 0.25),
              width=7.0, height=3.4, value_fmt="{:.2f}"):
    """Simple vertical bar chart with value labels on top.

    Negative values are supported (useful for the NCS plot in section 2).
    """
    colors = colors or [C_HIGHLIGHT] * len(values)
    lo, hi, step = y_range
    axes = Axes(
        x_range=[0, len(values), 1],
        y_range=[lo, hi, step],
        x_length=width,
        y_length=height,
        tips=False,
        axis_config={"color": C_EDGE, "stroke_width": 2,
                     "font_size": 20, "include_ticks": False},
        y_axis_config={"include_ticks": True, "include_numbers": True,
                       "decimal_number_config": {"num_decimal_places": 2}},
    )
    axes.y_axis.set_color(C_EDGE)
    bar_w = width / len(values) * 0.55

    bars = VGroup()
    for i, (val, lab, col) in enumerate(zip(values, labels, colors)):
        x0 = axes.c2p(i + 0.5, 0)
        x1 = axes.c2p(i + 0.5, val)
        h = abs(x1[1] - x0[1])
        bar = Rectangle(
            width=bar_w, height=max(h, 0.01),
            stroke_width=0, fill_color=col, fill_opacity=0.85,
        )
        bar.move_to((x0 + x1) / 2)
        vlab = txt(value_fmt.format(val), size=16, color=col)
        vlab.next_to(bar, UP if val >= 0 else DOWN, buff=0.12)
        xlab = txt(lab, size=16, color=MUTED)
        xlab.next_to(axes.c2p(i + 0.5, lo), DOWN, buff=0.18)
        bars.add(VGroup(bar, vlab, xlab))

    chart = VGroup(axes, bars)
    chart.axes = axes
    chart.bars = bars
    return chart


def line_chart(series, x_labels, y_range=(0.0, 1.0, 0.2), width=7.0, height=3.6,
               bars=None, bar_label=None, dot_radius=0.055, legend=True,
               x_label=None, label_size=15):
    """Multi-series line chart over categorical bins -- the Figure 1 shape.

    series:    list of dicts {"name": str, "values": [...], "color": color,
                              "dashed": bool (default True)}
    x_labels:  bin labels, same length as each series' values
    bars:      optional list of counts drawn as grey background bars
               (node-count distribution, like the paper's right y-axis)

    Returns a VGroup with `.axes`, `.plots` (dict name -> VGroup of line+dots),
    `.legend`, and `.point(name, i)` giving the scene coordinate of a marker.
    """
    lo, hi, step = y_range
    n = len(x_labels)
    axes = Axes(
        x_range=[0, n, 1],
        y_range=[lo, hi + 1e-9, step],
        x_length=width,
        y_length=height,
        tips=False,
        axis_config={"color": C_EDGE, "stroke_width": 2, "include_ticks": False},
        x_axis_config={"include_numbers": False},
        y_axis_config={
            "include_ticks": True, "include_numbers": True, "font_size": 18,
            "decimal_number_config": {"num_decimal_places": 2},
        },
    )
    axes.y_axis.numbers.set_color(MUTED)

    group = VGroup(axes)

    # Background bars (node counts), scaled so the tallest reaches ~92% height.
    if bars:
        top = max(bars)
        bar_w = width / n * 0.78
        bar_group = VGroup()
        for i, count in enumerate(bars):
            frac = count / top * 0.92
            y_top = lo + (hi - lo) * frac
            base = axes.c2p(i + 0.5, lo)
            tip = axes.c2p(i + 0.5, y_top)
            rect = Rectangle(
                width=bar_w, height=max(tip[1] - base[1], 0.01),
                stroke_width=0, fill_color=MUTED, fill_opacity=0.16,
            ).move_to((base + tip) / 2)
            bar_group.add(rect)
        group.add(bar_group)
        group.bars = bar_group
        if bar_label:
            lab = txt(bar_label, size=14, color=MUTED).rotate(PI / 2)
            lab.next_to(axes, RIGHT, buff=0.12)
            group.add(lab)

    plots = {}
    for spec in series:
        color = spec.get("color", C_HIGHLIGHT)
        pts = [axes.c2p(i + 0.5, v) for i, v in enumerate(spec["values"])]
        path = VGroup()
        for a, b in zip(pts[:-1], pts[1:]):
            seg = Line(a, b, stroke_width=3, color=color)
            if spec.get("dashed", True):
                seg = DashedVMobject(seg, num_dashes=6)
            path.add(seg)
        dots = VGroup(*[Dot(p, radius=dot_radius, color=color) for p in pts])
        plot = VGroup(path, dots)
        plot.dots = dots
        plot.path = path
        plots[spec["name"]] = plot
        group.add(plot)

    # x tick labels, slanted like the paper's
    ticks = VGroup()
    for i, lab in enumerate(x_labels):
        t = txt(lab, size=label_size, color=MUTED).rotate(PI / 9)
        t.next_to(axes.c2p(i + 0.5, lo), DOWN, buff=0.18)
        ticks.add(t)
    group.add(ticks)
    if x_label:
        xl = txt(x_label, size=16, color=MUTED)
        xl.next_to(ticks, DOWN, buff=0.18)
        group.add(xl)

    leg = VGroup()
    if legend:
        for spec in series:
            color = spec.get("color", C_HIGHLIGHT)
            key = VGroup(
                Line(LEFT * 0.16, RIGHT * 0.16, stroke_width=3, color=color),
                Dot(radius=0.05, color=color),
            )
            leg.add(VGroup(key, txt(spec["name"], size=15, color=INK))
                    .arrange(RIGHT, buff=0.16))
        leg.arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        group.add(leg)

    group.axes = axes
    group.plots = plots
    group.legend = leg
    group.ticks = ticks
    group.point = lambda name, i: plots[name].dots[i].get_center()
    return group


# --------------------------------------------------------------------------
# Scene base class. Inherit from this so background, banner and the subtitle
# habit are identical across sections.
# --------------------------------------------------------------------------

class GlanceScene(VoiceoverScene):
    """Base scene: nền tối + banner section + thuyết minh tự đồng bộ.

    Subclass đặt `section`, `section_name`, gọi `self.banner()` ở đầu
    construct(), rồi bọc animation trong khối thuyết minh:

        with self.voiceover(text="Câu thuyết minh.") as tracker:
            self.play(Create(circle), run_time=tracker.duration)

    Thời lượng animation bám theo độ dài file audio, không phải đoán tay.
    Khối `with` tự chờ nốt phần audio còn thừa khi animation ngắn hơn lời đọc.
    Phụ đề .srt được plugin sinh tự động từ chính `text` — không gọi
    add_subcaption thủ công nữa, sẽ bị trùng.

    Giọng đọc tự chọn: có AZURE_SUBSCRIPTION_KEY trong .env thì dùng Azure,
    không thì rơi về gTTS. Ép thủ công bằng biến môi trường:
        GLANCE_TTS=azure  (giọng vi-VN tự nhiên, cần AZURE_* trong .env)
        GLANCE_TTS=gtts   (free, cần mạng, hay bị rate-limit khi nhiều câu mới)
        GLANCE_TTS=record (tự thu giọng thật qua CLI lúc render)
    """

    section = None
    section_name = ""
    voice_lang = "vi"
    # Giọng multilingual đọc đúng cả tiếng Việt lẫn thuật ngữ tiếng Anh.
    # Giọng nam: en-US-AndrewMultilingualNeural.
    # Muốn giọng vi-VN thuần: đặt azure_voice = "vi-VN-HoaiMyNeural" (khi đó
    # thuật ngữ tiếng Anh sẽ bị đọc theo âm Việt, và <lang> tự động tắt).
    azure_voice = "en-US-AvaMultilingualNeural"
    _multilingual = False

    def setup(self):
        self.camera.background_color = BG
        self.set_speech_service(self.speech_service(), create_subcaption=True)

    def voiceover(self, text=None, **kwargs):
        """Tự bọc thuật ngữ tiếng Anh bằng <lang> và giữ phụ đề sạch thẻ."""
        if text is not None and self._multilingual:
            kwargs.setdefault("subcaption", strip_ssml(text))
            text = ssml_mix(text)
        return super().voiceover(text=text, **kwargs)

    def speech_service(self):
        _load_env()
        backend = os.environ.get("GLANCE_TTS", "").lower()
        if not backend:
            backend = "azure" if os.environ.get("AZURE_SUBSCRIPTION_KEY") else "gtts"

        if backend == "azure":
            from manim_voiceover.services.azure import AzureService
            voice = os.environ.get("GLANCE_VOICE", self.azure_voice)
            validate_azure_voice(voice)
            self._multilingual = azure_voice_supports_code_switch(voice)
            return AzureService(voice=voice)
        if backend in ("record", "recorder"):
            from manim_voiceover.services.recorder import RecorderService
            return RecorderService()
        return GTTSService(lang=self.voice_lang)

    def banner(self):
        if self.section is None:
            return None
        b = section_banner(self.section, self.section_name)
        self.add(b)
        return b

    def pad_to(self, target):
        """Chờ tới đúng mốc `target` giây tính từ đầu scene.

        Dùng khi kịch bản quy định mốc thời gian cụ thể: chạy animation xong thì
        gọi pad_to(18) để nhịp tiếp theo bắt đầu đúng giây thứ 18.
        """
        now = self.renderer.time
        if target > now:
            self.wait(target - now)
        return self.renderer.time

    def say(self, text):
        """Nhịp chỉ có lời đọc, không animation. Trả về tracker."""
        with self.voiceover(text=text) as tracker:
            self.wait(tracker.duration)
        return tracker

    def clear_scene(self, keep=()):
        """Fade out everything except `keep` mobjects."""
        leaving = [m for m in self.mobjects if m not in keep]
        if leaving:
            self.play(*[FadeOut(m) for m in leaving], run_time=0.6)
