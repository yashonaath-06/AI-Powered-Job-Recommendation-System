"""Job description analyzer."""
import re


class JobAnalyzer:
    SKILL_CATEGORIES = {
        "programming": ["python", "java", "javascript", "typescript", "c++", "c#", "ruby", "go", "rust", "php", "swift", "kotlin", "scala", "r"],
        "frameworks": ["react", "angular", "vue", "next.js", "express", "django", "flask", "fastapi", "spring boot", "rails", "laravel", "node.js"],
        "data_science": ["machine learning", "deep learning", "tensorflow", "pytorch", "pandas", "numpy", "scikit-learn", "nlp", "computer vision", "data analysis"],
        "databases": ["sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "dynamodb", "cassandra", "firebase"],
        "cloud": ["aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ci/cd", "devops", "linux", "jenkins"],
        "tools": ["git", "jira", "agile", "scrum", "rest api", "graphql", "microservices", "html", "css", "tailwind"],
    }

    def extract_required_skills(self, description: str) -> list[str]:
        text_lower = description.lower()
        found_skills = []
        for category, skills in self.SKILL_CATEGORIES.items():
            for skill in skills:
                if len(skill) <= 3:
                    if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
                        found_skills.append(skill)
                else:
                    if skill in text_lower:
                        found_skills.append(skill)
        return sorted(list(set(found_skills)))

    def extract_experience_requirement(self, description: str) -> dict:
        patterns = [
            r'(\d+)\s*[-\u2013to]+\s*(\d+)\s*(?:years?|yrs?)',
            r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience|exp)',
        ]
        for pattern in patterns:
            match = re.search(pattern, description.lower())
            if match:
                groups = match.groups()
                if len(groups) == 2:
                    return {"min": float(groups[0]), "max": float(groups[1])}
                return {"min": float(groups[0]), "max": float(groups[0]) + 2}
        return {"min": 0.0, "max": 0.0}

    def analyze_job(self, title: str, description: str, company: str = "") -> dict:
        skills = self.extract_required_skills(description)
        experience = self.extract_experience_requirement(description)
        return {
            "title": title,
            "company": company,
            "skills_required": skills,
            "experience_requirement": experience,
            "requirements": [],
            "job_type": "full-time",
            "is_remote": "remote" in description.lower(),
        }


job_analyzer = JobAnalyzer()
