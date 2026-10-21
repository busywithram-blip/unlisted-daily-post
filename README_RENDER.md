Render Cron Job - Unlisted Daily Post

Files in this directory:
- unlisted_daily_post.py - Main script (drafts post via OpenRouter API + emails via Gmail SMTP)
- requirements.txt - Python dependencies (requests, pytz)
- render.yaml - Render cron job config

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

Note: Uses OpenRouter API with automated fallback across free models (e.g. openrouter/free, google/gemma-4-31b-it:free).
