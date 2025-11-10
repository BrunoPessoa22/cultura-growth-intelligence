"""
Advanced ROI Calculator - Calculate true profitability, not just CAC.

This gives you CONFIDENCE to scale because you know:
- Which campaigns drive users who actually pay
- Which campaigns drive users who stick around
- What's the TRUE return on ad spend
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)


class ROICalculator:
    """
    Calculate comprehensive ROI metrics for campaign performance analysis.
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize ROI calculator with business metrics.

        Args:
            config: Configuration dictionary with business metrics
        """
        self.config = config or {}

        # Business metrics from config/environment
        self.annual_fee = float(os.getenv('ANNUAL_FEE', '2998'))
        self.discount_rate = float(os.getenv('DISCOUNT_RATE', '0.30'))
        self.target_cac = float(os.getenv('TARGET_CAC', '400'))
        self.target_ltv_cac_ratio = float(os.getenv('TARGET_LTV_CAC_RATIO', '3'))

        # Effective annual revenue after discount
        self.effective_annual_revenue = self.annual_fee * (1 - self.discount_rate)

        logger.info(f"ROI Calculator initialized: Annual Fee={self.annual_fee}, "
                   f"Effective Revenue={self.effective_annual_revenue}, Target CAC={self.target_cac}")

    def calculate_true_roi(
        self,
        campaign_spend: float,
        amplitude_revenue: float,
        retention_data: Optional[Dict] = None,
        days_active: int = 30
    ) -> Dict[str, float]:
        """
        Calculate comprehensive ROI metrics for a campaign.

        Args:
            campaign_spend: Total ad spend
            amplitude_revenue: Actual revenue from Amplitude
            retention_data: Optional dict with retention rates
            days_active: Days the campaign has been running

        Returns:
            Dictionary with ROI metrics:
                - immediate_roi: Revenue / Spend ratio (short-term)
                - predicted_roi: Predicted LTV / Spend ratio (long-term)
                - payback_period_days: Days to recoup investment
                - profit_margin: Percentage profit
        """
        roi_metrics = {}

        # Immediate ROI (current revenue vs spend)
        roi_metrics['immediate_roi'] = (
            amplitude_revenue / campaign_spend if campaign_spend > 0 else 0
        )

        # Predict future revenue based on retention
        if retention_data:
            predicted_ltv = self.predict_ltv(
                amplitude_revenue / max(retention_data.get('users', 1), 1),  # Revenue per user
                retention_data.get('day_30_retention', 50) / 100,  # Retention rate
                12  # 12 month horizon
            )
            total_predicted_revenue = predicted_ltv * retention_data.get('users', 0)
        else:
            total_predicted_revenue = amplitude_revenue * 1.5  # Conservative estimate

        # Predicted ROI
        roi_metrics['predicted_roi'] = (
            total_predicted_revenue / campaign_spend if campaign_spend > 0 else 0
        )

        # Payback period (days to break even)
        if amplitude_revenue > 0:
            daily_revenue_rate = amplitude_revenue / days_active
            days_to_payback = campaign_spend / daily_revenue_rate if daily_revenue_rate > 0 else 999
            roi_metrics['payback_period_days'] = min(days_to_payback, 999)
        else:
            roi_metrics['payback_period_days'] = 999

        # Profit margin
        roi_metrics['profit_margin'] = (
            ((total_predicted_revenue - campaign_spend) / total_predicted_revenue * 100)
            if total_predicted_revenue > 0 else -100
        )

        return roi_metrics

    def predict_ltv(
        self,
        early_revenue: float,
        retention_rate: float,
        avg_subscription_months: int = 12
    ) -> float:
        """
        Predict lifetime value from early signals.

        Uses retention curve to project future value.

        Args:
            early_revenue: Revenue per user in first period
            retention_rate: 30-day retention rate (0-1)
            avg_subscription_months: Expected subscription length

        Returns:
            Predicted LTV per user
        """
        if early_revenue == 0:
            return 0

        # Model: LTV = Early Revenue + (Retained Revenue over time)
        # Retention decay factor
        monthly_retention = retention_rate ** (30 / 30)  # Normalize to monthly

        # Calculate retained value over subscription period
        retained_value = 0
        for month in range(1, avg_subscription_months):
            decay = monthly_retention ** month
            retained_value += (self.effective_annual_revenue / 12) * decay

        predicted_ltv = early_revenue + retained_value

        return predicted_ltv

    def calculate_scale_confidence(
        self,
        campaign_metrics: Dict,
        cohort_size: int,
        data_days: int
    ) -> Tuple[str, int, str]:
        """
        Calculate confidence score for scaling decision.

        Args:
            campaign_metrics: Dictionary with campaign performance metrics
            cohort_size: Number of users in cohort
            data_days: Days of data available

        Returns:
            Tuple of (confidence_level, confidence_score, reasoning)
            - confidence_level: 'high', 'medium', or 'low'
            - confidence_score: 0-100
            - reasoning: Explanation of confidence level
        """
        score = 0
        reasons = []

        # Factor 1: Data maturity (0-30 points)
        if data_days >= 30:
            score += 30
            reasons.append("30+ days of data")
        elif data_days >= 14:
            score += 20
            reasons.append("14-30 days of data")
        elif data_days >= 7:
            score += 10
            reasons.append("7-14 days of data")
        else:
            reasons.append(f"Only {data_days} days of data")

        # Factor 2: Sample size (0-30 points)
        paid_users = campaign_metrics.get('paying_users', 0)
        if paid_users >= 30:
            score += 30
            reasons.append(f"{paid_users} paid conversions")
        elif paid_users >= 10:
            score += 20
            reasons.append(f"{paid_users} paid conversions")
        elif paid_users >= 5:
            score += 10
            reasons.append(f"{paid_users} paid conversions (small sample)")
        else:
            reasons.append(f"Only {paid_users} paid conversions (very small sample)")

        # Factor 3: Metric stability (0-20 points)
        ltv_cac = campaign_metrics.get('ltv_cac_ratio', 0)
        if ltv_cac >= self.target_ltv_cac_ratio:
            score += 20
            reasons.append(f"Strong LTV:CAC of {ltv_cac:.1f}x")
        elif ltv_cac >= self.target_ltv_cac_ratio * 0.7:
            score += 10
            reasons.append(f"Moderate LTV:CAC of {ltv_cac:.1f}x")
        else:
            reasons.append(f"Low LTV:CAC of {ltv_cac:.1f}x")

        # Factor 4: User quality (0-20 points)
        activation_rate = campaign_metrics.get('activation_rate', 0)
        payment_rate = campaign_metrics.get('payment_rate', 0)

        if activation_rate >= 70 and payment_rate >= 30:
            score += 20
            reasons.append("Excellent user quality metrics")
        elif activation_rate >= 50 and payment_rate >= 20:
            score += 10
            reasons.append("Good user quality metrics")
        else:
            reasons.append("User quality metrics need improvement")

        # Determine confidence level
        if score >= 70:
            confidence_level = "HIGH"
        elif score >= 40:
            confidence_level = "MEDIUM"
        else:
            confidence_level = "LOW"

        reasoning = "; ".join(reasons)

        return confidence_level, score, reasoning

    def calculate_campaign_metrics(
        self,
        enriched_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Calculate comprehensive metrics for all campaigns in enriched dataset.

        Args:
            enriched_df: DataFrame with matched Meta and Amplitude data

        Returns:
            DataFrame with additional calculated metrics
        """
        df = enriched_df.copy()

        # Add missing columns with defaults if not present (for Meta-only mode)
        if 'actual_signups' not in df.columns:
            df['actual_signups'] = df.get('conversions', df.get('meta_conversions', 0))
        if 'paying_users' not in df.columns:
            # Use purchases from Meta Ads if available, otherwise 0
            df['paying_users'] = df['purchases'].fillna(0) if 'purchases' in df.columns else 0
        if 'total_revenue' not in df.columns:
            # Estimate revenue from purchases if available
            if 'paying_users' in df.columns and df['paying_users'].sum() > 0:
                df['total_revenue'] = df['paying_users'] * self.effective_annual_revenue
            else:
                df['total_revenue'] = 0
        if 'activated_users' not in df.columns:
            df['activated_users'] = 0

        # Immediate metrics (Day 0-7)
        df['acquisition_cac'] = df['spend'] / df['actual_signups'].replace(0, np.nan)

        # Short-term metrics (Day 7-30) - Use actual purchase CAC from Meta Ads
        df['payment_cac'] = df['spend'] / df['paying_users'].replace(0, np.nan)
        df['true_cac'] = df['payment_cac']  # Alias for clarity
        df['revenue_per_paying_user'] = df['total_revenue'] / df['paying_users'].replace(0, np.nan)

        # Calculate rates (with defaults for Meta-only mode)
        df['activation_rate'] = ((df['activated_users'] / df['actual_signups']) * 100).fillna(0).replace([np.inf, -np.inf], 0)
        df['payment_rate'] = ((df['paying_users'] / df['actual_signups']) * 100).fillna(0).replace([np.inf, -np.inf], 0)

        # Long-term metrics (Predicted)
        # For Meta-only mode, use simple LTV = annual revenue (no retention modeling needed)
        # For Amplitude mode, use retention-based prediction
        df['predicted_ltv'] = df.apply(
            lambda row: (
                self.predict_ltv(
                    row.get('revenue_per_paying_user', 0),
                    row.get('day_30_retention', 0.5) / 100 if row.get('day_30_retention', 0) > 1 else 0.5,  # Convert % to decimal
                    12
                ) if 'day_30_retention' in row and pd.notna(row.get('day_30_retention'))
                else self.effective_annual_revenue  # Simple: use full year revenue for Meta-only
            ) if row.get('paying_users', 0) > 0 else 0,
            axis=1
        )

        df['ltv_cac_ratio'] = df['predicted_ltv'] / df['payment_cac'].replace(0, np.nan)

        df['expected_profit_per_user'] = df['predicted_ltv'] - df['payment_cac']

        # Payback period in months
        monthly_revenue = df['revenue_per_paying_user'] / 12
        df['months_to_breakeven'] = (df['payment_cac'] / monthly_revenue).replace([np.inf, -np.inf], np.nan)

        # Scaling recommendation score
        df['scale_score'] = df.apply(
            lambda row: self._calculate_scale_score(row),
            axis=1
        )

        return df

    def _calculate_scale_score(self, row: pd.Series) -> float:
        """
        Calculate a 0-100 scale score for a campaign.

        High score = good candidate for scaling
        """
        score = 50  # Start neutral

        # LTV:CAC ratio (most important)
        ltv_cac = row.get('ltv_cac_ratio', 0)
        if ltv_cac >= 5:
            score += 30
        elif ltv_cac >= 3:
            score += 20
        elif ltv_cac >= 2:
            score += 10
        else:
            score -= 20

        # User quality
        activation_rate = row.get('activation_rate', 0)
        if activation_rate >= 70:
            score += 10
        elif activation_rate >= 50:
            score += 5

        payment_rate = row.get('payment_rate', 0)
        if payment_rate >= 30:
            score += 10
        elif payment_rate >= 20:
            score += 5

        # Sample size reliability
        paying_users = row.get('paying_users', 0)
        if paying_users >= 30:
            score += 10
        elif paying_users >= 10:
            score += 5
        elif paying_users < 5:
            score -= 10

        # CAC efficiency
        true_cac = row.get('payment_cac', row.get('true_cac', 999))
        if true_cac <= self.target_cac:
            score += 10
        elif true_cac <= self.target_cac * 1.5:
            score += 5
        else:
            score -= 10

        return max(0, min(100, score))  # Clamp to 0-100

    def generate_scaling_recommendations(
        self,
        campaigns_df: pd.DataFrame,
        current_budget: Optional[Dict[str, float]] = None
    ) -> pd.DataFrame:
        """
        Generate specific scaling recommendations for each campaign.

        Args:
            campaigns_df: DataFrame with campaign metrics
            current_budget: Optional dict mapping campaign_name to current daily budget

        Returns:
            DataFrame with scaling recommendations
        """
        recommendations = []

        for idx, campaign in campaigns_df.iterrows():
            rec = {
                'campaign_name': campaign['campaign_name'],
                'current_performance': self._performance_summary(campaign),
                'recommendation': self._get_recommendation(campaign),
                'suggested_budget_change': self._suggest_budget_change(campaign, current_budget),
                'expected_outcome': self._predict_outcome(campaign),
                'risk_level': self._assess_risk(campaign),
                'confidence': campaign.get('data_confidence', 'low')
            }

            recommendations.append(rec)

        return pd.DataFrame(recommendations)

    def _performance_summary(self, campaign: pd.Series) -> str:
        """Generate one-line performance summary."""
        return (
            f"CAC: {campaign.get('payment_cac', 0):.0f} BRL, "
            f"LTV:CAC: {campaign.get('ltv_cac_ratio', 0):.1f}x, "
            f"Pay Rate: {campaign.get('payment_rate', 0):.1f}%"
        )

    def _get_recommendation(self, campaign: pd.Series) -> str:
        """Get scaling recommendation (SCALE/MAINTAIN/PAUSE)."""
        scale_score = campaign.get('scale_score', 50)

        if scale_score >= 70:
            return "SCALE AGGRESSIVELY"
        elif scale_score >= 60:
            return "SCALE CAUTIOUSLY"
        elif scale_score >= 40:
            return "MAINTAIN & MONITOR"
        elif scale_score >= 30:
            return "OPTIMIZE BEFORE SCALING"
        else:
            return "PAUSE OR RESTRUCTURE"

    def _suggest_budget_change(
        self,
        campaign: pd.Series,
        current_budget: Optional[Dict] = None
    ) -> str:
        """Suggest specific budget change."""
        rec = self._get_recommendation(campaign)
        campaign_name = campaign['campaign_name']

        if current_budget and campaign_name in current_budget:
            current = current_budget[campaign_name]

            if "SCALE AGGRESSIVELY" in rec:
                new_budget = current * 3
                return f"{current:.0f} → {new_budget:.0f} BRL/day (+200%)"
            elif "SCALE CAUTIOUSLY" in rec:
                new_budget = current * 1.5
                return f"{current:.0f} → {new_budget:.0f} BRL/day (+50%)"
            elif "MAINTAIN" in rec:
                return f"Keep at {current:.0f} BRL/day"
            else:
                return f"Reduce from {current:.0f} BRL/day or pause"
        else:
            return "Budget data not available"

    def _predict_outcome(self, campaign: pd.Series) -> str:
        """Predict outcome if scaled."""
        paying_users = campaign.get('paying_users', 0)
        payment_rate = campaign.get('payment_rate', 0) / 100
        payment_cac = campaign.get('payment_cac', 999)

        if payment_rate > 0:
            estimated_users_per_1k = (1000 / payment_cac) * payment_rate
            return f"~{estimated_users_per_1k:.0f} paid users per 1,000 BRL spend"
        else:
            return "Insufficient data for prediction"

    def _assess_risk(self, campaign: pd.Series) -> str:
        """Assess risk level of scaling."""
        paying_users = campaign.get('paying_users', 0)
        data_days = campaign.get('days_active', 0)
        ltv_cac = campaign.get('ltv_cac_ratio', 0)

        risk_factors = []

        if paying_users < 10:
            risk_factors.append("small sample size")
        if data_days < 14:
            risk_factors.append("limited time data")
        if ltv_cac < 2:
            risk_factors.append("low profitability")

        if len(risk_factors) == 0:
            return "LOW - Strong metrics, sufficient data"
        elif len(risk_factors) == 1:
            return f"MEDIUM - {risk_factors[0]}"
        else:
            return f"HIGH - {', '.join(risk_factors)}"
