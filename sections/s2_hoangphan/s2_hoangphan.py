"""Section 2 — Đánh giá các routing heuristic hiện có.  Owner: Hoàng Phan.

Nguồn trong paper: §4 mở đầu, §4.1 + Bảng 1 (tr.3–4)
Nhiệm vụ chi tiết: sections/s2_hoangphan/TASK.md

Chữ trên hình: tiếng Anh. Phụ đề: tiếng Việt (kịch bản thu tiếng).

Render:  manim -ql sections/s2_hoangphan/s2_hoangphan.py -a
"""

import pathlib
import sys

# Cho phép import glance_style.py ở thư mục gốc repo.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from glance_style import *  # noqa: E402,F403

SECTION = "2"
SECTION_NAME = "Routing heuristic"
OWNER = "Hoàng Phan"
ACCENT = SECTION_COLORS.get(SECTION, C_HIGHLIGHT)

# Layer order for every node-edge illustration in this section.
GRAPH_EDGE_Z = 0
GRAPH_EDGE_FX_Z = 1
GRAPH_NODE_Z = 2
GRAPH_LABEL_Z = 4

SRC_T1 = "Table 1, p.4"

ASSET_DIR = pathlib.Path(__file__).resolve().parent / "assets"
PAPER_ASSETS = [
    ("E-LLaGNN", "arXiv:2407.14996", ASSET_DIR / "ellagnn_page.jpg"),
    ("LLM-GNN", "arXiv:2310.04668", ASSET_DIR / "llm_gnn_page.jpg"),
    ("LOGIN", "arXiv:2405.13902", ASSET_DIR / "login_page.jpg"),
]

# --------------------------------------------------------------------------
# Nhịp thuyết minh
#
# Mỗi nhịp là một khối `self.voiceover()`: audio do backend TTS sinh, nhịp hình
# bám theo `tracker.duration` chứ không ước bằng tay nữa. Khối `with` tự chờ nốt
# phần audio còn thừa khi animation ngắn hơn câu đọc, nên không cần canh run_time.
# Phụ đề .srt cũng do plugin sinh thẳng từ `text`, không add_subcaption thủ công.
#
# Lời thoại viết theo cách ĐỌC LÊN, dùng phiên âm đã chốt trong plan.md:
#   "LLM" -> "lờ lờ mờ"   "GNN" -> "gờ nờ nờ"   "node" -> "nót"
# --------------------------------------------------------------------------


def beat(scene, text, *anims, run_time=1.0, speed=None, steps=None,
         min_step=0.3, tail=0.2):
    """Một nhịp nói: chạy animation trong lúc đọc, rồi giữ hình cho hết câu.

    `speed` đọc riêng câu này nhanh/chậm hơn (audio sinh mới ở tốc độ đó, tốc độ
    nằm trong cache key), dùng cho các chuỗi chữ cái đọc rời rạc.

    `steps` chia nhịp thành nhiều bước nối tiếp và tự giãn cho kín câu nói: mỗi
    phần tử là một list animation, hoặc tuple `(list animation, trọng số)`. Dùng
    khi một câu cần diễn nhiều bước ví dụ — trước đây những câu này chỉ có một
    animation ngắn rồi hình đứng im chờ hết audio. Tổng run_time luôn nhỏ hơn
    `tracker.duration` nên hình không chạy lố sang câu sau.
    """
    plan = []
    for step in steps or ():
        step_anims, weight = step if isinstance(step, tuple) else (step, 1.0)
        step_anims = [a for a in step_anims if a is not None]
        if step_anims:
            plan.append((step_anims, float(weight)))

    with scene.tts_speed(speed):
        with scene.voiceover(text=text) as tracker:
            if plan:
                budget = max(tracker.duration - tail, min_step * len(plan))
                total = sum(w for _, w in plan)
                for step_anims, weight in plan:
                    scene.play(*step_anims,
                               run_time=max(min_step, budget * weight / total))
            elif anims:
                scene.play(*anims, run_time=min(run_time, tracker.duration))


# --------------------------------------------------------------------------
# Bảng 1 (tr.4), cột Enhanced features. Không làm tròn lại.
# Thứ tự cột: Cora 10/15/20 · Pubmed 10/15/20 · Arxiv23 10/15/20
# --------------------------------------------------------------------------

STRATS = ["Random", "C-density", "Degree", "Uncertainty"]
T1 = {
    "GCN": {
        "Random":      [-0.02, -0.06, -0.04, 0.06, 0.05, 0.04, 0.05, 0.04, 0.04],
        "C-density":   [-0.02, -0.03, -0.03, 0.05, 0.06, 0.05, 0.07, 0.07, 0.06],
        "Degree":      [-0.04, -0.01, -0.02, 0.04, 0.04, 0.04, 0.04, 0.05, 0.05],
        "Uncertainty": [-0.09, -0.03, -0.01, 0.20, 0.18, 0.17, 0.15, 0.13, 0.13],
    },
    "GCNII": {
        "Random":      [0.00, 0.01, -0.01, 0.01, 0.01, 0.01, -0.01, 0.00, 0.00],
        "C-density":   [0.00, -0.03, -0.03, 0.02, 0.02, 0.02, 0.03, 0.03, 0.03],
        "Degree":      [-0.03, -0.03, -0.02, 0.03, 0.03, 0.03, -0.03, -0.02, -0.01],
        "Uncertainty": [-0.04, -0.02, -0.03, 0.09, 0.08, 0.08, 0.05, 0.04, 0.05],
    },
}
DATASETS = ["Cora", "Pubmed", "Arxiv23"]
KS = ["10%", "15%", "20%"]


def ncs_color(value, cap=0.22):
    """Thang đỏ → nền → xanh cho heatmap Bảng 1. Chỉ pha từ màu có sẵn."""
    t = max(-1.0, min(1.0, value / cap))
    end = C_GOOD if t >= 0 else C_BAD
    return interpolate_color(ManimColor(BG), ManimColor(end), abs(t) ** 0.75)


# --------------------------------------------------------------------------
# Đồ thị riêng của section 2
#
# demo_tag() được dựng cho câu chuyện homophily ở section 3, nên nó không có
# vùng "dày đặc nhưng heterophilous". Thiếu vùng đó thì phần clustering density
# mất hẳn phản ví dụ. Vì vậy section này dùng tag_graph() với layout riêng, dựng
# sao cho mỗi vùng phá đúng một heuristic:
#
#   S1..S4  chuỗi thưa, toàn class A  -> degree thấp + density 0, nhưng DỄ
#   H       hub 7 hàng xóm, 6 khác class -> degree cao, nhưng KHÓ
#   D1..D6  cụm nhiều tam giác, class trộn -> density cao, nhưng KHÓ
#
# Giữ đúng hai class như demo_tag() (A teal, B amber) để viền tím C_ROUTER của
# node được route không lẫn với màu class nào.
# --------------------------------------------------------------------------

S2_POS = {
    "S1": [-5.7, 1.5, 0], "S2": [-4.8, 0.4, 0], "S3": [-5.3, -0.9, 0], "S4": [-4.2, -2.0, 0],
    "H": [-1.5, 0.3, 0],
    "N1": [-3.0, 1.4, 0], "N2": [-3.1, -0.8, 0], "N3": [-1.8, 2.2, 0], "N4": [-0.2, 1.5, 0],
    "N5": [-0.1, -0.9, 0], "N6": [-2.4, -1.8, 0], "N7": [-0.8, -2.2, 0],
    "D1": [2.2, 1.6, 0], "D2": [3.6, 2.0, 0], "D3": [4.7, 0.8, 0],
    "D4": [3.5, -0.3, 0], "D5": [2.3, 0.2, 0], "D6": [4.3, -1.6, 0],
}
S2_EDGES = [
    ("S1", "S2"), ("S2", "S3"), ("S3", "S4"),
    ("H", "N1"), ("H", "N2"), ("H", "N3"), ("H", "N4"),
    ("H", "N5"), ("H", "N6"), ("H", "N7"),
    # Ghép cặp các lá của hub để bậc 1 chỉ còn nằm ở vùng thưa bên trái.
    ("N1", "N3"), ("N6", "N7"),
    ("D1", "D2"), ("D1", "D3"), ("D1", "D5"), ("D2", "D3"), ("D2", "D5"),
    ("D3", "D4"), ("D3", "D5"), ("D3", "D6"), ("D4", "D5"), ("D4", "D6"),
    ("S3", "N2"), ("N4", "D1"), ("N5", "D5"),
]
S2_LABELS = {
    "S1": "A", "S2": "A", "S3": "A", "S4": "A",
    "H": "A", "N5": "A",
    "N1": "B", "N2": "B", "N3": "B", "N4": "B", "N6": "B", "N7": "B",
    "D1": "B", "D2": "A", "D3": "B", "D4": "A", "D5": "A", "D6": "B",
}

SPARSE = ["S1", "S2", "S3", "S4"]
DENSE = ["D1", "D2", "D3", "D4", "D5", "D6"]
# 5 tam giác trong cụm phải, dùng để tô phần "mật độ cao".
DENSE_TRIS = [("D1", "D2", "D3"), ("D1", "D2", "D5"), ("D2", "D3", "D5"),
              ("D3", "D4", "D5"), ("D3", "D4", "D6")]

DEG = {n: sum(1 for u, v in S2_EDGES if n in (u, v)) for n in S2_POS}
# Chỉ S1 và S4 có bậc 1, và cả hai nằm trong vùng thưa toàn một lớp.
# 2 trên 18 nót ~ 11%, xấp xỉ mức 10% mà paper dùng.
LOW_DEGREE = ["S1", "S4"]
EASY_LOW_DEG = "S1"     # bậc 1, hàng xóm duy nhất cùng lớp -> GNN vốn đã đúng
HARD_HIGH_DEG = "H"     # bậc 7, 6/7 hàng xóm khác lớp -> GNN sai, mà không được route


def s2_graph():
    """Đồ thị minh hoạ của section 2. Node to và cạnh dày hơn mặc định cho dễ đọc."""
    g = tag_graph(S2_EDGES, S2_POS, labels=S2_LABELS, radius=0.21)
    g.edges.set_stroke(width=2.8).set_z_index(GRAPH_EDGE_Z)
    for node in g.nodes.values():
        node.set_z_index(GRAPH_NODE_Z)
    return g


def neighbors_of(n):
    out = []
    for u, v in S2_EDGES:
        if u == n:
            out.append(v)
        elif v == n:
            out.append(u)
    return out


def edge_mobjs(graph, pred):
    """Các cạnh thoả pred(u, v). tag_graph dựng .edges đúng thứ tự S2_EDGES."""
    return VGroup(*[m for (u, v), m in zip(S2_EDGES, graph.edges) if pred(u, v)])


def deg_label(graph, n, color=ACCENT):
    return mono(f"deg {DEG[n]}", size=17, color=color).next_to(
        graph.nodes[n], UP, buff=0.2).set_z_index(GRAPH_LABEL_Z)


def msg_flash(graph, target, sources=None, color=C_HIGHLIGHT, width=5.0,
              time_width=0.55):
    """Xung sáng chạy dọc cạnh, hướng VỀ `target`: hình ảnh truyền thông điệp.

    Trả về list animation, mỗi cạnh kề một xung; `sources` giới hạn danh sách
    hàng xóm. Dùng ShowPassingFlash nên mobject tạm tự dọn, không phải fade out.
    """
    out = []
    for u, v in S2_EDGES:
        if target not in (u, v):
            continue
        other = v if u == target else u
        if sources is not None and other not in sources:
            continue
        path = Line(graph.nodes[other].get_center(), graph.nodes[target].get_center(),
                    stroke_width=width, color=color, z_index=GRAPH_EDGE_FX_Z)
        out.append(ShowPassingFlash(path, time_width=time_width))
    return out


def class_legend(graph):
    """Chú giải màu lớp, đọc thẳng màu từ node nên luôn khớp tag_graph()."""
    rows = VGroup()
    for label, sample in (("A", "S1"), ("B", "N1")):
        swatch = Dot(radius=0.11, color=graph.nodes[sample].get_color())
        rows.add(VGroup(swatch, mono(f"class {label}", size=16, color=MUTED))
                 .arrange(RIGHT, buff=0.18))
    return rows.arrange(DOWN, buff=0.18, aligned_edge=LEFT)


# ===========================================================================
class S2_01_AdaptiveFusion(GlanceScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        # Không dùng title card: scene nối trực tiếp từ câu hỏi ở cuối section 1.
        static_head = heading("Static fusion", color=C_BAD).to_edge(UP, buff=0.75)
        nodes = VGroup(*[
            Dot(radius=0.18, color=C_GNN).set_z_index(GRAPH_NODE_Z)
            for _ in range(5)
        ]).arrange(DOWN, buff=0.48).move_to(LEFT * 3.4 + DOWN * 0.2)
        node_label = mono("all nodes", size=17, color=MUTED).next_to(nodes, LEFT, buff=0.35)
        llm = labeled_box("LLM", C_LLM).move_to(
            RIGHT * 3.1 + DOWN * 0.2
        ).set_z_index(GRAPH_NODE_Z)
        # Năm mũi tên cùng chụm vào một cạnh của khối lờ lờ mờ, nên đầu mũi tên
        # mặc định phình to thành một bó nhọn. Ép tip_length nhỏ hẳn và cắm vào
        # năm cao độ rời nhau trên cạnh trái để đọc ra từng đường một.
        llm_left = llm.get_left()
        arrow_targets = [llm_left + UP * offset for offset in (0.32, 0.16, 0.0, -0.16, -0.32)]
        all_arrows = VGroup(*[
            Arrow(
                node.get_right(), target, buff=0.2,
                color=C_EDGE, stroke_width=2.0,
                tip_length=0.10,
                max_tip_length_to_length_ratio=0.04,
            ).set_z_index(GRAPH_EDGE_FX_Z)
            for node, target in zip(nodes, arrow_targets)
        ])
        static_note = txt("Every node queries the LLM", size=21, color=C_BAD)
        static_note.to_edge(DOWN, buff=0.55)

        beat(
            self,
            "Thay vì định tuyến mọi nót sang lờ lờ mờ như cách kết hợp tĩnh, tại sao không chỉ chọn những nót thật sự có lợi khi gọi lờ lờ mờ?",
            FadeIn(static_head), FadeIn(nodes), FadeIn(node_label), FadeIn(llm),
            LaggedStart(*[GrowArrow(a) for a in all_arrows], lag_ratio=0.08),
            FadeIn(static_note),
            run_time=1.8,
        )

        adaptive_head = heading("Adaptive fusion", color=C_ROUTER).move_to(static_head)
        selected = (1, 3)
        rings = VGroup(*[
            Circle(radius=0.28, color=C_ROUTER, stroke_width=3).move_to(nodes[i])
            for i in selected
        ])
        routed_arrows = VGroup(*[
            Arrow(
                nodes[i].get_right(), llm_left + UP * offset, buff=0.2,
                color=C_ROUTER, stroke_width=2.6,
                tip_length=0.11,
                max_tip_length_to_length_ratio=0.05,
            ).set_z_index(GRAPH_EDGE_FX_Z)
            for i, offset in zip(selected, (0.18, -0.18))
        ])
        adaptive_note = txt(
            "Route only nodes with expected LLM benefit",
            size=21, color=C_ROUTER, weight=BOLD,
        ).to_edge(DOWN, buff=0.55)

        beat(
            self,
            "Hướng tiếp cận này được gọi là kết hợp thích ứng (adaptive routing).",
            Transform(static_head, adaptive_head), FadeOut(all_arrows),
            FadeOut(static_note), FadeOut(node_label),
            LaggedStart(*[nodes[i].animate.set_opacity(0.28)
                          for i in range(len(nodes)) if i not in selected], lag_ratio=0.08),
            LaggedStart(*[Create(r) for r in rings], lag_ratio=0.15),
            LaggedStart(*[GrowArrow(a) for a in routed_arrows], lag_ratio=0.15),
            FadeIn(adaptive_note),
            run_time=1.4,
        )

        self.clear_scene()

        def paper_card(name, arxiv_id, image_path):
            page = ImageMobject(str(image_path)).set_height(4.45)
            frame = SurroundingRectangle(
                page, color=C_EDGE, stroke_width=2, buff=0.05,
            )
            label = VGroup(
                txt(name, size=22, color=ACCENT, weight=BOLD),
                mono(arxiv_id, size=14, color=MUTED),
            ).arrange(DOWN, buff=0.08).next_to(page, UP, buff=0.18)
            return Group(page, frame, label)

        papers = Group(*[
            paper_card(name, arxiv_id, image_path)
            for name, arxiv_id, image_path in PAPER_ASSETS
        ]).arrange(RIGHT, buff=0.42, aligned_edge=DOWN).shift(DOWN * 0.42)
        paper_head = heading(
            "Three prior adaptive-fusion methods", color=ACCENT,
        ).to_edge(UP, buff=0.45)

        # Ba tên công trình tách thành ba clip riêng, mỗi clip ngắn và đọc nhanh:
        # gộp cả ba chuỗi chữ cái vào một câu thì giọng đọc méo hẳn. Đổi lại mỗi
        # tấm ảnh cũng lên đúng lúc tên nó được đọc.
        beat(self, "Ta hãy cùng khảo sát ba công trình từng áp dụng cách tiếp cận này.",
             FadeIn(paper_head), run_time=0.8)
        beat(self, "Thứ nhất, e lờ lờ a gờ nờ nờ.",
             FadeIn(papers[0], shift=UP * 0.2), run_time=0.7, speed=1.3)
        beat(self, "Thứ hai, lờ lờ mờ, gờ nờ nờ.",
             FadeIn(papers[1], shift=UP * 0.2), run_time=0.7, speed=1.3)
        beat(self, "Và thứ ba, lốc gin.",
             FadeIn(papers[2], shift=UP * 0.2), run_time=0.7, speed=1.3)
        beat(self, "Chúng dùng tiêu chí nào để đánh giá và định tuyến nót sang lờ lờ mờ?")
        beat(self, "Từng tiêu chí mạnh yếu ra sao?")
        # Câu hỏi thứ ba hướng về GLANCE, vì section này chỉ ra hạn chế của từng
        # công trình chứ không đi sâu vào cơ chế riêng của chúng. Trả lời ở S2_12.
        beat(self, "Và gờ lans đã kế thừa được gì từ cả ba?")


# ===========================================================================
class S2_02_TwoQuestions(GlanceScene):
    """Thước đo để chấm ba tiêu chí sắp xem.

    Không có scene này thì khán giả nghe ba lời phủ định liên tiếp mà chưa biết
    thứ *nên* đo là gì, và khái niệm lợi thế của LLM mãi tới S2_12 mới xuất hiện.
    """

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()

        def qcard(tag, text, color):
            t = txt(tag, size=SMALL_SIZE, color=color, weight=BOLD)
            b = txt(text, size=BODY_SIZE, color=INK, line_spacing=0.85)
            inner = VGroup(t, b).arrange(DOWN, buff=0.28, aligned_edge=LEFT)
            return VGroup(panel(inner, color=color, buff=0.4), inner)

        q1 = qcard("QUESTION 1", "Which nodes look HARD\nfor the GNN?", C_GNN)
        q2 = qcard("QUESTION 2", "Which nodes ACTUALLY\nimprove with an LLM?", C_LLM)
        VGroup(q1, q2).arrange(RIGHT, buff=0.8, aligned_edge=UP).shift(UP * 0.55)

        beat(self, "Trước khi chấm ba tiêu chí đó, ta cần một thước đo.")
        beat(self, "Có hai câu hỏi rất dễ tưởng là một.",
             FadeIn(q1, shift=RIGHT * 0.3), run_time=0.9)
        beat(self, "Câu thứ nhất: nót nào trông có vẻ khó với gờ nờ nờ?")
        beat(self, "Câu thứ hai: nót nào thật sự khá lên khi gọi lờ lờ mờ?",
             FadeIn(q2, shift=LEFT * 0.3), run_time=0.9)

        # --- hai tập không trùng nhau -------------------------------------------
        c1 = Circle(radius=1.5, stroke_color=C_GNN, stroke_width=3.2).set_fill(C_GNN, 0.12)
        c2 = Circle(radius=1.5, stroke_color=C_LLM, stroke_width=3.2).set_fill(C_LLM, 0.12)
        c1.move_to(LEFT * 0.88 + DOWN * 0.75)
        c2.move_to(RIGHT * 0.88 + DOWN * 0.75)
        lens = Intersection(c1, c2, fill_color=C_ROUTER, fill_opacity=0.55, stroke_width=0)
        n1 = txt("GNN difficulty", size=SMALL_SIZE, color=C_GNN).next_to(c1, LEFT, buff=0.2)
        n2 = txt("LLM advantage", size=SMALL_SIZE, color=C_LLM).next_to(c2, RIGHT, buff=0.2)
        core = txt("only the overlap is worth paying for", size=SMALL_SIZE,
                   color=C_ROUTER, weight=BOLD).next_to(VGroup(c1, c2), DOWN, buff=0.4)

        self.play(FadeOut(q1, shift=UP * 0.3), FadeOut(q2, shift=UP * 0.3), run_time=0.6)
        beat(self, "Nghe thì giống nhau, nhưng hai tập nót này không trùng nhau.",
             Create(c1), Create(c2), FadeIn(n1), FadeIn(n2), run_time=1.2)
        beat(self, "Chỉ phần giao mới đáng để ta trả tiền cho một lời gọi.",
             FadeIn(lens), Write(core), run_time=1.0)
        beat(self, "Ba tiêu chí sắp xem đều chỉ nhìn được vòng tròn bên trái.",
             c1.animate.set_fill(C_GNN, 0.42), run_time=1.0)
        beat(self, "Hãy nhớ hình này, ta sẽ quay lại nó ở cuối phần.")

        self.clear_scene()


# ===========================================================================
class S2_03_Degree(GlanceScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        head = heading("Heuristic 1: Node degree", color=ACCENT).to_edge(UP, buff=0.85)
        sub = mono("E-LLaGNN  ·  route the lowest-degree nodes", size=18,
                   color=MUTED).next_to(head, DOWN, buff=0.18)
        g = s2_graph().scale(0.9).move_to(DOWN * 0.4)
        ring_r = g.nodes["H"].radius * 1.9

        # Hai nót mẫu cho phần định nghĩa: D3 bậc 5 trong cụm dày, S1 bậc 1 ở
        # chuỗi thưa. Cặp này diễn luôn cả định nghĩa lẫn hệ quả "bậc thấp nhận
        # ít thông điệp", nên không cần chạm tới hub — hub để dành cho phản ví dụ.
        deg_hi, deg_lo = "D3", "S1"
        tag_hi = deg_label(g, deg_hi, MUTED)
        tag_lo = deg_label(g, deg_lo, ACCENT)
        legend = class_legend(g).to_corner(UL, buff=0.55).shift(DOWN * 0.8)

        beat(self, "Đầu tiên là e lờ lờ a gờ nờ nờ.",
             FadeIn(head), FadeIn(sub), run_time=0.8, speed=1.3)
        # Đồ thị lên ngay từ câu thứ hai, đúng lúc bắt đầu nói về nót bậc — bản
        # cũ để khán giả nghe ba câu liền trên nền trống rồi mới vẽ.
        beat(self, "Công trình này dùng nót bậc làm tiêu chí định tuyến.", steps=[
            ([Create(g.edges)], 1.0),
            ([LaggedStart(*[GrowFromCenter(d) for d in g.nodes.values()],
                          lag_ratio=0.06)], 1.2),
        ])
        # Đếm bậc ngay trên hình: xung sáng chạy về nót rồi mới hiện nhãn "deg".
        beat(self, "bậc là số hàng xóm nối với nót đó.", steps=[
            (msg_flash(g, deg_hi, color=MUTED) + [FadeIn(tag_hi)], 1.3),
            (msg_flash(g, deg_lo, color=ACCENT) + [FadeIn(tag_lo)], 1.0),
        ])
        beat(self, "nót bậc thấp nhận ít thông tin qua truyền thông điệp.", steps=[
            (msg_flash(g, deg_hi, color=MUTED, time_width=0.35), 1.0),
            (msg_flash(g, deg_lo, color=ACCENT, time_width=0.35)
             + [Indicate(g.nodes[deg_lo], color=ACCENT, scale_factor=1.35)], 1.0),
        ])
        beat(self, "Nên gờ nờ nờ có thể gặp khó, và ta ưu tiên định tuyến chúng sang lờ lờ mờ.",
             steps=[
                 ([LaggedStart(*[Indicate(d, color=ACCENT, scale_factor=1.2)
                                 for d in g.nodes.values()], lag_ratio=0.05)], 1.4),
                 ([FadeOut(tag_hi), FadeOut(tag_lo)]
                  + [Indicate(g.nodes[n], color=C_ROUTER, scale_factor=1.4)
                     for n in LOW_DEGREE], 1.0),
             ])
        # Chú giải màu lớp hiện theo từng lớp, kèm nháy đúng nhóm nót của lớp đó.
        beat(self, "Màu nót là lớp thật của nó.", steps=[
            [FadeIn(legend[0])] + [Indicate(d, color=d.get_color(), scale_factor=1.25)
                                   for n, d in g.nodes.items() if S2_LABELS[n] == "A"],
            [FadeIn(legend[1])] + [Indicate(d, color=d.get_color(), scale_factor=1.25)
                                   for n, d in g.nodes.items() if S2_LABELS[n] == "B"],
        ])

        # --- tập được route -----------------------------------------------------
        rings = VGroup(*[
            Circle(radius=ring_r, color=C_ROUTER, stroke_width=3).move_to(g.nodes[n])
            for n in LOW_DEGREE
        ])
        tags = VGroup(*[deg_label(g, n, C_ROUTER) for n in LOW_DEGREE])
        chip = VGroup(panel(txt("Routed to the LLM", size=19, color=C_ROUTER), buff=0.26),
                      txt("Routed to the LLM", size=19, color=C_ROUTER))
        chip.to_corner(UR, buff=0.6)

        beat(self, "Đây là hai nót bậc thấp nhất, chúng sẽ được định tuyến.", steps=[
            ([LaggedStart(*[Create(r) for r in rings], lag_ratio=0.15),
              LaggedStart(*[FadeIn(t) for t in tags], lag_ratio=0.15)], 1.3),
            ([FadeIn(chip, shift=LEFT * 0.25)], 1.0),
        ])

        # --- phản ví dụ 1: bậc thấp nhất nhưng dễ --------------------------------
        # Giữ sáng cả vùng thưa để thấy rõ nó chỉ có một lớp duy nhất.
        keep = set(SPARSE)
        dim_nodes = VGroup(*[d for i, d in g.nodes.items() if i not in keep])
        dim_edges = edge_mobjs(g, lambda u, v: not ({u, v} <= keep))
        sparse_nodes = VGroup(*[g.nodes[n] for n in SPARSE])
        sparse_edges = edge_mobjs(g, lambda u, v: {u, v} <= keep)
        focus = DashedVMobject(
            SurroundingRectangle(sparse_nodes, color=ACCENT, stroke_width=2.2, buff=0.34),
            num_dashes=48)
        ok = check(size=0.5).next_to(
            g.nodes[EASY_LOW_DEG], RIGHT, buff=0.45
        ).set_z_index(GRAPH_LABEL_Z)
        msg1 = txt("The whole region is one class. The GNN was already right.",
                   size=21, color=C_GOOD).to_edge(DOWN, buff=0.45)
        waste_inner = txt("Wasted LLM call", size=18, color=C_BAD)
        waste = VGroup(panel(waste_inner, color=C_BAD, buff=0.22, fill_opacity=0.12),
                       waste_inner).to_corner(DL, buff=0.55)

        beat(self, "Nhưng hãy nhìn kỹ vùng bên trái này.", steps=[
            [dim_nodes.animate.set_opacity(0.15), dim_edges.animate.set_opacity(0.15)],
            [Create(focus)],
        ])
        beat(self, "Hàng xóm duy nhất của nó cùng lớp, và cả vùng cũng chỉ có một lớp.",
             steps=[
                 (msg_flash(g, EASY_LOW_DEG, color=C_GOOD, time_width=0.7)
                  + [Create(ok)], 1.0),
                 ([LaggedStart(*[Indicate(d, color=C_GOOD, scale_factor=1.3)
                                 for d in sparse_nodes], lag_ratio=0.12),
                   FadeIn(msg1)], 1.3),
             ])
        # Tín hiệu đồng thuận: xung xanh chạy dọc chuỗi thưa, không còn đứng im.
        beat(self, "truyền thông điệp chỉ đưa vào tín hiệu đồng thuận.", steps=[
            [LaggedStart(*[ShowPassingFlash(
                e.copy().set_stroke(C_GOOD, width=5), time_width=0.6)
                for e in sparse_edges], lag_ratio=0.2)],
            [Indicate(sparse_edges, color=C_GOOD, scale_factor=1.0)],
        ])
        beat(self, "gờ nờ nờ vốn đã đúng ở đây. Gọi lờ lờ mờ chỉ là lãng phí tiền.", steps=[
            ([Indicate(rings[LOW_DEGREE.index(EASY_LOW_DEG)],
                       color=C_ROUTER, scale_factor=1.25)], 1.0),
            ([FadeIn(waste, shift=UP * 0.2)], 1.0),
            ([Indicate(waste, color=C_BAD, scale_factor=1.05)], 1.0),
        ])

        self.play(dim_nodes.animate.set_opacity(1), dim_edges.animate.set_opacity(1),
                  FadeOut(ok), FadeOut(msg1), FadeOut(focus), FadeOut(waste),
                  run_time=0.7)

        # --- phản ví dụ 2: bậc cao nhất nhưng khó --------------------------------
        hub_nb = neighbors_of(HARD_HIGH_DEG)
        keep2 = {HARD_HIGH_DEG, *hub_nb}
        dim2_nodes = VGroup(*[d for i, d in g.nodes.items() if i not in keep2])
        dim2_edges = edge_mobjs(g, lambda u, v: not ({u, v} <= keep2))
        # Tách 6 cạnh khác lớp khỏi 1 cạnh cùng lớp: đúng con số trong lời thoại,
        # và tô lần lượt thì khán giả đếm được thay vì thấy cả chùm đỏ cùng lúc.
        hub_conflict = edge_mobjs(
            g, lambda u, v: HARD_HIGH_DEG in (u, v) and S2_LABELS[u] != S2_LABELS[v])
        hub_same = edge_mobjs(
            g, lambda u, v: HARD_HIGH_DEG in (u, v) and S2_LABELS[u] == S2_LABELS[v])
        conflict_nb = [n for n in hub_nb if S2_LABELS[n] != S2_LABELS[HARD_HIGH_DEG]]
        same_nb = [n for n in hub_nb if S2_LABELS[n] == S2_LABELS[HARD_HIGH_DEG]]
        # Nhãn phải nằm dưới hẳn dòng `sub` và không thò sang trái quá mép phải của
        # nó: đặt buff nhỏ hoặc để chữ dài là dính ngay vào phụ đề tiêu đề.
        skip_lbl = mono("highest degree → never routed", size=16, color=MUTED)
        skip_lbl.scale_to_fit_width(3.4).next_to(chip, DOWN, buff=0.62).align_to(chip, RIGHT)
        want_ring = Circle(radius=ring_r * 1.25, color=C_ROUTER,
                           stroke_width=3).move_to(g.nodes[HARD_HIGH_DEG])
        msg3 = txt("The node that actually needs the LLM is never routed.",
                   size=21, color=C_ROUTER).to_edge(DOWN, buff=0.45)
        hub_tag = VGroup(
            panel(mono("degree = 7", size=17, color=C_BAD), buff=0.18, fill_opacity=0.95),
            mono("degree = 7", size=17, color=C_BAD),
        ).next_to(g.nodes[HARD_HIGH_DEG], DOWN, buff=0.42).set_z_index(GRAPH_LABEL_Z)
        bad = cross(size=0.42).next_to(
            g.nodes[HARD_HIGH_DEG], RIGHT, buff=0.5
        ).set_z_index(GRAPH_LABEL_Z)
        msg2 = txt("Degree 7, but 6 of 7 neighbors are a different class.",
                   size=21, color=C_BAD).to_edge(DOWN, buff=0.45)

        beat(self, "Bây giờ ngược lại, hãy nhìn nót giữa hình.", steps=[
            [dim2_nodes.animate.set_opacity(0.15), dim2_edges.animate.set_opacity(0.15),
             rings.animate.set_opacity(0.15), tags.animate.set_opacity(0.15)],
            [FadeIn(hub_tag), Indicate(g.nodes[HARD_HIGH_DEG], color=ACCENT,
                                       scale_factor=1.4)],
        ])
        # Bậc cao nhất: xung sáng chạy về hub trên cả 7 cạnh, rồi mới nói nó bị bỏ qua.
        beat(self, "bậc của nó cao nhất đồ thị, nên tiêu chí bỏ qua.", steps=[
            (msg_flash(g, HARD_HIGH_DEG, color=ACCENT, time_width=0.45), 1.3),
            ([FadeIn(skip_lbl), Indicate(chip, color=MUTED, scale_factor=1.04)], 1.0),
        ])
        beat(self, "Nhưng sáu trong bảy hàng xóm lại khác lớp với nó.", steps=[
            ([LaggedStart(*[e.animate.set_stroke(color=C_BAD, width=3.2)
                            for e in hub_conflict], lag_ratio=0.18)], 1.4),
            ([hub_same.animate.set_stroke(color=C_GOOD, width=3.2),
              FadeIn(msg2)], 1.0),
        ])
        # Thông điệp mâu thuẫn thật sự chạy vào hub trước khi dấu X hiện ra.
        beat(self, "truyền thông điệp trộn tín hiệu mâu thuẫn, gờ nờ nờ dự đoán sai.",
             steps=[
                 (msg_flash(g, HARD_HIGH_DEG, sources=conflict_nb, color=C_BAD,
                            time_width=0.45)
                  + msg_flash(g, HARD_HIGH_DEG, sources=same_nb, color=C_GOOD,
                              time_width=0.45), 1.4),
                 ([Indicate(g.nodes[HARD_HIGH_DEG], color=C_BAD, scale_factor=1.5),
                   Create(bad)], 1.0),
             ])
        # Vòng tím hiện lên rồi tan: nót đáng được định tuyến mà tiêu chí không chọn.
        beat(self, "Đây mới đúng là nót cần lờ lờ mờ, nhưng nó không được chọn.", steps=[
            ([Create(want_ring), ReplacementTransform(msg2, msg3)], 1.2),
            ([FadeOut(want_ring, scale=0.7), Indicate(skip_lbl, color=C_BAD,
                                                      scale_factor=1.06)], 1.0),
        ])

        # --- chốt --------------------------------------------------------------
        self.clear_scene()
        punch = VGroup(
            txt("Degree measures the AMOUNT of structural information,", size=24, color=INK),
            txt("not the QUALITY of that information.", size=24, color=ACCENT, weight=BOLD),
        ).arrange(DOWN, buff=0.26)
        tail = txt("Low degree ≠ node text clear enough for the LLM",
                   size=20, color=MUTED).next_to(punch, DOWN, buff=0.6)
        beat(self, "bậc chỉ đo số lượng thông tin cấu trúc.",
             Write(punch[0]), run_time=1.6)
        beat(self, "Nó không đo chất lượng của thông tin đó.",
             Write(punch[1]), run_time=1.3)
        beat(self, "bậc thấp cũng không đảm bảo văn bản của nót đủ rõ cho lờ lờ mờ.", steps=[
            ([FadeIn(tail, shift=UP * 0.2)], 1.0),
            ([Indicate(tail, color=ACCENT, scale_factor=1.04)], 1.0),
        ])


# ===========================================================================
class S2_04_Density(GlanceScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        head = heading("Heuristic 2: C-density in feature space", color=ACCENT)
        head.to_edge(UP, buff=0.85)
        sub = mono("Derived from LLM-GNN  ·  GLANCE routes the bottom-k%", size=17,
                   color=MUTED).next_to(head, DOWN, buff=0.16)

        # Schematic 2D projection of feature vectors. All points share one neutral
        # colour: the clusters come from K-means, not from ground-truth labels.
        coords = [
            [-4.8, 0.25, 0], [-4.35, -0.55, 0], [-3.95, 0.55, 0],
            [-3.55, -0.35, 0], [-3.15, 0.15, 0],
            [-1.05, 1.15, 0], [-0.62, 0.45, 0], [-0.12, 1.25, 0],
            [0.30, 0.38, 0], [0.72, 0.95, 0],
            [1.70, -0.20, 0], [2.05, -1.02, 0], [2.62, -0.48, 0],
            [3.05, -1.18, 0], [3.42, -0.28, 0], [4.72, 0.78, 0],
        ]
        points = VGroup(*[
            Dot(p, radius=0.105, color=MUTED).set_z_index(GRAPH_NODE_Z)
            for p in coords
        ])
        graph_edges = VGroup(*[
            Line(points[i].get_center(), points[j].get_center(),
                 color=C_EDGE, stroke_width=2, stroke_opacity=0.7)
            for i, j in [
                (0, 1), (0, 2), (1, 3), (2, 4), (3, 4),
                (5, 6), (5, 7), (6, 8), (7, 9), (8, 9),
                (10, 11), (10, 12), (11, 13), (12, 14), (13, 14), (14, 15),
            ]
        ]).set_z_index(GRAPH_EDGE_Z)
        axes = VGroup(
            Line(LEFT * 5.35 + DOWN * 1.62, RIGHT * 5.35 + DOWN * 1.62,
                 color=C_EDGE, stroke_width=1.4, stroke_opacity=0.45),
            Line(LEFT * 5.35 + DOWN * 1.62, LEFT * 5.35 + UP * 1.65,
                 color=C_EDGE, stroke_width=1.4, stroke_opacity=0.45),
        ).set_z_index(GRAPH_EDGE_Z)

        topology_icon = VGroup(
            Triangle(color=MUTED, stroke_width=2).scale(0.32),
            mono("Topology density", size=14, color=MUTED),
        ).arrange(DOWN, buff=0.12).move_to(RIGHT * 4.55 + UP * 1.35)
        topology_cross = cross(size=0.52).move_to(topology_icon[0])
        topology_group = VGroup(topology_icon, topology_cross)

        centroid_pos = [LEFT * 3.95, LEFT * 0.20 + UP * 0.82, RIGHT * 2.55 + DOWN * 0.62]
        cluster_bounds = VGroup(
            Ellipse(width=2.35, height=1.65, color=MUTED, stroke_width=1.5,
                    stroke_opacity=0.28).move_to(centroid_pos[0]),
            Ellipse(width=2.45, height=1.65, color=MUTED, stroke_width=1.5,
                    stroke_opacity=0.28).move_to(centroid_pos[1]),
            Ellipse(width=2.45, height=1.85, color=MUTED, stroke_width=1.5,
                    stroke_opacity=0.28).move_to(centroid_pos[2]),
        )
        centroids = VGroup(*[
            VGroup(
                Circle(radius=0.20, color=C_ROUTER, stroke_width=2.5),
                Dot(radius=0.075, color=C_ROUTER),
            ).move_to(p).set_z_index(GRAPH_NODE_Z)
            for p in centroid_pos
        ])
        centroid_labels = VGroup(*[
            MathTex(rf"CC_{{{i}}}", font_size=24, color=C_ROUTER).next_to(
                c, direction, buff=0.14).set_z_index(GRAPH_LABEL_Z)
            for i, (c, direction) in enumerate(
                zip(centroids, [LEFT, RIGHT, LEFT]), start=1)
        ])
        k_note = mono("K = number of classes", size=17, color=C_ROUTER)
        k_note.to_edge(RIGHT, buff=0.5).shift(DOWN * 1.75)
        # Câu kết bằng hai chuỗi chữ cái liền nhau ("lờ lờ mờ, gờ nờ nờ") nên bị
        # đọc méo; sinh lại nhanh hơn cho giọng ổn định.
        beat(self, "Tiêu chí thứ hai là mật độ xê, được kế thừa từ lờ lờ mờ, gờ nờ nờ.",
             FadeIn(head), FadeIn(sub), Create(graph_edges),
             LaggedStart(*[GrowFromCenter(p) for p in points], lag_ratio=0.04),
             run_time=1.6, speed=1.15)
        beat(self, "Mật độ xê ở đây không phải mật độ cạnh hay số tam giác xung quanh nót.",
             FadeOut(graph_edges), Create(axes),
             FadeIn(topology_group), run_time=1.3)
        beat(self, "Trước hết, ca min phân cụm các véc-tơ đặc trưng, với số cụm bằng số lớp.",
             FadeOut(topology_group), FadeIn(cluster_bounds),
             LaggedStart(*[GrowFromCenter(c) for c in centroids], lag_ratio=0.2),
             FadeIn(centroid_labels), FadeIn(k_note), run_time=1.5)

        near_node = points[5]
        near_centroid = centroids[1]
        near_ring = Circle(radius=0.19, color=C_ROUTER, stroke_width=3).move_to(near_node)
        near_line = DashedLine(near_node.get_center(), near_centroid.get_center(),
                               color=C_ROUTER, stroke_width=2.5, dash_length=0.12,
                               z_index=GRAPH_EDGE_FX_Z)
        # Hai công thức xuống thấp thêm một chút để rời hẳn khỏi dải điểm dữ liệu.
        distance = MathTex(r"d_i=\lVert x_i-x_{CC_i}\rVert", font_size=30,
                           color=INK).move_to(LEFT * 0.25 + DOWN * 2.35)
        beat(self, "Với mỗi nót, ta đo khoảng cách từ véc-tơ của nó đến tâm cụm gần nhất.",
             Create(near_ring), Create(near_line), Write(distance), run_time=1.3)

        far_node = points[15]
        far_centroid = centroids[2]
        far_ring = Circle(radius=0.20, color=C_LLM, stroke_width=3.2).move_to(far_node)
        far_line = DashedLine(far_node.get_center(), far_centroid.get_center(),
                              color=C_ROUTER, stroke_width=2.5, dash_length=0.12,
                              z_index=GRAPH_EDGE_FX_Z)
        near_note = VGroup(
            mono("Near centroid", size=16, color=MUTED),
            mono("high C-density", size=17, color=C_ROUTER),
        ).arrange(DOWN, buff=0.08).next_to(near_node, LEFT, buff=0.3)
        far_note = VGroup(
            mono("Far from centroid", size=16, color=MUTED),
            mono("low C-density", size=17, color=C_LLM),
        ).arrange(DOWN, buff=0.08).next_to(far_node, UP, buff=0.22)
        comparison = VGroup(near_note, far_note)
        density_formula = MathTex(
            r"\operatorname{C\!\text{-}\!Density}(v_i)="
            r"\frac{1}{1+\lVert x_{v_i}-x_{CC_{v_i}}\rVert}",
            font_size=30, color=INK,
        ).move_to(DOWN * 2.55)
        density_box = panel(density_formula, color=C_ROUTER, buff=0.18, fill_opacity=0.1)
        formula_group = VGroup(density_box, density_formula)
        with self.voiceover(text=(
            "Trước tiên, nót gần tâm cụm có khoảng cách nhỏ, nên mật độ xê cao. "
            "Ngược lại, nót ở xa tâm cụm có khoảng cách lớn, nên mật độ xê thấp."
        )) as tracker:
            step_time = min(1.1, tracker.duration * 0.2)
            self.play(FadeOut(distance), FadeIn(near_note), FadeIn(formula_group),
                      run_time=step_time)
            # Giữ trạng thái near trong khi câu đầu tiếp tục được đọc. Audio vẫn
            # chạy liên tục; đây chỉ là khoảng giữ hình, không chèn silence.
            self.wait(max(0, tracker.duration * 0.5 - step_time))
            self.play(Create(far_ring), Create(far_line), FadeIn(far_note),
                      run_time=step_time)

        feature_phase = VGroup(
            axes, points, cluster_bounds, centroids, centroid_labels, k_note,
            near_ring, near_line, far_ring, far_line, comparison, formula_group,
        )
        routed_node = VGroup(
            VGroup(
                Circle(radius=0.25, color=C_LLM, stroke_width=3),
                Dot(radius=0.10, color=MUTED),
            ),
            mono("Low C-density", size=17, color=C_LLM),
        ).arrange(DOWN, buff=0.18)
        router = labeled_box("Router", C_ROUTER, width=2.0, height=0.9)
        llm = labeled_box("LLM", C_LLM, width=2.0, height=0.9)
        route_items = VGroup(routed_node, router, llm).arrange(RIGHT, buff=1.15)
        route_items.set_z_index(GRAPH_NODE_Z)
        route_arrows = VGroup(*[
            Arrow(route_items[i].get_right(), route_items[i + 1].get_left(),
                  buff=0.12, color=C_LLM, stroke_width=4,
                  z_index=GRAPH_EDGE_FX_Z)
            for i in range(2)
        ])
        route_note = mono("GLANCE: bottom-k% by C-density", size=19,
                          color=C_LLM).next_to(route_items, DOWN, buff=0.5)
        route_phase = VGroup(route_items, route_arrows, route_note).move_to(DOWN * 0.35)
        beat(self, "Trong thí nghiệm của gờ lans, các nót có mật độ xê thấp nhất được định tuyến sang lờ lờ mờ.",
             FadeOut(feature_phase), FadeIn(route_items),
             LaggedStart(*[GrowArrow(a) for a in route_arrows], lag_ratio=0.25),
             FadeIn(route_note), run_time=1.4, speed=1.15)

        outcome_title = heading("Same C-density, different outcomes", color=ACCENT)
        outcome_title.to_edge(UP, buff=1.0)

        def outcome_card(left_text, left_color, right_text, right_color, border_color):
            centroid = VGroup(
                Circle(radius=0.17, color=C_ROUTER, stroke_width=2.2),
                Dot(radius=0.06, color=C_ROUTER),
            ).set_z_index(GRAPH_NODE_Z)
            candidate = Dot(radius=0.10, color=MUTED).shift(
                RIGHT * 1.15
            ).set_z_index(GRAPH_NODE_Z)
            measure = DashedLine(centroid.get_center(), candidate.get_center(),
                                 color=C_ROUTER, stroke_width=2.2, dash_length=0.1,
                                 z_index=GRAPH_EDGE_FX_Z)
            measured = VGroup(centroid, candidate, measure)
            same_d = MathTex(r"d_i=d_j", font_size=25, color=MUTED).next_to(
                measured, UP, buff=0.15
            ).set_z_index(GRAPH_LABEL_Z)
            result = VGroup(
                txt(left_text, size=20, color=left_color, weight=BOLD),
                mono("→", size=24, color=MUTED),
                txt(right_text, size=20, color=right_color, weight=BOLD),
            ).arrange(RIGHT, buff=0.18)
            content = VGroup(VGroup(measured, same_d), result).arrange(DOWN, buff=0.45)
            frame = panel(content, color=border_color, buff=0.35, fill_opacity=0.08)
            return VGroup(frame, content)

        helped = outcome_card("GNN wrong", C_BAD, "LLM correct", C_GOOD, C_GOOD)
        harmed = outcome_card("GNN correct", C_GOOD, "LLM wrong", C_BAD, C_BAD)
        outcomes = VGroup(helped, harmed).arrange(RIGHT, buff=0.65).move_to(DOWN * 0.25)
        outcome_phase = VGroup(outcome_title, outcomes)
        intro_phase = VGroup(head, sub, route_phase)
        beat(self, "Tuy nhiên, khoảng cách đến tâm cụm không trực tiếp cho biết gờ nờ nờ đang sai, cũng không cho biết lờ lờ mờ có thể sửa dự đoán đó hay không.",
             FadeOut(intro_phase), FadeIn(outcome_title),
             LaggedStart(FadeIn(helped), FadeIn(harmed), lag_ratio=0.25), run_time=1.8)

        punch = VGroup(
            txt("Feature-space typicality", size=31, color=INK, weight=BOLD),
            mono("≠", size=38, color=C_BAD),
            txt("LLM benefit", size=31, color=C_LLM, weight=BOLD),
        ).arrange(RIGHT, buff=0.38)
        punch_sub = mono("C-density remains an indirect proxy", size=19,
                         color=MUTED).next_to(punch, DOWN, buff=0.42)
        punch_group = VGroup(punch, punch_sub)
        beat(self, "Vì vậy, mật độ xê vẫn chỉ là một tín hiệu thay thế gián tiếp cho lợi ích của việc định tuyến.",
             FadeOut(outcome_phase), FadeIn(punch_group, shift=UP * 0.18), run_time=1.4)


# ===========================================================================
class S2_05_Uncertainty(GlanceScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        bnr = self.banner()
        head = heading("Heuristic 3: GNN uncertainty", color=ACCENT).to_edge(UP, buff=0.85)
        sub = mono("LOGIN  ·  route the highest-uncertainty nodes", size=18,
                   color=MUTED).next_to(head, DOWN, buff=0.18)

        base = RIGHT * 2.9 + DOWN * 1.5
        bar_w, gap, unit = 0.7, 0.4, 2.9
        cols = [C_GNN, C_LLM, C_ROUTER]

        def make_bars(vals):
            grp = VGroup()
            for i, (v, c) in enumerate(zip(vals, cols)):
                r = Rectangle(width=bar_w, height=max(v, 0.004) * unit,
                              fill_color=c, fill_opacity=0.9, stroke_width=0)
                r.move_to(base + RIGHT * (i - 1) * (bar_w + gap), aligned_edge=DOWN)
                grp.add(r)
            return grp

        axis = Line(base + LEFT * 1.9, base + RIGHT * 1.9, stroke_color=C_EDGE, stroke_width=2)
        ticks = VGroup(*[
            mono(n, size=17, color=cols[i]).next_to(
                base + RIGHT * (i - 1) * (bar_w + gap), DOWN, buff=0.2)
            for i, n in enumerate(["A", "B", "C"])
        ])
        ylab = mono("P(class)", size=16, color=MUTED).next_to(base + LEFT * 1.9, UP, buff=1.5)
        passes = [[0.42, 0.38, 0.20], [0.24, 0.55, 0.21], [0.51, 0.30, 0.19], [0.29, 0.34, 0.37]]
        bars = make_bars(passes[0])
        node = Dot(
            LEFT * 3.2 + DOWN * 0.6, radius=0.26, color=C_GNN
        ).set_z_index(GRAPH_NODE_Z)
        nlab = mono("node v", size=17, color=MUTED).next_to(node, DOWN, buff=0.28)
        counter = mono("forward pass 1 / 4", size=18, color=MUTED)
        counter.next_to(VGroup(axis, ylab), UP, buff=0.4)
        # Mũi tên đi NGANG đúng cao độ của nót: bản cũ trỏ chéo xuống mép trái
        # trục nên nhìn như bị méo, lại thêm đầu mũi tên quá to.
        arrow = Arrow(
            node.get_right(),
            np.array([axis.get_left()[0] - 0.2, node.get_center()[1], 0.0]),
            buff=0.3, stroke_width=2.4, color=C_EDGE,
            tip_length=0.12, max_tip_length_to_length_ratio=0.06,
        ).set_z_index(GRAPH_EDGE_FX_Z)

        beat(self, "Cuối cùng là lốc gin.", FadeIn(head), FadeIn(sub), run_time=0.8)
        # "gờ nờ nờ uncertainty" — chuỗi chữ cái rời ghép ngay vào một từ tiếng
        # Anh nên bị đọc méo; dùng "độ bất định của gờ nờ nờ" và đọc nhanh hơn.
        beat(self, "Công trình này dùng độ bất định (ân certainty) của gờ nờ nờ làm tiêu chí định tuyến.",
             speed=1.15)
        beat(self, "Mô hình chạy nhiều lần lượt truyền xuôi với đờ-róp-ao bật.",
             GrowFromCenter(node), FadeIn(nlab), GrowArrow(arrow), Create(axis),
             FadeIn(ticks), FadeIn(ylab), FadeIn(counter), FadeIn(bars), run_time=1.3)
        beat(self, "Mỗi lần, một phần neuron bị tắt ngẫu nhiên.")

        # Ba lượt truyền xuôi còn lại chạy TRONG lúc đọc câu kế, và mỗi lượt để
        # lại một phân phối thu nhỏ ở hàng dưới. Bản cũ chỉ thay tại chỗ nên
        # xem xong không còn gì để so sánh — mà "dao động" thì phải thấy nhiều
        # mẫu cạnh nhau mới cảm được.
        sample_slots = [LEFT * 4.3 + DOWN * 2.25, LEFT * 2.65 + DOWN * 2.25,
                        LEFT * 1.0 + DOWN * 2.25]
        samples = VGroup()
        with self.voiceover(
            text="Dự đoán dao động nhiều thì nót đó bị coi là không chắc chắn."
        ) as tracker:
            for (i, vals), slot in zip(enumerate(passes[1:], start=2), sample_slots):
                self.play(
                    Transform(bars, make_bars(vals)),
                    Transform(counter, mono(f"forward pass {i} / 4", size=18,
                                            color=MUTED).move_to(counter)),
                    run_time=0.55,
                )
                snap_bars = make_bars(vals).scale(0.34)
                snap_label = mono(f"pass {i}", size=13, color=MUTED)
                snapshot = VGroup(snap_bars, snap_label).arrange(DOWN, buff=0.14).move_to(slot)
                samples.add(snapshot)
                self.play(TransformFromCopy(bars, snap_bars), FadeIn(snap_label), run_time=0.4)

        verdict = VGroup(panel(txt("high uncertainty", size=20, color=ACCENT), buff=0.24),
                         txt("high uncertainty", size=20, color=ACCENT))
        verdict.next_to(VGroup(axis, ticks), DOWN, buff=0.7)

        # --- Bốn câu dưới đây trước kia đọc chay trên hình cũ. Dựng một dải so
        # sánh ba tiêu chí, rồi chỉ ra đúng chỗ hụt của độ bất định. ------------
        def criterion_card(name, note, color, dim=False):
            inner = VGroup(
                mono(name, size=19, color=MUTED if dim else color),
                txt(note, size=15, color=MUTED),
            ).arrange(DOWN, buff=0.14)
            frame = panel(inner, color=MUTED if dim else color, buff=0.26,
                          fill_opacity=0.05 if dim else 0.12)
            return VGroup(frame, inner)

        criteria = VGroup(
            criterion_card("degree", "counts neighbours", C_GNN, dim=True),
            criterion_card("C-density", "distance in feature space", C_ROUTER, dim=True),
            criterion_card("GNN uncertainty", "reads the model's own state", ACCENT),
        ).arrange(RIGHT, buff=0.55).move_to(UP * 0.75)

        beat(self, "So với bậc và mật độ, độ bất định trực tiếp hơn hẳn.",
             FadeIn(verdict), run_time=0.7)
        beat(self, "Vì nó phản ánh trạng thái của chính mô hình gờ nờ nờ.",
             FadeOut(VGroup(node, nlab, arrow, axis, ticks, ylab, counter, bars,
                            samples, verdict)),
             FadeIn(criteria, shift=UP * 0.12),
             run_time=1.2)

        gnn_source = labeled_box("GNN", C_GNN, width=1.9, height=0.72).move_to(
            DOWN * 1.45
        ).set_z_index(GRAPH_NODE_Z)
        to_uncertainty = Arrow(
            gnn_source.get_top(), criteria[2].get_bottom(), buff=0.18,
            color=ACCENT, stroke_width=2.2, tip_length=0.12,
            max_tip_length_to_length_ratio=0.06,
        ).set_z_index(GRAPH_EDGE_FX_Z)
        struggling = VGroup(
            cross(color=C_BAD, size=0.22),
            txt("GNN is struggling here", size=19, color=C_BAD, weight=BOLD),
        ).arrange(RIGHT, buff=0.2).move_to(
            LEFT * 0.35 + DOWN * 2.5
        ).set_z_index(GRAPH_NODE_Z)
        beat(self, "Nhưng độ bất định cao chỉ nói rằng gờ nờ nờ đang gặp khó.",
             FadeIn(gnn_source), GrowArrow(to_uncertainty),
             FadeIn(struggling, shift=UP * 0.1), run_time=1.3)

        llm_guess = labeled_box("LLM does better?", C_LLM, width=3.4, height=0.72)
        llm_guess.move_to(RIGHT * 4.55 + DOWN * 2.5).set_z_index(GRAPH_NODE_Z)
        maybe_link = DashedLine(struggling.get_right(), llm_guess.get_left(),
                                dash_length=0.12, color=MUTED, stroke_width=2,
                                z_index=GRAPH_EDGE_FX_Z)
        not_implied = txt("not implied", size=15, color=MUTED)
        not_implied.next_to(maybe_link, UP, buff=0.12)
        beat(self, "Nó không đảm bảo lờ lờ mờ sẽ làm tốt hơn.",
             Create(maybe_link), FadeIn(not_implied), FadeIn(llm_guess), run_time=1.2)

        self.clear_scene(keep=(bnr,))

        # --- hai node cùng uncertainty, hai kết cục ------------------------------
        def case(tag, snippet, outcome, color, mark):
            # text_chip() chỉ dựng một dòng rồi co lại cho vừa bề rộng, trích dẫn
            # dài sẽ nhỏ tới mức không đọc được. Dựng bằng txt() nhiều dòng + panel().
            t = txt(tag, size=17, color=MUTED, weight=BOLD)
            quote = txt(snippet, size=18, color=INK, line_spacing=0.9)
            quote_box = VGroup(panel(quote, color=C_EDGE, buff=0.28, fill_opacity=0.5), quote)
            res = VGroup(mark, txt(outcome, size=21, color=color, weight=BOLD)).arrange(
                RIGHT, buff=0.28)
            inner = VGroup(t, quote_box, res).arrange(DOWN, buff=0.3)
            return VGroup(panel(inner, color=color, buff=0.36), inner)

        left = case("NODE 1 · CLEAR TEXT",
                    '"Support vector machines for\ntext categorization: we propose\n'
                    'a kernel-based classifier..."',
                    "LLM fixes it", C_GOOD, check())
        right = case("NODE 2 · VAGUE TEXT",
                     '"A note on the complexity\nof the problem."',
                     "LLM fails too", C_BAD, cross())
        cases = VGroup(left, right).arrange(RIGHT, buff=0.6, aligned_edge=UP).shift(DOWN * 0.3)
        same = VGroup(panel(txt("Same high uncertainty", size=20, color=ACCENT), buff=0.24),
                      txt("Same high uncertainty", size=20, color=ACCENT))
        same.next_to(cases, DOWN, buff=0.4)

        beat(self, "Hãy xét hai nót có cùng mức độ bất định cao.")
        beat(self, "nót thứ nhất: cấu trúc nhiễu, nhưng phần tóm tắt nói rất rõ chủ đề.",
             FadeIn(left, shift=RIGHT * 0.3), run_time=1.0)
        beat(self, "lờ lờ mờ đọc đoạn văn bản này và sửa được dự đoán.")
        beat(self, "nót thứ hai: cấu trúc nhiễu y hệt, nhưng văn bản ngắn và mơ hồ.",
             FadeIn(right, shift=LEFT * 0.3), run_time=1.0)
        beat(self, "Ở đây lờ lờ mờ cũng không đủ thông tin, gọi thêm chỉ tốn tiền.")
        beat(self, "Cùng một tín hiệu độ bất định, hai kết cục khác hẳn nhau.",
             FadeIn(same), run_time=0.7)

        self.clear_scene(keep=(bnr,))

        # --- rủi ro rewiring của LOGIN -------------------------------------------
        a = Dot(LEFT * 1.5 + DOWN * 0.2, radius=0.24, color=C_GNN).set_z_index(
            GRAPH_NODE_Z
        )
        b = Dot(RIGHT * 1.5 + DOWN * 0.2, radius=0.24, color=C_LLM).set_z_index(
            GRAPH_NODE_Z
        )
        e = Line(
            a.get_center(), b.get_center(), stroke_color=C_EDGE, stroke_width=4,
            z_index=GRAPH_EDGE_Z,
        )
        elab = mono("heterophilous edge", size=17, color=MUTED).next_to(
            e, UP, buff=0.25
        ).set_z_index(GRAPH_LABEL_Z)
        cut = cross(size=0.4).move_to(e).set_z_index(GRAPH_LABEL_Z)
        warn = txt("Cutting hard edges can cut useful information too.",
                   size=22, color=C_BAD).next_to(e, DOWN, buff=1.0)

        beat(self, "Ngoài ra, lốc gin còn dùng độ bất định để cắt bớt cạnh của đồ thị.",
             Create(e), GrowFromCenter(a), GrowFromCenter(b), FadeIn(elab), run_time=1.0)
        beat(self, "Tức là loại bỏ những cạnh bị coi là gây khó, chứ không nối thêm cạnh mới.")
        beat(self, "Việc này có rủi ro riêng.", Create(cut),
             e.animate.set_stroke(color=C_BAD, opacity=0.25), run_time=0.8)
        beat(self, "Nó có thể xoá nhầm cạnh dị phối vẫn đang mang thông tin.",
             FadeIn(warn), run_time=0.7)

        self.clear_scene()
        punch = VGroup(
            txt("Uncertainty reads the state of the GNN.", size=24, color=INK),
            txt("But it cannot read the LLM.", size=24, color=ACCENT, weight=BOLD),
        ).arrange(DOWN, buff=0.26)
        beat(self, "độ bất định đọc được trạng thái của gờ nờ nờ.", Write(punch), run_time=1.5)
        # Câu ngắn kết thúc ngay sau chuỗi "lờ lờ mờ" nên bị đọc méo; kéo dài câu
        # cho có đà và sinh lại nhanh hơn một chút.
        beat(self, "Nhưng nó không nói được gì về phía lờ lờ mờ.", speed=1.15)


# ===========================================================================
class S2_06_Setup(GlanceScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        head = heading("How do we evaluate a heuristic fairly?",
                       color=ACCENT).to_edge(UP, buff=0.9)

        beat(self, "Vậy đánh giá một tiêu chí định tuyến thế nào cho công bằng?",
             Write(head), run_time=1.4)
        beat(self, "bài báo không chỉ nhìn độ chính xác của gờ nờ nờ trên nhóm nót bị coi là khó.")
        beat(self, "Thay vào đó, kiểm tra thẳng điều gì xảy ra sau khi định tuyến.")

        flow = pipeline([
            ("Graph", C_EDGE),
            ("Heuristic", C_ROUTER),
            ("Top-k% nodes", C_LLM),
            ("LLM", C_LLM),
            ("Compare vs GNN", C_GOOD),
        ], box_w=2.25, box_h=0.9, buff=0.4).shift(UP * 0.65)
        frozen = mono("both GNN and LLM are frozen", size=18,
                      color=C_GNN).next_to(flow, DOWN, buff=0.55)

        beat(self, "Từ đồ thị, tiêu chí chọn ra tốp ca phần trăm nót.",
             LaggedStart(*[FadeIn(b, shift=RIGHT * 0.2) for b in flow.boxes], lag_ratio=0.16),
             LaggedStart(*[GrowArrow(a) for a in flow.arrows], lag_ratio=0.16), run_time=2.0)
        beat(self, "Những nót đó đi qua lờ lờ mờ, rồi so với dự đoán gốc của gờ nờ nờ.")
        beat(self, "Quan trọng: cả gờ nờ nờ lẫn lờ lờ mờ đều được đóng băng.", FadeIn(frozen), run_time=0.7)
        beat(self, "Nên mọi khác biệt chỉ đến từ việc tiêu chí đã chọn tập nót nào.")

        def chips(label, items, color):
            lab = mono(label, size=17, color=MUTED)
            row = VGroup()
            for i in items:
                t = txt(i, size=19, color=color)
                row.add(VGroup(panel(t, buff=0.18), t))
            row.arrange(RIGHT, buff=0.22)
            return VGroup(lab, row).arrange(DOWN, buff=0.22)

        cfg = VGroup(
            chips("DATASET", DATASETS, INK),
            chips("BACKBONE", ["GCN", "GCNII"], C_GNN),
            chips("FEATURES", ["original", "enhanced"], C_LLM),
            chips("BUDGET", KS, C_ROUTER),
        ).arrange(RIGHT, buff=0.55).next_to(frozen, DOWN, buff=0.6)
        cfg.scale_to_fit_width(12.2)

        beat(self, "Thí nghiệm chạy trên cô ra, pắp mét và ác xíp hai ba.",
             FadeIn(cfg[0]), run_time=0.7)
        beat(self, "Hai mô hình nền: gờ xê en là mô hình cơ sở, còn gờ xê en hai là mô hình hiện đại hơn.",
             FadeIn(cfg[1]), run_time=0.7, speed=1.15)
        beat(self, "Hai loại đặc trưng: gốc, và tăng cường sinh bởi quy en ba tám bi.",
             FadeIn(cfg[2]), run_time=0.7)
        # Bảng 1 chỉ báo cáo cột tăng cường. Nói rõ ở đây, nếu không khán giả sẽ
        # đi tìm hàng "gốc" trong bản đồ nhiệt ở S2_08 và không thấy.
        beat(self, "Bảng số lát nữa chỉ lấy cột tăng cường, cho gọn.",
             Circumscribe(cfg[2][1][1], color=C_LLM, buff=0.12), run_time=1.2)
        beat(self, "Mỗi tiêu chí lần lượt định tuyến tốp mười, mười lăm, rồi hai mươi phần trăm.",
             FadeIn(cfg[3]), run_time=0.7)

        self.clear_scene()
        rules = bullets([
            "Degree-based: pick the LOWEST-degree nodes",
            "Density-based: pick the LOWEST-density nodes",
            "Uncertainty-based: pick the HIGHEST-uncertainty nodes",
            "Random routing: the baseline to beat",
        ], size=23, dot_color=ACCENT, width=9.0)

        beat(self, "Cụ thể: cách dựa trên bậc chọn nót có bậc thấp nhất.",
             FadeIn(rules[0], shift=RIGHT * 0.2), run_time=0.7)
        beat(self, "Cách dựa trên mật độ chọn nót có mật độ phân cụm thấp nhất.",
             FadeIn(rules[1], shift=RIGHT * 0.2), run_time=0.7)
        beat(self, "Cách dựa trên độ bất định chọn nót có độ bất định cao nhất.",
             FadeIn(rules[2], shift=RIGHT * 0.2), run_time=0.7)
        beat(self, "Và ngẫu nhiên định tuyến làm mốc so sánh.",
             FadeIn(rules[3], shift=RIGHT * 0.2), run_time=0.7)
        beat(self, "Đây là cái mốc mà mọi tiêu chí ít nhất phải vượt qua.",
             Circumscribe(rules[3], color=MUTED, buff=0.16), run_time=1.4)


# ===========================================================================
class S2_07_NCS(GlanceScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        head = heading("Net Correction Score", color=ACCENT).to_edge(UP, buff=0.85)
        sub = mono("NCS  ·  the net benefit of routing", size=18,
                   color=MUTED).next_to(head, DOWN, buff=0.18)

        def defn(tag, desc, color, mark):
            t = VGroup(mark, mono(tag, size=20, color=color)).arrange(RIGHT, buff=0.26)
            d = txt(desc, size=20, color=INK, line_spacing=0.9)
            inner = VGroup(t, d).arrange(DOWN, buff=0.24, aligned_edge=LEFT)
            return VGroup(panel(inner, color=color, buff=0.34), inner)

        wc = defn("WC  (wrong to correct)",
                  "GNN wrong, LLM makes it right.\nA BENEFICIAL correction.", C_GOOD, check())
        cw = defn("CW  (correct to wrong)",
                  "GNN right, LLM makes it wrong.\nA HARMFUL correction.", C_BAD, cross())
        defs = VGroup(wc, cw).arrange(RIGHT, buff=0.6, aligned_edge=UP).shift(DOWN * 0.3)

        beat(self, "Để đo chất lượng tập nót được định tuyến, bài báo dùng điểm hiệu chỉnh thuần.",
             FadeIn(head), FadeIn(sub), run_time=0.9)
        beat(self, "Viết tắt là en xi ét. Ý tưởng rất trực quan.")
        beat(self, "gờ nờ nờ sai mà lờ lờ mờ sửa thành đúng: một lần sửa có lợi.",
             FadeIn(wc, shift=RIGHT * 0.3), run_time=1.0)
        # Ba câu quanh đây toàn chuỗi chữ cái đánh vần liền nhau nên giọng đọc bị
        # méo; đọc nhanh hơn một nhịp cho liền mạch.
        beat(self, "Tập này gọi là đắp-bờ-liu xi, tức là sai thành đúng.", speed=1.15)
        beat(self, "gờ nờ nờ đúng mà lờ lờ mờ làm thành sai: một lần sửa có hại.",
             FadeIn(cw, shift=LEFT * 0.3), run_time=1.0, speed=1.15)
        beat(self, "Tập này gọi là xi đắp-bờ-liu, đúng thành sai.")

        formula = MathTex(r"\mathrm{NCS} \;=\; \frac{|WC| - |CW|}{|R|}",
                          color=INK).scale(1.15).shift(DOWN * 0.3)
        self.play(FadeOut(defs), run_time=0.5)
        beat(self, "en xi ét bằng số nót trong đắp-bờ-liu xi trừ số nót trong xi đắp-bờ-liu.",
             Write(formula), run_time=1.6)
        beat(self, "Rồi chia cho tổng số nót được định tuyến.")

        # --- ví dụ 100 node ------------------------------------------------------
        self.play(formula.animate.scale(0.62).to_edge(RIGHT, buff=1.2).shift(UP * 0.6),
                  run_time=0.8)
        cells = VGroup()
        for i in range(100):
            cells.add(Square(side_length=0.26, fill_color=C_EDGE, fill_opacity=0.35,
                             stroke_color=C_EDGE, stroke_width=1.0)
                      .move_to(RIGHT * (i % 10) * 0.32 + DOWN * (i // 10) * 0.32))
        cells.move_to(LEFT * 3.2 + DOWN * 0.3)
        glab = mono("100 routed nodes", size=18, color=MUTED).next_to(cells, UP, buff=0.32)
        t_wc = VGroup(mono("WC", size=20, color=C_GOOD),
                      mono("25", size=28, color=C_GOOD)).arrange(RIGHT, buff=0.3)
        t_cw = VGroup(mono("CW", size=20, color=C_BAD),
                      mono("10", size=28, color=C_BAD)).arrange(RIGHT, buff=0.3)
        tallies = VGroup(t_wc, t_cw).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        tallies.next_to(formula, DOWN, buff=0.8)
        result = MathTex(r"\mathrm{NCS}=\frac{25-10}{100}=0.15",
                         color=INK).scale(0.9).next_to(tallies, DOWN, buff=0.6)

        beat(self, "Ví dụ, giả sử ta định tuyến một trăm nót.",
             LaggedStart(*[FadeIn(c) for c in cells], lag_ratio=0.006),
             FadeIn(glab), run_time=1.3)
        beat(self, "lờ lờ mờ sửa đúng được hai mươi lăm nót.",
             LaggedStart(*[c.animate.set_fill(C_GOOD, 0.9).set_stroke(C_GOOD)
                           for c in cells[:25]], lag_ratio=0.02),
             FadeIn(t_wc), run_time=1.4)
        beat(self, "Nhưng đồng thời làm hỏng mười nót.",
             LaggedStart(*[c.animate.set_fill(C_BAD, 0.9).set_stroke(C_BAD)
                           for c in cells[25:35]], lag_ratio=0.04),
             FadeIn(t_cw), run_time=1.3)
        beat(self, "en xi ét bằng hai mươi lăm trừ mười, chia một trăm, tức không chấm một năm.",
             Write(result), run_time=1.2)

        # --- thang đo -------------------------------------------------------------
        self.clear_scene()
        axis = NumberLine(x_range=[-1, 1, 0.5], length=9.2, include_numbers=True,
                          decimal_number_config={"num_decimal_places": 1},
                          color=C_EDGE, font_size=24).shift(DOWN * 0.2)
        axis.numbers.set_color(MUTED)
        neg = Line(axis.n2p(-1), axis.n2p(0), stroke_color=C_BAD, stroke_width=7)
        pos = Line(axis.n2p(0), axis.n2p(1), stroke_color=C_GOOD, stroke_width=7)
        shead = txt("How to read an NCS value", size=24,
                    color=INK).next_to(axis, UP, buff=1.4)
        l_pos = txt("LLM yields net benefit", size=20,
                    color=C_GOOD).next_to(axis.n2p(0.5), DOWN, buff=0.8)
        l_zero = txt("break-even: paid for nothing", size=20,
                     color=MUTED).next_to(axis.n2p(0), UP, buff=0.5)
        l_neg = txt("more harm than good", size=20,
                    color=C_BAD).next_to(axis.n2p(-0.5), DOWN, buff=0.8)

        beat(self, "Cách đọc en xi ét như sau.", FadeIn(shead), Create(axis), run_time=1.1)
        beat(self, "en xi ét dương nghĩa là lờ lờ mờ tạo ra lợi ích ròng.",
             Create(pos), FadeIn(l_pos), run_time=0.9)
        # Trường hợp en xi ét bằng không được dựng thành hình: hai hàng ô bằng
        # nhau (sửa được / làm hỏng) triệt tiêu lẫn nhau, và chi phí gọi lờ lờ mờ
        # bị gạch bỏ. Hai câu này trước kia đọc chay trên cái thang đo tĩnh.
        zero_dot = Dot(axis.n2p(0), radius=0.10, color=MUTED)
        fixed_row = VGroup(*[
            Square(0.17, fill_color=C_GOOD, fill_opacity=0.9, stroke_width=0)
            for _ in range(12)
        ]).arrange(RIGHT, buff=0.07)
        broken_row = VGroup(*[
            Square(0.17, fill_color=C_BAD, fill_opacity=0.9, stroke_width=0)
            for _ in range(12)
        ]).arrange(RIGHT, buff=0.07)
        balance = VGroup(
            VGroup(fixed_row, mono("fixed", size=15, color=C_GOOD)).arrange(DOWN, buff=0.14),
            mono("=", size=26, color=MUTED),
            VGroup(broken_row, mono("broken", size=15, color=C_BAD)).arrange(DOWN, buff=0.14),
        ).arrange(RIGHT, buff=0.55).move_to(DOWN * 2.45)

        cost_inner = mono("cost paid:  100 LLM calls", size=19, color=C_LLM)
        cost_chip = VGroup(panel(cost_inner, color=C_LLM, buff=0.22, fill_opacity=0.1), cost_inner)
        cost_chip.move_to(UP * 2.6)
        strike = Line(cost_chip.get_left() + RIGHT * 0.12, cost_chip.get_right() + LEFT * 0.12,
                      color=C_BAD, stroke_width=3)
        nothing_back = mono("net gain: 0", size=19, color=C_BAD, weight=BOLD)
        nothing_back.next_to(cost_chip, RIGHT, buff=0.45)

        beat(self, "en xi ét bằng không: số nót sửa được đúng bằng số nót bị làm hỏng.",
             FadeIn(l_zero), FadeIn(zero_dot, scale=0.6),
             FadeIn(balance, shift=UP * 0.12), FadeIn(cost_chip), run_time=1.3)
        beat(self, "Toàn bộ chi phí bỏ ra để gọi lờ lờ mờ coi như đổ sông đổ biển.",
             Create(strike), cost_chip.animate.set_opacity(0.45),
             FadeIn(nothing_back, shift=LEFT * 0.12),
             LaggedStart(*[c.animate.set_opacity(0.3)
                           for c in [*fixed_row, *broken_row]], lag_ratio=0.02),
             run_time=1.4, speed=1.15)
        beat(self, "Còn en xi ét âm nghĩa là định tuyến gây hại nhiều hơn có lợi.",
             Create(neg), FadeIn(l_neg), run_time=0.9)

        self.clear_scene()
        punch = VGroup(
            txt("NCS does not reward finding hard nodes.", size=24, color=INK),
            txt("It rewards only the nodes the LLM actually fixes.", size=24,
                color=ACCENT, weight=BOLD),
        ).arrange(DOWN, buff=0.26)
        beat(self, "Điểm hay của en xi ét nằm ở đây.", Write(punch), run_time=1.6)
        beat(self, "Nó không thưởng cho việc tìm ra nót khó.")
        beat(self, "Nó chỉ thưởng khi lờ lờ mờ thật sự sửa được nót đó.")


# ===========================================================================
CELL_W, CELL_H = 0.74, 0.42


def build_heatmap():
    """Bảng 1 dưới dạng heatmap. Trả VGroup kèm .cell / .row / .block."""
    grid = VGroup()
    cell, row, row_lab, block_lab = {}, {}, {}, {}
    y = 0.0
    for backbone in ["GCN", "GCNII"]:
        bl = mono(f"{backbone} · Enh.", size=18, color=ACCENT)
        bl.move_to([-CELL_W * 4.5 - 1.5, y, 0], aligned_edge=LEFT)
        block_lab[backbone] = bl
        grid.add(bl)
        y -= CELL_H * 0.95
        for strat in STRATS:
            cells = VGroup()
            for c, v in enumerate(T1[backbone][strat]):
                rect = Rectangle(width=CELL_W, height=CELL_H, fill_color=ncs_color(v),
                                 fill_opacity=1.0, stroke_color=BG, stroke_width=1.2)
                rect.move_to([(c - 4) * CELL_W, y, 0])
                cells.add(VGroup(rect, mono(f"{v:.2f}", size=14, color=INK).move_to(rect)))
                cell[(backbone, strat, c)] = cells[-1]
            lab = mono(strat, size=17, color=MUTED if strat == "Random" else INK)
            lab.next_to(cells, LEFT, buff=0.28)
            row[(backbone, strat)] = cells
            row_lab[(backbone, strat)] = lab
            grid.add(cells, lab)
            y -= CELL_H
        y -= CELL_H * 0.5

    header = VGroup()
    for i, ds in enumerate(DATASETS):
        header.add(txt(ds, size=21, color=INK, weight=BOLD)
                   .move_to([(i * 3 + 1 - 4) * CELL_W, CELL_H * 2.0, 0]))
        header.add(Line([(i * 3 - 4.5) * CELL_W + 0.05, CELL_H * 1.5, 0],
                        [(i * 3 + 2.5) * CELL_W - 0.05, CELL_H * 1.5, 0],
                        stroke_color=C_EDGE, stroke_width=2))
    for c in range(9):
        header.add(mono(KS[c % 3], size=14, color=MUTED)
                   .move_to([(c - 4) * CELL_W, CELL_H * 1.05, 0]))

    g = VGroup(header, grid)
    g.cell, g.row, g.row_lab, g.block_lab, g.header = cell, row, row_lab, block_lab, header
    g.block = lambda bb: VGroup(block_lab[bb], *[row[(bb, s)] for s in STRATS],
                                *[row_lab[(bb, s)] for s in STRATS])
    g.cols = lambda ds: range(DATASETS.index(ds) * 3, DATASETS.index(ds) * 3 + 3)
    return g


class S2_08_Table1(GlanceScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        head = heading("Table 1 · NCS per routing strategy", color=ACCENT)
        head.scale_to_fit_width(min(head.width, 11.0)).to_edge(UP, buff=0.8)
        sub = mono("greener = more benefit  ·  redder = more harm", size=17,
                   color=MUTED).next_to(head, DOWN, buff=0.16)
        hm = build_heatmap().scale(0.88).move_to(LEFT * 0.9 + DOWN * 0.7)

        beat(self, "Đây là Bảng 1 của bài báo, trình bày lại dưới dạng bản đồ nhiệt.",
             FadeIn(head), FadeIn(sub), run_time=0.9)
        beat(self, "Mỗi ô là một giá trị en xi ét.",
             FadeIn(hm.header), run_time=0.7)
        beat(self, "Ô càng xanh thì lợi ích càng cao, càng đỏ thì càng gây hại.",
             LaggedStart(*[FadeIn(hm.block(bb)) for bb in ["GCN", "GCNII"]], lag_ratio=0.3),
             run_time=1.7)
        beat(self, "Bốn hàng là bốn chiến lược, chín cột là ba bộ dữ liệu nhân ba mức định tuyến.")

        good = VGroup(*[hm.cell[(bb, "Uncertainty", c)] for bb in ["GCN", "GCNII"]
                        for ds in ["Pubmed", "Arxiv23"] for c in hm.cols(ds)])
        frames = VGroup(*[
            SurroundingRectangle(
                VGroup(*[hm.cell[(bb, "Uncertainty", c)] for bb in ["GCN", "GCNII"]
                         for c in hm.cols(ds)]),
                color=C_LLM, stroke_width=3, buff=0.05, corner_radius=0.04)
            for ds in ["Pubmed", "Arxiv23"]
        ])
        star = hm.cell[("GCN", "Uncertainty", 3)]

        # Phóng to ô tại chỗ sẽ che ô bên cạnh. Thay bằng viền nhấn + số đọc lại
        # ở lề phải, chỗ đang trống vì heatmap đã dịch sang trái.
        star_ring = SurroundingRectangle(star, color=C_GOOD, stroke_width=3.5,
                                         buff=0.03, corner_radius=0.03)
        readout = VGroup(
            mono("Pubmed · GCN Enh. · k = 10%", size=14, color=MUTED),
            txt("0.20", size=42, color=C_GOOD, weight=BOLD),
        ).arrange(DOWN, buff=0.16)
        readout.move_to([4.3, star.get_center()[1], 0])
        lead = Line(star_ring.get_right(), readout.get_left(), buff=0.18,
                    stroke_color=C_GOOD, stroke_width=2)

        beat(self, "Hãy nhìn pắp mét và ác xíp hai ba trước.",
             Create(frames), Indicate(good, color=C_LLM, scale_factor=1.04), run_time=1.4)
        beat(self, "Ở đây độ bất định là tiêu chí tốt nhất trong mọi thiết lập.")
        beat(self, "Với gờ xê en dùng đặc trưng tăng cường trên pắp mét, en xi ét đạt không chấm hai không.",
             Create(star_ring), Create(lead), FadeIn(readout, shift=LEFT * 0.2), run_time=1.0)
        beat(self, "Nghĩa là cứ một trăm nót được định tuyến, lờ lờ mờ tạo hai mươi lần sửa có lợi.")
        beat(self, "Sau khi đã trừ đi những nót bị làm sai. Đây là kết quả tốt.")

        self.play(FadeOut(frames), FadeOut(star_ring), FadeOut(lead), FadeOut(readout),
                  run_time=0.6)

        # Đòn kết trên cô ra để dành cho S2_09, nơi biểu đồ cột cho thấy việc đổi
        # dấu rõ hơn hẳn bản đồ nhiệt. Ở đây chỉ gieo câu hỏi, tránh kể cùng một
        # kết luận hai lần trong vòng chín mươi giây.
        f_cora = SurroundingRectangle(
            VGroup(*[hm.cell[(bb, s, c)] for bb in ["GCN", "GCNII"]
                     for s in STRATS for c in hm.cols("Cora")]),
            color=C_BAD, stroke_width=3, buff=0.05, corner_radius=0.04)

        beat(self, "Nhưng bây giờ nhìn sang cột cô ra bên trái.",
             Create(f_cora), run_time=0.9)
        beat(self, "Cả mảng đỏ. Trên bộ dữ liệu này không tiêu chí nào có lợi.")
        beat(self, "Kể cả tiêu chí vừa thắng ở hai bộ kia.",
             Indicate(hm.cell[("GCN", "Uncertainty", 0)], color=C_BAD, scale_factor=1.15),
             run_time=1.2)
        beat(self, "Chuyện gì đang xảy ra ở đây?")


# ===========================================================================
class S2_09_PubmedVsCora(GlanceScene):
    """Đối chiếu trực tiếp Pubmed và Cora bằng bar_chart (gợi ý trong TASK.md)."""

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        head = heading("Uncertainty routing: Pubmed vs Cora",
                       color=ACCENT).to_edge(UP, buff=0.8)
        sub = mono("GCN · enhanced features · NCS at k = 10 / 15 / 20%", size=17,
                   color=MUTED).next_to(head, DOWN, buff=0.16)

        pub = T1["GCN"]["Uncertainty"][3:6]
        cora = T1["GCN"]["Uncertainty"][0:3]
        chart = bar_chart(
            pub + cora,
            ["10%", "15%", "20%", "10%", "15%", "20%"],
            colors=[C_GOOD] * 3 + [C_BAD] * 3,
            y_range=(-0.15, 0.25, 0.1),
            width=8.6, height=3.9,
        ).shift(DOWN * 0.55)
        # Cột Cora đều âm, next_to(..., UP) sẽ dán nhãn ngay trên trục 0 nhìn rất lệch.
        # Ghim cả hai nhãn lên cùng một độ cao, phía trên khung trục.
        pub_bars = VGroup(*[chart.bars[i] for i in range(3)])
        cora_bars = VGroup(*[chart.bars[i] for i in range(3, 6)])
        lab_y = chart.axes.get_top()[1] + 0.34
        lab_pub = txt("Pubmed", size=21, color=C_GOOD, weight=BOLD)
        lab_cora = txt("Cora", size=21, color=C_BAD, weight=BOLD)
        lab_pub.move_to([pub_bars.get_center()[0], lab_y, 0])
        lab_cora.move_to([cora_bars.get_center()[0], lab_y, 0])

        # Mốc ngẫu nhiên trên cô ra. Random đổi theo từng mức k (-0.02 / -0.06 /
        # -0.04), nên phải vẽ ba đoạn riêng: một đường ngang duy nhất sẽ khiến
        # khán giả hiểu random là hằng số, và câu "tệ hơn random" chỉ đúng ở 10%.
        rand_marks = VGroup()
        for i, rv in enumerate(T1["GCN"]["Random"][0:3]):
            bar = chart.bars[3 + i][0]
            y = chart.axes.c2p(0, rv)[1]
            rand_marks.add(DashedLine(
                [bar.get_center()[0] - 0.44, y, 0],
                [bar.get_center()[0] + 0.44, y, 0],
                stroke_color=MUTED, stroke_width=3, dash_length=0.1))
        rand_lab = mono("random", size=15, color=MUTED)
        rand_lab.next_to(rand_marks[-1], RIGHT, buff=0.18)

        beat(self, "Tách riêng độ bất định ra, đặt hai bộ dữ liệu cạnh nhau.",
             FadeIn(head), FadeIn(sub), FadeIn(chart.axes), run_time=1.0)
        beat(self, "Trên pắp mét, tiêu chí này cho en xi ét dương ở cả ba mức.",
             LaggedStart(*[GrowFromEdge(chart.bars[i], DOWN) for i in range(3)],
                         lag_ratio=0.15), FadeIn(lab_pub), run_time=1.5)
        beat(self, "Trên cô ra, vẫn tiêu chí đó, cả ba mức đều âm.",
             LaggedStart(*[GrowFromEdge(chart.bars[i], DOWN) for i in range(3, 6)],
                         lag_ratio=0.15), FadeIn(lab_cora), run_time=1.5)
        beat(self, "Không phải kém đi một chút, mà đổi hẳn dấu.")
        beat(self, "Ba đường nét đứt là mốc chọn nót ngẫu nhiên trên cô ra.",
             LaggedStart(*[Create(m) for m in rand_marks], lag_ratio=0.2),
             FadeIn(rand_lab), run_time=1.4)
        beat(self, "Ở mức mười phần trăm, chọn bừa chỉ âm không chấm không hai.")
        beat(self, "Còn chọn kỹ những nót mà gờ nờ nờ không chắc chắn nhất.")
        beat(self, "Lại tụt xuống âm không chấm không chín, tệ hơn hẳn chọn bừa.",
             Indicate(VGroup(chart.bars[3], rand_marks[0]),
                      color=C_BAD, scale_factor=1.08), run_time=1.4)
        beat(self, "Ở hai mức còn lại nó nhúc nhích khá hơn ngẫu nhiên, nhưng vẫn âm cả ba.")

        self.clear_scene()
        punch = VGroup(
            txt("Same rule, opposite sign.", size=26, color=INK),
            txt("The heuristic is dataset-dependent.", size=26, color=ACCENT, weight=BOLD),
        ).arrange(DOWN, buff=0.26)
        beat(self, "Cùng một luật, ngược dấu. Tiêu chí này phụ thuộc bộ dữ liệu.",
             Write(punch), run_time=1.6)
        # Kết luận này trước đây nằm ở S2_08, chuyển xuống đây để đòn kết gọn vào
        # một chỗ. Cũng là lần đầu nối lại với vòng tròn bên phải ở S2_02.
        beat(self, "Nói cách khác, độ bất định của gờ nờ nờ không phải lúc nào cũng "
                   "phản ánh lợi thế của lờ lờ mờ.")


# ===========================================================================
class S2_10_DegreeDensity(GlanceScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        head = heading("What about degree and density?", color=ACCENT).to_edge(UP, buff=0.8)
        hm = build_heatmap().scale(0.88).move_to(LEFT * 0.9 + DOWN * 0.7)
        self.add(head, hm)

        unc = VGroup(*[hm.row[(bb, "Uncertainty")] for bb in ["GCN", "GCNII"]],
                     *[hm.row_lab[(bb, "Uncertainty")] for bb in ["GCN", "GCNII"]])
        cmp_rows = VGroup(*[hm.row[(bb, s)] for bb in ["GCN", "GCNII"]
                            for s in ["Random", "C-density", "Degree"]])

        beat(self, "Còn bậc và mật độ phân cụm thì sao?")
        beat(self, "Tạm bỏ hàng độ bất định sang một bên.",
             unc.animate.set_opacity(0.12), run_time=0.9)
        beat(self, "Chỉ so ba hàng còn lại với nhau.",
             Indicate(cmp_rows, color=MUTED, scale_factor=1.02), run_time=1.4)
        beat(self, "Trong phần lớn thiết lập, en xi ét của chúng chỉ xấp xỉ ngẫu nhiên định tuyến.")
        beat(self, "Có trường hợp còn thấp hơn cả ngẫu nhiên.")

        f = SurroundingRectangle(
            VGroup(*[hm.cell[("GCNII", "Degree", c)] for c in range(3)]),
            color=C_BAD, stroke_width=3, buff=0.05, corner_radius=0.04)
        tag_inner = txt("negative at all three budgets", size=19, color=C_BAD)
        tag = VGroup(panel(tag_inner, buff=0.22), tag_inner)
        tag.to_edge(RIGHT, buff=0.4).align_to(f, UP)

        beat(self, "Ví dụ, trên cô ra với mô hình nền gờ xê en hai.")
        beat(self, "Cách dựa trên bậc cho en xi ét âm ở cả ba mức định tuyến.",
             Create(f), FadeIn(tag), run_time=1.3)
        beat(self, "Trên pắp mét và ác xíp hai ba đôi khi có lợi ích dương.")
        beat(self, "Nhưng mức cải thiện rất nhỏ và không hề nhất quán.")

        self.clear_scene()
        punch = VGroup(
            txt("Simple structural properties can help sometimes,", size=24, color=INK),
            txt("but cannot pin down which nodes need the LLM.", size=24,
                color=ACCENT, weight=BOLD),
        ).arrange(DOWN, buff=0.26)
        beat(self, "Thuộc tính cấu trúc đơn giản có thể hữu ích đôi lúc.",
             Write(punch), run_time=1.6)
        beat(self, "Nhưng vẫn không đủ để xác định chắc chắn nót nào mới cần tới lờ lờ mờ.",
             speed=1.15)


# ===========================================================================
class S2_11_Backbone(GlanceScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        head = heading("Change the backbone, routing changes too",
                       color=ACCENT).to_edge(UP, buff=0.8)
        sub = mono("Pubmed · uncertainty routing", size=17,
                   color=MUTED).next_to(head, DOWN, buff=0.16)

        gcn = T1["GCN"]["Uncertainty"][3:6]
        gcnii = T1["GCNII"]["Uncertainty"][3:6]
        chart = bar_chart(
            gcn + gcnii,
            ["10%", "15%", "20%", "10%", "15%", "20%"],
            colors=[C_GNN] * 3 + [C_ROUTER] * 3,
            y_range=(0, 0.25, 0.1),
            width=8.6, height=3.6,
        ).shift(DOWN * 0.5)
        l_gcn = txt("GCN", size=22, color=C_GNN, weight=BOLD)
        l_gcnii = txt("GCNII", size=22, color=C_ROUTER, weight=BOLD)
        l_gcn.next_to(VGroup(*[chart.bars[i] for i in range(3)]), UP, buff=0.75)
        l_gcnii.next_to(VGroup(*[chart.bars[i] for i in range(3, 6)]), UP, buff=0.75)

        beat(self, "Còn một quan sát nữa, và nó khá tinh tế.",
             FadeIn(head), FadeIn(sub), FadeIn(chart.axes), run_time=1.0)
        beat(self, "Hiệu quả định tuyến thay đổi khi mô hình nền thay đổi.")
        beat(self, "Trên pắp mét, độ bất định với gờ xê en đạt en xi ét từ không chấm một bảy đến không chấm hai không.",
             LaggedStart(*[GrowFromEdge(chart.bars[i], DOWN) for i in range(3)],
                         lag_ratio=0.15), FadeIn(l_gcn), run_time=1.5)
        beat(self, "Nhưng đổi sang mô hình nền mạnh hơn là gờ xê en hai.",
             LaggedStart(*[GrowFromEdge(chart.bars[i], DOWN) for i in range(3, 6)],
                         lag_ratio=0.15), FadeIn(l_gcnii), run_time=1.5)
        beat(self, "Cùng tiêu chí đó chỉ còn khoảng không chấm không tám đến không chấm không chín. Giảm hơn một nửa.")
        beat(self, "Lý do có thể hiểu thế này.")
        beat(self, "gờ xê en hai đã tự xử lý được một phần nót khó.")
        beat(self, "Nên phần còn lại cho lờ lờ mờ sửa cũng co hẹp theo.")
        beat(self, "Một nót khó với gờ xê en chưa chắc còn khó với gờ xê en hai.")

        self.clear_scene()
        punch = VGroup(
            txt("Routing heuristics depend not only on the DATASET,", size=23, color=INK),
            txt("but also on the BACKBONE in use.", size=23, color=ACCENT, weight=BOLD),
        ).arrange(DOWN, buff=0.26)
        beat(self, "tiêu chí định tuyến không chỉ phụ thuộc bộ dữ liệu.", Write(punch), run_time=1.6)
        beat(self, "Mà còn phụ thuộc cả mô hình nền đang dùng.")


# ===========================================================================
class S2_12_Limits(GlanceScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        head = heading("Three limitations of existing heuristics",
                       color=ACCENT).to_edge(UP, buff=0.85)

        def limit(n, text, color):
            num = txt(n, size=20, color=BG, weight=BOLD)
            disc = Circle(radius=0.26, fill_color=color, fill_opacity=1,
                          stroke_width=0).move_to(num)
            label = txt(text, size=22, color=INK)
            return VGroup(VGroup(disc, num), label).arrange(RIGHT, buff=0.38)

        lims = VGroup(
            limit("1", "DATASET-dependent: what helps on Pubmed can hurt on Cora.", C_GNN),
            limit("2", "BACKBONE-dependent: a new GNN, a new set of hard nodes.", C_GNN),
            limit("3", "All of them are only proxies for GNN DIFFICULTY.", C_ROUTER),
        ).arrange(DOWN, buff=0.5, aligned_edge=LEFT).shift(DOWN * 0.3)

        beat(self, "Tổng hợp lại, bài báo chỉ ra ba hạn chế chính.", Write(head), run_time=1.3)
        beat(self, "Thứ nhất, chúng phụ thuộc bộ dữ liệu.",
             FadeIn(lims[0], shift=RIGHT * 0.25), run_time=0.8)
        beat(self, "Tín hiệu tốt trên pắp mét có thể gây hại trên cô ra.")
        beat(self, "Thứ hai, chúng phụ thuộc mô hình nền.",
             FadeIn(lims[1], shift=RIGHT * 0.25), run_time=0.8)
        beat(self, "Đổi gờ nờ nờ thì tập nót khó cũng đổi theo.")
        beat(self, "Và thứ ba, quan trọng nhất.",
             FadeIn(lims[2], shift=RIGHT * 0.25), run_time=0.8)
        beat(self, "Cả ba đều chỉ là tín hiệu thay thế cho độ khó với gờ nờ nờ.",
             Circumscribe(lims[2], color=C_ROUTER, buff=0.18), run_time=1.4)

        adv = MathTex(r"\text{LLM advantage}", r"\;=\;",
                      r"\mathcal{L}_{\text{GNN}}", r"\;-\;",
                      r"\mathcal{L}_{\text{LLM}}", color=INK).scale(1.05)
        adv[0].set_color(C_ROUTER)
        adv[2].set_color(C_GNN)
        adv[4].set_color(C_LLM)
        note = txt("the loss saved by calling the LLM, versus the GNN alone",
                   size=20, color=MUTED)
        grp = VGroup(adv, note).arrange(DOWN, buff=0.4)

        self.play(FadeOut(lims), FadeOut(head), run_time=0.6)
        beat(self, "Trong khi đó, thứ mà bộ định tuyến thật sự cần ước lượng chính là lợi thế mà lờ lờ mờ mang lại.",
             Write(adv), run_time=1.8, speed=1.15)
        beat(self, "Tức phần hàm mất mát tiết kiệm được khi dùng lờ lờ mờ so với chỉ dùng gờ nờ nờ.",
             FadeIn(note), run_time=0.7)

        self.play(grp.animate.scale(0.75).to_edge(UP, buff=1.0), run_time=0.8)

        # --- gọi lại hai vòng tròn ở S2_02, đóng vòng lập luận -------------------
        c1 = Circle(radius=1.4, stroke_color=C_GNN, stroke_width=3.2).set_fill(C_GNN, 0.42)
        c2 = Circle(radius=1.4, stroke_color=C_LLM, stroke_width=3.2).set_fill(C_LLM, 0.12)
        c1.move_to(LEFT * 0.82 + DOWN * 0.9)
        c2.move_to(RIGHT * 0.82 + DOWN * 0.9)
        lens = Intersection(c1, c2, fill_color=C_ROUTER, fill_opacity=0.55, stroke_width=0)
        n1 = txt("what the three signals measure", size=18,
                 color=C_GNN).next_to(c1, LEFT, buff=0.18)
        n2 = txt("what a router needs", size=18,
                 color=C_LLM).next_to(c2, RIGHT, buff=0.18)

        beat(self, "Còn nhớ hai vòng tròn ở đầu phần không?",
             Create(c1), Create(c2), FadeIn(lens), run_time=1.2)
        beat(self, "Ba tiêu chí ta vừa xem đều đo vòng bên trái.",
             FadeIn(n1), run_time=0.8)
        beat(self, "Còn thứ ta cần lại nằm ở vòng bên phải.",
             FadeIn(n2), Indicate(c2, color=C_LLM, scale_factor=1.06), run_time=1.3)

        self.play(FadeOut(VGroup(c1, c2, lens, n1, n2)), run_time=0.6)
        cost_inner = txt("The gain must be large enough to pay for that call.",
                         size=22, color=INK)
        cost = VGroup(panel(cost_inner, buff=0.3), cost_inner).shift(DOWN * 0.5)
        beat(self, "Và còn một yếu tố nữa: chi phí.", FadeIn(cost), run_time=0.8)
        beat(self, "nót đáng định tuyến không chỉ vì gờ nờ nờ làm chưa tốt.")
        beat(self, "Mà vì lờ lờ mờ phải cải thiện đủ nhiều để bù lại giá của lời gọi đó.")

        # --- trả lời câu hỏi thứ ba đã đặt ở S2_01 -------------------------------
        self.clear_scene()
        punch = VGroup(
            txt("GLANCE keeps all three signals, as INPUTS to a router.",
                size=23, color=INK),
            txt("What it drops: letting any single one make the DECISION.",
                size=23, color=C_BAD, weight=BOLD),
        ).arrange(DOWN, buff=0.26)

        beat(self, "Vậy quay lại câu hỏi ban đầu: gờ lans kế thừa được gì từ ba công trình này?")
        beat(self, "Nó giữ lại cả ba tín hiệu, nhưng chỉ dùng làm đầu vào cho một bộ định tuyến.",
             Write(punch), run_time=1.8)
        beat(self, "Và bỏ hẳn cách để một tín hiệu đơn lẻ tự quyết định.")


# ===========================================================================
class S2_13_Bridge(GlanceScene):
    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()
        line1 = txt("Hand-picked heuristics are unstable.", size=28, color=INK)
        line2 = txt("So which signal is the right one?", size=28, color=ACCENT, weight=BOLD)
        grp = VGroup(line1, line2).arrange(DOWN, buff=0.32)

        # Một nhịp lặng trước khi vào câu cầu nối: scene trước vừa dứt, nói ngay
        # nghe như bị chèn. Chỉ chèn khoảng lặng ở ĐẦU scene, không đụng lời thoại
        # (câu cầu nối đã chốt trong plan.md, đọc y nguyên).
        self.wait(0.7)
        beat(self, "Heuristic thủ công không ổn định.", Write(line1), run_time=1.3)
        beat(self, "Vậy tín hiệu nào mới đúng?", Write(line2), run_time=1.3)
        self.wait(0.8)
        self.play(FadeOut(grp), run_time=0.8)
