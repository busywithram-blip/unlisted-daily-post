import os
import sys
import smtplib
import html
import re
import urllib.parse
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
    "nvidia/nemotron-3.5-lightning:free",
    "liquid/lfm-2.5-2.6b:free",
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "recursive/flint-v1.0:free",
    "openrouter/free"
]

NICHES = [
    {
        "category": "B2B Marketing & Agencies",
        "niche": "Performance Agencies Pitching Aesthetic & Dental Clinics",
        "target_audience": "Agency founders who run Meta/Google ads for dentists, dermatologists, and hair transplant clinics.",
        "cities": "South Delhi, Bandra & Juhu (Mumbai), Jubilee Hills (Hyderabad)",
        "pain_point": "Sales reps spend 4 hours a day on Google Maps only to get blocked by clinic receptionists who say 'doctor is in surgery'.",
        "ticket": "₹50,000 to ₹1,50,000/mo retainer per clinic"
    },
    {
        "category": "B2B High-Ticket Services",
        "niche": "Turnkey Interior Fitout & Commercial Architecture Firms",
        "target_audience": "Founders of commercial interior studios and architectural firms pitching retail stores, offices, and upscale clinics.",
        "cities": "Indiranagar & Whitefield (Bengaluru), BKC & Lower Parel (Mumbai), Gurugram",
        "pain_point": "Instagram DMs are handled by junior social media interns who delete pitches. Principal architects live on WhatsApp on-site managing contractors.",
        "ticket": "₹10L to ₹50L+ project budgets"
    },
    {
        "category": "C2B Creators & Solo Operators",
        "niche": "High-Intent UGC Creators & Video Ad Specialists Pitching D2C Brands",
        "target_audience": "Solo UGC creators, video editors, and creative strategists pitching direct-to-consumer (D2C) brands for paid ad creative.",
        "cities": "Bengaluru, Mumbai, Surat, Ahmedabad",
        "pain_point": "Cold DMs to brand Instagram pages get answered by 20-year-old community managers with zero hiring budget. Founders check WhatsApp between warehouse and ad checks.",
        "ticket": "₹30,000 to ₹1,00,000 creative retainer packages"
    },
    {
        "category": "B2B Agencies & Tech",
        "niche": "E-commerce Growth & Retention Agencies for D2C Brands",
        "target_audience": "Performance agency founders pitching high-growth consumer brands doing ₹10L–₹50L/mo GMV.",
        "cities": "Bengaluru, Mumbai, Delhi NCR, Ahmedabad",
        "pain_point": "Apollo and LinkedIn have generic info@ emails. DMs get buried in customer support. Founders review WhatsApp in between inventory and ad checks.",
        "ticket": "₹75,000 to ₹2,50,000/mo retainer"
    },
    {
        "category": "B2B Real Estate & Broking",
        "niche": "Commercial Real Estate Channel Partners & Luxury Mandate Brokers",
        "target_audience": "Agency operators and prime real estate brokers pitching luxury developers and commercial landlords.",
        "cities": "BKC (Mumbai), Golf Course Road (Gurugram), HITEC City (Hyderabad)",
        "pain_point": "Portals sell recycled 2-year-old lead lists to 500 brokers. Agency pitches must hit the managing partner or prime broker directly on WhatsApp.",
        "ticket": "₹2Cr to ₹15Cr property mandates"
    },
    {
        "category": "B2B Creative Studios",
        "niche": "High-End Video Production & Commercial Studios",
        "target_audience": "Creative directors and video production house founders pitching corporate commercials and D2C brand films.",
        "cities": "Mumbai, Bengaluru, Delhi NCR",
        "pain_point": "Cold emails bounce or sit in unread agency inboxes. Brand CMOs and founders respond to 15-second personalized video reviews on WhatsApp.",
        "ticket": "₹1,50,000 to ₹6,00,000 per brand film"
    },
    {
        "category": "B2B Industrial & Manufacturing",
        "niche": "B2B Industrial, Capital Equipment & Solar EPC Contractors",
        "target_audience": "Marketing leaders and sales heads of industrial machinery manufacturers and commercial solar installers.",
        "cities": "Pune, Coimbatore, Peenya (Bengaluru), Ahmedabad",
        "pain_point": "Cold emails get flagged as spam. Managing Directors never check LinkedIn InMail, but keep WhatsApp open all day for client purchase orders.",
        "ticket": "₹15L to ₹1Cr+ industrial orders"
    },
    {
        "category": "C2B High-Ticket Freelancers",
        "niche": "Direct-Response Copywriters & Funnel Builders Pitching E-comm Founders",
        "target_audience": "Solo direct-response copywriters, email marketing specialists, and funnel consultants.",
        "cities": "National / Remote (India & Global)",
        "pain_point": "Cold emails to generic support desks never reach the founder. A 3-line WhatsApp teardown identifying an email checkout leak gets answered in 10 minutes.",
        "ticket": "₹40,000 to ₹1,20,000/mo retainer"
    },
    {
        "category": "B2B Consulting & HR",
        "niche": "Corporate Training, Executive Coaching & HR Consultancies",
        "target_audience": "Founders of leadership training consultancies and boutique executive search firms pitching fast-scaling startups.",
        "cities": "Bengaluru, Delhi NCR, Hyderabad, Mumbai",
        "pain_point": "Pitches to corporate HR land in a black hole. Founders need direct mobile access to the CEO or COO.",
        "ticket": "₹1,50,000 to ₹5,00,000 per engagement"
    },
    {
        "category": "B2B Hospitality & Retail",
        "niche": "Fine-Dining, Cloud Kitchen & Franchise Restaurant Chains",
        "target_audience": "Agency founders pitching food & beverage brand scaling, local SEO, and influencer marketing.",
        "cities": "Koramangala (Bengaluru), Connaught Place (Delhi), Indiranagar",
        "pain_point": "On-site restaurant managers never pass sales calls to the owner. The owner only monitors daily revenue and supplier chats on WhatsApp.",
        "ticket": "₹1L to ₹3L/mo marketing/growth retainers"
    }
]

def get_daily_niche(dt=None):
    if dt is None:
        tz = pytz.timezone("Asia/Kolkata")
        dt = datetime.now(tz)
    idx = dt.timetuple().tm_yday % len(NICHES)
    return NICHES[idx]

def build_prompt(niche_info):
    return f"""You are the Chief Marketing Officer and Growth Lead for 'Unlisted' (the B2B WhatsApp decision-maker lead engine in India).
Generate today's complete Daily Marketing Brief & Growth Stack for the founder (Ram) to market Unlisted and acquire paying agency and B2B clients.

TODAY'S TARGET FOCUS:
- Category: {niche_info['category']}
- Niche: {niche_info['niche']}
- Target Audience: {niche_info['target_audience']}
- Target Cities: {niche_info['cities']}
- Friction & Gatekeeper Bottleneck: {niche_info['pain_point']}
- Average Deal Size: {niche_info['ticket']}

THE PRODUCT (UNLISTED):
- What it does: Crawls live business websites to extract verified business owner WhatsApp numbers directly.
- Core Advantages:
  * 100% Ban-Proof: Zero bots or automation touching their WhatsApp accounts. Human reps tap a pre-filled 1-click wa.me link to send.
  * Zero Passwords or Logins Required: Never ask for Instagram, WhatsApp, or email logins (0% account liability).
  * Fresh, Active Data: Pulled directly from live business websites and active domains, never stale or recycled databases.

STRICT PRICING & TONE RULES:
- ABSOLUTELY NO EXPLICIT PUBLIC PRICING: NEVER mention "₹8,000", "₹8,000/mo", or any specific rupee fee in any public post, comment, or headline.
- Instead, anchor value against operational waste: "replaces full-time SDR payroll bloat", "zero hiring overhead", "fractional pipeline setup".
- Risk-Reversal Offer: "Test on your niche 1 week free. If it books meetings, we scale. If not, ₹0 and keep the leads."
- DO NOT mention legal acts or compliance statutes (NO "DPDP Act", NO "Section 3(c)(ii)"). Buyers only care about ban-proof safety and verified owner responses.

CRITICAL FORMATTING INSTRUCTION:
- Do NOT output any preamble, thinking, planning, or introductory remarks.
- Start your response immediately with the exact text: '=== 1. TODAY'S DIRECTIVE & GROWTH STACK ==='.

OUTPUT FORMAT (You must output EXACTLY the following 5 labeled sections using these exact headers):

=== 1. TODAY'S DIRECTIVE & GROWTH STACK ===
- 3 clear bullet points: Step-by-step instructions for Ram on what to execute today in 15 minutes.
- Psychology Lever: 1 sentence explaining the psychological trigger used today (from consumer psychology or business economics).
- Daily Book Takeaway: Exactly 1 actionable insight from a classic book (Influence by Cialdini, Never Split the Difference by Chris Voss, $100M Offers by Alex Hormozi, Alchemy by Rory Sutherland, The Ultimate Sales Machine by Chet Holmes, Thinking Fast and Slow by Daniel Kahneman, Pitch Anything by Oren Klaff). Format: 📖 *[Book Name] by [Author]:* "[Quote/Concept] — [Application]"

=== 2. WHATSAPP COMMUNITY POST ===
STRICT CONSTRAINT: 50 TO 80 WORDS MAXIMUM. DO NOT WRITE AN ESSAY.
WhatsApp group members skim in 3 seconds. Use this exact 3-part micro-structure:
1. Pattern Interrupt Hook: 1 sharp contrarian line exposing why outreach fails for {niche_info['niche']} in {niche_info['cities']}.
2. Core Reality: Exactly 3 punchy bullet points (one line each):
   • Point 1: Why receptionists/cold emails fail
   • Point 2: Why decision-makers live on WhatsApp
   • Point 3: 1-click mobile dispatch with zero account risk
3. Low-Friction Call-to-Action: 1 closing question (e.g. "Dropping 10 verified owner lines for {niche_info['cities']} founders today. Reply 'SEND' if you want the sheet.").
NO corporate filler. NO generic intros. NO explicit pricing numbers. Under 80 words.

=== 3. LINKEDIN AUTHORITY POST ===
- Compelling scroll-stopping 2-line hook.
- A hard-hitting breakdown of why Indian agencies waste money on SDRs cold-calling receptionists or sending dead emails.
- Contrast table or bullet points comparing Old Outbound (Apollo/IG scrapers/calls) vs New Outbound (Direct WhatsApp + 100% ban-proof, zero password requests).
- Offer & CTA: "Want to test this? Comment 'DATA' and your city below — I'll send you 10 verified owner WhatsApp lines for your niche 100% free."
- 130-180 words. Clean LinkedIn formatting. NO explicit pricing numbers.

=== 4. DIRECT OUTBOUND TROJAN HORSE PITCH ===
- A 1-to-1 cold WhatsApp message Ram can send directly to 5 agency founders who serve {niche_info['niche']}.
- Permissionless value: "Hey [Name], ran a live scan across [City] and pulled 3 verified clinic/business owner WhatsApp direct lines this morning: [Lead 1, Lead 2, Lead 3]. Have 30 more in a sheet. Free to test if your team wants?"
- Under 80 words. Zero pitch, 100% value.

=== 5. PIGGYBACK PROTOCOL (TOP CREATORS & READY-TO-PASTE COMMENTS) ===
Select 2-3 top creators relevant to Indian agencies, founders, and growth (choose dynamically from: Vaibhav Sisinty, Saheli Chatterjee, Jasmin Alic, Lara Acosta, Matt Gray, Varun Mayya, Kshitij Ladia, Justin Welsh, Ruben Hassid).
For each creator provide:
• Creator: [Name] | Profile: [linkedin.com/in/handle] | Today's Context: [1 sentence on why their audience cares today]
• Outperforming Comment: A 3-4 line masterclass comment designed to rise to the top of their post.
  Formula:
  1) Immediate pattern interrupt / counter-intuitive agreement.
  2) A hard receipt/data point from real outbound testing in India (e.g., 20–35% WhatsApp reply rates vs 2% cold email spam; SDR headcount costing ₹35k/mo to book 2 calls).
  3) A punchy takeaway or low-friction question that makes other readers like and reply.
  Tone: Authoritative technical operator / builder who shows receipts. No sycophancy (NO "Great post!", NO "Thanks for sharing!"). NO explicit pricing numbers.
"""

def parse_sections(raw_text):
    sections = {
        "directive": "",
        "whatsapp": "",
        "linkedin": "",
        "trojan": "",
        "piggyback": ""
    }
    headers = re.findall(r'===\s*([^=
]+)\s*===', raw_text)
    bodies = re.split(r'===\s*[^=
]+\s*===', raw_text)[1:]

    for h, b in zip(headers, bodies):
        h_lower = h.lower()
        b_clean = b.strip()
        if "directive" in h_lower or "growth stack" in h_lower:
            sections["directive"] = b_clean
        elif "whatsapp" in h_lower:
            sections["whatsapp"] = b_clean
        elif "linkedin" in h_lower:
            sections["linkedin"] = b_clean
        elif "trojan" in h_lower or "outbound" in h_lower:
            sections["trojan"] = b_clean
        elif "piggyback" in h_lower or "creator" in h_lower:
            sections["piggyback"] = b_clean

    if not sections["whatsapp"] and not sections["linkedin"]:
        sections["whatsapp"] = raw_text.strip()

    return sections

def extract_linkedin_links(piggyback_text):
    matches = re.findall(r'(?:https?://)?(?:www\.)?linkedin\.com/in/([a-zA-Z0-9_-]+)', piggyback_text)
    links = []
    seen = set()
    for m in matches:
        if m not in seen:
            seen.add(m)
            links.append((m, f"https://www.linkedin.com/in/{m}"))
    return links

def build_html_email(niche_info, raw_text):
    sections = parse_sections(raw_text)

    directive_html = html.escape(sections["directive"]).replace("\n", "<br>")
    whatsapp_clean = sections["whatsapp"]
    linkedin_clean = sections["linkedin"]
    trojan_clean = sections["trojan"]
    piggyback_clean = sections["piggyback"]

    whatsapp_html = html.escape(whatsapp_clean).replace("\n", "<br>")
    linkedin_html = html.escape(linkedin_clean).replace("\n", "<br>")
    trojan_html = html.escape(trojan_clean).replace("\n", "<br>")
    piggyback_html = html.escape(piggyback_clean).replace("\n", "<br>")

    wa_encoded = urllib.parse.quote(whatsapp_clean)
    wa_url = f"https://wa.me/?text={wa_encoded}"

    li_links = extract_linkedin_links(piggyback_clean)
    creator_buttons_html = ""
    if li_links:
        creator_buttons_html = '<div style="margin-bottom: 12px; display: flex; flex-wrap: wrap; gap: 8px;">'
        for handle, link in li_links:
            creator_buttons_html += f'<a href="{link}" target="_blank" class="action-btn li-btn">🔗 Open @{html.escape(handle)}</a> '
        creator_buttons_html += '</div>'

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Daily Marketing Brief</title>
<style>
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    background-color: #080c14;
    color: #f1f5f9;
    margin: 0;
    padding: 24px 12px;
  }}
  .container {{
    max-width: 680px;
    margin: 0 auto;
  }}
  .header {{
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
  }}
  .badge-row {{
    margin-bottom: 12px;
  }}
  .badge {{
    display: inline-block;
    padding: 4px 10px;
    border-radius: 9999px;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }}
  .badge-category {{
    background: #2563eb;
    color: #ffffff;
  }}
  .badge-city {{
    background: #1e293b;
    color: #94a3b8;
    border: 1px solid #334155;
    margin-left: 6px;
  }}
  h1 {{
    font-size: 22px;
    font-weight: 800;
    margin: 0 0 8px 0;
    color: #ffffff;
    letter-spacing: -0.02em;
  }}
  .meta-sub {{
    font-size: 12px;
    color: #94a3b8;
    line-height: 1.5;
  }}
  .card {{
    background: #0f172a;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
    border: 1px solid #1e293b;
    box-shadow: 0 4px 12px rgba(0,0,0,0.25);
  }}
  .card-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;
    border-bottom: 1px solid #1e293b;
    padding-bottom: 10px;
  }}
  .card-title {{
    font-size: 14px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }}
  .directive-title {{ color: #c084fc; }}
  .whatsapp-title {{ color: #4ade80; }}
  .linkedin-title {{ color: #38bdf8; }}
  .trojan-title {{ color: #fbbf24; }}
  .piggyback-title {{ color: #2dd4bf; }}

  .action-bar {{
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 8px;
  }}
  .action-btn {{
    display: inline-block;
    padding: 7px 14px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 700;
    text-decoration: none;
    letter-spacing: 0.02em;
  }}
  .wa-btn {{
    background: #22c55e;
    color: #052e16;
  }}
  .li-btn {{
    background: #0284c7;
    color: #ffffff;
  }}
  .copy-pill {{
    display: inline-block;
    font-size: 11px;
    color: #94a3b8;
    background: #1e293b;
    border: 1px solid #334155;
    padding: 4px 8px;
    border-radius: 4px;
    font-weight: 600;
  }}
  .copy-box {{
    background: #080c14;
    border: 1px solid #1e293b;
    border-radius: 8px;
    padding: 16px;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    font-size: 13px;
    line-height: 1.6;
    color: #f1f5f9;
    white-space: pre-wrap;
    word-break: break-word;
    user-select: all !important;
    -webkit-user-select: all !important;
    cursor: pointer;
  }}
  .directive-box {{
    font-size: 13px;
    line-height: 1.65;
    color: #cbd5e1;
  }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div class="badge-row">
      <span class="badge badge-category">{html.escape(niche_info.get('category', 'B2B Outbound'))}</span>
      <span class="badge badge-city">{html.escape(niche_info.get('cities', 'India'))}</span>
    </div>
    <h1>Today's Target: {html.escape(niche_info.get('niche', 'B2B Niche'))}</h1>
    <div class="meta-sub">Deal Size: {html.escape(niche_info.get('ticket', '₹50k-₹2L'))} • Zero SDR Payroll Bloat • Fractional Setup</div>
  </div>

  <!-- Card 1: Directive -->
  <div class="card">
    <div class="card-header">
      <div class="card-title directive-title">🎯 1. Today's 15-Minute Directive & Growth Stack</div>
    </div>
    <div class="directive-box">
      {directive_html}
    </div>
  </div>

  <!-- Card 2: WhatsApp Community Post -->
  <div class="card">
    <div class="card-header">
      <div class="card-title whatsapp-title">📱 2. WhatsApp Community & Group Post (50–80 Words)</div>
    </div>
    <div class="action-bar">
      <a href="{wa_url}" target="_blank" class="action-btn wa-btn">📲 1-Tap Open & Send in WhatsApp</a>
      <span class="copy-pill">📋 Tap Text to Select All</span>
    </div>
    <div class="copy-box">{whatsapp_html}</div>
  </div>

  <!-- Card 3: LinkedIn Authority Post -->
  <div class="card">
    <div class="card-header">
      <div class="card-title linkedin-title">💼 3. LinkedIn Authority Post</div>
    </div>
    <div class="action-bar">
      <a href="https://www.linkedin.com/feed/" target="_blank" class="action-btn li-btn">💼 Open LinkedIn Feed</a>
      <span class="copy-pill">📋 Tap Text to Select All</span>
    </div>
    <div class="copy-box">{linkedin_html}</div>
  </div>

  <!-- Card 4: Trojan Horse Pitch -->
  <div class="card">
    <div class="card-header">
      <div class="card-title trojan-title">⚔️ 4. Direct Outbound Trojan Horse Pitch (Send to 5 Founders)</div>
    </div>
    <div class="action-bar">
      <span class="copy-pill">📋 Tap Text to Select All</span>
    </div>
    <div class="copy-box">{trojan_html}</div>
  </div>

  <!-- Card 5: Piggyback Protocol -->
  <div class="card">
    <div class="card-header">
      <div class="card-title piggyback-title">🚀 5. The Lara Acosta Piggyback Protocol (Top Creators & Comments)</div>
    </div>
    {creator_buttons_html}
    <div class="action-bar">
      <span class="copy-pill">📋 Tap Text to Select All</span>
    </div>
    <div class="copy-box">{piggyback_html}</div>
  </div>
</div>
</body>
</html>"""

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

def send_email(content, niche_info=None, subject=None):
    user = os.environ.get("GMAIL_USER", "busywithram@gmail.com")
    pwd  = os.environ.get("GMAIL_APP_PASSWORD", "tuavhrwqahthbkcj")

    if niche_info is None:
        niche_info = get_daily_niche()

    to_emails_raw = os.environ.get("TO_EMAILS", user)
    recipients = [e.strip() for e in to_emails_raw.split(",") if e.strip()]
    if not recipients:
        recipients = [user]

    if subject is None:
        subject = f"🔥 Daily Marketing Brief & Growth Stack: {niche_info['niche']}"

    msg = EmailMessage()
    msg["From"] = user
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject

    msg.set_content(content)
    html_content = build_html_email(niche_info, content)
    msg.add_alternative(html_content, subtype="html")

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
    status = send_email(post, niche_info=niche)
    print(status)
