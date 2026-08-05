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


def voiceover_texts():
    """Lấy riêng giá trị chuỗi trong các dict VO, bỏ qua chữ hiển thị trên hình."""
    for path in sorted((REPO_ROOT / "sections").glob("*/*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
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
                if not (
                    isinstance(key, ast.Constant)
                    and isinstance(key.value, str)
                    and isinstance(value, ast.Constant)
                    and isinstance(value.value, str)
                ):
                    continue
                yield path, key.value, value.value


class VoicePronunciationTest(unittest.TestCase):
    def test_voiceover_has_no_untranslated_english_terms(self):
        violations = []
        for path, key, text in voiceover_texts():
            matches = sorted({match.group(0) for match in FORBIDDEN_ENGLISH.finditer(text)})
            if matches:
                violations.append(f"{path.relative_to(REPO_ROOT)}:{key}: {', '.join(matches)}")
        self.assertEqual(violations, [], "\n".join(violations))

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
