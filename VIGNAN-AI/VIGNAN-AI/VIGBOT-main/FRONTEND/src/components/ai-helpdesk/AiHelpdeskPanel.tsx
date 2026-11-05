"use client";

import React, { useRef, useEffect } from "react";
import {
  Send,
  Bot,
  User,
  ShieldCheck,
  ArrowUpRight,
  RotateCcw,
  Zap,
  Sparkles,
  Mic,
  MicOff,
  PhoneCall,
  HeartHandshake,
  LifeBuoy,
  Phone,
  Stethoscope,
  MapPin,
  CalendarClock,
  Armchair,
  Lightbulb,
  X,
  Maximize2,
  Minimize2,
  ChevronDown,
  ChevronUp,
  ThumbsUp,
  ThumbsDown,
  Check,
  Cpu,
  Cloud,
  FileText,
  SlidersHorizontal,
} from "lucide-react";
import {
  StructuredCardData,
  ConversationTurn,
} from "@/lib/ai-engine";
import { apiClient } from "@/lib/api-client";
import { CURRENT_STUDENT } from "@/data/student";
import { QuickActionChips } from "@/components/quick-actions/QuickActionChips";
import { Badge } from "@/components/ui/badge";
import { MarkdownText } from "@/components/ui/markdown-text";
import { cn } from "@/lib/utils";
import { useAgentChat } from "@/context/AgentChatContext";
import { useLanguage } from "@/context/LanguageContext";
import { useStudent } from "@/context/StudentContext";

const InteractiveAttendanceCard = ({ card, tone, onOpenServiceModal, onNavigateTab }: any) => {
  const [simulatedClasses, setSimulatedClasses] = React.useState(0);
  const data = card.data || {};
  
  const calculateSimulatedPct = () => {
    let held = Number(data.classesHeld || 40);
    let attended = Number(data.classesAttended || 29);
    
    if (data.current_attendance) {
      const current = parseFloat(data.current_attendance.replace('%', ''));
      held = 100;
      attended = current;
    }
    
    const newHeld = held + simulatedClasses;
    const newAtt = attended + simulatedClasses;
    return Math.min(100, Math.round((newAtt / newHeld) * 100));
  };
  
  const currentPct = parseFloat(String(data.currentPct || data.current_attendance || "75").replace('%', ''));
  const targetPct = 75;

  return (
    <div className={cn("mt-3 rounded-lg border p-4 shadow-xs", tone.border, tone.bg)}>
      <div className="flex flex-wrap items-center gap-2 mb-2">
        <Badge variant={tone.badge} className="whitespace-normal text-left">{card.badge}</Badge>
        <span className="text-xs font-bold text-slate-900">{card.title}</span>
      </div>
      <p className="text-xs text-slate-700 mb-3 font-medium">{card.subtitle}</p>
      
      <div className="grid grid-cols-2 gap-2 mb-4">
        <div className="rounded-lg bg-card p-2.5 border border-slate-200">
          <div className="text-xs text-muted-foreground">{data.current_cgpa ? "Current CGPA" : "Current Pct"}</div>
          <div className="font-bold text-slate-800">{data.current_cgpa || `${currentPct.toFixed(1)}%`}</div>
        </div>
        <div className="rounded-lg bg-card p-2.5 border border-slate-200">
          <div className="text-xs text-muted-foreground">{data.attendance_buffer ? "Buffer" : "Needed"}</div>
          <div className="font-bold text-slate-800 text-[11px] leading-tight mt-1">{data.attendance_buffer || `Next ${data.classesNeeded || 0} classes`}</div>
        </div>
      </div>

      <div className="mb-4 bg-white rounded-lg p-3 border border-slate-200 shadow-sm">
        <div className="flex justify-between items-center mb-2">
          <span className="text-[11px] font-bold text-slate-700 flex items-center gap-1">
             <SlidersHorizontal className="w-3 h-3 text-slate-500" />
             Attendance Recovery Simulator
          </span>
          <span className="text-[10px] font-mono text-slate-600 font-bold">Target: {targetPct}%</span>
        </div>
        
        <input
          type="range"
          min="0"
          max="15"
          value={simulatedClasses}
          onChange={(e) => setSimulatedClasses(parseInt(e.target.value))}
          className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-slate-600 mb-2"
        />
        
        <div className="flex justify-between items-center bg-slate-50 rounded p-1.5 border border-slate-100">
          <span className="text-[11px] text-slate-600">+ {simulatedClasses} classes</span>
          <span className="text-xs font-bold text-slate-900">{calculateSimulatedPct()}%</span>
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        {card.actionLabel && (
          <button
            onClick={() => {
              if (card.actionIntent?.startsWith("view:")) onNavigateTab(card.actionIntent.split(":")[1]);
              else onOpenServiceModal(card.actionIntent);
            }}
            className={cn("flex items-center gap-1 rounded-lg text-white px-3 py-1.5 text-xs font-semibold transition-colors shadow-xs cursor-pointer", tone.button)}
          >
            <span>{card.actionLabel}</span>
            <ArrowUpRight className="h-3.5 w-3.5" />
          </button>
        )}
        <button
          onClick={() => onOpenServiceModal("GRIEVANCE")}
          className="flex items-center gap-1 rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-[11px] font-semibold text-slate-700 transition-colors shadow-xs cursor-pointer hover:bg-slate-50"
        >
          <span>Create Grievance</span>
          <FileText className="h-3.5 w-3.5 text-rose-500" />
        </button>
        <button
          onClick={() => onOpenServiceModal("BONAFIDE_CERTIFICATE")}
          className="flex items-center gap-1 rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-[11px] font-semibold text-slate-700 transition-colors shadow-xs cursor-pointer hover:bg-slate-50"
        >
          <span>Request Document</span>
          <FileText className="h-3.5 w-3.5 text-emerald-500" />
        </button>
      </div>
    </div>
  );
};

export interface AiHelpdeskPanelProps {
  onNavigateTab: (tab: string) => void;
  onOpenServiceModal: (category?: string) => void;
  onOpenEscalation: (summary?: string) => void;
  onTriggerDistressSupport: () => void;
  /** Visual variant: 'central' for Home hero, 'side' for contextual panel, 'maximized' for fullscreen modal */
  variant?: "central" | "side" | "maximized";
  /** Renders as a full-height docked panel (backwards compatible prop). */
  fillHeight?: boolean;
  /** Shown as a close button in the header when the panel is a dismissible overlay. */
  onClose?: () => void;
}

export const AiHelpdeskPanel: React.FC<AiHelpdeskPanelProps> = ({
  onNavigateTab,
  onOpenServiceModal,
  onOpenEscalation,
  onTriggerDistressSupport,
  variant,
  fillHeight = false,
  onClose,
}) => {
  const effectiveVariant: "central" | "side" | "maximized" =
    variant || (fillHeight ? "side" : "central");

  const {
    messages,
    inputQuery,
    setInputQuery,
    isTyping,
    isListening,
    setIsMaximized,
    handleSend,
    handleResetChat,
    handleSpeechToggle,
    registerDistressCallback,
  } = useAgentChat();

  const { t, language } = useLanguage();
  const { studentData } = useStudent();
  const student = studentData?.profile || CURRENT_STUDENT;
  const tr = t;
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const isFirstRender = useRef(true);

  useEffect(() => {
    registerDistressCallback(onTriggerDistressSupport);
  }, [onTriggerDistressSupport, registerDistressCallback]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  };

  useEffect(() => {
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }
    scrollToBottom();
  }, [messages, isTyping]);

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSend();
  };

  const [feedbackState, setFeedbackState] = React.useState<Record<number, "up" | "down">>({});
  const [feedbackSubmitting, setFeedbackSubmitting] = React.useState<Record<number, boolean>>({});
  const [showQuickActions, setShowQuickActions] = React.useState(true);
  const [verifyingTurn, setVerifyingTurn] = React.useState<ConversationTurn | null>(null);

  const handleFeedback = async (
    index: number,
    rating: "up" | "down",
    turn: ConversationTurn
  ) => {
    if (feedbackSubmitting[index]) return;
    setFeedbackSubmitting((prev) => ({ ...prev, [index]: true }));
    setFeedbackState((prev) => ({ ...prev, [index]: rating }));

    const contextMsgs = messages.slice(0, index + 1).map((m) => ({
      role: m.role,
      content: m.content,
    }));

    try {
      await apiClient.sendFeedback(
        turn.conversationId,
        turn.messageId,
        rating,
        undefined,
        contextMsgs,
        turn.content
      );
    } catch (e) {
      console.warn("Feedback submission error:", e);
    } finally {
      setFeedbackSubmitting((prev) => ({ ...prev, [index]: false }));
    }
  };

  // Shared visual tone tokens per card type
  const cardTone = {
    attendance: {
      border: "border-amber-200",
      bg: "bg-amber-50/50",
      badge: "warning" as const,
      button: "bg-amber-700 hover:bg-amber-800",
      tile: "border-amber-100",
    },
    exam: {
      border: "border-blue-200",
      bg: "bg-blue-50/50",
      badge: "primary" as const,
      button: "bg-blue-600 hover:bg-blue-700",
      tile: "border-blue-100",
    },
    fee: {
      border: "border-amber-200",
      bg: "bg-amber-50/40",
      badge: "warning" as const,
      button: "bg-slate-900 hover:bg-slate-800",
      tile: "border-slate-200",
    },
    curriculum: {
      border: "border-cyan-200",
      bg: "bg-cyan-50/40",
      badge: "info" as const,
      button: "bg-cyan-700 hover:bg-cyan-800",
      tile: "border-cyan-100",
    },
    service: {
      border: "border-indigo-200",
      bg: "bg-indigo-50/50",
      badge: "info" as const,
      button: "bg-indigo-600 hover:bg-indigo-700",
      tile: "border-indigo-100",
    },
    academicRoadmap: {
      border: "border-emerald-200",
      bg: "bg-emerald-50/50",
      badge: "success" as const,
      button: "bg-emerald-600 hover:bg-emerald-700",
      tile: "border-emerald-100",
    }
  };

  // Render structured interactive card
  const renderStructuredCard = (card: StructuredCardData) => {
    if (card.type === "distress") {
      return (
        <div className="mt-3 rounded-lg border-2 border-rose-200 bg-rose-50/90 p-4 shadow-sm">
          <div className="flex items-center gap-2 text-rose-700 font-bold text-xs uppercase tracking-wider mb-2">
            <HeartHandshake className="h-4 w-4 text-rose-600" />
            <span>{card.badge}</span>
          </div>
          <h4 className="text-sm font-bold text-rose-950">{card.title}</h4>
          <p className="text-xs text-rose-800 mt-1 mb-3">{card.subtitle}</p>
          <div className="rounded-xl bg-card p-3 border border-rose-200 text-xs text-rose-900 space-y-1.5 mb-3 font-medium">
            <div className="flex items-center gap-1.5">
              <Phone className="h-3.5 w-3.5 shrink-0 text-rose-600" />
              24/7 Helpline: <strong>1800-599-0019</strong>
            </div>
            <div className="flex items-center gap-1.5">
              <Stethoscope className="h-3.5 w-3.5 shrink-0 text-rose-600" />
              Counselor: <strong>Dr. Ananya Roy (Lead Student Psychologist)</strong>
            </div>
            <div className="flex items-center gap-1.5">
              <MapPin className="h-3.5 w-3.5 shrink-0 text-rose-600" />
              Location: <strong>{t.wellnessCenter || "Student Wellness Center, Health Block Room 104"}</strong>
            </div>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={onTriggerDistressSupport}
              className="flex items-center gap-1.5 rounded-xl bg-rose-600 px-3.5 py-1.5 text-xs font-bold text-white shadow-xs hover:bg-rose-700 transition-colors cursor-pointer"
            >
              <PhoneCall className="h-3.5 w-3.5" />
              <span>{t.connectCounselor}</span>
            </button>
            <button
              onClick={() => onOpenEscalation("Student experiencing extreme stress and academic pressure")}
              className="flex items-center gap-1.5 rounded-xl bg-card border border-rose-300 px-3 py-1.5 text-xs font-semibold text-rose-700 hover:bg-rose-50 transition-colors cursor-pointer"
            >
              <span>{t.talkToHuman}</span>
            </button>
          </div>
        </div>
      );
    }

    if (card.type === "attendance" || card.type === "ACADEMIC_ROADMAP" || card.type === "ACADEMIC_ADVISING_PLAN") {
      const tone = card.type === "attendance" ? cardTone.attendance : cardTone.academicRoadmap;
      return <InteractiveAttendanceCard key={card.title} card={card} tone={tone} onOpenServiceModal={onOpenServiceModal} onNavigateTab={onNavigateTab} />;
    }

    if (card.type === "FACULTY_CONTACT") {
      const tone = cardTone.curriculum;
      const data = card.data as Record<string, any>;
      return (
        <div className={cn("mt-3 rounded-lg border p-4 shadow-xs", tone.border, tone.bg)}>
          <div className="flex flex-wrap items-center gap-2 mb-2">
            <Badge variant={tone.badge} className="whitespace-normal text-left">{card.badge}</Badge>
            <span className="text-xs font-bold text-cyan-950">{card.title}</span>
          </div>
          <p className="text-xs text-cyan-900/90 mb-3 font-medium">{card.subtitle}</p>
          
          <div className="space-y-2 mb-4">
            {Object.entries(data).map(([role, info]: [string, any]) => (
              <div key={role} className="flex justify-between items-center rounded-lg bg-card p-2 border border-cyan-100 shadow-sm text-xs">
                <span className="font-semibold text-cyan-800 capitalize">{role.replace('_', ' ')}</span>
                <span className="text-slate-600">{info?.name}</span>
              </div>
            ))}
          </div>

          {card.actionLabel && (
            <button
              onClick={() => onOpenServiceModal(card.actionIntent)}
              className={cn("flex items-center gap-1 rounded-lg text-white px-3 py-1.5 text-xs font-semibold transition-colors shadow-xs cursor-pointer", tone.button)}
            >
              <span>{card.actionLabel}</span>
              <ArrowUpRight className="h-3.5 w-3.5" />
            </button>
          )}
        </div>
      );
    }

    if (card.type === "exam") {
      const data = card.data as Record<string, unknown>;
      const examsList = Array.isArray(data.exams) ? (data.exams as any[]) : [];
      const firstExam = examsList[0] || {};
      const examDate = (data.date && data.date !== "undefined") ? String(data.date) : (firstExam.exam_date || "18 Sep 2026");
      const examTime = (data.time && data.time !== "undefined") ? String(data.time) : (firstExam.time || "10:00 AM");
      const examVenue = (data.venue && data.venue !== "undefined") ? String(data.venue) : (firstExam.venue || "Examination Hall (N-312 / N-Block)");
      const seating = (data.seating && data.seating !== "undefined") ? String(data.seating) : (firstExam.hall_ticket_status || "Hall Ticket Allocated");
      const tone = cardTone.exam;
      return (
        <div className={cn("mt-3 rounded-lg border p-4 shadow-xs", tone.border, tone.bg)}>
          <div className="flex flex-wrap items-center gap-2 mb-2">
            <Badge variant={tone.badge} className="whitespace-normal text-left">{card.badge}</Badge>
            <span className="text-xs font-mono font-bold text-blue-700">7 {t.daysRemaining}</span>
          </div>
          <h4 className="text-sm font-bold text-foreground">{card.title}</h4>
          <div className={cn("my-2 rounded-xl bg-card p-2.5 border text-xs space-y-1.5 text-foreground", tone.tile)}>
            <div className="flex items-center gap-1.5">
              <CalendarClock className="h-3.5 w-3.5 shrink-0 text-blue-600" />
              Date & Time: <strong>{String(examDate)} at {String(examTime)}</strong>
            </div>
            <div className="flex items-center gap-1.5">
              <MapPin className="h-3.5 w-3.5 shrink-0 text-blue-600" />
              Examination Venue: <strong>{String(examVenue)}</strong>
            </div>
            <div className="flex items-center gap-1.5">
              <Armchair className="h-3.5 w-3.5 shrink-0 text-blue-600" />
              Seating Allocation: <strong>{String(seating)}</strong>
            </div>
          </div>
          <button
            onClick={() => onNavigateTab("exams")}
            className={cn("flex items-center gap-1 rounded-lg text-white px-3 py-1.5 text-xs font-semibold transition-colors shadow-xs cursor-pointer", tone.button)}
          >
            <span>{tr.viewExamSchedule}</span>
            <ArrowUpRight className="h-3.5 w-3.5" />
          </button>
        </div>
      );
    }

    if (card.type === "fee") {
      const data = card.data as Record<string, unknown>;
      const tone = cardTone.fee;
      return (
        <div className={cn("mt-3 rounded-lg border p-4 shadow-xs", tone.border, tone.bg)}>
          <div className="flex flex-wrap items-center gap-x-2 gap-y-1 mb-2">
            <Badge variant={tone.badge} className="whitespace-normal text-left">{card.badge}</Badge>
            <span className="text-xs font-bold text-amber-900">Due: {String(data.dueDate)}</span>
          </div>
          <div className="grid grid-cols-2 gap-2 my-2 text-xs">
            <div className={cn("rounded-lg bg-card p-2.5 border", tone.tile)}>
              <div className="text-sm text-muted-foreground">{t.totalFees}</div>
              <div className="font-bold text-foreground">{String(data.demand)}</div>
            </div>
            <div className={cn("rounded-lg bg-card p-2.5 border", tone.tile)}>
              <div className="text-sm text-muted-foreground">{t.amountPaid}</div>
              <div className="font-bold text-emerald-600">{String(data.paid)}</div>
            </div>
          </div>
          <button
            onClick={() => onNavigateTab("fees")}
            className={cn("flex items-center gap-1 rounded-lg text-white px-3 py-1.5 text-xs font-semibold transition-colors shadow-xs cursor-pointer", tone.button)}
          >
            <span>{t.navFees}</span>
            <ArrowUpRight className="h-3.5 w-3.5" />
          </button>
        </div>
      );
    }

    if (card.type === "curriculum") {
      const tone = cardTone.curriculum;
      return (
        <div className={cn("mt-3 rounded-lg border p-4 shadow-xs", tone.border, tone.bg)}>
          <div className="flex flex-wrap items-center gap-2 mb-2">
            <Badge variant={tone.badge} className="whitespace-normal text-left">{card.badge}</Badge>
            <span className="text-xs font-bold text-cyan-900">Progress: 60%</span>
          </div>
          <p className="text-xs text-foreground mb-3 font-medium">
            You have earned <strong>72 of 120 required credits</strong>. Current semester load is 24 credits, leaving 24 credits remaining across Semesters 6, 7 & 8.
          </p>
          <button
            onClick={() => onNavigateTab("curriculum")}
            className={cn("flex items-center gap-1 rounded-lg text-white px-3 py-1.5 text-xs font-semibold transition-colors shadow-xs cursor-pointer", tone.button)}
          >
            <span>{t.navCurriculum}</span>
            <ArrowUpRight className="h-3.5 w-3.5" />
          </button>
        </div>
      );
    }

    if (card.type === "service") {
      const tone = cardTone.service;
      return (
        <div className={cn("mt-3 rounded-lg border p-4 shadow-xs", tone.border, tone.bg)}>
          <div className="flex flex-wrap items-center gap-2 mb-2">
            <Badge variant={tone.badge} className="whitespace-normal text-left">{card.badge}</Badge>
            <span className="text-xs font-bold text-indigo-950">{card.title}</span>
          </div>
          <p className="text-xs text-indigo-900/90 mb-3">{card.subtitle}</p>
          <button
            onClick={() => onOpenServiceModal()}
            className={cn("flex items-center gap-1 rounded-lg text-white px-3 py-1.5 text-xs font-semibold transition-colors shadow-xs cursor-pointer", tone.button)}
          >
            <span>{t.newServiceRequest}</span>
            <ArrowUpRight className="h-3.5 w-3.5" />
          </button>
        </div>
      );
    }

    if (card.type === "hostel") {
      const data = (card.data || {}) as Record<string, unknown>;
      return (
        <div className="mt-3 rounded-lg border border-blue-200 bg-blue-50/50 p-4 shadow-xs">
          <div className="flex flex-wrap items-center gap-2 mb-2">
            <Badge variant="primary" className="whitespace-normal text-left">{card.badge || "Hostel Resident Portal"}</Badge>
            <span className="text-xs font-bold text-blue-950">{card.title}</span>
          </div>
          <p className="text-xs text-blue-900/90 mb-2 font-medium">{card.subtitle}</p>
          <div className="rounded-lg bg-card p-2.5 border border-blue-100 text-xs text-slate-700 space-y-1 mb-3">
            {Boolean(data.curfew) && <div><strong>Curfew:</strong> {String(data.curfew)}</div>}
            {Boolean(data.messTimings) && <div><strong>Mess Timings:</strong> {String(data.messTimings)}</div>}
            {Boolean(data.outingPass) && <div><strong>Outing Pass:</strong> {String(data.outingPass)}</div>}
            {Boolean(data.wardenContact) && <div><strong>Warden Desk:</strong> {String(data.wardenContact)}</div>}
          </div>
          <button
            onClick={() => onOpenServiceModal("Hostel Outing Pass")}
            className="flex items-center gap-1 rounded-lg text-white px-3 py-1.5 text-xs font-semibold bg-blue-600 hover:bg-blue-700 transition-colors shadow-xs cursor-pointer"
          >
            <span>{card.actionLabel || "Apply Outing Pass"}</span>
            <ArrowUpRight className="h-3.5 w-3.5" />
          </button>
        </div>
      );
    }

    if (card.type === "transport") {
      const data = (card.data || {}) as Record<string, unknown>;
      const routes = Array.isArray(data.routes) ? data.routes : [];
      return (
        <div className="mt-3 rounded-lg border border-emerald-200 bg-emerald-50/50 p-4 shadow-xs">
          <div className="flex flex-wrap items-center gap-2 mb-2">
            <Badge variant="success" className="whitespace-normal text-left">{card.badge || "Active Fleet"}</Badge>
            <span className="text-xs font-bold text-emerald-950">{card.title}</span>
          </div>
          <p className="text-xs text-emerald-900/90 mb-2 font-medium">{card.subtitle}</p>
          <div className="rounded-lg bg-card p-2.5 border border-emerald-100 text-xs text-slate-700 space-y-1 mb-3">
            {routes.length > 0 && (
              <div>
                <strong>Active Bus Routes:</strong>
                <ul className="list-disc list-inside mt-0.5 space-y-0.5 text-slate-600">
                  {routes.map((r, i) => <li key={i}>{String(r)}</li>)}
                </ul>
              </div>
            )}
            {Boolean(data.deskLocation) && <div><strong>Transport Desk:</strong> {String(data.deskLocation)}</div>}
            {Boolean(data.contact) && <div><strong>Contact:</strong> {String(data.contact)}</div>}
          </div>
          <button
            onClick={() => onOpenServiceModal("Bus Pass Endorsement")}
            className="flex items-center gap-1 rounded-lg text-white px-3 py-1.5 text-xs font-semibold bg-emerald-600 hover:bg-emerald-700 transition-colors shadow-xs cursor-pointer"
          >
            <span>{card.actionLabel || "Request Bus Pass"}</span>
            <ArrowUpRight className="h-3.5 w-3.5" />
          </button>
        </div>
      );
    }

    if (card.type === "circulars") {
      const data = (card.data || {}) as Record<string, unknown>;
      const notices = Array.isArray(data.latestNotices) ? data.latestNotices : [];
      return (
        <div className="mt-3 rounded-lg border border-cyan-200 bg-cyan-50/50 p-4 shadow-xs">
          <div className="flex flex-wrap items-center gap-2 mb-2">
            <Badge variant="info" className="whitespace-normal text-left">{card.badge || "Official Notices"}</Badge>
            <span className="text-xs font-bold text-cyan-950">{card.title}</span>
          </div>
          <p className="text-xs text-cyan-900/90 mb-2 font-medium">{card.subtitle}</p>
          {notices.length > 0 && (
            <div className="rounded-lg bg-card p-2.5 border border-cyan-100 text-xs text-slate-700 space-y-1.5 mb-3">
              {notices.map((n: any, i: number) => (
                <div key={i} className="border-b border-slate-100 pb-1 last:border-0 last:pb-0">
                  <div className="font-semibold text-slate-900">{n.title}</div>
                  <div className="text-[11px] text-muted-foreground">Ref: {n.ref} {n.date ? `| Issued: ${n.date}` : ""}</div>
                </div>
              ))}
            </div>
          )}
          <button
            onClick={() => onNavigateTab("circulars")}
            className="flex items-center gap-1 rounded-lg text-white px-3 py-1.5 text-xs font-semibold bg-cyan-700 hover:bg-cyan-800 transition-colors shadow-xs cursor-pointer"
          >
            <span>{t.navCirculars || "View Circulars"}</span>
            <ArrowUpRight className="h-3.5 w-3.5" />
          </button>
        </div>
      );
    }

    if (card.type === "events") {
      const data = (card.data || {}) as Record<string, unknown>;
      const festivals = Array.isArray(data.festivals) ? data.festivals : [];
      return (
        <div className="mt-3 rounded-lg border border-purple-200 bg-purple-50/50 p-4 shadow-xs">
          <div className="flex flex-wrap items-center gap-2 mb-2">
            <Badge variant="primary" className="whitespace-normal text-left bg-purple-600 text-white">{card.badge || "Campus Highlights"}</Badge>
            <span className="text-xs font-bold text-purple-950">{card.title}</span>
          </div>
          <p className="text-xs text-purple-900/90 mb-2 font-medium">{card.subtitle}</p>
          {festivals.length > 0 && (
            <div className="rounded-lg bg-card p-2.5 border border-purple-100 text-xs text-slate-700 space-y-1.5 mb-3">
              {festivals.map((f: any, i: number) => (
                <div key={i} className="flex justify-between items-center text-xs">
                  <span className="font-semibold text-slate-900">{f.name || f.title}</span>
                  <span className="text-[11px] text-purple-700 font-medium">{f.type || f.venue}</span>
                </div>
              ))}
            </div>
          )}
          <button
            onClick={() => onNavigateTab("calendar")}
            className="flex items-center gap-1 rounded-lg text-white px-3 py-1.5 text-xs font-semibold bg-purple-600 hover:bg-purple-700 transition-colors shadow-xs cursor-pointer"
          >
            <span>{card.actionLabel || "View Events Calendar"}</span>
            <ArrowUpRight className="h-3.5 w-3.5" />
          </button>
        </div>
      );
    }

    return null;
  };

  const isFullHeight = effectiveVariant === "side" || effectiveVariant === "maximized";
  const centralMessageHeight = showQuickActions
    ? "h-[270px] sm:h-[300px] md:h-[320px]"
    : "h-[390px] sm:h-[430px] md:h-[460px]";

  return (
    <div
      className={cn(
        "bg-card transition-all",
        effectiveVariant === "central" &&
          "w-full rounded-xl border border-slate-200/90 shadow-md shadow-blue-500/5 overflow-hidden flex flex-col",
        effectiveVariant === "side" &&
          "flex h-full flex-col rounded-none border-0 overflow-hidden",
        effectiveVariant === "maximized" &&
          "flex h-full w-full flex-col rounded-xl overflow-hidden shadow-2xl border border-slate-200"
      )}
    >
      {/* Panel Header */}
      {effectiveVariant === "side" ? (
        /* Side Panel Header: 2 clean rows to prevent any overlap */
        <div className="border-b border-slate-100 bg-gradient-to-r from-blue-50/80 via-indigo-50/40 to-white px-3.5 py-3 shrink-0 space-y-2.5">
          {/* Row 1: Bot + Title + VIGNAN-AI | Maximize + Close */}
          <div className="flex items-center justify-between gap-2">
            <div className="flex items-center gap-2 min-w-0">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 text-white shadow-xs">
                <Bot className="h-4 w-4" />
              </div>
              <div className="min-w-0 flex items-center gap-1.5 truncate">
                <h2 className="text-sm font-bold text-foreground truncate">{t.studentHelpdesk || "VIGNAN-AI"}</h2>
                <Badge variant="primary" className="text-xs px-1.5 py-0 bg-blue-600 text-white shrink-0">
                  AI
                </Badge>
              </div>
            </div>

            <div className="flex items-center gap-1 shrink-0">
              {/* Maximize Button */}
              <button
                onClick={() => setIsMaximized(true)}
                className="flex h-8 w-8 items-center justify-center rounded-lg text-muted-foreground hover:bg-muted hover:text-foreground transition-colors cursor-pointer"
                title="Maximize chat to full screen"
                aria-label="Maximize chat"
              >
                <Maximize2 className="h-4 w-4" />
              </button>

              {/* Close Button */}
              {onClose && (
                <button
                  onClick={onClose}
                  className="flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 hover:bg-muted hover:text-foreground transition-colors cursor-pointer"
                  title="Close chat"
                  aria-label="Close chat"
                >
                  <X className="h-4 w-4" />
                </button>
              )}
            </div>
          </div>

          {/* Row 2: Reset + Need human help? */}
          <div className="flex items-center gap-2">
            <button
              onClick={handleResetChat}
              className="flex items-center gap-1.5 rounded-lg border border-slate-200 bg-card px-2.5 py-1 text-xs font-medium text-muted-foreground hover:bg-muted/50 hover:text-foreground transition-colors shadow-2xs cursor-pointer"
              title="Clear context & reset session"
              aria-label="New conversation / Reset"
            >
              <RotateCcw className="h-3 w-3" />
              <span>{tr.resetSession}</span>
            </button>

            <button
              onClick={() => onOpenEscalation()}
              className="flex items-center gap-1.5 rounded-lg border border-indigo-200 bg-indigo-50 px-2.5 py-1 text-xs font-semibold text-indigo-700 hover:bg-indigo-100 transition-colors cursor-pointer"
              title="Connect with Human Student Support"
            >
              <LifeBuoy className="h-3.5 w-3.5 text-indigo-600" />
              <span>{tr.needHumanHelp}</span>
            </button>
          </div>
        </div>
      ) : (
        /* Central & Maximized Header */
        <div
          className={cn(
            "border-b border-slate-100 bg-gradient-to-r from-blue-50/80 via-indigo-50/40 to-white shrink-0",
            effectiveVariant === "central" && "px-4 sm:px-6 py-3 sm:py-3.5",
            effectiveVariant === "maximized" && "px-6 py-4"
          )}
        >
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            {/* Header Title & Branding */}
            <div className="flex items-center gap-3 min-w-0">
              <div
                className={cn(
                  "flex shrink-0 items-center justify-center rounded-lg bg-gradient-to-tr from-blue-600 to-indigo-600 text-white shadow-sm shadow-blue-500/20",
                  effectiveVariant === "central" ? "h-10 w-10" : "h-10 w-10"
                )}
              >
                <Bot className="h-5 w-5" />
              </div>
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-2">
                  <h2 className="text-sm sm:text-base font-bold text-foreground truncate">
                    VIGNAN-AI
                  </h2>
                  <Badge variant="primary" className="bg-blue-600 text-white font-semibold">
                    AI
                  </Badge>
                  <span className="hidden md:inline-flex items-center gap-1 rounded-full bg-emerald-50 border border-emerald-200/80 px-2.5 py-0.5 text-sm font-medium text-emerald-700">
                    <ShieldCheck className="h-3 w-3 text-emerald-600" />
                    RLS Verified: {student.id}
                  </span>
                </div>
                {effectiveVariant === "central" && (
                  <p className="text-xs text-muted-foreground font-normal mt-0.5 truncate sm:whitespace-normal">
                    Primary conversational access to academic records, attendance, exams, fees & institutional policies.
                  </p>
                )}
              </div>
            </div>

            {/* Header Action Buttons */}
            <div className="flex items-center gap-1.5 sm:gap-2 shrink-0">
              {/* Reset */}
              <button
                onClick={handleResetChat}
                className="flex items-center gap-1.5 rounded-lg border border-slate-200 bg-card px-2.5 py-1.5 text-xs font-medium text-muted-foreground hover:bg-muted/50 hover:text-foreground transition-colors shadow-xs cursor-pointer"
                title="Clear context & start new conversation"
                aria-label="New conversation / Reset"
              >
                <RotateCcw className="h-3.5 w-3.5" />
                <span>{tr.resetSession}</span>
              </button>

              {/* Maximize Button (shown on Central) */}
              {effectiveVariant === "central" && (
                <button
                  onClick={() => setIsMaximized(true)}
                  className="flex items-center gap-1.5 rounded-lg border border-slate-200 bg-card px-2.5 py-1.5 text-xs font-medium text-muted-foreground hover:bg-muted/50 hover:text-foreground transition-colors shadow-xs cursor-pointer"
                  title="Maximize chat to expanded workspace"
                  aria-label="Maximize chat"
                >
                  <Maximize2 className="h-3.5 w-3.5 text-muted-foreground" />
                  <span>{t.maximize || "Maximize"}</span>
                </button>
              )}

              {/* Restore Button (shown when Maximized) */}
              {effectiveVariant === "maximized" && (
                <button
                  onClick={() => setIsMaximized(false)}
                  className="flex items-center gap-1.5 rounded-lg border border-slate-200 bg-card px-2.5 py-1.5 text-xs font-medium text-foreground hover:bg-muted/50 hover:text-foreground transition-colors shadow-xs cursor-pointer"
                  title="Restore chat to regular view (Esc)"
                  aria-label="Restore chat"
                >
                  <Minimize2 className="h-3.5 w-3.5 text-muted-foreground" />
                  <span>{tr.restoreSession}</span>
                </button>
              )}

              {/* Need human help */}
              <button
                onClick={() => onOpenEscalation()}
                className="flex items-center gap-1.5 rounded-lg border border-indigo-200 bg-indigo-50 px-2.5 py-1.5 text-xs font-semibold text-indigo-700 hover:bg-indigo-100 transition-colors cursor-pointer"
                title="Connect with Human Student Services"
              >
                <LifeBuoy className="h-3.5 w-3.5 text-indigo-600" />
                <span className="hidden md:inline">{tr.needHumanHelp}</span>
                <span className="md:hidden">{t.help || "Help"}</span>
              </button>

              {/* Close button for Maximized */}
              {effectiveVariant === "maximized" && (
                <button
                  onClick={() => setIsMaximized(false)}
                  className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-slate-400 hover:bg-muted hover:text-foreground transition-colors cursor-pointer"
                  title="Close expanded chat (Esc)"
                  aria-label="Close expanded chat"
                >
                  <X className="h-4 w-4" />
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Messages Scroll View */}
      <div
        className={cn(
          "overflow-y-auto overscroll-contain space-y-4 bg-muted/50/50",
          effectiveVariant === "central" && `${centralMessageHeight} p-4 sm:p-5`,
          effectiveVariant === "side" && "flex-1 min-h-0 p-4",
          effectiveVariant === "maximized" && "flex-1 min-h-0 p-6"
        )}
      >
        {messages.map((turn, index) => {
          const isUser = turn.role === "user";
          return (
            <div
              key={index}
              className={cn(
                "flex gap-2.5",
                isFullHeight ? "max-w-[92%]" : "max-w-5xl w-full",
                isUser ? "ml-auto flex-row-reverse" : "mr-auto"
              )}
            >
              {/* Avatar Icon */}
              <div
                className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-xl text-xs font-bold ${
                  isUser
                    ? "bg-slate-700 text-white"
                    : "bg-gradient-to-tr from-blue-600 to-indigo-600 text-white shadow-xs"
                }`}
              >
                {isUser ? <User className="h-3.5 w-3.5" /> : <Bot className="h-3.5 w-3.5" />}
              </div>

              {/* Message Bubble */}
              <div
                className={cn(
                  "min-w-0 rounded-lg px-3.5 py-2.5 text-sm leading-relaxed",
                  isUser
                    ? "bg-blue-600 text-white shadow-xs rounded-tr-sm"
                    : "bg-card border border-slate-200 text-foreground shadow-xs rounded-tl-sm"
                )}
              >
                {/* Main Message Content */}
                <MarkdownText
                  text={turn.content}
                  className={isUser ? "text-white" : "text-foreground"}
                />

                {/* Redirect Button */}
                {!isUser && turn.responseMeta?.redirect_path && (
                  <div className="mt-3">
                    <button
                      onClick={() => onNavigateTab((turn.responseMeta?.action?.target || turn.responseMeta!.redirect_path) as any)}
                      className="flex items-center gap-1.5 rounded-lg bg-blue-100 px-3 py-1.5 text-xs font-semibold text-blue-700 hover:bg-blue-200 transition-colors shadow-xs cursor-pointer"
                    >
                      <ArrowUpRight className="h-3.5 w-3.5" />
                      <span>{turn.responseMeta.action?.label || `Go to ${turn.responseMeta.redirect_path}`}</span>
                    </button>
                  </div>
                )}

                {/* Structured Cards (Attendance, Exams, Fees, etc.) */}
                {!isUser && turn.responseMeta?.structuredCard && (
                  renderStructuredCard(turn.responseMeta.structuredCard)
                )}

                {/* Thumbs Feedback & Architecture Telemetry Badge */}
                {!isUser && (
                  <div className="mt-2.5 pt-2 border-t border-slate-100 flex flex-wrap items-center justify-between gap-2 text-xs">
                    <div className="flex items-center gap-2">
                      {/* Live routed_by Telemetry Badge & Verifier Trigger */}
                      <button
                        type="button"
                        onClick={() => setVerifyingTurn(turn)}
                        title="Click to inspect live inference tier, privacy redaction and model verification"
                        className={cn(
                          "inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-semibold transition-all border cursor-pointer",
                          turn.responseMeta?.routed_by === "learned_remediation"
                            ? "bg-violet-50 text-violet-700 border-violet-300 hover:bg-violet-100 shadow-2xs"
                            : turn.responseMeta?.routed_by === "gemini"
                            ? "bg-purple-50 text-purple-700 border-purple-200 hover:bg-purple-100"
                            : turn.responseMeta?.routed_by === "classifier" || turn.responseMeta?.routed_by === "classifier_pipeline_test"
                            ? "bg-emerald-50 text-emerald-700 border-emerald-200 hover:bg-emerald-100"
                            : "bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100"
                        )}
                      >
                        <Cpu className="h-3 w-3" />
                        <span>
                          {(() => {
                            const rBy = turn.responseMeta?.routed_by;
                            const modelId = turn.responseMeta?.model_used || "Cloud LLM";
                            if (rBy === "learned_remediation") return "Cognitive Remediation: Self-Learned Rule";
                            if (rBy === "rules") return "Tier 1: Deterministic Guardrail & Rules";
                            if (rBy === "classifier" || rBy === "classifier_pipeline_test") return "Tier 2: Local ML Intent Classifier (TF-IDF + LR)";
                            if (rBy === "gemini" || rBy === "groq" || turn.responseMeta?.llm_provider === "gemini" || turn.responseMeta?.llm_provider === "groq") {
                              return `Tier 3: Cloud LLM Fallback (${modelId}, PII-Redacted)`;
                            }
                            return "Tier 1: Deterministic Guardrail & Rules";
                          })()}
                        </span>
                      </button>

                      <div className="flex items-center gap-1">
                        <span className="text-[11px] text-slate-400 font-medium">Helpful?</span>
                        <button
                          onClick={() => handleFeedback(index, "up", turn)}
                          disabled={feedbackSubmitting[index]}
                          title="Thumbs up: Helpful response"
                          className={cn(
                            "inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium transition-all cursor-pointer",
                            feedbackState[index] === "up"
                              ? "bg-emerald-100 text-emerald-800 border border-emerald-300 font-semibold"
                              : "hover:bg-slate-100 text-slate-500 hover:text-slate-800 border border-slate-200"
                          )}
                        >
                          <ThumbsUp className={cn("h-3 w-3", feedbackState[index] === "up" && "fill-emerald-600 text-emerald-600")} />
                          <span>👍</span>
                        </button>

                        <button
                          onClick={() => handleFeedback(index, "down", turn)}
                          disabled={feedbackSubmitting[index]}
                          title="Thumbs down: Mark response as not helpful"
                          className={cn(
                            "inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium transition-all cursor-pointer",
                            feedbackState[index] === "down"
                              ? "bg-rose-100 text-rose-800 border border-rose-300 font-semibold"
                              : "hover:bg-slate-100 text-slate-500 hover:text-slate-800 border border-slate-200"
                          )}
                        >
                          <ThumbsDown className={cn("h-3 w-3", feedbackState[index] === "down" && "fill-rose-600 text-rose-600")} />
                          <span>👎</span>
                        </button>
                      </div>
                    </div>

                    {feedbackState[index] === "up" && (
                      <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full animate-in fade-in duration-200">
                        <Check className="h-2.5 w-2.5 text-emerald-600" />
                        Feedback recorded
                      </span>
                    )}
                    {feedbackState[index] === "down" && (
                      <span className="inline-flex items-center gap-1 text-[10px] font-medium text-slate-500 bg-slate-50 border border-slate-200 px-2 py-0.5 rounded-full">
                        Feedback recorded
                      </span>
                    )}

                  </div>
                )}

                {/* Suggested Follow-up chips */}
                {!isUser && turn.responseMeta?.suggestedFollowUps && (
                  <div className="mt-3 pt-2.5 border-t border-slate-100">
                    <div className="text-sm font-bold uppercase tracking-wider text-slate-400 mb-2">
                      Suggested follow-ups:
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {turn.responseMeta.suggestedFollowUps.map((prompt, pIdx) => (
                        <button
                          key={pIdx}
                          onClick={() => handleSend(prompt, "3B")}
                          className="rounded-lg border border-slate-200 bg-muted/50 px-2.5 py-1.5 text-xs font-medium text-foreground hover:border-blue-300 hover:bg-blue-50 hover:text-blue-700 transition-colors cursor-pointer text-left"
                        >
                          {prompt}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {/* Typing indicator */}
        {isTyping && (
          <div className="flex gap-3 max-w-xl mr-auto">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 text-white shadow-xs">
              <Bot className="h-4 w-4" />
            </div>
            <div className="rounded-lg rounded-tl-sm border border-slate-200 bg-card px-4 py-3 shadow-xs">
              <div className="flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-blue-600 animate-bounce" />
                <span className="h-2 w-2 rounded-full bg-indigo-600 animate-bounce [animation-delay:0.2s]" />
                <span className="h-2 w-2 rounded-full bg-blue-400 animate-bounce [animation-delay:0.4s]" />
                <span className="ml-2 text-xs font-medium text-muted-foreground">
                  Retrieving authorized record from institutional agents...
                </span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div
        className={cn(
          "border-t border-slate-200/80 bg-card shrink-0",
          effectiveVariant === "central" ? "p-3 sm:p-4 space-y-2" : "p-3 space-y-2"
        )}
      >
        <form onSubmit={handleFormSubmit} className="flex items-center gap-2">
          {/* Real Speech Recognition Mic Button */}
          <button
            type="button"
            onClick={handleSpeechToggle}
            className={cn(
              "relative flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border transition-all cursor-pointer",
              isListening
                ? "border-rose-500 bg-rose-50 text-rose-600 ring-2 ring-rose-400 ring-offset-1 shadow-sm"
                : "border-slate-200 bg-muted/50 text-muted-foreground hover:bg-muted hover:text-foreground"
            )}
            title={isListening ? (tr.micListening || "Listening... speak now") : (tr.micStart || "Click to speak")}
            aria-label={isListening ? "Stop listening" : "Start voice input"}
          >
            {isListening ? (
              <>
                <span className="absolute -top-1 -right-1 flex h-2.5 w-2.5">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75" />
                  <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-rose-500" />
                </span>
                <MicOff className="h-4 w-4 animate-pulse" />
              </>
            ) : (
              <Mic className="h-4 w-4" />
            )}
          </button>

          {/* Text Input */}
          <div className="relative flex-1">
            <input
              ref={inputRef}
              type="text"
              value={inputQuery}
              onChange={(e) => setInputQuery(e.target.value)}
              placeholder={isListening ? (tr.micListening || "Listening... speak now...") : tr.chatPlaceholder}
              className={cn(
                "w-full rounded-xl border px-4 py-2.5 text-sm text-foreground placeholder:text-slate-400 focus:outline-hidden transition-all",
                isListening
                  ? "border-rose-400 bg-rose-50/40 ring-2 ring-rose-100 placeholder:text-rose-600 placeholder:font-medium animate-pulse"
                  : "border-slate-200 bg-muted/50 focus:border-blue-500 focus:bg-card focus:ring-2 focus:ring-blue-100"
              )}
            />
          </div>


          {/* Send Button */}
          <button
            type="submit"
            disabled={!inputQuery.trim() || isTyping}
            className="flex h-10 shrink-0 items-center justify-center gap-1.5 rounded-xl bg-blue-600 w-10 sm:w-auto sm:px-4 text-xs sm:text-sm font-semibold text-white shadow-xs hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all cursor-pointer"
          >
            <span className="hidden sm:inline">{tr.askButton}</span>
            <Send className="h-4 w-4 sm:h-3.5 sm:w-3.5" />
          </button>
        </form>

        {/* Quick Action Chips Bar & Contextual Actions (Uses Fast 3B Model) */}
        <QuickActionChips
          onSelectAction={(query) => handleSend(query, "3B")}
          showActions={showQuickActions}
          onToggleActions={() => setShowQuickActions((visible) => !visible)}
        />
      </div>

      {/* AI Model Verification Modal */}
      {verifyingTurn && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4 animate-in fade-in duration-150"
          onClick={() => setVerifyingTurn(null)}
        >
          <div
            className="w-full max-w-md rounded-2xl bg-card border border-slate-200 shadow-2xl overflow-hidden animate-in zoom-in-95 duration-150"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-5 py-4 text-white flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-white/15 backdrop-blur-xs border border-white/20">
                  <Cpu className="h-5 w-5 text-white" />
                </div>
                <div>
                  <h3 className="text-sm font-bold leading-tight">AI Model Used for This Response</h3>
                  <p className="text-[11px] text-blue-100">Actual inference model and runtime used</p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setVerifyingTurn(null)}
                className="rounded-lg p-1.5 text-white/80 hover:bg-white/20 hover:text-white transition-colors cursor-pointer"
                title="Close"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            {/* Modal Content */}
            <div className="p-5 space-y-3.5 text-xs">
              {/* Active Model Pill */}
              <div className="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-200/80">
                <span className="font-medium text-slate-500">Active Routing Tier:</span>
                <span className="font-bold text-slate-900 bg-white px-2.5 py-1 rounded-lg border border-slate-200 shadow-2xs font-mono text-[11px]">
                  {(() => {
                    const r = verifyingTurn.responseMeta?.routed_by;
                    const mId = verifyingTurn.responseMeta?.model_used || "Cloud LLM";
                    if (r === "learned_remediation") return "Cognitive Remediation (Self-Learned Rule)";
                    if (r === "rules") return "Tier 1: Deterministic Guardrail & Rules";
                    if (r === "classifier" || r === "classifier_pipeline_test") return "Tier 2: Local ML Intent Classifier (TF-IDF + LR)";
                    if (r === "gemini" || r === "groq" || verifyingTurn.responseMeta?.llm_provider === "gemini" || verifyingTurn.responseMeta?.llm_provider === "groq") {
                      return `Tier 3: Cloud LLM Fallback (${mId}, PII-Redacted)`;
                    }
                    return "Tier 1: Deterministic Guardrail & Rules";
                  })()}
                </span>
              </div>

              {/* Inference Engine & Hardware */}
              <div className="grid grid-cols-2 gap-2.5">
                <div className="p-3 rounded-xl bg-slate-50 border border-slate-200/80 space-y-1">
                  <div className="text-[10px] uppercase tracking-wider font-semibold text-slate-400">Inference Runtime</div>
                  <div className="font-bold text-slate-800 flex items-center gap-1.5">
                    <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                    {(() => {
                      const rBy = verifyingTurn.responseMeta?.routed_by;
                      const modelId = verifyingTurn.responseMeta?.model_used || "Cloud LLM";
                      if (rBy === "learned_remediation") return "Cognitive Remediation Loop";
                      if (rBy === "rules") return "Deterministic Rules & Guardrails";
                      if (rBy === "classifier" || rBy === "classifier_pipeline_test") return "Local CPU Scikit-Learn";
                      if (rBy === "gemini" || rBy === "groq" || verifyingTurn.responseMeta?.llm_provider === "cloud" || verifyingTurn.responseMeta?.llm_provider === "gemini" || verifyingTurn.responseMeta?.llm_provider === "groq") {
                        return `${modelId} Cloud (PII-Redacted)`;
                      }
                      return "Deterministic Rules Engine";
                    })()}
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-slate-50 border border-slate-200/80 space-y-1">
                  <div className="text-[10px] uppercase tracking-wider font-semibold text-slate-400">Security & Privacy</div>
                  <div className="font-bold text-emerald-700 flex items-center gap-1">
                    <ShieldCheck className="h-3.5 w-3.5 text-emerald-600" />
                    <span>PII-Redacted & RLS</span>
                  </div>
                </div>
              </div>

              {/* RLS & Privacy Redaction Details */}
              <div className="rounded-xl border border-blue-100 bg-blue-50/60 p-3 text-slate-700 space-y-1.5">
                <div className="flex items-center justify-between text-[11px]">
                  <span className="font-semibold text-blue-950">Authorized Student:</span>
                  <span className="font-mono font-bold text-blue-800">{student.id}</span>
                </div>
                <div className="flex items-center justify-between text-[11px]">
                  <span className="font-semibold text-blue-950">Cloud Privacy Redaction:</span>
                  <span className="inline-flex items-center gap-1 text-emerald-700 font-bold">
                    <Check className="h-3 w-3 text-emerald-600" /> Student PII (Name/Roll No) Anonymized
                  </span>
                </div>
                <div className="flex items-center justify-between text-[11px]">
                  <span className="font-semibold text-blue-950">Database Isolation:</span>
                  <span className="inline-flex items-center gap-1 text-emerald-700 font-bold">
                    <Check className="h-3 w-3 text-emerald-600" /> Active Session Token Enforced
                  </span>
                </div>
              </div>

              {/* Explanation note */}
              <p className="text-[11px] text-slate-500 leading-relaxed">
                This response was processed through the VIGNAN-AI Hybrid 3-Tier Architecture. Student PII (Name and Roll Number) is stripped and replaced with anonymized placeholders prior to any Tier 3 Cloud LLM fallback.
              </p>
            </div>

            {/* Modal Footer */}
            <div className="bg-slate-50 px-5 py-3 border-t border-slate-100 flex justify-end">
              <button
                type="button"
                onClick={() => setVerifyingTurn(null)}
                className="px-4 py-1.5 rounded-xl bg-blue-600 text-white font-semibold text-xs hover:bg-blue-700 transition-colors shadow-xs cursor-pointer"
              >
                Done
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
