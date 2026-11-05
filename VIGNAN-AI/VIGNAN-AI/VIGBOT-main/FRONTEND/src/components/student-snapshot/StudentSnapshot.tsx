"use client";

import React from "react";
import {
  UserCheck,
  GraduationCap,
  Clock,
  Calendar,
  CreditCard,
  BookOpen,
  ArrowUpRight,
  AlertTriangle,
  LucideIcon,
} from "lucide-react";
import { ATTENDANCE_DATA } from "@/data/attendance";
import { MARKS_DATA } from "@/data/marks";
import { TODAY_TIMETABLE } from "@/data/timetable";
import { EXAMINATIONS_DATA } from "@/data/examinations";
import { useStudent } from "@/context/StudentContext";
import { useLanguage } from "@/context/LanguageContext";
import { cn, formatCurrency } from "@/lib/utils";
import { useDynamicSchedule } from "@/hooks/useDynamicSchedule";

interface StudentSnapshotProps {
  onNavigateTab: (tab: string) => void;
}

interface SnapshotCardProps {
  label: string;
  icon: LucideIcon;
  tone: "amber" | "emerald" | "blue" | "indigo" | "cyan";
  value: React.ReactNode;
  valueSuffix?: string;
  meta: React.ReactNode;
  subtext: string;
  footerLabel: string;
  onClick: () => void;
  emphasize?: boolean;
}

const toneClasses: Record<
  SnapshotCardProps["tone"],
  { border: string; icon: string; iconBg: string; value: string; footer: string }
> = {
  amber: {
    border: "hover:border-amber-300",
    icon: "text-amber-600",
    iconBg: "bg-amber-50 group-hover:bg-amber-100",
    value: "text-amber-900",
    footer: "text-amber-700 group-hover:text-amber-900",
  },
  emerald: {
    border: "hover:border-emerald-300",
    icon: "text-emerald-600",
    iconBg: "bg-emerald-50 group-hover:bg-emerald-100",
    value: "text-foreground",
    footer: "text-emerald-700 group-hover:text-emerald-900",
  },
  blue: {
    border: "hover:border-blue-300",
    icon: "text-blue-600",
    iconBg: "bg-blue-50 group-hover:bg-blue-100",
    value: "text-foreground",
    footer: "text-blue-700 group-hover:text-blue-900",
  },
  indigo: {
    border: "hover:border-indigo-300",
    icon: "text-indigo-600",
    iconBg: "bg-indigo-50 group-hover:bg-indigo-100",
    value: "text-indigo-950",
    footer: "text-indigo-700 group-hover:text-indigo-900",
  },
  cyan: {
    border: "hover:border-cyan-300",
    icon: "text-cyan-600",
    iconBg: "bg-cyan-50 group-hover:bg-cyan-100",
    value: "text-foreground",
    footer: "text-cyan-700 group-hover:text-cyan-900",
  },
};

const SnapshotCard: React.FC<SnapshotCardProps> = ({
  label,
  icon: Icon,
  tone,
  value,
  meta,
  subtext,
  footerLabel,
  onClick,
  emphasize,
}) => {
  const toneStyle = toneClasses[tone];
  return (
    <div
      onClick={onClick}
      className={cn(
        "group relative flex h-full min-h-[168px] cursor-pointer flex-col justify-between rounded-lg border bg-card p-4 transition-all hover:shadow-md hover:-translate-y-0.5",
        emphasize ? "border-amber-200" : "border-slate-200",
        toneStyle.border
      )}
    >
      <div className="flex flex-col flex-1">
        {/* Card Header */}
        <div className="mb-2 flex items-center justify-between gap-2">
          <span className="text-sm font-bold uppercase tracking-wider text-muted-foreground truncate">
            {label}
          </span>
          <div
            className={cn(
              "flex h-7 w-7 shrink-0 items-center justify-center rounded-lg transition-colors",
              toneStyle.iconBg
            )}
          >
            <Icon className={cn("h-4 w-4", toneStyle.icon)} />
          </div>
        </div>

        {/* Value Line - Uniform baseline height */}
        <div className={cn("flex h-9 items-baseline gap-1.5 text-2xl font-black truncate", toneStyle.value)}>
          {value}
        </div>

        {/* Meta Line - Fixed height */}
        <div className="mt-1.5 flex h-5 items-center text-xs font-semibold text-foreground truncate">
          {meta}
        </div>

        {/* Subtext Line - Fixed height with ellipsis */}
        <p className="mt-0.5 h-7 text-sm leading-snug text-muted-foreground line-clamp-1 truncate" title={typeof subtext === "string" ? subtext : undefined}>
          {subtext}
        </p>
      </div>

      {/* Footer Line - Uniform bottom alignment */}
      <div
        className={cn(
          "mt-3 flex items-center justify-between border-t border-slate-100 pt-2.5 text-xs font-medium shrink-0",
          toneStyle.footer
        )}
      >
        <span className="truncate">{footerLabel}</span>
        <ArrowUpRight className="h-3.5 w-3.5 shrink-0 transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
      </div>
    </div>
  );
};

export const StudentSnapshot: React.FC<StudentSnapshotProps> = ({ onNavigateTab }) => {
  const { studentData } = useStudent();
  const { t, tDynamic } = useLanguage();
  const student = studentData?.profile;
  const attendance = studentData?.attendance || ATTENDANCE_DATA;
  const marks = studentData?.marks || MARKS_DATA;
  const fees = studentData?.fees;

  const lowestSub = attendance.subjects && attendance.subjects.length > 0
    ? [...attendance.subjects].sort((a, b) => a.percentage - b.percentage)[0]
    : null;

  const nextExam = EXAMINATIONS_DATA.exams[0];
  const { nextClassSlot, formattedNextExamDate } = useDynamicSchedule();

  return (
    <section className="space-y-3.5">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <h3 className="text-lg font-bold text-foreground">{t.snapshotTitle} (Section 7, N-312)</h3>
          <p className="text-xs text-muted-foreground">
            {t.snapshotSubtitle} • {student?.id || "251FA04E13"} • Class Teacher: Mr. T. Latesh Babu
          </p>
        </div>
        <span className="self-start sm:self-auto inline-flex items-center gap-1.5 whitespace-nowrap rounded-full bg-emerald-50 px-2.5 py-1 text-sm font-medium text-emerald-700 border border-emerald-100">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
          {t.sectionSynchronized}
        </span>
      </div>

      {/* 6 Responsive Grid Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-3.5">
        <SnapshotCard
          label={t.navAttendance}
          icon={UserCheck}
          tone="amber"
          emphasize
          value={
            <>
              <span>{attendance.overallPercentage}%</span>
              <span className="text-xs font-semibold text-amber-700">{t.overall}</span>
            </>
          }
          meta={
            <span className="flex items-center gap-1 text-amber-700">
              <AlertTriangle className="h-3 w-3" />
              {attendance.status ? tDynamic(attendance.status) : t.statusAttention}
            </span>
          }
          subtext={lowestSub ? `${lowestSub.name} (${lowestSub.percentage}%)` : "DLD-25CS205 (68%)"}
          footerLabel={t.viewAttendance}
          onClick={() => onNavigateTab("attendance")}
        />

        <SnapshotCard
          label={t.navMarks}
          icon={GraduationCap}
          tone="emerald"
          value={
            <>
              <span>{marks.overallPercentage}%</span>
              <span className="text-xs font-semibold text-emerald-700">CGPA {student?.cgpa ?? 8.42}</span>
            </>
          }
          meta={t.currentPerformance}
          subtext={t.topPerformer}
          footerLabel={t.viewMarks}
          onClick={() => onNavigateTab("marks")}
        />

        <SnapshotCard
          label={t.nextClass}
          icon={Clock}
          tone="blue"
          value={<span className="text-xl sm:text-2xl">{nextClassSlot ? nextClassSlot.time.split("–")[0].trim() : "12:30 PM"}</span>}
          meta={<span className="truncate">{nextClassSlot ? nextClassSlot.subject : "Discrete Mathematics"}</span>}
          subtext={nextClassSlot ? `${nextClassSlot.room} • ${nextClassSlot.faculty.split("(")[0].trim()}` : "N-312 • Dr. N. Santhoshi"}
          footerLabel={t.viewSchedule}
          onClick={() => onNavigateTab("timetable")}
        />

        <SnapshotCard
          label={t.nextExam}
          icon={Calendar}
          tone="indigo"
          value={<span className="text-xl sm:text-2xl whitespace-nowrap">{formattedNextExamDate}</span>}
          meta={<span className="truncate">{nextExam ? nextExam.subject : "Digital Logic design"}</span>}
          subtext={nextExam ? `${nextExam.time.split("–")[0].trim()} • ${nextExam.venue.split(",")[0].trim()} (${nextExam.daysRemaining}d left)` : "10:00 AM • Hall A2"}
          footerLabel={t.viewExams}
          onClick={() => onNavigateTab("exams")}
        />

        <SnapshotCard
          label={t.navFees}
          icon={CreditCard}
          tone="amber"
          value={<span className="text-xl sm:text-2xl">{formatCurrency(fees?.outstandingBalance ?? 0)}</span>}
          meta={t.outstandingDues}
          subtext={`${formatCurrency(fees?.paidAmount ?? 100000)} ${t.statusPaid} (${t.statusDue} 30 Sep 2026)`}
          footerLabel={t.viewDetails}
          onClick={() => onNavigateTab("fees")}
        />

        <SnapshotCard
          label={t.navCurriculum}
          icon={BookOpen}
          tone="cyan"
          value={
            <>
              <span>78</span>
              <span className="text-sm font-normal text-slate-400">/ 160</span>
            </>
          }
          meta={t.creditsCompleted}
          subtext={t.curriculumProgressSub}
          footerLabel={t.viewProgress}
          onClick={() => onNavigateTab("curriculum")}
        />
      </div>
    </section>
  );
};
