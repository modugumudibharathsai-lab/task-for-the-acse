"use client";

import React, { useState } from "react";
import {
  FileText,
  Search,
  BookOpen,
  Calendar,
  ShieldCheck,
  ChevronRight,
  X,
  Sparkles,
} from "lucide-react";
import { POLICIES_DATA, PolicyItem } from "@/data/policies";
import { useLanguage } from "@/context/LanguageContext";

interface PoliciesViewProps {
  onAskHelpdesk: (query: string) => void;
}

export const PoliciesView: React.FC<PoliciesViewProps> = ({ onAskHelpdesk }) => {
  const { t, tDynamic } = useLanguage();
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedPolicy, setSelectedPolicy] = useState<PolicyItem | null>(null);

  const filteredPolicies = POLICIES_DATA.filter(
    (p) =>
      p.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.category.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.shortDescription.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="@container space-y-6">
      {/* Header */}
      <div className="flex flex-col @lg:flex-row @lg:items-center justify-between gap-3 border-b border-slate-200/80 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-foreground">{t.policiesTitle || "University Policies & Guidelines"}</h2>
            
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            {t.policiesSubtitle || "Authoritative institutional regulations approved by the Academic Senate."}
          </p>
        </div>

        {/* Search Input */}
        <div className="relative w-full sm:w-72">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder={t.searchPlaceholder || "Search policies..."}
            className="w-full rounded-xl border border-slate-200 bg-card py-2 pl-9 pr-3 text-xs text-foreground placeholder:text-slate-400 focus:border-blue-500 focus:outline-hidden"
          />
        </div>
      </div>

      {/* Policies Grid */}
      <div className="grid grid-cols-1 @2xl:grid-cols-2 gap-4">
        {filteredPolicies.map((pol) => (
          <div
            key={pol.id}
            className="rounded-lg border border-slate-200 bg-card p-5 shadow-2xs hover:shadow-sm hover:border-slate-300 transition-all flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="rounded-full bg-blue-50 px-2.5 py-0.5 text-sm font-bold text-blue-700">
                  {pol.category}
                </span>
                <span className="text-sm text-slate-400">Effective: {pol.effectiveDate}</span>
              </div>

              <h3 className="text-base font-bold text-foreground mb-1">{pol.title}</h3>
              <p className="text-xs text-muted-foreground leading-relaxed">{pol.shortDescription}</p>

              <div className="mt-3 space-y-1">
                {pol.keyPoints.slice(0, 2).map((pt, i) => (
                  <div key={i} className="text-sm text-muted-foreground flex items-start gap-1.5">
                    <span className="h-1.5 w-1.5 rounded-full bg-blue-500 mt-1.5 shrink-0" />
                    <span>{pt}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
              <button
                onClick={() => setSelectedPolicy(pol)}
                className="text-xs font-semibold text-blue-600 hover:text-blue-800 transition-colors flex items-center gap-1 cursor-pointer"
              >
                <span>{t.viewFullPolicy || "View Full Policy"}</span>
                <ChevronRight className="h-3.5 w-3.5" />
              </button>

              <button
                onClick={() => onAskHelpdesk(`What does the ${pol.title} say?`)}
                className="text-xs text-muted-foreground hover:text-foreground flex items-center gap-1"
              >
                <Sparkles className="h-3 w-3 text-violet-600" />
                <span>{t.askAi || "Ask AI"}</span>
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Policy Detail Modal */}
      {selectedPolicy && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-xs p-4">
          <div className="relative w-full max-w-2xl max-h-[85vh] overflow-y-auto overscroll-contain rounded-xl bg-card p-6 shadow-2xl border border-slate-200">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <span className="rounded-full bg-blue-50 px-2 py-0.5 text-sm font-bold text-blue-700">
                  {selectedPolicy.category}
                </span>
                <h3 className="text-lg font-bold text-foreground mt-1">{selectedPolicy.title}</h3>
              </div>
              <button
                onClick={() => setSelectedPolicy(null)}
                className="rounded-full p-1.5 text-slate-400 hover:bg-muted transition-colors cursor-pointer"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="my-4 space-y-4 text-xs text-foreground leading-relaxed">
              <div className="rounded-xl bg-blue-50/60 p-3 border border-blue-100">
                <span className="font-bold text-blue-900">Summary: </span>
                {selectedPolicy.shortDescription}
              </div>

              <div>
                <h4 className="font-bold text-foreground text-sm mb-2">Key Regulatory Articles:</h4>
                <ul className="space-y-2">
                  {selectedPolicy.keyPoints.map((pt, i) => (
                    <li key={i} className="rounded-lg bg-muted/50 p-2.5 border border-slate-100 text-foreground">
                      {pt}
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <h4 className="font-bold text-foreground text-sm mb-1">Senate Ordinance Text:</h4>
                <div className="rounded-xl bg-muted/50 p-3 border border-slate-100 whitespace-pre-line text-muted-foreground font-mono text-sm">
                  {selectedPolicy.fullText}
                </div>
              </div>
            </div>

            <div className="flex justify-end pt-3 border-t border-slate-100">
              <button
                onClick={() => setSelectedPolicy(null)}
                className="rounded-xl bg-slate-900 px-4 py-2 text-xs font-semibold text-white hover:bg-slate-800 cursor-pointer"
              >
                Close Policy
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
