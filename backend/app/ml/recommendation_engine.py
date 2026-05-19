"""Recommendation engine - orchestrates matching, skill gap analysis, and career suggestions."""
from app.ml.similarity_engine import similarity_engine
from app.ml.resume_parser import CERTIFICATIONS_DB

LEARNING_RESOURCES = {
    "python": {"platform": "Coursera", "course": "Python for Everybody", "duration": "8 weeks"},
    "java": {"platform": "Udemy", "course": "Java Masterclass", "duration": "10 weeks"},
    "javascript": {"platform": "freeCodeCamp", "course": "JavaScript Algorithms", "duration": "6 weeks"},
    "react": {"platform": "Udemy", "course": "React - The Complete Guide", "duration": "8 weeks"},
    "machine learning": {"platform": "Coursera", "course": "ML by Andrew Ng", "duration": "12 weeks"},
    "aws": {"platform": "AWS Training", "course": "AWS Cloud Practitioner", "duration": "6 weeks"},
    "docker": {"platform": "Docker", "course": "Docker Getting Started", "duration": "4 weeks"},
    "sql": {"platform": "Khan Academy", "course": "Intro to SQL", "duration": "4 weeks"},
    "kubernetes": {"platform": "Linux Foundation", "course": "Kubernetes Basics", "duration": "6 weeks"},
    "typescript": {"platform": "TypeScript Docs", "course": "TypeScript Deep Dive", "duration": "4 weeks"},
    "node.js": {"platform": "Udemy", "course": "NodeJS Complete Guide", "duration": "8 weeks"},
    "tensorflow": {"platform": "Google", "course": "TensorFlow Developer", "duration": "10 weeks"},
    "pytorch": {"platform": "PyTorch", "course": "PyTorch Fundamentals", "duration": "8 weeks"},
    "django": {"platform": "Django Project", "course": "Django for Beginners", "duration": "6 weeks"},
    "mongodb": {"platform": "MongoDB University", "course": "M001 Basics", "duration": "4 weeks"},
}


class RecommendationEngine:
    def generate_recommendations(self, resume_text: str, resume_skills: list[str], resume_experience: float, jobs: list[dict], top_k: int = 10) -> list[dict]:
        matches = similarity_engine.batch_match(resume_text=resume_text, resume_skills=resume_skills, resume_experience=resume_experience, jobs=jobs)
        enriched = []
        for match in matches[:top_k]:
            skill_gaps = self.analyze_skill_gaps(resume_skills, match.get("missing_skills", []))
            career = self.generate_career_suggestions(match.get("matched_skills", []), match.get("missing_skills", []), match.get("job_title", ""), resume_experience)
            recruiter = self.generate_recruiter_summary(match.get("overall_score", 0), match.get("matched_skills", []), match.get("missing_skills", []), resume_experience, match.get("job_title", ""))
            certs = self.suggest_certifications(match.get("missing_skills", []))
            match["skill_gaps"] = skill_gaps
            match["career_suggestions"] = career
            match["recruiter_summary"] = recruiter
            match["suggested_certifications"] = certs
            enriched.append(match)
        return enriched

    def analyze_skill_gaps(self, current_skills: list[str], required_skills: list[str]) -> list[dict]:
        gaps = []
        for skill in required_skills:
            sl = skill.lower()
            gap = {"skill": skill, "priority": "high" if sl in ["python", "java", "javascript", "sql", "react"] else "medium", "difficulty": "advanced" if sl in {"machine learning", "deep learning", "kubernetes"} else "intermediate" if sl in {"react", "django", "aws", "docker"} else "beginner"}
            gap["recommended_course"] = LEARNING_RESOURCES.get(sl, {"platform": "Udemy/Coursera", "course": f"Complete {skill.title()} Course", "duration": "6 weeks"})
            gaps.append(gap)
        return gaps

    def suggest_certifications(self, missing_skills: list[str]) -> list[str]:
        suggested = set()
        for skill in missing_skills:
            for key, certs in CERTIFICATIONS_DB.items():
                if key in skill.lower() or skill.lower() in key:
                    for cert in certs:
                        suggested.add(cert)
        return sorted(list(suggested))[:5]

    def generate_career_suggestions(self, matched: list, missing: list, job_title: str, exp: float) -> str:
        total = len(matched) + len(missing)
        ratio = len(matched) / total if total > 0 else 0
        parts = []
        if ratio >= 0.8:
            parts.append(f"Excellent fit for {job_title}. Apply immediately.")
        elif ratio >= 0.6:
            parts.append(f"Strong candidate for {job_title}. Focus on: {', '.join(missing[:3])}")
        elif ratio >= 0.4:
            parts.append(f"Moderate fit. Build projects in: {', '.join(missing[:4])}")
        else:
            parts.append("Significant upskilling needed. Start with foundational courses.")
        if exp < 2:
            parts.append("Focus on internships and open-source contributions.")
        elif exp < 5:
            parts.append("Emphasize project leadership and impact metrics.")
        else:
            parts.append("Target leadership and architect roles.")
        return " ".join(parts)

    def generate_recruiter_summary(self, score: float, matched: list, missing: list, exp: float, title: str) -> str:
        fit = "Excellent" if score >= 80 else "Strong" if score >= 60 else "Moderate" if score >= 40 else "Limited"
        lines = [f"[{fit} Match - {score:.0f}%] Candidate for {title}:", f"- Experience: {exp:.0f} years", f"- Matching Skills ({len(matched)}): {', '.join(matched[:6])}"]
        if missing:
            lines.append(f"- Skills Gap ({len(missing)}): {', '.join(missing[:4])}")
        rec = "Proceed to interview" if score >= 60 else "Consider for development program" if score >= 40 else "May not meet minimum requirements"
        lines.append(f"- Recommendation: {rec}")
        return "\n".join(lines)


recommendation_engine = RecommendationEngine()
