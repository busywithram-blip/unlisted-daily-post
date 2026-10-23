# 🚀 Unlisted Daily Post: Automated B2B Outbound Engine

> **Every morning at 8:00 AM IST**, this automated pipeline generates and emails a 5-card actionable outbound brief tailored to high-ticket Indian agencies and founders.
> Designed to scale **Unlisted** to ₹1,00,000/mo MRR by providing plug-and-play copy, Trojan Horse pitches, and top-creator comment hijacks.

---

## 📬 The 5 Daily Brief Cards

Every email delivers 5 distinct, copy-paste-ready cards directly to your inbox:

| Card | Name | Description | Action Time |
| :--- | :--- | :--- | :--- |
| **🎯 Card 1** | **15-Minute Directive & Growth Stack** | Tactical daily mission, target city, and operational insight. | 2 min read |
| **📱 Card 2** | **WhatsApp Community & Group Post** | Native conversational value drop for agency groups & communities. | 30 sec tap-to-copy |
| **💼 Card 3** | **LinkedIn Authority Post** | High-dwell-time post (teardown, contrast table, or story) formatted for LinkedIn's algorithm. | 60 sec publish |
| **⚔️ Card 4** | **Trojan Horse Outbound Pitch** | 3-line direct message offering a free 10-lead sample batch to 5 agency founders. | 5 min send |
| **🚀 Card 5** | **The Lara Acosta Piggyback Protocol** | 2-3 top creators (Vaibhav Sisinty, Saheli Chatterjee, Jasmin Alic, Lara Acosta) with pre-written, outperforming comments designed to win the #1 pinned spot. | 3 min paste |

---

## 🔄 Rotating Target Niche Engine (10 Verticals)

The generator automatically rotates across 10 high-margin Indian B2B niches:

1. **Performance Agencies** pitching Aesthetic & Dental Clinics (South Delhi, Bandra, Jubilee Hills)
2. **Turnkey Interior & Architecture Studios** (Indiranagar, Whitefield, BKC, Gurugram)
3. **High-Intent UGC Creators & Video Ad Specialists** pitching D2C Brands (Bengaluru, Mumbai, Surat)
4. **E-commerce Growth & Retention Agencies** (Bengaluru, Mumbai, Delhi NCR)
5. **Commercial Real Estate Partners & Luxury Brokers** (Golf Course Road, BKC, HITEC City)
6. **High-End Commercial Video Production Houses** (Mumbai, Bengaluru, Delhi NCR)
7. **B2B Industrial, Capital Equipment & Solar EPC Contractors** (Pune, Coimbatore, Peenya)
8. **Direct-Response Copywriters & Funnel Builders** (National / Remote)
9. **Corporate Training & Boutique Executive HR Consultancies** (Bengaluru, Delhi NCR, Hyderabad)
10. **High-Ticket Luxury Architects & Builders** (Indiranagar, Lavelle Road)

---

## 🔒 The Golden Rule of Pricing

> **No public pricing (e.g. ₹8,000/mo) is ever included in public headlines, posts, or comments.**
> - **Operational Contrast Framing:** All public content compares *full-time SDR headcount & bloated payroll* vs *automated 1-tap fractional pipeline*.
> - **Pricing Wall:** Exact setup fees are only quoted inside private 1-on-1 DM strategy calls after diagnosing the prospect's lead volume.

---

## ⚙️ Architecture & Automation Stack

```
GitHub Actions Cron (02:30 UTC = 8:00 AM IST)
      │
      ▼
Python Daily Generator (unlisted_daily_post.py)
      │
      ├─► Niche Selector (10-Niche Rotation)
      ├─► Multi-Model OpenRouter AI Fallback Chain
      │     1. nvidia/nemotron-3-ultra-550b-a55b:free
      │     2. minimax/minimax-m3.1-flash:free
      │     3. liquid/lfm-2.5-2.6b:free
      │     4. openrouter/free
      │
      ▼
Responsive HTML Email Compiler (Dark Navy UI + user-select: all copy blocks)
      │
      ▼
Gmail SMTP Dispatcher (Direct to busywithram@gmail.com)
```

---

## 🛠️ Local Testing & Manual Dispatch

Run the pipeline manually from your terminal at any time:

```bash
# Set required environment variables
export OPENROUTER_API_KEY="your_key_here"
export GMAIL_USER="busywithram@gmail.com"
export GMAIL_APP_PASSWORD="your_app_password"

# Run generator and send today's email immediately
python unlisted_daily_post.py
```

### Running Unit Tests
```bash
python test_unlisted_daily_post.py
# 10/10 tests pass
```
