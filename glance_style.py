"""Shared visual language for the GLANCE explainer video.

Every section imports from this module so the six independently-rendered
sections look like one video. Do NOT fork this file inside a section folder --
if you need a new helper, add it here and tell the team in the PR.

Usage inside sections/<yours>/<yours>.py:

    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
    from glance_style import *
"""

from manim import *

import manimpango

# --------------------------------------------------------------------------
# Fonts. Vietnamese diacritics need a font with full Latin Extended coverage.
# We pick the first installed font from the list instead of hard-coding one,
# so the same script renders on macOS, Linux and Windows machines.
# --------------------------------------------------------------------------

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

BG = "#0E1116"
INK = "#E8ECF1"
MUTED = "#8B97A8"

C_GNN = "#3ECFB2"
C_LLM = "#F2B441"
C_ROUTER = "#A98BFF"
C_GOOD = "#5BD97E"
C_BAD = "#FF6B6B"
C_EDGE = "#4A5468"
C_HIGHLIGHT = "#6EA8FE"

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


# --------------------------------------------------------------------------
# Scene base class. Inherit from this so background, banner and the subtitle
# habit are identical across sections.
# --------------------------------------------------------------------------

class GlanceScene(Scene):
    """Base scene: dark background + optional persistent section banner.

    Subclasses set `section` and `section_name`, then call `self.banner()`
    once at the start of construct().
    """

    section = None
    section_name = ""

    def setup(self):
        self.camera.background_color = BG

    def banner(self):
        if self.section is None:
            return None
        b = section_banner(self.section, self.section_name)
        self.add(b)
        return b

    def say(self, text, duration=2.0):
        """Subtitle-only beat (no animation). Keeps the .srt in sync."""
        self.add_subcaption(text, duration=duration)
        self.wait(duration)

    def clear_scene(self, keep=()):
        """Fade out everything except `keep` mobjects."""
        leaving = [m for m in self.mobjects if m not in keep]
        if leaving:
            self.play(*[FadeOut(m) for m in leaving], run_time=0.6)
