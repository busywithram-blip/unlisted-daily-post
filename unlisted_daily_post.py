import os
import smtplib
from email.message import EmailMessage
from datetime import datetime
import pytz
import requests

MODELS = [
    "openrouter/free",
    "google/gemma-4-31b-it:free",
    "google/gemma-4-26b-a4b-it:free",
    "nvidia/nemotron-3.5-lightning:free",
    "minimax/minimax-m3.1-flash:free",
    "thinkingmachines/inkling:free"
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
    for model in MODELS:
        try:
            r = requests.post(url, headers=headers, json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 800,
                "temperature": 0.7
            }, timeout=180)
            if r.status_code == 200:
                data = r.json()
                if "choices" in data and len(data["choices"]) > 0:
                    content = data["choices"][0]["message"]["content"]
                    if content and content.strip():
                        return content
            errors.append(f"{model}: HTTP {r.status_code} - {r.text[:100]}")
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
    print(send_email(post))
