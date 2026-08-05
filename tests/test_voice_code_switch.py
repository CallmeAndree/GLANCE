import base64
import json
import pathlib
import tempfile
import unittest
from unittest.mock import patch

from glance_style import (
    TimedTTSService,
    azure_voice_supports_code_switch,
    ssml_mix,
    strip_ssml,
    validate_azure_voice,
)


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


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
    def test_generates_mp3_without_putting_token_in_cache_metadata(self):
        payload = {
            "audio_base64": base64.b64encode(b"fake-mp3").decode("ascii"),
            "duration": 1.25,
            "format": "mp3",
            "sample_rate": 24000,
            "segments": [{"text": "Xin chào.", "start": 0.0, "end": 1.25}],
        }
        with tempfile.TemporaryDirectory() as cache_dir:
            service = TimedTTSService(
                endpoint="https://tts.example/api/tts/timed",
                token="secret-token",
                cache_dir=cache_dir,
            )
            with patch(
                "glance_style.urlrequest.urlopen",
                return_value=FakeResponse(payload),
            ) as urlopen:
                result = service.generate_from_text("Xin chào.")

            request = urlopen.call_args.args[0]
            self.assertEqual(request.get_header("Authorization"), "Bearer secret-token")
            self.assertEqual(
                json.loads(request.data.decode("utf-8")),
                {"text": "Xin chào.", "format": "mp3"},
            )
            self.assertNotIn("secret-token", json.dumps(result))
            self.assertEqual(result["segments"], payload["segments"])
            self.assertEqual(
                (pathlib.Path(cache_dir) / result["original_audio"]).read_bytes(),
                b"fake-mp3",
            )

    def test_requires_token(self):
        with self.assertRaisesRegex(ValueError, "GLANCE_TIMED_TTS_TOKEN"):
            TimedTTSService(endpoint="https://tts.example", token="")


if __name__ == "__main__":
    unittest.main()
