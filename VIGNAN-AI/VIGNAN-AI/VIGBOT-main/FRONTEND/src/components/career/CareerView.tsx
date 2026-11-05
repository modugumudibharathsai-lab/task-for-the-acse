import React, { useEffect, useState } from "react";
import { FileText, Sparkles, Briefcase, Code, Download } from "lucide-react";
import { getResumeData, saveResumeData } from "@/actions/career";
import { useStudent } from "@/context/StudentContext";
import { CURRENT_STUDENT } from "@/data/student";

export const CareerView = () => {
  const { studentData } = useStudent();
  const student = studentData?.profile || CURRENT_STUDENT;
  
  const [skills, setSkills] = useState("");
  const [projects, setProjects] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [showPreview, setShowPreview] = useState(false);

  useEffect(() => {
    const fetchResume = async () => {
      const res = await getResumeData(student.id);
      if (res.success && res.data) {
        const data = res.data as any;
        setSkills(data.skills || "");
        setProjects(data.projects || "");
        if (data.skills || data.projects) setShowPreview(true);
      }
    };
    fetchResume();
  }, [student.id]);

  const handleGenerate = async () => {
    setIsGenerating(true);
    await saveResumeData(student.id, skills, projects);
    
    // Simulate AI generation delay
    setTimeout(() => {
      setIsGenerating(false);
      setShowPreview(true);
    }, 1500);
  };

  return (
    <div className="space-y-6 animate-in fade-in zoom-in-95 duration-300">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">AI Resume Builder</h2>
          <p className="text-sm text-muted-foreground">Input your raw details and let AI format a professional resume.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Form */}
        <div className="space-y-4">
          <div className="rounded-xl border border-border bg-card p-5 shadow-sm space-y-5">
            <div>
              <label className="flex items-center gap-2 text-sm font-semibold text-slate-700 mb-2">
                <Code className="h-4 w-4 text-blue-600" /> Technical Skills
              </label>
              <textarea 
                value={skills}
                onChange={(e) => setSkills(e.target.value)}
                placeholder="E.g., React, TypeScript, Python, SQL, Machine Learning..."
                rows={4}
                className="w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
              />
            </div>
            
            <div>
              <label className="flex items-center gap-2 text-sm font-semibold text-slate-700 mb-2">
                <Briefcase className="h-4 w-4 text-indigo-600" /> Key Projects
              </label>
              <textarea 
                value={projects}
                onChange={(e) => setProjects(e.target.value)}
                placeholder="Describe 1-2 major projects you built..."
                rows={5}
                className="w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
              />
            </div>

            <button 
              onClick={handleGenerate}
              disabled={isGenerating || (!skills && !projects)}
              className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-medium text-sm px-4 py-3 rounded-lg transition-colors shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isGenerating ? (
                <><Sparkles className="h-4 w-4 animate-spin" /> Generating AI Template...</>
              ) : (
                <><Sparkles className="h-4 w-4" /> Generate Professional Resume</>
              )}
            </button>
          </div>
        </div>

        {/* AI Output Preview */}
        <div className="space-y-4 h-full">
          {showPreview ? (
            <div className="rounded-xl border border-border bg-card shadow-sm h-full flex flex-col min-h-[500px]">
              <div className="bg-muted/30 border-b border-border p-3 flex items-center justify-between">
                <h3 className="font-semibold text-sm flex items-center gap-2">
                  <FileText className="h-4 w-4" /> Resume Preview
                </h3>
                <button className="flex items-center gap-1 text-xs font-medium text-blue-600 hover:text-blue-800 bg-blue-50 px-2 py-1 rounded-md">
                  <Download className="h-3 w-3" /> PDF
                </button>
              </div>
              <div className="flex-1 p-6 bg-slate-50/50 overflow-y-auto">
                <div className="max-w-lg mx-auto bg-white border border-slate-200 shadow-xs p-8 rounded-sm space-y-6 min-h-[600px]">
                  {/* Mock AI formatting */}
                  <div className="text-center border-b pb-4">
                    <h1 className="text-2xl font-bold uppercase tracking-widest text-slate-800">{student.name}</h1>
                    <p className="text-sm text-slate-500 mt-1">{student.id} | B.Tech Computer Science | {student.email}</p>
                  </div>
                  
                  <div>
                    <h2 className="text-sm font-bold uppercase tracking-wider text-indigo-700 mb-2 border-b pb-1 border-indigo-100">Skills & Competencies</h2>
                    <div className="flex flex-wrap gap-2">
                      {skills.split(',').map((s, i) => s.trim() && (
                        <span key={i} className="bg-slate-100 px-2 py-1 rounded text-xs text-slate-700 font-medium">{s.trim()}</span>
                      ))}
                    </div>
                  </div>

                  <div>
                    <h2 className="text-sm font-bold uppercase tracking-wider text-indigo-700 mb-2 border-b pb-1 border-indigo-100">Professional Projects</h2>
                    <p className="text-xs text-slate-600 leading-relaxed whitespace-pre-wrap">{projects}</p>
                  </div>
                  
                  <div className="mt-8 pt-4 border-t border-dashed border-slate-200 text-center opacity-50">
                    <Sparkles className="h-4 w-4 mx-auto text-indigo-400 mb-1" />
                    <p className="text-[10px]">Formatted by VIGNAN-AI Career Hub</p>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="rounded-xl border border-dashed border-border bg-muted/30 h-full min-h-[500px] flex flex-col items-center justify-center p-8 text-center">
              <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-3 opacity-30" />
              <p className="font-medium text-slate-600">No Resume Generated Yet</p>
              <p className="text-sm text-muted-foreground mt-1 max-w-xs">Fill in your skills and projects on the left, and our AI will format a beautiful resume for you.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
