Render Cron Job - Unlisted Daily Post

Files in this directory:
- unlisted_daily_post.py - Main script (drafts post via NVIDIA API + emails via Gmail SMTP)
- requirements.txt - Python dependencies (requests, pytz)
- render.yaml - Render cron job config

Render Setup (Free):
1. Go to https://dashboard.render.com
2. Click "New" > "Blueprint"
3. Connect your GitHub repo (create a new repo and upload these 3 files)
4. Render will auto-detect render.yaml and create a Cron Job
5. Add Environment Variables:
   - NVIDIA_API_KEY: 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
   - GMAIL_USER: busywithram@gmail.com
   - GMAIL_APP_PASSWORD: tuavhrwqahthbkcj
6. Cron runs at 04:30 UTC which is 10:00 AM IST (UTC+5:30). Adjust if needed.

Note: Uses NVIDIA NIM API (meta/llama-3.1-8b-instruct). Free tier varies by model.
