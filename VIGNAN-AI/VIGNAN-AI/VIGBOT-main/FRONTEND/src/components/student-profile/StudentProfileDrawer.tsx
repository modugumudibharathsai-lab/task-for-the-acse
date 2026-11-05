"use client";

import React from "react";
import {
  User,
  ShieldCheck,
  X,
  Mail,
  Phone,
  BookOpen,
  Calendar,
  Building,
  GraduationCap,
  Award,
  LogOut,
} from "lucide-react";
import { CURRENT_STUDENT } from "@/data/student";
import { useStudent } from "@/context/StudentContext";
import { useLanguage } from "@/context/LanguageContext";

interface StudentProfileDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  onAskHelpdesk: (query: string) => void;
  onLogout?: () => void;
}

export const StudentProfileDrawer: React.FC<StudentProfileDrawerProps> = ({
  isOpen,
  onClose,
  onAskHelpdesk,
  onLogout,
}) => {
  const { studentData } = useStudent();
  const { t } = useLanguage();
  const student = studentData?.profile || CURRENT_STUDENT;
  const initials = studentData?.profile?.initials || (student.name ? student.name.split(" ").map((n) => n[0]).join("").slice(0, 2).toUpperCase() : "AR");

  if (!isOpen) return null;

  return (
    <div role="dialog" aria-modal="true" className="fixed inset-0 z-50 flex justify-end bg-slate-900/40 backdrop-blur-xs">
      <div className="relative w-full max-w-md h-full bg-card shadow-2xl border-l border-slate-200 flex flex-col animate-in slide-in-from-right duration-300">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-200 p-5 bg-gradient-to-r from-blue-50 to-white">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-gradient-to-tr from-blue-600 to-indigo-600 font-extrabold text-base text-white shadow-md shadow-blue-500/20">
              {initials}
            </div>
            <div>
              <h3 className="text-base font-bold text-foreground">{student.name}</h3>
              <p className="text-xs font-mono text-blue-600">{student.id}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="rounded-full p-1.5 text-slate-400 hover:bg-muted hover:text-foreground transition-colors cursor-pointer"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Body Content */}
        <div className="flex-1 overflow-y-auto overscroll-contain p-6 space-y-6 text-xs text-foreground">
          {/* Security Guarantee Box */}
          <div className="rounded-lg border border-emerald-200 bg-emerald-50/70 p-4 space-y-1.5 text-emerald-950">
            <div className="flex items-center gap-1.5 font-bold">
              <ShieldCheck className="h-4 w-4 text-emerald-600" />
              <span>{student.authStatus} Student</span>
            </div>
            <p className="text-sm text-emerald-900 leading-relaxed">
              {student.securityLabel}. Your personal academic information is protected by Row-Level Security guardrails. Sourced from {student.sourceAgent}.
            </p>
            <div className="font-mono text-sm text-emerald-800 pt-1">
              Auth Token: <span className="font-mono text-emerald-600 font-semibold px-1 py-0.5 rounded bg-emerald-50 border border-emerald-200">Verified</span>
            </div>
          </div>

          {/* Academic Details List */}
          <div className="rounded-lg border border-slate-200 bg-muted/50/60 p-4 space-y-3">
            <h4 className="font-bold text-foreground uppercase tracking-wider text-sm">
              Institutional Enrollment
            </h4>
            <div className="space-y-2">
              <div className="flex items-center justify-between border-b border-slate-200/60 pb-1.5">
                <span className="text-muted-foreground flex items-center gap-1.5">
                  <GraduationCap className="h-3.5 w-3.5 text-slate-400" />
                  <span>{t.programLabel}:</span>
                </span>
                <span className="font-bold text-foreground">{student.programme}</span>
              </div>

              <div className="flex items-center justify-between border-b border-slate-200/60 pb-1.5">
                <span className="text-muted-foreground flex items-center gap-1.5">
                  <Building className="h-3.5 w-3.5 text-slate-400" />
                  <span>Department:</span>
                </span>
                <span className="font-bold text-foreground">{student.department}</span>
              </div>

              <div className="flex items-center justify-between border-b border-slate-200/60 pb-1.5">
                <span className="text-muted-foreground flex items-center gap-1.5">
                  <Calendar className="h-3.5 w-3.5 text-slate-400" />
                  <span>Academic Year:</span>
                </span>
                <span className="font-bold text-foreground">{student.academicYear}</span>
              </div>

              <div className="flex items-center justify-between border-b border-slate-200/60 pb-1.5">
                <span className="text-muted-foreground flex items-center gap-1.5">
                  <BookOpen className="h-3.5 w-3.5 text-slate-400" />
                  <span>{t.semesterLabel}:</span>
                </span>
                <span className="font-bold text-blue-700">Semester {student.semester}</span>
              </div>

              <div className="flex items-center justify-between border-b border-slate-200/60 pb-1.5">
                <span className="text-muted-foreground flex items-center gap-1.5">
                  <Award className="h-3.5 w-3.5 text-slate-400" />
                  <span>{t.cgpaLabel}:</span>
                </span>
                <span className="font-bold text-emerald-700">{student.cgpa} / 10.0</span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Admission Year:</span>
                <span className="font-bold text-foreground">{student.admissionYear}</span>
              </div>
            </div>
          </div>

          {/* Contact Details */}
          <div className="rounded-lg border border-slate-200 bg-card p-4 space-y-2.5">
            <h4 className="font-bold text-foreground uppercase tracking-wider text-sm">
              Verified Contacts
            </h4>
            <div className="flex items-center gap-2 text-foreground">
              <Mail className="h-4 w-4 text-slate-400" />
              <span>{student.email}</span>
            </div>
            <div className="flex items-center gap-2 text-foreground">
              <Phone className="h-4 w-4 text-slate-400" />
              <span>{student.phone}</span>
            </div>
          </div>

          {/* Faculty Advisors & Mentors */}
          <div className="rounded-lg border border-indigo-200 bg-indigo-50/50 p-4 space-y-3">
            <h4 className="font-bold text-indigo-950 uppercase tracking-wider text-sm flex items-center justify-between">
              <span>Academic Advisors & Faculty</span>
            </h4>

            {/* Class Teacher */}
            {student.classTeacher && (
              <div className="rounded-md border border-indigo-100 bg-white/80 p-2.5 space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-indigo-800 uppercase tracking-wide">Class Teacher</span>
                  <span className="text-[11px] font-medium text-slate-500">{student.classTeacher.cabin}</span>
                </div>
                <div className="text-sm font-semibold text-foreground">{student.classTeacher.name}</div>
                <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-muted-foreground pt-0.5">
                  <span className="flex items-center gap-1"><Phone className="h-3 w-3 text-indigo-600" /> {student.classTeacher.phone}</span>
                  <span className="flex items-center gap-1"><Mail className="h-3 w-3 text-indigo-600" /> {student.classTeacher.email}</span>
                </div>
              </div>
            )}

            {/* Counsellor */}
            {student.counsellor && (
              <div className="rounded-md border border-emerald-100 bg-white/80 p-2.5 space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-emerald-800 uppercase tracking-wide">Student Counsellor</span>
                  <span className="text-[11px] font-medium text-slate-500">{student.counsellor.cabin}</span>
                </div>
                <div className="text-sm font-semibold text-foreground">{student.counsellor.name}</div>
                <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-muted-foreground pt-0.5">
                  <span className="flex items-center gap-1"><Phone className="h-3 w-3 text-emerald-600" /> {student.counsellor.phone}</span>
                  <span className="flex items-center gap-1"><Mail className="h-3 w-3 text-emerald-600" /> {student.counsellor.email}</span>
                </div>
              </div>
            )}

            {/* Mentor */}
            <div className="rounded-md border border-indigo-100 bg-white/80 p-2.5 space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-indigo-800 uppercase tracking-wide">Assigned Mentor</span>
                <span className="text-[11px] font-medium text-slate-500">{student.mentor.cabin}</span>
              </div>
              <div className="text-sm font-semibold text-foreground">{student.mentor.name}</div>
              <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-muted-foreground pt-0.5">
                <span className="flex items-center gap-1"><Phone className="h-3 w-3 text-indigo-600" /> {student.mentor.phone}</span>
                <span className="flex items-center gap-1"><Mail className="h-3 w-3 text-indigo-600" /> {student.mentor.email}</span>
              </div>
            </div>

            <button
              onClick={() => {
                onClose();
                onAskHelpdesk(`I want to book a meeting with my advisor ${student.mentor.name}.`);
              }}
              className="mt-1 w-full rounded-xl bg-indigo-600 py-2 text-xs font-semibold text-white hover:bg-indigo-700 transition-colors cursor-pointer"
            >
              {t.chipBookMentor || "Book Mentor / Advisor Session"}
            </button>
          </div>

          {/* Sign Out Action */}
          {onLogout && (
            <div className="pt-2">
              <button
                onClick={() => {
                  onClose();
                  onLogout();
                }}
                className="w-full flex items-center justify-center gap-2 rounded-xl border border-rose-200 bg-rose-50/70 py-2.5 px-4 text-xs font-semibold text-rose-700 hover:bg-rose-100/70 transition-colors cursor-pointer"
              >
                <LogOut className="h-4 w-4" />
                <span>{t.signOut || "Sign Out"}</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
