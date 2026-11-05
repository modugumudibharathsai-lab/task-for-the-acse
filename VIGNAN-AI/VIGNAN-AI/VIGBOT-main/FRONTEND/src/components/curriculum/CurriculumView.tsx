"use client";

import React, { useState } from "react";
import {
  BookOpen,
  CheckCircle2,
  Circle,
  GraduationCap,
  Sparkles,
  ArrowRight,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { CURRICULUM_DATA, CourseCategory } from "@/data/curriculum";
import { useLanguage } from "@/context/LanguageContext";

interface CurriculumViewProps {
  onAskHelpdesk: (query: string) => void;
}

export const CurriculumView: React.FC<CurriculumViewProps> = ({ onAskHelpdesk }) => {
  const { t, tDynamic } = useLanguage();
  const [expandedCat, setExpandedCat] = useState<string>("Core Engineering");

  const toggleExpand = (name: string) => {
    setExpandedCat(expandedCat === name ? "" : name);
  };

  const progressPct = Math.round(
    (CURRICULUM_DATA.completedCredits / CURRICULUM_DATA.totalDegreeCredits) * 100
  );

  return (
    <div className="@container space-y-6">
      {/* Header */}
      <div className="flex flex-col @lg:flex-row @lg:items-center justify-between gap-3 border-b border-slate-200/80 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-foreground">{t.curriculumTitle || "Course Curriculum & Syllabus"}</h2>
            
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            Program: {CURRICULUM_DATA.programme} • 120 {t.totalCredits || "Total Credits"}
          </p>
        </div>

        <button
          onClick={() => onAskHelpdesk("How many credits do I still need to graduate?")}
          className="flex items-center gap-1.5 rounded-xl bg-cyan-700 px-3.5 py-2 text-xs font-semibold text-white shadow-xs hover:bg-cyan-800 transition-colors cursor-pointer"
        >
          <Sparkles className="h-4 w-4" />
          <span>{t.askButton}: {t.curriculumTitle}</span>
        </button>
      </div>

      {/* Progress Overview Card */}
      <div className="rounded-xl border border-cyan-200 bg-gradient-to-r from-cyan-50/70 via-blue-50/40 to-white p-6 shadow-2xs space-y-4">
        <div className="flex flex-col @lg:flex-row @lg:items-center justify-between gap-4">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-cyan-900">
              Degree Audit Completion
            </span>
            <div className="flex items-baseline gap-2 mt-1">
              <span className="text-3xl font-black text-foreground">
                {CURRICULUM_DATA.completedCredits}
              </span>
              <span className="text-sm font-semibold text-muted-foreground">
                / {CURRICULUM_DATA.totalDegreeCredits} Total Credits
              </span>
              <span className="rounded-full bg-cyan-100 px-2.5 py-0.5 text-xs font-bold text-cyan-800 ml-2">
                {progressPct}% Completed
              </span>
            </div>
          </div>

          <div className="flex gap-4 text-xs font-medium">
            <div className="rounded-xl bg-card p-3 border border-cyan-100 shadow-2xs">
              <div className="text-muted-foreground text-sm">{t.currentSem || "Current Sem"} 5</div>
              <div className="text-base font-bold text-cyan-900">
                {CURRICULUM_DATA.currentSemesterCredits} Credits
              </div>
            </div>
            <div className="rounded-xl bg-card p-3 border border-cyan-100 shadow-2xs">
              <div className="text-muted-foreground text-sm">{t.curriculumProgressSub}</div>
              <div className="text-base font-bold text-indigo-900">
                {CURRICULUM_DATA.remainingCredits} Credits
              </div>
            </div>
          </div>
        </div>

        {/* Global Progress Bar */}
        <div className="h-3 w-full overflow-hidden rounded-full bg-slate-200">
          <div
            className="h-full bg-gradient-to-r from-cyan-500 via-blue-600 to-indigo-600 transition-all duration-700"
            style={{ width: `${progressPct}%` }}
          />
        </div>
      </div>

      {/* Course Categories Accordion / Cards */}
      <div className="space-y-3">
        {CURRICULUM_DATA.categories.map((cat) => {
          const isExpanded = expandedCat === cat.name;
          const catPct = Math.round((cat.completedCredits / cat.totalRequiredCredits) * 100);

          return (
            <div
              key={cat.name}
              className="rounded-lg border border-slate-200 bg-card overflow-hidden shadow-2xs transition-all"
            >
              <div
                onClick={() => toggleExpand(cat.name)}
                className="p-4 flex items-center justify-between cursor-pointer hover:bg-muted/50/70 transition-colors"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <h4 className="font-bold text-foreground text-sm">{cat.name}</h4>
                    <span className="rounded-md bg-muted px-2 py-0.5 text-sm font-bold text-muted-foreground">
                      {cat.completedCredits} / {cat.totalRequiredCredits} Credits ({catPct}%)
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground">{cat.description}</p>
                </div>

                <div className="flex items-center gap-3">
                  <div className="w-24 hidden sm:block">
                    <div className="h-2 w-full rounded-full bg-muted overflow-hidden">
                      <div className="h-full bg-cyan-600" style={{ width: `${catPct}%` }} />
                    </div>
                  </div>
                  {isExpanded ? (
                    <ChevronUp className="h-4 w-4 text-slate-400" />
                  ) : (
                    <ChevronDown className="h-4 w-4 text-slate-400" />
                  )}
                </div>
              </div>

              {isExpanded && (
                <div className="border-t border-slate-100 p-4 bg-muted/50/40 grid grid-cols-1 @lg:grid-cols-2 gap-4 text-xs">
                  {/* Completed Courses */}
                  <div>
                    <div className="flex items-center gap-1.5 font-bold text-emerald-800 mb-2">
                      <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" />
                      <span>{t.creditsCompleted}:</span>
                    </div>
                    {cat.coursesDone.length > 0 ? (
                      <ul className="space-y-1 pl-1">
                        {cat.coursesDone.map((c, i) => (
                          <li key={i} className="text-foreground flex items-center gap-1.5">
                            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
                            <span>{c}</span>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-slate-400 italic">No courses completed in this category yet.</p>
                    )}
                  </div>

                  {/* Pending Courses */}
                  <div>
                    <div className="flex items-center gap-1.5 font-bold text-indigo-900 mb-2">
                      <Circle className="h-3.5 w-3.5 text-indigo-600" />
                      <span>Required to Graduate:</span>
                    </div>
                    {cat.pendingCourses.length > 0 ? (
                      <ul className="space-y-1 pl-1">
                        {cat.pendingCourses.map((c, i) => (
                          <li key={i} className="text-foreground flex items-center gap-1.5">
                            <span className="h-1.5 w-1.5 rounded-full bg-indigo-400" />
                            <span>{c}</span>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="flex items-center gap-1.5 text-emerald-700 font-semibold">
                        <CheckCircle2 className="h-3.5 w-3.5" />
                        Category requirement fully satisfied!
                      </p>
                    )}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
