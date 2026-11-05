"use client";

import React, { useState } from "react";
import {
  Calendar as CalendarIcon,
  Clock,
  CheckCircle2,
  AlertCircle,
  Flag,
  ArrowRight,
  Info,
} from "lucide-react";
import { ACADEMIC_CALENDAR_DATA, CalendarEvent } from "@/data/calendar";
import { useLanguage } from "@/context/LanguageContext";

interface CalendarViewProps {
  onAskHelpdesk: (query: string) => void;
  onNavigateTab: (tab: string) => void;
}

export const CalendarView: React.FC<CalendarViewProps> = ({ onAskHelpdesk, onNavigateTab }) => {
  const { t, tDynamic } = useLanguage();
  const [selectedEvent, setSelectedEvent] = useState<CalendarEvent | null>(
    ACADEMIC_CALENDAR_DATA.find((e) => e.status === "Current") || ACADEMIC_CALENDAR_DATA[6]
  );

  return (
    <div className="@container space-y-6">
      {/* Header */}
      <div className="flex flex-col @lg:flex-row @lg:items-center justify-between gap-3 border-b border-slate-200/80 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-foreground">{t.calendarTitle || "Academic Calendar 2026-27 (Semester-I)"}</h2>
            <span className="rounded-full bg-teal-100 px-2.5 py-0.5 text-[11px] font-bold text-teal-800">
              VFSTR Official
            </span>
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            Vignan's Foundation for Science, Technology and Research (Vadlamudi) • B.Tech 2nd (R25), 3rd (R22C24) & 4th (R22) Year • Dated: 6/1/2026
          </p>
        </div>

        <button
          onClick={() => onAskHelpdesk("What is the next deadline on the academic calendar?")}
          className="flex items-center gap-1.5 rounded-xl bg-slate-900 px-3.5 py-2 text-xs font-semibold text-white shadow-xs hover:bg-slate-800 transition-colors cursor-pointer"
        >
          <CalendarIcon className="h-4 w-4" />
          <span>{t.askButton || "Ask Agent"}: {t.calendarMilestones || "Milestones"}</span>
        </button>
      </div>

      <div className="grid grid-cols-1 @4xl:grid-cols-12 gap-6">
        {/* Timeline Events (8 Cols) */}
        <div className="@4xl:col-span-8 space-y-3">
          {ACADEMIC_CALENDAR_DATA.map((evt) => {
            const isSelected = selectedEvent?.id === evt.id;
            const isCompleted = evt.status === "Completed";

            return (
              <div
                key={evt.id}
                onClick={() => setSelectedEvent(evt)}
                className={`rounded-2xl border p-4 transition-all cursor-pointer ${
                  isSelected
                    ? "border-teal-500 bg-teal-50/30 ring-2 ring-teal-100 shadow-sm"
                    : "border-slate-200 bg-card hover:border-slate-300 hover:shadow-2xs"
                }`}
              >
                <div className="flex flex-col @lg:flex-row @lg:items-center justify-between gap-2">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="rounded-full bg-muted px-2.5 py-0.5 text-[11px] font-bold text-foreground">
                        {evt.category}
                      </span>
                      <h4 className="font-bold text-foreground text-sm">{evt.title}</h4>
                    </div>
                    <p className="text-xs text-muted-foreground leading-relaxed">{evt.description}</p>
                  </div>

                  <div className="text-left sm:text-right shrink-0">
                    <div className="flex items-center justify-end gap-1 font-mono text-xs font-bold text-teal-800">
                      <CalendarIcon className="h-3.5 w-3.5 shrink-0" />
                      {evt.startDate}
                      {evt.endDate && ` – ${evt.endDate}`}
                    </div>
                    <span
                      className={`inline-block rounded-full px-2 py-0.5 text-[11px] font-bold mt-1 ${
                        isCompleted
                          ? "bg-muted text-muted-foreground"
                          : "bg-teal-100 text-teal-800"
                      }`}
                    >
                      {evt.status}
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Right: Selected Event Card (4 Cols) */}
        <div className="@4xl:col-span-4">
          {selectedEvent ? (
            <div className="@4xl:sticky @4xl:top-28 rounded-2xl border border-teal-200 bg-card p-5 shadow-2xs space-y-4">
              <div className="flex items-center gap-2 border-b border-slate-100 pb-2.5">
                <Info className="h-4 w-4 text-teal-600" />
                <h4 className="text-xs font-bold uppercase tracking-wider text-foreground">
                  Milestone Details
                </h4>
              </div>

              <div className="space-y-2">
                <span className="rounded-full bg-teal-50 px-2.5 py-0.5 text-[11px] font-bold text-teal-800">
                  {selectedEvent.category}
                </span>
                <h3 className="text-base font-bold text-foreground">{selectedEvent.title}</h3>
                <div className="flex items-center gap-1 text-xs font-bold text-teal-900">
                  <CalendarIcon className="h-3.5 w-3.5 shrink-0" />
                  {selectedEvent.startDate}
                  {selectedEvent.endDate && ` – ${selectedEvent.endDate}`}
                </div>
                <p className="text-xs text-muted-foreground leading-relaxed pt-1">
                  {selectedEvent.description}
                </p>
                <div className="text-[11px] text-slate-400 pt-2">
                  Sourced from {selectedEvent.sourceAgent}
                </div>
              </div>

              <button
                onClick={() => onAskHelpdesk(`Tell me more about ${selectedEvent.title}`)}
                className="w-full flex items-center justify-center gap-1.5 rounded-xl bg-teal-700 py-2.5 text-xs font-semibold text-white hover:bg-teal-800 transition-colors shadow-2xs cursor-pointer"
              >
                <span>{t.askButton}: {t.upcomingMilestone}</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </button>
            </div>
          ) : (
            <div className="rounded-2xl border border-dashed border-slate-200 p-6 text-center text-xs text-slate-400">
              Select an event to view full details.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
