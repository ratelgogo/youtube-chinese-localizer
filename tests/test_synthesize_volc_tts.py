import json
import os
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.localize_video import synthesize_volc_tts


class TestSynthesizeVolcTTS(unittest.TestCase):

    def setUp(self):
        os.environ["VOLCENGINE_TTS_API_KEY"] = "test-api-key"
        os.environ["VOLCENGINE_TTS_RESOURCE_ID"] = "volc.speech.mt"
        os.environ["VOLCENGINE_TTS_APP_ID"] = "test-app-id"

    @patch("urllib.request.urlopen")
    def test_successful_tts_request(self, mock_urlopen):
        mock_response = MagicMock()
        audio_data = "SGVsbG8gd29ybGQ="
        response_text = json.dumps({"data": audio_data, "code": 0, "message": "success"})
        mock_response.read.return_value = response_text.encode("utf-8")
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        result = synthesize_volc_tts(
            "Hello world",
            speaker="zh_male_beijingxiaoye_emo_v2_mars_bigtts",
            response_format="wav",
            sample_rate=24000,
        )

        self.assertIsInstance(result, bytes)
        self.assertEqual(result, b"Hello world")

    @patch("urllib.request.urlopen")
    def test_multiple_audio_chunks(self, mock_urlopen):
        mock_response = MagicMock()
        response_lines = [
            json.dumps({"data": "Y2h1bmsx", "code": 0}),
            json.dumps({"data": "Y2h1bmsy", "code": 0}),
            json.dumps({"data": "Y2h1bmsz", "code": 0}),
        ]
        response_text = "\n".join(response_lines)
        mock_response.read.return_value = response_text.encode("utf-8")
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        result = synthesize_volc_tts(
            "Test text",
            speaker="zh_male",
            response_format="mp3",
            sample_rate=16000,
        )

        self.assertIsInstance(result, bytes)
        self.assertEqual(result, b"chunk1chunk2chunk3")

    @patch("urllib.request.urlopen")
    def test_http_error_raises_exception(self, mock_urlopen):
        mock_response = MagicMock()
        error_body = json.dumps({"code": 1001, "message": "Invalid API key"})
        mock_response.read.return_value = error_body.encode("utf-8")

        http_error = urllib.error.HTTPError(
            url="https://openspeech.bytedance.com/api/v3/tts/unidirectional",
            code=401,
            msg="Unauthorized",
            hdrs={},
            fp=mock_response,
        )
        mock_urlopen.side_effect = http_error

        with self.assertRaises(SystemExit) as context:
            synthesize_volc_tts(
                "Test text",
                speaker="zh_male",
                response_format="wav",
                sample_rate=24000,
            )
        self.assertIn("401", str(context.exception))
        self.assertIn("Invalid API key", str(context.exception))

    @patch("urllib.request.urlopen")
    def test_missing_audio_chunks_raises_exception(self, mock_urlopen):
        mock_response = MagicMock()
        response_text = json.dumps({"code": 0, "message": "success"})
        mock_response.read.return_value = response_text.encode("utf-8")
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        with self.assertRaises(SystemExit) as context:
            synthesize_volc_tts(
                "Test text",
                speaker="zh_male",
                response_format="wav",
                sample_rate=24000,
            )

        self.assertIn("did not contain audio chunks", str(context.exception))

    @patch("urllib.request.urlopen")
    def test_error_code_raises_exception(self, mock_urlopen):
        mock_response = MagicMock()
        response_text = json.dumps({
            "data": "c29tZV9hdWRpb19kYXRh",
            "code": 1001,
            "message": "Server error"
        })
        mock_response.read.return_value = response_text.encode("utf-8")
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        with self.assertRaises(SystemExit) as context:
            synthesize_volc_tts(
                "Test text",
                speaker="zh_male",
                response_format="wav",
                sample_rate=24000,
            )

        self.assertIn("failed", str(context.exception))
        self.assertIn("1001", str(context.exception))
    @patch("urllib.request.urlopen")
    def test_error_code_without_audio_surfaces_upstream_error(self, mock_urlopen):
        mock_response = MagicMock()
        response_text = json.dumps({"code": 401, "message": "Unauthorized"})
        mock_response.read.return_value = response_text.encode("utf-8")
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        with self.assertRaises(SystemExit) as context:
            synthesize_volc_tts(
                "Test text",
                speaker="zh_male",
                response_format="wav",
                sample_rate=24000,
            )

        self.assertIn("Volc TTS failed", str(context.exception))
        self.assertIn("401", str(context.exception))
        self.assertNotIn("did not contain audio chunks", str(context.exception))

    @patch("urllib.request.urlopen")
    def test_nested_audio_payload_is_supported(self, mock_urlopen):
        mock_response = MagicMock()
        response_text = json.dumps(
            {"data": {"audio": "SGVsbG8gd29ybGQ="}, "code": 0, "message": "success"}
        )
        mock_response.read.return_value = response_text.encode("utf-8")
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        result = synthesize_volc_tts(
            "Test text",
            speaker="zh_male",
            response_format="wav",
            sample_rate=24000,
        )

        self.assertEqual(result, b"Hello world")

    def test_missing_api_key_raises_exception(self):
        for key in (
            "VOLCENGINE_TTS_API_KEY",
            "VOLCENGINE_TTS_APP_ID",
            "VOLCENGINE_TTS_ACCESS_KEY",
        ):
            if key in os.environ:
                del os.environ[key]

        with self.assertRaises(SystemExit) as context:
            synthesize_volc_tts(
                "Test text",
                speaker="zh_male",
                response_format="wav",
                sample_rate=24000,
            )

        self.assertIn("TTS credentials missing", str(context.exception))


if __name__ == "__main__":
    unittest.main()