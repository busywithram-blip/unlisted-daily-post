import os
import unittest
from unittest.mock import patch, MagicMock
import unlisted_daily_post

VALID_REFERENCE_POST = """I run a bot that finds verified owner WhatsApp numbers for agency outreach.

I found your agency using it.

Not a sales pitch. Here is what it does.

It finds the lead. It pulls the owner's direct mobile number from the business's own website and local listings. Not info@. Not a reception desk.

It writes the message. A short message for that specific business, based on what they sell and which city they are in.

It sends in one tap. One tap opens WhatsApp with the message already typed. You hit send from your own number, so it reads like you.

No logins. No cookies. Nothing to get flagged. Every message carries a "Reply STOP to opt out" line, so it stays compliant.

Here is my offer.

I run it on your niche and city. You look at the leads first. If they are good, you use it free while it proves itself.

If it books you meetings, you pay me at the end of that period and I will quote you for it.

If it does not, you owe nothing.

Drop your target niche and city. I will run it live."""

class TestUnlistedDailyPost(unittest.TestCase):

    # --- PROMPT TESTS ---
    def test_build_prompt_contains_opening(self):
        prompt = unlisted_daily_post.build_prompt("Wednesday")
        self.assertIn("I run a bot that finds", prompt)

    def test_build_prompt_contains_required_labels(self):
        prompt = unlisted_daily_post.build_prompt("Wednesday")
        self.assertIn("It finds the lead", prompt)
        self.assertIn("It writes the message", prompt)
        self.assertIn("It sends in one tap", prompt)

    def test_build_prompt_contains_offer_and_cta(self):
        prompt = unlisted_daily_post.build_prompt("Wednesday")
        self.assertIn("you owe nothing", prompt)
        self.assertIn("Drop your target niche and city", prompt)

    def test_build_prompt_no_hardcoded_8000(self):
        prompt = unlisted_daily_post.build_prompt("Wednesday")
        self.assertNotIn("₹8,000", prompt)
        self.assertNotIn("8000", prompt)

    def test_build_prompt_interpolates_day(self):
        prompt = unlisted_daily_post.build_prompt("Friday")
        self.assertIn("Day: Friday", prompt)

    # --- VALIDATOR REJECTION TESTS ---
    def test_validator_rejects_digits(self):
        invalid_post = VALID_REFERENCE_POST.replace("one tap", "1 tap")
        self.assertFalse(unlisted_daily_post.is_valid_post(invalid_post))
        self.assertIn("Contains digits", unlisted_daily_post.post_validation_errors(invalid_post))

    def test_validator_rejects_missing_opening(self):
        invalid_post = VALID_REFERENCE_POST.replace("I run a bot that finds", "I made a tool that finds")
        self.assertFalse(unlisted_daily_post.is_valid_post(invalid_post))

    def test_validator_rejects_missing_finds_lead(self):
        invalid_post = VALID_REFERENCE_POST.replace("It finds the lead", "It gets the lead")
        self.assertFalse(unlisted_daily_post.is_valid_post(invalid_post))

    def test_validator_rejects_missing_writes_message(self):
        invalid_post = VALID_REFERENCE_POST.replace("It writes the message", "It crafts the text")
        self.assertFalse(unlisted_daily_post.is_valid_post(invalid_post))

    def test_validator_rejects_missing_sends_in_one_tap(self):
        invalid_post = VALID_REFERENCE_POST.replace("It sends in one tap", "It sends in one click")
        self.assertFalse(unlisted_daily_post.is_valid_post(invalid_post))

    def test_validator_rejects_missing_owe_nothing(self):
        invalid_post = VALID_REFERENCE_POST.replace("you owe nothing", "you pay nothing")
        self.assertFalse(unlisted_daily_post.is_valid_post(invalid_post))

    def test_validator_rejects_missing_cta(self):
        invalid_post = VALID_REFERENCE_POST.replace("Drop your target niche and city", "Send your niche and city")
        self.assertFalse(unlisted_daily_post.is_valid_post(invalid_post))

    def test_validator_rejects_url_http(self):
        invalid_post = VALID_REFERENCE_POST + "\n\nVisit https://example.com for info"
        self.assertFalse(unlisted_daily_post.is_valid_post(invalid_post))

    def test_validator_rejects_url_wa_me(self):
        invalid_post = VALID_REFERENCE_POST + "\n\nwa.me/123456"
        self.assertFalse(unlisted_daily_post.is_valid_post(invalid_post))

    def test_validator_rejects_url_pages_dev(self):
        invalid_post = VALID_REFERENCE_POST + "\n\nunlistedbot.pages.dev"
        self.assertFalse(unlisted_daily_post.is_valid_post(invalid_post))

    def test_validator_rejects_greeting_start(self):
        invalid_post = "Hey members!\n\n" + VALID_REFERENCE_POST
        self.assertFalse(unlisted_daily_post.is_valid_post(invalid_post))

    def test_validator_rejects_banned_jargon_pipeline(self):
        invalid_post = VALID_REFERENCE_POST.replace("sales pitch", "pipeline")
        self.assertFalse(unlisted_daily_post.is_valid_post(invalid_post))

    def test_validator_rejects_banned_jargon_funnel(self):
        invalid_post = VALID_REFERENCE_POST.replace("sales pitch", "funnel")
        self.assertFalse(unlisted_daily_post.is_valid_post(invalid_post))

    def test_validator_rejects_banned_jargon_sdr(self):
        invalid_post = VALID_REFERENCE_POST.replace("sales pitch", "sdr team")
        self.assertFalse(unlisted_daily_post.is_valid_post(invalid_post))

    def test_validator_rejects_banned_trope_free_trial(self):
        invalid_post = VALID_REFERENCE_POST.replace("proves itself", "proves itself in a free trial")
        self.assertFalse(unlisted_daily_post.is_valid_post(invalid_post))

    def test_validator_rejects_under_80_words(self):
        short_post = "I run a bot that finds verified owner WhatsApp numbers. It finds the lead. It writes the message. It sends in one tap. You owe nothing. Drop your target niche and city."
        self.assertFalse(unlisted_daily_post.is_valid_post(short_post))

    def test_validator_rejects_over_200_words(self):
        long_post = VALID_REFERENCE_POST + " extra word" * 80
        self.assertFalse(unlisted_daily_post.is_valid_post(long_post))

    def test_validator_rejects_first_line_over_100_chars(self):
        long_line_post = "I run a bot that finds verified owner WhatsApp numbers for agency outreach and leads generation in Indian cities today.\n\n" + VALID_REFERENCE_POST
        self.assertFalse(unlisted_daily_post.is_valid_post(long_line_post))

    # --- VALIDATOR ACCEPTANCE TESTS ---
    def test_validator_accepts_reference_post(self):
        self.assertTrue(unlisted_daily_post.is_valid_post(VALID_REFERENCE_POST))

    def test_validator_accepts_variation_agencies_like_yours(self):
        var_post = VALID_REFERENCE_POST.replace("I found your agency using it.", "I found agencies like yours using it.")
        self.assertTrue(unlisted_daily_post.is_valid_post(var_post))

    def test_validator_accepts_info_at_email(self):
        self.assertIn("Not info@.", VALID_REFERENCE_POST)
        self.assertTrue(unlisted_daily_post.is_valid_post(VALID_REFERENCE_POST))

    # --- REPAIR PASS & DRAFT TESTS ---
    @patch.dict(os.environ, {}, clear=True)
    def test_draft_post_missing_api_key(self):
        with self.assertRaises(RuntimeError) as ctx:
            unlisted_daily_post.draft_post()
        self.assertIn("Missing OPENROUTER_API_KEY", str(ctx.exception))

    @patch.dict(os.environ, {"OPENROUTER_API_KEY": "fake_key"})
    @patch("unlisted_daily_post._post_once")
    def test_draft_post_valid_first_attempt(self, mock_post_once):
        mock_post_once.return_value = (VALID_REFERENCE_POST, None)
        result = unlisted_daily_post.draft_post()
        self.assertEqual(result, VALID_REFERENCE_POST)
        self.assertEqual(mock_post_once.call_count, 1)

    @patch.dict(os.environ, {"OPENROUTER_API_KEY": "fake_key"})
    @patch("unlisted_daily_post._post_once")
    def test_draft_post_repair_pass_success(self, mock_post_once):
        invalid_first = VALID_REFERENCE_POST.replace("one tap", "1 tap")
        mock_post_once.side_effect = [
            (invalid_first, None),
            (VALID_REFERENCE_POST, None)
        ]
        result = unlisted_daily_post.draft_post()
        self.assertEqual(result, VALID_REFERENCE_POST)
        self.assertEqual(mock_post_once.call_count, 2)

    @patch.dict(os.environ, {"OPENROUTER_API_KEY": "fake_key"})
    @patch("unlisted_daily_post._post_once")
    def test_draft_post_repair_pass_fails_next_model(self, mock_post_once):
        invalid_first = VALID_REFERENCE_POST.replace("one tap", "1 tap")
        mock_post_once.side_effect = [
            (invalid_first, None),
            (invalid_first, None),
            (VALID_REFERENCE_POST, None)
        ]
        result = unlisted_daily_post.draft_post()
        self.assertEqual(result, VALID_REFERENCE_POST)
        self.assertEqual(mock_post_once.call_count, 3)

    @patch.dict(os.environ, {"OPENROUTER_API_KEY": "fake_key"})
    @patch("unlisted_daily_post._post_once")
    def test_draft_post_free_models_quota_stops_immediately(self, mock_post_once):
        mock_post_once.return_value = ("", "HTTP 429: free-models-per-day rate limit exceeded")
        with self.assertRaises(RuntimeError) as ctx:
            unlisted_daily_post.draft_post()
        self.assertIn("All model attempts failed", str(ctx.exception))
        self.assertEqual(mock_post_once.call_count, 1)

    # --- EMAIL TESTS ---
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
