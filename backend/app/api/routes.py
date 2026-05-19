"""API routes for the Job Recommendation System."""
import os
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.core.config import settings
from app.models.models import Resume, Job, Recommendation, AnalyticsLog
from app.ml.resume_parser import resume_parser
from app.ml.job_analyzer import job_analyzer
from app.ml.ats_scorer import ats_scorer
from app.ml.recommendation_engine import recommendation_engine
from app.schemas.schemas import JobCreate, JobResponse, ResumeUploadResponse, ResumeDetail

router = APIRouter()


@router.post("/resume/upload", response_model=ResumeUploadResponse)
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    allowed_types = [".pdf", ".docx", ".doc", ".txt"]
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_types:
        raise HTTPException(status_code=400, detail=f"File type not supported. Allowed: {', '.join(allowed_types)}")
    file_id = str(uuid.uuid4())
    file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}{file_ext}")
    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Max 10MB.")
    with open(file_path, "wb") as f:
        f.write(content)
    parsed = resume_parser.parse_resume(file_path)
    if parsed.get("error") and file_ext == ".txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            raw_text = f.read()
        parsed["raw_text"] = raw_text
        parsed["skills"] = resume_parser.extract_skills(raw_text)
        parsed["keywords"] = resume_parser.extract_keywords(raw_text)
    ats_result = ats_scorer.compute_ats_score(text=parsed["raw_text"], skills=parsed["skills"]["all"], experience=parsed["experience_years"], education=parsed["education"])
    resume = Resume(filename=file.filename, raw_text=parsed["raw_text"], parsed_data=parsed, skills=parsed["skills"]["all"], experience_years=parsed["experience_years"], education=parsed["education"], keywords=parsed["keywords"], ats_score=ats_result["overall_score"])
    db.add(resume)
    db.commit()
    db.refresh(resume)
    db.add(AnalyticsLog(resume_id=resume.id, event_type="resume_upload", event_data={"filename": file.filename}))
    db.commit()
    return resume


@router.get("/resume/{resume_id}", response_model=ResumeDetail)
async def get_resume(resume_id: int, db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume


@router.get("/resumes")
async def list_resumes(db: Session = Depends(get_db)):
    resumes = db.query(Resume).order_by(Resume.created_at.desc()).all()
    return [{"id": r.id, "filename": r.filename, "skills_count": len(r.skills) if r.skills else 0, "experience_years": r.experience_years, "ats_score": r.ats_score, "created_at": r.created_at.isoformat()} for r in resumes]


@router.get("/resume/{resume_id}/ats-score")
async def get_ats_score(resume_id: int, db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return ats_scorer.compute_ats_score(text=resume.raw_text, skills=resume.skills or [], experience=resume.experience_years, education=resume.education or [])


@router.post("/jobs", response_model=JobResponse)
async def create_job(job_data: JobCreate, db: Session = Depends(get_db)):
    analysis = job_analyzer.analyze_job(title=job_data.title, description=job_data.description, company=job_data.company)
    job = Job(title=job_data.title, company=job_data.company, location=job_data.location, description=job_data.description, requirements=job_data.requirements or analysis["requirements"], skills_required=job_data.skills_required or analysis["skills_required"], experience_min=job_data.experience_min or analysis["experience_requirement"]["min"], experience_max=job_data.experience_max or analysis["experience_requirement"]["max"], salary_min=job_data.salary_min, salary_max=job_data.salary_max, job_type=job_data.job_type or analysis["job_type"], remote=job_data.remote or analysis["is_remote"], category=job_data.category)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.get("/jobs", response_model=list[JobResponse])
async def list_jobs(skip: int = 0, limit: int = 50, category: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Job).filter(Job.is_active == True)
    if category:
        query = query.filter(Job.category == category)
    return query.order_by(Job.posted_date.desc()).offset(skip).limit(limit).all()


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/recommendations/{resume_id}")
async def generate_recommendations(resume_id: int, top_k: int = Query(default=10, le=50), db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    jobs = db.query(Job).filter(Job.is_active == True).all()
    if not jobs:
        raise HTTPException(status_code=404, detail="No jobs available")
    jobs_data = [{"id": j.id, "title": j.title, "company": j.company, "description": j.description, "skills_required": j.skills_required or [], "experience_min": j.experience_min, "experience_max": j.experience_max} for j in jobs]
    results = recommendation_engine.generate_recommendations(resume_text=resume.raw_text, resume_skills=resume.skills or [], resume_experience=resume.experience_years, jobs=jobs_data, top_k=top_k)
    saved = []
    for result in results:
        rec = Recommendation(resume_id=resume_id, job_id=result["job_id"], match_score=result["overall_score"], skill_match_score=result["skill_match_score"], experience_match_score=result["experience_match_score"], semantic_similarity_score=result["semantic_similarity_score"], matched_skills=result["matched_skills"], missing_skills=result["missing_skills"], skill_gaps=result["skill_gaps"], suggested_certifications=result["suggested_certifications"], career_suggestions=result["career_suggestions"], recruiter_summary=result["recruiter_summary"])
        db.add(rec)
        db.flush()
        job = db.query(Job).filter(Job.id == result["job_id"]).first()
        saved.append({"id": rec.id, "resume_id": resume_id, "job_id": result["job_id"], "match_score": result["overall_score"], "skill_match_score": result["skill_match_score"], "experience_match_score": result["experience_match_score"], "semantic_similarity_score": result["semantic_similarity_score"], "matched_skills": result["matched_skills"], "missing_skills": result["missing_skills"], "skill_gaps": result["skill_gaps"], "suggested_certifications": result["suggested_certifications"], "career_suggestions": result["career_suggestions"], "recruiter_summary": result["recruiter_summary"], "job": {"id": job.id, "title": job.title, "company": job.company, "location": job.location, "job_type": job.job_type, "remote": job.remote, "salary_min": job.salary_min, "salary_max": job.salary_max, "skills_required": job.skills_required} if job else None})
    db.commit()
    return saved


@router.get("/recommendations/{resume_id}")
async def get_recommendations(resume_id: int, db: Session = Depends(get_db)):
    recs = db.query(Recommendation).filter(Recommendation.resume_id == resume_id).order_by(Recommendation.match_score.desc()).all()
    results = []
    for rec in recs:
        job = db.query(Job).filter(Job.id == rec.job_id).first()
        results.append({"id": rec.id, "resume_id": rec.resume_id, "job_id": rec.job_id, "match_score": rec.match_score, "skill_match_score": rec.skill_match_score, "experience_match_score": rec.experience_match_score, "semantic_similarity_score": rec.semantic_similarity_score, "matched_skills": rec.matched_skills, "missing_skills": rec.missing_skills, "skill_gaps": rec.skill_gaps, "suggested_certifications": rec.suggested_certifications, "career_suggestions": rec.career_suggestions, "recruiter_summary": rec.recruiter_summary, "created_at": rec.created_at.isoformat(), "job": {"id": job.id, "title": job.title, "company": job.company, "location": job.location, "description": job.description, "job_type": job.job_type, "remote": job.remote, "salary_min": job.salary_min, "salary_max": job.salary_max, "skills_required": job.skills_required, "experience_min": job.experience_min, "experience_max": job.experience_max} if job else None})
    return results


@router.get("/skill-gap/{resume_id}")
async def get_skill_gap_analysis(resume_id: int, db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    jobs = db.query(Job).filter(Job.is_active == True).all()
    all_required = set()
    for job in jobs:
        if job.skills_required:
            all_required.update(job.skills_required)
    current = set(resume.skills or [])
    missing = all_required - current
    skill_gaps = recommendation_engine.analyze_skill_gaps(list(current), list(missing)[:15])
    certs = recommendation_engine.suggest_certifications(list(missing))
    return {"current_skills": sorted(list(current)), "in_demand_skills": sorted(list(all_required))[:20], "missing_skills": sorted(list(missing))[:15], "skill_match_percentage": round(len(current.intersection(all_required)) / max(len(all_required), 1) * 100, 2), "skill_gaps": skill_gaps, "suggested_certifications": certs}


@router.get("/analytics/overview")
async def get_analytics_overview(db: Session = Depends(get_db)):
    total_resumes = db.query(func.count(Resume.id)).scalar()
    total_jobs = db.query(func.count(Job.id)).filter(Job.is_active == True).scalar()
    total_recs = db.query(func.count(Recommendation.id)).scalar()
    avg_match = db.query(func.avg(Recommendation.match_score)).scalar() or 0
    jobs = db.query(Job).filter(Job.is_active == True).all()
    skill_demand = {}
    for job in jobs:
        if job.skills_required:
            for skill in job.skills_required:
                skill_demand[skill] = skill_demand.get(skill, 0) + 1
    top_skills = sorted(skill_demand.items(), key=lambda x: x[1], reverse=True)[:10]
    recs = db.query(Recommendation).all()
    score_ranges = {"90-100": 0, "80-89": 0, "70-79": 0, "60-69": 0, "50-59": 0, "Below 50": 0}
    all_missing = {}
    for rec in recs:
        s = rec.match_score
        if s >= 90: score_ranges["90-100"] += 1
        elif s >= 80: score_ranges["80-89"] += 1
        elif s >= 70: score_ranges["70-79"] += 1
        elif s >= 60: score_ranges["60-69"] += 1
        elif s >= 50: score_ranges["50-59"] += 1
        else: score_ranges["Below 50"] += 1
        if rec.missing_skills:
            for skill in rec.missing_skills:
                all_missing[skill] = all_missing.get(skill, 0) + 1
    top_gaps = sorted(all_missing.items(), key=lambda x: x[1], reverse=True)[:10]
    return {"total_resumes": total_resumes, "total_jobs": total_jobs, "total_recommendations": total_recs, "avg_match_score": round(avg_match, 2), "top_skills_in_demand": [{"skill": s, "count": c} for s, c in top_skills], "skill_gap_summary": [{"skill": s, "count": c} for s, c in top_gaps], "match_score_distribution": [{"range": k, "count": v} for k, v in score_ranges.items()]}


@router.get("/analytics/resume/{resume_id}")
async def get_resume_analytics(resume_id: int, db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    recs = db.query(Recommendation).filter(Recommendation.resume_id == resume_id).all()
    if not recs:
        return {"resume_id": resume_id, "total_recommendations": 0, "avg_match_score": 0, "top_match_score": 0, "ats_score": resume.ats_score, "skills_count": len(resume.skills or []), "experience_years": resume.experience_years, "match_score_distribution": [], "skills_matched_across_jobs": [], "skills_commonly_missing": [], "top_matching_jobs": []}
    scores = [r.match_score for r in recs]
    all_matched = set()
    all_missing = set()
    for rec in recs:
        if rec.matched_skills: all_matched.update(rec.matched_skills)
        if rec.missing_skills: all_missing.update(rec.missing_skills)
    return {"resume_id": resume_id, "total_recommendations": len(recs), "avg_match_score": round(sum(scores) / len(scores), 2), "top_match_score": round(max(scores), 2), "ats_score": resume.ats_score, "skills_count": len(resume.skills or []), "experience_years": resume.experience_years, "skills_matched_across_jobs": sorted(list(all_matched)), "skills_commonly_missing": sorted(list(all_missing))[:10], "match_score_distribution": [{"range": "90-100", "count": len([s for s in scores if s >= 90])}, {"range": "80-89", "count": len([s for s in scores if 80 <= s < 90])}, {"range": "70-79", "count": len([s for s in scores if 70 <= s < 80])}, {"range": "60-69", "count": len([s for s in scores if 60 <= s < 70])}, {"range": "Below 60", "count": len([s for s in scores if s < 60])}], "top_matching_jobs": [{"job_id": r.job_id, "match_score": r.match_score, "matched_skills": r.matched_skills} for r in sorted(recs, key=lambda x: x.match_score, reverse=True)[:5]]}


@router.get("/career-suggestions/{resume_id}")
async def get_career_suggestions(resume_id: int, db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    skills = resume.skills or []
    experience = resume.experience_years
    role_categories = {
        "Frontend Developer": ["react", "angular", "vue", "javascript", "typescript", "html", "css"],
        "Backend Developer": ["python", "java", "node.js", "django", "fastapi", "spring boot"],
        "Full Stack Developer": ["react", "node.js", "javascript", "python", "sql", "mongodb"],
        "Data Scientist": ["python", "machine learning", "pandas", "numpy", "tensorflow"],
        "DevOps Engineer": ["docker", "kubernetes", "aws", "terraform", "ci/cd", "linux"],
        "ML Engineer": ["python", "tensorflow", "pytorch", "deep learning", "machine learning"],
        "Cloud Architect": ["aws", "azure", "gcp", "terraform", "kubernetes", "microservices"],
    }
    role_scores = {}
    for role, role_skills in role_categories.items():
        matched = len(set(s.lower() for s in skills).intersection(set(role_skills)))
        role_scores[role] = matched / len(role_skills) * 100
    sorted_roles = sorted(role_scores.items(), key=lambda x: x[1], reverse=True)
    if experience < 2:
        growth_paths = [{"stage": "Junior Developer", "timeline": "Current"}, {"stage": "Mid-Level", "timeline": "2-3 years"}, {"stage": "Senior", "timeline": "4-6 years"}, {"stage": "Tech Lead", "timeline": "7+ years"}]
    elif experience < 5:
        growth_paths = [{"stage": "Mid-Level", "timeline": "Current"}, {"stage": "Senior", "timeline": "1-2 years"}, {"stage": "Tech Lead / Architect", "timeline": "3-5 years"}, {"stage": "Engineering Manager", "timeline": "5+ years"}]
    else:
        growth_paths = [{"stage": "Senior Developer", "timeline": "Current"}, {"stage": "Staff Engineer", "timeline": "1-2 years"}, {"stage": "Principal Engineer", "timeline": "3-5 years"}, {"stage": "VP Engineering / CTO", "timeline": "5+ years"}]
    return {"current_role_fit": sorted_roles[0][0] if sorted_roles else "General Developer", "role_fit_score": round(sorted_roles[0][1], 2) if sorted_roles else 0, "suggested_roles": [{"role": r, "fit_percentage": round(s, 2)} for r, s in sorted_roles[:5]], "growth_stage": "Entry Level" if experience < 2 else "Mid Level" if experience < 5 else "Senior Level", "growth_paths": growth_paths, "industry_trends": ["AI/ML skills demand increased 45% in 2024", "Cloud certifications boost salary by 20-30%", "Full-stack developers most in-demand at startups", "Remote work opportunities growing for specialized roles", "DevOps/SRE roles seeing 35% growth year-over-year"], "salary_insights": {"entry_level": "$60,000 - $85,000", "mid_level": "$85,000 - $130,000", "senior_level": "$130,000 - $200,000", "lead_level": "$150,000 - $250,000+"}}
