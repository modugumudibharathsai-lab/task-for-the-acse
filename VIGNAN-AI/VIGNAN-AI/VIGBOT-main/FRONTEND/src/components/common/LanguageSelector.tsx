"use client";

import React, { useState, useRef, useEffect } from "react";
import { Globe, ChevronDown, Check, Search, X } from "lucide-react";
import { cn } from "@/lib/utils";
import {
  Language,
  OFFICIAL_LANGUAGES_OF_INDIA,
  LanguageMeta,
} from "@/data/translations";
import { useLanguage } from "@/context/LanguageContext";

interface LanguageSelectorProps {
  className?: string;
  buttonClassName?: string;
  dropdownAlign?: "left" | "right";
}

export const LanguageSelector: React.FC<LanguageSelectorProps> = ({
  className,
  buttonClassName,
  dropdownAlign = "right",
}) => {
  const { language: currentLang, setLanguage } = useLanguage();
  const [isOpen, setIsOpen] = useState(false);
  const [searchLang, setSearchLang] = useState("");
  const dropdownRef = useRef<HTMLDivElement>(null);

  const activeLangMeta: LanguageMeta =
    OFFICIAL_LANGUAGES_OF_INDIA.find((l) => l.code === currentLang) ||
    OFFICIAL_LANGUAGES_OF_INDIA[0];

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
        setSearchLang("");
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const filteredLanguages = OFFICIAL_LANGUAGES_OF_INDIA.filter((l) => {
    const q = searchLang.toLowerCase().trim();
    if (!q) return true;
    return (
      l.name.toLowerCase().includes(q) ||
      l.nativeName.toLowerCase().includes(q) ||
      l.code.toLowerCase().includes(q) ||
      l.region.toLowerCase().includes(q)
    );
  });

  return (
    <div className={cn("relative", className)} ref={dropdownRef}>
      <button
        onClick={() => setIsOpen((prev) => !prev)}
        className={cn(
          "flex items-center gap-1.5 rounded-xl border px-3 py-2 text-xs font-semibold transition-all shadow-xs cursor-pointer select-none",
          isOpen
            ? "border-blue-500 bg-blue-50/80 text-blue-700 ring-2 ring-blue-200/60"
            : "border-slate-200 bg-card text-foreground hover:border-slate-300 hover:bg-muted/50",
          buttonClassName
        )}
        aria-label="Select Indian Language"
        aria-expanded={isOpen}
      >
        <Globe className="h-3.5 w-3.5 text-blue-600 shrink-0" />
        <span className="font-bold tracking-wide">{activeLangMeta.nativeName}</span>
        <span className="text-xs font-mono text-slate-400 uppercase">
          ({currentLang})
        </span>
        <ChevronDown
          className={cn(
            "h-3 w-3 text-slate-400 transition-transform duration-200",
            isOpen && "rotate-180 text-blue-600"
          )}
        />
      </button>

      {isOpen && (
        <div
          className={cn(
            "absolute mt-2 w-80 sm:w-88 rounded-lg border border-slate-200/90 bg-card p-2.5 shadow-2xl z-50 animate-in fade-in-50 zoom-in-95 duration-150",
            dropdownAlign === "right" ? "right-0" : "left-0"
          )}
        >
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
              onClick={() => {
                setIsOpen(false);
                setSearchLang("");
              }}
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
                      setLanguage(lang.code);
                      setIsOpen(false);
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
            <span>22 Eighth Schedule Languages + English</span>
            <span className="text-emerald-600 font-medium">100% Native Script</span>
          </div>
        </div>
      )}
    </div>
  );
};
