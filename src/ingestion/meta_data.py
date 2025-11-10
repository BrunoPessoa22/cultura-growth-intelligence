"""
Meta Ads data loader and processor.
Handles loading Meta Ads campaign data from CSV files (with API integration planned).
"""

import pandas as pd
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class MetaDataLoader:
    """
    Load and process Meta Ads campaign data.

    Currently supports CSV export from Meta Ads Manager.
    Future: Direct API integration with Meta Marketing API.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Meta data loader.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}

    def load_from_csv(self, file_path: str) -> pd.DataFrame:
        """
        Load Meta Ads data from CSV export.

        Args:
            file_path: Path to the CSV file exported from Meta Ads Manager

        Returns:
            DataFrame with standardized Meta Ads campaign data

        Expected CSV columns:
            - Campaign name
            - Amount spent
            - Impressions
            - Link clicks
            - Results (conversions)
            - Cost per result
        """
        logger.info(f"Loading Meta Ads data from {file_path}")

        if not Path(file_path).exists():
            raise FileNotFoundError(f"Meta Ads CSV file not found: {file_path}")

        # Load CSV with flexible encoding and delimiter detection
        try:
            df = pd.read_csv(file_path, encoding='utf-8', sep=None, engine='python')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='latin-1', sep=None, engine='python')

        logger.info(f"Loaded {len(df)} campaigns from Meta Ads")

        # Standardize the DataFrame
        df = self._standardize_columns(df)
        df = self._clean_data(df)

        return df

    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize column names from Meta Ads export.

        Meta exports have varying column names depending on language/settings.
        This maps them to consistent internal names.
        """
        # Common Meta Ads column name mappings
        column_mapping = {
            # English
            'Campaign name': 'campaign_name',
            'Amount spent (BRL)': 'spend',
            'Impressions': 'impressions',
            'Link clicks': 'clicks',
            'Results': 'conversions',
            'Cost per result': 'meta_cac',
            'Purchases': 'purchases',
            'Cost per purchase': 'cost_per_purchase',

            # Portuguese (Standard)
            'Nome da campanha': 'campaign_name',
            'Valor gasto (BRL)': 'spend',
            'Impressões': 'impressions',
            'Cliques no link': 'clicks',
            'Resultados': 'conversions',
            'Custo por resultado': 'meta_cac',
            'Compras': 'purchases',
            'Custo por compra': 'cost_per_purchase',

            # Portuguese (Actual export format)
            'Valor usado (BRL)': 'spend',
            'Custo por resultados': 'meta_cac',
            'Alcance': 'reach',
            'Compra': 'purchases',  # Singular form from Meta export
            'Custo por compra (BRL)': 'cost_per_purchase',  # With currency

            # Alternative formats
            'Campaign': 'campaign_name',
            'Spend': 'spend',
            'Clicks': 'clicks',
        }

        # Rename columns if they exist
        df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})

        # Verify required columns exist
        required = ['campaign_name', 'spend']
        missing = [col for col in required if col not in df.columns]

        if missing:
            logger.warning(f"Missing columns: {missing}. Available: {list(df.columns)}")
            logger.warning("Please verify CSV format matches Meta Ads export")

        return df

    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and type-convert Meta Ads data.
        """
        df = df.copy()

        # Convert numeric columns (remove currency symbols, convert to float)
        numeric_columns = ['spend', 'impressions', 'clicks', 'conversions', 'meta_cac', 'purchases', 'cost_per_purchase', 'reach']

        for col in numeric_columns:
            if col in df.columns:
                # Remove currency symbols and convert (handle both US and BR formats)
                if df[col].dtype == 'object':
                    # Remove R$ and whitespace
                    df[col] = df[col].astype(str).str.replace('R$', '').str.strip()
                    # If it contains both . and ,, it's likely BR format (1.234,56)
                    # Convert to US format by removing . and replacing , with .
                    df[col] = df[col].str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Calculate derived metrics
        if 'clicks' in df.columns and 'impressions' in df.columns:
            df['ctr'] = (df['clicks'] / df['impressions'] * 100).round(2)

        if 'spend' in df.columns and 'clicks' in df.columns:
            df['cpc'] = (df['spend'] / df['clicks']).round(2)

        # Remove rows with zero spend (not active campaigns)
        if 'spend' in df.columns:
            df = df[df['spend'] > 0]

        logger.info(f"Cleaned data: {len(df)} active campaigns")

        return df

    def extract_utm_parameters(self, df: pd.DataFrame, url_column: str = 'campaign_url') -> pd.DataFrame:
        """
        Extract UTM parameters from campaign URLs if available.

        This helps match Meta campaigns to Amplitude user cohorts.
        """
        if url_column not in df.columns:
            logger.warning(f"URL column '{url_column}' not found. UTM extraction skipped.")
            return df

        df = df.copy()

        # Extract UTM parameters using regex
        import re

        def extract_utm(url, param):
            if pd.isna(url):
                return None
            match = re.search(f'{param}=([^&]+)', str(url))
            return match.group(1) if match else None

        df['utm_source'] = df[url_column].apply(lambda x: extract_utm(x, 'utm_source'))
        df['utm_medium'] = df[url_column].apply(lambda x: extract_utm(x, 'utm_medium'))
        df['utm_campaign'] = df[url_column].apply(lambda x: extract_utm(x, 'utm_campaign'))

        logger.info("Extracted UTM parameters from URLs")

        return df

    def load_from_api(self, account_id: str, date_range: Dict[str, str]) -> pd.DataFrame:
        """
        Load Meta Ads data directly from Meta Marketing API.

        FUTURE IMPLEMENTATION - Placeholder for API integration.

        Args:
            account_id: Meta Ads account ID
            date_range: Dictionary with 'start_date' and 'end_date'

        Returns:
            DataFrame with Meta Ads campaign data
        """
        # TODO: Implement Meta Marketing API integration
        # Will require: facebook-business SDK, access token, permissions
        raise NotImplementedError("Meta API integration coming in Phase 2")


def load_meta_data(file_path: str, config: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    """
    Convenience function to load Meta Ads data from CSV.

    Args:
        file_path: Path to Meta Ads CSV export
        config: Optional configuration

    Returns:
        Cleaned and standardized Meta Ads DataFrame
    """
    loader = MetaDataLoader(config)
    return loader.load_from_csv(file_path)
