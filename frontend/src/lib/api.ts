const API_BASE = "/api";

async function fetchAPI(endpoint: string, options?: RequestInit) {
  const res = await fetch(`${API_BASE}${endpoint}`, options);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(err.detail || `API Error: ${res.status}`);
  }
  return res.json();
}

export async function uploadResume(file: File) {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE}/resume/upload`, { method: "POST", body: formData });
  if (!res.ok) { const err = await res.json().catch(() => ({ detail: "Upload failed" })); throw new Error(err.detail); }
  return res.json();
}

export async function getResume(id: number) { return fetchAPI(`/resume/${id}`); }
export async function listResumes() { return fetchAPI("/resumes"); }
export async function getATSScore(id: number) { return fetchAPI(`/resume/${id}/ats-score`); }
export async function listJobs(category?: string) { return fetchAPI(`/jobs${category ? `?category=${category}` : ""}`); }
export async function generateRecommendations(id: number, topK = 10) { return fetchAPI(`/recommendations/${id}?top_k=${topK}`, { method: "POST" }); }
export async function getRecommendations(id: number) { return fetchAPI(`/recommendations/${id}`); }
export async function getSkillGap(id: number) { return fetchAPI(`/skill-gap/${id}`); }
export async function getAnalyticsOverview() { return fetchAPI("/analytics/overview"); }
export async function getResumeAnalytics(id: number) { return fetchAPI(`/analytics/resume/${id}`); }
export async function getCareerSuggestions(id: number) { return fetchAPI(`/career-suggestions/${id}`); }
