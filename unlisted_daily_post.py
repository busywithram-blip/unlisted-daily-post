import os
import re
import smtplib
from email.message import EmailMessage
from datetime import datetime
import pytz
import requests

MODELS = [
    "openrouter/free",
    "minimax/minimax-m3.1-flash:free",
    "google/gemma-4-31b-it:free",
    "google/gemma-4-26b-a4b-it:free",
    "nvidia/nemotron-3.5-lightning:free",
    "liquid/lfm-2.5-2.6b:free"
]

MAX_TOKENS = 4000
REPAIR_MAX_TOKENS = 1500

REASONING_ARTIFACTS = re.compile(
    r"(?i)(thought|thinking|reasoning|chain of thought|let's think|i need to|rule check|word count):"
)

REQUIRED_PHRASES = [
    "I run a bot that finds",
    "It finds the lead",
    "It writes the message",
    "It sends in one tap",
    "you owe nothing",
    "Drop your target niche and city"
]

BANNED_JARGON = [
    "pipeline", "funnel", "sdr", "cadence", "outreach", "leverage",
    "streamline", "synergy", "ecosystem", "bandwidth", "game-changer", "revolutionary"
]

BANNED_TROPES = [
    "free trial", "limited time offer", "click here", "dm for price",
    "best tool in the market", "guaranteed"
]

URL_PATTERN = re.compile(r"(?i)(https?://|www\.|wa\.me|\.com|\.pages\.dev|\.in/)")
GREETING_PATTERN = re.compile(r"^(hey|hi|hello|dear|good day)", re.IGNORECASE)

def get_models():
    override = os.environ.get("OPENROUTER_MODEL")
    if override:
        return [override.strip()]
    return MODELS

def build_prompt(day):
    return f"""Create ONE WhatsApp group post for Unlisted. Target audience: Indian digital agency owners, freelancers and small business service providers.

=== ANGLE (this is the hook, use it) ===
Lead with transparency, not hype. Open by admitting you run a bot that finds verified owner WhatsApp numbers for agency outreach, and that you found the reader's agency using it. Transparency IS the hook.

=== MANDATORY STRUCTURE (every post, same order) ===
1. "I run a bot that finds verified owner WhatsApp numbers for agency outreach."
2. "I found your agency using it." (or "I found agencies like yours using it" - only if that is true)
3. One short line: not a sales pitch, here is what it does.
4. The SAME three things, in this exact order. Label them with WORDS, never digits:
   - It finds the lead. The owner's direct mobile number, pulled from the business's own website and local listings. Not info@. Not a reception desk.
   - It writes the message. A short message for that specific business, based on what they sell and which city they are in.
   - It sends in one tap. One tap opens WhatsApp with the message already typed. They hit send from their own number, so it reads like them.
5. Compliance line: no logins, no cookies, nothing to get flagged, every message carries a "Reply STOP to opt out" line.
6. The offer: "I run it on your niche and city. You look at the leads first. If they are good, you use it free while it proves itself. If it books you meetings, you pay me at the end of that period and I will quote you for it. If it does not, you owe nothing."
7. CTA: "Drop your target niche and city."

=== HARD RULES ===
- ZERO DIGITS. No prices, no timeframes, no lead counts, no step numbers, no durations. Write numbers as words only where unavoidable (like "one tap").
- NO invented stories, NO fake numbers, NO fake testimonials, NO quotes, NO "I pulled 28 lines" style claims.
- ZERO URLs, ZERO links. No payment links, no sheet links.
- Plain English. Short sentences. No jargon: pipeline, funnel, SDR, cadence, outreach, leverage, streamline, synergy, ecosystem, bandwidth, game-changer, revolutionary.
- No banned tropes: "free trial", "limited time offer", "click here", "DM for price", "guaranteed ROI", "best tool in the market".
- No greetings. Never start with "Hey", "Hi", "Hello", "Dear members", "Good day".
- Indian context only: Indian business types (clinics, coaching centres, salons, contractors, hotels, wedding planners, gyms, hardware shops, CA firms, travel agencies, interior designers) and Indian cities.
- Blank line between every 1-2 lines. One idea per line.
- The first line must register instantly in the notification preview. Keep it short and self-contained, well under 100 characters.

Day: {day}

Output ONLY the post text. No preamble, no explanation, no word count, no markdown headers."""

def clean_post(text):
    if not text:
        return ""
    # Strip markdown code blocks
    text = re.sub(r"```[\s\S]*?```", "", text)
    # Strip "Post:" or "Output:" prefixes
    text = re.sub(r"^(Post|Output):\s*", "", text, flags=re.IGNORECASE)
    return text.strip()

def post_validation_errors(text):
    errors = []
    if not text or not text.strip():
        errors.append("Empty text")
        return errors

    cleaned = clean_post(text)

    if REASONING_ARTIFACTS.search(cleaned):
        errors.append("Contains reasoning artifacts")

    words = cleaned.split()
    word_count = len(words)
    if not (80 <= word_count <= 200):
        errors.append(f"Word count must be 80-200 (got {word_count})")

    if re.search(r"\d", cleaned):
        errors.append("Contains digits")

    lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
    if lines:
        first_line = lines[0]
        if len(first_line) >= 100:
            errors.append("First line length >= 100 characters")
        if GREETING_PATTERN.search(first_line):
            errors.append("First line starts with a greeting")

    for phrase in REQUIRED_PHRASES:
        if phrase not in cleaned:
            errors.append(f"Missing required phrase: '{phrase}'")

    if URL_PATTERN.search(cleaned):
        errors.append("Contains forbidden URL/link pattern")

    # Allow "agency outreach" in opening line by masking it before checking BANNED_JARGON
    lower_cleaned = re.sub(r"agency\s+outreach", "agency_masked", cleaned, flags=re.IGNORECASE).lower()
    for jargon in BANNED_JARGON:
        if re.search(r"\b" + re.escape(jargon) + r"\b", lower_cleaned):
            errors.append(f"Contains banned jargon: '{jargon}'")

    for trope in BANNED_TROPES:
        if trope in lower_cleaned:
            errors.append(f"Contains banned trope: '{trope}'")

    return errors

def is_valid_post(text):
    return len(post_validation_errors(text)) == 0

def _post_once(model, prompt, max_tokens, api_key):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://github.com/busywithram-blip/unlisted-daily-post",
        "X-Title": "Unlisted Daily Post",
        "Content-Type": "application/json"
    }
    r = requests.post(url, headers=headers, json={
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.7
    }, timeout=180)

    if r.status_code == 200:
        data = r.json()
        if "choices" in data and len(data["choices"]) > 0:
            msg = data["choices"][0].get("message", {})
            content = msg.get("content")
            if isinstance(content, str):
                return clean_post(content), None
            elif isinstance(content, list):
                parts = [item["text"] for item in content if isinstance(item, dict) and "text" in item]
                return clean_post("\n".join(parts)), None
        return "", f"Empty choices response from {model}"
    return "", f"HTTP {r.status_code}: {r.text[:100]}"

def draft_post():
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENROUTER_API_KEY environment variable")

    ist = pytz.timezone('Asia/Kolkata')
    day = datetime.now(ist).strftime('%A')
    prompt = build_prompt(day)

    models = get_models()
    errors = []

    for model in models:
        text, err = _post_once(model, prompt, MAX_TOKENS, api_key)
        if err:
            errors.append(f"{model}: {err}")
            if "free-models-per-day" in err:
                break
            continue

        if is_valid_post(text):
            return text

        val_errs = post_validation_errors(text)
        repair_prompt = f"""Fix the following WhatsApp post so it satisfies all rules.

ORIGINAL POST:
{text}

VALIDATION ERRORS TO FIX:
- {'; '.join(val_errs)}

RULES:
- Keep exact phrases: "I run a bot that finds", "It finds the lead", "It writes the message", "It sends in one tap", "you owe nothing", "Drop your target niche and city"
- ZERO DIGITS. Write numbers as words.
- Word count MUST be between 80 and 200 words.
- First line under 100 chars, no greetings.
- No URLs, no jargon, no banned tropes.

Output ONLY the fixed post text."""

        repaired_text, repair_err = _post_once(model, repair_prompt, REPAIR_MAX_TOKENS, api_key)
        if not repair_err and is_valid_post(repaired_text):
            return repaired_text

        errors.append(f"{model}: Initial output invalid ({'; '.join(val_errs)})")

    raise RuntimeError(f"All model attempts failed: {'; '.join(errors)}")

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
