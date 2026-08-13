"""Guards for the shared visual language of the 3Blue1Brown redesign."""

import pathlib
import sys
import tempfile
import unittest


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import glance_style as gs  # noqa: E402


class ThreeBrownOneBlueStyleTests(unittest.TestCase):
    def test_text_uses_one_monospace_family(self):
        self.assertEqual(gs.FONT_MAIN, gs.FONT_MONO)
        self.assertIn(
            gs.FONT_MAIN,
            {"Menlo", "SF Mono", "DejaVu Sans Mono", "Liberation Mono", "Courier New"},
        )

    def test_llm_and_success_have_distinct_semantic_colors(self):
        self.assertNotEqual(gs.C_LLM.to_hex(), gs.C_GOOD.to_hex())
        self.assertEqual("#A3E635", gs.C_LLM.to_hex().upper())

    def test_named_layout_contract(self):
        self.assertEqual(12.0, gs.SAFE_WIDTH)
        self.assertEqual(12, gs.GRID_COLUMNS)
        self.assertEqual(0.25, gs.BASELINE_STEP)
        self.assertGreater(gs.CHROME_Y, gs.TITLE_Y)
        self.assertLessEqual(gs.BOTTOM_Y, -3.0)
        self.assertEqual(0.10, gs.DIM_OPACITY)

    def test_header_and_source_share_the_top_chrome_row(self):
        header = gs.section_header("5", "Training objective & experiments")
        stamp = gs.source("Table 5, p.9")
        self.assertLess(header.get_left()[0], 0)
        self.assertGreater(stamp.get_right()[0], 0)
        self.assertGreater(header.get_center()[1], gs.TITLE_Y)
        self.assertGreater(stamp.get_center()[1], gs.TITLE_Y)

    def test_numbered_scene_subtitle_is_removed(self):
        header = gs.step_header(2, "Aggregate")
        self.assertLessEqual(header.width, 0.01)
        self.assertLessEqual(header.height, 0.01)

    def test_scene_debug_badge_has_number_but_no_title(self):
        chrome = gs.section_chrome("4", "GLANCE architecture", "15")
        self.assertEqual("15", chrome[1][1].text)
        self.assertNotIn("Router score", str(chrome))

    def test_arrow_snaps_small_accidental_tilt(self):
        arrow = gs.small_arrow([-2, 0.06, 0], [2, -0.06, 0], buff=0)
        self.assertAlmostEqual(arrow.get_start()[1], arrow.get_end()[1], places=6)

    def test_arrow_keeps_meaningful_diagonal(self):
        arrow = gs.small_arrow([-2, -1, 0], [2, 1, 0], buff=0)
        self.assertNotAlmostEqual(arrow.get_start()[1], arrow.get_end()[1], places=6)

    def test_safe_text_caps_width(self):
        label = gs.safe_text("W" * 200, max_width=5.0)
        self.assertLessEqual(label.width, 5.0 + 1e-6)

    def test_multiline_is_built_as_centered_rows(self):
        label = gs.safe_multiline("first line", "second line")
        self.assertEqual(2, len(label))
        self.assertAlmostEqual(label[0].get_center()[0], label[1].get_center()[0], places=6)

    def test_silent_service_creates_offline_timing_audio(self):
        with tempfile.TemporaryDirectory() as cache_dir:
            service = gs.SilentService(cache_dir=cache_dir)
            result = service.generate_from_text("one two three")
            audio = pathlib.Path(cache_dir) / result["original_audio"]
            self.assertTrue(audio.is_file())
            self.assertEqual(".wav", audio.suffix)


if __name__ == "__main__":
    unittest.main()
