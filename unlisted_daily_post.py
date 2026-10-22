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

NICHES = [
    {
        "niche": "Luxury Interior Designers & Turnkey Architects",
        "cities": "Indiranagar & Whitefield (Bengaluru), Bandra & Juhu (Mumbai), Gurugram",
        "ticket": "₹5L to ₹25L+ project profits",
        "gatekeeper_trap": "Instagram DMs get deleted by 21-year-old junior interns. Receptionists block calls. But principal architects live on WhatsApp 24/7 managing site contractors."
    },
    {
        "niche": "High-Ticket Aesthetic, Dental & Hair Restoration Clinics",
        "cities": "South Delhi, Bandra (Mumbai), Jubilee Hills (Hyderabad)",
        "ticket": "₹50,000 to ₹3,00,000 per patient package",
        "gatekeeper_trap": "Cold calls hit reception desks who say 'doctor is in surgery'. Cold emails bounce. Doctors manage clinic ops and VIP consults on their direct WhatsApp."
    },
    {
        "niche": "Direct-to-Consumer (D2C) & Premium Lifestyle Brands",
        "cities": "Bengaluru, Mumbai, Surat, Ahmedabad",
        "ticket": "₹10L to ₹50L/mo revenue brands",
        "gatekeeper_trap": "Apollo and LinkedIn have generic info@ emails. DMs get buried in customer support. Founders review WhatsApp in between inventory and ad checks."
    },
    {
        "niche": "Commercial Real Estate & Luxury Channel Partners",
        "cities": "BKC (Mumbai), Golf Course Road (Gurugram), HITEC City (Hyderabad)",
        "ticket": "₹2Cr to ₹15Cr property mandates",
        "gatekeeper_trap": "Portals sell recycled 2-year-old lead lists to 500 brokers. Agency pitches must hit the managing partner or prime broker directly on WhatsApp."
    },
    {
        "niche": "Upscale Fine-Dining & Cloud Kitchen Restaurant Chains",
        "cities": "Koramangala (Bengaluru), Connaught Place (Delhi), Indiranagar",
        "ticket": "₹1L to ₹3L/mo marketing/growth retainers",
        "gatekeeper_trap": "Restaurant managers on-site never pass sales calls to the owner. The owner only monitors daily revenue and supplier chats on WhatsApp."
    },
    {
        "niche": "B2B Industrial, Capital Equipment & Solar EPC Contractors",
        "cities": "Pune, Coimbatore, Peenya (Bengaluru), Ahmedabad",
        "ticket": "₹15L to ₹1Cr+ industrial orders",
        "gatekeeper_trap": "Cold emails get flagged as spam. Managing Directors never check LinkedIn InMail, but keep WhatsApp open all day for client purchase orders."
    }
]

def get_daily_niche(dt=None):
    """Deterministically pick today's high-ticket Indian niche based on the day of the year."""
    if dt is None:
        tz = pytz.timezone("Asia/Kolkata")
        dt = datetime.now(tz)
    idx = dt.timetuple().tm_yday % len(NICHES)
    return NICHES[idx]

def build_prompt(niche_info):
    return f"""You are the founder of 'Unlisted' (an outbound lead intelligence platform for agencies and B2B founders in India).
Create today's daily marketing content pack to position Unlisted as the undisputed B2B outbound authority.

TODAY'S NICHE TEARDOWN:
- Focus Niche: {niche_info['niche']}
- Target Cities: {niche_info['cities']}
- Typical Deal Size: {niche_info['ticket']}
- Gatekeeper Reality: {niche_info['gatekeeper_trap']}

THE PRODUCT (UNLISTED):
- What it does: Crawls live business websites to extract verified business owner WhatsApp numbers directly.
- Key Moat: Zero Instagram logins/cookies (no account ban risk), 100% DPDP Act 2023 Sec 3(c)(ii) compliant audit trail, 1-tap mobile wa.me links.
- Economic Anchor: Replaces a ₹25,000–₹35,000/mo junior SDR for ₹8,000/mo flat.
- Risk-Reversal Offer: "Test on your niche 2 weeks free. If it books meetings, pay ₹8,000. If not, ₹0 and keep the leads."

OUTPUT FORMAT:
Generate EXACTLY two sections separated by an explicit boundary line:

=== SECTION 1: WHATSAPP GROUP POST ===
- Start with a punchy pattern interrupt highlighting why traditional outbound (cold DMs, cold calls, Apollo lists) fails for {niche_info['niche']}.
- 2-3 lines of practical sales/consumer psychology strategy for how agencies should actually reach these owners.
- 1 punchy book takeaway from a classic (Influence by Robert Cialdini, Never Split the Difference by Chris Voss, $100M Offers by Alex Hormozi, Alchemy by Rory Sutherland, The Ultimate Sales Machine by Chet Holmes, Thinking Fast and Slow by Daniel Kahneman, Pitch Anything by Oren Klaff, etc.).
  Format: 📖 *Daily Insight from [Book Name] by [Author]:* "[Quote or core concept] — [How to apply it today]"
- The Unlisted bridge: How Unlisted solves this by pulling verified owner WhatsApp numbers straight from live business websites.
- The Hormozi risk-reversal offer + CTA: "Drop your target niche + city below to test 2 weeks free."
- Formatting Rules:
  * Clean WhatsApp formatting: *bold* for key terms, blank line between every 1-2 lines.
  * DO NOT output section numbers or labels inside the post (NO "1. Hook", NO "Section 1", NO "Hook:", etc.).
  * DO NOT mention days of the week (NO "Thursday drop", etc.).
  * Length: 130 to 200 words.

=== SECTION 2: X.COM & THREADS POST ===
- A razor-sharp, high-engagement micro-post (under 280-450 characters).
- Hook: The brutal reality of pitching {niche_info['niche']} in India.
- Insight: Why direct WhatsApp in the owner's pocket beats cold email & IG DMs.
- CTA: "Testing 2 weeks free for agencies. Comment your niche + city."
- No fluff, maximum 1-2 relevant hashtags.
"""

def draft_post(niche_info=None):
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENROUTER_API_KEY environment variable")

    if niche_info is None:
        niche_info = get_daily_niche()

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://github.com/busywithram-blip/unlisted-daily-post",
        "X-Title": "Unlisted Daily Post",
        "Content-Type": "application/json"
    }

    prompt = build_prompt(niche_info)

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

def publish_to_x(content):
    """Placeholder hook for planned X.com API automation."""
    # Automated publishing to X will be configured in a subsequent phase.
    print("[INFO] X.com automated posting planned for next release.")

def publish_to_threads(content):
    """Placeholder hook for planned Meta Threads API automation."""
    # Automated publishing to Threads will be configured in a subsequent phase.
    print("[INFO] Threads automated posting planned for next release.")

def send_email(content, subject=None):
    user = os.environ.get("GMAIL_USER", "busywithram@gmail.com")
    pwd  = os.environ.get("GMAIL_APP_PASSWORD", "tuavhrwqahthbkcj")

    to_emails_raw = os.environ.get("TO_EMAILS", user)
    recipients = [e.strip() for e in to_emails_raw.split(",") if e.strip()]
    if not recipients:
        recipients = [user]

    if subject is None:
        niche_info = get_daily_niche()
        subject = f"Daily Marketing Pack: {niche_info['niche']}"

    msg = EmailMessage()
    msg["From"] = user
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject
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
    niche = get_daily_niche()
    post = draft_post(niche)
    status = send_email(post, subject=f"Daily Marketing Pack: {niche['niche']}")
    print(status)
