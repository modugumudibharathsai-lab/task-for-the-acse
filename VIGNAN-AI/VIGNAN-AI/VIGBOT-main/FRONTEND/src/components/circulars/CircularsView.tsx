"use client";

import React, { useState } from "react";
import {
  Bell,
  AlertCircle,
  FileText,
  Calendar,
  ChevronRight,
  Filter,
  Download,
} from "lucide-react";
import { CIRCULARS_DATA, CircularItem } from "@/data/circulars";
import { useLanguage } from "@/context/LanguageContext";

interface CircularsViewProps {
  onAskHelpdesk: (query: string) => void;
}

export const CircularsView: React.FC<CircularsViewProps> = ({ onAskHelpdesk }) => {
  const { t, tDynamic } = useLanguage();
  const [filterCategory, setFilterCategory] = useState<string>("All");

  const categories = ["All", "Examinations", "Academics", "Administration", "Holidays"];

  const filteredCirculars =
    filterCategory === "All"
      ? CIRCULARS_DATA
      : CIRCULARS_DATA.filter((c) => c.category === filterCategory);

  return (
    <div className="@container space-y-6">
      {/* Header */}
      <div className="flex flex-col @lg:flex-row @lg:items-center justify-between gap-3 border-b border-slate-200/80 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-foreground">{t.circularsTitle || "Official University Circulars"}</h2>
            
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            {t.circularsSubtitle || "Official announcements issued by the Registrar and Controller of Examinations."}
          </p>
        </div>

        {/* Category Filters */}
        <div className="flex items-center gap-1.5 overflow-x-auto">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setFilterCategory(cat)}
              className={`rounded-lg px-2.5 py-1 text-xs font-semibold transition-all cursor-pointer ${
                filterCategory === cat
                  ? "bg-slate-900 text-white shadow-2xs"
                  : "bg-card border border-slate-200 text-muted-foreground hover:bg-muted/50"
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Circulars List */}
      <div className="space-y-3">
        {filteredCirculars.map((item) => {
          const isUrgent = item.priority === "Urgent";
          const isHigh = item.priority === "High";

          return (
            <div
              key={item.id}
              className={`rounded-lg border p-5 transition-all bg-card hover:shadow-2xs ${
                isUrgent
                  ? "border-rose-300 bg-rose-50/20"
                  : isHigh
                  ? "border-amber-200 bg-amber-50/20"
                  : "border-slate-200"
              }`}
            >
              <div className="flex flex-col @lg:flex-row @lg:items-start justify-between gap-2">
                <div className="space-y-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span
                      className={`rounded-full px-2 py-0.5 text-sm font-bold uppercase tracking-wider ${
                        isUrgent
                          ? "bg-rose-100 text-rose-800"
                          : isHigh
                          ? "bg-amber-100 text-amber-800"
                          : "bg-muted text-muted-foreground"
                      }`}
                    >
                      {item.priority}
                    </span>
                    <span className="rounded-md bg-blue-50 px-2 py-0.5 text-sm font-semibold text-blue-700">
                      {item.category}
                    </span>
                    <span className="font-mono text-sm text-slate-400">Ref: {item.refNo}</span>
                  </div>

                  <h3 className="text-sm sm:text-base font-bold text-foreground pt-1">
                    {item.title}
                  </h3>
                  <p className="text-xs text-muted-foreground leading-relaxed">{item.shortDescription}</p>

                  {item.actionRequired && (
                    <div className="mt-2 text-xs font-semibold text-rose-800 flex items-center gap-1.5">
                      <AlertCircle className="h-3.5 w-3.5 text-rose-600" />
                      <span>Action: {item.actionRequired}</span>
                    </div>
                  )}
                </div>

                <div className="flex flex-row @lg:flex-col @lg:items-end justify-between gap-2 shrink-0 pt-2 @lg:pt-0">
                  <span className="flex items-center gap-1 text-xs text-slate-400 font-medium">
                    <Calendar className="h-3.5 w-3.5" />
                    {item.date}
                  </span>
                  <button
                    onClick={() => onAskHelpdesk(`Tell me more about circular: ${item.title}`)}
                    className="text-xs font-semibold text-blue-600 hover:text-blue-800 flex items-center gap-1"
                  >
                    <span>{t.askButton}</span>
                    <ChevronRight className="h-3.5 w-3.5" />
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
