"use client";

import React, { useState, useEffect } from "react";
import { LoginView } from "@/components/auth/LoginView";
import { LandingPage } from "@/components/landing/LandingPage";
import { Sidebar } from "@/components/sidebar/Sidebar";
import { Header } from "@/components/header/Header";
import { AiHelpdeskPanel } from "@/components/ai-helpdesk/AiHelpdeskPanel";
import { StudentSnapshot } from "@/components/student-snapshot/StudentSnapshot";
import { AttendanceView } from "@/components/attendance/AttendanceView";
import { MarksView } from "@/components/marks/MarksView";
import { TimetableView } from "@/components/timetable/TimetableView";
import { ExaminationsView } from "@/components/examinations/ExaminationsView";
import { FeesView } from "@/components/fees/FeesView";
import { CurriculumView } from "@/components/curriculum/CurriculumView";
import { PoliciesView } from "@/components/policies/PoliciesView";
import { CircularsView } from "@/components/circulars/CircularsView";
import { CalendarView } from "@/components/calendar/CalendarView";
import { ClubsView } from "@/components/clubs/ClubsView";
import { LostAndFoundView } from "@/components/lost-and-found/LostAndFoundView";
import { BookingsView } from "@/components/bookings/BookingsView";
import { StudentServicesView } from "@/components/services/StudentServicesView";
import { CampusMapView } from "@/components/map/CampusMapView";
import { EventRegistrationView } from "@/components/events/EventRegistrationView";
import { HostelManagementView } from "@/components/hostel/HostelManagementView";
import { MarketplaceView } from "@/components/marketplace/MarketplaceView";
import { CareerView } from "@/components/career/CareerView";
import { GamificationView } from "@/components/gamification/GamificationView";
import { LibraryView } from "@/components/library/LibraryView";
import { TransportView } from "@/components/transport/TransportView";
import { AlumniView } from "@/components/alumni/AlumniView";
import { WellnessView } from "@/components/wellness/WellnessView";
import { PollingView } from "@/components/polling/PollingView";
import { ServiceRequestModal } from "@/components/services/ServiceRequestModal";
import { HumanEscalationModal } from "@/components/escalation/HumanEscalationModal";
import { DistressSupportOverlay } from "@/components/distress/DistressSupportOverlay";
import { SecurityDrawer } from "@/components/security/SecurityDrawer";
import { StudentProfileDrawer } from "@/components/student-profile/StudentProfileDrawer";
import { NotificationsDrawer } from "@/components/notifications/NotificationsDrawer";
import { CommandBarModal } from "@/components/command-center/CommandBarModal";
import { Language } from "@/data/translations";
import { LanguageProvider, useLanguage } from "@/context/LanguageContext";
import { INITIAL_NOTIFICATIONS, NotificationItem } from "@/data/notifications";
import { INITIAL_SERVICES, ServiceRequest } from "@/data/services";
import { CURRENT_STUDENT } from "@/data/student";
import { ATTENDANCE_DATA } from "@/data/attendance";
import { AgentChatProvider, useAgentChat } from "@/context/AgentChatContext";
import { useStudent } from "@/context/StudentContext";
import { useDynamicSchedule } from "@/hooks/useDynamicSchedule";
import {
  ShieldCheck,
  HeartHandshake,
  Bot,
  Sparkles,
  AlertTriangle,
  Clock,
  Calendar,
  LifeBuoy,
} from "lucide-react";

function VignanAIContent() {
  const { studentData, logout } = useStudent();
  const student = studentData?.profile || CURRENT_STUDENT;
  const attendance = studentData?.attendance || ATTENDANCE_DATA;

  // Authentication State: First screen is the marketing Landing page,
  // then Login, then the authenticated dashboard.
  const [hasEnteredLogin, setHasEnteredLogin] = useState<boolean>(false);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);

  // Navigation & Localization
  const [activeTab, setActiveTab] = useState<string>("home");
  const { language: currentLang, setLanguage: setCurrentLang, t, tDynamic } = useLanguage();
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState<boolean>(false);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState<boolean>(false);

  // Notifications State
  const [notifications, setNotifications] = useState<NotificationItem[]>(INITIAL_NOTIFICATIONS);
  const unreadCount = notifications.filter((n) => !n.read).length;

  // Services State
  const [services, setServices] = useState<ServiceRequest[]>(INITIAL_SERVICES);

  // Modal / Drawer Visibility Flags
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [isSecurityDrawerOpen, setIsSecurityDrawerOpen] = useState(false);
  const [isCommandBarOpen, setIsCommandBarOpen] = useState(false);
  const [isServiceModalOpen, setIsServiceModalOpen] = useState(false);
  const [serviceModalCategory, setServiceModalCategory] = useState<string>("Certificate");
  const [isEscalationOpen, setIsEscalationOpen] = useState(false);
  const [escalationSummary, setEscalationSummary] = useState<string | undefined>();
  const [isDistressOpen, setIsDistressOpen] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);

  // Shared VIGBOT Chat Context
  const { isMaximized, setIsMaximized, handleSend, handleResetChat } = useAgentChat();

  const { nextClassSlot, formattedNextExamDate } = useDynamicSchedule();

  useEffect(() => {
    if (activeTab === "student-profile" || activeTab === "profile") {
      setIsProfileOpen(true);
      setActiveTab("home");
    }
  }, [activeTab]);

  const handleNavigateTab = (tab: string) => {
    if (tab === "student-profile" || tab === "profile") {
      setIsProfileOpen(true);
    } else {
      setActiveTab(tab);
    }
  };



  const handlePerformLogout = () => {
    logout();
    handleResetChat();
    setIsAuthenticated(false);
    setActiveTab("home");
  };

  const handleAskHelpdesk = (query: string) => {
    if (activeTab === "home") {
      handleSend(query);
      const el = document.getElementById("vignan-ai-central-workspace") || document.getElementById("vigbot-central-workspace");
      el?.scrollIntoView({ behavior: "smooth", block: "nearest" });
    } else {
      setIsChatOpen(true);
      handleSend(query);
    }
  };

  const handleSelectCommandQuery = (query: string) => {
    if (activeTab === "home") {
      handleSend(query);
      const el = document.getElementById("vignan-ai-central-workspace") || document.getElementById("vigbot-central-workspace");
      el?.scrollIntoView({ behavior: "smooth", block: "nearest" });
    } else {
      setIsChatOpen(true);
      handleSend(query);
    }
  };

  const handleOpenNewService = (category?: string) => {
    setServiceModalCategory(category || "Certificate");
    setIsServiceModalOpen(true);
  };

  const handleAddNewServiceRequest = (newReq: ServiceRequest) => {
    setServices((prev) => [newReq, ...prev]);
    setNotifications((prev) => [
      {
        id: `NOTIF-SR-${Date.now()}`,
        type: "SERVICE_UPDATE",
        title: "SERVICE UPDATE",
        message: `Your ${newReq.category} request (${newReq.title}) has been received and forwarded to Student Services.`,
        timestamp: "Just now",
        priority: "normal",
        read: false,
        sourceAgent: "VIGNAN-AI (Services)",
      },
      ...prev,
    ]);
  };

  const handleMarkAllNotificationsRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  };

  const handleSelectNotification = (item: NotificationItem) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === item.id ? { ...n, read: true } : n))
    );
    if (item.actionHref) {
      const tab = item.actionHref.replace("#", "");
      if (tab) setActiveTab(tab);
    }
  };

  // 1. First-time visitors see the marketing Landing page
  if (!hasEnteredLogin) {
    return <LandingPage onGetStarted={() => setHasEnteredLogin(true)} />;
  }

  // 2. Then the institutional Login screen
  if (!isAuthenticated) {
    return <LoginView onLogin={() => setIsAuthenticated(true)} />;
  }

  // 3. Once authenticated, display the unified VIGBOT Dashboard
  return (
    <div className="min-h-dvh flex bg-muted/50 text-foreground antialiased selection:bg-blue-600 selection:text-white">
      {/* Primary Navigation: Left Sidebar (stabilizes layout on full screen) */}
      <Sidebar
        activeTab={activeTab}
        onSelectTab={(tab) => {
          setActiveTab(tab);
          setIsMobileSidebarOpen(false);
        }}
        isOpenMobile={isMobileSidebarOpen}
        onCloseMobile={() => setIsMobileSidebarOpen(false)}
        onLogout={handlePerformLogout}
        onOpenProfile={() => setIsProfileOpen(true)}
        onOpenSecurityDrawer={() => setIsSecurityDrawerOpen(true)}
        currentLang={currentLang}
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={() => setIsSidebarCollapsed((v) => !v)}
      />

      {/* Main Content Column */}
      <div className="flex-1 flex flex-col min-w-0 overflow-x-hidden">
        {/* Top Header Bar */}
        <Header
          currentLang={currentLang}
          onLanguageChange={(lang) => setCurrentLang(lang)}
          unreadCount={unreadCount}
          onOpenNotifications={() => setIsNotificationsOpen(true)}
          onOpenProfile={() => setIsProfileOpen(true)}
          onOpenSecurityDrawer={() => setIsSecurityDrawerOpen(true)}
          onOpenCommandBar={() => setIsCommandBarOpen(true)}
          onToggleMobileMenu={() => setIsMobileSidebarOpen(true)}
          onLogout={handlePerformLogout}
        />

        {/* Dynamic Page Content */}
        <main className="@container flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6 pb-24 lg:pb-8 space-y-6">
          {/* HOME TAB: AI Agent Helpdesk Core front & center */}
          {activeTab === "home" && (
            <div className="space-y-6">
              {/* 1. Compact Context & Welcome Banner */}
              <div className="relative overflow-hidden rounded-lg border border-slate-200 bg-card p-4 sm:p-5 shadow-sm">
                <div className="relative z-10 flex flex-col @2xl:flex-row @2xl:items-center justify-between gap-4">
                  <div className="space-y-1.5 max-w-2xl">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="inline-flex items-center gap-1.5 rounded-full bg-blue-50 px-2.5 py-0.5 text-sm font-semibold text-blue-700 border border-blue-200 whitespace-nowrap">
                        <Sparkles className="h-3 w-3" />
                        {t.vignanAiCoreActive || t.vigbotCoreActive || "VIGNAN-AI CORE ACTIVE"}
                      </span>
                      <button
                        onClick={() => setIsSecurityDrawerOpen(true)}
                        className="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 px-2.5 py-0.5 text-sm font-medium text-emerald-700 border border-emerald-200 hover:bg-emerald-100 transition-colors cursor-pointer whitespace-nowrap"
                        title="Click to view Row-Level Security verification"
                      >
                        <ShieldCheck className="h-3.5 w-3.5" />
                        <span>{t.rlsGuardrailVerified}: {student.id}</span>
                      </button>
                    </div>

                    <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-foreground">
                      {t.welcomeBack}, {student.name}
                    </h1>
                    <p className="text-xs sm:text-sm text-muted-foreground font-normal max-w-xl leading-relaxed">
                      {t.heroSubtitle}
                    </p>
                  </div>

                  {/* Telemetry Quick Pills */}
                  <div className="hidden sm:flex flex-wrap @2xl:flex-col gap-2 shrink-0">
                    <button
                      onClick={() => setActiveTab("attendance")}
                      className="flex items-center justify-between gap-3 rounded-xl border border-slate-200 bg-muted/30 px-3 py-1.5 text-xs text-foreground hover:bg-muted/60 transition-colors cursor-pointer"
                    >
                      <span className="flex items-center gap-1.5 text-amber-600">
                        <AlertTriangle className="h-3.5 w-3.5" />
                        <span>{t.navAttendance}</span>
                      </span>
                      <span className="font-bold">{attendance.overallPercentage}%</span>
                    </button>

                    <button
                      onClick={() => setActiveTab("timetable")}
                      className="flex items-center justify-between gap-3 rounded-xl border border-slate-200 bg-muted/30 px-3 py-1.5 text-xs text-foreground hover:bg-muted/60 transition-colors cursor-pointer"
                    >
                      <span className="flex items-center gap-1.5 text-blue-600">
                        <Clock className="h-3.5 w-3.5" />
                        <span>{t.nextClass}</span>
                      </span>
                      <span className="font-bold">{nextClassSlot ? nextClassSlot.time.split("–")[0].trim() : "12:30 PM"}</span>
                    </button>

                    <button
                      onClick={() => setActiveTab("exams")}
                      className="flex items-center justify-between gap-3 rounded-xl border border-slate-200 bg-muted/30 px-3 py-1.5 text-xs text-foreground hover:bg-muted/60 transition-colors cursor-pointer"
                    >
                      <span className="flex items-center gap-1.5 text-indigo-600">
                        <Calendar className="h-3.5 w-3.5" />
                        <span>{t.nextExam}</span>
                      </span>
                      <span className="font-bold">{formattedNextExamDate}</span>
                    </button>
                  </div>
                </div>
              </div>

              {/* 2. Large Central VIGNAN-AI Interface */}
              <div id="vignan-ai-central-workspace" className="w-full">
                <AiHelpdeskPanel
                  variant="central"
                  onNavigateTab={handleNavigateTab}
                  onOpenServiceModal={handleOpenNewService}
                  onOpenEscalation={(summary) => {
                    setEscalationSummary(summary);
                    setIsEscalationOpen(true);
                  }}
                  onTriggerDistressSupport={() => setIsDistressOpen(true)}
                />
              </div>

              {/* 3. Academic Snapshot (6 KPI cards - each leads to respective tab) */}
              <div className="pt-2">
                <StudentSnapshot onNavigateTab={handleNavigateTab} />
              </div>

              {/* 4. Academic Routine & Examination Overview (Full Width & Uncramped) */}
              <div className="space-y-8 pt-2">
                <TimetableView onAskHelpdesk={handleAskHelpdesk} />
                <ExaminationsView onAskHelpdesk={handleAskHelpdesk} />
              </div>
            </div>
          )}

          {/* Tab: Attendance */}
          {activeTab === "attendance" && (
            <AttendanceView onAskHelpdesk={handleAskHelpdesk} />
          )}

          {/* Tab: Marks */}
          {activeTab === "marks" && (
            <MarksView onAskHelpdesk={handleAskHelpdesk} />
          )}

          {/* Tab: Gamification */}
          {activeTab === "gamification" && <GamificationView />}

          {/* Tab: Library */}
          {activeTab === "library" && <LibraryView />}

          {/* Tab: Timetable */}
          {activeTab === "timetable" && (
            <TimetableView onAskHelpdesk={handleAskHelpdesk} />
          )}

          {/* Tab: Exams */}
          {activeTab === "exams" && (
            <ExaminationsView onAskHelpdesk={handleAskHelpdesk} />
          )}

          {/* Tab: Fees */}
          {activeTab === "fees" && (
            <FeesView onAskHelpdesk={handleAskHelpdesk} />
          )}

          {/* Tab: Curriculum */}
          {activeTab === "curriculum" && (
            <CurriculumView onAskHelpdesk={handleAskHelpdesk} />
          )}

          {/* Tab: Policies */}
          {activeTab === "policies" && (
            <PoliciesView onAskHelpdesk={handleAskHelpdesk} />
          )}

          {/* Tab: Circulars */}
          {activeTab === "circulars" && (
            <CircularsView onAskHelpdesk={handleAskHelpdesk} />
          )}

          {/* Tab: Clubs & Communities */}
          {activeTab === "clubs" && (
            <ClubsView />
          )}

          {/* Tab: Lost & Found */}
          {activeTab === "lost-and-found" && (
            <LostAndFoundView />
          )}

          {/* Tab: Bookings */}
          {activeTab === "bookings" && (
            <BookingsView />
          )}

          {/* Tab: Calendar */}
          {activeTab === "calendar" && (
            <CalendarView
              onAskHelpdesk={handleAskHelpdesk}
              onNavigateTab={handleNavigateTab}
            />
          )}

          {/* Tab: Map */}
          {activeTab === "map" && <CampusMapView />}

          {/* Tab: Events */}
          {activeTab === "events" && <EventRegistrationView />}

          {/* Tab: Hostel */}
          {activeTab === "hostel" && <HostelManagementView />}

          {/* Tab: Marketplace */}
          {activeTab === "marketplace" && <MarketplaceView />}

          {/* Tab: Transport */}
          {activeTab === "transport" && <TransportView />}

          {/* Tab: Alumni */}
          {activeTab === "alumni" && <AlumniView />}

          {/* Tab: Polling */}
          {activeTab === "polling" && <PollingView />}

          {/* Tab: Wellness */}
          {activeTab === "wellness" && <WellnessView />}

          {/* Tab: Career */}
          {activeTab === "career" && <CareerView />}

          {/* Tab: Services */}
          {activeTab === "services" && (
            <StudentServicesView
              services={services}
              onOpenNewServiceModal={handleOpenNewService}
              onAskHelpdesk={handleAskHelpdesk}
            />
          )}
        </main>

        {/* Global Modals & Drawers */}
        <NotificationsDrawer
          isOpen={isNotificationsOpen}
          notifications={notifications}
          onClose={() => setIsNotificationsOpen(false)}
          onMarkAllRead={handleMarkAllNotificationsRead}
          onSelectNotification={handleSelectNotification}
        />

        <StudentProfileDrawer
          isOpen={isProfileOpen}
          onClose={() => setIsProfileOpen(false)}
          onAskHelpdesk={handleAskHelpdesk}
          onLogout={() => {
            setIsProfileOpen(false);
            setIsAuthenticated(false);
            setActiveTab("home");
          }}
        />

        <SecurityDrawer
          isOpen={isSecurityDrawerOpen}
          onClose={() => setIsSecurityDrawerOpen(false)}
        />

        <CommandBarModal
          isOpen={isCommandBarOpen}
          onClose={() => setIsCommandBarOpen(false)}
          onSelectQuery={handleSelectCommandQuery}
        />

        <ServiceRequestModal
          isOpen={isServiceModalOpen}
          initialCategory={serviceModalCategory}
          onClose={() => setIsServiceModalOpen(false)}
          onSubmitRequest={handleAddNewServiceRequest}
        />

        <HumanEscalationModal
          isOpen={isEscalationOpen}
          contextSummary={escalationSummary}
          onClose={() => setIsEscalationOpen(false)}
        />

        {/* Mandatory Distress Detection Support Overlay */}
        <DistressSupportOverlay
          isOpen={isDistressOpen}
          onClose={() => setIsDistressOpen(false)}
          onConnectHuman={() => {
            setIsDistressOpen(false);
            setIsEscalationOpen(true);
          }}
        />

        {/* Fullscreen Maximized VIGBOT Workspace Modal */}
        {isMaximized && (
          <div
            className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 md:p-8 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-200"
            role="dialog"
            aria-modal="true"
            aria-label="VIGNAN-AI Fullscreen Workspace"
          >
            <div className="w-full max-w-[92vw] h-[88vh] bg-card rounded-xl shadow-2xl overflow-hidden animate-in zoom-in-95 duration-200 flex flex-col border border-slate-200">
              <AiHelpdeskPanel
                variant="maximized"
                fillHeight
                onNavigateTab={(tab) => {
                  setActiveTab(tab);
                  setIsMaximized(false);
                }}
                onOpenServiceModal={(cat) => {
                  setIsMaximized(false);
                  handleOpenNewService(cat);
                }}
                onOpenEscalation={(summary) => {
                  setIsMaximized(false);
                  setEscalationSummary(summary);
                  setIsEscalationOpen(true);
                }}
                onTriggerDistressSupport={() => {
                  setIsMaximized(false);
                  setIsDistressOpen(true);
                }}
              />
            </div>
          </div>
        )}

        {/* Institutional Footer */}
        <footer className="mt-8 border-t border-slate-200 bg-card py-6 text-xs text-muted-foreground">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2.5">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600 text-white font-bold text-xs shadow-xs">
                <Bot className="h-4 w-4" />
              </div>
              <div>
                <div className="font-bold text-foreground">
                  {t.footerBrand}
                </div>
                <div className="text-sm text-muted-foreground">
                  {t.footerSub}
                </div>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-4 text-xs">
              <button
                onClick={() => setIsSecurityDrawerOpen(true)}
                className="flex items-center gap-1 text-muted-foreground hover:text-blue-600 cursor-pointer"
              >
                <ShieldCheck className="h-3.5 w-3.5 text-emerald-600" />
                <span>{t.footerRls}</span>
              </button>
              <button
                onClick={() => setIsDistressOpen(true)}
                className="flex items-center gap-1 text-rose-600 hover:underline cursor-pointer"
              >
                <HeartHandshake className="h-3.5 w-3.5" />
                <span>{t.footerDistress}</span>
              </button>
              <button
                onClick={() => setIsEscalationOpen(true)}
                className="flex items-center gap-1 text-muted-foreground hover:text-foreground cursor-pointer"
              >
                <LifeBuoy className="h-3.5 w-3.5 text-violet-600" />
                <span>{t.footerEscalation}</span>
              </button>
            </div>

            <div className="text-right text-sm text-slate-400">
              {t.authenticatedLabel}: {student.name} ({student.id})
            </div>
          </div>
        </footer>
      </div>

      {/* AI Helpdesk Side Panel: Used exclusively on internal pages (Attendance, Marks, Timetable, etc.) */}
      {activeTab !== "home" && isChatOpen && (
        <div className="hidden lg:sticky lg:top-0 lg:flex lg:h-dvh w-[390px] xl:w-[410px] shrink-0 flex-col border-l border-slate-200 bg-card shadow-sm">
          <AiHelpdeskPanel
            variant="side"
            fillHeight
            onClose={() => setIsChatOpen(false)}
            onNavigateTab={(tab) => {
              setActiveTab(tab);
              setIsChatOpen(false);
            }}
            onOpenServiceModal={(cat) => {
              setIsChatOpen(false);
              handleOpenNewService(cat);
            }}
            onOpenEscalation={(summary) => {
              setIsChatOpen(false);
              setEscalationSummary(summary);
              setIsEscalationOpen(true);
            }}
            onTriggerDistressSupport={() => {
              setIsChatOpen(false);
              setIsDistressOpen(true);
            }}
          />
        </div>
      )}

      {/* On narrow/mobile viewports the side panel overlays on internal pages */}
      {activeTab !== "home" && isChatOpen && (
        <div className="fixed inset-y-0 right-0 z-50 flex h-full w-full flex-col bg-card shadow-2xl animate-in slide-in-from-right duration-300 lg:hidden">
          <AiHelpdeskPanel
            variant="side"
            fillHeight
            onClose={() => setIsChatOpen(false)}
            onNavigateTab={(tab) => {
              setActiveTab(tab);
              setIsChatOpen(false);
            }}
            onOpenServiceModal={(cat) => {
              setIsChatOpen(false);
              handleOpenNewService(cat);
            }}
            onOpenEscalation={(summary) => {
              setIsChatOpen(false);
              setEscalationSummary(summary);
              setIsEscalationOpen(true);
            }}
            onTriggerDistressSupport={() => {
              setIsChatOpen(false);
              setIsDistressOpen(true);
            }}
          />
        </div>
      )}

      {/* Floating AI Helpdesk Launcher: available on internal pages when side panel is closed */}
      {activeTab !== "home" && !isChatOpen && (
        <button
          onClick={() => setIsChatOpen(true)}
          className="fixed bottom-6 right-6 z-40 flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-tr from-blue-600 to-indigo-600 text-white shadow-lg shadow-blue-600/30 hover:scale-105 transition-transform cursor-pointer"
          title="Ask VIGNAN-AI"
          aria-label="Open VIGNAN-AI chat"
        >
          <Bot className="h-6 w-6" />
          {unreadCount > 0 && (
            <span className="absolute -top-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-rose-500 text-sm font-bold text-white ring-2 ring-white">
              {unreadCount}
            </span>
          )}
        </button>
      )}
    </div>
  );
}

export default function Home() {
  return (
    <LanguageProvider>
      <AgentChatProvider>
        <VignanAIContent />
      </AgentChatProvider>
    </LanguageProvider>
  );
}
