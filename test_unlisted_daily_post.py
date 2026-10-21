import os
import unittest
from unittest.mock import patch, MagicMock
import unlisted_daily_post

class TestUnlistedDailyPost(unittest.TestCase):

    @patch.dict(os.environ, {}, clear=True)
    def test_draft_post_missing_api_keys(self):
        with self.assertRaises(RuntimeError) as ctx:
            unlisted_daily_post.draft_post()
        self.assertIn("Missing API Key", str(ctx.exception))

    @patch.dict(os.environ, {"GEMINI_API_KEY": "fake_gemini_key"}, clear=True)
    @patch("requests.post")
    def test_draft_post_gemini_success(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "Gemini generated post."}}]
        }
        mock_post.return_value = mock_resp

        result = unlisted_daily_post.draft_post()
        self.assertEqual(result, "Gemini generated post.")
        self.assertEqual(mock_post.call_count, 1)

    @patch.dict(os.environ, {"OPENROUTER_API_KEY": "fake_openrouter_key"}, clear=True)
    @patch("requests.post")
    def test_draft_post_openrouter_success(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "OpenRouter generated post."}}]
        }
        mock_post.return_value = mock_resp

        result = unlisted_daily_post.draft_post()
        self.assertEqual(result, "OpenRouter generated post.")
        self.assertEqual(mock_post.call_count, 1)

    @patch.dict(os.environ, {"GEMINI_API_KEY": "fake_gemini", "OPENROUTER_API_KEY": "fake_openrouter"}, clear=True)
    @patch("requests.post")
    def test_draft_post_gemini_fail_fallback_to_openrouter(self, mock_post):
        mock_gemini_fail = MagicMock()
        mock_gemini_fail.status_code = 400
        mock_gemini_fail.text = "Bad Request"

        mock_openrouter_success = MagicMock()
        mock_openrouter_success.status_code = 200
        mock_openrouter_success.json.return_value = {
            "choices": [{"message": {"content": "OpenRouter fallback post."}}]
        }

        mock_post.side_effect = [
            mock_gemini_fail, mock_gemini_fail, mock_gemini_fail, # 3 Gemini models fail
            mock_openrouter_success # OpenRouter succeeds
        ]

        result = unlisted_daily_post.draft_post()
        self.assertEqual(result, "OpenRouter fallback post.")

    @patch.dict(os.environ, {"GMAIL_USER": "user@test.com", "GMAIL_APP_PASSWORD": "pass", "TO_EMAILS": "a@test.com, b@test.com"})
    @patch("smtplib.SMTP")
    def test_send_email_success(self, mock_smtp_class):
        mock_smtp = MagicMock()
        mock_smtp_class.return_value.__enter__.return_value = mock_smtp

        result = unlisted_daily_post.send_email("Test content")
        self.assertEqual(result, "ok")
        mock_smtp.starttls.assert_called_once()
        mock_smtp.login.assert_called_once_with("user@test.com", "pass")
        mock_smtp.send_message.assert_called_once()

        sent_msg = mock_smtp.send_message.call_args[0][0]
        self.assertEqual(sent_msg["To"], "a@test.com, b@test.com")
        self.assertEqual(sent_msg["From"], "user@test.com")

if __name__ == "__main__":
    unittest.main()
