import json
import os
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch

# Cho phép import glance_style.py ở thư mục gốc repo, giống các file section.
# Nhờ vậy chạy được cả `python tests/test_voice_code_switch.py` lẫn
# `python -m unittest discover -s tests -t .` mà không cần đặt PYTHONPATH.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from glance_style import (  # noqa: E402
    TimedTTSService,
    _load_env,
    _read_tts_key,
    azure_voice_supports_code_switch,
    ssml_mix,
    strip_ssml,
    validate_azure_voice,
)


class EnvironmentLoadingTest(unittest.TestCase):
    def test_reads_dotenv_as_utf8(self):
        with (
            patch("glance_style.pathlib.Path.exists", return_value=True),
            patch(
                "glance_style.pathlib.Path.read_text",
                return_value="GLANCE_TEST_UTF8=ok\n",
            ) as read_text,
            patch.dict(os.environ, {}, clear=False),
        ):
            _load_env()

            read_text.assert_called_once_with(encoding="utf-8")
            self.assertEqual(os.environ["GLANCE_TEST_UTF8"], "ok")


class FakeResponse:
    def __init__(self, audio):
        self.audio = audio

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self.audio


class VoiceCodeSwitchTest(unittest.TestCase):
    def test_mixed_vietnamese_english_ssml(self):
        text = "GLANCE dùng local homophily trong GNN pipeline."

        mixed = ssml_mix(text)

        self.assertIn('<lang xml:lang="en-US">Glance</lang>', mixed)
        self.assertIn('<lang xml:lang="en-US">local homophily</lang>', mixed)
        self.assertIn('<lang xml:lang="en-US">G N N</lang>', mixed)
        self.assertIn('<lang xml:lang="en-US">pipeline</lang>', mixed)
        self.assertNotIn("<", strip_ssml(mixed))

    def test_escapes_plain_text_for_ssml(self):
        mixed = ssml_mix("GNN nhanh hơn A & B.")

        self.assertIn("A &amp; B", mixed)

    def test_supported_multilingual_voices(self):
        self.assertTrue(
            azure_voice_supports_code_switch("en-US-AvaMultilingualNeural")
        )
        self.assertTrue(
            azure_voice_supports_code_switch("en-US-Andrew:DragonHDLatestNeural")
        )
        self.assertFalse(
            azure_voice_supports_code_switch("vi-VN-HoaiMyNeural")
        )

    def test_rejects_multilingual_voices_without_vietnamese(self):
        for voice in (
            "en-US-JennyMultilingualNeural",
            "en-US-RyanMultilingualNeural",
        ):
            with self.subTest(voice=voice):
                with self.assertRaisesRegex(ValueError, "không hỗ trợ vi-VN"):
                    validate_azure_voice(voice)


class TimedTTSServiceTest(unittest.TestCase):
    def test_reads_bearer_key_from_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            key_file = pathlib.Path(temp_dir) / "api.key"
            key_file.write_text("secret-token\n", encoding="utf-8")

            self.assertEqual(_read_tts_key(key_file), "secret-token")

    def test_generates_mp3_without_putting_token_in_cache_metadata(self):
        with tempfile.TemporaryDirectory() as cache_dir:
            service = TimedTTSService(
                endpoint="https://tts.example/api/tts",
                token="secret-token",
                cache_dir=cache_dir,
            )
            with patch(
                "glance_style.urlrequest.urlopen",
                return_value=FakeResponse(b"fake-mp3"),
            ) as urlopen:
                result = service.generate_from_text("Xin chào.")

            request = urlopen.call_args.args[0]
            self.assertEqual(request.get_header("Authorization"), "Bearer secret-token")
            self.assertEqual(
                json.loads(request.data.decode("utf-8")),
                {
                    "text": "Xin chào.",
                    "format": "mp3",
                    "temperature": 0.45,
                    "top_k": 30,
                    "top_p": 0.85,
                    "speed": 1.15,
                },
            )
            self.assertNotIn("secret-token", json.dumps(result))
            self.assertEqual(
                (pathlib.Path(cache_dir) / result["original_audio"]).read_bytes(),
                b"fake-mp3",
            )

    def test_wrap_reuses_cache_without_duplicate_entries(self):
        with tempfile.TemporaryDirectory() as cache_dir:
            service = TimedTTSService(
                endpoint="https://tts.example/api/tts",
                token="secret-token",
                cache_dir=cache_dir,
            )
            with patch(
                "glance_style.urlrequest.urlopen",
                return_value=FakeResponse(b"fake-mp3"),
            ) as urlopen:
                first = service._wrap_generate_from_text("Xin chào.")
                second = service._wrap_generate_from_text("Xin chào.")

            cache = json.loads(
                (pathlib.Path(cache_dir) / "cache.json").read_text(encoding="utf-8")
            )
            self.assertEqual(urlopen.call_count, 1)
            self.assertEqual(len(cache), 1)
            self.assertEqual(first["original_audio"], second["original_audio"])

    def test_cache_survives_endpoint_change(self):
        """Đổi tunnel không được làm hỏng cache.

        Server TTS chạy sau tunnel tạm nên URL đổi mỗi lần khởi động lại. Trước
        đây endpoint nằm trong khoá cache, nên mỗi lần đổi URL là toàn bộ audio
        bị sinh lại — cache từng vỡ thành bốn mảnh theo bốn URL khác nhau.
        """
        with tempfile.TemporaryDirectory() as cache_dir:
            first_service = TimedTTSService(
                endpoint="https://tunnel-cu.example/api/tts",
                token="secret-token",
                cache_dir=cache_dir,
            )
            with patch(
                "glance_style.urlrequest.urlopen",
                return_value=FakeResponse(b"fake-mp3"),
            ) as urlopen:
                first = first_service._wrap_generate_from_text("Xin chào.")
            self.assertEqual(urlopen.call_count, 1)

            moved_service = TimedTTSService(
                endpoint="https://tunnel-moi.example/api/tts",
                token="secret-token",
                cache_dir=cache_dir,
            )
            with patch(
                "glance_style.urlrequest.urlopen",
                side_effect=AssertionError("đổi endpoint không được gọi lại TTS"),
            ) as urlopen:
                second = moved_service._wrap_generate_from_text("Xin chào.")

            self.assertEqual(urlopen.call_count, 0)
            self.assertEqual(first["original_audio"], second["original_audio"])

    def test_sfx_survives_manim_animation_cache(self):
        """SFX phải được ghi cả khi manim đang tái dùng animation trong cache.

        `Scene.add_sound` mở đầu bằng `if self.renderer.skip_animations: return`,
        mà renderer bật cờ đó mỗi lần lấy animation từ cache. Không vá thì render
        lần hai trở đi SFX biến mất mà không báo lỗi gì — đúng nghĩa hỏng lặng lẽ.
        """
        import glance_style

        class FakeRenderer:
            skip_animations = True

        class FakeScene:
            def __init__(self):
                self.renderer = FakeRenderer()
                self.calls = []

            def add_sound(self, path, time_offset=0, gain=None, **kwargs):
                # Cờ phải đang TẮT lúc add_sound chạy, đúng như manim yêu cầu.
                assert not self.renderer.skip_animations
                self.calls.append((path, time_offset, gain))

        scene = FakeScene()
        with patch.object(glance_style, "SFX_DIR", pathlib.Path(tempfile.mkdtemp())):
            (glance_style.SFX_DIR / "ping.wav").write_bytes(b"RIFF")
            glance_style.play_sfx(scene, "ping", below=10.0)

        self.assertEqual(len(scene.calls), 1)
        self.assertTrue(scene.calls[0][0].endswith("ping.wav"))
        self.assertAlmostEqual(scene.calls[0][2], glance_style.VOICE_MEAN_DBFS - 10.0)
        # Cờ phải được trả lại nguyên trạng cho renderer.
        self.assertTrue(scene.renderer.skip_animations)

    def test_requires_token(self):
        with self.assertRaisesRegex(ValueError, "Thiếu API key"):
            TimedTTSService(endpoint="https://tts.example", token="")


if __name__ == "__main__":
    unittest.main()
