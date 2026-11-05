"use client";

import React from "react";
import {
  Calendar,
  Clock,
  GraduationCap,
  FileText,
  Bell,
  AlertTriangle,
  UserCheck,
  CreditCard,
  LifeBuoy,
  FileCheck2,
  Sparkles,
  BookOpen,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { useLanguage } from "@/context/LanguageContext";

interface QuickActionChipsProps {
  onSelectAction: (query: string) => void;
  showActions: boolean;
  onToggleActions: () => void;
}

export const QuickActionChips: React.FC<QuickActionChipsProps> = ({
  onSelectAction,
  showActions,
  onToggleActions,
}) => {
  const { t, language } = useLanguage();
  const [showAll, setShowAll] = React.useState(false);


  const primaryActions = [
    {
      label: t.quickMyAttendance,
      query: language === "te" ? "నా హాజరు వివరాలు ఏమిటి?" : language === "hi" ? "मेरी उपस्थिति का विवरण क्या है?" : "What is my attendance across my registered subjects?",
      icon: UserCheck,
      color: "text-blue-600 bg-blue-50 border-blue-200",
    },
    {
      label: t.quickNextExam,
      query: language === "te" ? "నా తదుపరి పరీక్ష ఎప్పుడు?" : language === "hi" ? "मेरी अगली परीक्षा कब है?" : "When is my next exam?",
      icon: Clock,
      color: "text-indigo-600 bg-indigo-50 border-indigo-200",
    },
    {
      label: t.quickMyMarks,
      query: language === "te" ? "నా తాజా మార్కులు మరియు CGPA ఎంత?" : language === "hi" ? "मेरे नवीनतम अंक और CGPA क्या हैं?" : "What are my latest marks and CGPA?",
      icon: GraduationCap,
      color: "text-emerald-600 bg-emerald-50 border-emerald-200",
    },
    {
      label: t.quickTodayTimetable,
      query: language === "te" ? "ఈ రోజు నా టైమ్‌టేబుల్ ఏమిటి?" : language === "hi" ? "आज की मेरी समय सारिणी क्या है?" : "What is my timetable for today?",
      icon: Calendar,
      color: "text-purple-600 bg-purple-50 border-purple-200",
    },
    {
      label: t.quickFeeStatus,
      query: language === "te" ? "నా ఫీజు బకాయి వివరాలు ఏమిటి?" : language === "hi" ? "मेरी फीस स्थिति और बकाया राशि क्या है?" : "What is my fee status and outstanding balance?",
      icon: CreditCard,
      color: "text-amber-600 bg-amber-50 border-amber-200",
    },
    {
      label: t.quickCurriculum,
      query: language === "te" ? "ఈ సెమిస్టర్ సబ్జెక్టులు ఏమిటి?" : language === "hi" ? "इस सेमेस्टर मेरे विषय क्या हैं?" : "What are my subjects this semester?",
      icon: BookOpen,
      color: "text-cyan-600 bg-cyan-50 border-cyan-200",
    },
    {
      label: t.quickCirculars,
      query: language === "te" ? "తాజా విశ్వవిద్యాలయ సర్క్యులర్లు ఏమిటి?" : language === "hi" ? "नवीनतम विश्वविद्यालय परिपत्र क्या हैं?" : "What are the latest university circulars?",
      icon: Bell,
      color: "text-rose-600 bg-rose-50 border-rose-200",
    },
    {
      label: t.quickPolicies,
      query: language === "te" ? "హాజరు మరియు పరీక్షల యూనివర్సిటీ నిబంధనలు ఏమిటి?" : language === "hi" ? "विश्वविद्यालय की उपस्थिति और परीक्षा नीतियां क्या हैं?" : "What are the university policies on attendance condonation?",
      icon: FileText,
      color: "text-muted-foreground bg-muted/50 border-slate-200",
    },
    {
      label: t.quickCalendar,
      query: language === "te" ? "రాబోయే విద్యా క్యాలెండర్ ఈవెంట్లు ఏమిటి?" : language === "hi" ? "आगामी शैक्षणिक कैलेंडर कार्यक्रम क्या हैं?" : "What are the upcoming academic calendar events?",
      icon: Calendar,
      color: "text-teal-600 bg-teal-50 border-teal-200",
    },
    {
      label: t.quickServices,
      query: language === "te" ? "నేను ఏ విద్యార్థి సేవలను అభ్యర్థించవచ్చు?" : language === "hi" ? "मैं किन छात्र सेवाओं का अनुरोध कर सकता हूँ?" : "What student services can I request?",
      icon: LifeBuoy,
      color: "text-sky-600 bg-sky-50 border-sky-200",
    },
  ];

  const contextualActions = [
    {
      label: t.chipBelow75,
      query: language === "te" ? "75% కన్నా తక్కువ హాజరు ఉన్న సబ్జెక్టులు చూపించు" : language === "hi" ? "75% से कम उपस्थिति वाले विषय दिखाएं" : "Show subjects below 75% attendance",
      icon: AlertTriangle,
      badge: "Important",
    },
    {
      label: t.chipUpcomingAssessments,
      query: language === "te" ? "నా రాబోయే పరీక్షలు మరియు అసైన్‌మెంట్లు చూపించు" : language === "hi" ? "मेरे आगामी मूल्यांकन और परीक्षाएं दिखाएं" : "Show my upcoming assessments",
      icon: Sparkles,
    },
    {
      label: t.chipExplainCurriculum,
      query: language === "te" ? "నా ప్రస్తుత సెమిస్టర్ సిలబస్ వివరించు" : language === "hi" ? "मेरे वर्तमान सेमेस्टर का पाठ्यक्रम समझाएं" : "Explain my curriculum",
      icon: BookOpen,
    },
    {
      label: t.chipRaiseService,
      query: language === "te" ? "బోనాఫైడ్ సర్టిఫికెట్ కోసం సర్వీస్ రిక్వెస్ట్ చేయండి" : language === "hi" ? "प्रमाणपत्र के लिए सेवा अनुरोध दर्ज करें" : "Raise a service request for bonafide certificate",
      icon: FileCheck2,
    },
    {
      label: t.chipBookMentor,
      query: language === "te" ? "నా క్లాస్ టీచర్ Mr. T. Latesh Babuతో అపాయింట్‌మెంట్ బుక్ చేయండి" : language === "hi" ? "कक्षा अध्यापक Mr. T. Latesh Babu से मिलने का समय बुक करें" : "Book a mentor meeting with class teacher Mr. T. Latesh Babu",
      icon: UserCheck,
    },
    {
      label: t.chipRaiseGrievance,
      query: language === "te" ? "విద్యా సమస్యపై ఫిర్యాదు నమోదు చేయండి" : language === "hi" ? "शैक्षणिक विषय पर शिकायत दर्ज करें" : "Raise an academic grievance",
      icon: AlertTriangle,
    },
  ];

  return (
    <div className="space-y-2 pt-1 border-t border-slate-100">
      {/* Primary Category Row */}
      <div className="space-y-1">
        <div className="flex items-center justify-between gap-2">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
            {t.quickActionsTitle}
          </span>
          <button
            type="button"
            onClick={onToggleActions}
            className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg border border-slate-200 bg-card text-slate-500 transition-colors hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700 focus-visible:outline-hidden focus-visible:ring-2 focus-visible:ring-blue-500 cursor-pointer"
            title={showActions ? "Minimize quick actions" : "Show quick actions"}
            aria-label={showActions ? "Minimize quick actions" : "Show quick actions"}
            aria-expanded={showActions}
            aria-controls="vigbot-quick-action-list"
          >
            {showActions ? <ChevronDown className="h-4 w-4" /> : <ChevronUp className="h-4 w-4" />}
          </button>
        </div>
      </div>

      <div
        id="vigbot-quick-action-list"
        aria-hidden={!showActions}
        className={showActions ? "space-y-2" : "hidden"}
      >
        <div className="flex flex-wrap items-center gap-1.5 pb-1">
          {primaryActions.slice(0, showAll ? primaryActions.length : 5).map((action, i) => {
            const Icon = action.icon;
            return (
              <button
                key={i}
                onClick={() => onSelectAction(action.query)}
                className={`flex shrink-0 items-center gap-1 rounded-full border px-2.5 py-1 text-sm font-medium transition-all hover:scale-102 hover:shadow-xs cursor-pointer ${action.color}`}
              >
                <Icon className="h-3 w-3" />
                <span>{action.label}</span>
              </button>
            );
          })}
        </div>

        {/* Contextual / Workflow Actions */}
        <div className="space-y-1">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
            {t.contextualActionsTitle}
          </span>
          <div className="flex flex-wrap items-center gap-1.5 pb-1">
            {contextualActions.slice(0, showAll ? contextualActions.length : 3).map((action, i) => {
              const Icon = action.icon;
              return (
                <button
                  key={i}
                  onClick={() => onSelectAction(action.query)}
                  className="group flex shrink-0 items-center gap-1.5 rounded-full border border-slate-200 bg-card px-2.5 py-1 text-sm font-medium text-foreground hover:border-blue-300 hover:bg-blue-50/50 hover:text-blue-700 transition-all cursor-pointer shadow-2xs"
                >
                  <Icon className="h-3 w-3 text-slate-400 group-hover:text-blue-600" />
                  <span>{action.label}</span>
                  {action.badge && (
                    <span className="rounded-full bg-amber-100 px-1.5 py-0.2 text-[9px] font-semibold text-amber-700">
                      {action.badge}
                    </span>
                  )}
                </button>
              );
            })}

            <button
              onClick={() => setShowAll(!showAll)}
              className="flex shrink-0 items-center gap-1 rounded-full border border-slate-200 bg-muted/30 px-2.5 py-1 text-sm font-medium text-slate-600 hover:bg-muted/60 transition-all cursor-pointer shadow-2xs"
            >
              <span>{showAll ? "Show less" : "More actions..."}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
