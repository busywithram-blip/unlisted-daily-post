Render Cron Job - Unlisted Daily Post

Files in this directory:
- unlisted_daily_post.py - Main script (drafts post via Gemini or OpenRouter API + emails via Gmail SMTP)
- requirements.txt - Python dependencies (requests, pytz)
- render.yaml - Render cron job config

Render Setup (Free):
1. Go to https://dashboard.render.com
2. Click "New" > "Blueprint"
3. Connect your GitHub repo
4. Render will auto-detect render.yaml and create a Cron Job
5. Add Environment Variables:
   - GEMINI_API_KEY: your_gemini_api_key (recommended)
   - OPENROUTER_API_KEY: your_openrouter_api_key (optional/fallback)
   - GMAIL_USER: busywithram@gmail.com
   - GMAIL_APP_PASSWORD: your_gmail_app_password
   - TO_EMAILS: busywithram@gmail.com (optional, comma-separated for multiple recipients)
6. Cron runs every 4 hours (`0 */4 * * *`).

Note: Supports Google Gemini API (gemini-2.5-flash) and OpenRouter API with automated fallback across free models.
