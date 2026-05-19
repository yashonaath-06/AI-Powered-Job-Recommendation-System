"""Resume parsing module - extracts skills, experience, education from resumes."""
import re
from pathlib import Path

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    from docx import Document
except ImportError:
    Document = None

TECHNICAL_SKILLS = {
    "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "go",
    "rust", "php", "swift", "kotlin", "scala", "r", "matlab", "perl",
    "react", "angular", "vue", "next.js", "express", "django", "flask",
    "fastapi", "spring boot", "rails", "laravel", "svelte", "nuxt.js",
    "machine learning", "deep learning", "tensorflow", "pytorch", "keras",
    "scikit-learn", "pandas", "numpy", "scipy", "matplotlib", "seaborn",
    "nlp", "computer vision", "neural networks", "data mining",
    "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
    "cassandra", "dynamodb", "firebase", "sqlite", "oracle",
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform",
    "jenkins", "ci/cd", "github actions", "ansible", "linux",
    "git", "jira", "confluence", "figma", "postman",
    "tableau", "power bi", "excel",
    "rest api", "graphql", "microservices", "agile", "scrum",
    "html", "css", "sass", "tailwind", "bootstrap",
    "node.js", "deno", "webpack", "vite",
}

SOFT_SKILLS = {
    "leadership", "communication", "teamwork", "problem solving",
    "critical thinking", "time management", "adaptability", "creativity",
    "collaboration", "presentation", "mentoring", "project management",
}

EDUCATION_KEYWORDS = [
    "bachelor", "master", "phd", "doctorate", "b.tech", "m.tech",
    "b.sc", "m.sc", "b.e", "m.e", "mba", "bca", "mca",
    "b.com", "m.com", "diploma", "certification", "degree",
    "university", "college", "institute",
]

CERTIFICATIONS_DB = {
    "python": ["Python Institute PCEP", "Google Python Certificate"],
    "aws": ["AWS Certified Solutions Architect", "AWS Cloud Practitioner"],
    "azure": ["Azure Fundamentals AZ-900", "Azure Developer Associate"],
    "data science": ["IBM Data Science Professional", "Google Data Analytics"],
    "machine learning": ["Stanford ML Certificate", "AWS ML Specialty"],
    "project management": ["PMP", "PRINCE2", "Certified Scrum Master"],
    "docker": ["Docker Certified Associate"],
    "kubernetes": ["CKA - Certified Kubernetes Administrator"],
    "react": ["Meta Front-End Developer Certificate"],
    "java": ["Oracle Certified Professional Java"],
    "cloud": ["Google Cloud Professional Cloud Architect"],
}


class ResumeParser:
    def extract_text_from_pdf(self, file_path: str) -> str:
        if PyPDF2 is None:
            return ""
        text = ""
        try:
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"Error reading PDF: {e}")
        return text

    def extract_text_from_docx(self, file_path: str) -> str:
        if Document is None:
            return ""
        text = ""
        try:
            doc = Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            print(f"Error reading DOCX: {e}")
        return text

    def extract_text(self, file_path: str) -> str:
        path = Path(file_path)
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            return self.extract_text_from_pdf(file_path)
        elif suffix in (".docx", ".doc"):
            return self.extract_text_from_docx(file_path)
        elif suffix == ".txt":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        return ""

    def extract_skills(self, text: str) -> dict:
        text_lower = text.lower()
        found_technical = []
        for skill in TECHNICAL_SKILLS:
            if len(skill) <= 3:
                if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
                    found_technical.append(skill)
            else:
                if skill in text_lower:
                    found_technical.append(skill)
        found_soft = [s for s in SOFT_SKILLS if s in text_lower]
        return {
            "technical": sorted(list(set(found_technical))),
            "soft": sorted(list(set(found_soft))),
            "all": sorted(list(set(found_technical + found_soft))),
        }

    def extract_experience(self, text: str) -> float:
        patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience|exp)',
            r'experience\s*(?:of)?\s*(\d+)\+?\s*(?:years?|yrs?)',
        ]
        years_found = []
        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            years_found.extend([float(m) for m in matches])
        if years_found:
            return max(years_found)
        date_pattern = r'(20\d{2}|19\d{2})\s*[-\u2013]\s*(20\d{2}|19\d{2}|present|current)'
        date_matches = re.findall(date_pattern, text.lower())
        total_years = 0
        for start, end in date_matches:
            start_year = int(start)
            end_year = 2024 if end in ("present", "current") else int(end)
            total_years += max(0, end_year - start_year)
        return float(total_years)

    def extract_education(self, text: str) -> list[dict]:
        education_list = []
        lines = text.split('\n')
        for line in lines:
            line_lower = line.lower().strip()
            for keyword in EDUCATION_KEYWORDS:
                if keyword in line_lower:
                    education_entry = {"text": line.strip(), "type": self._classify_education(line_lower)}
                    year_match = re.search(r'(20\d{2}|19\d{2})', line)
                    if year_match:
                        education_entry["year"] = int(year_match.group(1))
                    education_list.append(education_entry)
                    break
        seen = set()
        unique = []
        for edu in education_list:
            key = edu["text"][:50]
            if key not in seen:
                seen.add(key)
                unique.append(edu)
        return unique[:5]

    def _classify_education(self, text: str) -> str:
        if any(k in text for k in ["phd", "doctorate"]):
            return "Doctorate"
        elif any(k in text for k in ["master", "m.tech", "m.sc", "m.e", "mba", "mca"]):
            return "Masters"
        elif any(k in text for k in ["bachelor", "b.tech", "b.sc", "b.e", "bca"]):
            return "Bachelors"
        elif "diploma" in text:
            return "Diploma"
        return "Other"

    def extract_keywords(self, text: str) -> list[str]:
        stop_words = {"the", "a", "an", "is", "are", "was", "were", "be", "been", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should", "and", "or", "but", "if", "for", "to", "from", "in", "on", "at", "by", "with", "about", "of", "this", "that", "not", "no", "so", "very", "just", "also", "we", "our", "you", "your", "they", "my", "me"}
        words = re.findall(r'\b[a-z][a-z+#.]{2,}\b', text.lower())
        filtered = [w for w in words if w not in stop_words and len(w) > 2]
        freq = {}
        for word in filtered:
            freq[word] = freq.get(word, 0) + 1
        sorted_keywords = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return [k for k, v in sorted_keywords[:30]]

    def parse_resume(self, file_path: str) -> dict:
        text = self.extract_text(file_path)
        if not text.strip():
            return {"raw_text": "", "skills": {"technical": [], "soft": [], "all": []}, "experience_years": 0.0, "education": [], "keywords": [], "error": "Could not extract text"}
        return {
            "raw_text": text,
            "skills": self.extract_skills(text),
            "experience_years": self.extract_experience(text),
            "education": self.extract_education(text),
            "keywords": self.extract_keywords(text),
        }


resume_parser = ResumeParser()
