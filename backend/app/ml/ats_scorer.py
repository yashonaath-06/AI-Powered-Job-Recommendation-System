"""ATS (Applicant Tracking System) compatibility scorer."""
import re


class ATSScorer:
    EXPECTED_SECTIONS = ["education", "experience", "skills", "projects", "certifications", "summary", "objective"]
    ACTION_VERBS = ["achieved", "built", "created", "delivered", "developed", "designed", "engineered", "implemented", "improved", "led", "managed", "optimized", "reduced", "resolved"]

    def score_format(self, text: str) -> dict:
        score = 100.0
        suggestions = []
        sections_found = [s for s in self.EXPECTED_SECTIONS if re.search(r'(?:^|\n)\s*' + re.escape(s), text.lower())]
        if len(sections_found) < 3:
            score -= 20
            suggestions.append("Add clear section headers (Education, Experience, Skills, Projects)")
        word_count = len(text.split())
        if word_count < 150:
            score -= 20
            suggestions.append("Resume is too short. Add more detail.")
        elif word_count > 1000:
            score -= 10
            suggestions.append("Consider condensing to 1-2 pages.")
        return {"score": max(0, min(100, score)), "suggestions": suggestions}

    def score_keywords(self, text: str, target_keywords=None) -> dict:
        score = 70.0
        suggestions = []
        text_lower = text.lower()
        action_verbs_found = [v for v in self.ACTION_VERBS if v in text_lower]
        score += min(30, len(action_verbs_found) * 5)
        if len(action_verbs_found) < 3:
            suggestions.append("Use more action verbs (achieved, developed, implemented, optimized)")
        has_numbers = bool(re.search(r'\d+%|\d+\s*(?:users|clients|projects)', text_lower))
        if has_numbers:
            score += 10
        else:
            suggestions.append("Add quantifiable achievements (e.g., 'Increased performance by 30%')")
        return {"score": max(0, min(100, score)), "suggestions": suggestions}

    def score_readability(self, text: str) -> dict:
        score = 85.0
        suggestions = []
        special_chars = len(re.findall(r'[^\w\s\-.,;:()/@#&$%+]', text))
        if special_chars > 10:
            score -= 15
            suggestions.append("Reduce special characters that may confuse ATS systems.")
        return {"score": max(0, min(100, score)), "suggestions": suggestions}

    def score_completeness(self, text: str, skills: list, experience: float, education: list) -> dict:
        score = 0.0
        suggestions = []
        if re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', text):
            score += 15
        else:
            suggestions.append("Add your email address.")
        if re.search(r'[\+]?[(]?[0-9]{1,4}[)]?[-\s./0-9]{7,}', text):
            score += 10
        else:
            suggestions.append("Add your phone number.")
        if len(skills) >= 5:
            score += 25
        elif len(skills) >= 3:
            score += 15
            suggestions.append("Add more technical skills (aim for 8-12).")
        else:
            suggestions.append("Add a dedicated skills section.")
        if experience > 0:
            score += 20
        else:
            suggestions.append("Clearly state your years of experience.")
        if education:
            score += 15
        else:
            suggestions.append("Add educational qualifications.")
        if "linkedin" in text.lower() or "github" in text.lower():
            score += 15
        else:
            suggestions.append("Add LinkedIn/GitHub links.")
        return {"score": max(0, min(100, score)), "suggestions": suggestions}

    def compute_ats_score(self, text: str, skills: list, experience: float, education: list, target_keywords=None) -> dict:
        fmt = self.score_format(text)
        kw = self.score_keywords(text, target_keywords)
        rd = self.score_readability(text)
        cm = self.score_completeness(text, skills, experience, education)
        overall = fmt["score"] * 0.25 + kw["score"] * 0.30 + rd["score"] * 0.20 + cm["score"] * 0.25
        all_suggestions = fmt["suggestions"] + kw["suggestions"] + rd["suggestions"] + cm["suggestions"]
        return {
            "overall_score": round(overall, 1),
            "format_score": round(fmt["score"], 1),
            "keyword_score": round(kw["score"], 1),
            "readability_score": round(rd["score"], 1),
            "completeness_score": round(cm["score"], 1),
            "suggestions": all_suggestions[:10],
        }


ats_scorer = ATSScorer()
