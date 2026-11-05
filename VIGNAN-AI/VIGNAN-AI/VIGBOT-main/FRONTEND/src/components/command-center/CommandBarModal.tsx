"use client";

import React, { useState, useEffect, useRef } from "react";
import {
  Search,
  X,
  Sparkles,
  ArrowRight,
  UserCheck,
  Calendar,
  CreditCard,
  BookOpen,
  FileText,
  LifeBuoy,
} from "lucide-react";
import { useStudent } from "@/context/StudentContext";
import { useLanguage } from "@/context/LanguageContext";

interface CommandBarModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectQuery: (query: string) => void;
}

export const CommandBarModal: React.FC<CommandBarModalProps> = ({
  isOpen,
  onClose,
  onSelectQuery,
}) => {
  const { studentData } = useStudent();
  const { t, tDynamic } = useLanguage();
  const student = studentData?.profile;

  const [searchTerm, setSearchTerm] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [isOpen]);

  // Keyboard shortcut listener for Ctrl+K / Cmd+K
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        if (isOpen) {
          onClose();
        }
      } else if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const defaultSuggestions = [
    { label: "What is my attendance in Digital Electronics?", cat: "Attendance", icon: UserCheck },
    { label: "When is my next exam?", cat: "Examinations", icon: Calendar },
    { label: "What is my fee status and outstanding balance?", cat: "Fee Ledger", icon: CreditCard },
    { label: "How many credits do I still need to graduate?", cat: "Curriculum", icon: BookOpen },
    { label: "What does the attendance policy say about condonation?", cat: "Policies", icon: FileText },
    { label: "I want to apply for a Bonafide certificate.", cat: "Services", icon: LifeBuoy },
    { label: "I want to book a mentor meeting with Dr. Radhika Sharma.", cat: "Services", icon: LifeBuoy },
  ];

  const handleExecute = (queryText: string) => {
    onSelectQuery(queryText);
    onClose();
  };

  return (
    <div role="dialog" aria-modal="true" className="fixed inset-0 z-50 flex items-start justify-center bg-slate-900/50 backdrop-blur-xs pt-20 p-4">
      <div className="relative w-full max-w-xl rounded-xl bg-card shadow-2xl border border-slate-200 overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Search Bar Input */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (searchTerm.trim()) {
              handleExecute(searchTerm);
            }
          }}
          className="flex items-center gap-3 border-b border-slate-100 px-5 py-4 bg-muted/50/50"
        >
          <Search className="h-5 w-5 text-blue-600 shrink-0" />
          <input
            ref={inputRef}
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Ask or search anything (e.g. attendance, exams, fees, timetable)..."
            className="w-full bg-transparent text-sm text-foreground placeholder:text-slate-400 focus:outline-hidden"
          />
          {searchTerm && (
            <button
              type="button"
              onClick={() => setSearchTerm("")}
              className="text-slate-400 hover:text-muted-foreground"
            >
              <X className="h-4 w-4" />
            </button>
          )}
          <kbd className="hidden sm:inline-block rounded border border-slate-200 bg-card px-2 py-0.5 font-mono text-sm text-slate-400">
            ESC
          </kbd>
        </form>

        {/* Suggestions / Results */}
        <div className="max-h-80 overflow-y-auto overscroll-contain p-3 text-xs space-y-1">
          {searchTerm.trim() ? (
            <div
              onClick={() => handleExecute(searchTerm)}
              className="rounded-xl bg-blue-50/80 p-3 text-blue-900 font-semibold flex items-center justify-between cursor-pointer hover:bg-blue-100/80 transition-colors"
            >
              <div className="flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-blue-600" />
                <span>Ask VIGNAN-AI: &quot;{searchTerm}&quot;</span>
              </div>
              <ArrowRight className="h-4 w-4 text-blue-600" />
            </div>
          ) : (
            <div className="px-3 py-1.5 text-sm font-bold uppercase tracking-wider text-slate-400">
              Popular Queries for {student?.name || "Student"} ({student?.id || "Student ID"})
            </div>
          )}

          {defaultSuggestions.map((item, idx) => {
            const Icon = item.icon;
            return (
              <div
                key={idx}
                onClick={() => handleExecute(item.label)}
                className="flex items-center justify-between rounded-xl p-2.5 hover:bg-muted/50 text-foreground hover:text-foreground transition-colors cursor-pointer"
              >
                <div className="flex items-center gap-2.5">
                  <Icon className="h-4 w-4 text-slate-400" />
                  <span className="font-medium">{item.label}</span>
                </div>
                <span className="rounded-md bg-muted px-2 py-0.5 text-sm text-muted-foreground font-semibold">
                  {item.cat}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
