"""
Meta Marketing API integration for automatic campaign data sync.

Automatically pulls campaign performance data from Meta Ads without CSV exports.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd

logger = logging.getLogger(__name__)

# Meta Marketing API requires facebook-business SDK
try:
    from facebook_business.api import FacebookAdsApi
    from facebook_business.adobjects.adaccount import AdAccount
    from facebook_business.adobjects.campaign import Campaign
    from facebook_business.adobjects.adsinsights import AdsInsights
    META_API_AVAILABLE = True
except ImportError:
    META_API_AVAILABLE = False
    logger.warning("facebook-business SDK not installed. Install with: pip install facebook-business")


class MetaAdsAPI:
    """
    Automatically sync campaign data from Meta Marketing API.

    No CSV exports needed - pulls data directly from Meta Ads Manager.
    """

    def __init__(
        self,
        access_token: Optional[str] = None,
        app_id: Optional[str] = None,
        app_secret: Optional[str] = None,
        ad_account_id: Optional[str] = None
    ):
        """
        Initialize Meta Marketing API client.

        Args:
            access_token: Meta API access token
            app_id: Facebook App ID
            app_secret: Facebook App Secret
            ad_account_id: Ad Account ID (format: act_123456789)
        """
        if not META_API_AVAILABLE:
            raise ImportError(
                "facebook-business SDK not installed. "
                "Install with: pip install facebook-business"
            )

        self.access_token = access_token or os.getenv('META_ACCESS_TOKEN')
        self.app_id = app_id or os.getenv('META_APP_ID')
        self.app_secret = app_secret or os.getenv('META_APP_SECRET')
        self.ad_account_id = ad_account_id or os.getenv('META_AD_ACCOUNT_ID')

        if not all([self.access_token, self.app_id, self.app_secret, self.ad_account_id]):
            raise ValueError(
                "Missing Meta API credentials. Set in .env:\n"
                "META_ACCESS_TOKEN, META_APP_ID, META_APP_SECRET, META_AD_ACCOUNT_ID"
            )

        # Initialize API
        FacebookAdsApi.init(
            app_id=self.app_id,
            app_secret=self.app_secret,
            access_token=self.access_token
        )

        self.ad_account = AdAccount(self.ad_account_id)
        logger.info(f"Meta API initialized for account: {self.ad_account_id}")

    def sync_campaigns(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        days_back: int = 30
    ) -> pd.DataFrame:
        """
        Automatically sync campaign data from Meta Ads.

        Args:
            start_date: Start date (YYYY-MM-DD) or None for auto-calculate
            end_date: End date (YYYY-MM-DD) or None for today
            days_back: Days to look back if start_date not provided

        Returns:
            DataFrame with campaign performance data
        """
        logger.info("Syncing campaigns from Meta Marketing API...")

        # Calculate date range
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')

        if start_date is None:
            start = datetime.now() - timedelta(days=days_back)
            start_date = start.strftime('%Y-%m-%d')

        logger.info(f"Pulling data from {start_date} to {end_date}")

        # Define fields to retrieve
        fields = [
            AdsInsights.Field.campaign_id,
            AdsInsights.Field.campaign_name,
            AdsInsights.Field.spend,
            AdsInsights.Field.impressions,
            AdsInsights.Field.clicks,
            AdsInsights.Field.actions,  # Conversions
            AdsInsights.Field.cpc,
            AdsInsights.Field.cpm,
            AdsInsights.Field.ctr,
            AdsInsights.Field.reach,
        ]

        # Parameters for the API call
        params = {
            'time_range': {
                'since': start_date,
                'until': end_date
            },
            'level': 'campaign',
            'filtering': [],
            'breakdowns': [],
        }

        try:
            # Fetch insights
            insights = self.ad_account.get_insights(
                fields=fields,
                params=params
            )

            # Convert to list of dicts
            campaigns_data = []
            for insight in insights:
                campaign = {
                    'campaign_id': insight.get('campaign_id'),
                    'campaign_name': insight.get('campaign_name'),
                    'spend': float(insight.get('spend', 0)),
                    'impressions': int(insight.get('impressions', 0)),
                    'clicks': int(insight.get('clicks', 0)),
                    'cpc': float(insight.get('cpc', 0)),
                    'cpm': float(insight.get('cpm', 0)),
                    'ctr': float(insight.get('ctr', 0)),
                    'reach': int(insight.get('reach', 0)),
                }

                # Extract conversions from actions
                conversions = 0
                actions = insight.get('actions', [])
                if actions:
                    for action in actions:
                        # Look for purchase, lead, or complete_registration actions
                        action_type = action.get('action_type', '')
                        if action_type in ['purchase', 'lead', 'complete_registration', 'offsite_conversion.fb_pixel_purchase']:
                            conversions += int(action.get('value', 0))

                campaign['conversions'] = conversions
                campaign['meta_conversions'] = conversions  # Alias

                # Calculate Meta CAC
                campaign['meta_cac'] = campaign['spend'] / conversions if conversions > 0 else 0

                campaigns_data.append(campaign)

            # Convert to DataFrame
            df = pd.DataFrame(campaigns_data)

            logger.info(f"✅ Synced {len(df)} campaigns from Meta API")

            # Standardize column names (match CSV loader format)
            df = self._standardize_columns(df)

            return df

        except Exception as e:
            logger.error(f"Failed to sync from Meta API: {e}")
            raise

    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize column names to match the CSV loader format.
        """
        # Already using standard names from API, but ensure consistency
        column_mapping = {
            'campaign_id': 'campaign_id',
            'campaign_name': 'campaign_name',
            'spend': 'spend',
            'impressions': 'impressions',
            'clicks': 'clicks',
            'conversions': 'conversions',
            'meta_cac': 'meta_cac',
        }

        return df

    def get_campaign_details(self, campaign_id: str) -> Dict:
        """
        Get detailed information about a specific campaign.

        Args:
            campaign_id: Campaign ID

        Returns:
            Dictionary with campaign details
        """
        campaign = Campaign(campaign_id)
        campaign_data = campaign.api_get(fields=[
            Campaign.Field.name,
            Campaign.Field.status,
            Campaign.Field.objective,
            Campaign.Field.daily_budget,
            Campaign.Field.lifetime_budget,
            Campaign.Field.created_time,
        ])

        return dict(campaign_data)

    def test_connection(self) -> bool:
        """
        Test if API connection works.

        Returns:
            True if connection successful
        """
        try:
            account_info = self.ad_account.api_get(fields=[
                AdAccount.Field.name,
                AdAccount.Field.currency,
                AdAccount.Field.timezone_name,
            ])

            logger.info(f"✅ Connected to Meta Ads Account: {account_info.get('name')}")
            logger.info(f"   Currency: {account_info.get('currency')}")
            logger.info(f"   Timezone: {account_info.get('timezone_name')}")

            return True
        except Exception as e:
            logger.error(f"❌ Connection test failed: {e}")
            return False


def get_meta_api_client() -> MetaAdsAPI:
    """
    Get configured Meta API client from environment variables.

    Returns:
        MetaAdsAPI instance

    Raises:
        ValueError: If credentials not configured
    """
    return MetaAdsAPI()


def sync_meta_campaigns(days_back: int = 30) -> pd.DataFrame:
    """
    Convenience function to sync Meta campaigns.

    Args:
        days_back: Number of days to sync

    Returns:
        DataFrame with campaign data
    """
    client = get_meta_api_client()
    return client.sync_campaigns(days_back=days_back)
