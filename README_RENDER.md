Render Cron Job - Unlisted Daily Post

Files in this directory:
- unlisted_daily_post.py - Main script (drafts post via OpenRouter API + emails via Gmail SMTP)
- requirements.txt - Python dependencies (requests, pytz)
- render.yaml - Render cron job config
- POSTS.md - Reference posts and posting guidelines

Render Setup (Free):
1. Go to https://dashboard.render.com
2. Click "New" > "Blueprint"
3. Connect your GitHub repo
4. Render will auto-detect render.yaml and create a Cron Job
5. Add Environment Variables:
   - OPENROUTER_API_KEY: your_openrouter_api_key
   - GMAIL_USER: busywithram@gmail.com
   - GMAIL_APP_PASSWORD: your_gmail_app_password
   - TO_EMAILS: busywithram@gmail.com (optional, comma-separated for multiple recipients)
6. Cron runs at 04:30 UTC which is 10:00 AM IST (UTC+5:30). Adjust if needed.

## System Prompt (v3 - Honest Bot Angle)
- **Angle**: Transparency-first hook ("I run a bot that finds... I found your agency using it.").
- **Structure**: 7 mandatory elements in strict order, including three labeled mechanisms ("It finds the lead", "It writes the message", "It sends in one tap").
- **Zero-Digit Rule**: No numeric digits permitted in the post body to prevent AI hallucination of fake prices, step numbers, or timeframes.
- **Validation**: Strict 10-rule validator enforces length (80-200 words), zero digits, no URLs, no greetings in first line, no sales jargon, and no banned tropes.
- **Repair Pass**: Bounded single-retry repair pass per model if initial output contains minor validation errors.
- **Off-Post Pricing**: Price (Rs 8,000/month) and free-trial window details are handled in DMs rather than the public post.
