"""
Amplitude Analytics API integration.

THE GAME CHANGER - This module pulls actual user behavior data to understand
which campaigns drive high-quality users who activate, pay, and retain.
"""

import requests
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import time
import os

logger = logging.getLogger(__name__)


class AmplitudeAPI:
    """
    Connect to Amplitude Analytics API to pull user cohort and behavior data.

    This is critical for understanding TRUE campaign performance beyond
    just acquisition metrics.
    """

    BASE_URL = "https://amplitude.com/api/2"

    def __init__(self, api_key: str, secret_key: str):
        """
        Initialize Amplitude API client.

        Args:
            api_key: Amplitude API key (from project settings)
            secret_key: Amplitude secret key (from project settings)
        """
        self.api_key = api_key
        self.secret_key = secret_key
        self.session = requests.Session()
        self.session.auth = (api_key, secret_key)

    def get_user_cohorts(
        self,
        start_date: str,
        end_date: str,
        group_by: List[str] = None
    ) -> pd.DataFrame:
        """
        Pull user cohorts grouped by acquisition source/campaign.

        This shows which campaigns are driving actual user signups.

        Args:
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
            group_by: List of user properties to group by (e.g., ['utm_campaign', 'utm_source'])

        Returns:
            DataFrame with columns:
                - campaign: Campaign identifier
                - user_count: Number of users acquired
                - signup_date: Date of acquisition
                - utm_source, utm_medium, utm_campaign: UTM parameters
        """
        logger.info(f"Fetching user cohorts from {start_date} to {end_date}")

        if group_by is None:
            group_by = ['utm_campaign', 'utm_source', 'utm_medium']

        # Use Amplitude's Dashboard REST API to get user composition
        # https://developers.amplitude.com/docs/dashboard-rest-api

        endpoint = f"{self.BASE_URL}/events/segmentation"

        params = {
            'e': {
                'event_type': os.getenv('AMPLITUDE_SIGNUP_EVENT', 'user_signup')
            },
            'start': start_date,
            'end': end_date,
            'g': ','.join(group_by)  # Group by properties
        }

        try:
            response = self.session.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()

            # Parse response into DataFrame
            cohorts = self._parse_cohort_response(data, group_by)

            logger.info(f"Retrieved {len(cohorts)} cohorts with {cohorts['user_count'].sum()} total users")

            return cohorts

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch user cohorts: {e}")
            raise

    def _parse_cohort_response(self, data: Dict, group_by: List[str]) -> pd.DataFrame:
        """
        Parse Amplitude API response into cohort DataFrame.
        """
        # Amplitude returns data in nested structure
        # This is simplified - actual implementation depends on API response format

        cohorts = []

        if 'data' in data:
            series_data = data['data'].get('series', [])

            for series in series_data:
                cohort = {}

                # Extract grouping properties
                if 'segmentValue' in series:
                    values = series['segmentValue']
                    if isinstance(values, list):
                        for i, prop in enumerate(group_by):
                            cohort[prop] = values[i] if i < len(values) else None

                # Extract user count
                if 'value' in series:
                    cohort['user_count'] = series['value']

                cohorts.append(cohort)

        df = pd.DataFrame(cohorts)

        # Create campaign identifier
        if 'utm_campaign' in df.columns:
            df['campaign'] = df['utm_campaign']
        else:
            df['campaign'] = df.get('utm_source', 'unknown')

        return df

    def get_cohort_metrics(
        self,
        cohort_ids: List[str],
        events: List[str] = None,
        start_date: str = None,
        end_date: str = None
    ) -> pd.DataFrame:
        """
        Get activation and conversion metrics for specific cohorts.

        This shows which campaigns drive users who actually USE the product
        and convert to paying customers.

        Args:
            cohort_ids: List of cohort identifiers (campaign names)
            events: List of events to track (e.g., ['course_started', 'payment_completed'])
            start_date: Start date for analysis
            end_date: End date for analysis

        Returns:
            DataFrame with columns:
                - campaign: Campaign identifier
                - activated_users: Users who completed activation event
                - paying_users: Users who completed payment event
                - total_revenue: Total revenue from cohort
                - activation_rate: % of users who activated
                - payment_rate: % of users who paid
        """
        logger.info(f"Fetching cohort metrics for {len(cohort_ids)} cohorts")

        if events is None:
            events = [
                os.getenv('AMPLITUDE_ACTIVATION_EVENT', 'course_started'),
                os.getenv('AMPLITUDE_REVENUE_EVENT', 'payment_completed')
            ]

        metrics = []

        for cohort_id in cohort_ids:
            cohort_metrics = self._get_metrics_for_cohort(
                cohort_id, events, start_date, end_date
            )
            metrics.append(cohort_metrics)

            # Rate limiting - Amplitude has API limits
            time.sleep(0.1)

        df = pd.DataFrame(metrics)

        logger.info(f"Retrieved metrics for {len(df)} cohorts")

        return df

    def _get_metrics_for_cohort(
        self,
        cohort_id: str,
        events: List[str],
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """
        Get metrics for a single cohort.
        """
        # This is a simplified version
        # Real implementation uses Amplitude's funnel or user search APIs

        endpoint = f"{self.BASE_URL}/useractivity"

        params = {
            'user': cohort_id,  # This would be user IDs in real implementation
            'start': start_date,
            'end': end_date
        }

        try:
            response = self.session.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()

            # Parse user activity to calculate metrics
            return self._calculate_cohort_metrics(data, cohort_id, events)

        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to fetch metrics for cohort {cohort_id}: {e}")
            return {'campaign': cohort_id, 'error': str(e)}

    def _calculate_cohort_metrics(
        self,
        data: Dict,
        cohort_id: str,
        events: List[str]
    ) -> Dict[str, Any]:
        """
        Calculate activation and payment metrics from user activity data.
        """
        # Simplified calculation
        # Real implementation analyzes user event sequences

        metrics = {
            'campaign': cohort_id,
            'activated_users': 0,
            'paying_users': 0,
            'total_revenue': 0,
            'activation_rate': 0,
            'payment_rate': 0
        }

        # TODO: Parse actual Amplitude response and calculate metrics

        return metrics

    def get_retention_data(
        self,
        cohort_ids: List[str],
        days: List[int] = None,
        start_date: str = None
    ) -> pd.DataFrame:
        """
        Get retention metrics for user cohorts.

        This shows which campaigns drive STICKY users who come back.

        Args:
            cohort_ids: List of cohort identifiers
            days: List of day intervals to measure (e.g., [7, 14, 30])
            start_date: Cohort start date

        Returns:
            DataFrame with columns:
                - campaign: Campaign identifier
                - day_7_retention: % of users active after 7 days
                - day_14_retention: % of users active after 14 days
                - day_30_retention: % of users active after 30 days
        """
        logger.info(f"Fetching retention data for {len(cohort_ids)} cohorts")

        if days is None:
            days = [7, 14, 30]

        # Use Amplitude's retention analysis API
        endpoint = f"{self.BASE_URL}/retention"

        retention_data = []

        for cohort_id in cohort_ids:
            params = {
                'start': start_date,
                'days': ','.join(map(str, days)),
                'segment': cohort_id
            }

            try:
                response = self.session.get(endpoint, params=params)
                response.raise_for_status()
                data = response.json()

                cohort_retention = self._parse_retention_response(data, cohort_id, days)
                retention_data.append(cohort_retention)

                time.sleep(0.1)  # Rate limiting

            except requests.exceptions.RequestException as e:
                logger.warning(f"Failed to fetch retention for {cohort_id}: {e}")

        df = pd.DataFrame(retention_data)

        logger.info(f"Retrieved retention data for {len(df)} cohorts")

        return df

    def _parse_retention_response(
        self,
        data: Dict,
        cohort_id: str,
        days: List[int]
    ) -> Dict[str, Any]:
        """
        Parse retention API response.
        """
        retention = {'campaign': cohort_id}

        # Amplitude returns retention as array of percentages
        if 'data' in data:
            retention_values = data['data']
            for i, day in enumerate(days):
                if i < len(retention_values):
                    retention[f'day_{day}_retention'] = retention_values[i]

        return retention

    def calculate_ltv_by_campaign(
        self,
        cohort_data: pd.DataFrame,
        revenue_data: pd.DataFrame,
        retention_data: pd.DataFrame,
        prediction_horizon_months: int = 12
    ) -> pd.DataFrame:
        """
        Calculate predicted Lifetime Value (LTV) by campaign.

        This combines early revenue signals with retention data to predict
        long-term value of users from each campaign.

        Args:
            cohort_data: DataFrame with cohort sizes
            revenue_data: DataFrame with revenue per cohort
            retention_data: DataFrame with retention rates
            prediction_horizon_months: Months to predict (default 12)

        Returns:
            DataFrame with columns:
                - campaign: Campaign identifier
                - avg_revenue_per_user: Average revenue per user so far
                - predicted_ltv: Predicted lifetime value
                - confidence: Confidence level (high/medium/low)
        """
        logger.info("Calculating LTV predictions by campaign")

        # Merge all data sources
        ltv_data = cohort_data.merge(revenue_data, on='campaign', how='left')
        ltv_data = ltv_data.merge(retention_data, on='campaign', how='left')

        # Calculate average revenue per user
        ltv_data['avg_revenue_per_user'] = (
            ltv_data['total_revenue'] / ltv_data['user_count']
        ).fillna(0)

        # Predict LTV based on retention curve
        # Simplified model: LTV = Revenue * (1 + retention_factor * horizon)
        ltv_data['retention_factor'] = (
            ltv_data.get('day_30_retention', 0) / 100
        )

        ltv_data['predicted_ltv'] = (
            ltv_data['avg_revenue_per_user'] *
            (1 + ltv_data['retention_factor'] * (prediction_horizon_months / 12))
        )

        # Assign confidence based on data availability
        ltv_data['confidence'] = 'low'
        ltv_data.loc[ltv_data['user_count'] >= 30, 'confidence'] = 'medium'
        ltv_data.loc[
            (ltv_data['user_count'] >= 50) & (ltv_data['day_30_retention'].notna()),
            'confidence'
        ] = 'high'

        logger.info("LTV calculation complete")

        return ltv_data[['campaign', 'avg_revenue_per_user', 'predicted_ltv', 'confidence']]


def get_amplitude_client() -> AmplitudeAPI:
    """
    Get configured Amplitude API client from environment variables.

    Returns:
        Configured AmplitudeAPI instance

    Raises:
        ValueError: If API keys are not configured
    """
    api_key = os.getenv('AMPLITUDE_API_KEY')
    secret_key = os.getenv('AMPLITUDE_SECRET_KEY')

    if not api_key or not secret_key:
        raise ValueError(
            "Amplitude API keys not configured. "
            "Set AMPLITUDE_API_KEY and AMPLITUDE_SECRET_KEY in .env file."
        )

    return AmplitudeAPI(api_key, secret_key)
