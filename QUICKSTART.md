# 🚀 Quick Start Guide

Get up and running in **30 minutes**.

## ✅ Step 1: Install Dependencies (5 min)

```bash
# Navigate to project
cd cultura-growth-intelligence

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate  # Windows

# Install packages
pip install -r requirements.txt
```

## ✅ Step 2: Configure API Keys (10 min)

### Get Anthropic API Key (for AI analysis)

1. Go to https://console.anthropic.com/
2. Sign up / Log in
3. Go to **API Keys**
4. Create new key
5. Copy the key

### Get Amplitude API Keys (for user behavior data)

1. Log into your Amplitude account
2. **Settings** → **Projects** → Select your project
3. **API Keys** tab
4. Copy:
   - **API Key**
   - **Secret Key**

### Set Up .env File

```bash
# Copy the template
cp .env.example .env

# Edit with your keys
nano .env  # or use any text editor
```

Add your keys:
```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
AMPLITUDE_API_KEY=your-amplitude-api-key
AMPLITUDE_SECRET_KEY=your-amplitude-secret-key
```

Save and close.

## ✅ Step 3: Export Meta Ads Data (5 min)

1. Go to **Meta Ads Manager**
2. Select your campaigns
3. Click **Export** → **Export table data**
4. Choose **CSV** format
5. Save to `data/meta_ads.csv`

**Required columns:**
- Campaign name
- Amount spent (BRL)
- Impressions
- Results (conversions)
- Cost per result

## ✅ Step 4: Run Your First Analysis (10 min)

### Option A: Without Amplitude (Quick Test)

```bash
python main.py analyze --file data/meta_ads.csv
```

This will:
- ✅ Load and analyze Meta Ads data
- ✅ Calculate basic metrics (spend, CAC, efficiency)
- ✅ Show top campaigns
- ❌ No user behavior metrics (activation, retention)

### Option B: With Amplitude (RECOMMENDED)

```bash
python main.py analyze --file data/meta_ads.csv --amplitude --days 30
```

This will:
- ✅ Load Meta Ads data
- ✅ Pull Amplitude user behavior data (last 30 days)
- ✅ Match campaigns to user cohorts
- ✅ Calculate TRUE metrics (activation, payment rate, retention)
- ✅ Calculate LTV:CAC ratios
- ✅ Run AI analysis with Claude
- ✅ Generate specific scaling recommendations

**Output:**
- Report saved to `reports/analysis_TIMESTAMP.md`
- Console shows AI recommendations
- Top campaigns table displayed

## ✅ Step 5: Launch Dashboard

```bash
python main.py dashboard
```

This opens an interactive web dashboard at `http://localhost:8501`

**Features:**
1. Upload Meta CSV
2. Sync Amplitude data
3. View scaling decisions
4. Compare campaigns
5. Analyze cohorts
6. Explore AI insights
7. Simulate scaling scenarios

## 📊 Example Output

After running analysis, you'll see:

```
🚀 Cultura Growth Intelligence - Campaign Analysis

✅ Loaded 12 campaigns from Meta Ads
✅ Retrieved 8 cohorts from Amplitude
✅ Matched 12 campaigns
✅ AI analysis complete

📊 AI INSIGHTS & RECOMMENDATIONS

SCALING RECOMMENDATIONS:

Campaign #7: VENDA-EMPREENDEDORES
→ SCALE AGGRESSIVELY from 50 → 250 BRL/day
   - True CAC: 206 BRL ✅
   - LTV:CAC Ratio: 11.6x ✅✅✅
   - Activation Rate: 85%
   - Payment Rate: 45%
   - Confidence: HIGH (30 days data, 42 paid users)
   - Risk: LOW

Campaign #12: TESTE-JOVENS
→ PAUSE OR RESTRUCTURE
   - True CAC: 760 BRL ❌
   - LTV:CAC Ratio: 2.8x
   - Payment Rate: 12%
   - Confidence: MEDIUM (14 days data, 8 users)
   - Recommendation: Pause and rework messaging

🏆 TOP PERFORMING CAMPAIGNS

┌────────────────────────────────┬──────────┬────────┬──────────┬──────────┐
│ Campaign                        │ Spend    │ CAC    │ Pay Rate │ LTV:CAC  │
├────────────────────────────────┼──────────┼────────┼──────────┼──────────┤
│ VENDA-EMPREENDEDORES           │ 1,236.00 │ 206.00 │ 45.0%    │ 11.60x   │
│ RETARGETING-ENGAJADOS          │   850.00 │ 283.00 │ 38.0%    │  7.20x   │
│ LAL-PAGANTES                   │ 2,100.00 │ 350.00 │ 32.0%    │  5.80x   │
└────────────────────────────────┴──────────┴────────┴──────────┴──────────┘

✅ Report saved to: reports/analysis_20241110_143022.md
```

## 🎯 Weekly Workflow

### Monday Morning Routine:

```bash
# 1. Export last week's Meta data
# (from Meta Ads Manager)

# 2. Run weekly analysis
python main.py analyze \
  --file data/meta_this_week.csv \
  --amplitude \
  --days 7

# 3. Review AI recommendations

# 4. Make scaling decisions

# 5. Launch dashboard for team review
python main.py dashboard

# 6. Track decisions in database
# (automatically saved)
```

## 🆘 Troubleshooting

### "Amplitude API keys not configured"
→ Check your `.env` file has `AMPLITUDE_API_KEY` and `AMPLITUDE_SECRET_KEY`

### "Anthropic API key not found"
→ Check `.env` has `ANTHROPIC_API_KEY`
→ Or skip AI analysis (basic metrics still work)

### "No campaign column found"
→ Your Meta CSV might have different column names
→ Check `src/ingestion/meta_data.py` for supported formats
→ Or rename columns to match expected format

### "Module not found"
→ Make sure virtual environment is activated: `source venv/bin/activate`
→ Reinstall: `pip install -r requirements.txt`

## 🎓 Next Steps

1. **Read the full README.md** for detailed documentation
2. **Explore the dashboard** - try all 6 tabs
3. **Set up weekly analysis** as a recurring task
4. **Track your scaling decisions** - learn what works
5. **Customize business metrics** in `.env` if needed

## 💡 Pro Tips

1. **Run analysis regularly** (weekly) to track trends
2. **Compare time periods** to see if performance is improving
3. **Use the simulator** before making big budget changes
4. **Trust HIGH confidence recommendations** - act on them!
5. **Investigate LOW confidence campaigns** - might need more time/data

## ✨ You're Ready!

You now have a **growth intelligence system** that:
- ✅ Shows TRUE campaign performance (not just ad metrics)
- ✅ Tells you exactly which campaigns to scale (and by how much)
- ✅ Gives you confidence with data-backed recommendations
- ✅ Tracks your decisions and outcomes over time

**Start scaling with confidence!** 🚀

Questions? Issues? Check the README.md or contact the development team.
