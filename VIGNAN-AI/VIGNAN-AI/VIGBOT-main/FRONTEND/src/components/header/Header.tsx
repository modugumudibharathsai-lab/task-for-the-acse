"use client";

import React, { useState, useEffect, useRef } from "react";
import Image from "next/image";
import {
  Bell,
  Search,
  Globe,
  SlidersHorizontal,
  ChevronDown,
  Sparkles,
  BookOpen,
  Menu,
  LogOut,
  ShieldCheck,
  Check,
  X,
} from "lucide-react";
import { CURRENT_STUDENT } from "@/data/student";
import { Language, TRANSLATIONS, OFFICIAL_LANGUAGES_OF_INDIA } from "@/data/translations";
import { useLanguage } from "@/context/LanguageContext";
import { useStudent } from "@/context/StudentContext";
import { cn } from "@/lib/utils";
import { LanguageSelector } from "@/components/common/LanguageSelector";

interface HeaderProps {
  currentLang: Language;
  onLanguageChange: (lang: Language) => void;
  unreadCount: number;
  onOpenNotifications: () => void;
  onOpenProfile: () => void;
  onOpenSecurityDrawer: () => void;
  onOpenCommandBar: () => void;
  onToggleMobileMenu: () => void;
  onLogout: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  currentLang,
  onLanguageChange,
  unreadCount,
  onOpenNotifications,
  onOpenProfile,
  onOpenSecurityDrawer,
  onOpenCommandBar,
  onToggleMobileMenu,
  onLogout,
}) => {
  const { t } = useLanguage();
  const { studentData } = useStudent();
  const student = studentData?.profile || CURRENT_STUDENT;
  const initials = studentData?.profile?.initials || (student.name ? student.name.split(" ").map((n) => n[0]).join("").slice(0, 2).toUpperCase() : "AR");

  const [isLangOpen, setIsLangOpen] = useState(false);
  const [searchLang, setSearchLang] = useState("");
  const langDropdownRef = useRef<HTMLDivElement>(null);

  // Close language dropdown on outside click
  useEffect(() => {
    const handleOutsideClick = (e: MouseEvent) => {
      if (
        langDropdownRef.current &&
        !langDropdownRef.current.contains(e.target as Node)
      ) {
        setIsLangOpen(false);
      }
    };
    document.addEventListener("mousedown", handleOutsideClick);
    return () => document.removeEventListener("mousedown", handleOutsideClick);
  }, []);

  const activeLangMeta = OFFICIAL_LANGUAGES_OF_INDIA.find(
    (l) => l.code === currentLang
  ) || {
    code: currentLang,
    name: "English",
    nativeName: "English",
    script: "Latin",
    region: "India",
  };

  const filteredLanguages = OFFICIAL_LANGUAGES_OF_INDIA.filter((l) => {
    if (!searchLang.trim()) return true;
    const s = searchLang.toLowerCase();
    return (
      l.name.toLowerCase().includes(s) ||
      l.nativeName.toLowerCase().includes(s) ||
      l.region.toLowerCase().includes(s) ||
      l.code.toLowerCase().includes(s)
    );
  });

  return (
    <header className="sticky top-0 z-30 w-full border-b border-border bg-card/80 backdrop-blur-md transition-colors shadow-xs">
      <div className="w-full px-4 sm:px-6 py-3 flex items-center justify-between gap-3">
        {/* Left: Hamburger menu (mobile) + Compact Brand for mobile / small views */}
        <div className="flex items-center gap-2 sm:gap-3">
          <button
            onClick={onToggleMobileMenu}
            className="lg:hidden flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 bg-card text-muted-foreground hover:bg-muted transition-colors cursor-pointer"
            aria-label="Toggle navigation menu"
          >
            <Menu className="h-5 w-5" />
          </button>

          {/* Vignan logo for mobile view when sidebar is closed */}
          <img
            src="/vignan-logo.png"
            alt="Vignan's University"
            className="h-7 w-auto object-contain lg:hidden"
          />

          {/* Quick RLS Guardrail indicator in header */}
          <button
            onClick={onOpenSecurityDrawer}
            className="hidden sm:inline-flex items-center gap-1.5 rounded-full bg-emerald-50 px-3 py-1.5 text-xs font-semibold text-emerald-700 border border-emerald-200/80 hover:bg-emerald-100/70 transition-colors cursor-pointer whitespace-nowrap"
            title="Row-Level Security Active: Only authorized records can be retrieved."
          >
            <ShieldCheck className="h-3.5 w-3.5 text-emerald-600" />
            <span>{t.rlsActiveLabel || "RLS Active"}: {student.id}</span>
          </button>
        </div>

        {/* Center: Search / Command Bar Trigger */}
        <div className="flex-1 min-w-0 max-w-lg mx-2 sm:mx-4">
          <button
            onClick={onOpenCommandBar}
            className="flex w-full items-center justify-center sm:justify-between rounded-xl border border-slate-200/90 bg-muted/50/90 p-2.5 sm:px-4 sm:py-2.5 text-sm text-muted-foreground hover:border-blue-400 hover:bg-card hover:text-foreground transition-all shadow-xs cursor-pointer group"
          >
            <div className="flex items-center gap-2.5 truncate">
              <Search className="h-4 w-4 text-slate-400 group-hover:text-blue-500 transition-colors shrink-0" />
              <span className="hidden sm:block truncate">{t.searchPlaceholder || "Ask Helpdesk anything (attendance, exams, fees)..."}</span>
            </div>
            <kbd className="hidden sm:inline-block rounded-md border border-slate-200 bg-card px-1.5 py-0.5 text-sm font-mono text-slate-400 shadow-xs shrink-0">
              Ctrl K
            </kbd>
          </button>
        </div>

        {/* Right: Actions */}
        <div className="flex items-center gap-2 sm:gap-2.5 shrink-0">
          {/* Clickable Language Selector with all Official Languages of India */}
          <div className="relative" ref={langDropdownRef}>
            <button
              onClick={() => setIsLangOpen((prev) => !prev)}
              className={cn(
                "flex items-center gap-1.5 rounded-xl border px-3 py-2 text-xs font-semibold transition-all shadow-xs cursor-pointer select-none",
                isLangOpen
                  ? "border-blue-500 bg-blue-50/80 text-blue-700 ring-2 ring-blue-200/60"
                  : "border-border bg-card text-foreground hover:border-slate-300 hover:bg-muted/50"
              )}
              aria-label="Select Indian Language"
              aria-expanded={isLangOpen}
            >
              <Globe className="h-4 w-4 text-blue-600 shrink-0" />
              <span className="hidden sm:inline-block font-bold tracking-wide">{activeLangMeta.nativeName}</span>
              <span className="hidden sm:inline text-xs font-mono text-slate-400 uppercase">({currentLang})</span>
              <ChevronDown
                className={cn(
                  "hidden sm:inline-block h-3 w-3 text-slate-400 transition-transform duration-200",
                  isLangOpen && "rotate-180 text-blue-600"
                )}
              />
            </button>

            {isLangOpen && (
              <div className="absolute right-0 mt-2 w-80 sm:w-88 rounded-lg border border-slate-200/90 bg-card p-2.5 shadow-2xl z-50 animate-in fade-in-50 zoom-in-95 duration-150">
                {/* Header title */}
                <div className="flex items-center justify-between px-2 pt-1 pb-2 border-b border-slate-100">
                  <div className="flex items-center gap-1.5">
                    <Globe className="h-4 w-4 text-blue-600" />
                    <div>
                      <h4 className="text-xs font-bold text-foreground leading-tight">
                        Official Languages of India
                      </h4>
                      <p className="text-xs text-muted-foreground">
                        8th Schedule • 22 Recognized Languages + English
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => setIsLangOpen(false)}
                    className="p-1 rounded-lg text-slate-400 hover:bg-muted hover:text-muted-foreground transition-colors cursor-pointer"
                  >
                    <X className="h-3.5 w-3.5" />
                  </button>
                </div>

                {/* Search Filter input */}
                <div className="relative my-2 px-1">
                  <Search className="absolute left-3.5 top-2.5 h-3.5 w-3.5 text-slate-400 pointer-events-none" />
                  <input
                    type="text"
                    value={searchLang}
                    onChange={(e) => setSearchLang(e.target.value)}
                    placeholder="Search language / भाषा खोजें..."
                    className="w-full rounded-xl border border-slate-200 bg-muted/50 py-1.5 pl-8 pr-7 text-xs text-foreground placeholder-slate-400 focus:border-blue-500 focus:bg-card focus:outline-none focus:ring-2 focus:ring-blue-100 transition-all"
                    autoFocus
                  />
                  {searchLang && (
                    <button
                      onClick={() => setSearchLang("")}
                      className="absolute right-3.5 top-2 text-slate-400 hover:text-muted-foreground cursor-pointer"
                    >
                      <X className="h-3.5 w-3.5" />
                    </button>
                  )}
                </div>

                {/* Languages List */}
                <div className="max-h-72 overflow-y-auto space-y-0.5 pr-1">
                  {filteredLanguages.length > 0 ? (
                    filteredLanguages.map((lang) => {
                      const isSelected = currentLang === lang.code;
                      return (
                        <button
                          key={lang.code}
                          onClick={() => {
                            onLanguageChange(lang.code);
                            setIsLangOpen(false);
                            setSearchLang("");
                          }}
                          className={cn(
                            "flex w-full items-center justify-between rounded-xl px-3 py-2 text-left transition-all cursor-pointer group",
                            isSelected
                              ? "bg-blue-50/90 text-blue-900 font-semibold ring-1 ring-blue-200"
                              : "hover:bg-muted/50 text-foreground"
                          )}
                        >
                          <div className="flex flex-col min-w-0 pr-2">
                            <div className="flex items-center gap-2">
                              <span className="text-sm font-semibold tracking-wide text-foreground group-hover:text-blue-700 transition-colors">
                                {lang.nativeName}
                              </span>
                              <span className="text-xs text-muted-foreground font-normal">
                                {lang.name}
                              </span>
                              <span className="rounded bg-muted px-1.5 py-0.2 text-[9px] font-mono text-muted-foreground uppercase">
                                {lang.code}
                              </span>
                            </div>
                            <span className="text-xs text-slate-400 truncate mt-0.5">
                              {lang.region}
                            </span>
                          </div>
                          {isSelected && (
                            <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-blue-600 text-white shadow-2xs">
                              <Check className="h-3 w-3 stroke-[3]" />
                            </span>
                          )}
                        </button>
                      );
                    })
                  ) : (
                    <div className="py-6 text-center text-xs text-slate-400">
                      No matching Indian language found
                    </div>
                  )}
                </div>

                {/* Footer status */}
                <div className="mt-2 pt-2 border-t border-slate-100 px-2 flex items-center justify-between text-xs text-slate-400">
                  <span>Selected: <strong className="text-foreground">{activeLangMeta.name}</strong></span>
                  <span className="font-mono text-[9px] text-emerald-600 font-semibold">23 Languages Active</span>
                </div>
              </div>
            )}
          </div>

          {/* Security & Connected Agents Drawer Trigger */}
          <button
            onClick={onOpenSecurityDrawer}
            className="hidden md:flex items-center gap-1.5 rounded-xl border border-slate-200 bg-card px-3 py-2 text-xs font-medium text-foreground hover:border-slate-300 hover:bg-muted/50 shadow-xs transition-colors cursor-pointer whitespace-nowrap"
            title="View Row-Level Security, Connected Agents & Audit Logs"
          >
            <SlidersHorizontal className="h-3.5 w-3.5 text-indigo-600" />
            <span>Agents (12)</span>
          </button>

          {/* Notifications Bell */}
          <button
            onClick={onOpenNotifications}
            className="relative flex h-9 w-9 items-center justify-center rounded-xl border border-border bg-card text-foreground hover:bg-muted/50 shadow-xs transition-colors cursor-pointer"
            aria-label="Notifications"
          >
            <Bell className="h-4 w-4 text-muted-foreground" />
            {unreadCount > 0 && (
              <span className="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-rose-500 text-xs font-bold text-white ring-2 ring-white">
                {unreadCount}
              </span>
            )}
          </button>

          {/* Authenticated Student Chip */}
          <div
            onClick={onOpenProfile}
            className="flex items-center gap-2 rounded-xl border border-blue-200 bg-blue-50/70 py-1.5 px-2.5 hover:bg-blue-100/70 transition-all cursor-pointer shadow-xs"
            title="Click to view student profile"
          >
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-gradient-to-tr from-blue-600 to-indigo-600 text-xs font-bold text-white shadow-xs shrink-0">
              {initials}
            </div>
            <div className="text-left hidden xl:block">
              <div className="flex items-center gap-1.5">
                <span className="text-xs font-semibold text-foreground leading-none">
                  {student.name}
                </span>
                <span className="inline-block h-1.5 w-1.5 rounded-full bg-emerald-500" />
              </div>
              <p className="text-sm font-mono text-muted-foreground leading-tight mt-0.5">
                {student.id}
              </p>
            </div>
          </div>

          {/* Quick Sign Out Button */}
          <button
            onClick={onLogout}
            className="flex h-9 w-9 items-center justify-center rounded-xl border border-slate-200 bg-card text-muted-foreground hover:text-rose-600 hover:border-rose-200 hover:bg-rose-50 transition-colors cursor-pointer"
            title={`${t.signOut || "Sign Out"} / Back to Login`}
            aria-label={t.signOut || "Sign Out"}
          >
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </div>
    </header>
  );
};
