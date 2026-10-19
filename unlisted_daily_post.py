import os
import smtplib
from email.message import EmailMessage
from datetime import datetime
import pytz
import requests

def draft_post():
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        return "ERROR: Missing OPENROUTER_API_KEY"
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
    try:
        r = requests.post(url, headers=headers, json={
            "model": "deepseek/deepseek-chat-v3-0324:free",
            "messages": [{"role":"user","content":prompt}],
            "max_tokens": 800,
            "temperature": 0.7
        }, timeout=180)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
        return f"ERR:{r.status_code}"
    except Exception as e:
        return str(e)

def send_email(content):
    user = os.environ.get("GMAIL_USER","busywithram@gmail.com")
    pwd  = os.environ.get("GMAIL_APP_PASSWORD","tuavhrwqahthbkcj")
    msg = EmailMessage()
    msg["From"]=user; msg["To"]=user
    msg["Subject"]="Daily WhatsApp Group Post Draft"
    msg.set_content(content)
    try:
        with smtplib.SMTP("smtp.gmail.com",587) as s:
            s.starttls(); s.login(user,pwd); s.send_message(msg)
        return "ok"
    except Exception as e:
        return str(e)

if __name__=="__main__":
    print(send_email(draft_post()))
