"use client";
import React, { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { BarChart3, TrendingUp, Target, Brain, Award } from "lucide-react";
import { getAnalyticsOverview, listResumes, getResumeAnalytics } from "@/lib/api";
import { AnalyticsOverview, ResumeSummary, ResumeAnalytics } from "@/types";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from "recharts";

const COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#06b6d4"];

export default function AnalyticsPage() {
  const [overview, setOverview] = useState<AnalyticsOverview | null>(null);
  const [resumes, setResumes] = useState<ResumeSummary[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [resumeData, setResumeData] = useState<ResumeAnalytics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { Promise.all([getAnalyticsOverview(), listResumes()]).then(([o, r]) => { setOverview(o); setResumes(r); if (r.length) setSelectedId(r[0].id); }).catch(console.error).finally(() => setLoading(false)); }, []);
  useEffect(() => { if (selectedId) getResumeAnalytics(selectedId).then(setResumeData).catch(console.error); }, [selectedId]);

  if (loading) return <div className="flex items-center justify-center h-64"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div></div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div><h1 className="text-3xl font-bold tracking-tight">Analytics</h1><p className="text-muted-foreground">Insights into job matching performance</p></div>
        {resumes.length > 0 && <select className="rounded-md border bg-background px-3 py-2 text-sm" value={selectedId || ""} onChange={e => setSelectedId(parseInt(e.target.value))}>{resumes.map(r => <option key={r.id} value={r.id}>{r.filename}</option>)}</select>}
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card><CardContent className="pt-6"><div className="flex items-center gap-3"><div className="h-10 w-10 rounded-lg bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center"><BarChart3 className="h-5 w-5 text-blue-600" /></div><div><p className="text-2xl font-bold">{overview?.total_recommendations || 0}</p><p className="text-xs text-muted-foreground">Total Matches</p></div></div></CardContent></Card>
        <Card><CardContent className="pt-6"><div className="flex items-center gap-3"><div className="h-10 w-10 rounded-lg bg-green-100 dark:bg-green-900/30 flex items-center justify-center"><TrendingUp className="h-5 w-5 text-green-600" /></div><div><p className="text-2xl font-bold">{overview?.avg_match_score?.toFixed(1) || 0}%</p><p className="text-xs text-muted-foreground">Avg Score</p></div></div></CardContent></Card>
        <Card><CardContent className="pt-6"><div className="flex items-center gap-3"><div className="h-10 w-10 rounded-lg bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center"><Brain className="h-5 w-5 text-purple-600" /></div><div><p className="text-2xl font-bold">{resumeData?.skills_count || 0}</p><p className="text-xs text-muted-foreground">Your Skills</p></div></div></CardContent></Card>
        <Card><CardContent className="pt-6"><div className="flex items-center gap-3"><div className="h-10 w-10 rounded-lg bg-yellow-100 dark:bg-yellow-900/30 flex items-center justify-center"><Award className="h-5 w-5 text-yellow-600" /></div><div><p className="text-2xl font-bold">{resumeData?.ats_score?.toFixed(0) || 0}%</p><p className="text-xs text-muted-foreground">ATS Score</p></div></div></CardContent></Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card><CardHeader><CardTitle className="text-lg">Skills in Demand</CardTitle></CardHeader><CardContent>
          {overview?.top_skills_in_demand?.length ? <ResponsiveContainer width="100%" height={300}><BarChart data={overview.top_skills_in_demand} layout="vertical"><CartesianGrid strokeDasharray="3 3" className="opacity-30" /><XAxis type="number" tick={{fontSize:11}} /><YAxis dataKey="skill" type="category" tick={{fontSize:11}} width={100} /><Tooltip /><Bar dataKey="count" fill="hsl(221.2,83.2%,53.3%)" radius={[0,4,4,0]} /></BarChart></ResponsiveContainer> : <div className="flex items-center justify-center h-[300px] text-muted-foreground">No data</div>}
        </CardContent></Card>
        <Card><CardHeader><CardTitle className="text-lg">Skill Gaps</CardTitle></CardHeader><CardContent>
          {overview?.skill_gap_summary?.length ? <ResponsiveContainer width="100%" height={300}><BarChart data={overview.skill_gap_summary} layout="vertical"><CartesianGrid strokeDasharray="3 3" className="opacity-30" /><XAxis type="number" tick={{fontSize:11}} /><YAxis dataKey="skill" type="category" tick={{fontSize:11}} width={100} /><Tooltip /><Bar dataKey="count" fill="#ef4444" radius={[0,4,4,0]} /></BarChart></ResponsiveContainer> : <div className="flex items-center justify-center h-[300px] text-muted-foreground">No gap data yet</div>}
        </CardContent></Card>
        <Card><CardHeader><CardTitle className="text-lg">Score Distribution</CardTitle></CardHeader><CardContent>
          {overview?.match_score_distribution?.some(d=>d.count>0) ? <ResponsiveContainer width="100%" height={300}><PieChart><Pie data={overview.match_score_distribution.filter(d=>d.count>0)} cx="50%" cy="50%" outerRadius={100} dataKey="count" label={({range,count})=>`${range}:${count}`}>{overview.match_score_distribution.filter(d=>d.count>0).map((_,i)=><Cell key={i} fill={COLORS[i%COLORS.length]} />)}</Pie><Tooltip /><Legend /></PieChart></ResponsiveContainer> : <div className="flex items-center justify-center h-[300px] text-muted-foreground">Generate recommendations first</div>}
        </CardContent></Card>
        <Card><CardHeader><CardTitle className="text-lg">Your Performance</CardTitle></CardHeader><CardContent>
          {resumeData && resumeData.total_recommendations > 0 ? (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4"><div className="text-center rounded-lg border p-4"><p className="text-2xl font-bold text-primary">{resumeData.top_match_score.toFixed(0)}%</p><p className="text-xs text-muted-foreground">Best Match</p></div><div className="text-center rounded-lg border p-4"><p className="text-2xl font-bold text-green-600">{resumeData.avg_match_score.toFixed(0)}%</p><p className="text-xs text-muted-foreground">Average</p></div></div>
              <div><p className="text-sm font-medium mb-2">Skills Matched:</p><div className="flex flex-wrap gap-1.5">{resumeData.skills_matched_across_jobs?.slice(0,10).map(s => <Badge key={s} variant="success" className="text-xs">{s}</Badge>)}</div></div>
              <div><p className="text-sm font-medium mb-2">Commonly Missing:</p><div className="flex flex-wrap gap-1.5">{resumeData.skills_commonly_missing?.slice(0,8).map(s => <Badge key={s} variant="destructive" className="text-xs">{s}</Badge>)}</div></div>
            </div>
          ) : <div className="flex items-center justify-center h-[250px] text-muted-foreground"><div className="text-center"><Target className="h-8 w-8 mx-auto mb-2 opacity-50" /><p className="text-sm">Upload resume and generate recommendations first</p></div></div>}
        </CardContent></Card>
      </div>
    </div>
  );
}
