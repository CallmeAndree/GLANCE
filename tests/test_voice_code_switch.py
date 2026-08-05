import unittest

from glance_style import (
    azure_voice_supports_code_switch,
    ssml_mix,
    strip_ssml,
    validate_azure_voice,
)


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


if __name__ == "__main__":
    unittest.main()
