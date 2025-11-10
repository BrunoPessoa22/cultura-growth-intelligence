"""
AI-Powered Campaign Analysis using Claude Sonnet 4.

THE BRAIN OF THE SYSTEM - Uses Claude to analyze campaigns with FULL context:
- Ad spend and CAC
- Actual user quality metrics from Amplitude
- Retention and revenue data
- Cohort comparisons

Provides SPECIFIC, ACTIONABLE recommendations with confidence levels.
"""

import anthropic
import pandas as pd
import logging
import os
import json
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class CampaignAnalyzer:
    """
    AI-powered campaign analyzer using Claude Sonnet 4.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize campaign analyzer with Anthropic API.

        Args:
            api_key: Optional Anthropic API key (defaults to env var)
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')

        if not self.api_key:
            raise ValueError(
                "Anthropic API key not found. "
                "Set ANTHROPIC_API_KEY environment variable."
            )

        self.client = anthropic.Anthropic(api_key=self.api_key)

        # Business context
        self.business_context = {
            'company': 'Cultura Builder',
            'product': 'AI education platform in Brazil',
            'pricing': f"{os.getenv('ANNUAL_FEE', '2998')} BRL annual subscription",
            'effective_price': f"~{float(os.getenv('ANNUAL_FEE', '2998')) * (1 - float(os.getenv('DISCOUNT_RATE', '0.30')))} BRL after {float(os.getenv('DISCOUNT_RATE', '0.30')) * 100}% discount",
            'target_cac': f"{os.getenv('TARGET_CAC', '400')} BRL",
            'target_ltv_cac': f"{os.getenv('TARGET_LTV_CAC_RATIO', '3')}-4x",
            'goal': 'Scale from 10k to 30-40k BRL/month with confidence'
        }

    def analyze_campaigns(
        self,
        enriched_df: pd.DataFrame,
        focus: str = "scaling"
    ) -> Dict[str, Any]:
        """
        Run comprehensive AI analysis on campaign data.

        Args:
            enriched_df: DataFrame with enriched campaign metrics
            focus: Analysis focus ('scaling', 'quality', 'patterns', 'all')

        Returns:
            Dictionary with AI insights and recommendations
        """
        logger.info(f"Running AI analysis with focus: {focus}")

        # Prepare data summary for Claude
        data_summary = self._prepare_data_summary(enriched_df)

        # Build the prompt
        prompt = self._build_analysis_prompt(data_summary, focus)

        # Call Claude
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                temperature=0.3,  # Lower temperature for more consistent analysis
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            analysis_text = response.content[0].text

            # Parse and structure the response
            analysis = self._parse_analysis(analysis_text, enriched_df)

            logger.info("AI analysis complete")

            return analysis

        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            raise

    def _prepare_data_summary(self, df: pd.DataFrame) -> str:
        """
        Prepare campaign data summary for Claude.
        """
        summary_parts = []

        summary_parts.append("=== CAMPAIGN PERFORMANCE DATA ===\n")

        # Sort by performance score
        df_sorted = df.sort_values('efficiency_score', ascending=False) if 'efficiency_score' in df.columns else df

        for idx, campaign in df_sorted.head(20).iterrows():  # Top 20 campaigns
            campaign_summary = f"""
Campaign: {campaign.get('campaign_name', 'Unknown')}
---
AD METRICS:
- Spend: {campaign.get('spend', 0):.2f} BRL
- Impressions: {campaign.get('impressions', 0):,.0f}
- Meta Conversions: {campaign.get('meta_conversions', 0):.0f}
- Meta CAC: {campaign.get('meta_cac', 0):.2f} BRL

USER ACQUISITION:
- Actual Signups: {campaign.get('actual_signups', 0):.0f}
- Acquisition CAC: {campaign.get('acquisition_cac', 0):.2f} BRL

USER QUALITY:
- Activation Rate: {campaign.get('activation_rate', 0):.1f}%
- Activated Users: {campaign.get('activated_users', 0):.0f}
- Payment Rate: {campaign.get('payment_rate', 0):.1f}%
- Paying Users: {campaign.get('paying_users', 0):.0f}

REVENUE & ROI:
- Total Revenue: {campaign.get('total_revenue', 0):.2f} BRL
- True CAC: {campaign.get('true_cac', 0):.2f} BRL
- Revenue/User: {campaign.get('revenue_per_user', 0):.2f} BRL
- Predicted LTV: {campaign.get('predicted_ltv', 0):.2f} BRL
- LTV:CAC Ratio: {campaign.get('ltv_cac_ratio', 0):.2f}x

RETENTION:
- 7-day: {campaign.get('day_7_retention', 0):.1f}%
- 14-day: {campaign.get('day_14_retention', 0):.1f}%
- 30-day: {campaign.get('day_30_retention', 0):.1f}%

DATA QUALITY:
- Confidence: {campaign.get('data_confidence', 'unknown')}
- Flags: {campaign.get('quality_flags', 'none')}
- Efficiency Score: {campaign.get('efficiency_score', 0):.1f}/100

"""
            summary_parts.append(campaign_summary)

        return "\n".join(summary_parts)

    def _build_analysis_prompt(self, data_summary: str, focus: str) -> str:
        """
        Build comprehensive analysis prompt for Claude.
        """
        context = f"""You are an expert growth marketing analyst for {self.business_context['company']}.

BUSINESS CONTEXT:
- Product: {self.business_context['product']}
- Pricing: {self.business_context['pricing']}
- Effective Price: {self.business_context['effective_price']}
- Target CAC: {self.business_context['target_cac']}
- Target LTV:CAC: {self.business_context['target_ltv_cac']}
- Goal: {self.business_context['goal']}

Your task is to analyze paid marketing campaigns with FULL CONTEXT - not just ad metrics,
but actual user behavior: activation, payment, retention, and revenue.

CAMPAIGN DATA:
{data_summary}

ANALYSIS REQUIRED:

1. SCALING RECOMMENDATIONS (MOST IMPORTANT)
For each campaign, provide SPECIFIC recommendations:
- Should we scale? By how much? (exact budget recommendations)
- Confidence level: HIGH/MEDIUM/LOW (with reasoning)
- Expected outcomes (specific numbers)
- Risk assessment
- Next steps

BE SPECIFIC:
✅ "Scale Campaign X from 50 → 250 BRL/day"
✅ "Campaign has 206 BRL CAC, 85% activation, 45% payment rate"
✅ "Early cohort shows 2,400 BRL LTV = 11.6x LTV:CAC"
✅ "Confidence: HIGH - 30 days data, 42 paid users, stable metrics"

❌ NOT: "Consider increasing budget on high performers"
❌ NOT: "Campaign looks good"

2. USER QUALITY INSIGHTS
- Which campaigns drive the BEST users? (high retention, revenue)
- Are there high CAC but high LTV campaigns? (worth it!)
- Are there low CAC but poor retention campaigns? (not worth it!)
- Patterns in activation → payment funnel

3. PATTERN RECOGNITION
- What messaging/angles work best?
- What audience types perform best?
- Are there clear winners we should double down on?
- Are there experiments worth trying?

4. TESTING STRATEGY
- What should we test next?
- Which channels to expand to?
- What targeting to try?
- What creative approaches to explore?

5. RISK ASSESSMENT
- What are we spending on that doesn't work?
- Where are we leaving money on the table?
- What's the audience saturation risk?
- Where could quality degrade if we scale?

CONFIDENCE SCORING:
- HIGH: 30+ days data, 30+ conversions, stable metrics, clear patterns
- MEDIUM: 14-30 days data, 10-30 conversions, some variance
- LOW: <14 days data, <10 conversions, high variance

Provide actionable, data-driven recommendations that give confidence to scale.
"""

        return context

    def _parse_analysis(self, analysis_text: str, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Parse Claude's analysis into structured format.
        """
        analysis = {
            'full_analysis': analysis_text,
            'timestamp': pd.Timestamp.now().isoformat(),
            'campaigns_analyzed': len(df),
            'total_spend': df['spend'].sum() if 'spend' in df.columns else 0,
            'total_revenue': df['total_revenue'].sum() if 'total_revenue' in df.columns else 0,
        }

        # Extract structured recommendations (simple parsing)
        # In production, you might use Claude with structured output or JSON mode

        lines = analysis_text.split('\n')

        # Extract campaigns mentioned for scaling
        scaling_campaigns = []
        for line in lines:
            if 'SCALE' in line.upper() and 'BRL/day' in line:
                scaling_campaigns.append(line.strip())

        analysis['scaling_recommendations'] = scaling_campaigns

        # Calculate summary metrics
        high_performers = df[df.get('ltv_cac_ratio', 0) >= 5] if 'ltv_cac_ratio' in df.columns else pd.DataFrame()
        analysis['high_performers_count'] = len(high_performers)

        return analysis

    def generate_weekly_report(
        self,
        enriched_df: pd.DataFrame,
        previous_week_df: Optional[pd.DataFrame] = None
    ) -> str:
        """
        Generate weekly performance report with week-over-week comparisons.

        Args:
            enriched_df: Current week data
            previous_week_df: Optional previous week data for comparison

        Returns:
            Formatted weekly report (markdown)
        """
        logger.info("Generating weekly report")

        report_sections = []

        # Header
        report_sections.append("# 📊 Weekly Growth Intelligence Report")
        report_sections.append(f"**Generated:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}\n")

        # Executive Summary
        report_sections.append("## 🎯 Executive Summary\n")

        total_spend = enriched_df['spend'].sum()
        total_revenue = enriched_df['total_revenue'].sum()
        total_paying = enriched_df['paying_users'].sum()
        avg_ltv_cac = enriched_df['ltv_cac_ratio'].mean()

        report_sections.append(f"- **Total Spend:** {total_spend:,.2f} BRL")
        report_sections.append(f"- **Total Revenue:** {total_revenue:,.2f} BRL")
        report_sections.append(f"- **Paying Users:** {total_paying:.0f}")
        report_sections.append(f"- **Avg LTV:CAC:** {avg_ltv_cac:.2f}x")
        report_sections.append(f"- **ROI:** {(total_revenue / total_spend * 100):.1f}%\n")

        # Top Performers
        report_sections.append("## 🏆 Top Performing Campaigns\n")

        top_campaigns = enriched_df.nlargest(5, 'ltv_cac_ratio') if 'ltv_cac_ratio' in enriched_df.columns else enriched_df.head(5)

        for idx, campaign in top_campaigns.iterrows():
            report_sections.append(f"### {campaign['campaign_name']}")
            report_sections.append(f"- LTV:CAC: **{campaign.get('ltv_cac_ratio', 0):.2f}x**")
            report_sections.append(f"- True CAC: {campaign.get('true_cac', 0):.2f} BRL")
            report_sections.append(f"- Payment Rate: {campaign.get('payment_rate', 0):.1f}%")
            report_sections.append(f"- Paying Users: {campaign.get('paying_users', 0):.0f}\n")

        # Run AI analysis
        analysis = self.analyze_campaigns(enriched_df, focus="scaling")

        report_sections.append("## 🤖 AI Analysis\n")
        report_sections.append(analysis['full_analysis'])

        return "\n".join(report_sections)


def analyze_campaigns(
    enriched_df: pd.DataFrame,
    api_key: Optional[str] = None,
    focus: str = "scaling"
) -> Dict[str, Any]:
    """
    Convenience function to analyze campaigns with AI.

    Args:
        enriched_df: DataFrame with enriched campaign data
        api_key: Optional Anthropic API key
        focus: Analysis focus

    Returns:
        Analysis results dictionary
    """
    analyzer = CampaignAnalyzer(api_key)
    return analyzer.analyze_campaigns(enriched_df, focus)
