#!/usr/bin/env python3
"""
Cultura Growth Intelligence - CLI Interface

Command-line interface for the growth intelligence system.
"""

import click
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
import logging
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from rich.progress import Progress
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.ingestion.meta_data import load_meta_data
from src.ingestion.amplitude_api import get_amplitude_client
from src.ingestion.data_matcher import match_campaigns
from src.analysis.campaign_analyzer import CampaignAnalyzer
from src.analysis.roi_calculator import ROICalculator
from src.database.db import get_database

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

console = Console()


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """
    🚀 Cultura Growth Intelligence

    Analyze paid marketing performance with true ROI tracking using
    Meta Ads data + Amplitude user behavior analytics.
    """
    pass


@cli.command()
@click.option('--file', '-f', required=True, help='Path to Meta Ads CSV file')
@click.option('--amplitude', is_flag=True, help='Pull and match Amplitude data')
@click.option('--days', '-d', default=30, help='Days of Amplitude data to analyze')
@click.option('--output', '-o', default=None, help='Output file path for report')
def analyze(file, amplitude, days, output):
    """
    Analyze campaign performance with AI insights.

    Example:
        python main.py analyze --file data/meta_oct_nov.csv --amplitude --days 30
    """
    console.print("\n[bold blue]🚀 Cultura Growth Intelligence - Campaign Analysis[/bold blue]\n")

    with Progress() as progress:
        # Step 1: Load Meta data
        task1 = progress.add_task("[cyan]Loading Meta Ads data...", total=1)
        try:
            meta_df = load_meta_data(file)
            console.print(f"✅ Loaded {len(meta_df)} campaigns from Meta Ads")
            progress.update(task1, completed=1)
        except Exception as e:
            console.print(f"[red]❌ Error loading Meta data: {e}[/red]")
            sys.exit(1)

        # Step 2: Load Amplitude data (if requested)
        if amplitude:
            task2 = progress.add_task("[cyan]Fetching Amplitude data...", total=1)
            try:
                amp_client = get_amplitude_client()

                # Calculate date range
                from datetime import datetime, timedelta
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)

                # Get cohorts
                cohorts = amp_client.get_user_cohorts(
                    start_date.strftime('%Y-%m-%d'),
                    end_date.strftime('%Y-%m-%d')
                )

                # Get cohort metrics
                cohort_ids = cohorts['campaign'].unique().tolist()
                revenue_data = amp_client.get_cohort_metrics(cohort_ids)
                retention_data = amp_client.get_retention_data(cohort_ids)

                console.print(f"✅ Retrieved {len(cohorts)} cohorts from Amplitude")
                progress.update(task2, completed=1)

                # Step 3: Match data
                task3 = progress.add_task("[cyan]Matching campaigns to user cohorts...", total=1)
                enriched_df = match_campaigns(
                    meta_df,
                    cohorts,
                    revenue_data,
                    retention_data
                )
                console.print(f"✅ Matched {len(enriched_df)} campaigns")
                progress.update(task3, completed=1)

            except ValueError as e:
                console.print(f"[yellow]⚠️  Amplitude integration skipped: {e}[/yellow]")
                console.print("[yellow]   Continuing with Meta data only...[/yellow]")
                enriched_df = meta_df
            except Exception as e:
                console.print(f"[red]❌ Error with Amplitude: {e}[/red]")
                enriched_df = meta_df
        else:
            enriched_df = meta_df

        # Step 4: Calculate ROI metrics
        task4 = progress.add_task("[cyan]Calculating ROI metrics...", total=1)
        calculator = ROICalculator()
        enriched_df = calculator.calculate_campaign_metrics(enriched_df)
        progress.update(task4, completed=1)

        # Step 5: Run AI analysis
        task5 = progress.add_task("[cyan]Running AI analysis...", total=1)
        try:
            analyzer = CampaignAnalyzer()
            analysis = analyzer.analyze_campaigns(enriched_df, focus="scaling")

            console.print("✅ AI analysis complete")
            progress.update(task5, completed=1)

            # Display analysis
            console.print("\n[bold green]📊 AI INSIGHTS & RECOMMENDATIONS[/bold green]\n")
            console.print(analysis['full_analysis'])

            # Display top campaigns
            _display_top_campaigns(enriched_df)

            # Save report
            if output:
                _save_report(analysis, enriched_df, output)
                console.print(f"\n✅ Report saved to: {output}")
            else:
                # Save to reports folder with timestamp
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                report_path = f"reports/analysis_{timestamp}.md"
                os.makedirs('reports', exist_ok=True)
                _save_report(analysis, enriched_df, report_path)
                console.print(f"\n✅ Report saved to: {report_path}")

        except ValueError as e:
            console.print(f"[yellow]⚠️  AI analysis skipped: {e}[/yellow]")
            console.print("[yellow]   Set ANTHROPIC_API_KEY to enable AI analysis[/yellow]")
            _display_top_campaigns(enriched_df)
        except Exception as e:
            console.print(f"[red]❌ AI analysis failed: {e}[/red]")
            _display_top_campaigns(enriched_df)


@cli.command()
@click.option('--campaign', '-c', required=True, help='Campaign name to analyze')
@click.option('--days', '-d', default=30, help='Days of data to retrieve')
def cohorts(campaign, days):
    """
    Show detailed cohort analysis for a specific campaign.

    Example:
        python main.py cohorts --campaign "VENDA-EMPREENDEDORES" --days 30
    """
    console.print(f"\n[bold blue]📊 Cohort Analysis: {campaign}[/bold blue]\n")

    try:
        amp_client = get_amplitude_client()

        from datetime import datetime, timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Get cohort data
        cohorts = amp_client.get_user_cohorts(
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )

        # Filter for specific campaign
        campaign_cohort = cohorts[cohorts['campaign'].str.contains(campaign, case=False, na=False)]

        if len(campaign_cohort) == 0:
            console.print(f"[yellow]No cohort data found for campaign: {campaign}[/yellow]")
            return

        # Get detailed metrics
        cohort_ids = campaign_cohort['campaign'].unique().tolist()
        revenue_data = amp_client.get_cohort_metrics(cohort_ids)
        retention_data = amp_client.get_retention_data(cohort_ids)

        # Display cohort funnel
        _display_cohort_funnel(campaign_cohort, revenue_data, retention_data)

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")


@cli.command()
@click.option('--campaigns', '-c', required=True, help='Comma-separated campaign names')
def compare(campaigns):
    """
    Compare specific campaigns side-by-side.

    Example:
        python main.py compare --campaigns "Campaign-7,Campaign-8,Campaign-9"
    """
    campaign_list = [c.strip() for c in campaigns.split(',')]

    console.print(f"\n[bold blue]🔍 Comparing {len(campaign_list)} Campaigns[/bold blue]\n")

    # TODO: Implement comparison logic
    console.print("[yellow]Comparison feature coming soon![/yellow]")


@cli.command()
@click.option('--days', '-d', default=90, help='Days of data to sync')
def sync_amplitude(days):
    """
    Pull latest data from Amplitude and update local database.

    Example:
        python main.py sync-amplitude --days 90
    """
    console.print("\n[bold blue]🔄 Syncing Amplitude Data[/bold blue]\n")

    try:
        amp_client = get_amplitude_client()
        db = get_database()

        from datetime import datetime, timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        with Progress() as progress:
            task = progress.add_task("[cyan]Fetching cohort data...", total=1)

            cohorts = amp_client.get_user_cohorts(
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )

            progress.update(task, completed=1)

            # Save to database
            task2 = progress.add_task(f"[cyan]Saving {len(cohorts)} cohorts...", total=len(cohorts))

            for idx, cohort in cohorts.iterrows():
                db.save_cohort({
                    'campaign_name': cohort['campaign'],
                    'user_count': cohort.get('user_count', 0),
                    'utm_source': cohort.get('utm_source'),
                    'utm_medium': cohort.get('utm_medium'),
                    'utm_campaign': cohort.get('utm_campaign'),
                })
                progress.update(task2, advance=1)

        console.print(f"\n✅ Synced {len(cohorts)} cohorts from last {days} days")

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")


@cli.command()
@click.option('--days', '-d', default=30, help='Days of data to sync')
@click.option('--auto-analyze', is_flag=True, help='Automatically run analysis after sync')
def sync_all(days, auto_analyze):
    """
    🔄 AUTOMATED SYNC - Pull data from Meta + Amplitude automatically.

    No CSV needed! Syncs directly from APIs.

    Example:
        python main.py sync-all --days 30 --auto-analyze
    """
    console.print("\n[bold blue]🔄 Automated Data Sync[/bold blue]\n")

    synced_data = {}

    # Sync Meta Ads
    console.print("[cyan]📊 Syncing Meta Ads data...[/cyan]")
    try:
        from src.ingestion.meta_ads_api import sync_meta_campaigns

        meta_df = sync_meta_campaigns(days_back=days)
        synced_data['meta'] = meta_df

        console.print(f"✅ Synced {len(meta_df)} campaigns from Meta Ads")

    except ImportError as e:
        console.print("[yellow]⚠️  Meta API not configured. Install: pip install facebook-business[/yellow]")
    except ValueError as e:
        console.print(f"[yellow]⚠️  Meta API credentials not found: {e}[/yellow]")
        console.print("[yellow]   Add META_ACCESS_TOKEN, META_APP_ID, META_APP_SECRET, META_AD_ACCOUNT_ID to .env[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Meta sync failed: {e}[/red]")

    # Sync Amplitude
    console.print("\n[cyan]📈 Syncing Amplitude data...[/cyan]")
    try:
        from datetime import timedelta
        amp_client = get_amplitude_client()

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        cohorts = amp_client.get_user_cohorts(
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )

        synced_data['amplitude'] = cohorts

        console.print(f"✅ Synced {len(cohorts)} cohorts from Amplitude")

    except ValueError as e:
        console.print(f"[yellow]⚠️  Amplitude credentials not found: {e}[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Amplitude sync failed: {e}[/red]")

    # Save to database
    if synced_data:
        console.print("\n[cyan]💾 Saving to database...[/cyan]")
        db = get_database()

        if 'meta' in synced_data:
            for idx, campaign in synced_data['meta'].iterrows():
                db.save_campaign({
                    'platform': 'meta',
                    'campaign_name': campaign['campaign_name'],
                    'spend': campaign.get('spend', 0),
                    'impressions': campaign.get('impressions', 0),
                    'conversions': campaign.get('conversions', 0),
                })

        console.print("✅ Data saved to database")

        # Auto-analyze if requested
        if auto_analyze and 'meta' in synced_data:
            console.print("\n[cyan]🤖 Running AI analysis...[/cyan]")

            # Match with Amplitude if available
            if 'amplitude' in synced_data:
                enriched_df = match_campaigns(
                    synced_data['meta'],
                    synced_data['amplitude']
                )
            else:
                enriched_df = synced_data['meta']

            # Calculate ROI
            calculator = ROICalculator()
            enriched_df = calculator.calculate_campaign_metrics(enriched_df)

            # Run AI analysis
            try:
                analyzer = CampaignAnalyzer()
                analysis = analyzer.analyze_campaigns(enriched_df, focus="scaling")

                console.print("\n[bold green]📊 AI INSIGHTS[/bold green]\n")
                console.print(analysis['full_analysis'])

                # Save report
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                report_path = f"reports/auto_sync_{timestamp}.md"
                os.makedirs('reports', exist_ok=True)
                _save_report(analysis, enriched_df, report_path)

                console.print(f"\n✅ Report saved: {report_path}")

            except Exception as e:
                console.print(f"[yellow]⚠️  AI analysis skipped: {e}[/yellow]")

    else:
        console.print("\n[red]❌ No data synced. Check your API credentials.[/red]")


@cli.command()
def dashboard():
    """
    Launch Streamlit dashboard.

    Example:
        python main.py dashboard
    """
    console.print("\n[bold blue]🚀 Launching Dashboard[/bold blue]\n")

    import subprocess
    try:
        subprocess.run(["streamlit", "run", "dashboard.py"])
    except FileNotFoundError:
        console.print("[red]❌ Streamlit not found. Install with: pip install streamlit[/red]")


# Helper functions

def _display_top_campaigns(df: pd.DataFrame, top_n: int = 5):
    """Display top performing campaigns in a table."""
    console.print("\n[bold green]🏆 TOP PERFORMING CAMPAIGNS[/bold green]\n")

    # Sort by LTV:CAC ratio if available, otherwise by efficiency score
    if 'ltv_cac_ratio' in df.columns:
        top_campaigns = df.nlargest(top_n, 'ltv_cac_ratio')
    elif 'efficiency_score' in df.columns:
        top_campaigns = df.nlargest(top_n, 'efficiency_score')
    else:
        top_campaigns = df.head(top_n)

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Campaign", style="cyan")
    table.add_column("Spend (BRL)", justify="right")
    table.add_column("CAC (BRL)", justify="right")
    table.add_column("Pay Rate", justify="right")
    table.add_column("LTV:CAC", justify="right", style="green")

    for idx, campaign in top_campaigns.iterrows():
        table.add_row(
            campaign.get('campaign_name', 'Unknown')[:40],
            f"{campaign.get('spend', 0):,.2f}",
            f"{campaign.get('true_cac', campaign.get('payment_cac', 0)):,.2f}",
            f"{campaign.get('payment_rate', 0):.1f}%",
            f"{campaign.get('ltv_cac_ratio', 0):.2f}x"
        )

    console.print(table)


def _display_cohort_funnel(cohort_df, revenue_df, retention_df):
    """Display cohort funnel metrics."""
    # TODO: Implement cohort funnel visualization
    console.print("Cohort funnel visualization coming soon!")


def _save_report(analysis: dict, df: pd.DataFrame, output_path: str):
    """Save analysis report to file."""
    with open(output_path, 'w') as f:
        f.write("# Cultura Growth Intelligence - Analysis Report\n\n")
        f.write(f"**Generated:** {pd.Timestamp.now()}\n\n")
        f.write("## AI Analysis\n\n")
        f.write(analysis['full_analysis'])
        f.write("\n\n## Campaign Data\n\n")

        # Save top campaigns table
        top_campaigns = df.nlargest(10, 'ltv_cac_ratio') if 'ltv_cac_ratio' in df.columns else df.head(10)

        for idx, campaign in top_campaigns.iterrows():
            f.write(f"### {campaign.get('campaign_name', 'Unknown')}\n\n")
            f.write(f"- **Spend:** {campaign.get('spend', 0):.2f} BRL\n")
            f.write(f"- **True CAC:** {campaign.get('true_cac', 0):.2f} BRL\n")
            f.write(f"- **Payment Rate:** {campaign.get('payment_rate', 0):.1f}%\n")
            f.write(f"- **LTV:CAC Ratio:** {campaign.get('ltv_cac_ratio', 0):.2f}x\n")
            f.write(f"- **Paying Users:** {campaign.get('paying_users', 0):.0f}\n\n")


if __name__ == '__main__':
    cli()
