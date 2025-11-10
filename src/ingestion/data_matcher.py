"""
Data matching layer - connects ad spend to actual user behavior.

THE CRITICAL PIECE: Meta says "100 conversions" but we need to know:
- How many actually ACTIVATED?
- How many actually PAID?
- Are they still ACTIVE 30 days later?

This module matches Meta campaigns to Amplitude user cohorts and calculates TRUE metrics.
"""

import pandas as pd
import logging
from typing import Dict, List, Optional, Tuple
import re

logger = logging.getLogger(__name__)


class CampaignMatcher:
    """
    Match Meta Ads campaigns to Amplitude user cohorts and calculate true performance metrics.
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize campaign matcher.

        Args:
            config: Configuration dictionary with matching rules
        """
        self.config = config or {}
        self.normalization_rules = self.config.get('matching', {}).get('normalize', [])

    def match_and_enrich_campaigns(
        self,
        meta_df: pd.DataFrame,
        amplitude_cohorts: pd.DataFrame,
        amplitude_revenue: Optional[pd.DataFrame] = None,
        amplitude_retention: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """
        Match Meta campaign data with Amplitude user cohorts and enrich with true metrics.

        This is where the magic happens - we see TRUE performance beyond Meta's numbers.

        Args:
            meta_df: DataFrame from Meta Ads (spend, impressions, Meta conversions)
            amplitude_cohorts: DataFrame from Amplitude (actual user signups by campaign)
            amplitude_revenue: Optional DataFrame with revenue metrics
            amplitude_retention: Optional DataFrame with retention metrics

        Returns:
            Enriched DataFrame with both ad metrics and user behavior metrics:
                - Meta metrics: spend, impressions, meta_conversions, meta_cac
                - True metrics: actual_signups, activated_users, paying_users
                - Quality metrics: activation_rate, payment_rate, retention
                - ROI metrics: true_cac, true_ltv, ltv_cac_ratio
        """
        logger.info("Starting campaign matching and enrichment")

        # Normalize campaign names for matching
        meta_normalized = self._normalize_campaign_names(meta_df.copy())
        amplitude_normalized = self._normalize_campaign_names(amplitude_cohorts.copy())

        # Match campaigns
        merged = self._merge_campaigns(meta_normalized, amplitude_normalized)

        # Enrich with revenue data if available
        if amplitude_revenue is not None:
            revenue_normalized = self._normalize_campaign_names(amplitude_revenue.copy())
            merged = merged.merge(
                revenue_normalized,
                on='campaign_normalized',
                how='left',
                suffixes=('', '_revenue')
            )

        # Enrich with retention data if available
        if amplitude_retention is not None:
            retention_normalized = self._normalize_campaign_names(amplitude_retention.copy())
            merged = merged.merge(
                retention_normalized,
                on='campaign_normalized',
                how='left',
                suffixes=('', '_retention')
            )

        # Calculate true metrics
        enriched = self._calculate_true_metrics(merged)

        # Flag data quality issues
        enriched = self._flag_data_quality(enriched)

        # Clean up temporary columns
        enriched = enriched.drop(columns=['campaign_normalized'], errors='ignore')

        logger.info(f"Matched and enriched {len(enriched)} campaigns")
        logger.info(f"Matched: {enriched['match_status'].value_counts().to_dict()}")

        return enriched

    def _normalize_campaign_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize campaign names for matching.

        Handles variations like:
        - "VENDA-EMPREENDEDORES" vs "venda_empreendedores"
        - Extra whitespace
        - Different UTM parameter formats
        """
        df = df.copy()

        if 'campaign_name' in df.columns:
            campaign_col = 'campaign_name'
        elif 'campaign' in df.columns:
            campaign_col = 'campaign'
        else:
            logger.warning("No campaign column found for normalization")
            return df

        # Create normalized version
        df['campaign_normalized'] = df[campaign_col].astype(str)

        # Apply normalization rules
        for rule in self.normalization_rules:
            if isinstance(rule, dict):
                if 'replace' in rule:
                    for old, new in zip(rule['replace'][::2], rule['replace'][1::2]):
                        df['campaign_normalized'] = df['campaign_normalized'].str.replace(old, new, regex=False)

                if rule.get('lowercase'):
                    df['campaign_normalized'] = df['campaign_normalized'].str.lower()

                if rule.get('trim_whitespace'):
                    df['campaign_normalized'] = df['campaign_normalized'].str.strip()

        # Remove special characters
        df['campaign_normalized'] = df['campaign_normalized'].str.replace(r'[^a-z0-9]', '', regex=True)

        return df

    def _merge_campaigns(
        self,
        meta_df: pd.DataFrame,
        amplitude_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Merge Meta and Amplitude data by campaign name.
        """
        # Merge on normalized campaign name
        merged = meta_df.merge(
            amplitude_df,
            on='campaign_normalized',
            how='outer',
            suffixes=('_meta', '_amplitude'),
            indicator=True
        )

        # Add match status
        merged['match_status'] = merged['_merge'].map({
            'both': 'matched',
            'left_only': 'meta_only',
            'right_only': 'amplitude_only'
        })

        merged = merged.drop(columns=['_merge'])

        # Consolidate campaign name (prefer Meta version)
        if 'campaign_name_meta' in merged.columns:
            merged['campaign_name'] = merged['campaign_name_meta'].fillna(
                merged.get('campaign_name_amplitude', merged.get('campaign_amplitude', ''))
            )
        elif 'campaign_meta' in merged.columns:
            merged['campaign_name'] = merged['campaign_meta'].fillna(
                merged.get('campaign_amplitude', '')
            )

        return merged

    def _calculate_true_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate TRUE performance metrics by combining Meta and Amplitude data.

        This is the key insight:
        - Meta CAC = Spend / Meta Conversions (what Meta SAYS)
        - True CAC = Spend / Actual Paid Users (what ACTUALLY happened)
        - LTV:CAC Ratio = True LTV / True CAC (should we scale this?)
        """
        df = df.copy()

        # Standardize column names from merge
        df['spend'] = df.get('spend', df.get('spend_meta', 0))
        df['meta_conversions'] = df.get('conversions', df.get('conversions_meta', 0))
        df['meta_cac'] = df.get('meta_cac', df.get('meta_cac_meta', 0))

        df['actual_signups'] = df.get('user_count', df.get('user_count_amplitude', 0))
        df['activated_users'] = df.get('activated_users', 0)
        df['paying_users'] = df.get('paying_users', 0)
        df['total_revenue'] = df.get('total_revenue', 0)

        # Calculate rates
        df['activation_rate'] = (
            (df['activated_users'] / df['actual_signups'] * 100)
            .fillna(0)
            .round(1)
        )

        df['payment_rate'] = (
            (df['paying_users'] / df['actual_signups'] * 100)
            .fillna(0)
            .round(1)
        )

        # Calculate TRUE CAC (spend / actual paid users, not just signups)
        df['true_cac'] = (
            (df['spend'] / df['paying_users'])
            .replace([float('inf'), -float('inf')], None)
            .round(2)
        )

        # Calculate acquisition CAC (spend / signups)
        df['acquisition_cac'] = (
            (df['spend'] / df['actual_signups'])
            .replace([float('inf'), -float('inf')], None)
            .round(2)
        )

        # Calculate revenue per user
        df['revenue_per_user'] = (
            (df['total_revenue'] / df['paying_users'])
            .replace([float('inf'), -float('inf')], None)
            .round(2)
        )

        # Calculate predicted LTV (from Amplitude data if available)
        if 'predicted_ltv' in df.columns:
            df['true_ltv'] = df['predicted_ltv']
        else:
            # Simple estimate: current revenue per user
            df['true_ltv'] = df['revenue_per_user']

        # Calculate LTV:CAC ratio
        df['ltv_cac_ratio'] = (
            (df['true_ltv'] / df['true_cac'])
            .replace([float('inf'), -float('inf')], None)
            .round(2)
        )

        # Calculate payback period (months)
        # How many months to recoup CAC?
        monthly_revenue = df['revenue_per_user'] / 12  # Assuming annual subscription
        df['payback_period_months'] = (
            (df['true_cac'] / monthly_revenue)
            .replace([float('inf'), -float('inf')], None)
            .round(1)
        )

        # Calculate efficiency score (combines multiple factors)
        df['efficiency_score'] = self._calculate_efficiency_score(df)

        return df

    def _calculate_efficiency_score(self, df: pd.DataFrame) -> pd.Series:
        """
        Calculate overall efficiency score (0-100) for each campaign.

        Factors:
        - Payment rate (higher is better)
        - LTV:CAC ratio (higher is better)
        - Activation rate (higher is better)
        - 30-day retention (higher is better)
        """
        score = pd.Series(0.0, index=df.index)

        # Payment rate (0-25 points)
        score += (df['payment_rate'].fillna(0) / 100 * 25).clip(0, 25)

        # LTV:CAC ratio (0-35 points) - target is 5x+
        score += ((df['ltv_cac_ratio'].fillna(0) / 5) * 35).clip(0, 35)

        # Activation rate (0-20 points)
        score += (df['activation_rate'].fillna(0) / 100 * 20).clip(0, 20)

        # 30-day retention (0-20 points)
        if 'day_30_retention' in df.columns:
            score += (df['day_30_retention'].fillna(0) * 20).clip(0, 20)

        return score.round(1)

    def _flag_data_quality(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Flag potential data quality issues for review.
        """
        df = df.copy()
        df['quality_flags'] = ''

        # Flag: Campaign in Meta but no Amplitude users
        mask = (df['match_status'] == 'meta_only') & (df['spend'] > 100)
        df.loc[mask, 'quality_flags'] += 'NO_AMPLITUDE_DATA; '

        # Flag: Campaign in Amplitude but no Meta spend
        mask = df['match_status'] == 'amplitude_only'
        df.loc[mask, 'quality_flags'] += 'NO_META_DATA; '

        # Flag: High spend but low signups (possible tracking issue)
        mask = (df['spend'] > 500) & (df['actual_signups'] < 5)
        df.loc[mask, 'quality_flags'] += 'LOW_SIGNUPS_FOR_SPEND; '

        # Flag: Signups but no activations (onboarding issue?)
        mask = (df['actual_signups'] > 10) & (df['activation_rate'] < 20)
        df.loc[mask, 'quality_flags'] += 'LOW_ACTIVATION; '

        # Flag: High activation but low payment (pricing/value issue?)
        mask = (df['activation_rate'] > 70) & (df['payment_rate'] < 10)
        df.loc[mask, 'quality_flags'] += 'ACTIVATION_TO_PAYMENT_GAP; '

        # Flag: Very high CAC (above threshold)
        max_cac = self.config.get('MAX_CAC_ALERT', 600)
        mask = df['true_cac'] > max_cac
        df.loc[mask, 'quality_flags'] += f'HIGH_CAC_ALERT; '

        # Flag: Small sample size (low confidence)
        mask = (df['actual_signups'] < 10) & (df['actual_signups'] > 0)
        df.loc[mask, 'quality_flags'] += 'SMALL_SAMPLE; '

        # Clean up flags
        df['quality_flags'] = df['quality_flags'].str.rstrip('; ')

        # Add confidence level
        df['data_confidence'] = 'low'
        df.loc[df['actual_signups'] >= 10, 'data_confidence'] = 'medium'
        df.loc[df['actual_signups'] >= 30, 'data_confidence'] = 'high'

        return df

    def get_unmatched_campaigns(self, enriched_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get campaigns that didn't match between Meta and Amplitude.

        Returns:
            Tuple of (meta_only_campaigns, amplitude_only_campaigns)
        """
        meta_only = enriched_df[enriched_df['match_status'] == 'meta_only'].copy()
        amplitude_only = enriched_df[enriched_df['match_status'] == 'amplitude_only'].copy()

        return meta_only, amplitude_only


def match_campaigns(
    meta_df: pd.DataFrame,
    amplitude_cohorts: pd.DataFrame,
    amplitude_revenue: Optional[pd.DataFrame] = None,
    amplitude_retention: Optional[pd.DataFrame] = None,
    config: Optional[Dict] = None
) -> pd.DataFrame:
    """
    Convenience function to match and enrich campaign data.

    Args:
        meta_df: Meta Ads campaign data
        amplitude_cohorts: Amplitude user cohorts
        amplitude_revenue: Optional revenue data
        amplitude_retention: Optional retention data
        config: Optional configuration

    Returns:
        Enriched DataFrame with true performance metrics
    """
    matcher = CampaignMatcher(config)
    return matcher.match_and_enrich_campaigns(
        meta_df,
        amplitude_cohorts,
        amplitude_revenue,
        amplitude_retention
    )
