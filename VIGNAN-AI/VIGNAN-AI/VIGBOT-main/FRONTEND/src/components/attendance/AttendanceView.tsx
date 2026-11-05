"use client";

import React, { useState } from "react";
import {
  UserCheck,
  AlertTriangle,
  CheckCircle2,
  X,
  Calculator,
  Calendar,
  ShieldCheck,
  ArrowRight,
  TrendingUp,
} from "lucide-react";
import { ATTENDANCE_DATA, AttendanceSubject } from "@/data/attendance";
import { calculateConsecutiveClassesNeeded } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { useStudent } from "@/context/StudentContext";
import { useLanguage } from "@/context/LanguageContext";

interface AttendanceViewProps {
  onAskHelpdesk: (query: string) => void;
}

export const AttendanceView: React.FC<AttendanceViewProps> = ({ onAskHelpdesk }) => {
  const { studentData } = useStudent();
  const { t, tDynamic } = useLanguage();
  const student = studentData?.profile;
  const attendanceData = studentData?.attendance || ATTENDANCE_DATA;

  const [selectedSubject, setSelectedSubject] = useState<AttendanceSubject | null>(
    attendanceData.subjects.find((s) => s.status === "Critical" || s.status === "Attention") ||
    attendanceData.subjects[0] || null
  );
  const [simulatedClasses, setSimulatedClasses] = useState<number>(4);

  const calculateSimulatedPct = (sub: AttendanceSubject, additionalAttended: number) => {
    const newAttended = sub.attended + additionalAttended;
    const newTotal = sub.total + additionalAttended;
    return Math.round((newAttended / newTotal) * 100);
  };

  const lowestSub = [...attendanceData.subjects].sort((a, b) => a.percentage - b.percentage)[0];

  return (
    <div className="@container space-y-6">
      {/* Section Header */}
      <div className="flex flex-col @lg:flex-row @lg:items-center justify-between gap-3 border-b border-slate-200/80 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-foreground">{t.attendanceTitle || "Attendance Telemetry"}</h2>
            
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            {t.attendanceSubtitle || "Biometric and lecture-by-lecture records. Statutory minimum threshold: 75%."}
          </p>
        </div>

        <div className="flex items-center gap-2">
          {lowestSub && lowestSub.percentage < 75 && (
            <div className="rounded-xl bg-amber-50 border border-amber-200 px-3 py-1.5 text-xs font-semibold text-amber-800 flex items-center gap-1.5 whitespace-nowrap">
              <AlertTriangle className="h-3.5 w-3.5 text-amber-600 shrink-0" />
              <span>{lowestSub.name} below 75% ({lowestSub.percentage}%)</span>
            </div>
          )}
        </div>
      </div>

      {/* Main Grid: Subjects Table & Detail Drawer */}
      <div className="grid grid-cols-1 @4xl:grid-cols-12 gap-6">
        {/* Left: Subjects Cards/Table (7 Cols) */}
        <div className="@4xl:col-span-7 space-y-3">
          {attendanceData.subjects.map((sub) => {
            const isAttention = sub.status === "Attention";
            const isSelected = selectedSubject?.code === sub.code;

            return (
              <div
                key={sub.code}
                onClick={() => {
                  setSelectedSubject(sub);
                  setSimulatedClasses(sub.classesNeeded75 || calculateConsecutiveClassesNeeded(sub.attended, sub.total, 75) || 1);
                }}
                className={`rounded-lg border p-4 transition-all cursor-pointer ${
                  isSelected
                    ? "border-blue-500 bg-blue-50/30 ring-2 ring-blue-100 shadow-sm"
                    : "border-slate-200 bg-card hover:border-slate-300 hover:shadow-2xs"
                }`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs text-muted-foreground font-semibold">{sub.code}</span>
                      <span className="font-bold text-foreground text-sm">{sub.name}</span>
                    </div>
                    <p className="text-xs text-muted-foreground mt-0.5">{sub.faculty}</p>
                  </div>

                  <div className="text-right">
                    <div className="flex items-baseline justify-end gap-1">
                      <span
                        className={`text-xl font-extrabold ${
                          isAttention ? "text-amber-900" : "text-emerald-700"
                        }`}
                      >
                        {sub.percentage}%
                      </span>
                    </div>
                    <Badge variant={isAttention ? "warning" : "success"}>
                      {isAttention ? (
                        <>
                          <AlertTriangle className="h-2.5 w-2.5" />
                          {tDynamic(sub.status)}
                        </>
                      ) : (
                        <>
                          <CheckCircle2 className="h-2.5 w-2.5" />
                          {tDynamic(sub.status)}
                        </>
                      )}
                    </Badge>
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="mt-3">
                  <div className="flex justify-between text-sm text-muted-foreground mb-1">
                    <span>
                      {t.classesAttended || "Attended"}: <strong>{sub.attended}</strong> / {sub.total}
                    </span>
                    <span>{t.classesMissed}: {sub.total - sub.attended}</span>
                  </div>
                  <div className="relative h-2.5 w-full overflow-hidden rounded-full bg-muted">
                    {/* Minimum 75% guideline line */}
                    <div
                      className="absolute top-0 bottom-0 w-0.5 bg-slate-400 z-10"
                      style={{ left: "75%" }}
                      title={t.mandatoryThreshold || "Mandatory 75% threshold"}
                    />
                    <div
                      className={`h-full transition-all duration-500 ${
                        isAttention
                          ? "bg-gradient-to-r from-amber-400 to-amber-600"
                          : "bg-gradient-to-r from-emerald-400 to-emerald-600"
                      }`}
                      style={{ width: `${sub.percentage}%` }}
                    />
                  </div>
                </div>

                {/* Subtext advice */}
                {isAttention && (
                  <div className="mt-2.5 rounded-lg bg-amber-50 p-2 text-sm text-amber-900 font-medium flex items-center justify-between">
                    <span>{t.attendNext || "Attend next"} <strong>{sub.classesNeeded75 || calculateConsecutiveClassesNeeded(sub.attended, sub.total, 75)} {t.consecutiveClasses || "classes"}</strong> {t.toReach75 || "to reach 75%"}.</span>
                    <span className="text-sm font-bold text-amber-700 underline">{t.simulateAttendance || "Simulate"}</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Right: Subject Detail & Consecutive Classes Simulator (5 Cols) */}
        <div className="@4xl:col-span-5">
          {selectedSubject ? (
            <div className="@4xl:sticky @4xl:top-28 rounded-lg border border-blue-200 bg-card p-5 shadow-sm space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <div>
                  <span className="font-mono text-xs text-blue-600 font-bold">
                    {selectedSubject.code}
                  </span>
                  <h3 className="text-base font-bold text-foreground">
                    {selectedSubject.name}
                  </h3>
                </div>
                <div className="flex items-center gap-1 text-xs text-muted-foreground">
                  <ShieldCheck className="h-4 w-4 text-emerald-600" />
                  <span>{t.verified || "Verified"}</span>
                </div>
              </div>

              {/* Attendance KPI Summary */}
              <div className="grid grid-cols-3 gap-2 text-center text-xs">
                <div className="rounded-xl bg-muted/50 p-2.5 border border-slate-100">
                  <div className="text-sm text-muted-foreground">{t.classesAttended || "Attended"}</div>
                  <div className="text-base font-bold text-foreground">{selectedSubject.attended}</div>
                </div>
                <div className="rounded-xl bg-muted/50 p-2.5 border border-slate-100">
                  <div className="text-sm text-muted-foreground">{t.missed || "Missed"}</div>
                  <div className="text-base font-bold text-rose-600">
                    {selectedSubject.total - selectedSubject.attended}
                  </div>
                </div>
                <div className="rounded-xl bg-muted/50 p-2.5 border border-slate-100">
                  <div className="text-sm text-muted-foreground">{t.currentAttendance || "Current %"}</div>
                  <div
                    className={`text-base font-bold ${
                      selectedSubject.percentage < 75 ? "text-amber-800" : "text-emerald-700"
                    }`}
                  >
                    {selectedSubject.percentage}%
                  </div>
                </div>
              </div>

              {/* Actionable Consecutive Recovery Simulator */}
              <div className="rounded-lg bg-gradient-to-br from-blue-50/80 to-indigo-50/50 p-4 border border-blue-100 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5 text-xs font-bold text-blue-900">
                    <Calculator className="h-4 w-4 text-blue-600" />
                    <span>{t.simulateAttendance || "Attendance Calculator"}</span>
                  </div>
                  <span className="text-xs font-mono font-bold text-blue-700">
                    Target: 75%
                  </span>
                </div>

                <p className="text-xs text-muted-foreground leading-relaxed">
                  {selectedSubject.percentage < 75 ? (
                    <>
                      You currently have <strong>{selectedSubject.percentage}%</strong>. You must attend the next{" "}
                      <strong className="text-blue-900 underline">
                        {selectedSubject.classesNeeded75 || calculateConsecutiveClassesNeeded(selectedSubject.attended, selectedSubject.total, 75)} classes consecutively
                      </strong>{" "}
                      without absence to cross the statutory 75% threshold.
                    </>
                  ) : (
                    <>
                      You are in the safe zone at <strong>{selectedSubject.percentage}%</strong>. You can afford to miss up to{" "}
                      <strong>{Math.max(0, Math.floor((selectedSubject.attended - 0.75 * selectedSubject.total) / 0.75))} classes</strong> before falling below 75%.
                    </>
                  )}
                </p>

                {/* Interactive Slider */}
                <div className="pt-2">
                  <div className="flex justify-between text-xs font-semibold text-foreground mb-1">
                    <span>{t.simulateAttendance}:</span>
                    <span className="text-blue-700 font-bold">+{simulatedClasses} classes</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="15"
                    value={simulatedClasses}
                    onChange={(e) => setSimulatedClasses(parseInt(e.target.value))}
                    className="w-full h-2 bg-blue-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                  />
                  <div className="mt-2 flex items-center justify-between rounded-lg bg-card p-2.5 border border-blue-200 text-xs">
                    <span className="text-muted-foreground">{t.attendanceCalculator}:</span>
                    <span className="text-sm font-extrabold text-blue-900">
                      {calculateSimulatedPct(selectedSubject, simulatedClasses)}%
                    </span>
                  </div>
                </div>
              </div>

              {/* Course Schedule */}
              <div className="text-xs space-y-1.5 text-muted-foreground">
                <div className="font-semibold text-foreground flex items-center gap-1.5">
                  <Calendar className="h-3.5 w-3.5 text-muted-foreground" />
                  <span>Lecture Schedule:</span>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {selectedSubject.scheduleDays.map((slot) => (
                    <span
                      key={slot}
                      className="rounded-md bg-muted px-2 py-0.5 text-sm font-medium text-foreground"
                    >
                      {slot}
                    </span>
                  ))}
                </div>
              </div>

              {/* Direct conversational query trigger */}
              <button
                onClick={() =>
                  onAskHelpdesk(`How many classes do I need to attend to reach 75% in ${selectedSubject.name}?`)
                }
                className="w-full flex items-center justify-center gap-1.5 rounded-xl bg-slate-900 py-2.5 text-xs font-semibold text-white hover:bg-slate-800 transition-colors shadow-2xs cursor-pointer"
              >
                <span>Ask Helpdesk about {selectedSubject.name}</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </button>
            </div>
          ) : (
            <div className="rounded-lg border border-dashed border-slate-300 p-8 text-center text-xs text-muted-foreground">
              Select a subject from the left to inspect detailed metrics and consecutive class calculations.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
