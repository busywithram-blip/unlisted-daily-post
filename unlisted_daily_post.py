import os
import smtplib
from email.message import EmailMessage
from datetime import datetime
import pytz
import requests

OPENROUTER_MODELS = [
    "openrouter/free",
    "minimax/minimax-m3.1-flash:free",
    "google/gemma-4-31b-it:free",
    "google/gemma-4-26b-a4b-it:free",
    "nvidia/nemotron-3.5-lightning:free",
    "liquid/lfm-2.5-2.6b:free"
]

GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash"
]

def extract_content(message_obj):
    if not message_obj:
        return ""
    content = message_obj.get("content")
    if isinstance(content, str):
        return content.strip()
    elif isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                if item.get("type") == "text" and "text" in item:
                    parts.append(item["text"])
                elif "text" in item:
                    parts.append(item["text"])
        return "\n".join(parts).strip()
    return ""

def draft_post():
    gemini_key = os.environ.get("GEMINI_API_KEY")
    openrouter_key = os.environ.get("OPENROUTER_API_KEY")

    if not gemini_key and not openrouter_key:
        raise RuntimeError("Missing API Key. Please set GEMINI_API_KEY or OPENROUTER_API_KEY in environment variables / GitHub Secrets.")

    ist = pytz.timezone('Asia/Kolkata')
    day = datetime.now(ist).strftime('%A')
    prompt = f"""Create ONE WhatsApp group post for Unlisted. Rules:
- 80-160 words
- Pattern interrupt in first 7 words (no greetings)
- *bold* key points
- Blank line between every 1-2 lines
- No URLs/links/jargon (pipeline,funnel,SDR,cadence,outreach,leverage,streamline,synergy,ecosystem,bandwidth,game-changer,revolutionary)
- Risk reversal: "Test on your niche 2 weeks free. If it books meetings, pay ₹8,000. If not, ₹0 and keep the leads."
- CTA: "Drop your target niche + city"
- Topic: verified owner WhatsApp numbers from live business sites, 1-tap wa.me, zero IG logins, DPDP compliant
- Day: {day}

ONLY post text."""

    errors = []

    # Try Gemini API if GEMINI_API_KEY is available
    if gemini_key:
        gemini_url = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
        headers = {
            "Authorization": f"Bearer {gemini_key}",
            "Content-Type": "application/json"
        }
        for model in GEMINI_MODELS:
            try:
                r = requests.post(gemini_url, headers=headers, json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 800,
                    "temperature": 0.7
                }, timeout=120)
                if r.status_code == 200:
                    data = r.json()
                    if "choices" in data and len(data["choices"]) > 0:
                        message = data["choices"][0].get("message", {})
                        extracted = extract_content(message)
                        if extracted:
                            return extracted
                errors.append(f"Gemini {model}: HTTP {r.status_code} - {r.text[:100]}")
            except Exception as e:
                errors.append(f"Gemini {model}: {e}")

    # Try OpenRouter API if OPENROUTER_API_KEY is available
    if openrouter_key:
        openrouter_url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {openrouter_key}",
            "HTTP-Referer": "https://github.com/busywithram-blip/unlisted-daily-post",
            "X-Title": "Unlisted Daily Post",
            "Content-Type": "application/json"
        }
        for model in OPENROUTER_MODELS:
            try:
                r = requests.post(openrouter_url, headers=headers, json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 800,
                    "temperature": 0.7
                }, timeout=120)
                if r.status_code == 200:
                    data = r.json()
                    if "choices" in data and len(data["choices"]) > 0:
                        message = data["choices"][0].get("message", {})
                        extracted = extract_content(message)
                        if extracted:
                            return extracted
                errors.append(f"OpenRouter {model}: HTTP {r.status_code} - {r.text[:100]}")
            except Exception as e:
                errors.append(f"OpenRouter {model}: {e}")

    raise RuntimeError(f"All AI provider attempts failed: {'; '.join(errors)}")

def send_email(content):
    user = os.environ.get("GMAIL_USER")
    pwd  = os.environ.get("GMAIL_APP_PASSWORD")

    if not user or not pwd:
        raise RuntimeError("Missing GMAIL_USER or GMAIL_APP_PASSWORD environment variable")

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
    print(send_email(post))
