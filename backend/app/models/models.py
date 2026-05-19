"""SQLAlchemy database models."""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Resume(Base):
    __tablename__ = "resumes"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    raw_text = Column(Text, nullable=False)
    parsed_data = Column(JSON, nullable=True)
    skills = Column(JSON, nullable=True)
    experience_years = Column(Float, default=0.0)
    education = Column(JSON, nullable=True)
    keywords = Column(JSON, nullable=True)
    ats_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    recommendations = relationship("Recommendation", back_populates="resume")


class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)
    description = Column(Text, nullable=False)
    requirements = Column(JSON, nullable=True)
    skills_required = Column(JSON, nullable=True)
    experience_min = Column(Float, default=0.0)
    experience_max = Column(Float, default=0.0)
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    job_type = Column(String(50), nullable=True)
    remote = Column(Boolean, default=False)
    category = Column(String(100), nullable=True)
    posted_date = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    recommendations = relationship("Recommendation", back_populates="job")


class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    match_score = Column(Float, nullable=False)
    skill_match_score = Column(Float, default=0.0)
    experience_match_score = Column(Float, default=0.0)
    semantic_similarity_score = Column(Float, default=0.0)
    matched_skills = Column(JSON, nullable=True)
    missing_skills = Column(JSON, nullable=True)
    skill_gaps = Column(JSON, nullable=True)
    suggested_certifications = Column(JSON, nullable=True)
    career_suggestions = Column(Text, nullable=True)
    recruiter_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    resume = relationship("Resume", back_populates="recommendations")
    job = relationship("Job", back_populates="recommendations")


class AnalyticsLog(Base):
    __tablename__ = "analytics_logs"
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=True)
    event_type = Column(String(100), nullable=False)
    event_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
