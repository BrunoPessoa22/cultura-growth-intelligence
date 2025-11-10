# 🚀 Cultura Growth Intelligence

**Advanced paid marketing analysis system with TRUE ROI tracking**

Stop guessing. Start scaling with confidence.

## 🎯 What Problem Does This Solve?

You're running Meta Ads and you see:
- ✅ "Campaign #7: 100 conversions, 206 BRL CAC"

But you don't know:
- ❓ Did those users actually **USE** your product?
- ❓ Did they actually **PAY**?
- ❓ Are they still **ACTIVE** 30 days later?
- ❓ Should you **SCALE** this campaign?

**This tool answers those questions** by combining:
1. **Meta Ads data** (spend, impressions, platform conversions)
2. **Amplitude Analytics data** (actual user behavior, activation, payment, retention)
3. **AI analysis** (Claude Sonnet 4 providing specific scaling recommendations)

## ⚡ What Makes This Different

### Before (Standard Analytics)
```
Campaign #7
- Spend: 1,236 BRL
- Meta CAC: 206 BRL
- Conversions: 6

Should I scale? 🤷
```

### After (Cultura Growth Intelligence)
```
Campaign #7: VENDA-EMPREENDEDORES
📊 Ad Metrics:
   - Spend: 1,236 BRL
   - Meta Conversions: 42

👥 Actual Users:
   - Signups: 42
   - Activated: 36 (85% activation rate)
   - Paying: 19 (45% payment rate)

💰 TRUE Metrics:
   - True CAC: 206 BRL ✅
   - Revenue: 12,600 BRL
   - Revenue/User: 2,100 BRL

📈 Quality Metrics:
   - 7-day retention: 78% ✅
   - 30-day retention: 62% ✅
   - Predicted LTV: 2,400 BRL

🎯 ROI Analysis:
   - LTV:CAC Ratio: 11.6x ✅✅✅
   - Payback Period: 12 days
   - Efficiency Score: 89/100

🚀 RECOMMENDATION:
   → SCALE AGGRESSIVELY
   → From 50 → 250 BRL/day
   → Confidence: HIGH (30 days data, 42 users, stable metrics)
   → Expected: +15 paid users/month at ~220 BRL CAC
   → Risk: LOW (audience supports 400/day before saturation)

Now you have PERMISSION to scale! 🎉
```

## 🏗️ Architecture

```
┌─────────────────┐         ┌──────────────────┐
│   Meta Ads CSV  │         │ Amplitude API    │
│   (Ad Metrics)  │         │ (User Behavior)  │
└────────┬────────┘         └────────┬─────────┘
         │                           │
         │                           │
         ▼                           ▼
    ┌────────────────────────────────────┐
    │     Data Matcher & Enricher        │
    │  (Match campaigns to user cohorts) │
    └────────────┬───────────────────────┘
                 │
                 ▼
    ┌────────────────────────────────────┐
    │       ROI Calculator               │
    │  (True CAC, LTV, LTV:CAC ratio)    │
    └────────────┬───────────────────────┘
                 │
                 ▼
    ┌────────────────────────────────────┐
    │    AI Analyzer (Claude Sonnet 4)   │
    │  (Specific scaling recommendations)│
    └────────────┬───────────────────────┘
                 │
         ┌───────┴────────┐
         ▼                ▼
    ┌─────────┐    ┌──────────────┐
    │   CLI   │    │  Dashboard   │
    │ Reports │    │  (Streamlit) │
    └─────────┘    └──────────────┘
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or navigate to project
cd cultura-growth-intelligence

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```bash
# Required for AI analysis
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Required for Amplitude integration
AMPLITUDE_API_KEY=your_amplitude_api_key_here
AMPLITUDE_SECRET_KEY=your_amplitude_secret_key_here

# Business metrics (already configured for Cultura Builder)
ANNUAL_FEE=2998
DISCOUNT_RATE=0.30
TARGET_CAC=400
```

### 3. Run Your First Analysis

```bash
# Analyze Meta Ads data (without Amplitude)
python main.py analyze --file data/your_meta_export.csv

# Analyze with Amplitude integration (RECOMMENDED)
python main.py analyze --file data/your_meta_export.csv --amplitude --days 30

# Launch interactive dashboard
python main.py dashboard
```

## 📊 Features

### 1. **CLI Analysis**
```bash
# Comprehensive analysis with AI recommendations
python main.py analyze --file data/meta_oct_nov.csv --amplitude --days 30

# Detailed cohort analysis for specific campaign
python main.py cohorts --campaign "VENDA-EMPREENDEDORES" --days 30

# Compare multiple campaigns
python main.py compare --campaigns "Campaign-7,Campaign-8,Campaign-9"

# Sync Amplitude data to local database
python main.py sync-amplitude --days 90
```

### 2. **Interactive Dashboard**

Launch with: `python main.py dashboard`

**Tabs:**

1. **🎯 Scaling Decisions** (MOST IMPORTANT)
   - Decision cards for each campaign
   - Clear SCALE/MAINTAIN/PAUSE recommendations
   - Confidence levels with reasoning
   - Expected outcomes and risk assessment

2. **📊 Campaign Comparison**
   - Side-by-side metrics table
   - Color-coded by performance
   - Interactive charts
   - LTV:CAC scatter plots

3. **🔍 Cohort Analysis**
   - User funnel visualization
   - Signup → Activation → Payment → Retention
   - Identify drop-off points
   - Compare cohorts over time

4. **🔥 User Quality Heatmap**
   - Visual comparison of campaign quality
   - Activation, payment, retention metrics
   - Spot patterns quickly

5. **🤖 AI Insights**
   - Full Claude analysis
   - Specific scaling recommendations
   - Pattern recognition
   - Testing strategy

6. **💰 Scaling Simulator**
   - "What if" scenario planning
   - Estimate CAC change when scaling
   - Risk assessment
   - Confidence scoring

### 3. **AI-Powered Analysis**

Uses **Claude Sonnet 4** to analyze campaigns with FULL context:

✅ **Specific recommendations:**
- "Scale Campaign #7 from 50 → 250 BRL/day"
- "Campaign has 206 BRL CAC, 85% activation, 45% payment rate"
- "Confidence: HIGH - 30 days data, 42 paid users"

❌ **NOT vague:**
- ~~"Consider increasing budget"~~
- ~~"Campaign looks good"~~

### 4. **Historical Tracking**

Database stores:
- Campaign performance over time
- User cohort metrics
- AI analysis results
- Scaling decisions and outcomes

**Learn from past decisions:**
- Did scaling work as expected?
- Did CAC increase when we scaled?
- Which patterns predict success?

## 📈 Use Cases

### Weekly Analysis Workflow

**Monday Morning:**
```bash
# 1. Export Meta Ads data from last week
# 2. Run analysis
python main.py analyze --file data/meta_this_week.csv --amplitude --days 7

# 3. Review recommendations
# 4. Make scaling decisions
# 5. Launch dashboard for team review
python main.py dashboard
```

### Scaling Decision

**Before making a change:**
```bash
# 1. Analyze specific campaign
python main.py cohorts --campaign "YOUR-CAMPAIGN-NAME" --days 30

# 2. Check confidence level
# 3. Review AI recommendation
# 4. Use simulator to test scenarios
```

### Performance Deep Dive

**When investigating poor performance:**
```bash
# 1. Compare underperforming campaign to winners
python main.py compare --campaigns "Winner-A,Winner-B,Underperformer-C"

# 2. Check cohort funnel to find drop-off
# 3. Review AI insights for patterns
```

## 🔑 Key Metrics Explained

| Metric | Description | Good Target |
|--------|-------------|-------------|
| **Acquisition CAC** | Spend / Signups | < 100 BRL |
| **True CAC** | Spend / Paying Users | < 400 BRL |
| **Activation Rate** | % who start using product | > 70% |
| **Payment Rate** | % who become paying customers | > 30% |
| **LTV:CAC Ratio** | Lifetime Value / True CAC | > 3x (ideal: 5x+) |
| **30-day Retention** | % still active after 30 days | > 50% |
| **Payback Period** | Months to recoup CAC | < 3 months |
| **Efficiency Score** | Overall campaign quality (0-100) | > 70 |

## 🎯 Cultura Builder Specifics

**Business Model:**
- Annual subscription: 2,998 BRL
- Average discount: 30%
- Effective revenue: ~2,100 BRL per customer

**Targets:**
- Target CAC: 400 BRL
- Target LTV:CAC: 3-4x
- Current spend: ~10k BRL/month
- Goal: Scale to 30-40k BRL/month with confidence

**Key Success Metrics:**
1. True CAC < 400 BRL
2. LTV:CAC Ratio > 3x
3. Payment Rate > 25%
4. 30-day Retention > 50%

## 🛠️ Technical Details

### Stack
- **Python 3.8+**
- **Data Processing:** pandas, numpy
- **AI:** Anthropic Claude Sonnet 4
- **Database:** SQLAlchemy (SQLite/PostgreSQL)
- **Dashboard:** Streamlit, Plotly
- **CLI:** Click, Rich

### Project Structure
```
cultura-growth-intelligence/
├── src/
│   ├── ingestion/
│   │   ├── meta_data.py          # Load Meta Ads data
│   │   ├── amplitude_api.py      # Amplitude integration
│   │   └── data_matcher.py       # Match campaigns to cohorts
│   ├── analysis/
│   │   ├── campaign_analyzer.py  # AI-powered analysis
│   │   └── roi_calculator.py     # ROI calculations
│   └── database/
│       ├── models.py              # Database models
│       └── db.py                  # Database utilities
├── config/
│   └── config.yaml                # Configuration
├── data/                          # CSV files
├── reports/                       # Analysis outputs
├── main.py                        # CLI interface
├── dashboard.py                   # Streamlit dashboard
├── requirements.txt
└── .env
```

## 📚 Getting Amplitude API Keys

1. Log into your Amplitude account
2. Go to **Settings** → **Projects**
3. Select your project
4. Click **API Keys** tab
5. Copy:
   - **API Key** → `AMPLITUDE_API_KEY`
   - **Secret Key** → `AMPLITUDE_SECRET_KEY`

## 🔄 Roadmap

### Phase 1: Core System ✅
- [x] Meta Ads CSV loading
- [x] Amplitude API integration
- [x] Campaign matching
- [x] ROI calculations
- [x] AI analysis
- [x] CLI interface
- [x] Dashboard

### Phase 2: Enhanced Analytics (Coming Soon)
- [ ] Meta Marketing API (live sync)
- [ ] Google Ads integration
- [ ] Automated weekly reports
- [ ] Slack/Email notifications
- [ ] A/B test analysis

### Phase 3: Predictive Intelligence (Future)
- [ ] ML-based LTV prediction
- [ ] Automated scaling suggestions
- [ ] Anomaly detection
- [ ] Budget optimization AI
- [ ] Multi-channel attribution

## 🤝 Contributing

This is a private tool for Cultura Builder. For questions or issues:
- Contact the development team
- Check `/reports` for analysis examples
- Review sample data in `/data`

## 📄 License

Proprietary - Cultura Builder Internal Use Only

---

**Built with ❤️ for Cultura Builder**

*Helping you scale with confidence, not guesswork.*

🚀 **Ready to scale?** Run your first analysis:
```bash
python main.py analyze --file data/your_meta_data.csv --amplitude --days 30
```
