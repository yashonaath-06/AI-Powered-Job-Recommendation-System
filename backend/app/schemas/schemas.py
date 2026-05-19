"""Pydantic schemas for API request/response validation."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ResumeUploadResponse(BaseModel):
    id: int
    filename: str
    skills: list[str]
    experience_years: float
    education: list[dict]
    keywords: list[str]
    ats_score: float
    created_at: datetime
    class Config:
        from_attributes = True


class ResumeDetail(BaseModel):
    id: int
    filename: str
    raw_text: str
    parsed_data: Optional[dict] = None
    skills: list[str]
    experience_years: float
    education: list[dict]
    keywords: list[str]
    ats_score: float
    created_at: datetime
    class Config:
        from_attributes = True


class JobBase(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    description: str
    requirements: Optional[list[str]] = None
    skills_required: Optional[list[str]] = None
    experience_min: float = 0.0
    experience_max: float = 0.0
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    job_type: Optional[str] = None
    remote: bool = False
    category: Optional[str] = None


class JobCreate(JobBase):
    pass


class JobResponse(JobBase):
    id: int
    posted_date: datetime
    is_active: bool
    class Config:
        from_attributes = True
