"use client";

import React, { useState } from "react";
import {
  ShieldCheck,
  X,
  Layers,
  Activity,
  Server,
  Timer,
} from "lucide-react";
import { CONNECTED_AGENTS } from "@/data/connected-agents";
import { INITIAL_SECURITY_LOGS, SecurityLogItem } from "@/data/security-logs";
import { CURRENT_STUDENT } from "@/data/student";
import { useLanguage } from "@/context/LanguageContext";
import { useStudent } from "@/context/StudentContext";

interface SecurityDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

export const SecurityDrawer: React.FC<SecurityDrawerProps> = ({ isOpen, onClose }) => {
  const { t } = useLanguage();
  const { studentData } = useStudent();
  const student = studentData?.profile || CURRENT_STUDENT;
  const [activeTab, setActiveTab] = useState<"architecture" | "logs" | "agents">("architecture");

  if (!isOpen) return null;

  return (
    <div role="dialog" aria-modal="true" className="fixed inset-0 z-50 flex justify-end bg-slate-900/40 backdrop-blur-xs">
      <div className="relative w-full max-w-2xl h-full bg-card shadow-2xl border-l border-slate-200 flex flex-col animate-in slide-in-from-right duration-300">
        {/* Drawer Header */}
        <div className="flex items-center justify-between border-b border-slate-200 p-5 bg-gradient-to-r from-blue-50 to-white">
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600 border border-emerald-200">
              <ShieldCheck className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-foreground">{t.securityTitle || "Security & Access Audit"}</h3>
              <p className="text-sm text-muted-foreground">
                Row-Level Security (RLS) Isolation • VIGNAN-AI Core
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="rounded-full p-1.5 text-slate-400 hover:bg-muted hover:text-foreground transition-colors cursor-pointer"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Navigation Tabs */}
        <div className="flex border-b border-slate-200 bg-muted/50 px-5 text-xs font-semibold">
          <button
            onClick={() => setActiveTab("architecture")}
            className={`py-3 px-4 border-b-2 transition-all cursor-pointer ${
              activeTab === "architecture"
                ? "border-blue-600 text-blue-700 font-bold bg-card"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            <span className="flex items-center gap-1.5">
              <Layers className="h-3.5 w-3.5" />
              <span>{t.rlsDataFlow || "RLS Guardrail Data Flow"}</span>
            </span>
          </button>
          <button
            onClick={() => setActiveTab("logs")}
            className={`py-3 px-4 border-b-2 transition-all cursor-pointer ${
              activeTab === "logs"
                ? "border-blue-600 text-blue-700 font-bold bg-card"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            <span className="flex items-center gap-1.5">
              <Activity className="h-3.5 w-3.5" />
              <span>{t.transactionHistory}</span>
            </span>
          </button>
          <button
            onClick={() => setActiveTab("agents")}
            className={`py-3 px-4 border-b-2 transition-all cursor-pointer ${
              activeTab === "agents"
                ? "border-blue-600 text-blue-700 font-bold bg-card"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            <span className="flex items-center gap-1.5">
              <Server className="h-3.5 w-3.5" />
              <span>Connected Services (12)</span>
            </span>
          </button>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto overscroll-contain p-5 space-y-5 text-xs text-foreground">
          {activeTab === "architecture" && (
            <div className="space-y-4">
              {/* Authenticated Verification Card */}
              <div className="rounded-lg border border-emerald-200 bg-emerald-50/70 p-4 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-emerald-950 flex items-center gap-1.5">
                    <ShieldCheck className="h-4 w-4 text-emerald-600" />
                    <span>{t.footerRls}</span>
                  </span>
                  <span className="rounded-md bg-emerald-200/80 px-2 py-0.5 text-sm font-bold text-emerald-900">
                    ENFORCED AT DATA LAYER
                  </span>
                </div>
                <p className="text-emerald-900/90 leading-relaxed text-sm">
                  The system only retrieves information from the authenticated student&apos;s own record (<strong>{student.id}</strong>). Cross-tenant queries are blocked before reaching database engines.
                </p>
              </div>

              {/* Data Flow Pipeline Diagram */}
              <div className="rounded-lg border border-slate-200 bg-muted/50/60 p-4 space-y-3">
                <h4 className="font-bold text-foreground text-xs uppercase tracking-wider">
                  Request Authorization & Pipeline Sequence:
                </h4>

                <div className="space-y-2">
                  {[
                    { step: "1", title: "Authenticate Student", desc: `Identity confirmed as ${student.name} (${student.id}) via Identity Service.` },
                    { step: "2", title: "Establish Identity Context", desc: "OAuth2 token injected: [Verified]." },
                    { step: "3", title: "Classify Question Intent", desc: "Categorized into Personal Data, Institutional Info, Service, or Distress." },
                    { step: "4", title: "Authorize Requested Scope", desc: "Validates caller rights. Rejects attempts to request other students' data." },
                    { step: "5", title: "Retrieve Only Student's Own Record", desc: "Data queried directly from specific specialized service (e.g. Biometric Attendance)." },
                    { step: "6", title: "Generate Actionable Answer", desc: "Combines raw record + contextual calculation (e.g. 4 consecutive classes)." },
                    { step: "7", title: "Route Service Request (if applicable)", desc: "Enqueues ticket into Services workflow bus." },
                    { step: "8", title: "Continuous Distress Monitoring", desc: "Monitored at all turns for immediate supportive Crisis Counselor handoff." },
                  ].map((s) => (
                    <div
                      key={s.step}
                      className="flex items-start gap-3 rounded-xl bg-card p-2.5 border border-slate-200 shadow-2xs"
                    >
                      <span className="flex h-5 w-5 items-center justify-center rounded-full bg-blue-600 text-sm font-bold text-white shrink-0">
                        {s.step}
                      </span>
                      <div>
                        <div className="font-bold text-foreground">{s.title}</div>
                        <div className="text-sm text-muted-foreground mt-0.5">{s.desc}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === "logs" && (
            <div className="space-y-3">
              <div className="flex items-center justify-between pb-1">
                <span className="text-sm font-bold uppercase tracking-wider text-slate-400">
                  Real-time Security Ledger
                </span>
                <span className="text-sm text-emerald-600 font-semibold flex items-center gap-1">
                  <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                  Live Audit Telemetry
                </span>
              </div>

              <div className="space-y-2">
                {INITIAL_SECURITY_LOGS.map((log) => (
                  <div
                    key={log.id}
                    className="rounded-xl border border-slate-200 bg-card p-3 shadow-2xs space-y-1"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-foreground">{log.event}</span>
                      <span
                        className={`rounded-full px-2 py-0.2 text-sm font-bold ${
                          log.status === "SUCCESS"
                            ? "bg-emerald-100 text-emerald-800"
                            : log.status === "FORWARDED"
                            ? "bg-blue-100 text-blue-800"
                            : "bg-rose-100 text-rose-800"
                        }`}
                      >
                        {log.status}
                      </span>
                    </div>
                    <div className="text-sm text-muted-foreground flex items-center gap-2">
                      <span className="flex items-center gap-1">
                        <Timer className="h-3 w-3" />
                        {log.time}
                      </span>
                      <span>•</span>
                      <span className="font-semibold text-blue-700">{log.agent}</span>
                      <span>•</span>
                      <span className="font-mono text-muted-foreground">{log.scope}</span>
                    </div>
                    <p className="text-sm text-muted-foreground italic">{log.details}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === "agents" && (
            <div className="space-y-3">
              <div className="pb-1">
                <h4 className="font-bold text-foreground text-xs">
                  Federated Institutional Service Matrix
                </h4>
                <p className="text-sm text-muted-foreground">
                  VIGNAN-AI coordinates requests across 12 distributed data sources.
                </p>
              </div>

              <div className="space-y-2">
                {CONNECTED_AGENTS.map((agent) => (
                  <div
                    key={agent.id}
                    className="rounded-xl border border-slate-200 bg-card p-3 shadow-2xs flex items-center justify-between"
                  >
                    <div className="space-y-0.5">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-foreground">{agent.name}</span>
                        
                        {agent.rlsEnforced && (
                          <span className="rounded-full bg-emerald-50 px-1.5 py-0.2 text-xs font-bold text-emerald-700 border border-emerald-200">
                            RLS
                          </span>
                        )}
                      </div>
                      <div className="text-sm text-muted-foreground">{agent.domain}</div>
                      <div className="text-sm text-slate-400 font-mono">{agent.endpoint}</div>
                    </div>

                    <div className="text-right">
                      <span className="inline-flex items-center gap-1 text-sm font-bold text-emerald-600">
                        <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
                        {agent.status}
                      </span>
                      <div className="text-sm text-slate-400 mt-0.5">{agent.lastSync}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
