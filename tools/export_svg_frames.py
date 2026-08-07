"""Xuất mỗi sub-scene của một (hoặc mọi) scene thành một khung SVG vector.

Một "sub-scene" = trạng thái màn hình ngay sau khi MỘT khối
`with self.voiceover(...)` kết thúc (toàn bộ animation bên trong khối đó đã
chạy xong và đã chờ hết audio, kể cả loop hiện-từng-item hay LaggedStart bên
trong) -- chỉ MỘT khung cho mỗi câu thoại, dù bên trong có bao nhiêu
self.play(). self.play() đứng ngoài mọi khối voiceover (banner, hiệu ứng phụ
như pulse chạy dọc mũi tên...) KHÔNG được chụp riêng nữa -- hiệu ứng của nó
vẫn có mặt trong khung của câu thoại kế tiếp, chỉ là không có khung riêng chỉ
để minh hoạ đúng bước chuyển tiếp đó. Có thêm một khung "chốt" ở cuối
construct() phòng khi có nội dung xuất hiện sau khối voiceover cuối cùng;
khung này bị bỏ nếu trùng hệt khung ngay trước nó.

Kỹ thuật: tái dùng đúng logic vẽ của Manim (camera.capture_mobjects: cùng thứ
tự mobject, cùng phép biến đổi tọa độ, cùng fill/stroke) nhưng đổi bề mặt
Cairo từ ImageSurface (raster) sang SVGSurface (vector). Chữ trong Manim
(Text/txt()) vốn là path do Pango sinh ra chứ không phải raster, nên sửa tay
được luôn cả chữ, không chỉ hình khối.

Manim tự đảo thứ tự R/B khi tô màu (`set_cairo_context_color`) để bù cho
cách nó tự dựng ImageSurface từ mảng numpy thô -- việc bù đó chỉ đúng cho
raster, nên nếu tái dùng nguyên hàm cho SVGSurface thì đỏ/lam sẽ bị hoán đổi.
Script này patch tạm hàm đó để trả lại đúng thứ tự R,G,B khi ghi ra SVG.

Không đổi hành vi render bình thường: script vẫn chạy `scene.render()` y hệt
`manim -ql ...` (kể cả sinh audio thuyết minh), chỉ gắn thêm hook chụp SVG.

    conda activate graphdm
    # một scene:
    python tools/export_svg_frames.py sections/s4_trannguyen/s4_trannguyen.py S4_02_EndToEnd
    # mọi scene trong file (không truyền class_name):
    python tools/export_svg_frames.py sections/s4_trannguyen/s4_trannguyen.py

Output: media/svg_frames/<TênScene>/001.svg, 002.svg, ... theo đúng thứ tự
sub-scene xuất hiện trong construct().
"""

import argparse
import importlib.util
import itertools as it
import re
import sys
from contextlib import contextmanager
from pathlib import Path

import cairo
import numpy as np
from manim import config
from manim.scene.scene import Scene
from manim_voiceover.voiceover_scene import VoiceoverScene

ROOT = Path(__file__).resolve().parents[1]
CLASS_RE = re.compile(r"^class\s+(\w+)\s*\(", re.MULTILINE)


def load_module(py_path: Path):
    module_name = py_path.stem
    spec = importlib.util.spec_from_file_location(module_name, py_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def find_class_names(py_path: Path) -> list[str]:
    return CLASS_RE.findall(py_path.read_text(encoding="utf-8"))


def snapshot(scene: Scene, out_path: Path) -> None:
    cam = scene.camera
    pw, ph = int(cam.pixel_width), int(cam.pixel_height)
    fw, fh, fc = cam.frame_width, cam.frame_height, cam.frame_center

    surface = cairo.SVGSurface(str(out_path), pw, ph)
    ctx = cairo.Context(surface)

    r, g, b = cam.background_color.to_rgb()
    ctx.save()
    ctx.set_source_rgb(r, g, b)
    ctx.paint()
    ctx.restore()

    # Cùng phép biến đổi Manim dùng để map tọa độ scene -> pixel, xem
    # manim/camera/camera.py::get_cairo_context.
    ctx.scale(pw, ph)
    ctx.set_matrix(
        cairo.Matrix(
            pw / fw, 0, 0, -(ph / fh),
            (pw / 2) - fc[0] * (pw / fw),
            (ph / 2) + fc[1] * (ph / fh),
        )
    )

    def straight_order_set_color(inner_ctx, rgbas, vmobject):
        # Bản không đảo R/B của Camera.set_cairo_context_color -- xem
        # docstring đầu file.
        if len(rgbas) == 1:
            inner_ctx.set_source_rgba(*rgbas[0][:3], rgbas[0][3])
        else:
            points = vmobject.get_gradient_start_and_end_points()
            points = cam.transform_points_pre_display(vmobject, points)
            pat = cairo.LinearGradient(*it.chain(*(p[:2] for p in points)))
            offsets = np.linspace(0, 1, len(rgbas))
            for rgba, offset in zip(rgbas, offsets, strict=True):
                pat.add_color_stop_rgba(offset, *rgba[:3], rgba[3])
            inner_ctx.set_source(pat)

    original_get_cairo_context = cam.get_cairo_context
    original_set_color = cam.set_cairo_context_color
    cam.get_cairo_context = lambda pixel_array: ctx
    cam.set_cairo_context_color = straight_order_set_color
    try:
        cam.capture_mobjects(scene.mobjects)
    finally:
        cam.get_cairo_context = original_get_cairo_context
        cam.set_cairo_context_color = original_set_color
    surface.finish()


def render_scene(scene_cls, out_dir: Path) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("*.svg"):
        old.unlink()

    counter = {"n": 0}
    last_bytes = {"data": None}

    def take_snapshot(scene, dedupe=False):
        path = out_dir / f"{counter['n'] + 1:03d}.svg"
        snapshot(scene, path)
        data = path.read_bytes()
        if dedupe and data == last_bytes["data"]:
            path.unlink()
            return
        counter["n"] += 1
        last_bytes["data"] = data

    original_voiceover = VoiceoverScene.voiceover

    @contextmanager
    def patched_voiceover(self, *vo_args, **vo_kwargs):
        with original_voiceover(self, *vo_args, **vo_kwargs) as tracker:
            yield tracker
        take_snapshot(self)

    VoiceoverScene.voiceover = patched_voiceover
    try:
        scene = scene_cls()
        scene.render()
        take_snapshot(scene, dedupe=True)
    finally:
        VoiceoverScene.voiceover = original_voiceover

    return counter["n"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("py_file", help="đường dẫn tới file section, vd sections/s4_trannguyen/s4_trannguyen.py")
    parser.add_argument("class_name", nargs="?", default=None,
                         help="tên class Scene cần xuất; bỏ trống để xuất mọi class trong file")
    parser.add_argument("-q", "--quality", default="low_quality",
                         choices=["low_quality", "medium_quality", "high_quality", "fourk_quality"])
    parser.add_argument("-o", "--out", default=None,
                         help="thư mục gốc để ghi (mặc định media/svg_frames). "
                              "Mỗi lần chạy XOÁ SẠCH *.svg của scene trong thư mục này, "
                              "nên đừng trỏ vào nơi đang giữ bản sửa tay.")
    args = parser.parse_args()

    py_path = Path(args.py_file).resolve()
    sys.path.insert(0, str(py_path.parents[2]))  # cho `from glance_style import *`
    config.quality = args.quality

    out_root = Path(args.out).resolve() if args.out else ROOT / "media" / "svg_frames"
    # svg_edited/ giữ bản sửa tay và nằm ngoài media/ (tức là được git theo dõi);
    # render_scene() xoá sạch *.svg trước khi ghi nên tuyệt đối không trỏ vào đó.
    if out_root.resolve() == (ROOT / "svg_edited").resolve():
        sys.exit("Từ chối ghi đè svg_edited/ — đó là nơi giữ bản sửa tay.")

    class_names = [args.class_name] if args.class_name else find_class_names(py_path)
    module = load_module(py_path)

    for class_name in class_names:
        scene_cls = getattr(module, class_name)
        out_dir = out_root / class_name
        n = render_scene(scene_cls, out_dir)
        print(f"{class_name}: {n} sub-scene -> {out_dir}")


if __name__ == "__main__":
    main()
