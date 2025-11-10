"""
Database models for storing historical campaign performance data.

Track performance over TIME to spot trends, measure scaling decisions,
and learn from past actions.
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, JSON, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import os

Base = declarative_base()


class Campaign(Base):
    """
    Ad platform campaign data (Meta, Google, etc.)
    """
    __tablename__ = 'campaigns'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.utcnow, index=True)
    platform = Column(String(50), default='meta')  # meta, google, tiktok, etc.
    campaign_id = Column(String(100))
    campaign_name = Column(String(200), index=True)

    # Spend metrics
    spend = Column(Float)
    impressions = Column(Integer)
    clicks = Column(Integer)
    conversions = Column(Integer)  # Platform-reported conversions

    # Calculated metrics
    ctr = Column(Float)  # Click-through rate
    cpc = Column(Float)  # Cost per click
    meta_cac = Column(Float)  # Platform-reported CAC

    # Relationships
    cohorts = relationship("Cohort", back_populates="campaign")
    analyses = relationship("Analysis", back_populates="campaign")

    def __repr__(self):
        return f"<Campaign(name={self.campaign_name}, spend={self.spend}, date={self.date})>"


class Cohort(Base):
    """
    User cohorts from Amplitude (actual user behavior)
    """
    __tablename__ = 'cohorts'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.utcnow, index=True)
    campaign_id = Column(Integer, ForeignKey('campaigns.id'))

    # Campaign identifiers
    campaign_name = Column(String(200), index=True)
    utm_source = Column(String(100))
    utm_medium = Column(String(100))
    utm_campaign = Column(String(200))

    # User counts
    user_count = Column(Integer)  # Total signups
    activated_count = Column(Integer)  # Completed activation event
    paid_count = Column(Integer)  # Completed payment event

    # Revenue
    total_revenue = Column(Float)

    # Relationships
    campaign = relationship("Campaign", back_populates="cohorts")
    metrics = relationship("CohortMetric", back_populates="cohort")

    def __repr__(self):
        return f"<Cohort(campaign={self.campaign_name}, users={self.user_count}, paid={self.paid_count})>"


class CohortMetric(Base):
    """
    Time-series user behavior metrics (track retention over time)
    """
    __tablename__ = 'cohort_metrics'

    id = Column(Integer, primary_key=True)
    cohort_id = Column(Integer, ForeignKey('cohorts.id'))
    days_since_signup = Column(Integer)  # 7, 14, 30, etc.

    # Metrics at this time point
    active_users = Column(Integer)
    revenue = Column(Float)
    retention_rate = Column(Float)  # Percentage

    # Relationships
    cohort = relationship("Cohort", back_populates="metrics")

    def __repr__(self):
        return f"<CohortMetric(cohort_id={self.cohort_id}, day={self.days_since_signup}, retention={self.retention_rate}%)>"


class Analysis(Base):
    """
    AI analysis results (track insights over time)
    """
    __tablename__ = 'analyses'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.utcnow, index=True)
    campaign_id = Column(Integer, ForeignKey('campaigns.id'), nullable=True)
    analysis_type = Column(String(50))  # weekly, scaling, quality, etc.

    # Analysis content (JSON for flexibility)
    insights = Column(JSON)
    recommendations = Column(JSON)
    campaigns_analyzed = Column(JSON)  # List of campaign IDs

    # Full text
    full_report = Column(Text)

    # Relationships
    campaign = relationship("Campaign", back_populates="analyses")

    def __repr__(self):
        return f"<Analysis(type={self.analysis_type}, date={self.date})>"


class ScalingDecision(Base):
    """
    Track scaling decisions and their outcomes

    This is CRITICAL for learning what works:
    - Did our scaling decision pay off?
    - Did performance degrade as we scaled?
    - What patterns predict successful scaling?
    """
    __tablename__ = 'scaling_decisions'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.utcnow, index=True)
    campaign_name = Column(String(200), index=True)

    # Decision details
    action = Column(String(50))  # scale, pause, maintain, test
    old_budget = Column(Float)
    new_budget = Column(Float)
    reason = Column(Text)  # Why we made this decision

    # Prediction at time of decision
    expected_outcome = Column(JSON)  # Expected CAC, users, revenue

    # Actual results (filled in later)
    actual_outcome = Column(JSON, nullable=True)  # Actual CAC, users, revenue
    success = Column(Boolean, nullable=True)  # Did it work as expected?

    # Metadata
    confidence_level = Column(String(20))  # high, medium, low
    data_days_available = Column(Integer)  # Days of data when decision was made

    def __repr__(self):
        return f"<ScalingDecision(campaign={self.campaign_name}, action={self.action}, success={self.success})>"


class DatabaseManager:
    """
    Manage database connections and operations.
    """

    def __init__(self, database_url: str = None):
        """
        Initialize database manager.

        Args:
            database_url: SQLAlchemy database URL
                         Defaults to SQLite: sqlite:///cultura_growth.db
                         For PostgreSQL: postgresql://user:pass@localhost/dbname
        """
        if database_url is None:
            database_url = os.getenv(
                'DATABASE_URL',
                'sqlite:///cultura_growth.db'
            )

        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)

    def create_tables(self):
        """Create all tables in the database."""
        Base.metadata.create_all(self.engine)

    def get_session(self):
        """Get a new database session."""
        return self.Session()

    def save_campaign(self, campaign_data: dict) -> Campaign:
        """
        Save campaign data to database.

        Args:
            campaign_data: Dictionary with campaign metrics

        Returns:
            Saved Campaign object
        """
        session = self.get_session()

        campaign = Campaign(**campaign_data)
        session.add(campaign)
        session.commit()
        session.refresh(campaign)

        return campaign

    def save_cohort(self, cohort_data: dict) -> Cohort:
        """Save cohort data to database."""
        session = self.get_session()

        cohort = Cohort(**cohort_data)
        session.add(cohort)
        session.commit()
        session.refresh(cohort)

        return cohort

    def save_analysis(self, analysis_data: dict) -> Analysis:
        """Save AI analysis to database."""
        session = self.get_session()

        analysis = Analysis(**analysis_data)
        session.add(analysis)
        session.commit()
        session.refresh(analysis)

        return analysis

    def save_scaling_decision(self, decision_data: dict) -> ScalingDecision:
        """Save scaling decision to database."""
        session = self.get_session()

        decision = ScalingDecision(**decision_data)
        session.add(decision)
        session.commit()
        session.refresh(decision)

        return decision

    def get_campaign_history(self, campaign_name: str, days: int = 90):
        """
        Get historical data for a specific campaign.

        Args:
            campaign_name: Campaign name
            days: Number of days of history to retrieve

        Returns:
            List of Campaign objects
        """
        session = self.get_session()

        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        campaigns = session.query(Campaign).filter(
            Campaign.campaign_name == campaign_name,
            Campaign.date >= cutoff_date
        ).order_by(Campaign.date.desc()).all()

        return campaigns

    def get_scaling_decision_outcomes(self):
        """
        Get all scaling decisions with their outcomes for learning.

        Returns:
            List of ScalingDecision objects
        """
        session = self.get_session()

        decisions = session.query(ScalingDecision).filter(
            ScalingDecision.actual_outcome.isnot(None)
        ).all()

        return decisions


def get_database() -> DatabaseManager:
    """
    Get configured database manager instance.

    Returns:
        DatabaseManager instance
    """
    db = DatabaseManager()
    db.create_tables()  # Ensure tables exist
    return db
