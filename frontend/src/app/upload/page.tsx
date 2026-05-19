"use client";
import React, { useState, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Upload, FileText, CheckCircle, AlertCircle, Brain, Zap, Target, Award, BookOpen, Briefcase } from "lucide-react";
import { uploadResume, getATSScore, generateRecommendations } from "@/lib/api";
import { ATSScore } from "@/types";
import Link from "next/link";

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<any>(null);
  const [atsScore, setAtsScore] = useState<ATSScore | null>(null);
  const [generating, setGenerating] = useState(false);
  const [recsGenerated, setRecsGenerated] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = useCallback((e: React.DragEvent) => { e.preventDefault(); e.stopPropagation(); setDragActive(e.type === "dragenter" || e.type === "dragover"); }, []);
  const handleDrop = useCallback((e: React.DragEvent) => { e.preventDefault(); e.stopPropagation(); setDragActive(false); if (e.dataTransfer.files?.[0]) { setFile(e.dataTransfer.files[0]); setError(null); } }, []);
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => { if (e.target.files?.[0]) { setFile(e.target.files[0]); setError(null); } };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true); setError(null);
    try {
      const result = await uploadResume(file);
      setUploadResult(result);
      const ats = await getATSScore(result.id);
      setAtsScore(ats);
    } catch (err: any) { setError(err.message || "Upload failed."); }
    finally { setUploading(false); }
  };

  const handleGenerate = async () => {
    if (!uploadResult) return;
    setGenerating(true);
    try { await generateRecommendations(uploadResult.id); setRecsGenerated(true); }
    catch (err: any) { setError(err.message); }
    finally { setGenerating(false); }
  };

  const getScoreColor = (s: number) => s >= 80 ? "text-green-600" : s >= 60 ? "text-yellow-600" : "text-red-600";

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div><h1 className="text-3xl font-bold tracking-tight">Upload Resume</h1><p className="text-muted-foreground">Upload your resume to get AI-powered job recommendations and ATS analysis</p></div>

      {!uploadResult && (
        <Card><CardContent className="pt-6">
          <div className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${dragActive ? "border-primary bg-primary/5" : "border-muted-foreground/25 hover:border-primary/50"}`} onDragEnter={handleDrag} onDragLeave={handleDrag} onDragOver={handleDrag} onDrop={handleDrop}>
            <Upload className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
            <h3 className="text-lg font-semibold mb-2">{file ? file.name : "Drop your resume here"}</h3>
            <p className="text-sm text-muted-foreground mb-4">Supports PDF, DOCX, DOC, and TXT (max 10MB)</p>
            <div className="flex items-center justify-center gap-4">
              <label className="cursor-pointer"><input type="file" className="hidden" accept=".pdf,.docx,.doc,.txt" onChange={handleFileChange} /><span className="inline-flex items-center gap-2 rounded-md border px-4 py-2 text-sm font-medium hover:bg-accent transition-colors"><FileText className="h-4 w-4" />Browse Files</span></label>
              {file && <Button onClick={handleUpload} disabled={uploading} className="gap-2">{uploading ? <><div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />Analyzing...</> : <><Brain className="h-4 w-4" />Analyze Resume</>}</Button>}
            </div>
            {file && <div className="mt-4 inline-flex items-center gap-2 rounded-full bg-muted px-3 py-1"><FileText className="h-4 w-4 text-primary" /><span className="text-sm font-medium">{file.name}</span><span className="text-xs text-muted-foreground">({(file.size / 1024).toFixed(1)} KB)</span></div>}
          </div>
          {error && <div className="mt-4 flex items-center gap-2 rounded-lg bg-destructive/10 p-3 text-destructive"><AlertCircle className="h-4 w-4" /><span className="text-sm">{error}</span></div>}
        </CardContent></Card>
      )}

      {uploadResult && (
        <div className="space-y-6">
          <Card className="border-green-200 dark:border-green-800"><CardContent className="pt-6"><div className="flex items-center gap-3"><CheckCircle className="h-8 w-8 text-green-600" /><div><h3 className="text-lg font-semibold text-green-600">Resume Analyzed Successfully!</h3><p className="text-sm text-muted-foreground">{uploadResult.filename} parsed by AI engine</p></div></div></CardContent></Card>

          <div className="grid gap-6 md:grid-cols-2">
            <Card><CardHeader><CardTitle className="text-lg flex items-center gap-2"><Zap className="h-5 w-5 text-primary" />Extracted Skills</CardTitle><CardDescription>{uploadResult.skills?.length || 0} skills identified</CardDescription></CardHeader><CardContent><div className="flex flex-wrap gap-2">{uploadResult.skills?.map((s: string, i: number) => <Badge key={i} variant="secondary">{s}</Badge>)}</div></CardContent></Card>
            <Card><CardHeader><CardTitle className="text-lg flex items-center gap-2"><Briefcase className="h-5 w-5 text-primary" />Profile Summary</CardTitle></CardHeader><CardContent className="space-y-4">
              <div className="flex items-center justify-between"><span className="text-sm text-muted-foreground">Experience</span><Badge variant="outline">{uploadResult.experience_years} years</Badge></div>
              <div className="flex items-center justify-between"><span className="text-sm text-muted-foreground">Education</span><Badge variant="outline">{uploadResult.education?.length || 0} entries</Badge></div>
              <div className="flex items-center justify-between"><span className="text-sm text-muted-foreground">Keywords</span><Badge variant="outline">{uploadResult.keywords?.length || 0} found</Badge></div>
            </CardContent></Card>
          </div>

          {atsScore && (
            <Card><CardHeader><CardTitle className="text-lg flex items-center gap-2"><Award className="h-5 w-5 text-primary" />ATS Compatibility Score</CardTitle><CardDescription>How well your resume performs with ATS</CardDescription></CardHeader><CardContent>
              <div className="grid gap-6 md:grid-cols-5 mb-6">
                <div className="md:col-span-1 flex flex-col items-center justify-center"><div className={`text-4xl font-bold ${getScoreColor(atsScore.overall_score)}`}>{atsScore.overall_score.toFixed(0)}</div><p className="text-xs text-muted-foreground mt-1">Overall</p></div>
                <div className="md:col-span-4 grid grid-cols-2 md:grid-cols-4 gap-4">
                  {[{l:"Format",s:atsScore.format_score},{l:"Keywords",s:atsScore.keyword_score},{l:"Readability",s:atsScore.readability_score},{l:"Completeness",s:atsScore.completeness_score}].map(item => (
                    <div key={item.l} className="text-center"><div className={`text-lg font-semibold ${getScoreColor(item.s)}`}>{item.s.toFixed(0)}%</div><Progress value={item.s} className="h-2 mt-1" /><p className="text-xs text-muted-foreground mt-1">{item.l}</p></div>
                  ))}
                </div>
              </div>
              {atsScore.suggestions?.length > 0 && <div className="border-t pt-4"><h4 className="text-sm font-semibold mb-2">Improvement Suggestions:</h4><ul className="space-y-2">{atsScore.suggestions.map((s, i) => <li key={i} className="flex items-start gap-2 text-sm text-muted-foreground"><AlertCircle className="h-4 w-4 mt-0.5 text-yellow-500 shrink-0" />{s}</li>)}</ul></div>}
            </CardContent></Card>
          )}

          <Card><CardContent className="pt-6"><div className="flex items-center justify-between">
            <div className="flex items-center gap-3"><Target className="h-8 w-8 text-primary" /><div><h3 className="font-semibold">Ready to Find Matching Jobs?</h3><p className="text-sm text-muted-foreground">AI will analyze and rank best job matches</p></div></div>
            {!recsGenerated ? <Button onClick={handleGenerate} disabled={generating} size="lg" className="gap-2">{generating ? <><div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />Matching...</> : <><Brain className="h-4 w-4" />Generate Recommendations</>}</Button> : <Link href={`/recommendations?resume_id=${uploadResult.id}`}><Button size="lg" className="gap-2"><CheckCircle className="h-4 w-4" />View Recommendations</Button></Link>}
          </div></CardContent></Card>
        </div>
      )}
    </div>
  );
}
