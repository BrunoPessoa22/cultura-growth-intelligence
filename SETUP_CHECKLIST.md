# 🚀 Setup Checklist - Get Running in 15 Minutes

## ✅ Step 1: API Keys (5 minutes)

### Anthropic (AI Analysis)
- ✅ **Status:** CONFIGURED
- **Key:** Starts with `sk-ant-api03-...`
- **Where:** https://console.anthropic.com/settings/keys

### Amplitude (User Behavior)
- ⚠️ **Status:** PARTIALLY CONFIGURED (need Secret Key)
- **API Key:** `ampex_...` ✅
- **Secret Key:** NEEDED ⚠️
- **Where to find:**
  1. Go to https://analytics.amplitude.com
  2. Settings → Projects → [Your Project]
  3. API Keys tab
  4. Look for **both** "API Key" and "Secret Key"

---

## ✅ Step 2: Export Meta Ads Data (5 minutes)

**NO API KEY NEEDED!** Just export CSV:

1. Go to **Meta Ads Manager**: https://business.facebook.com/adsmanager
2. Select date range (last 30 days)
3. Select all campaigns you want to analyze
4. Click **Export** button (top right)
5. Choose **Export table data** → **CSV**
6. Save to: `/Users/bruno.pessoa/Desktop/ai-AD-inteligence/cultura-growth-intelligence/data/meta_ads_oct_nov.csv`

**Required columns in export:**
- Campaign name
- Amount spent (BRL)
- Impressions
- Results (conversions)
- Cost per result

---

## ✅ Step 3: Run First Analysis (5 minutes)

```bash
cd /Users/bruno.pessoa/Desktop/ai-AD-inteligence/cultura-growth-intelligence
source venv/bin/activate

# Option A: Meta data only (works now!)
python main.py analyze --file data/meta_ads_oct_nov.csv

# Option B: With Amplitude (once you add Secret Key)
python main.py analyze --file data/meta_ads_oct_nov.csv --amplitude --days 30

# Option C: Launch dashboard
python main.py dashboard
```

---

## 📊 What You'll Get

### With Current Setup (Meta + AI):
✅ Campaign performance analysis
✅ Spend and CAC calculations
✅ AI-powered recommendations
✅ Top performing campaigns
✅ Scaling suggestions

### With Amplitude Added (Full System):
✅ Everything above, PLUS:
✅ Actual user activation rates
✅ Payment conversion rates
✅ Retention metrics (7/14/30 day)
✅ TRUE LTV:CAC ratios
✅ User quality scoring

---

## 🔑 API Keys Summary

| Service | Status | What It Does | Required? |
|---------|--------|--------------|-----------|
| **Anthropic** | ✅ READY | AI analysis & recommendations | ✅ YES |
| **Amplitude API Key** | ✅ READY | User behavior tracking | ⚠️ PARTIAL |
| **Amplitude Secret** | ❌ NEEDED | Required with API Key | ⚠️ PARTIAL |
| **Meta Ads** | 💡 USE CSV | Ad spend & performance | ✅ YES (via CSV) |
| **Google Ads** | 💡 USE CSV | Ad spend (if you use it) | ⬜ Optional |
| **Google Analytics** | ⬜ Optional | Website traffic | ⬜ Optional |

---

## 🎯 CURRENT STATUS: 90% READY!

You can start using the system RIGHT NOW with:
- ✅ Meta Ads CSV export
- ✅ AI analysis working
- ⚠️ Add Amplitude Secret Key for full power

---

## 🚀 Next Actions:

### TODAY (Do This Now):
1. ✅ Export Meta Ads data as CSV
2. ✅ Run analysis: `python main.py analyze --file data/your_file.csv`
3. ✅ See AI recommendations!

### THIS WEEK (When You Have Time):
1. ⚠️ Find Amplitude Secret Key
2. ⚠️ Add to `.env` file
3. ⚠️ Run with `--amplitude` flag
4. ✅ Get full user behavior insights

---

## 💡 Pro Tips:

1. **Start with CSV exports** - No API complexity, works immediately
2. **Weekly analysis** - Export Monday morning, analyze, make decisions
3. **Track outcomes** - System stores history, you learn what works
4. **Dashboard is beautiful** - Run `python main.py dashboard` to see it!

---

## 🆘 Need Help?

- **Can't find Amplitude Secret?** Check Settings → Projects → API Keys
- **Meta export issues?** Make sure you select all relevant columns
- **Analysis errors?** Check the reports/ folder for details
- **Want to see it work?** Use the sample data: `python main.py analyze --file data/sample_meta_ads.csv`

---

**You're 90% there! Just export Meta data and you're ready to analyze!** 🎉
