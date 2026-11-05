"use client";

import React, { useState, useEffect } from "react";
import {
  Calendar,
  Clock,
  MapPin,
  User,
  GraduationCap,
  Phone,
  CheckCircle2,
  PlayCircle,
  CircleDashed,
  Radio,
} from "lucide-react";
import {
  WEEKLY_TIMETABLE,
  SECTION_METADATA,
  TimetableSlot,
} from "@/data/timetable";
import { Badge } from "@/components/ui/badge";
import { useStudent } from "@/context/StudentContext";
import { useLanguage } from "@/context/LanguageContext";
import { apiClient } from "@/lib/api-client";

interface TimetableViewProps {
  onAskHelpdesk: (query: string) => void;
}

const DAYS_OF_WEEK = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

function getLiveSlotStatus(
  slotDay: string,
  timeSlot: string
): "Completed" | "Current" | "Next" | "Upcoming" {
  const realToday = DAYS_OF_WEEK[new Date().getDay()];
  if (slotDay !== realToday) {
    return "Upcoming";
  }

  const times = timeSlot.split(/[-–]/).map((t) => t.trim());
  if (times.length < 2) return "Upcoming";

  const parseToMinutes = (timeStr: string) => {
    const m = timeStr.match(/^(\d{1,2}):(\d{2})\s*(AM|PM)?$/i);
    if (!m) return null;
    let hours = parseInt(m[1], 10);
    const mins = parseInt(m[2], 10);
    const ampm = m[3] ? m[3].toUpperCase() : null;
    if (ampm === "PM" && hours < 12) hours += 12;
    if (ampm === "AM" && hours === 12) hours = 0;
    return hours * 60 + mins;
  };

  const startMinutes = parseToMinutes(times[0]);
  const endMinutes = parseToMinutes(times[1]);
  if (startMinutes === null || endMinutes === null) return "Upcoming";

  const now = new Date();
  const currentMinutes = now.getHours() * 60 + now.getMinutes();

  if (currentMinutes >= endMinutes) return "Completed";
  if (currentMinutes >= startMinutes && currentMinutes < endMinutes) return "Current";
  if (currentMinutes < startMinutes && startMinutes - currentMinutes <= 30) return "Next";
  return "Upcoming";
}

export const TimetableView: React.FC<TimetableViewProps> = () => {
  const { studentData } = useStudent();
  const { t } = useLanguage();
  const student = studentData?.profile;

  // Real today day name (e.g. Saturday)
  const realToday = DAYS_OF_WEEK[new Date().getDay()];
  const defaultDay = realToday === "Sunday" ? "Monday" : realToday;

  const [selectedDay, setSelectedDay] = useState<string>(defaultDay);
  const [weeklyTimetable, setWeeklyTimetable] = useState<Record<string, TimetableSlot[]>>(WEEKLY_TIMETABLE);
  const [isLiveSynced, setIsLiveSynced] = useState<boolean>(false);

  // Sync live timetable from backend API
  useEffect(() => {
    let isMounted = true;
    const loadLiveTimetable = async () => {
      try {
        const dash = await apiClient.getDashboard();
        if (dash && Array.isArray(dash.timetable) && dash.timetable.length > 0) {
          const byDay: Record<string, TimetableSlot[]> = {};
          dash.timetable.forEach((item: { day_of_week: string; time_slot?: string; course_title: string; course_code: string; room_no: string; faculty_name: string; slot_type?: string }, idx: number) => {
            const day = item.day_of_week;
            if (!byDay[day]) byDay[day] = [];
            const timeParts = (item.time_slot || "").split(/[-–]/).map((p: string) => p.trim());
            byDay[day].push({
              id: `${day.slice(0, 3).toUpperCase()}-${idx + 1}`,
              time: item.time_slot || "",
              startTime: timeParts[0] || "",
              endTime: timeParts[1] || "",
              subject: item.course_title,
              code: item.course_code,
              room: item.room_no,
              faculty: item.faculty_name,
              type: (item.slot_type || "Lecture") as "Lecture" | "Lab" | "Break" | "Tutorial" | "Self Learning" | "Counseling",
              status: "Upcoming",
            });
          });
          if (isMounted) {
            setWeeklyTimetable(byDay);
            setIsLiveSynced(true);
          }
        }
      } catch (err) {
        console.warn("Backend timetable fetch fallback to synchronized schedule:", err);
      }
    };
    loadLiveTimetable();
    return () => {
      isMounted = false;
    };
  }, [student?.id]);

  const currentSlots = weeklyTimetable[selectedDay] || [];

  return (
    <div className="space-y-5">
      {/* Header with Day Selector */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200/80 pb-4">
        <div>
          <div className="flex items-center gap-2 flex-wrap">
            <h2 className="text-xl font-bold text-foreground">{t.timetableTitle}</h2>
            <Badge variant="info">Section-7 (N-312)</Badge>
            {isLiveSynced ? (
              <Badge variant="outline" className="bg-emerald-50 text-emerald-700 border-emerald-200 text-sm gap-1">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                Live Database Schedule
              </Badge>
            ) : (
              <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200 text-sm gap-1">
                <Radio className="h-3 w-3" />
                Verified Routine
              </Badge>
            )}
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            Official department routine for student {student?.id || "251FA04E13"} • {t.classTeacher}: {SECTION_METADATA.classTeacher}
          </p>
        </div>

        {/* Day Selector Buttons */}
        <div className="flex flex-wrap items-center gap-1.5 rounded-xl border border-slate-200 bg-muted/50 p-1">
          {[
            { key: "Monday", label: t.monday },
            { key: "Tuesday", label: t.tuesday },
            { key: "Wednesday", label: t.wednesday },
            { key: "Thursday", label: t.thursday },
            { key: "Friday", label: t.friday },
            { key: "Saturday", label: t.saturday },
          ].map(({ key, label }) => {
            const isToday = key === realToday;
            return (
              <button
                key={key}
                onClick={() => setSelectedDay(key)}
                className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition-all cursor-pointer ${
                  selectedDay === key
                    ? "bg-card text-blue-700 shadow-xs font-bold ring-1 ring-blue-200"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                {label}
                {isToday && <span className="ml-1 text-xs text-blue-600 font-bold">• Today</span>}
              </button>
            );
          })}
        </div>
      </div>

      {/* Section 7 Institutional Info Banner */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
        <div className="rounded-xl border border-blue-100 bg-blue-50/50 p-3.5 flex items-center gap-3 min-h-[74px]">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-blue-600 text-white font-bold text-xs shadow-2xs">
            <MapPin className="h-4 w-4" />
          </div>
          <div className="min-w-0">
            <span className="text-xs font-bold text-blue-800 uppercase tracking-wider">Classroom & Section</span>
            <p className="text-xs font-bold text-foreground truncate">{SECTION_METADATA.section} ({SECTION_METADATA.room})</p>
          </div>
        </div>

        <div className="rounded-xl border border-indigo-100 bg-indigo-50/50 p-3.5 flex items-center gap-3 min-h-[74px]">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-indigo-600 text-white font-bold text-xs shadow-2xs">
            <User className="h-4 w-4" />
          </div>
          <div className="min-w-0">
            <span className="text-xs font-bold text-indigo-800 uppercase tracking-wider">{t.classTeacher}</span>
            <p className="text-xs font-bold text-foreground truncate">{SECTION_METADATA.classTeacher}</p>
          </div>
        </div>

        <div className="rounded-xl border border-purple-100 bg-purple-50/50 p-3.5 flex items-center gap-3 min-h-[74px]">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-purple-600 text-white font-bold text-xs shadow-2xs">
            <Phone className="h-4 w-4" />
          </div>
          <div className="min-w-0">
            <span className="text-xs font-bold text-purple-800 uppercase tracking-wider">{t.coordinator}</span>
            <p className="text-xs font-bold text-foreground truncate" title={`${SECTION_METADATA.timetableCoordinator} (${SECTION_METADATA.coordinatorPhone})`}>
              {SECTION_METADATA.timetableCoordinator}
            </p>
            <p className="text-xs font-mono text-purple-700 font-medium truncate">{SECTION_METADATA.coordinatorPhone}</p>
          </div>
        </div>

        <div className="rounded-xl border border-emerald-100 bg-emerald-50/50 p-3.5 flex items-center gap-3 min-h-[74px]">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-emerald-600 text-white font-bold text-xs shadow-2xs">
            <GraduationCap className="h-4 w-4" />
          </div>
          <div className="min-w-0">
            <span className="text-xs font-bold text-emerald-800 uppercase tracking-wider">HOD, CSE</span>
            <p className="text-xs font-bold text-foreground truncate">{SECTION_METADATA.hodCse}</p>
          </div>
        </div>
      </div>

      {/* Timeline List */}
      <div className="rounded-lg border border-slate-200 bg-card p-5 sm:p-6 shadow-2xs space-y-4">
        <div className="flex items-center justify-between pb-2 border-b border-slate-100">
          <div className="flex items-center gap-2">
            <Calendar className="h-4 w-4 text-muted-foreground" />
            <span className="text-xs font-bold text-foreground uppercase tracking-wider">
              {selectedDay} Academic Schedule ({SECTION_METADATA.section})
            </span>
          </div>
          <span className="text-xs text-muted-foreground font-medium">
            {currentSlots.length} Academic Sessions
          </span>
        </div>

        {currentSlots.length === 0 ? (
          <div className="py-8 text-center text-sm text-muted-foreground">
            No instructional sessions scheduled for {selectedDay}.
          </div>
        ) : (
          <div className="relative pl-6 space-y-5 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
            {currentSlots.map((slot) => {
              const liveStatus = getLiveSlotStatus(selectedDay, slot.time);
              const isCompleted = liveStatus === "Completed";
              const isCurrent = liveStatus === "Current";
              const isNext = liveStatus === "Next";

              return (
                <div key={slot.id} className="relative group">
                  {/* Timeline node icon */}
                  <div
                    className={`absolute -left-6 top-2 flex h-5 w-5 items-center justify-center rounded-full border-2 bg-card transition-transform group-hover:scale-110 ${
                      isCompleted
                        ? "border-emerald-500 text-emerald-600"
                        : isCurrent
                        ? "border-blue-600 bg-blue-600 text-white animate-pulse"
                        : isNext
                        ? "border-amber-500 text-amber-600"
                        : "border-slate-300 text-slate-400"
                    }`}
                  >
                    {isCompleted ? (
                      <CheckCircle2 className="h-3 w-3" />
                    ) : isCurrent ? (
                      <PlayCircle className="h-3 w-3 text-white" />
                    ) : (
                      <CircleDashed className="h-3 w-3" />
                    )}
                  </div>

                  {/* Slot Card */}
                  <div
                    className={`rounded-xl border p-4 transition-all ${
                      isCurrent
                        ? "border-blue-400 bg-blue-50/50 shadow-xs ring-1 ring-blue-200"
                        : isNext
                        ? "border-amber-300 bg-amber-50/30"
                        : "border-slate-200/80 bg-card hover:border-slate-300"
                    }`}
                  >
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                      <div>
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="font-bold text-foreground text-sm">{slot.subject}</span>
                          {slot.code && (
                            <span className="rounded-md bg-muted px-2 py-0.5 font-mono text-sm text-muted-foreground font-semibold">
                              {slot.code}
                            </span>
                          )}
                          <span className="rounded-full bg-muted px-2 py-0.5 text-sm font-medium text-muted-foreground">
                            {slot.type}
                          </span>
                        </div>

                        <div className="flex flex-wrap items-center gap-3 text-xs text-muted-foreground mt-1.5">
                          <div className="flex items-center gap-1 font-semibold text-blue-800">
                            <MapPin className="h-3.5 w-3.5 text-blue-600" />
                            <span>{slot.room}</span>
                          </div>
                          {slot.faculty && slot.faculty !== "-" && (
                            <div className="flex items-center gap-1 text-muted-foreground">
                              <User className="h-3.5 w-3.5 text-slate-400" />
                              <span>{slot.faculty}</span>
                            </div>
                          )}
                        </div>
                      </div>

                      <div className="flex items-center sm:flex-col sm:items-end gap-2">
                        <div className="flex items-center gap-1 text-xs font-bold text-foreground">
                          <Clock className="h-3.5 w-3.5 text-slate-400" />
                          <span>{slot.time}</span>
                        </div>

                        {/* Status Tag calculated from live clock */}
                        <span
                          className={`rounded-full px-2 py-0.5 text-sm font-bold ${
                            isCurrent
                              ? "bg-blue-600 text-white animate-pulse"
                              : isNext
                              ? "bg-amber-100 text-amber-800"
                              : isCompleted
                              ? "bg-emerald-100 text-emerald-800"
                              : "bg-muted text-muted-foreground"
                          }`}
                        >
                          {liveStatus}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

