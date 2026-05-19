"use client";
import React, { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Target, MapPin, Building2, Clock, DollarSign, Wifi, TrendingUp, BookOpen, Award, AlertCircle, CheckCircle, ChevronDown, ChevronUp, Brain } from "lucide-react";
import { getRecommendations, generateRecommendations, listResumes, getSkillGap, getCareerSuggestions } from "@/lib/api";
import { Recommendation, ResumeSummary, SkillGapAnalysis, CareerSuggestions } from "@/types";

export default function RecommendationsPage() {
  const searchParams = useSearchParams();
  const resumeIdParam = searchParams.get("resume_id");
  const [resumes, setResumes] = useState<ResumeSummary[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(resumeIdParam ? parseInt(resumeIdParam) : null);
  const [recs, setRecs] = useState<Recommendation[]>([]);
  const [skillGap, setSkillGap] = useState<SkillGapAnalysis | null>(null);
  const [career, setCareer] = useState<CareerSuggestions | null>(null);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<number | null>(null);

  useEffect(() => { listResumes().then(d => { setResumes(d); if (!selectedId && d.length) setSelectedId(d[0].id); }).catch(console.error); }, []);
  useEffect(() => {
    if (!selectedId) { setLoading(false); return; }
    setLoading(true);
    (async () => {
      try {
        let data = await getRecommendations(selectedId);
        if (!data.length) data = await generateRecommendations(selectedId);
        setRecs(data);
        const [sg, cs] = await Promise.all([getSkillGap(selectedId).catch(() => null), getCareerSuggestions(selectedId).catch(() => null)]);
        setSkillGap(sg); setCareer(cs);
      } catch (e) { console.error(e); }
      finally { setLoading(false); }
    })();
  }, [selectedId]);

  const scoreBadge = (s: number) => s >= 80 ? "success" : s >= 60 ? "default" : s >= 40 ? "warning" : "destructive";
  if (loading) return <div className="flex items-center justify-center h-64"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div></div>;
  if (!selectedId) return <div className="text-center py-20 text-muted-foreground"><Target className="h-16 w-16 mx-auto mb-4 opacity-50" /><h2 className="text-xl font-semibold">No Resume Found</h2><p>Upload a resume first.</p><a href="/upload" className="mt-4 inline-block"><Button>Upload Resume</Button></a></div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div><h1 className="text-3xl font-bold tracking-tight">Job Recommendations</h1><p className="text-muted-foreground">AI-matched jobs ranked by compatibility</p></div>
        {resumes.length > 1 && <select className="rounded-md border bg-background px-3 py-2 text-sm" value={selectedId || ""} onChange={e => setSelectedId(parseInt(e.target.value))}>{resumes.map(r => <option key={r.id} value={r.id}>{r.filename}</option>)}</select>}
      </div>

      <Tabs defaultValue="recommendations" className="space-y-4">
        <TabsList><TabsTrigger value="recommendations">Recommendations ({recs.length})</TabsTrigger><TabsTrigger value="skillgap">Skill Gap</TabsTrigger><TabsTrigger value="career">Career Suggestions</TabsTrigger></TabsList>

        <TabsContent value="recommendations" className="space-y-4">
          {recs.map((rec, i) => (
            <Card key={rec.id} className="overflow-hidden"><CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="flex items-center justify-center h-8 w-8 rounded-full bg-primary/10 text-primary text-sm font-bold">#{i+1}</span>
                    <h3 className="text-lg font-semibold">{rec.job?.title}</h3>
                    <Badge variant={scoreBadge(rec.match_score) as any}>{rec.match_score.toFixed(1)}% Match</Badge>
                  </div>
                  <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground mb-3">
                    <span className="flex items-center gap-1"><Building2 className="h-4 w-4" />{rec.job?.company}</span>
                    {rec.job?.location && <span className="flex items-center gap-1"><MapPin className="h-4 w-4" />{rec.job.location}</span>}
                    {rec.job?.job_type && <span className="flex items-center gap-1"><Clock className="h-4 w-4" />{rec.job.job_type}</span>}
                    {rec.job?.remote && <span className="flex items-center gap-1"><Wifi className="h-4 w-4 text-green-600" />Remote</span>}
                    {rec.job?.salary_min && <span className="flex items-center gap-1"><DollarSign className="h-4 w-4" />${(rec.job.salary_min/1000).toFixed(0)}k-${(rec.job.salary_max!/1000).toFixed(0)}k</span>}
                  </div>
                  <div className="grid grid-cols-3 gap-4 mb-3">
                    <div><div className="text-xs text-muted-foreground">Skill Match</div><div className="flex items-center gap-2"><Progress value={rec.skill_match_score} className="h-2 flex-1" /><span className="text-xs font-medium">{rec.skill_match_score.toFixed(0)}%</span></div></div>
                    <div><div className="text-xs text-muted-foreground">Experience</div><div className="flex items-center gap-2"><Progress value={rec.experience_match_score} className="h-2 flex-1" /><span className="text-xs font-medium">{rec.experience_match_score.toFixed(0)}%</span></div></div>
                    <div><div className="text-xs text-muted-foreground">Semantic</div><div className="flex items-center gap-2"><Progress value={rec.semantic_similarity_score} className="h-2 flex-1" /><span className="text-xs font-medium">{rec.semantic_similarity_score.toFixed(0)}%</span></div></div>
                  </div>
                  <div className="flex flex-wrap gap-1.5">{rec.matched_skills?.slice(0,6).map(s => <Badge key={s} variant="success" className="text-xs"><CheckCircle className="h-3 w-3 mr-1" />{s}</Badge>)}{rec.missing_skills?.slice(0,4).map(s => <Badge key={s} variant="destructive" className="text-xs"><AlertCircle className="h-3 w-3 mr-1" />{s}</Badge>)}</div>
                </div>
                <Button variant="ghost" size="icon" onClick={() => setExpandedId(expandedId === rec.id ? null : rec.id)}>{expandedId === rec.id ? <ChevronUp className="h-5 w-5" /> : <ChevronDown className="h-5 w-5" />}</Button>
              </div>
              {expandedId === rec.id && (
                <div className="mt-4 pt-4 border-t space-y-4">
                  {rec.recruiter_summary && <div className="rounded-lg bg-muted p-4"><h4 className="text-sm font-semibold mb-2 flex items-center gap-2"><Brain className="h-4 w-4 text-primary" />Recruiter Summary</h4><pre className="text-sm text-muted-foreground whitespace-pre-wrap font-sans">{rec.recruiter_summary}</pre></div>}
                  {rec.career_suggestions && <div className="rounded-lg bg-blue-50 dark:bg-blue-900/20 p-4"><h4 className="text-sm font-semibold mb-2 flex items-center gap-2"><TrendingUp className="h-4 w-4 text-blue-600" />Career Advice</h4><p className="text-sm text-muted-foreground">{rec.career_suggestions}</p></div>}
                  {rec.skill_gaps?.length > 0 && <div><h4 className="text-sm font-semibold mb-2 flex items-center gap-2"><BookOpen className="h-4 w-4 text-primary" />Skill Development</h4><div className="grid gap-2 md:grid-cols-2">{rec.skill_gaps.map((g,j) => <div key={j} className="rounded border p-3"><div className="flex items-center justify-between mb-1"><span className="text-sm font-medium">{g.skill}</span><Badge variant="outline" className="text-xs">{g.priority}</Badge></div><p className="text-xs text-muted-foreground">{g.recommended_course?.platform} - {g.recommended_course?.course} ({g.recommended_course?.duration})</p></div>)}</div></div>}
                  {rec.suggested_certifications?.length > 0 && <div><h4 className="text-sm font-semibold mb-2 flex items-center gap-2"><Award className="h-4 w-4 text-primary" />Certifications</h4><div className="flex flex-wrap gap-2">{rec.suggested_certifications.map((c,j) => <Badge key={j} variant="secondary">{c}</Badge>)}</div></div>}
                </div>
              )}
            </CardContent></Card>
          ))}
          {recs.length === 0 && <Card><CardContent className="py-10 text-center text-muted-foreground"><Target className="h-12 w-12 mx-auto mb-3 opacity-50" /><p>No recommendations yet</p></CardContent></Card>}
        </TabsContent>

        <TabsContent value="skillgap" className="space-y-4">
          {skillGap ? (
            <div className="grid gap-6 md:grid-cols-2">
              <Card><CardHeader><CardTitle className="text-lg">Your Skills</CardTitle></CardHeader><CardContent><div className="flex flex-wrap gap-2">{skillGap.current_skills.map(s => <Badge key={s} variant="success">{s}</Badge>)}</div></CardContent></Card>
              <Card><CardHeader><CardTitle className="text-lg">Missing Skills</CardTitle></CardHeader><CardContent><div className="flex flex-wrap gap-2">{skillGap.missing_skills.map(s => <Badge key={s} variant="destructive">{s}</Badge>)}</div></CardContent></Card>
              <Card className="md:col-span-2"><CardHeader><CardTitle className="text-lg">Skill Match Rate</CardTitle></CardHeader><CardContent><div className="flex items-center gap-4"><Progress value={skillGap.skill_match_percentage} className="flex-1 h-4" /><span className="text-2xl font-bold text-primary">{skillGap.skill_match_percentage.toFixed(1)}%</span></div></CardContent></Card>
              {skillGap.suggested_certifications.length > 0 && <Card className="md:col-span-2"><CardHeader><CardTitle className="text-lg flex items-center gap-2"><Award className="h-5 w-5" />Certifications</CardTitle></CardHeader><CardContent><div className="grid gap-3 md:grid-cols-2">{skillGap.suggested_certifications.map((c,i) => <div key={i} className="flex items-center gap-2 rounded-lg border p-3"><Award className="h-5 w-5 text-yellow-600" /><span className="text-sm font-medium">{c}</span></div>)}</div></CardContent></Card>}
            </div>
          ) : <Card><CardContent className="py-10 text-center text-muted-foreground"><p>Skill gap analysis requires recommendations first.</p></CardContent></Card>}
        </TabsContent>

        <TabsContent value="career" className="space-y-4">
          {career ? (
            <div className="grid gap-6 md:grid-cols-2">
              <Card><CardHeader><CardTitle className="text-lg">Current Role Fit</CardTitle></CardHeader><CardContent><div className="text-center py-4"><h3 className="text-2xl font-bold text-primary">{career.current_role_fit}</h3><p className="text-muted-foreground mt-1">Fit: {career.role_fit_score.toFixed(0)}%</p><Badge className="mt-2">{career.growth_stage}</Badge></div></CardContent></Card>
              <Card><CardHeader><CardTitle className="text-lg">Suggested Roles</CardTitle></CardHeader><CardContent><div className="space-y-3">{career.suggested_roles.map((r,i) => <div key={i} className="flex items-center justify-between"><span className="text-sm font-medium">{r.role}</span><div className="flex items-center gap-2 w-1/2"><Progress value={r.fit_percentage} className="h-2 flex-1" /><span className="text-xs w-10 text-right">{r.fit_percentage.toFixed(0)}%</span></div></div>)}</div></CardContent></Card>
              <Card><CardHeader><CardTitle className="text-lg">Growth Path</CardTitle></CardHeader><CardContent><div className="space-y-4">{career.growth_paths.map((p,i) => <div key={i} className="flex items-center gap-3"><div className={`h-3 w-3 rounded-full ${i===0?"bg-primary":"bg-muted-foreground/30"}`} /><div><p className="text-sm font-medium">{p.stage}</p><p className="text-xs text-muted-foreground">{p.timeline}</p></div></div>)}</div></CardContent></Card>
              <Card><CardHeader><CardTitle className="text-lg">Industry Trends</CardTitle></CardHeader><CardContent><ul className="space-y-2">{career.industry_trends.map((t,i) => <li key={i} className="flex items-start gap-2 text-sm text-muted-foreground"><TrendingUp className="h-4 w-4 mt-0.5 text-green-600 shrink-0" />{t}</li>)}</ul></CardContent></Card>
              <Card className="md:col-span-2"><CardHeader><CardTitle className="text-lg">Salary Insights</CardTitle></CardHeader><CardContent><div className="grid grid-cols-2 md:grid-cols-4 gap-4">{Object.entries(career.salary_insights).map(([k,v]) => <div key={k} className="text-center rounded-lg border p-4"><p className="text-xs text-muted-foreground capitalize">{k.replace("_"," ")}</p><p className="text-sm font-semibold mt-1">{v}</p></div>)}</div></CardContent></Card>
            </div>
          ) : <Card><CardContent className="py-10 text-center text-muted-foreground"><p>Upload a resume to see career suggestions.</p></CardContent></Card>}
        </TabsContent>
      </Tabs>
    </div>
  );
}
