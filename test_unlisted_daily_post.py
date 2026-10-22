import os
import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock
import unlisted_daily_post

class TestUnlistedDailyPost(unittest.TestCase):

    def test_get_daily_niche(self):
        # Deterministic test based on specific dates
        dt1 = datetime(2026, 1, 1)
        niche1 = unlisted_daily_post.get_daily_niche(dt1)
        self.assertIn("niche", niche1)
        self.assertIn("cities", niche1)
        self.assertIn("ticket", niche1)
        self.assertIn("gatekeeper_trap", niche1)

        # Confirm next day rotates
        dt2 = datetime(2026, 1, 2)
        niche2 = unlisted_daily_post.get_daily_niche(dt2)
        self.assertNotEqual(niche1["niche"], niche2["niche"])

    def test_build_prompt(self):
        sample_niche = unlisted_daily_post.NICHES[0]
        prompt = unlisted_daily_post.build_prompt(sample_niche)
        self.assertIn(sample_niche["niche"], prompt)
        self.assertIn("SECTION 1: WHATSAPP GROUP POST", prompt)
        self.assertIn("SECTION 2: X.COM & THREADS POST", prompt)
        self.assertIn("DPDP Act 2023", prompt)

    @patch.dict(os.environ, {}, clear=True)
    def test_draft_post_missing_api_key(self):
        with self.assertRaises(RuntimeError) as ctx:
            unlisted_daily_post.draft_post()
        self.assertIn("Missing OPENROUTER_API_KEY", str(ctx.exception))

    @patch.dict(os.environ, {"OPENROUTER_API_KEY": "fake_key"})
    @patch("requests.post")
    def test_draft_post_success_first_model(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "Sample generated post text."}}]
        }
        mock_post.return_value = mock_resp

        result = unlisted_daily_post.draft_post()
        self.assertEqual(result, "Sample generated post text.")
        self.assertEqual(mock_post.call_count, 1)

    @patch.dict(os.environ, {"OPENROUTER_API_KEY": "fake_key"})
    @patch("requests.post")
    def test_draft_post_fallback_model(self, mock_post):
        mock_fail = MagicMock()
        mock_fail.status_code = 404
        mock_fail.text = "Not Found"

        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {
            "choices": [{"message": {"content": "Fallback generated post."}}]
        }

        mock_post.side_effect = [mock_fail, mock_success]

        result = unlisted_daily_post.draft_post()
        self.assertEqual(result, "Fallback generated post.")
        self.assertEqual(mock_post.call_count, 2)

    @patch.dict(os.environ, {"OPENROUTER_API_KEY": "fake_key"})
    @patch("requests.post")
    def test_draft_post_all_models_fail(self, mock_post):
        mock_fail = MagicMock()
        mock_fail.status_code = 404
        mock_fail.text = "Not Found"
        mock_post.return_value = mock_fail

        with self.assertRaises(RuntimeError) as ctx:
            unlisted_daily_post.draft_post()
        self.assertIn("All model attempts failed", str(ctx.exception))
        self.assertEqual(mock_post.call_count, len(unlisted_daily_post.MODELS))

    @patch.dict(os.environ, {"GMAIL_USER": "user@test.com", "GMAIL_APP_PASSWORD": "pass", "TO_EMAILS": "a@test.com, b@test.com"})
    @patch("smtplib.SMTP")
    def test_send_email_success(self, mock_smtp_class):
        mock_smtp = MagicMock()
        mock_smtp_class.return_value.__enter__.return_value = mock_smtp

        result = unlisted_daily_post.send_email("Test content", subject="Custom Subject")
        self.assertEqual(result, "ok")
        mock_smtp.starttls.assert_called_once()
        mock_smtp.login.assert_called_once_with("user@test.com", "pass")
        mock_smtp.send_message.assert_called_once()

        sent_msg = mock_smtp.send_message.call_args[0][0]
        self.assertEqual(sent_msg["To"], "a@test.com, b@test.com")
        self.assertEqual(sent_msg["From"], "user@test.com")
        self.assertEqual(sent_msg["Subject"], "Custom Subject")

    @patch.dict(os.environ, {"OPENROUTER_API_KEY": "fake_key"})
    @patch("requests.post")
    def test_draft_post_empty_content_fallback(self, mock_post):
        mock_empty = MagicMock()
        mock_empty.status_code = 200
        mock_empty.json.return_value = {
            "choices": [{"message": {"content": None, "reasoning": "Thinking..."}, "finish_reason": "length"}]
        }

        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {
            "choices": [{"message": {"content": "Generated post after fallback ₹8,000"}}]
        }

        mock_post.side_effect = [mock_empty, mock_success]

        result = unlisted_daily_post.draft_post()
        self.assertEqual(result, "Generated post after fallback ₹8,000")
        self.assertEqual(mock_post.call_count, 2)

    @patch.dict(os.environ, {"GMAIL_USER": "user@test.com", "GMAIL_APP_PASSWORD": "pass"}, clear=True)
    @patch("smtplib.SMTP")
    def test_send_email_default_recipient_and_subject(self, mock_smtp_class):
        mock_smtp = MagicMock()
        mock_smtp_class.return_value.__enter__.return_value = mock_smtp

        result = unlisted_daily_post.send_email("Content")
        self.assertEqual(result, "ok")
        sent_msg = mock_smtp.send_message.call_args[0][0]
        self.assertEqual(sent_msg["To"], "user@test.com")
        self.assertTrue(sent_msg["Subject"].startswith("Daily Marketing Pack:"))

    def test_stubs_publish(self):
        # Ensure planned hooks run without error
        unlisted_daily_post.publish_to_x("test")
        unlisted_daily_post.publish_to_threads("test")

if __name__ == "__main__":
    unittest.main()
