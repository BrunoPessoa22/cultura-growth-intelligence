"""Database module for storing and retrieving historical campaign analysis data."""

import os
from datetime import datetime
from typing import Optional, List, Dict
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import streamlit as st

Base = declarative_base()

class CampaignSnapshot(Base):
    """Store campaign performance snapshots over time."""
    __tablename__ = 'campaign_snapshots'
    
    id = Column(Integer, primary_key=True)
    snapshot_date = Column(DateTime, default=datetime.utcnow, index=True)
    user_email = Column(String(255), index=True)
    campaign_name = Column(String(500))
    campaign_status = Column(String(50))
    spend = Column(Float)
    impressions = Column(Integer)
    purchases = Column(Float)
    paying_users = Column(Float)
    payment_cac = Column(Float)
    predicted_ltv = Column(Float)
    ltv_cac_ratio = Column(Float)
    scale_score = Column(Float)
    total_revenue = Column(Float)

class AnalysisLog(Base):
    """Log each analysis run."""
    __tablename__ = 'analysis_logs'
    
    id = Column(Integer, primary_key=True)
    run_date = Column(DateTime, default=datetime.utcnow, index=True)
    user_email = Column(String(255), index=True)
    campaigns_analyzed = Column(Integer)
    total_spend = Column(Float)
    total_purchases = Column(Float)
    ai_insights = Column(Text)

class DatabaseManager:
    """Manage database connections and operations."""
    
    def __init__(self):
        """Initialize database connection."""
        if hasattr(st, 'secrets') and 'DATABASE_URL' in st.secrets:
            database_url = st.secrets['DATABASE_URL']
        else:
            database_url = os.getenv('DATABASE_URL', 'sqlite:///cultura_growth_history.db')
        
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def save_analysis(self, df: pd.DataFrame, user_email: str, ai_insights: Optional[str] = None):
        """Save campaign analysis results to database."""
        session = self.Session()
        try:
            log = AnalysisLog(
                user_email=user_email,
                campaigns_analyzed=len(df),
                total_spend=df['spend'].sum() if 'spend' in df.columns else 0,
                total_purchases=df['paying_users'].sum() if 'paying_users' in df.columns else 0,
                ai_insights=ai_insights
            )
            session.add(log)
            
            for _, row in df.iterrows():
                snapshot = CampaignSnapshot(
                    user_email=user_email,
                    campaign_name=row.get('campaign_name', ''),
                    spend=row.get('spend', 0),
                    purchases=row.get('purchases', 0),
                    paying_users=row.get('paying_users', 0),
                    payment_cac=row.get('payment_cac', 0),
                    predicted_ltv=row.get('predicted_ltv', 0),
                    ltv_cac_ratio=row.get('ltv_cac_ratio', 0),
                    scale_score=row.get('scale_score', 0),
                    total_revenue=row.get('total_revenue', 0)
                )
                session.add(snapshot)
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_campaign_history(self, campaign_name: str, user_email: str, days: int = 90) -> pd.DataFrame:
        """Get historical data for a specific campaign."""
        session = self.Session()
        try:
            cutoff_date = datetime.utcnow() - pd.Timedelta(days=days)
            snapshots = session.query(CampaignSnapshot).filter(
                CampaignSnapshot.campaign_name == campaign_name,
                CampaignSnapshot.user_email == user_email,
                CampaignSnapshot.snapshot_date >= cutoff_date
            ).order_by(CampaignSnapshot.snapshot_date).all()
            
            data = [{
                'date': s.snapshot_date,
                'spend': s.spend,
                'purchases': s.purchases,
                'cac': s.payment_cac,
                'ltv_cac_ratio': s.ltv_cac_ratio,
                'scale_score': s.scale_score
            } for s in snapshots]
            
            return pd.DataFrame(data)
        finally:
            session.close()
    
    def get_week_over_week_comparison(self, user_email: str) -> Dict:
        """Compare this week vs last week performance."""
        session = self.Session()
        try:
            now = datetime.utcnow()
            week_ago = now - pd.Timedelta(days=7)
            two_weeks_ago = now - pd.Timedelta(days=14)
            
            this_week = session.query(CampaignSnapshot).filter(
                CampaignSnapshot.user_email == user_email,
                CampaignSnapshot.snapshot_date >= week_ago
            ).all()
            
            last_week = session.query(CampaignSnapshot).filter(
                CampaignSnapshot.user_email == user_email,
                CampaignSnapshot.snapshot_date >= two_weeks_ago,
                CampaignSnapshot.snapshot_date < week_ago
            ).all()
            
            def agg(snapshots):
                if not snapshots:
                    return None
                return {
                    'total_spend': sum(s.spend or 0 for s in snapshots),
                    'total_purchases': sum(s.purchases or 0 for s in snapshots),
                    'avg_cac': sum(s.payment_cac or 0 for s in snapshots) / len(snapshots),
                    'avg_ltv_cac': sum(s.ltv_cac_ratio or 0 for s in snapshots) / len(snapshots)
                }
            
            return {
                'this_week': agg(this_week),
                'last_week': agg(last_week)
            }
        finally:
            session.close()
