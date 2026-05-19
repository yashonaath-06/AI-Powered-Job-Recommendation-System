# AI-Powered Job Recommendation System

A production-grade, full-stack AI-powered job recommendation platform using NLP, TF-IDF, cosine similarity, and semantic embeddings to match resumes with job listings.

---

## Features

| Feature | Description |
|---------|-------------|
| Resume Upload & Parsing | PDF/DOCX/TXT with NLP skill extraction |
| AI Job Matching | Semantic similarity + TF-IDF + cosine similarity |
| ATS Compatibility Score | Format, keywords, readability, completeness |
| Skill Gap Analysis | Missing skills with learning paths |
| Career Suggestions | Role fit, growth paths, salary insights |
| Recruiter Summaries | Auto-generated candidate evaluations |
| Analytics Dashboard | Recharts visualizations |
| Dark/Light Mode | Modern responsive SaaS UI |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, TypeScript, Tailwind CSS, shadcn/ui, Recharts |
| Backend | FastAPI (Python), SQLAlchemy, Pydantic |
| ML/NLP | scikit-learn (TF-IDF), sentence-transformers, cosine similarity |
| Database | SQLite (default) / PostgreSQL |
| Deployment | Docker, Docker Compose |

---

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Linux/Mac
# venv\Scripts\activate       # Windows
pip install -r requirements.txt
python seed_data.py           # Load 15 sample jobs
python run.py                 # Starts on http://localhost:8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev                   # Starts on http://localhost:3000
```

### Docker (Alternative)

```bash
docker-compose up --build
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/resume/upload` | Upload and parse resume |
| GET | `/api/resume/{id}` | Get resume details |
| GET | `/api/resumes` | List all resumes |
| GET | `/api/resume/{id}/ats-score` | ATS compatibility score |
| GET | `/api/jobs` | List jobs |
| POST | `/api/recommendations/{resume_id}` | Generate recommendations |
| GET | `/api/recommendations/{resume_id}` | Get saved recommendations |
| GET | `/api/skill-gap/{resume_id}` | Skill gap analysis |
| GET | `/api/career-suggestions/{resume_id}` | Career suggestions |
| GET | `/api/analytics/overview` | Global analytics |
| GET | `/api/analytics/resume/{id}` | Resume analytics |

API Docs: http://localhost:8000/docs

---

## ML Pipeline

1. **Resume Parsing** - NLP pattern matching for 100+ skills
2. **TF-IDF Vectorization** - Text to numerical vectors
3. **Semantic Embeddings** - sentence-transformers (all-MiniLM-L6-v2)
4. **Cosine Similarity** - Vector distance measurement
5. **Weighted Scoring** - Skill(40%) + Semantic(25%) + TF-IDF(20%) + Experience(15%)
6. **Ranking & Enrichment** - Skill gaps, certifications, career advice

---

## Testing

Use the included `sample_resume.txt` file:
1. Start backend and frontend
2. Go to Upload page
3. Upload `sample_resume.txt`
4. View ATS score and extracted skills
5. Click "Generate Recommendations"
6. Explore recommendations, skill gaps, and career suggestions

---

## Viva Questions & Answers

1. **How does TF-IDF work?** - Weights terms by frequency in document vs rarity across corpus
2. **What is cosine similarity?** - Measures angle between vectors; 1.0 = identical, 0 = unrelated
3. **Role of sentence-transformers?** - Creates semantic embeddings capturing meaning beyond keywords
4. **How is match score calculated?** - Weighted: Skill(40%) + Semantic(25%) + TF-IDF(20%) + Experience(15%)
5. **What is ATS scoring?** - Evaluates resume format/keywords/readability for automated screening
6. **How to scale?** - Vector DBs, caching, async processing, horizontal scaling

---

## Resume Points

- Built AI job recommendation system using NLP, TF-IDF, and semantic embeddings
- Implemented full-stack with Next.js 14, FastAPI, and ML pipeline
- Designed ATS scoring engine analyzing 4 dimensions
- Created skill gap analyzer with personalized learning recommendations
- Built responsive SaaS dashboard with Recharts analytics

---

## License

MIT - Free for academic and personal use.
