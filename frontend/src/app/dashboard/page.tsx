"use client";
import React, { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Briefcase, FileText, Target, TrendingUp, Upload, BarChart3, Brain, Zap } from "lucide-react";
import Link from "next/link";
import { getAnalyticsOverview, listResumes } from "@/lib/api";
import { AnalyticsOverview, ResumeSummary } from "@/types";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";

const COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#06b6d4"];

export default function DashboardPage() {
  const [analytics, setAnalytics] = useState<AnalyticsOverview | null>(null);
  const [resumes, setResumes] = useState<ResumeSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [a, r] = await Promise.all([getAnalyticsOverview(), listResumes()]);
        setAnalytics(a); setResumes(r);
      } catch (e) { console.error(e); }
      finally { setLoading(false); }
    }
    fetchData();
  }, []);

  if (loading) return <div className="flex items-center justify-center h-64"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div></div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div><h1 className="text-3xl font-bold tracking-tight">Dashboard</h1><p className="text-muted-foreground">AI-powered job matching analytics and insights</p></div>
        <Link href="/upload"><Button className="gap-2"><Upload className="h-4 w-4" />Upload Resume</Button></Link>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card><CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2"><CardTitle className="text-sm font-medium">Total Resumes</CardTitle><FileText className="h-4 w-4 text-muted-foreground" /></CardHeader><CardContent><div className="text-2xl font-bold">{analytics?.total_resumes || 0}</div><p className="text-xs text-muted-foreground">Resumes analyzed</p></CardContent></Card>
        <Card><CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2"><CardTitle className="text-sm font-medium">Active Jobs</CardTitle><Briefcase className="h-4 w-4 text-muted-foreground" /></CardHeader><CardContent><div className="text-2xl font-bold">{analytics?.total_jobs || 0}</div><p className="text-xs text-muted-foreground">Available positions</p></CardContent></Card>
        <Card><CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2"><CardTitle className="text-sm font-medium">Recommendations</CardTitle><Target className="h-4 w-4 text-muted-foreground" /></CardHeader><CardContent><div className="text-2xl font-bold">{analytics?.total_recommendations || 0}</div><p className="text-xs text-muted-foreground">Matches generated</p></CardContent></Card>
        <Card><CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2"><CardTitle className="text-sm font-medium">Avg Match Score</CardTitle><TrendingUp className="h-4 w-4 text-muted-foreground" /></CardHeader><CardContent><div className="text-2xl font-bold">{analytics?.avg_match_score?.toFixed(1) || 0}%</div><p className="text-xs text-muted-foreground">Average compatibility</p></CardContent></Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card><CardHeader><CardTitle className="text-lg">Top Skills in Demand</CardTitle><CardDescription>Most requested skills across jobs</CardDescription></CardHeader><CardContent>
          {analytics?.top_skills_in_demand?.length ? (
            <ResponsiveContainer width="100%" height={250}><BarChart data={analytics.top_skills_in_demand}><CartesianGrid strokeDasharray="3 3" className="opacity-30" /><XAxis dataKey="skill" tick={{ fontSize: 11 }} angle={-45} textAnchor="end" height={80} /><YAxis tick={{ fontSize: 11 }} /><Tooltip /><Bar dataKey="count" fill="hsl(221.2, 83.2%, 53.3%)" radius={[4, 4, 0, 0]} /></BarChart></ResponsiveContainer>
          ) : <div className="flex items-center justify-center h-[250px] text-muted-foreground"><div className="text-center"><Brain className="h-12 w-12 mx-auto mb-2 opacity-50" /><p>Upload a resume to see data</p></div></div>}
        </CardContent></Card>
        <Card><CardHeader><CardTitle className="text-lg">Match Score Distribution</CardTitle><CardDescription>How well resumes match jobs</CardDescription></CardHeader><CardContent>
          {analytics?.match_score_distribution?.some(d => d.count > 0) ? (
            <ResponsiveContainer width="100%" height={250}><PieChart><Pie data={analytics.match_score_distribution.filter(d => d.count > 0)} cx="50%" cy="50%" outerRadius={80} dataKey="count" label={({ range, count }) => `${range}: ${count}`}>{analytics.match_score_distribution.filter(d => d.count > 0).map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}</Pie><Tooltip /></PieChart></ResponsiveContainer>
          ) : <div className="flex items-center justify-center h-[250px] text-muted-foreground"><div className="text-center"><BarChart3 className="h-12 w-12 mx-auto mb-2 opacity-50" /><p>No recommendations yet</p></div></div>}
        </CardContent></Card>
      </div>

      <Card><CardHeader><CardTitle className="text-lg">Recent Resumes</CardTitle><CardDescription>Latest uploads and scores</CardDescription></CardHeader><CardContent>
        {resumes.length > 0 ? (
          <div className="space-y-3">{resumes.slice(0, 5).map(r => (
            <div key={r.id} className="flex items-center justify-between rounded-lg border p-4 hover:bg-accent/50 transition-colors">
              <div className="flex items-center gap-3"><div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center"><FileText className="h-5 w-5 text-primary" /></div><div><p className="font-medium">{r.filename}</p><p className="text-sm text-muted-foreground">{r.skills_count} skills | {r.experience_years} yrs</p></div></div>
              <div className="flex items-center gap-3"><Badge variant={r.ats_score >= 70 ? "success" : "warning"}>ATS: {r.ats_score.toFixed(0)}%</Badge><Link href={`/recommendations?resume_id=${r.id}`}><Button variant="outline" size="sm">View Matches</Button></Link></div>
            </div>
          ))}</div>
        ) : (
          <div className="flex flex-col items-center justify-center py-10 text-muted-foreground"><Upload className="h-12 w-12 mb-3 opacity-50" /><p className="text-lg font-medium">No resumes uploaded yet</p><Link href="/upload" className="mt-4"><Button>Upload Resume</Button></Link></div>
        )}
      </CardContent></Card>

      <div className="grid gap-4 md:grid-cols-3">
        <Card className="border-primary/20"><CardContent className="pt-6"><div className="flex items-center gap-3 mb-3"><div className="h-10 w-10 rounded-lg bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center"><Brain className="h-5 w-5 text-blue-600" /></div><h3 className="font-semibold">NLP Resume Parsing</h3></div><p className="text-sm text-muted-foreground">Advanced NLP extracts skills, experience, and education automatically.</p></CardContent></Card>
        <Card className="border-primary/20"><CardContent className="pt-6"><div className="flex items-center gap-3 mb-3"><div className="h-10 w-10 rounded-lg bg-green-100 dark:bg-green-900/30 flex items-center justify-center"><Zap className="h-5 w-5 text-green-600" /></div><h3 className="font-semibold">Semantic Matching</h3></div><p className="text-sm text-muted-foreground">TF-IDF and sentence embeddings find best job matches.</p></CardContent></Card>
        <Card className="border-primary/20"><CardContent className="pt-6"><div className="flex items-center gap-3 mb-3"><div className="h-10 w-10 rounded-lg bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center"><TrendingUp className="h-5 w-5 text-purple-600" /></div><h3 className="font-semibold">Career Analytics</h3></div><p className="text-sm text-muted-foreground">Personalized career suggestions and skill gap analysis.</p></CardContent></Card>
      </div>
    </div>
  );
}
