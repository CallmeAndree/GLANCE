import sys
import os
from pathlib import Path

# Add project root to sys.path
project_root = Path(r"d:\DAI_HOC\NAM_3\SEM 3\Mining graph data\GIT VIDEO\GLANCE").resolve()
sys.path.insert(0, str(project_root))

from manim import *
import ast

def find_captions():
    code = Path(project_root / "sections" / "s1_trucmai" / "task1_glance_rebuilt.py").read_text(encoding="utf-8")
    tree = ast.parse(code)
    captions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and node.func.attr == "narrated_caption":
                arg = node.args[0]
                if isinstance(arg, ast.List):
                    for elt in arg.elts:
                        if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                            captions.append(elt.value)
    return captions

class SubtitleChecker(Scene):
    def construct(self):
        import glance_style as gs
        
        def create_subtitle_box(text, max_width=10.6): 
            label = Text(text, font=gs.FONT_MAIN, font_size=24, color=WHITE, weight="SEMIBOLD", stroke_width=1, stroke_color=BLACK)
            if label.width > max_width:
                raise ValueError(f"exceeds max width {max_width}")
            if "\n" in text:
                raise ValueError(f"contains a line break")
            return True

        captions = find_captions()
        out = [f"Checking {len(captions)} captions..."]
        failed = []
        for c in captions:
            try:
                create_subtitle_box(c)
            except Exception as e:
                failed.append((c, str(e)))
        
        if failed:
            out.append("FAILED CUES:")
            for c, err in failed:
                out.append(f"FAILED: '{c}' -> {err}")
        else:
            out.append("ALL CUES PASSED WIDTH CHECK.")
            
        Path(project_root / "check_subs_out.txt").write_text("\n".join(out), encoding="utf-8")

if __name__ == "__main__":
    SubtitleChecker().construct()
