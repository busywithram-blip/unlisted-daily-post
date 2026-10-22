import os
import sys
import smtplib
from email.message import EmailMessage
from datetime import datetime
import pytz
import requests

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

MODELS = [
    "minimax/minimax-m3.1-flash:free",
    "liquid/lfm-2.5-2.6b:free",
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "recursive/flint-v1.0:free",
    "nvidia/nemotron-3.5-lightning:free",
    "openrouter/free"
]

def draft_post():
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENROUTER_API_KEY environment variable")

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://github.com/busywithram-blip/unlisted-daily-post",
        "X-Title": "Unlisted Daily Post",
        "Content-Type": "application/json"
    }

    prompt = """Create ONE high-value, engaging daily WhatsApp group post for founders, agency owners, and sales leaders from 'Unlisted'.

Requirements & Structure:
1. Short 2-3 lines practical strategy for today:
   - Start with a punchy pattern interrupt (no greetings like "Hey", "Good morning").
   - Give 2-3 lines of an actionable, practical strategy on client outreach, sales psychology, conversation closing, or buyer economics.
2. Daily 1-thing book suggestion:
   - Provide exactly 1 powerful actionable suggestion/quote credited to a real business, sales, consumer psychology, or communication classic (e.g., Influence by Robert Cialdini, Never Split the Difference by Chris Voss, Pitch Anything by Oren Klaff, $100M Offers by Alex Hormozi, The Ultimate Sales Machine by Chet Holmes, Thinking Fast and Slow by Daniel Kahneman, etc.).
   - Format: 📖 *Daily Insight from [Book Name] by [Author]:* "[One punchy takeaway sentence and how to use it today]"
3. Unlisted connection & solution:
   - Seamlessly connect the strategy to how Unlisted solves it: verified owner WhatsApp numbers pulled from live business sites, 1-tap wa.me link, zero IG logins, DPDP compliant.
4. Risk reversal & CTA:
   - "Test on your niche 2 weeks free. If it books meetings, pay ₹8,000. If not, ₹0 and keep the leads."
   - CTA: Drop your target niche + city below to test 2 weeks free.

Formatting Rules:
- DO NOT output section numbers or labels (NO "1. Hook & Strategy", NO "Section 1", NO "Hook:", etc.). It must read like a natural, compelling WhatsApp message.
- DO NOT mention days of the week (NO "Thursday drop", "Ready for Thursday", etc.).
- Use WhatsApp formatting: *bold* for key points, clean whitespace (blank line between every 1-2 lines).
- No corporate buzzwords/jargon (synergy, streamline, game-changer, revolutionary, bandwidth).
- Length: 130 to 200 words.
- Output ONLY the final WhatsApp post text, nothing else."""

    errors = []
    for model in MODELS:
        try:
            r = requests.post(url, headers=headers, json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 3000,
                "temperature": 0.7
            }, timeout=45)
            if r.status_code == 200:
                data = r.json()
                if "choices" in data and len(data["choices"]) > 0:
                    choice = data["choices"][0]
                    content = choice.get("message", {}).get("content")
                    if content and content.strip():
                        return content.strip()
                    finish_reason = choice.get("finish_reason")
                    errors.append(f"{model}: HTTP 200 but empty content (finish_reason: {finish_reason})")
                else:
                    errors.append(f"{model}: HTTP 200 but no choices returned")
            else:
                errors.append(f"{model}: HTTP {r.status_code} - {r.text[:120]}")
        except Exception as e:
            errors.append(f"{model}: {e}")

    raise RuntimeError(f"All model attempts failed: {'; '.join(errors)}")

def send_email(content):
    user = os.environ.get("GMAIL_USER", "busywithram@gmail.com")
    pwd  = os.environ.get("GMAIL_APP_PASSWORD", "tuavhrwqahthbkcj")

    to_emails_raw = os.environ.get("TO_EMAILS", user)
    recipients = [e.strip() for e in to_emails_raw.split(",") if e.strip()]
    if not recipients:
        recipients = [user]

    msg = EmailMessage()
    msg["From"] = user
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = "Daily WhatsApp Group Post Draft"
    msg.set_content(content)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as s:
            s.starttls()
            s.login(user, pwd)
            s.send_message(msg)
        return "ok"
    except Exception as e:
        raise RuntimeError(f"Failed to send email: {e}")

if __name__ == "__main__":
    post = draft_post()
    status = send_email(post)
    print(status)
