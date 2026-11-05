"use client";

import React, { useState } from "react";
import {
  X,
  LifeBuoy,
  ShieldCheck,
  Send,
  UserCheck,
  CheckCircle2,
  Clock,
  Sparkles,
  PhoneCall,
  Mail,
} from "lucide-react";
import { CURRENT_STUDENT } from "@/data/student";
import { useLanguage } from "@/context/LanguageContext";
import { useStudent } from "@/context/StudentContext";

interface HumanEscalationModalProps {
  isOpen: boolean;
  contextSummary?: string;
  onClose: () => void;
}

export const HumanEscalationModal: React.FC<HumanEscalationModalProps> = ({
  isOpen,
  contextSummary,
  onClose,
}) => {
  const { studentData } = useStudent();
  const student = studentData?.profile || CURRENT_STUDENT;
  const [escalationReason, setEscalationReason] = useState(
    "Attendance condonation review for Digital Electronics (68%) & Examination seating clarification"
  );
  const [isForwarded, setIsForwarded] = useState(false);
  const { t } = useLanguage();

  if (!isOpen) return null;

  const handleConfirmHandoff = () => {
    setIsForwarded(true);
  };

  return (
    <div role="dialog" aria-modal="true" className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-xs p-4">
      <div className="relative w-full max-w-lg rounded-xl bg-card p-6 shadow-2xl border border-slate-200">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-violet-100 text-violet-700">
              <LifeBuoy className="h-4 w-4" />
            </div>
            <div>
              <h3 className="text-base font-bold text-foreground">
                {t.humanEscalationTitle}
              </h3>
              <p className="text-sm text-muted-foreground">
                {t.humanEscalationSub}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="rounded-full p-1.5 text-slate-400 hover:bg-muted transition-colors cursor-pointer"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {isForwarded ? (
          <div className="py-6 text-center space-y-4">
            <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-emerald-100 text-emerald-600">
              <CheckCircle2 className="h-8 w-8" />
            </div>
            <div>
              <h4 className="text-lg font-bold text-foreground">
                Escalation Ticket #ESC-4029 Dispatched
              </h4>
              <p className="text-xs text-muted-foreground mt-1 leading-relaxed max-w-sm mx-auto">
                Your conversation history, attendance metrics (68% Digital Electronics), and verified profile have been forwarded to Student Support. You will not need to repeat your issue.
              </p>
            </div>

            <div className="rounded-lg bg-muted/50 p-4 border border-slate-200 text-left text-xs space-y-1.5 text-foreground">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Assigned Officer:</span>
                <span className="font-bold text-foreground">Mr. R. Raghavan (Senior Academic Counselor)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Response Window:</span>
                <span className="font-bold text-blue-700">{t.within30Min || "Within 30 Minutes"}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Contact Method:</span>
                <span>{t.directCallback || "Direct Callback & Institutional Email"}</span>
              </div>
            </div>

            <button
              onClick={onClose}
              className="w-full rounded-xl bg-slate-900 py-2.5 text-xs font-semibold text-white hover:bg-slate-800 transition-colors cursor-pointer"
            >
              Close Window
            </button>
          </div>
        ) : (
          <div className="space-y-4 pt-4 text-xs">
            <div className="rounded-lg bg-blue-50/70 p-3.5 border border-blue-100 space-y-1 text-foreground">
              <div className="font-bold text-blue-950 flex items-center gap-1.5">
                <ShieldCheck className="h-4 w-4 text-blue-600" />
                <span>{t.zeroRepeatGuarantee || "Zero-Repeat Context Transfer Guarantee"}</span>
              </div>
              <p className="text-sm text-muted-foreground leading-relaxed">
                Your conversation and relevant context have been forwarded to Student Support so you do not need to repeat your issue.
              </p>
            </div>

            <div className="rounded-xl bg-muted/50 p-3 border border-slate-200 space-y-1.5 font-medium text-foreground">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Student:</span>
                <span className="font-bold text-foreground">
                  {student.name} ({student.id})
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Department:</span>
                <span>{student.department}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Faculty Advisor:</span>
                <span>{student.mentor.name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Priority:</span>
                <span className="font-bold text-amber-700">High (Academic Debarment Risk)</span>
              </div>
            </div>

            <div>
              <label className="block font-bold text-foreground mb-1">
                Reason & Context Summary
              </label>
              <textarea
                rows={3}
                value={contextSummary || escalationReason}
                onChange={(e) => setEscalationReason(e.target.value)}
                className="w-full rounded-xl border border-slate-200 bg-card p-2.5 text-xs text-foreground focus:border-blue-500 focus:outline-hidden"
              />
            </div>

            <div className="flex justify-end gap-2 pt-2 border-t border-slate-100">
              <button
                type="button"
                onClick={onClose}
                className="rounded-xl border border-slate-200 bg-card px-4 py-2 text-xs font-semibold text-muted-foreground hover:bg-muted/50 cursor-pointer"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleConfirmHandoff}
                className="flex items-center gap-1.5 rounded-xl bg-violet-600 px-5 py-2 text-xs font-semibold text-white shadow-xs hover:bg-violet-700 cursor-pointer"
              >
                <Send className="h-3.5 w-3.5" />
                <span>{t.forwardContextConnect || "Forward Context & Connect"}</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
