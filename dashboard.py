"""
Cultura Growth Intelligence - Professional Dashboard

Clean, readable, modern dashboard for campaign analysis.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.ingestion.meta_data import load_meta_data
from src.ingestion.amplitude_api import get_amplitude_client
from src.ingestion.data_matcher import match_campaigns
from src.analysis.campaign_analyzer import CampaignAnalyzer
from src.analysis.roi_calculator import ROICalculator

# Page config
st.set_page_config(
    page_title="Cultura Growth Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional, readable CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* GLOBAL */
    * {
        font-family: 'Inter', sans-serif;
    }

    html, body, [class*="css"] {
        font-size: 16px;
    }

    .stApp {
        background: #FAFAFA !important;
    }

    #MainMenu, footer, header {visibility: hidden;}

    /* Force all text to be visible */
    div, p, span, label, h1, h2, h3, h4, h5, h6 {
        color: #111827 !important;
    }

    .stMarkdown, .stMarkdown * {
        color: #111827 !important;
    }

    .block-container {
        padding: 3rem 4rem;
        max-width: 1600px;
    }

    /* HEADER */
    .dashboard-header {
        background: white;
        padding: 2rem 2.5rem;
        border-radius: 12px;
        margin-bottom: 3rem;
        border: 1px solid #E5E7EB;
    }

    .dashboard-header h1 {
        font-size: 2rem;
        font-weight: 600;
        color: #111827;
        margin: 0 0 0.5rem 0;
    }

    .dashboard-header p {
        font-size: 1rem;
        color: #6B7280;
        margin: 0;
    }

    /* SIDEBAR */
    [data-testid="stSidebar"] {
        background: white;
        border-right: 1px solid #E5E7EB;
        padding: 2rem 1.5rem;
    }

    [data-testid="stSidebar"] h2 {
        font-size: 1.125rem;
        font-weight: 600;
        color: #111827;
        margin-bottom: 2rem;
    }

    [data-testid="stSidebar"] h3 {
        font-size: 0.875rem;
        font-weight: 600;
        color: #374151;
        margin: 1.5rem 0 0.75rem 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* METRICS */
    [data-testid="stMetric"] {
        background: white;
        padding: 1.75rem 2rem;
        border-radius: 12px;
        border: 1px solid #E5E7EB;
    }

    [data-testid="stMetric"] label {
        font-size: 0.875rem;
        font-weight: 500;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-size: 2.25rem;
        font-weight: 600;
        color: #111827;
    }

    /* BUTTONS */
    .stButton > button {
        width: 100%;
        background: #2563EB;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-size: 0.9375rem;
        font-weight: 600;
        transition: all 0.2s;
    }

    .stButton > button:hover {
        background: #1D4ED8;
        transform: translateY(-1px);
    }

    /* TABS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: white;
        border-bottom: 2px solid #E5E7EB;
        padding: 0 2rem;
        border-radius: 12px 12px 0 0;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 1.25rem 2rem;
        font-size: 0.9375rem;
        font-weight: 500;
        color: #6B7280;
        border: none;
        background: transparent;
        border-bottom: 3px solid transparent;
        margin-bottom: -2px;
    }

    .stTabs [aria-selected="true"] {
        color: #2563EB;
        border-bottom-color: #2563EB;
    }

    /* SECTION TITLES */
    h1, .stMarkdown h1 {
        font-size: 1.875rem !important;
        font-weight: 600 !important;
        color: #111827 !important;
        margin-bottom: 0.5rem !important;
    }

    h2, .stMarkdown h2 {
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        color: #111827 !important;
        margin-bottom: 1rem !important;
    }

    h3, .stMarkdown h3 {
        font-size: 1.125rem !important;
        font-weight: 600 !important;
        color: #111827 !important;
    }

    p, .stMarkdown p {
        color: #374151 !important;
        font-size: 1rem !important;
    }

    /* CAMPAIGN CARDS */
    .campaign-card {
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 2rem;
        margin-bottom: 1.5rem;
    }

    .campaign-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #E5E7EB;
    }

    .campaign-name {
        font-size: 1.25rem;
        font-weight: 600;
        color: #111827;
    }

    .status-badge {
        padding: 0.5rem 1rem;
        border-radius: 6px;
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .status-badge.scale {
        background: #DCFCE7;
        color: #166534;
    }

    .status-badge.maintain {
        background: #FEF3C7;
        color: #92400E;
    }

    .status-badge.pause {
        background: #FEE2E2;
        color: #991B1B;
    }

    .metric-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 2rem;
        margin: 1.5rem 0;
    }

    .metric-item {
        padding: 1rem;
        background: #F9FAFB;
        border-radius: 8px;
    }

    .metric-label {
        font-size: 0.8125rem;
        font-weight: 600;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }

    .metric-value {
        font-size: 1.875rem;
        font-weight: 700;
        color: #111827;
    }

    .metric-subtitle {
        font-size: 0.875rem;
        color: #9CA3AF;
        margin-top: 0.25rem;
    }

    /* EXPANDERS */
    .streamlit-expanderHeader {
        background: white !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 12px;
        padding: 1.25rem 1.5rem !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: #111827 !important;
    }

    [data-testid="stExpander"] {
        background: white !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 12px !important;
    }

    [data-testid="stExpander"] summary {
        background: white !important;
        color: #111827 !important;
        padding: 1rem 1.5rem !important;
    }

    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] strong {
        color: #111827 !important;
    }

    /* FILE UPLOADER */
    [data-testid="stFileUploader"] {
        background: white;
        border: 1px solid #D1D5DB;
        border-radius: 8px;
        padding: 1rem;
    }

    [data-testid="stFileUploader"] section {
        background: white !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 6px;
        padding: 1.5rem !important;
    }

    [data-testid="stFileUploader"] section:hover {
        border-color: #2563EB !important;
        background: #F9FAFB !important;
    }

    [data-testid="stFileUploader"] label {
        font-size: 0.875rem;
        font-weight: 600;
        color: #111827 !important;
        margin-bottom: 0.5rem;
    }

    [data-testid="stFileUploader"] button {
        background: white !important;
        color: #2563EB !important;
        border: 1px solid #2563EB !important;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-size: 0.875rem;
        font-weight: 500;
        transition: all 0.2s;
    }

    [data-testid="stFileUploader"] button:hover {
        background: #EFF6FF !important;
    }

    [data-testid="stFileUploader"] small {
        color: #6B7280 !important;
        font-size: 0.8125rem;
    }

    /* DATAFRAME */
    [data-testid="stDataFrame"] {
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        overflow: hidden;
    }

    /* ALERTS */
    .stAlert {
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 1rem 1.25rem;
        font-size: 0.9375rem;
    }

    /* SUCCESS MESSAGE */
    .stSuccess {
        background: #DCFCE7;
        border-left: 4px solid #16A34A;
        color: #166534;
    }

    /* STEP CARDS */
    .step-card {
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 2rem;
        height: 100%;
    }

    .step-number {
        display: inline-block;
        width: 2.5rem;
        height: 2.5rem;
        background: #2563EB;
        color: white;
        border-radius: 50%;
        text-align: center;
        line-height: 2.5rem;
        font-size: 1.125rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }

    .step-title {
        font-size: 1.125rem;
        font-weight: 600;
        color: #111827;
        margin-bottom: 0.75rem;
    }

    .step-description {
        font-size: 0.9375rem;
        color: #6B7280;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'enriched_df' not in st.session_state:
    st.session_state.enriched_df = None
if 'analysis' not in st.session_state:
    st.session_state.analysis = None


def main():
    # Header
    st.markdown("""
    <div class="dashboard-header">
        <h1>Cultura Growth Intelligence</h1>
        <p>Advanced paid marketing analysis with true ROI tracking</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.markdown("## Configuration")

        st.markdown("### Date Range")
        days = st.slider("Days of data", 7, 90, 30, help="Select the time period for analysis")

        st.markdown("### Data Sources")
        uploaded_file = st.file_uploader("Upload Meta Ads CSV", type=['csv'], help="Export from Meta Ads Manager")

        use_amplitude = st.checkbox("Enable Amplitude Integration", value=False, help="Track actual user behavior")

        st.markdown("")
        if st.button("Run Analysis"):
            with st.spinner("Analyzing campaigns..."):
                run_analysis(uploaded_file, use_amplitude, days)

        if st.session_state.enriched_df is not None:
            st.success(f"✓ Analysis complete ({datetime.now().strftime('%H:%M')})")

    # Main content
    if st.session_state.enriched_df is None:
        show_demo_mode()
    else:
        show_dashboard()


def run_analysis(uploaded_file, use_amplitude, days):
    """Run the full analysis pipeline."""
    try:
        if uploaded_file is not None:
            temp_path = f"/tmp/meta_data_{datetime.now().timestamp()}.csv"
            with open(temp_path, 'wb') as f:
                f.write(uploaded_file.getvalue())
            meta_df = load_meta_data(temp_path)
        else:
            st.error("Please upload Meta Ads CSV file")
            return

        if use_amplitude:
            try:
                amp_client = get_amplitude_client()
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)
                cohorts = amp_client.get_user_cohorts(
                    start_date.strftime('%Y-%m-%d'),
                    end_date.strftime('%Y-%m-%d')
                )
                cohort_ids = cohorts['campaign'].unique().tolist()
                revenue_data = amp_client.get_cohort_metrics(cohort_ids)
                retention_data = amp_client.get_retention_data(cohort_ids)
                enriched_df = match_campaigns(meta_df, cohorts, revenue_data, retention_data)
            except Exception as e:
                st.warning(f"Amplitude integration failed: {e}. Using Meta data only.")
                enriched_df = meta_df
        else:
            enriched_df = meta_df

        calculator = ROICalculator()
        enriched_df = calculator.calculate_campaign_metrics(enriched_df)

        try:
            analyzer = CampaignAnalyzer()
            analysis = analyzer.analyze_campaigns(enriched_df, focus="scaling")
            st.session_state.analysis = analysis
        except Exception as e:
            st.warning(f"AI analysis skipped: {e}")
            st.session_state.analysis = None

        st.session_state.enriched_df = enriched_df

    except Exception as e:
        st.error(f"Analysis failed: {e}")


def show_dashboard():
    """Show the main dashboard with all tabs."""
    df = st.session_state.enriched_df

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Scaling Decisions",
        "Campaign Comparison",
        "Cohort Analysis",
        "User Quality",
        "AI Insights",
        "Scaling Simulator"
    ])

    with tab1:
        show_scaling_decisions(df)

    with tab2:
        show_campaign_comparison(df)

    with tab3:
        show_cohort_analysis(df)

    with tab4:
        show_user_quality_heatmap(df)

    with tab5:
        show_ai_insights()

    with tab6:
        show_scaling_simulator(df)


def show_scaling_decisions(df):
    """Tab 1: Scaling Decisions"""
    st.markdown('<h1 style="color: #111827;">Scaling Decisions</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #6B7280; font-size: 1rem;">Should you scale each campaign? Here\'s what the data says.</p>', unsafe_allow_html=True)
    st.markdown("")

    if 'scale_score' in df.columns:
        df_sorted = df.sort_values('scale_score', ascending=False)
    else:
        df_sorted = df

    for idx, campaign in df_sorted.head(10).iterrows():
        show_campaign_decision_card(campaign)


def show_campaign_decision_card(campaign):
    """Display a decision card for a single campaign."""
    campaign_name = campaign.get('campaign_name', 'Unknown')
    scale_score = campaign.get('scale_score', 50)

    if scale_score >= 70:
        rec_text = "SCALE AGGRESSIVELY"
        badge_class = "scale"
    elif scale_score >= 60:
        rec_text = "SCALE CAUTIOUSLY"
        badge_class = "scale"
    elif scale_score >= 40:
        rec_text = "MAINTAIN & MONITOR"
        badge_class = "maintain"
    else:
        rec_text = "PAUSE OR RESTRUCTURE"
        badge_class = "pause"

    with st.expander(f"**{campaign_name}** — Score: {scale_score:.0f}/100", expanded=(scale_score >= 60)):
        st.markdown(f'<div class="status-badge {badge_class}">{rec_text}</div>', unsafe_allow_html=True)
        st.markdown("")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("### 📈 Acquisition")
            st.metric("Total Spend", f"R$ {campaign.get('spend', 0):,.0f}")
            st.metric("Signups", f"{campaign.get('actual_signups', 0):.0f}")
            st.metric("Cost per Signup", f"R$ {campaign.get('acquisition_cac', 0):.0f}")

        with col2:
            st.markdown("### 💰 Revenue")
            st.metric("Paying Users", f"{campaign.get('paying_users', 0):.0f}")
            st.metric("True CAC", f"R$ {campaign.get('true_cac', campaign.get('payment_cac', 0)):.0f}")
            st.metric("Payment Rate", f"{campaign.get('payment_rate', 0):.1f}%")

        with col3:
            st.markdown("### ⚡ Quality")
            st.metric("Activation Rate", f"{campaign.get('activation_rate', 0):.1f}%")
            st.metric("LTV:CAC Ratio", f"{campaign.get('ltv_cac_ratio', 0):.1f}x")
            st.metric("30-day Retention", f"{campaign.get('day_30_retention', 0):.1f}%")


def show_campaign_comparison(df):
    """Tab 2: Campaign Comparison"""
    st.markdown('<h1 style="color: #111827;">Campaign Comparison</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #6B7280; font-size: 1rem;">Compare all campaigns side-by-side</p>', unsafe_allow_html=True)
    st.markdown("")

    comparison_cols = [
        'campaign_name', 'spend', 'true_cac', 'payment_rate',
        'ltv_cac_ratio', 'day_30_retention', 'efficiency_score'
    ]

    available_cols = [col for col in comparison_cols if col in df.columns]
    comparison_df = df[available_cols].copy()

    st.dataframe(comparison_df, use_container_width=True, hide_index=True, height=400)
    st.markdown("")

    col1, col2 = st.columns(2)

    with col1:
        if 'ltv_cac_ratio' in df.columns and 'spend' in df.columns:
            fig = px.scatter(
                df,
                x='spend',
                y='ltv_cac_ratio',
                size='paying_users' if 'paying_users' in df.columns else None,
                hover_data=['campaign_name'],
                title="LTV:CAC Ratio vs Spend",
                labels={'spend': 'Spend (BRL)', 'ltv_cac_ratio': 'LTV:CAC Ratio'},
                color_discrete_sequence=['#2563EB']
            )
            fig.add_hline(y=3, line_dash="dash", line_color="#6B7280", annotation_text="Target: 3x")
            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(family="Inter, sans-serif", size=14)
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        if 'payment_rate' in df.columns and 'activation_rate' in df.columns:
            fig = px.scatter(
                df,
                x='activation_rate',
                y='payment_rate',
                size='spend' if 'spend' in df.columns else None,
                hover_data=['campaign_name'],
                title="Payment vs Activation Rate",
                labels={'activation_rate': 'Activation (%)', 'payment_rate': 'Payment (%)'},
                color_discrete_sequence=['#2563EB']
            )
            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(family="Inter, sans-serif", size=14)
            )
            st.plotly_chart(fig, use_container_width=True)


def show_cohort_analysis(df):
    """Tab 3: Cohort Analysis"""
    st.markdown('<h1 style="color: #111827;">Cohort Analysis</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #6B7280; font-size: 1rem;">Deep dive into user journey from signup to retention</p>', unsafe_allow_html=True)
    st.markdown("")

    if 'campaign_name' not in df.columns or len(df) == 0:
        st.warning("No campaign data available. Please run an analysis first.")
        return

    campaigns = df['campaign_name'].unique()
    if len(campaigns) == 0:
        st.warning("No campaigns found in the data.")
        return

    selected_campaign = st.selectbox("Select Campaign", campaigns, key="cohort_campaign_select")
    campaign_matches = df[df['campaign_name'] == selected_campaign]

    if len(campaign_matches) == 0:
        st.warning(f"No data found for campaign: {selected_campaign}")
        return

    campaign_data = campaign_matches.iloc[0]

    st.markdown("")

    funnel_data = {
        'Stage': ['Signups', 'Activated', 'Paying', 'Active 30d'],
        'Users': [
            campaign_data.get('actual_signups', 0),
            campaign_data.get('activated_users', 0),
            campaign_data.get('paying_users', 0),
            campaign_data.get('paying_users', 0) * campaign_data.get('day_30_retention', 0) / 100
        ]
    }

    funnel_df = pd.DataFrame(funnel_data)

    fig = go.Figure(go.Funnel(
        y=funnel_df['Stage'],
        x=funnel_df['Users'],
        textinfo="value+percent initial",
        marker=dict(color='#2563EB')
    ))

    fig.update_layout(
        title=f"User Funnel: {selected_campaign}",
        font=dict(family="Inter, sans-serif", size=14),
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Signups", f"{campaign_data.get('actual_signups', 0):.0f}")

    with col2:
        st.metric("Activation Rate", f"{campaign_data.get('activation_rate', 0):.1f}%")

    with col3:
        st.metric("Payment Rate", f"{campaign_data.get('payment_rate', 0):.1f}%")

    with col4:
        st.metric("30-day Retention", f"{campaign_data.get('day_30_retention', 0):.1f}%")


def show_user_quality_heatmap(df):
    """Tab 4: User Quality"""
    st.markdown('<h1 style="color: #111827;">User Quality Metrics</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #6B7280; font-size: 1rem;">Compare quality metrics across all campaigns</p>', unsafe_allow_html=True)
    st.markdown("")

    quality_metrics = ['activation_rate', 'payment_rate', 'day_7_retention', 'day_30_retention']
    available_metrics = [m for m in quality_metrics if m in df.columns]

    if len(available_metrics) > 0:
        heatmap_data = df[['campaign_name'] + available_metrics].set_index('campaign_name')

        fig = px.imshow(
            heatmap_data.T,
            labels=dict(x="Campaign", y="Metric", color="Value"),
            x=heatmap_data.index,
            y=heatmap_data.columns,
            color_continuous_scale='Blues',
            title="Quality Metrics Heatmap"
        )

        fig.update_layout(
            height=600,
            font=dict(family="Inter, sans-serif", size=14),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📊 Enable Amplitude integration to see detailed user quality metrics")


def show_ai_insights():
    """Tab 5: AI Insights"""
    st.markdown('<h1 style="color: #111827;">AI Insights</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #6B7280; font-size: 1rem;">Claude AI analysis of your campaigns</p>', unsafe_allow_html=True)
    st.markdown("")

    if st.session_state.analysis:
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Campaigns Analyzed", st.session_state.analysis.get('campaigns_analyzed', 0))

        with col2:
            st.metric("Total Spend", f"R$ {st.session_state.analysis.get('total_spend', 0):,.0f}")

        with col3:
            st.metric("Total Revenue", f"R$ {st.session_state.analysis.get('total_revenue', 0):,.0f}")

        st.markdown("---")
        st.markdown("## Analysis Report")
        st.markdown(st.session_state.analysis['full_analysis'])
    else:
        st.info("🤖 Set ANTHROPIC_API_KEY in .env to enable AI-powered insights")


def show_scaling_simulator(df):
    """Tab 6: Scaling Simulator"""
    st.markdown('<h1 style="color: #111827;">Scaling Simulator</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #6B7280; font-size: 1rem;">Model the impact of budget changes before scaling</p>', unsafe_allow_html=True)
    st.markdown("")

    if 'campaign_name' not in df.columns or len(df) == 0:
        st.warning("No campaign data available. Please run an analysis first.")
        return

    campaigns = df['campaign_name'].unique()
    if len(campaigns) == 0:
        st.warning("No campaigns found in the data.")
        return

    selected_campaign = st.selectbox("Select Campaign", campaigns, key="simulator_campaign_select")
    campaign_matches = df[df['campaign_name'] == selected_campaign]

    if len(campaign_matches) == 0:
        st.warning(f"No data found for campaign: {selected_campaign}")
        return

    campaign_data = campaign_matches.iloc[0]

    st.markdown("")

    col1, col2 = st.columns(2)

    with col1:
        current_budget = st.number_input("Current Daily Budget (BRL)", value=100.0, min_value=0.0, step=10.0)

    with col2:
        proposed_budget = st.number_input("Proposed Daily Budget (BRL)", value=300.0, min_value=0.0, step=10.0)

    if current_budget > 0:
        scale_factor = proposed_budget / current_budget

        st.markdown("")
        st.markdown("## Projected Outcomes")
        st.markdown("")

        current_cac = campaign_data.get('true_cac', campaign_data.get('payment_cac', 0))
        expected_cac = current_cac * (1 + (scale_factor - 1) * 0.25)

        current_users = current_budget / current_cac if current_cac > 0 else 0
        expected_users = proposed_budget / expected_cac if expected_cac > 0 else 0

        col1, col2, col3 = st.columns(3)

        with col1:
            delta_pct = ((expected_cac / current_cac - 1) * 100) if current_cac > 0 else 0
            st.metric("Expected CAC", f"R$ {expected_cac:.0f}", delta=f"{delta_pct:+.1f}%")

        with col2:
            st.metric("Expected Users/Day", f"{expected_users:.1f}", delta=f"+{(expected_users - current_users):.1f}")

        with col3:
            st.metric("LTV:CAC Ratio", f"{campaign_data.get('ltv_cac_ratio', 0):.1f}x")

        st.markdown("---")

        if scale_factor > 3:
            st.error("⚠️ **High Risk**: Scaling by more than 3x may significantly increase CAC and degrade user quality")
        elif scale_factor > 2:
            st.warning("⚡ **Medium Risk**: Monitor CAC and quality metrics closely during scale-up")
        else:
            st.success("✅ **Low Risk**: Conservative scaling approach with minimal expected CAC increase")


def show_demo_mode():
    """Show demo instructions."""
    st.markdown('<h1 style="color: #111827;">Getting Started</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #6B7280; font-size: 1rem;">Follow these steps to analyze your campaigns</p>', unsafe_allow_html=True)
    st.markdown("")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="step-card">
            <div class="step-number">1</div>
            <div class="step-title">Upload Meta Ads Data</div>
            <div class="step-description">
                Export your campaign data from Meta Ads Manager as a CSV file and upload it using the sidebar.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="step-card">
            <div class="step-number">2</div>
            <div class="step-title">Enable Amplitude (Optional)</div>
            <div class="step-description">
                Set your API keys in .env and enable Amplitude integration for true user behavior tracking.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="step-card">
            <div class="step-number">3</div>
            <div class="step-title">Run Analysis</div>
            <div class="step-description">
                Click "Run Analysis" to get AI-powered scaling recommendations and detailed insights.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")
    st.markdown("---")
    st.markdown("")

    st.info("""
    **Required CSV columns:**
    - Campaign name
    - Amount spent (BRL)
    - Impressions
    - Results
    - Cost per result
    """)


if __name__ == "__main__":
    main()
