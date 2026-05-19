"""Semantic similarity engine using TF-IDF and sentence transformers."""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMER_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMER_AVAILABLE = False


class SimilarityEngine:
    def __init__(self):
        self._tfidf_vectorizer = TfidfVectorizer(max_features=5000, stop_words='english', ngram_range=(1, 2), sublinear_tf=True)
        self._model = None
        self._use_transformers = False

    def _get_transformer_model(self):
        if self._model is None and SENTENCE_TRANSFORMER_AVAILABLE:
            try:
                self._model = SentenceTransformer('all-MiniLM-L6-v2')
                self._use_transformers = True
            except Exception:
                self._use_transformers = False
        return self._model

    def tfidf_similarity(self, text1: str, text2: str) -> float:
        try:
            tfidf_matrix = self._tfidf_vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            return float(similarity[0][0])
        except Exception:
            return 0.0

    def semantic_similarity(self, text1: str, text2: str) -> float:
        model = self._get_transformer_model()
        if model is None:
            return self.tfidf_similarity(text1, text2)
        try:
            embeddings = model.encode([text1, text2])
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])
            return float(similarity[0][0])
        except Exception:
            return self.tfidf_similarity(text1, text2)

    def skill_similarity(self, resume_skills: list[str], job_skills: list[str]) -> dict:
        if not job_skills:
            return {"score": 0.0, "matched": [], "missing": [], "match_percentage": 0.0}
        resume_set = set(s.lower() for s in resume_skills)
        job_set = set(s.lower() for s in job_skills)
        matched = resume_set.intersection(job_set)
        missing = job_set - resume_set
        pct = (len(matched) / len(job_set)) * 100 if job_set else 0
        return {"score": pct, "matched": sorted(list(matched)), "missing": sorted(list(missing)), "match_percentage": round(pct, 2)}

    def experience_similarity(self, resume_years: float, job_min: float, job_max: float) -> float:
        if job_min == 0 and job_max == 0:
            return 80.0
        if resume_years >= job_min and resume_years <= job_max:
            return 100.0
        elif resume_years >= job_min:
            return max(60.0, 100.0 - ((resume_years - job_max) * 5))
        else:
            return max(20.0, 100.0 - ((job_min - resume_years) * 15))

    def compute_overall_match(self, resume_text: str, job_description: str, resume_skills: list[str], job_skills: list[str], resume_experience: float, job_exp_min: float, job_exp_max: float) -> dict:
        tfidf_score = self.tfidf_similarity(resume_text, job_description) * 100
        semantic_score = self.semantic_similarity(resume_text[:1000], job_description[:1000]) * 100
        skill_result = self.skill_similarity(resume_skills, job_skills)
        skill_score = skill_result["score"]
        exp_score = self.experience_similarity(resume_experience, job_exp_min, job_exp_max)
        overall_score = skill_score * 0.40 + semantic_score * 0.25 + tfidf_score * 0.20 + exp_score * 0.15
        return {
            "overall_score": round(min(overall_score, 100.0), 2),
            "skill_match_score": round(skill_score, 2),
            "semantic_similarity_score": round(semantic_score, 2),
            "tfidf_score": round(tfidf_score, 2),
            "experience_match_score": round(exp_score, 2),
            "matched_skills": skill_result["matched"],
            "missing_skills": skill_result["missing"],
        }

    def batch_match(self, resume_text: str, resume_skills: list[str], resume_experience: float, jobs: list[dict]) -> list[dict]:
        results = []
        for job in jobs:
            match = self.compute_overall_match(
                resume_text=resume_text,
                job_description=job.get("description", ""),
                resume_skills=resume_skills,
                job_skills=job.get("skills_required", []) or [],
                resume_experience=resume_experience,
                job_exp_min=job.get("experience_min", 0),
                job_exp_max=job.get("experience_max", 0),
            )
            match["job_id"] = job.get("id")
            match["job_title"] = job.get("title")
            match["company"] = job.get("company")
            results.append(match)
        results.sort(key=lambda x: x["overall_score"], reverse=True)
        return results


similarity_engine = SimilarityEngine()
