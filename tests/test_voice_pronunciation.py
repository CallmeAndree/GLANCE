"""Gác việc phiên âm lời thoại cho TTS, xem bảng phiên âm trong plan.md.

Test quét **mọi** lời thoại, không chỉ dict `VO`: các section truyền chuỗi trực
tiếp vào `voiceover(text=...)`, `narrated_caption(...)` hay helper `beat()` cũng
được kiểm. Trước đây chỉ quét `VO` nên s1, s2, s4 lọt hoàn toàn khỏi tầm kiểm.

Repo còn nợ phiên âm ở ba file đó. Thay vì để CI đỏ và khoá cả nhóm, số nợ được
ghi trong BASELINE dưới đây và siết dần:

  * file chưa có trong BASELINE mà xuất hiện vi phạm  -> fail
  * file trong BASELINE mà vi phạm TĂNG               -> fail
  * file trong BASELINE mà vi phạm GIẢM               -> fail, kèm số mới để
    cập nhật, để con số nợ ghi trong repo luôn đúng sự thật

Mục tiêu là mọi dòng BASELINE về 0 rồi xoá hẳn cả BASELINE.
"""

import ast
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_ENGLISH = re.compile(
    r"\b(?:LLMs?|GNNs?|GLANCE|MLP\s*Q|NCS|GCNII|node|neighborhood|"
    r"local homophily|relative degree|message passing|routing|router|signals?|"
    r"embedding|uncertainty|dropout|estimated (?:local )?homophily|"
    r"true homophily|heuristics?|degree|original features?|score|sigmoid|"
    r"top k|mini batch|layer|representation|backbone|prediction|pipeline|"
    r"Text-Attributed Graph|heterophily|context)\b",
    re.IGNORECASE,
)

# Số CHUỖI lời thoại còn vi phạm (không phải số lần xuất hiện thuật ngữ),
# đo tại thời điểm mở rộng test. Chỉ được giảm. Xem mục B2 trong bản duyệt.
BASELINE = {
    "sections/s1_trucmai/s1_trucmai.py": 29,
    "sections/s2_hoangphan/s2_hoangphan.py": 118,
    "sections/s4_trannguyen/s4_trannguyen.py": 91,
}

# Hàm nhận lời thoại ở đối số đầu tiên.
_TEXT_FIRST_ARG = {"narrated_caption", "say"}
# Helper riêng của s2: beat(scene, "lời thoại", *anims)
_TEXT_SECOND_ARG = {"beat"}


def _strings_in(node):
    """Mọi chuỗi hằng trong node: chuỗi đơn, hoặc list/tuple chuỗi."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [node.value]
    if isinstance(node, (ast.List, ast.Tuple)):
        out = []
        for element in node.elts:
            out.extend(_strings_in(element))
        return out
    if isinstance(node, ast.JoinedStr):  # f-string: ghép các phần hằng lại
        return ["".join(
            part.value for part in node.values
            if isinstance(part, ast.Constant) and isinstance(part.value, str)
        )]
    return []


def _vo_dict_texts(tree):
    """Lời thoại gom trong dict VO."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not any(
            isinstance(target, ast.Name) and target.id == "VO"
            for target in node.targets
        ):
            continue
        if not isinstance(node.value, ast.Dict):
            continue
        for key, value in zip(node.value.keys, node.value.values):
            if (
                isinstance(key, ast.Constant)
                and isinstance(key.value, str)
                and isinstance(value, ast.Constant)
                and isinstance(value.value, str)
            ):
                yield f"VO[{key.value!r}]", value.value


def _inline_texts(tree):
    """Lời thoại truyền trực tiếp vào lời gọi hàm, không qua dict VO."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")

        texts = []
        if name == "voiceover":
            for keyword in node.keywords:
                if keyword.arg == "text":
                    texts.extend(_strings_in(keyword.value))
            if not texts and node.args:
                texts.extend(_strings_in(node.args[0]))
        elif name in _TEXT_FIRST_ARG:
            for keyword in node.keywords:
                if keyword.arg in ("text", "text_segments"):
                    texts.extend(_strings_in(keyword.value))
            if not texts and node.args:
                texts.extend(_strings_in(node.args[0]))
        elif name in _TEXT_SECOND_ARG and len(node.args) >= 2:
            texts.extend(_strings_in(node.args[1]))

        for text in texts:
            if text.strip():
                yield f"{name}() dòng {node.lineno}", text


def voiceover_texts():
    """Mọi lời thoại trong sections/, kèm đường dẫn và nhãn vị trí."""
    for path in sorted((REPO_ROOT / "sections").glob("*/*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for label, text in _vo_dict_texts(tree):
            yield path, label, text
        for label, text in _inline_texts(tree):
            yield path, label, text


def violations_by_file():
    """{đường dẫn tương đối: [mô tả vi phạm, ...]}"""
    found = {}
    for path, label, text in voiceover_texts():
        matches = sorted({m.group(0) for m in FORBIDDEN_ENGLISH.finditer(text)})
        if matches:
            rel = path.relative_to(REPO_ROOT).as_posix()
            found.setdefault(rel, []).append(f"{label}: {', '.join(matches)}")
    return found


class VoicePronunciationTest(unittest.TestCase):
    def test_no_untranslated_english_in_unlisted_files(self):
        """File chưa có trong BASELINE thì không được có vi phạm nào."""
        found = violations_by_file()
        problems = []
        for rel, items in sorted(found.items()):
            if rel in BASELINE:
                continue
            problems.append(f"{rel} ({len(items)} chuỗi):")
            problems.extend(f"    {item}" for item in items)
        self.assertEqual(
            problems, [],
            "Lời thoại còn thuật ngữ chưa phiên âm, xem bảng trong plan.md.\n"
            + "\n".join(problems),
        )

    def test_baseline_files_only_improve(self):
        """Nợ phiên âm ở các file đã biết chỉ được giảm, và số phải đúng."""
        found = violations_by_file()
        problems = []
        for rel, allowed in sorted(BASELINE.items()):
            actual = len(found.get(rel, []))
            if actual > allowed:
                problems.append(
                    f"{rel}: {actual} chuỗi vi phạm, nhiều hơn mức đã ghi {allowed}. "
                    "Lời thoại mới phải phiên âm theo plan.md."
                )
            elif actual < allowed:
                problems.append(
                    f"{rel}: còn {actual} chuỗi, đã ít hơn mức ghi {allowed}. "
                    f"Sửa BASELINE trong file test này xuống {actual}"
                    + (" rồi xoá hẳn dòng đó." if actual == 0 else ".")
                )
        self.assertEqual(problems, [], "\n".join(problems))

    def test_required_acronym_pronunciations_are_used(self):
        script = " ".join(text.casefold() for _, _, text in voiceover_texts())
        for pronunciation in (
            "eo eo em",
            "em eo pi khiu",
            "gi en en",
            "gờ lans",
            "nót",
        ):
            with self.subTest(pronunciation=pronunciation):
                self.assertIn(pronunciation, script)
        self.assertNotIn("nút", script)


if __name__ == "__main__":
    unittest.main()
