import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Ensure usecases is importable
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from usecases.gemini_client import get_client, send_prompt
from google.genai import errors

class TestGeminiClient(unittest.TestCase):

    @patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"}, clear=True)
    def test_get_client_success(self):
        client = get_client()
        self.assertIsNotNone(client)

    @patch.dict(os.environ, clear=True)
    def test_get_client_missing_key(self):
        with self.assertRaises(ValueError):
            get_client()

    @patch('usecases.gemini_client.get_client')
    def test_send_prompt_success(self, mock_get_client):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Here is your bash command:\n```bash\nkill -9 1234\n```"
        mock_client.models.generate_content.return_value = mock_response
        mock_get_client.return_value = mock_client

        response = send_prompt("Terminate process 1234")
        self.assertEqual(response, "Here is your bash command:\n```bash\nkill -9 1234\n```")
        mock_client.models.generate_content.assert_called_once()

    @patch('usecases.gemini_client.get_client')
    def test_send_prompt_with_context(self, mock_get_client):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Got it."
        mock_client.models.generate_content.return_value = mock_response
        mock_get_client.return_value = mock_client

        context = [{"role": "user", "parts": "Hello"}]
        response = send_prompt("Hello again", context=context)
        self.assertEqual(response, "Got it.")

    @patch('usecases.gemini_client.get_client')
    def test_send_prompt_auth_failure(self, mock_get_client):
        mock_client = MagicMock()

        # Create a mock API error correctly
        mock_error = errors.APIError("Invalid API key", {})
        mock_client.models.generate_content.side_effect = mock_error
        mock_get_client.return_value = mock_client

        with self.assertRaises(errors.APIError):
            send_prompt("Test")

if __name__ == '__main__':
    unittest.main()
