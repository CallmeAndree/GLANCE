"""Gác việc phiên âm lời thoại cho TTS, xem bảng phiên âm trong plan.md.

Test quét **mọi** lời thoại, không chỉ dict `VO`: các section truyền chuỗi trực
tiếp vào `voiceover(text=...)`, `narrated_caption(...)` hay helper `beat()` cũng
được kiểm. Trước đây chỉ quét `VO` nên s1, s2, s4 lọt hoàn toàn khỏi tầm kiểm.

Toàn bộ nợ phiên âm đã được xử lý. Bất kỳ chuỗi lời thoại nào chứa lại thuật ngữ
chưa phiên âm đều làm test đỏ ngay.
"""

import ast
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_ENGLISH = re.compile(
    r"(?<![\w-])(?:"
    r"LLMs?|GNNs?|GLANCE|MLP(?:\s*Q)?|NCS|GCNII|GCN|TAG|LOGIN|"
    r"Text-Attributed Graph|Graph Mining|Net Correction (?:Score|điểm)|"
    r"local homophily|relative degree|message passing|structural information|"
    r"clustering density|forward pass|hidden state|policy gradient|class label|"
    r"wrong to correct|correct to wrong|one[- ]hop|two[- ]hop|top[- ]?k|"
    r"mini batch|average rank|query rate|low[- ]shot|fine[- ]tune|"
    r"Qwen3(?:-Embed)?-8B|Cora|Pubmed|Arxiv23|Top-3|"
    r"node|neighborhood|routing|router|route(?:d)?|signals?|embedding|"
    r"dropout|estimated (?:local )?homophily|true homophily|"
    r"degree|original features?|score|sigmoid|layer|representation|"
    r"backbone|prediction|pipeline|heterophily|heterophilous|context|paper|graph|class|text|"
    r"density|label|proxy|abstract|rewiring|accuracy|freeze|frozen|baseline|"
    r"features?|enhanced|random|correction|WC|CW|datasets?|loss|prior|ego|"
    r"Refiner|vectors?|softmax|prompts?|batch|encoder|shared|semantic|fused|"
    r"reward|entropy|skip|models?|tokens?|Year|Products|overall|heatmap|"
    r"difficulty|advantage|OOM|scale|Update|Aggregate|animation|linear|ReLU|"
    r"output|head|message|Task|Enhancer|Predictor|compute|budget|policy|Gain|"
    r"refine(?:d)?|hop|K"
    r")(?![\w-])",
    re.IGNORECASE,
)

# Tên bài báo được nhóm chốt đọc code-switch nguyên cụm này. Chỉ miễn đúng cụm,
# còn từ ``context`` đứng ở nơi khác vẫn bị gác như trước.
ALLOWED_SPOKEN_ENGLISH = (
    re.compile(r"\bgờ lans for context\b", re.IGNORECASE),
)

RAW_DECIMAL = re.compile(r"(?<!\w)[+-]?\d+\.\d+(?!\w)")
NUMBER_WORD = r"(?:không|một|hai|ba|bốn|năm|sáu|bảy|tám|chín|mười|mươi)"
DECIMAL_WITH_PHAY = re.compile(
    rf"\b{NUMBER_WORD}\s+phẩy\s+{NUMBER_WORD}\b",
    re.IGNORECASE,
)
RAW_UPPERCASE_SYMBOL = re.compile(r"\b[A-Z]\b")
RAW_SYMBOL_EXPRESSION = re.compile(
    r"\b(?:p|z|h|x|d|f)\s+(?:[A-Za-z]|\d)\b|"
    r"\b(?:z|h|x|d|f)\s+của\s+v\b"
)

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
        guarded_text = text
        for allowed in ALLOWED_SPOKEN_ENGLISH:
            guarded_text = allowed.sub("", guarded_text)
        matches = sorted({m.group(0) for m in FORBIDDEN_ENGLISH.finditer(guarded_text)})
        if matches:
            rel = path.relative_to(REPO_ROOT).as_posix()
            found.setdefault(rel, []).append(f"{label}: {', '.join(matches)}")
    return found


class VoicePronunciationTest(unittest.TestCase):
    def test_no_untranslated_english(self):
        """Mọi lời thoại đều phải tuân thủ bảng phiên âm."""
        found = violations_by_file()
        problems = []
        for rel, items in sorted(found.items()):
            problems.append(f"{rel} ({len(items)} chuỗi):")
            problems.extend(f"    {item}" for item in items)
        self.assertEqual(
            problems, [],
            "Lời thoại còn thuật ngữ chưa phiên âm, xem bảng trong plan.md.\n"
            + "\n".join(problems),
        )

    def test_required_acronym_pronunciations_are_used(self):
        script = " ".join(text.casefold() for _, _, text in voiceover_texts())
        for pronunciation in (
            "lờ lờ mờ",
            "mờ lờ bê kiu",
            "gờ nờ nờ",
            "gờ lans",
            "nót",
        ):
            with self.subTest(pronunciation=pronunciation):
                self.assertIn(pronunciation, script)
        self.assertNotIn("nút", script)

    def test_decimal_pronunciation_uses_cham(self):
        """Số thập phân phải viết thành lời với “chấm” để TTS đọc đúng."""
        problems = []
        for path, label, text in voiceover_texts():
            if RAW_DECIMAL.search(text) or DECIMAL_WITH_PHAY.search(text):
                rel = path.relative_to(REPO_ROOT).as_posix()
                problems.append(f"{rel}: {label}: {text}")
        self.assertEqual(
            problems,
            [],
            "Số thập phân trong lời thoại phải đọc bằng ‘chấm’, ví dụ "
            "0.08 → ‘không chấm không tám’.\n" + "\n".join(problems),
        )

    def test_symbol_letters_are_written_as_spoken_vietnamese(self):
        """Ký hiệu toán trong lời thoại không được để chữ cái thô cho TTS tự đoán."""
        problems = []
        script_parts = []
        for path, label, text in voiceover_texts():
            script_parts.append(text.casefold())
            if RAW_UPPERCASE_SYMBOL.search(text) or RAW_SYMBOL_EXPRESSION.search(text):
                rel = path.relative_to(REPO_ROOT).as_posix()
                problems.append(f"{rel}: {label}: {text}")
        self.assertEqual(
            problems,
            [],
            "Chữ cái trong ký hiệu phải viết theo âm đọc ở plan.md.\n"
            + "\n".join(problems),
        )
        script = " ".join(script_parts)
        self.assertIn("bê hắc phẩy a", script)
        self.assertTrue(
            "dét gờ vê" in script or "dét gờ a" in script,
            "z_G(v) phải đọc là ‘dét gờ vê’; z_G(A) phải đọc là ‘dét gờ a’.",
        )


if __name__ == "__main__":
    unittest.main()
