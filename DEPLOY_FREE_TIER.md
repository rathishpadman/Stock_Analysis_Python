# Deployment Guide - FREE Options (No Surprise Bills)

## 🎯 Recommended: Render.com (Safest)

**Why Render.com?**
- ✅ **No credit card required** - truly free
- ✅ **No timeout limits** - your 50s analysis works fine
- ✅ **750 hours/month free** - enough for always-on
- ⚠️ **Only downside**: 30s cold start after 15min idle

### Deploy to Render.com (5 minutes)

1. **Push code to GitHub** (if not already)
   ```bash
   git add .
   git commit -m "Add deployment files"
   git push
   ```

2. **Go to [render.com](https://render.com)** and sign up (use GitHub)

3. **New → Web Service → Connect your repo**

4. **Settings:**
   - Name: `nifty-agents-api`
   - Region: `Singapore` (closest to India)
   - Branch: `main`
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements_agents.txt`
   - Start Command: `uvicorn nifty_agents.api:app --host 0.0.0.0 --port $PORT`
   - Plan: **Free**

5. **Add Environment Variables** (in Render dashboard):
   - `GOOGLE_API_KEY` = your Gemini API key
   - `GEMINI_MODEL` = `gemini-2.0-flash-exp`
   - `SUPABASE_URL` = your Supabase URL
   - `SUPABASE_KEY` = your Supabase anon key

6. **Deploy!**

You'll get a URL like: `https://nifty-agents-api.onrender.com`

---

## 🔥 Alternative: Firebase Hosting + Cloud Run (with Budget Cap)

If you prefer Google ecosystem:

### Step 1: Set Budget Alert FIRST (Critical!)

```bash
# In Google Cloud Console:
# 1. Go to Billing → Budgets & Alerts
# 2. Create budget: $1 (or $0 for paranoid mode)
# 3. Set alert at 50%, 90%, 100%
# 4. Enable "Disable billing when budget exceeded" (optional nuclear option)
```

### Step 2: After $300 Expires

**Option A - Paranoid Mode:**
```bash
# Disable Cloud Run completely (no charges possible)
gcloud run services delete nifty-agents-api --region=asia-south1
```

**Option B - Keep Running with Limits:**
```bash
# Set max instances to 1 (limits spend)
gcloud run services update nifty-agents-api --max-instances=1
```

### Actual Costs After Free Tier (if you don't disable):
| Usage | Monthly Cost |
|-------|--------------|
| 100 analyses | ~$0.10 |
| 500 analyses | ~$0.50 |
| 1000 analyses | ~$1.00 |

The Python API costs are minimal. **99% of your cost will be Gemini API**, which is separate and has its own free tier.

---

## 📊 Cost Breakdown

| Service | Free Tier | After Free |
|---------|-----------|------------|
| **Gemini API** | $0 (free tier) | ~$0.0005/analysis |
| **Render.com** | 750 hrs/month | Free forever |
| **Vercel** | 100GB bandwidth | Free for dashboard |
| **Supabase** | 500MB, 50K requests | Free tier generous |

**Total monthly cost for light usage: $0**

---

## 🏗️ Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FREE TIER STACK                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Browser                                                   │
│      │                                                      │
│      ▼                                                      │
│   ┌─────────────────────┐                                  │
│   │  VERCEL (FREE)      │                                  │
│   │  Next.js Dashboard  │                                  │
│   │  - No CC required   │                                  │
│   └─────────┬───────────┘                                  │
│             │                                               │
│             ▼                                               │
│   ┌─────────────────────┐      ┌─────────────────────┐    │
│   │  RENDER.COM (FREE)  │ ───► │  GEMINI API         │    │
│   │  FastAPI Backend    │      │  (Free tier or      │    │
│   │  - No CC required   │      │   pay-as-you-go)    │    │
│   │  - No timeout       │      └─────────────────────┘    │
│   └─────────┬───────────┘                                  │
│             │                                               │
│             ▼                                               │
│   ┌─────────────────────┐                                  │
│   │  SUPABASE (FREE)    │                                  │
│   │  - Stock data       │                                  │
│   │  - 500MB storage    │                                  │
│   └─────────────────────┘                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start (Copy-Paste)

### Local Development
```bash
cd "c:\Rathish\Root Folder\Equity research\Stock_Analysis_Python"
.\venv\Scripts\Activate.ps1
python -m uvicorn nifty_agents.api:app --host 0.0.0.0 --port 8000
```

### Deploy to Render
1. Push to GitHub
2. Connect repo at render.com
3. Add env vars
4. Done!

### Deploy Dashboard to Vercel
```bash
cd dashboard
npm run build
npx vercel
```

---

## ❓ FAQ

**Q: What if Render.com free tier ends?**
A: They've had free tier since 2019. If it changes, migrate to Railway ($5 cap) or Fly.io.

**Q: What about Gemini API costs?**
A: Gemini has a generous free tier. After that, ~$0.0005 per analysis. Set up Google Cloud budget alerts.

**Q: Can I use Firebase Functions?**
A: Not recommended - 60 second timeout is too close to your 50s analysis time. Use Cloud Run if you want Google.
