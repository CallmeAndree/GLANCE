import json
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
    _read_tts_key,
    azure_voice_supports_code_switch,
    ssml_mix,
    strip_ssml,
    validate_azure_voice,
)


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
                endpoint="https://tts.example/v1/audio/speech",
                token="secret-token",
                voice="longkhongphainong",
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
                    "input": "Xin chào.",
                    "voice": "longkhongphainong",
                    "response_format": "mp3",
                },
            )
            self.assertNotIn("secret-token", json.dumps(result))
            self.assertEqual(
                (pathlib.Path(cache_dir) / result["original_audio"]).read_bytes(),
                b"fake-mp3",
            )

    def test_requires_token(self):
        with self.assertRaisesRegex(ValueError, "Thiếu API key"):
            TimedTTSService(endpoint="https://tts.example", token="")


if __name__ == "__main__":
    unittest.main()
