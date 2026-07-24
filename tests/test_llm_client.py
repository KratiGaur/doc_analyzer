import os
import unittest
from unittest.mock import patch

from backend.utils import llm_client


class LLMClientSecretTests(unittest.TestCase):
    def test_get_api_key_from_general_streamlit_secret(self):
        fake_secrets = {"general": {"GEMINI_API_KEY": "secret-from-general"}}

        with patch.dict(os.environ, {}, clear=True):
            with patch("streamlit.secrets", fake_secrets):
                self.assertEqual(llm_client._get_api_key(), "secret-from-general")

    def test_get_api_key_from_lowercase_streamlit_secret(self):
        fake_secrets = {"general": {"gemini_api_key": "secret-from-general-lowercase"}}

        with patch.dict(os.environ, {}, clear=True):
            with patch("streamlit.secrets", fake_secrets):
                self.assertEqual(llm_client._get_api_key(), "secret-from-general-lowercase")


if __name__ == "__main__":
    unittest.main()
