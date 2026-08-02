"""Section 0.1 — Related Work.  Owner: Hoàng Phan.

Nguồn trong paper: §2 (tr.2–3) + Phụ lục A (tr.14)
Nhiệm vụ chi tiết: sections/s0_background/TASK.md

Render:  manim -ql sections/s0_background/s0a_related_work.py -a
"""

import pathlib
import sys

# Cho phép import glance_style.py ở thư mục gốc repo.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from glance_style import *  # noqa: E402,F403

SECTION = "0"
SECTION_NAME = "Related Work"
OWNER = "Hoàng Phan"
ACCENT = SECTION_COLORS.get(SECTION, C_HIGHLIGHT)


class S0A_01_Title(GlanceScene):
    """Title card mở section. Giữ nguyên cấu trúc này cho đồng bộ cả video."""

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        card = title_card(
            f"{SECTION} — {SECTION_NAME}",
            "Một dòng tóm tắt section",
            OWNER,
            accent=ACCENT,
        )
        self.play(FadeIn(card, shift=UP * 0.3), run_time=1.2,
                  subcaption="Câu thuyết minh mở đầu.", subcaption_duration=3)
        self.wait(1.5)
        self.play(FadeOut(card), run_time=0.6)


class S0A_02_Content(GlanceScene):
    """Scene nội dung. Copy class này ra nhiều scene: S0A_03_, S0A_04_, ...

    Quy ước đặt tên: S<số section>_<số thứ tự 2 chữ số>_<TênNgắn>.
    build.sh ghép video theo đúng thứ tự class khai báo trong file.
    """

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()  # banner section góc trên trái

        head = heading("Tiêu đề scene", color=ACCENT).to_edge(UP, buff=0.85)
        self.play(Write(head),
                  subcaption="Phụ đề đi kèm — đây cũng là kịch bản thu tiếng.",
                  subcaption_duration=3)

        # --- Ví dụ các helper dùng chung (xoá khi viết nội dung thật) ---
        graph = demo_tag().scale(0.85).shift(LEFT * 3.2 + DOWN * 0.4)
        self.play(Create(graph.edges),
                  LaggedStart(*[GrowFromCenter(d) for d in graph.nodes.values()],
                              lag_ratio=0.06),
                  run_time=1.4)

        points = bullets([
            "Ý thứ nhất",
            "Ý thứ hai",
        ], size=21, dot_color=ACCENT, width=5.5)
        points.to_edge(RIGHT, buff=0.9)
        self.play(FadeIn(points, shift=LEFT * 0.2), run_time=0.9)

        # Mọi số liệu trích từ paper phải có stamp nguồn.
        self.add(source("§X, tr.Y"))
        self.wait(2)

        # Câu cầu nối sang section sau — lấy đúng câu trong plan.md.
        self.clear_scene()
        bridge = txt("Câu dẫn sang section tiếp theo.", size=24, color=MUTED)
        self.play(FadeIn(bridge), subcaption="Câu dẫn sang section tiếp theo.",
                  subcaption_duration=3)
        self.wait(1.5)


# ---------------------------------------------------------------------------
# Nhắc nhanh các helper có sẵn trong glance_style.py — đừng tự chế lại:
#
#   txt(s, size, color)          Text tiếng Việt an toàn
#   heading(s, color)            tiêu đề đậm
#   bullets([...])               danh sách gạch đầu dòng
#   caption(s) / source(ref)     chữ nhỏ / stamp nguồn góc dưới phải
#   title_card(...)              card mở section
#   section_banner(num, name)    banner góc trên trái (GlanceScene.banner())
#   panel(mobj)                  khung bo góc quanh nội dung
#   labeled_box("GNN", C_GNN)    khối model
#   pipeline([(label, color)...]) chuỗi khối + mũi tên
#   check() / cross()            dấu ✓ / ✗
#   tag_graph(edges, pos, labels) đồ thị tuỳ ý
#   demo_tag()                   đồ thị 12 node dùng chung cả video
#   ego_ring(graph, id, hops)    vòng nét đứt quanh ego + hàng xóm
#   text_chip("...")             thẻ text gắn vào node
#   bar_chart(values, labels)    biểu đồ cột (hỗ trợ giá trị âm)
#
# Màu: C_GNN, C_LLM, C_ROUTER, C_GOOD, C_BAD, C_EDGE, C_HIGHLIGHT, INK, MUTED
# ---------------------------------------------------------------------------
