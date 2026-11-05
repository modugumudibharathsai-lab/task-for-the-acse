"use client";

import React from "react";
import Image from "next/image";
import {
  Home,
  UserCheck,
  GraduationCap,
  Clock,
  Calendar,
  CreditCard,
  BookOpen,
  FileText,
  CalendarPlus,
  Bell,
  CalendarDays,
  Layers,
  Bot,
  ShieldCheck,
  LogOut,
  Sparkles,
  X,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
  Users,
  TrendingUp,
  MapPin,
  Ticket,
  BedDouble,
  Store,
  Briefcase,
  Trophy,
  Book,
  Bus,
  BarChart3,
} from "lucide-react";
import { CURRENT_STUDENT } from "@/data/student";
import { ATTENDANCE_DATA } from "@/data/attendance";
import { Language, TRANSLATIONS } from "@/data/translations";
import { useLanguage } from "@/context/LanguageContext";
import { useStudent } from "@/context/StudentContext";
import { cn } from "@/lib/utils";
import { useDynamicSchedule } from "@/hooks/useDynamicSchedule";

interface SidebarProps {
  activeTab: string;
  onSelectTab: (tab: string) => void;
  isOpenMobile: boolean;
  onCloseMobile: () => void;
  onLogout: () => void;
  onOpenProfile: () => void;
  onOpenSecurityDrawer: () => void;
  currentLang: Language;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  onSelectTab,
  isOpenMobile,
  onCloseMobile,
  onLogout,
  onOpenProfile,
  onOpenSecurityDrawer,
  isCollapsed,
  onToggleCollapse,
  currentLang,
}) => {
  const { t } = useLanguage();
  const { studentData } = useStudent();
  const student = studentData?.profile || CURRENT_STUDENT;
  const initials = studentData?.profile?.initials || (student.name ? student.name.split(" ").map((n) => n[0]).join("").slice(0, 2).toUpperCase() : "AR");
  const { formattedNextExamDate } = useDynamicSchedule();

  const navigationSections = [
    {
      title: t.sectionOverview || "Overview",
      items: [
        {
          id: "home",
          label: t.navHome || "Helpdesk Home",
          icon: Home,
          badge: "AI Core",
          badgeColor: "bg-blue-100 text-blue-700",
        },
      ],
    },
    {
      title: t.sectionAcademics || "Academics",
      items: [
        {
          id: "attendance",
          label: t.navAttendance || "Attendance",
          icon: UserCheck,
          badge: `${Math.round(studentData?.attendance?.overallPercentage ?? ATTENDANCE_DATA.overallPercentage)}%`,
          badgeColor: "bg-amber-100 text-amber-800",
        },
        {
          id: "marks",
          label: t.navMarks || "Marks & CGPA",
          icon: GraduationCap,
          badge: `${student?.cgpa?.toFixed(2) ?? "8.42"}`,
          badgeColor: "bg-emerald-100 text-emerald-800",
        },

        {
          id: "library",
          label: "Library",
          icon: Book,
        },
        {
          id: "timetable",
          label: t.navTimetable || "Timetable",
          icon: Clock,
        },
        {
          id: "exams",
          label: t.navExams || "Examinations",
          icon: Calendar,
          badge: formattedNextExamDate,
          badgeColor: "bg-indigo-100 text-indigo-800",
        },
        {
          id: "curriculum",
          label: t.navCurriculum || "Curriculum",
          icon: BookOpen,
        },
      ],
    },
    {
      title: t.sectionSupport || "Services & Fees",
      items: [
        {
          id: "fees",
          label: t.navFees || "Fee Status",
          icon: CreditCard,
          badge: "Due",
          badgeColor: "bg-amber-100 text-amber-800",
        },
        {
          id: "services",
          label: t.navServices || "Student Services",
          icon: Layers,
        },
        {
          id: "hostel",
          label: "Hostel & Mess",
          icon: BedDouble,
        },
        {
          id: "career",
          label: "Career Hub",
          icon: Briefcase,
          badge: "AI",
          badgeColor: "bg-indigo-100 text-indigo-700",
        },

        {
          id: "calendar",
          label: t.navCalendar || "Academic Calendar",
          icon: CalendarDays,
        },
      ],
    },
    {
      title: t.sectionSystem || "University Info",
      items: [
        {
          id: "circulars",
          label: t.navCirculars || "Circulars & Notices",
          icon: Bell,
          badge: "New",
          badgeColor: "bg-red-100 text-red-700",
        },
        {
          id: "map",
          label: "Campus Map",
          icon: MapPin,
        },
        {
          id: "transport",
          label: "Transport (Live)",
          icon: Bus,
        },
        {
          id: "events",
          label: "Event Registration",
          icon: Ticket,
        },
        {
          id: "lost-and-found",
          label: "Lost & Found",
          icon: FileText,
          badge: "New",
          badgeColor: "bg-emerald-100 text-emerald-800",
        },
        {
          id: "bookings",
          label: "Facility Booking",
          icon: CalendarPlus,
        },
        {
          id: "clubs",
          label: "Clubs & Communities",
          icon: Users,
        },
        {
          id: "marketplace",
          label: "Marketplace",
          icon: Store,
        },
        {
          id: "polling",
          label: "Campus Polling",
          icon: BarChart3,
        },
        {
          id: "alumni",
          label: "Alumni Network",
          icon: Users,
        },
        {
          id: "policies",
          label: t.navPolicies || "Policies & Regulations",
          icon: FileText,
        },
      ],
    },
  ];

  const handleItemClick = (id: string) => {
    onSelectTab(id);
    if (isOpenMobile) {
      onCloseMobile();
    }
  };

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpenMobile && (
        <div
          onClick={onCloseMobile}
          className="fixed inset-0 z-40 bg-slate-900/50 backdrop-blur-xs lg:hidden"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={cn(
          "fixed top-0 bottom-0 left-0 z-50 flex flex-col border-r border-border bg-card shadow-sm transition-[width,transform] duration-200 ease-in-out lg:sticky lg:translate-x-0 lg:h-dvh lg:shrink-0",
          isOpenMobile ? "translate-x-0" : "-translate-x-full",
          isCollapsed ? "w-[72px]" : "w-64"
        )}
      >
        {/* Brand Header */}
        <div
          className={cn(
            "flex items-center border-b border-slate-200/80 transition-all",
            isCollapsed ? "flex-col gap-2 py-3.5 px-2" : "h-20 justify-between px-4"
          )}
        >
          <div
            onClick={() => handleItemClick("home")}
            className={cn(
              "flex items-center cursor-pointer group min-w-0 flex-1",
              !isCollapsed ? "gap-2.5" : "justify-center w-full"
            )}
          >
            {!isCollapsed ? (
              <div className="flex items-center gap-2.5 min-w-0 flex-1">
                <Image
                  src="/vignan-logo.png"
                  alt="Vignan's University"
                  width={155}
                  height={48}
                  className="h-12 w-auto max-w-[155px] object-contain drop-shadow-xs group-hover:scale-[1.02] transition-transform shrink-0"
                />
                <span className="shrink-0 rounded-full bg-indigo-50 px-2 py-0.5 text-xs font-bold text-indigo-700 border border-indigo-200 shadow-2xs">
                  VIGNAN-AI
                </span>
              </div>
            ) : (
              <div className="flex items-center justify-center w-full py-1">
                <Image
                  src="/vignan-logo.png"
                  alt="Vignan's University"
                  width={100}
                  height={32}
                  className="h-8 w-auto object-contain drop-shadow-xs"
                />
              </div>
            )}
          </div>

          {/* Collapse toggle on desktop */}
          <button
            onClick={onToggleCollapse}
            className="hidden lg:flex rounded-lg p-1.5 text-slate-400 hover:bg-muted hover:text-foreground cursor-pointer shrink-0"
            title={isCollapsed ? (t.expandSidebar || "Expand sidebar") : (t.collapseSidebar || "Collapse sidebar")}
          >
            {isCollapsed ? (
              <ChevronsRight className="h-4 w-4" />
            ) : (
              <ChevronsLeft className="h-4 w-4" />
            )}
          </button>

          {/* Close button on mobile */}
          {!isCollapsed && (
            <button
              onClick={onCloseMobile}
              className="rounded-lg p-1.5 text-muted-foreground hover:bg-muted lg:hidden cursor-pointer shrink-0"
            >
              <X className="h-5 w-5" />
            </button>
          )}
        </div>

        {/* Navigation List */}
        <div className="flex-1 overflow-y-auto overscroll-contain px-3 py-4 space-y-5 scrollbar-thin">
          {navigationSections.map((section) => (
            <div key={section.title} className="space-y-1">
              {!isCollapsed && (
                <div className="px-3 text-sm font-bold uppercase tracking-wider text-slate-400">
                  {section.title}
                </div>
              )}
              <div className="space-y-0.5">
                {section.items.map((item) => {
                  const Icon = item.icon;
                  const isActive = activeTab === item.id;
                  return (
                    <button
                      key={item.id}
                      onClick={() => handleItemClick(item.id)}
                      title={isCollapsed ? item.label : undefined}
                      className={cn(
                        "group flex w-full items-center rounded-xl py-2.5 text-sm font-medium transition-all cursor-pointer",
                        isCollapsed ? "justify-center px-0" : "justify-between px-3",
                        isActive
                          ? "bg-blue-50 text-blue-700 font-semibold shadow-xs"
                          : "text-muted-foreground hover:bg-muted/50 hover:text-foreground"
                      )}
                    >
                      <div className={cn("flex items-center min-w-0", !isCollapsed && "gap-2.5")}>
                        <Icon
                          className={`h-4 w-4 shrink-0 transition-colors ${
                            isActive
                              ? "text-blue-600"
                              : "text-slate-400 group-hover:text-muted-foreground"
                          }`}
                        />
                        {!isCollapsed && <span className="truncate">{item.label}</span>}
                      </div>

                      {!isCollapsed && item.badge && (
                        <span
                          className={`shrink-0 whitespace-nowrap rounded-full px-2 py-0.5 text-sm font-semibold ${item.badgeColor}`}
                        >
                          {item.badge}
                        </span>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </div>

        {/* VIGNAN-AI Status Pill & Security */}
        <div className="px-3 py-2 border-t border-slate-100 bg-muted/50/50">
          <button
            onClick={onOpenSecurityDrawer}
            title={isCollapsed ? `RLS Active: ${student.id}` : undefined}
            className={cn(
              "flex w-full items-center rounded-xl border border-emerald-200 bg-emerald-50/60 p-2 text-left hover:bg-emerald-100/60 transition-colors cursor-pointer",
              isCollapsed ? "justify-center" : "justify-between"
            )}
          >
            <div className={cn("flex items-center", !isCollapsed && "gap-2")}>
              <span className="relative flex h-2 w-2 shrink-0">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              {!isCollapsed && (
                <div>
                  <p className="text-xs font-bold text-emerald-900 leading-tight">
                    RLS Active: {student.id}
                  </p>
                  <p className="text-sm text-emerald-700 leading-tight mt-0.5">
                    12 Connected Agents
                  </p>
                </div>
              )}
            </div>
            {!isCollapsed && <ShieldCheck className="h-4 w-4 text-emerald-600 shrink-0" />}
          </button>
        </div>

        {/* Student Profile & Sign Out Footer */}
        <div className="border-t border-slate-200 p-3 bg-card">
          <div className={cn("flex items-center", isCollapsed ? "flex-col gap-2" : "justify-between")}>
            <div
              onClick={onOpenProfile}
              title={isCollapsed ? student.name : undefined}
              className={cn(
                "flex items-center cursor-pointer hover:opacity-80 transition-opacity min-w-0",
                isCollapsed ? "" : "gap-2.5 flex-1 mr-1"
              )}
            >
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gradient-to-tr from-blue-600 to-indigo-600 text-xs font-bold text-white shadow-xs">
                {initials}
              </div>
              {!isCollapsed && (
                <div className="min-w-0 flex-1">
                  <p className="text-xs font-bold text-foreground truncate leading-tight">
                    {student.name}
                  </p>
                  <p className="text-sm font-mono text-muted-foreground truncate leading-tight mt-0.5">
                    {student.id}
                  </p>
                </div>
              )}
            </div>

            <button
              onClick={onLogout}
              className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors cursor-pointer shrink-0"
              title={t.signOut || "Sign Out"}
              aria-label={t.signOut || "Sign Out"}
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        </div>
      </aside>
    </>
  );
};
