"""Guard the video's English-on-screen / Vietnamese-voice split."""

import ast
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SECTION_FILES = sorted((ROOT / "sections").glob("s[1-5]_*/*.py"))

# These helpers create text that is actually visible in the rendered frame.
VISUAL_CALLS = {
    "Text",
    "bar_chart",
    "caption",
    "create_text_document",
    "heading",
    "labeled_box",
    "line_chart",
    "metric_card",
    "mono",
    "numbered_row",
    "pill",
    "pipeline",
    "source",
    "t",
    "text_chip",
    "title_card",
    "txt",
}

# Deliberately excludes mathematical glyphs such as ŷ, ĥ, π, β and superscripts.
VIETNAMESE_LETTERS = set(
    "ăâđêôơưĂÂĐÊÔƠƯ"
    "àáảãạằắẳẵặầấẩẫậ"
    "èéẻẽẹềếểễệ"
    "ìíỉĩị"
    "òóỏõọồốổỗộờớởỡợ"
    "ùúủũụừứửữự"
    "ỳýỷỹỵ"
    "ÀÁẢÃẠẰẮẲẴẶẦẤẨẪẬ"
    "ÈÉẺẼẸỀẾỂỄỆ"
    "ÌÍỈĨỊ"
    "ÒÓỎÕỌỒỐỔỖỘỜỚỞỠỢ"
    "ÙÚỦŨỤỪỨỮỬỰ"
    "ỲÝỶỸỴ"
)


def _call_name(node):
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    return getattr(node.func, "id", "")


def _string_constants(node):
    for child in ast.walk(node):
        if isinstance(child, ast.Constant) and isinstance(child.value, str):
            yield child


def _contains_vietnamese(text):
    return any(char in VIETNAMESE_LETTERS for char in text)


class VisualLanguageTests(unittest.TestCase):
    def test_visible_scene_text_is_english(self):
        failures = []
        for path in SECTION_FILES:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call) or _call_name(node) not in VISUAL_CALLS:
                    continue
                values = [*node.args, *(kw.value for kw in node.keywords)]
                for value in values:
                    for string in _string_constants(value):
                        if _contains_vietnamese(string.value):
                            failures.append(
                                f"{path.relative_to(ROOT)}:{string.lineno}: {string.value!r}"
                            )
        self.assertEqual([], failures, "Vietnamese text found in visual helpers:\n" + "\n".join(failures))

    def test_reusable_scene_labels_are_english(self):
        failures = []
        for path in SECTION_FILES:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in tree.body:
                if not isinstance(node, ast.Assign):
                    continue
                names = [target.id for target in node.targets if isinstance(target, ast.Name)]
                if not any(name == "SECTION_NAME" or name.startswith("SRC_") for name in names):
                    continue
                for string in _string_constants(node.value):
                    if _contains_vietnamese(string.value):
                        failures.append(
                            f"{path.relative_to(ROOT)}:{string.lineno}: {string.value!r}"
                        )
        self.assertEqual([], failures, "Vietnamese reusable labels found:\n" + "\n".join(failures))

    def test_source_prefix_is_english(self):
        style = (ROOT / "glance_style.py").read_text(encoding="utf-8")
        self.assertIn('caption(f"Source: {ref}")', style)
        self.assertNotIn('caption(f"Nguồn: {ref}")', style)


if __name__ == "__main__":
    unittest.main()
