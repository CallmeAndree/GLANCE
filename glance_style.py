"""Shared visual language for the GLANCE explainer video.

Every section imports from this module so the six independently-rendered
sections look like one video. Do NOT fork this file inside a section folder --
if you need a new helper, add it here and tell the team in the PR.

Usage inside sections/<yours>/<yours>.py:

    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
    from glance_style import *
"""

import json
import os
import pathlib
import re
from urllib import error as urlerror
from urllib import request as urlrequest

from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.helper import remove_bookmarks
from manim_voiceover.services.base import SpeechService

# GTTSService cố tình KHÔNG import ở đây. Import nó khi chưa cài extra `gtts`
# sẽ in một dòng ERROR mỗi lần chạy manim, kể cả khi cả nhóm dùng backend
# `timed`. Nó được import bên trong speech_service() khi thật sự cần, giống
# cách làm sẵn có với AzureService và RecorderService.

import manimpango


DEFAULT_TIMED_TTS_URL = (
    "https://gig-largest-submissions-pending.trycloudflare.com/v1/audio/speech"
)
DEFAULT_TIMED_TTS_VOICE = "longkhongphainong"
DEFAULT_TIMED_TTS_KEY_FILE = ".run/api.key"


class TimedTTSService(SpeechService):
    """Adapter cho API speech tương thích OpenAI, trả file audio trực tiếp."""

    def __init__(
        self,
        endpoint,
        token,
        voice=DEFAULT_TIMED_TTS_VOICE,
        audio_format="mp3",
        timeout=120,
        **kwargs,
    ):
        if not endpoint:
            raise ValueError("Thiếu endpoint cho timed TTS.")
        if not token:
            raise ValueError("Thiếu API key cho backend GLANCE_TTS=timed.")
        super().__init__(**kwargs)
        self.endpoint = endpoint.rstrip("/")
        self.token = token
        self.voice = voice
        self.audio_format = audio_format.lower()
        self.timeout = timeout

    def generate_from_text(self, text, cache_dir=None, path=None, **kwargs):
        cache_dir = pathlib.Path(cache_dir or self.cache_dir)
        input_text = remove_bookmarks(text)
        input_data = {
            "input_text": input_text,
            "service": "glance-timed-tts-v1",
            "endpoint": self.endpoint,
            "voice": self.voice,
            "format": self.audio_format,
        }

        cached = self.get_cached_result(input_data, cache_dir)
        if cached is not None:
            cached_audio = cache_dir / cached["original_audio"]
            if cached_audio.is_file():
                return cached

        audio_path = path or (
            self.get_audio_basename(input_data) + f".{self.audio_format}"
        )
        payload = json.dumps(
            {
                "input": input_text,
                "voice": self.voice,
                "response_format": self.audio_format,
            },
            ensure_ascii=False,
        ).encode("utf-8")
        request = urlrequest.Request(
            self.endpoint,
            data=payload,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urlrequest.urlopen(request, timeout=self.timeout) as response:
                audio = response.read()
        except urlerror.HTTPError as exc:
            detail = exc.read(500).decode("utf-8", errors="replace")
            raise RuntimeError(
                f"Timed TTS trả HTTP {exc.code}: {detail}"
            ) from exc
        except urlerror.URLError as exc:
            raise RuntimeError(f"Không kết nối được timed TTS: {exc.reason}") from exc
        if not audio:
            raise RuntimeError("Timed TTS trả file audio rỗng.")

        destination = cache_dir / audio_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_suffix(destination.suffix + ".tmp")
        temporary.write_bytes(audio)
        temporary.replace(destination)

        return {
            "input_text": text,
            "input_data": input_data,
            "original_audio": audio_path,
        }


def _read_tts_key(key_file):
    """Đọc bearer key ngoài Git; đường dẫn tương đối tính từ root repo."""
    path = pathlib.Path(key_file).expanduser()
    if not path.is_absolute():
        path = pathlib.Path(__file__).resolve().parent / path
    if not path.is_file():
        raise ValueError(
            f"Thiếu API key tại {path}. Tạo file này theo README; không commit key."
        )
    token = path.read_text(encoding="utf-8").strip()
    if not token:
        raise ValueError(f"API key tại {path} đang rỗng.")
    return token

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

# Light/deep variants of the LLM accent, for sections that need to distinguish
# several LLM-derived signals (e.g. ego / 1-hop / 2-hop context embeddings)
# while keeping them recognisably in the same "LLM = amber" family.
C_LLM_LIGHT = ManimColor("#F7CE85")
C_LLM_DEEP = ManimColor("#C98A1E")

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


def mt(tex, size=32, color=INK, **kw):
    """MathTex viết ngắn, dùng cho các công thức chèn trong câu.

    Chỉ dùng cho công thức toán. Tiếng Việt phải đi qua txt() vì LaTeX mặc định
    không dựng được dấu.
    """
    return MathTex(tex, font_size=size, color=color, **kw)


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
# Diagram building blocks. Small labelled shapes for architecture walk-throughs
# (model boxes, equation cards, embedding strips, MLP diagrams, prompt cards).
# Added for the GLANCE-architecture section; reusable by any section that
# needs to draw a pipeline of labelled boxes and vectors.
# --------------------------------------------------------------------------

def fit_width(mobject, width):
    """Shrink `mobject` in place if it is wider than `width`."""
    if mobject.width > width:
        mobject.scale_to_fit_width(width)
    return mobject


def avatar_node(label, target=False, radius=0.30):
    """A labelled circle standing in for one example node, e.g. avatar_node("A").

    Outlined, not filled: dark disc behind a light ring. `target=True` brightens
    and thickens the ring instead of switching hue, so the focus node still reads
    first on a still frame without spending one of the palette's meanings on it.
    """
    circle = Circle(
        radius=radius,
        fill_color=BG,
        fill_opacity=1,
        stroke_color=INK if target else MUTED,
        stroke_width=2.6 if target else 1.8,
    )
    label_mob = txt(label, size=20, color=INK if target else MUTED, weight=BOLD).move_to(circle)
    return VGroup(circle, label_mob)


def step_header(number, title):
    """Numbered step banner for a scene sequence, e.g. step_header(2, "Aggregate").

    Starts clear of the top-left corner (offset right by ~4.3 units) so it
    never overlaps a `section_banner()` placed there in the same scene.
    """
    number_mob = txt(f"{number:02d}", size=SMALL_SIZE, color=BG, weight=BOLD)
    pill = RoundedRectangle(
        width=0.62, height=0.38, corner_radius=0.10,
        fill_color=INK, fill_opacity=1, stroke_width=0,
    )
    number_mob.move_to(pill)
    title_mob = fit_width(txt(title, size=HEAD_SIZE, color=INK, weight=BOLD), 8.6)
    head = VGroup(VGroup(pill, number_mob), title_mob).arrange(RIGHT, buff=0.22)
    head.to_corner(UL, buff=0.32).shift(RIGHT * 4.3)
    rule = Line(LEFT * 6.7, RIGHT * 6.7, color=C_EDGE, stroke_width=1.5)
    rule.to_edge(UP, buff=0.98)
    return VGroup(head, rule)


def takeaway_chip(text_value):
    """Small pill-shaped takeaway line pinned to the bottom of the frame."""
    body = fit_width(txt(text_value, size=21, color=MUTED, weight=BOLD), 11.8)
    bg = RoundedRectangle(
        width=max(body.width + 0.45, 4.8), height=body.height + 0.25,
        corner_radius=0.10, fill_color=BG, fill_opacity=0.94,
        stroke_color=C_EDGE, stroke_width=1,
    )
    body.move_to(bg)
    return VGroup(bg, body).to_edge(DOWN, buff=0.18)


def doc_icon(scale=1.0):
    """Tiny document glyph, a stand-in for 'raw node text'."""
    page = RoundedRectangle(
        width=0.36, height=0.46, corner_radius=0.04,
        fill_color=BG, fill_opacity=1, stroke_color=MUTED, stroke_width=1.2,
    )
    lines = VGroup(*[
        Line(LEFT * 0.11, RIGHT * 0.11, color=MUTED, stroke_width=1) for _ in range(3)
    ]).arrange(DOWN, buff=0.06).move_to(page)
    return VGroup(page, lines).scale(scale)


def _box(width, height, stroke=MUTED, fill=BG, radius=0.18):
    return RoundedRectangle(
        width=width, height=height, corner_radius=radius,
        stroke_color=stroke, stroke_width=1.6, fill_color=fill, fill_opacity=1,
    )


def module_box(title, subtitle, width=4.5, height=1.05, emphasized=False):
    """A labelled model block with a subtitle, e.g. module_box("GNN", "backbone")."""
    outer = _box(width, height, stroke=INK if emphasized else MUTED, fill=BG)
    title_mob = fit_width(txt(title, size=24, color=INK if emphasized else MUTED, weight=BOLD), width - 0.35)
    subtitle_mob = fit_width(txt(subtitle, size=17, color=MUTED), width - 0.35)
    content = VGroup(title_mob, subtitle_mob).arrange(DOWN, buff=0.08).move_to(outer)
    return VGroup(outer, content)


def math_module_box(tex, subtitle, width=4.0, height=0.95, emphasized=False):
    """Like module_box, but the title is a LaTeX formula."""
    outer = _box(width, height, stroke=INK if emphasized else MUTED, fill=BG)
    title_mob = fit_width(MathTex(tex, font_size=30, color=INK if emphasized else MUTED), width - 0.35)
    subtitle_mob = fit_width(txt(subtitle, size=17, color=MUTED), width - 0.35)
    content = VGroup(title_mob, subtitle_mob).arrange(DOWN, buff=0.08).move_to(outer)
    return VGroup(outer, content)


def equation_card(formula, subtitle, width=4.2, height=1.25, emphasized=False):
    """A boxed formula with a caption underneath."""
    box = _box(width, height, stroke=INK if emphasized else MUTED, fill=BG)
    equation = fit_width(MathTex(formula, font_size=40, color=INK if emphasized else MUTED), width - 0.34)
    label = txt(subtitle, size=19, color=MUTED)
    content = VGroup(equation, label).arrange(DOWN, buff=0.12).move_to(box)
    return VGroup(box, content)


def feature_strip(label, n=7, cell_size=0.34, math_label=False):
    """A row of small squares standing in for an opaque feature vector."""
    cells = VGroup(*[
        Square(
            side_length=cell_size, stroke_color=MUTED, stroke_width=1.2,
            fill_color=INK if i % 3 == 0 else (MUTED if i % 3 == 1 else C_EDGE),
            fill_opacity=0.92,
        )
        for i in range(n)
    ]).arrange(RIGHT, buff=0.035)
    label_mob = MathTex(label, font_size=28, color=INK) if math_label else txt(label, size=22, color=INK, weight=BOLD)
    return VGroup(label_mob, cells).arrange(RIGHT, buff=0.18)


def probability_bars(label, values, width=2.25, math_label=False):
    """A small stack of horizontal bars, one per class probability."""
    label_mob = MathTex(label, font_size=25, color=INK) if math_label else txt(label, size=19, color=INK, weight=BOLD)
    bars = VGroup()
    for value in values:
        track = RoundedRectangle(
            width=width, height=0.17, corner_radius=0.04,
            fill_color=C_EDGE, fill_opacity=1, stroke_width=0,
        )
        fill_bar = RoundedRectangle(
            width=max(width * value, 0.05), height=0.17, corner_radius=0.04,
            fill_color=MUTED, fill_opacity=1, stroke_width=0,
        ).align_to(track, LEFT)
        bars.add(VGroup(track, fill_bar))
    bars.arrange(DOWN, buff=0.07)
    return VGroup(label_mob, bars).arrange(RIGHT, buff=0.15)


def embedding_strip(label, color, n=9, cell_size=0.29, emphasized=False):
    """A row of coloured cells representing a learned embedding, labelled by its name."""
    cells = VGroup(*[
        Square(
            side_length=cell_size, stroke_color=INK if emphasized else MUTED, stroke_width=1.1,
            fill_color=color, fill_opacity=0.95 if index % 2 == 0 else 0.65,
        )
        for index in range(n)
    ]).arrange(RIGHT, buff=0.03)
    label_mob = MathTex(label, font_size=29, color=color if emphasized else INK)
    return VGroup(label_mob, cells).arrange(RIGHT, buff=0.18)


def named_embedding_strip(label, color, n=7, cell_size=0.25):
    """Embedding strip whose mathematical name is centered above the cells."""
    cells = VGroup(*[
        Square(
            side_length=cell_size, stroke_color=MUTED, stroke_width=1.0,
            fill_color=color, fill_opacity=0.95 if index % 2 == 0 else 0.65,
        )
        for index in range(n)
    ]).arrange(RIGHT, buff=0.03)
    return VGroup(MathTex(label, font_size=29, color=color), cells).arrange(DOWN, buff=0.14)


def segmented_embedding(label, segments, cells_per_segment=4, cell_size=0.28):
    """An embedding strip made of several coloured segments, e.g. one per source."""
    cells = VGroup()
    for color in segments:
        for index in range(cells_per_segment):
            cells.add(
                Square(
                    side_length=cell_size, stroke_color=MUTED, stroke_width=1.0,
                    fill_color=color, fill_opacity=0.95 if index % 2 == 0 else 0.65,
                )
            )
    cells.arrange(RIGHT, buff=0.028)
    return VGroup(MathTex(label, font_size=29, color=INK), cells).arrange(RIGHT, buff=0.18)


def router_glyph(radius=0.66):
    """A divided circle with aggregation and sigmoid, standing in for the router."""
    ring = Circle(
        radius=radius, stroke_color=C_ROUTER, stroke_width=4.0,
        fill_color=BG, fill_opacity=1.0,
    )
    divider = Line(
        ring.get_top() + DOWN * 0.06, ring.get_bottom() + UP * 0.06,
        color=C_ROUTER, stroke_width=3.0,
    )
    sigma_sum = MathTex(r"\Sigma", font_size=43, color=INK).move_to(LEFT * radius * 0.48)
    sigma_gate = MathTex(r"\sigma", font_size=43, color=INK).move_to(RIGHT * radius * 0.48)
    return VGroup(ring, divider, sigma_sum, sigma_gate)


def score_row(label, value, active=True, width=3.35):
    """One row of a routing-score ranking: an avatar plus its score."""
    icon = avatar_node(label, target=active, radius=0.22)
    expression = MathTex(rf"a_{{{label}}}={value:.2f}", font_size=29, color=INK if active else MUTED)
    content = VGroup(icon, expression).arrange(RIGHT, buff=0.28)
    box = _box(width, 0.62, stroke=INK if active else MUTED, fill=BG, radius=0.10)
    content.move_to(box)
    return VGroup(box, content)


def prompt_panel(title_text, lines, width=8.8, height=3.65):
    """A card showing a serialized LLM prompt: a title plus a few example lines."""
    box = _box(width, height, stroke=MUTED, fill=BG)
    title_mob = txt(title_text, size=24, color=INK, weight=BOLD)
    body = VGroup(*[
        fit_width(
            txt(line, size=20, color=INK if index == 0 else MUTED, weight=BOLD if index == 0 else NORMAL),
            width - 0.75,
        )
        for index, line in enumerate(lines)
    ]).arrange(DOWN, aligned_edge=LEFT, buff=0.17)
    content = VGroup(title_mob, body).arrange(DOWN, aligned_edge=LEFT, buff=0.30).move_to(box)
    return VGroup(box, content)


def small_arrow(start, end, color=MUTED, stroke_width=2.0, buff=0.10):
    return Arrow(start, end, buff=buff, color=color, stroke_width=stroke_width, tip_length=0.10)


def probability_chart(values, title_tex, class_names, width=5.15):
    """A small titled bar list, one row per class probability."""
    title = MathTex(title_tex, font_size=31, color=INK)
    rows = VGroup()
    # The name slot has to clear the *widest* label, not a guessed constant: a
    # VGroup takes the union of its parts, so a label wider than its slot grows
    # the column and pushes that row's bar right, leaving the bars ragged.
    names = [txt(n, size=19, color=MUTED, weight=BOLD) for n in class_names]
    slot_width = max(1.82, max(n.width for n in names) + 0.06)
    for name, value in zip(names, values):
        name_slot = Rectangle(width=slot_width, height=0.26, stroke_opacity=0, fill_opacity=0)
        name.move_to(name_slot).align_to(name_slot, LEFT)
        name_column = VGroup(name_slot, name)
        track = RoundedRectangle(
            width=2.25, height=0.22, corner_radius=0.05,
            fill_color=C_EDGE, fill_opacity=1, stroke_width=0,
        )
        fill = RoundedRectangle(
            width=max(2.25 * value, 0.06), height=0.22, corner_radius=0.05,
            fill_color=INK, fill_opacity=1, stroke_width=0,
        ).align_to(track, LEFT)
        number = txt(f"{value:.2f}", size=18, color=INK, weight=BOLD)
        bar = VGroup(track, fill)
        value_group = VGroup(bar, number).arrange(RIGHT, buff=0.12)
        rows.add(VGroup(name_column, value_group).arrange(RIGHT, buff=0.20))
    rows.arrange(DOWN, aligned_edge=LEFT, buff=0.23)
    content = VGroup(title, rows).arrange(DOWN, aligned_edge=LEFT, buff=0.32)
    box = _box(width, content.height + 0.58, stroke=MUTED, fill=BG)
    content.move_to(box)
    return VGroup(box, content)


def mlp_diagram(layer_sizes=(5, 6, 4, 3), radius=0.105, layer_gap=0.56, node_gap=0.34):
    """Vertical MLP: neuron rows flow from top to bottom. Returns (network, edges, layers)."""
    layers = VGroup()
    for size in layer_sizes:
        layer = VGroup(*[
            Circle(radius=radius, stroke_color=MUTED, stroke_width=1.3, fill_color=BG, fill_opacity=1.0)
            for _ in range(size)
        ]).arrange(RIGHT, buff=node_gap)
        layers.add(layer)
    layers.arrange(DOWN, buff=layer_gap)

    edges = VGroup()
    for upper_layer, lower_layer in zip(layers[:-1], layers[1:]):
        for upper_node in upper_layer:
            for lower_node in lower_layer:
                edges.add(Line(
                    upper_node.get_center(), lower_node.get_center(),
                    stroke_color=C_EDGE, stroke_width=0.85, stroke_opacity=0.72,
                    buff=radius * 1.18,
                ))

    network = VGroup(edges, layers)
    return network, edges, layers


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

    Giọng đọc tự chọn: có file key cho speech API thì dùng backend chính,
    sau đó mới thử Azure và gTTS. Ép thủ công bằng biến môi trường:
        GLANCE_TTS=timed  (speech API trả MP3 trực tiếp)
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
            key_file = os.environ.get(
                "GLANCE_TIMED_TTS_KEY_FILE", DEFAULT_TIMED_TTS_KEY_FILE
            )
            key_path = pathlib.Path(key_file).expanduser()
            if not key_path.is_absolute():
                key_path = pathlib.Path(__file__).resolve().parent / key_path
            if key_path.is_file():
                backend = "timed"
            elif os.environ.get("AZURE_SUBSCRIPTION_KEY"):
                backend = "azure"
            else:
                backend = "gtts"

        if backend in ("timed", "api"):
            key_file = os.environ.get(
                "GLANCE_TIMED_TTS_KEY_FILE", DEFAULT_TIMED_TTS_KEY_FILE
            )
            return TimedTTSService(
                endpoint=os.environ.get(
                    "GLANCE_TIMED_TTS_URL", DEFAULT_TIMED_TTS_URL
                ),
                token=_read_tts_key(key_file),
                voice=os.environ.get(
                    "GLANCE_TIMED_TTS_VOICE", DEFAULT_TIMED_TTS_VOICE
                ),
                audio_format=os.environ.get("GLANCE_TIMED_TTS_FORMAT", "mp3"),
                timeout=float(os.environ.get("GLANCE_TIMED_TTS_TIMEOUT", "120")),
            )

        if backend == "azure":
            from manim_voiceover.services.azure import AzureService
            voice = os.environ.get("GLANCE_VOICE", self.azure_voice)
            validate_azure_voice(voice)
            self._multilingual = azure_voice_supports_code_switch(voice)
            return AzureService(voice=voice)
        if backend in ("record", "recorder"):
            from manim_voiceover.services.recorder import RecorderService
            return RecorderService()
        from manim_voiceover.services.gtts import GTTSService
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


class GlanceMovingScene(GlanceScene, MovingCameraScene):
    """GlanceScene variant for beats that pan or zoom the camera (self.camera.frame)."""
    pass
