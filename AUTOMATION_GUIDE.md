# 🤖 Automation Guide - No CSV Imports Needed!

**Automatic data sync** from Meta Ads + Amplitude APIs.

Set it up once, then just run one command to analyze everything!

---

## 🎯 What You Get

### **Before (Manual CSV)**:
1. Export Meta CSV
2. Upload to system
3. Run analysis
4. Repeat weekly...

### **After (Automated)**:
```bash
python main.py sync-all --days 30 --auto-analyze
```
**That's it!** Pulls data from Meta + Amplitude, analyzes, generates report. ✨

---

## 🔑 Step 1: Get Meta Marketing API Credentials (15 minutes)

### **1.1: Create Facebook App**

1. Go to https://developers.facebook.com/apps/
2. Click **Create App**
3. Choose **Business** type
4. Give it a name: "Cultura Growth Intelligence"
5. Click **Create App**

### **1.2: Add Marketing API**

1. In your new app dashboard
2. Click **Add Product**
3. Find **Marketing API** → Click **Set Up**
4. This gives you API access

### **1.3: Get Access Token**

1. In app dashboard, go to **Tools** → **Access Token Tool**
2. Select your ad account
3. Generate token with these permissions:
   - `ads_read`
   - `ads_management`
4. Copy the **Access Token** (starts with `EAA...`)

⚠️ **IMPORTANT**: This token expires! For production, you need a **Long-Lived Token**:

```bash
# Get long-lived token (valid for 60 days)
curl -X GET "https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=YOUR_APP_ID&client_secret=YOUR_APP_SECRET&fb_exchange_token=YOUR_SHORT_TOKEN"
```

### **1.4: Get Your Account ID**

1. Go to https://business.facebook.com/adsmanager
2. Look at URL: `...act=123456789` ← That's your account ID
3. Format: `act_123456789` (add `act_` prefix)

### **1.5: Get App Credentials**

1. In Facebook App dashboard
2. **Settings** → **Basic**
3. Copy:
   - **App ID**
   - **App Secret** (click "Show")

---

## 🔑 Step 2: Configure Environment Variables

Edit your `.env` file:

```bash
# Anthropic (already have)
ANTHROPIC_API_KEY=sk-ant-api03-...

# Amplitude (need Secret Key)
AMPLITUDE_API_KEY=ampex_nUb2ss0LArLnr1f0_...
AMPLITUDE_SECRET_KEY=YOUR_SECRET_KEY_HERE  # ← FIND THIS

# Meta Marketing API (new!)
META_ACCESS_TOKEN=EAA...your_long_lived_token
META_APP_ID=1234567890
META_APP_SECRET=abc123...
META_AD_ACCOUNT_ID=act_1234567890
```

### **Finding Amplitude Secret Key:**

1. Go to https://analytics.amplitude.com
2. **Settings** (gear icon) → **Projects**
3. Select your project
4. **API Keys** tab
5. You'll see:
   - API Key: `ampex_...` ✅ (you have this)
   - **Secret Key**: Long string ← Look for this!

---

## 🚀 Step 3: Install Dependencies

```bash
cd /Users/bruno.pessoa/Desktop/ai-AD-inteligence/cultura-growth-intelligence
source venv/bin/activate

# Install Meta Marketing API SDK
pip install facebook-business

# Or reinstall all requirements
pip install -r requirements.txt
```

---

## ✨ Step 4: Test the Automation!

### **Test Meta API Connection**:

```bash
python -c "from src.ingestion.meta_ads_api import MetaAdsAPI; client = MetaAdsAPI(); client.test_connection()"
```

Expected output:
```
✅ Connected to Meta Ads Account: Cultura Builder
   Currency: BRL
   Timezone: America/Sao_Paulo
```

### **Run Full Automated Sync**:

```bash
# Sync last 30 days + auto-analyze
python main.py sync-all --days 30 --auto-analyze
```

Expected output:
```
🔄 Automated Data Sync

📊 Syncing Meta Ads data...
✅ Synced 12 campaigns from Meta Ads

📈 Syncing Amplitude data...
✅ Synced 8 cohorts from Amplitude

💾 Saving to database...
✅ Data saved to database

🤖 Running AI analysis...
✅ AI analysis complete

📊 AI INSIGHTS
[Full Claude analysis with recommendations]

✅ Report saved: reports/auto_sync_20241110_143022.md
```

---

## 🔄 Automation Options

### **Option 1: Manual Run (Whenever You Want)**

```bash
python main.py sync-all --days 30 --auto-analyze
```

### **Option 2: Weekly Automation (Monday Mornings)**

Create a cron job (Mac/Linux) or Task Scheduler (Windows):

**Mac/Linux cron:**
```bash
# Edit crontab
crontab -e

# Add this line (runs every Monday at 9 AM)
0 9 * * 1 cd /Users/bruno.pessoa/Desktop/ai-AD-inteligence/cultura-growth-intelligence && ./venv/bin/python main.py sync-all --days 7 --auto-analyze
```

**Windows Task Scheduler:**
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Weekly, Monday, 9:00 AM
4. Action: Start a program
5. Program: `C:\path\to\venv\Scripts\python.exe`
6. Arguments: `main.py sync-all --days 7 --auto-analyze`
7. Start in: `C:\path\to\cultura-growth-intelligence`

### **Option 3: Daily Quick Check**

```bash
# Sync just yesterday's data
python main.py sync-all --days 1
```

---

## 📊 What Gets Synced Automatically

### **From Meta Ads API:**
- ✅ Campaign names
- ✅ Spend (BRL)
- ✅ Impressions
- ✅ Clicks
- ✅ Conversions
- ✅ CTR, CPC, CPM
- ✅ Campaign objectives

### **From Amplitude API:**
- ✅ User signups by campaign
- ✅ Activation events
- ✅ Payment events
- ✅ Retention rates (7/14/30 day)
- ✅ Revenue per cohort

### **Generated Automatically:**
- ✅ Campaign matching (Meta → Amplitude)
- ✅ True CAC calculations
- ✅ LTV predictions
- ✅ ROI metrics
- ✅ AI analysis with recommendations
- ✅ Markdown report saved to `reports/`

---

## 🎯 Example Workflow

### **Monday Morning Routine:**

```bash
cd /Users/bruno.pessoa/Desktop/ai-AD-inteligence/cultura-growth-intelligence
source venv/bin/activate

# Pull last week's data + analyze
python main.py sync-all --days 7 --auto-analyze

# Open dashboard to review visually
python main.py dashboard

# Check the report
cat reports/auto_sync_*.md | tail -100
```

**Time:** 5 minutes (vs 30+ minutes with manual CSV exports)

---

## 🔧 Troubleshooting

### **"Meta API credentials not found"**
→ Check your `.env` file has all 4 Meta variables:
- META_ACCESS_TOKEN
- META_APP_ID
- META_APP_SECRET
- META_AD_ACCOUNT_ID

### **"Access token expired"**
→ Meta tokens expire. Generate new long-lived token:
```bash
curl -X GET "https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=YOUR_APP_ID&client_secret=YOUR_APP_SECRET&fb_exchange_token=YOUR_OLD_TOKEN"
```
Copy new token to `.env`

### **"Amplitude Secret Key not found"**
→ Go to Amplitude → Settings → Projects → API Keys
→ Look for "Secret Key" (different from API Key)

### **"No campaigns synced"**
→ Check date range: `--days 30` might be too far back if campaigns are new
→ Try: `python main.py sync-all --days 7`

---

## 💡 Pro Tips

### **1. Incremental Syncs**
```bash
# Daily: Just sync yesterday
python main.py sync-all --days 1

# Weekly: Sync last 7 days
python main.py sync-all --days 7 --auto-analyze
```

### **2. Historical Backfill**
```bash
# One-time: Pull last 90 days
python main.py sync-all --days 90 --auto-analyze
```

### **3. Compare Before/After**
```bash
# Sync last 60 days, AI will compare periods
python main.py sync-all --days 60 --auto-analyze
```

### **4. Schedule Email Reports**

Combine with email tool:
```bash
python main.py sync-all --days 7 --auto-analyze && \
  cat reports/auto_sync_latest.md | mail -s "Weekly Growth Report" you@email.com
```

---

## 🎉 You're Done!

### **Before:**
- ❌ Manual CSV exports
- ❌ 30 minutes per week
- ❌ Easy to forget
- ❌ Data gets stale

### **After:**
- ✅ One command: `python main.py sync-all --auto-analyze`
- ✅ 30 seconds
- ✅ Can automate completely
- ✅ Always fresh data

---

## 📚 Additional Commands

```bash
# Just sync, don't analyze
python main.py sync-all --days 30

# Sync + analyze + open dashboard
python main.py sync-all --days 30 --auto-analyze && python main.py dashboard

# Check what's in the database
python -c "from src.database.db import get_database; db = get_database(); print(f'Total campaigns: {len(db.get_campaign_history(\"ALL\", 90))}')"
```

---

**Now you have a FULLY AUTOMATED growth intelligence system!** 🚀

No more CSV exports. Just run one command and get AI-powered insights.

Questions? Check the main README.md or QUICKSTART.md.
