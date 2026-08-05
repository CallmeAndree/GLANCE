"""TEMPLATE — copy file này vào folder của bạn, đừng sửa trực tiếp ở đây.

    cp sections/_template.py sections/s3_nhutanh/s3_nhutanh.py

Sau đó đổi SECTION / SECTION_NAME / OWNER và bắt đầu viết scene của mình.
Đọc TASK.md trong folder của bạn để biết phải trình bày nội dung gì.

Render thử:
    conda activate graphdm
    manim -ql sections/<folder>/<file>.py -a          # render cả section
    manim -ql sections/<folder>/<file>.py S3_01_Title # render 1 scene
"""

import pathlib
import sys

# Cho phép import glance_style.py ở thư mục gốc repo.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from glance_style import *  # noqa: E402,F403

SECTION = "X"                 # "0" | "1" | ... | "5"
SECTION_NAME = "Tên section"  # hiện ở banner góc trên trái
OWNER = "Tên bạn"
ACCENT = SECTION_COLORS.get(SECTION, C_HIGHLIGHT)

# Lời thuyết minh gom một chỗ cho dễ sửa và dễ duyệt.
# Viết theo cách ĐỌC LÊN, không theo cách viết công thức:
#   "h_v"  ->  "h của v"        "3/4"  ->  "ba phần tư"
#   "0.75" ->  "không phẩy bảy lăm"    "N(v)" -> "tập hàng xóm của v"
VO = {
    "intro": "Câu thuyết minh mở đầu.",
    "point": "Câu thuyết minh cho nhịp thứ hai.",
}


class SX_01_Title(GlanceScene):
    """Title card mở section. Giữ nguyên cấu trúc này cho đồng bộ cả video."""

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        card = title_card(
            f"{SECTION} — {SECTION_NAME}",
            "Một dòng tóm tắt section",
            OWNER,
            accent=ACCENT,
        )
        with self.voiceover(text=VO["intro"]):
            self.play(FadeIn(card, shift=UP * 0.3), run_time=1.2)
        self.play(FadeOut(card), run_time=0.6)


class SX_02_Content(GlanceScene):
    """Scene nội dung. Copy class này ra nhiều scene: SX_03_, SX_04_, ...

    Quy ước đặt tên: S<số section>_<số thứ tự 2 chữ số>_<TênNgắn>.
    build.sh ghép video theo đúng thứ tự class khai báo trong file.
    """

    section, section_name = SECTION, SECTION_NAME

    def construct(self):
        self.banner()  # banner section góc trên trái

        head = heading("Tiêu đề scene", color=ACCENT).to_edge(UP, buff=0.85)
        graph = demo_tag().scale(0.85).shift(LEFT * 3.2 + DOWN * 0.4)
        points = bullets(["Ý thứ nhất", "Ý thứ hai"],
                         size=21, dot_color=ACCENT, width=5.5).to_edge(RIGHT, buff=0.9)

        # Mọi animation nằm trong khối thuyết minh. Khối tự chờ nốt phần audio
        # còn thừa, nên không cần canh run_time cho khớp giọng đọc.
        with self.voiceover(text=VO["intro"]):
            self.play(Write(head), run_time=1.2)
            self.play(Create(graph.edges),
                      LaggedStart(*[GrowFromCenter(d) for d in graph.nodes.values()],
                                  lag_ratio=0.06),
                      run_time=1.4)

        with self.voiceover(text=VO["point"]) as tracker:
            # Cần một animation kéo dài đúng bằng câu nói thì dùng tracker:
            self.play(FadeIn(points, shift=LEFT * 0.2), run_time=min(1.0, tracker.duration))

        # Mọi số liệu trích từ paper phải có stamp nguồn.
        self.add(source("§X, tr.Y"))
        self.wait(1.0)


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
#   line_chart(series, x_labels) biểu đồ đường nhiều series
#
# Trên GlanceScene:
#   self.banner()                banner section
#   self.voiceover(text=...)     khối thuyết minh (tracker.duration = độ dài audio)
#   self.say("...")              nhịp chỉ có lời đọc, không animation
#   self.pad_to(t)               chờ tới mốc giây t tính từ đầu scene
#   self.clear_scene(keep=(...)) xoá sạch trừ vài mobject
#
# Màu: C_GNN, C_LLM, C_ROUTER, C_GOOD, C_BAD, C_EDGE, C_HIGHLIGHT, INK, MUTED
# ---------------------------------------------------------------------------
