# 🚀 Deployment Guide - Cultura Growth Intelligence

Deploy your dashboard to Streamlit Cloud with Google OAuth authentication and PostgreSQL database for historical tracking.

## Prerequisites

- GitHub account
- Streamlit Cloud account (free tier available at share.streamlit.io)
- PostgreSQL database (recommendations below)
- Google account for OAuth

## Step 1: Database Setup

### Option A: Neon (Recommended - Free Tier)
1. Go to https://neon.tech
2. Sign up for free account
3. Create a new project
4. Copy the connection string (looks like: `postgresql://user:password@host/database`)

### Option B: Supabase (Also Free)
1. Go to https://supabase.com
2. Create new project
3. Get PostgreSQL connection string from Settings > Database

### Option C: Railway (Paid but simple)
1. Go to https://railway.app
2. Create PostgreSQL database
3. Copy connection string

## Step 2: Push to GitHub

```bash
cd /Users/bruno.pessoa/Desktop/ai-AD-inteligence/cultura-growth-intelligence

# Initialize git if not already
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Cultura Growth Intelligence Dashboard"

# Create repository on GitHub (do this in browser first)
# Then connect and push:
git remote add origin https://github.com/YOUR_USERNAME/cultura-growth-intelligence.git
git branch -M main
git push -u origin main
```

## Step 3: Deploy to Streamlit Cloud

1. **Go to https://share.streamlit.io**

2. **Click "New app"**

3. **Connect GitHub:**
   - Repository: `YOUR_USERNAME/cultura-growth-intelligence`
   - Branch: `main`
   - Main file path: `dashboard.py`

4. **Add Secrets (click "Advanced settings" → "Secrets"):**
   
   Paste this in the secrets editor:
   
   ```toml
   # Anthropic API
   ANTHROPIC_API_KEY = "sk-ant-api03-YOUR-KEY-HERE"
   
   # Amplitude Analytics
   AMPLITUDE_API_KEY = "your-amplitude-api-key"
   AMPLITUDE_SECRET_KEY = "your-amplitude-secret-key"
   
   # Business Metrics
   ANNUAL_FEE = "2998"
   DISCOUNT_RATE = "0.30"
   TARGET_CAC = "400"
   
   # Database (from Step 1)
   DATABASE_URL = "postgresql://user:password@host:5432/database"
   ```

5. **Deploy!** Click "Deploy"

## Step 4: Enable Google OAuth

1. In Streamlit Cloud dashboard, go to your app settings

2. **Navigate to "Sharing"**

3. **Enable "Require sign-in"**

4. **Select "Google OAuth"**

5. **Add allowed email domains:**
   - Add your company domain (e.g., `@culturabuilder.com`)
   - Or specific email addresses

6. **Save settings**

## Step 5: Access Your Dashboard

Your dashboard will be available at:
```
https://YOUR_APP_NAME.streamlit.app
```

Only users with allowed email addresses can sign in!

## Features Enabled

✅ **Authentication:** Only your team can access (Google OAuth)
✅ **Historical Tracking:** All analyses saved to PostgreSQL
✅ **Week-over-Week:** Compare performance trends
✅ **AI Insights:** Powered by Claude (Anthropic)
✅ **Professional UI:** Clean, Google Analytics-style design

## Updating the App

Push updates to GitHub:
```bash
git add .
git commit -m "Update dashboard"
git push
```

Streamlit Cloud will automatically redeploy!

## Troubleshooting

### Database Connection Error
- Check DATABASE_URL format
- Ensure database allows connections from Streamlit Cloud IPs
- Test connection string locally first

### Authentication Not Working
- Verify email domain is correct
- Check Google OAuth is enabled in Streamlit Cloud settings
- Users need to accept permissions on first login

### Missing Data
- Ensure CSV upload works
- Check database tables were created
- Verify user_email is being captured

## Support

Questions? Check the code or reach out to the development team.

---

**Built with:**
- Streamlit (UI Framework)
- Anthropic Claude (AI Analysis)
- PostgreSQL (Historical Data)
- Meta Ads API (Campaign Data)
- Amplitude (User Analytics)
