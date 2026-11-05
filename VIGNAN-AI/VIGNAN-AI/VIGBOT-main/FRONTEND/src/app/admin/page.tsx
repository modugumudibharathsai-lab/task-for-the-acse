"use client";

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  fetchAllTickets,
  updateTicketStatus,
  deleteTicket,
  fetchCognitiveRemediations,
  updateRemediationStatus,
  deleteRemediationRule,
  fetchGeminiStatus,
  updateGeminiConfig,
  pingGeminiConnection
} from '@/actions/admin';
import { getAnalyticsData } from '@/actions/analytics';
import { getAllBroadcasts, toggleBroadcastStatus, deleteBroadcast, createBroadcast } from '@/actions/broadcasts';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line, AreaChart, Area
} from 'recharts';
import {
  LogOut,
  ShieldCheck,
  Search,
  Filter,
  MessageSquareWarning,
  Users,
  CheckCircle2,
  Clock,
  XCircle,
  MoreVertical,
  Activity,
  Calendar,
  PackageSearch,
  BarChart3,
  Radio,
  Plus,
  Trash2,
  AlertTriangle,
  HeartPulse,
  KanbanSquare,
  Database,
  BookOpen,
  Power,
  Terminal,
  FileText,
  Send,
  Eye,
  Settings,
  ChevronRight,
  Bot,
  RefreshCw,
  Scale,
  Headset,
  FileCheck,
  Gavel,
  Download,
  Ear,
  MessageSquareOff,
  Map,
  TrendingDown,
  ScatterChart,
  ShieldAlert,
  Mic,
  UserX,
  AlertOctagon,
  MessageCircle,
  Video,
  UserPlus,
  Bell,
  Sparkles,
  KeyRound,
  Zap,
  Check,
  ExternalLink,
  Shield,
  ThumbsDown,
  ToggleLeft,
  ToggleRight,
  Sliders,
  CheckCircle,
  AlertCircle,
  Lock,
  ChevronDown,
  Layers,
  Cpu,
  Server,
  PanelLeftClose,
  PanelLeftOpen,
  Menu,
  X,
  Copy
} from 'lucide-react';

interface ServiceRequest {
  id: string;
  request_no: string;
  student_id: string;
  category: string;
  title: string;
  description: string;
  status: string;
  created_at: string;
  sla_due_date?: string;
  assigned_office?: string;
}

interface HostelRequest {
  id: number;
  student_id: string;
  type: string;
  details: string;
  status: string;
  created_at: string;
}

interface Grievance {
  id: string;
  student_id: string;
  category: string;
  description: string;
  status: string;
  timestamp: string;
  withdrawal_reason?: string;
}

interface ClubApp {
  id: number;
  student_name: string;
  club_id: string;
  status: string;
  timestamp: string;
  withdrawal_reason?: string;
}

interface FacilityBooking {
  id: number;
  student_id: string;
  facility_id: string;
  date: string;
  start_time: string;
  end_time: string;
  purpose: string;
  status: string;
}

interface NavItem {
  id: string;
  label: string;
  icon: React.ReactNode;
  badge?: string;
  badgeClass?: string;
  count?: number;
  countClass?: string;
  isAi?: boolean;
}

interface NavSection {
  title: string;
  items: NavItem[];
}

interface LostAndFound {
  id: number;
  student_id: string;
  type: string;
  title: string;
  description: string;
  date_posted: string;
  status: string;
}

export default function AdminDashboard() {
  const [adminUser, setAdminUser] = useState<{ username: string; role: string; name: string } | null>(null);
  const [activeTab, setActiveTab] = useState<
    'service_requests' | 'hostel_requests' | 'grievances' | 'clubs' | 'bookings' | 'lost_found' |
    'compliance' | 'live_sessions' | 'verifications' | 'distress' | 'health' | 'kanban' | 'audit' |
    'knowledge' | 'analytics' | 'broadcasts' | 'remediation'
  >('remediation');
  const [loading, setLoading] = useState(true);
  const [currentTime, setCurrentTime] = useState<string>('');
  const [sidebarFilter, setSidebarFilter] = useState('');
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // Data states
  const [serviceRequests, setServiceRequests] = useState<ServiceRequest[]>([]);
  const [hostelRequests, setHostelRequests] = useState<HostelRequest[]>([]);
  const [grievances, setGrievances] = useState<Grievance[]>([]);
  const [clubApps, setClubApps] = useState<ClubApp[]>([]);
  const [bookings, setBookings] = useState<FacilityBooking[]>([]);
  const [lostAndFound, setLostAndFound] = useState<LostAndFound[]>([]);
  const [analytics, setAnalytics] = useState<any>(null);
  const [broadcasts, setBroadcasts] = useState<any[]>([]);

  // Search filter
  const [searchQuery, setSearchQuery] = useState('');

  // Broadcast state
  const [newBroadcastMsg, setNewBroadcastMsg] = useState('');
  const [newBroadcastType, setNewBroadcastType] = useState('INFO');

  const router = useRouter();

  // Clock effect for command center
  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setCurrentTime(
        now.toLocaleTimeString('en-IN', {
          timeZone: 'Asia/Kolkata',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
          hour12: true
        }) + ' IST'
      );
    };
    updateTime();
    const timer = setInterval(updateTime, 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    // Check auth
    const session = localStorage.getItem('adminSession');
    if (!session) {
      router.push('/admin/login');
      return;
    }
    setAdminUser(JSON.parse(session));
    loadData();
  }, [router]);

  const loadData = async () => {
    setLoading(true);
    try {
      const token = typeof window !== "undefined" ? (localStorage.getItem('adminToken') || undefined) : undefined;
      const data = await fetchAllTickets(token);
      if (data && data.success) {
        setServiceRequests(data.serviceRequests || []);
        setHostelRequests(data.hostelRequests || []);
        setGrievances(data.grievances || []);
        setClubApps(data.clubApps || []);
        setBookings(data.bookings || []);
        setLostAndFound(data.lostAndFound || []);
      }

      const analyticsData = await getAnalyticsData();
      if (analyticsData) setAnalytics(analyticsData);

      const broadcastsData = await getAllBroadcasts();
      if (broadcastsData && broadcastsData.broadcasts) setBroadcasts(broadcastsData.broadcasts);

    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('adminSession');
    localStorage.removeItem('adminToken');
    router.push('/admin/login');
  };

  const handleStatusUpdate = async (id: string | number, type: 'service_request' | 'hostel' | 'grievance' | 'club' | 'booking' | 'lost_found', status: string) => {
    const token = typeof window !== "undefined" ? (localStorage.getItem('adminToken') || undefined) : undefined;
    await updateTicketStatus(id, type, status, token);
    loadData();
  };

  const handleDeleteTicket = async (id: string | number, type: 'service_request' | 'hostel' | 'grievance' | 'club' | 'booking' | 'lost_found') => {
    if (!confirm('Are you sure you want to permanently delete this item?')) return;
    const token = typeof window !== "undefined" ? (localStorage.getItem('adminToken') || undefined) : undefined;
    await deleteTicket(id, type, token);
    loadData();
  };

  const handleCreateBroadcast = async () => {
    if (!newBroadcastMsg.trim()) return;
    const res = await createBroadcast(newBroadcastMsg, newBroadcastType);
    if (res.success) {
      setNewBroadcastMsg('');
      loadData();
    }
  };

  const handleToggleBroadcast = async (id: number, currentStatus: number) => {
    await toggleBroadcastStatus(id, !currentStatus);
    loadData();
  };

  const handleDeleteBroadcast = async (id: number) => {
    await deleteBroadcast(id);
    loadData();
  };

  const getStatusBadgeColor = (status: string) => {
    const s = status.toLowerCase();
    if (s.includes('resolved') || s.includes('approved') || s.includes('confirmed') || s.includes('claimed')) {
      return 'bg-emerald-50 text-emerald-700 border-emerald-200';
    }
    if (s.includes('withdrawn') || s.includes('rejected') || s.includes('cancelled')) {
      return 'bg-rose-50 text-rose-700 border-rose-200';
    }
    if (s.includes('investigation') || s.includes('forwarded') || s.includes('open') || s.includes('pending') || s.includes('in_review') || s.includes('submitted')) {
      return 'bg-amber-50 text-amber-700 border-amber-200';
    }
    return 'bg-blue-50 text-blue-700 border-blue-200';
  };

  const getStatusIcon = (status: string) => {
    const s = status.toLowerCase();
    if (s.includes('resolved') || s.includes('approved')) return <CheckCircle2 className="w-3.5 h-3.5 mr-1 text-emerald-600" />;
    if (s.includes('withdrawn') || s.includes('rejected')) return <XCircle className="w-3.5 h-3.5 mr-1 text-rose-600" />;
    if (s.includes('investigation') || s.includes('forwarded')) return <Activity className="w-3.5 h-3.5 mr-1 text-amber-600" />;
    return <Clock className="w-3.5 h-3.5 mr-1 text-blue-600" />;
  };

  if (!adminUser) {
    return (
      <div className="min-h-dvh bg-slate-50 flex items-center justify-center font-sans text-slate-800">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-3 border-blue-600 border-t-transparent rounded-full animate-spin" />
          <p className="text-xs font-semibold text-slate-500 font-mono tracking-wider">INITIALIZING NODAL OFFICER COMMAND CENTER...</p>
        </div>
      </div>
    );
  }

  const filteredServiceRequests = serviceRequests.filter(s =>
    (s.request_no && s.request_no.toLowerCase().includes(searchQuery.toLowerCase())) ||
    (s.student_id && s.student_id.toLowerCase().includes(searchQuery.toLowerCase())) ||
    (s.title && s.title.toLowerCase().includes(searchQuery.toLowerCase())) ||
    (s.category && s.category.toLowerCase().includes(searchQuery.toLowerCase())) ||
    (s.description && s.description.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  const filteredHostelRequests = hostelRequests.filter(h =>
    (h.student_id && h.student_id.toLowerCase().includes(searchQuery.toLowerCase())) ||
    (h.type && h.type.toLowerCase().includes(searchQuery.toLowerCase())) ||
    (h.details && h.details.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  const filteredGrievances = grievances.filter(g => 
    g.id.toLowerCase().includes(searchQuery.toLowerCase()) || 
    g.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredClubApps = clubApps.filter(c => 
    c.student_name.toLowerCase().includes(searchQuery.toLowerCase()) || 
    c.club_id.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredBookings = bookings.filter(b => 
    b.student_id.toLowerCase().includes(searchQuery.toLowerCase()) || 
    b.purpose.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredLostAndFound = lostAndFound.filter(l => 
    l.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
    l.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
    l.student_id.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Navigation Items definitions
  const navSections: NavSection[] = [
    {
      title: 'AI & Cognitive Surveillance',
      items: [
        {
          id: 'remediation',
          label: 'AI Remediation & Gemini',
          icon: <Sparkles className="w-4 h-4 text-purple-400" />,
          badge: 'Live',
          badgeClass: 'bg-purple-500/20 text-purple-300 border border-purple-500/30 animate-pulse',
          isAi: true
        }
      ]
    },
    {
      title: 'Surveillance & Student Triage',
      items: [
        {
          id: 'distress',
          label: 'Distress Protocols',
          icon: <AlertOctagon className="w-4 h-4 text-rose-600" />,
          badge: '3 Active',
          badgeClass: 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
        },
        {
          id: 'grievances',
          label: 'Student Grievances',
          icon: <MessageSquareWarning className="w-4 h-4 text-amber-600" />,
          count: grievances.length,
          countClass: 'bg-amber-500/10 text-amber-300 border border-amber-500/20'
        },
        {
          id: 'live_sessions',
          label: 'Live Session Shadowing',
          icon: <Headset className="w-4 h-4 text-cyan-400" />,
          badge: 'Live Agent',
          badgeClass: 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
        }
      ]
    },
    {
      title: 'Campus Desk & Services',
      items: [
        {
          id: 'service_requests',
          label: 'Service Requests',
          icon: <FileCheck className="w-4 h-4 text-blue-600" />,
          count: serviceRequests.length,
          countClass: 'bg-blue-500/10 text-blue-300 border border-blue-500/20'
        },
        {
          id: 'hostel_requests',
          label: 'Hostel & Mess Requests',
          icon: <Users className="w-4 h-4 text-indigo-400" />,
          count: hostelRequests.length,
          countClass: 'bg-indigo-500/10 text-indigo-300 border border-indigo-500/20'
        },
        {
          id: 'bookings',
          label: 'Facility Bookings',
          icon: <Calendar className="w-4 h-4 text-emerald-600" />,
          count: bookings.length,
          countClass: 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/20'
        },
        {
          id: 'lost_found',
          label: 'Lost & Found Registry',
          icon: <PackageSearch className="w-4 h-4 text-amber-600" />,
          count: lostAndFound.length,
          countClass: 'bg-amber-500/10 text-amber-300 border border-amber-500/20'
        },
        {
          id: 'clubs',
          label: 'Student Clubs & Orgs',
          icon: <Users className="w-4 h-4 text-violet-400" />,
          count: clubApps.length,
          countClass: 'bg-violet-500/10 text-violet-300 border border-violet-500/20'
        }
      ]
    },
    {
      title: 'Statutory & Governance',
      items: [
        {
          id: 'compliance',
          label: 'Academic Compliance',
          icon: <Scale className="w-4 h-4 text-purple-400" />,
          badge: 'SLA Risk',
          badgeClass: 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
        },
        {
          id: 'verifications',
          label: 'Document Verifications',
          icon: <CheckCircle2 className="w-4 h-4 text-emerald-600" />,
          badge: 'Crypto',
          badgeClass: 'bg-blue-500/20 text-blue-300 border border-blue-500/30'
        },
        {
          id: 'health',
          label: 'Agent Telemetry & Health',
          icon: <HeartPulse className="w-4 h-4 text-rose-600" />,
          badge: '99.98%',
          badgeClass: 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
        },
        {
          id: 'kanban',
          label: 'Grievance Kanban',
          icon: <KanbanSquare className="w-4 h-4 text-blue-600" />
        },
        {
          id: 'audit',
          label: 'System Audit Logs',
          icon: <Database className="w-4 h-4 text-slate-400" />
        },
        {
          id: 'knowledge',
          label: 'Knowledge Base (RAG)',
          icon: <BookOpen className="w-4 h-4 text-amber-600" />
        },
        {
          id: 'broadcasts',
          label: 'Broadcasts & Directives',
          icon: <Radio className="w-4 h-4 text-cyan-400" />
        },
        {
          id: 'analytics',
          label: 'Real-Time Analytics',
          icon: <BarChart3 className="w-4 h-4 text-blue-600" />
        }
      ]
    }
  ];

  const getActiveTabInfo = () => {
    for (const sec of navSections) {
      const match = sec.items.find(it => it.id === activeTab);
      if (match) return { section: sec.title, label: match.label, icon: match.icon };
    }
    return { section: 'Command Center', label: 'Dashboard', icon: <Lock className="w-4 h-4 text-blue-600" /> };
  };
  const activeInfo = getActiveTabInfo();

  return (
    <div className="min-h-dvh bg-slate-50 text-slate-900 flex flex-col font-sans selection:bg-blue-100 selection:text-blue-900">
      {/* Institutional Command Header - Spacious, Balanced & Executive */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-40 shadow-xs backdrop-blur-md">
        <div className="w-full px-4 sm:px-6">
          <div className="flex justify-between items-center h-16">
            {/* Left: Mobile Drawer Trigger + Desktop Rail Collapse + Brand & Breadcrumb */}
            <div className="flex items-center gap-3 sm:gap-4">
              {/* Mobile Drawer Trigger (lg:hidden) */}
              <button
                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                className="lg:hidden p-2 text-slate-500 hover:text-slate-900 hover:bg-slate-100 rounded-xl border border-slate-200 transition-colors cursor-pointer"
                title="Open navigation drawer"
                aria-label="Open navigation drawer"
              >
                <Menu className="w-5 h-5 text-blue-600" />
              </button>

              {/* Desktop Sidebar Collapse Toggle (hidden lg:flex) */}
              <button
                onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
                className="hidden lg:flex p-2 text-slate-500 hover:text-slate-900 hover:bg-slate-100 rounded-xl border border-slate-200 hover:border-slate-300 transition-all cursor-pointer group"
                title={isSidebarCollapsed ? "Expand sidebar rail" : "Collapse sidebar rail"}
                aria-label="Toggle sidebar collapse"
              >
                {isSidebarCollapsed ? (
                  <PanelLeftOpen className="w-4 h-4 text-blue-600 group-hover:scale-110 transition-transform" />
                ) : (
                  <PanelLeftClose className="w-4 h-4 text-slate-500 group-hover:text-blue-600 group-hover:scale-110 transition-all" />
                )}
              </button>

              {/* Brand Logo & Title matching Screenshot 2 */}
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 bg-slate-900 text-white rounded-xl flex items-center justify-center shadow-xs shrink-0">
                  <Shield className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h1 className="font-bold text-base leading-tight text-slate-900 tracking-tight">Nodal Officer Portal</h1>
                  <p className="text-[10px] text-slate-400 font-mono font-semibold tracking-wider uppercase mt-0.5">COMMAND CENTER</p>
                </div>
              </div>

              {/* Discreet Section Breadcrumb on Desktop */}
              <div className="hidden xl:flex items-center gap-2 text-xs text-slate-400 pl-4 border-l border-slate-200">
                <span className="text-slate-400 font-medium">{activeInfo.section}</span>
                <ChevronRight className="w-3.5 h-3.5 text-slate-300" />
                <span className="text-slate-700 font-semibold flex items-center gap-1.5">
                  {activeInfo.icon}
                  {activeInfo.label}
                </span>
              </div>
            </div>

            {/* Right: Sleek Telemetry Pod + User profile & Logout */}
            <div className="flex items-center gap-3">
              {/* Compact Unified Telemetry Pill */}
              <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-50 border border-slate-200 text-xs font-mono text-slate-600 shadow-2xs">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </span>
                <span className="font-semibold text-emerald-700">Neon DB Synced</span>
                {currentTime && (
                  <>
                    <span className="text-slate-300">•</span>
                    <span className="text-slate-600">{currentTime}</span>
                  </>
                )}
              </div>

              {/* User Profile Card */}
              <div className="flex items-center gap-2.5 bg-slate-50 border border-slate-200 rounded-xl px-3 py-1.5 text-xs shadow-2xs">
                <div className="w-7 h-7 rounded-full bg-blue-100 border border-blue-200 text-blue-700 flex items-center justify-center font-bold text-xs">
                  {adminUser.name.charAt(0)}
                </div>
                <div className="hidden sm:block text-left">
                  <div className="text-slate-900 font-semibold leading-tight">{adminUser.name}</div>
                  <div className="text-[10px] text-slate-400 font-mono">{adminUser.role}</div>
                </div>
              </div>

              {/* Logout Button */}
              <button 
                onClick={handleLogout}
                className="p-2 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-xl border border-transparent hover:border-rose-200 transition-all cursor-pointer"
                title="Sign out of Command Center"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Mobile Drawer (Visible on < lg screens when toggled) */}
      {isMobileMenuOpen && (
        <div className="fixed inset-0 z-50 flex lg:hidden">
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs transition-opacity"
            onClick={() => setIsMobileMenuOpen(false)}
          />

          {/* Drawer Panel */}
          <div className="relative w-80 max-w-[85vw] bg-white border-r border-slate-200 flex flex-col justify-between p-4 shadow-2xl z-10 overflow-y-auto animate-in slide-in-from-left duration-200">
            <div className="space-y-4">
              {/* Drawer Header */}
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 bg-blue-500/10 border border-blue-500/20 rounded-lg flex items-center justify-center">
                    <Lock className="w-4 h-4 text-blue-600" />
                  </div>
                  <div>
                    <h2 className="text-sm font-bold text-slate-900">Nodal Navigation</h2>
                    <p className="text-[10px] text-slate-400">Institutional Modules</p>
                  </div>
                </div>
                <button
                  onClick={() => setIsMobileMenuOpen(false)}
                  className="p-1.5 text-slate-500 hover:text-slate-900 hover:bg-slate-100 rounded-lg border border-slate-200 transition-colors cursor-pointer"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Module Filter Input */}
              <div className="relative">
                <Search className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="Filter navigation..."
                  value={sidebarFilter}
                  onChange={e => setSidebarFilter(e.target.value)}
                  className="w-full pl-8 pr-7 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all"
                />
                {sidebarFilter && (
                  <button
                    onClick={() => setSidebarFilter('')}
                    className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 text-xs cursor-pointer"
                  >
                    ✕
                  </button>
                )}
              </div>

              {/* Navigation Sections */}
              <div className="space-y-4">
                {navSections.map((sec, secIdx) => {
                  const filteredItems = sec.items.filter(item =>
                    item.label.toLowerCase().includes(sidebarFilter.toLowerCase())
                  );
                  if (filteredItems.length === 0) return null;

                  return (
                    <div key={secIdx} className="space-y-1">
                      <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider px-3 mb-1.5">
                        {sec.title}
                      </div>

                      <div className="space-y-0.5">
                        {filteredItems.map(item => {
                          const isSelected = activeTab === item.id;
                          return (
                            <button
                              key={item.id}
                              onClick={() => {
                                setActiveTab(item.id as any);
                                setIsMobileMenuOpen(false);
                              }}
                              className={`w-full px-3 py-2.5 text-xs font-medium rounded-xl transition-all duration-150 flex items-center justify-between text-left group cursor-pointer relative ${
                                isSelected
                                  ? 'bg-blue-50 text-blue-700 border border-blue-200/80 font-bold shadow-2xs before:absolute before:left-0 before:top-2 before:bottom-2 before:w-1 before:bg-blue-600 before:rounded-r-md'
                                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100/70 border border-transparent'
                              }`}
                            >
                              <span className="flex items-center gap-2.5 truncate pl-1">
                                <span className={`shrink-0 transition-transform group-hover:scale-110 ${isSelected ? 'text-blue-600' : 'text-slate-400'}`}>
                                  {item.icon}
                                </span>
                                <span className="truncate">{item.label}</span>
                              </span>

                              <div className="flex items-center gap-1.5 shrink-0 ml-2">
                                {item.badge && (
                                  <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-bold ${item.badgeClass || 'bg-slate-100 text-slate-600'}`}>
                                    {item.badge}
                                  </span>
                                )}
                                {item.count !== undefined && item.count > 0 && (
                                  <span className={`text-[10px] px-1.5 py-0.2 rounded-full font-mono font-bold ${item.countClass || 'bg-slate-100 text-slate-600'}`}>
                                    {item.count}
                                  </span>
                                )}
                              </div>
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Mobile Drawer Telemetry Pod */}
            <div className="pt-3 border-t border-slate-100">
              <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 space-y-1.5 text-[10px] font-mono text-slate-600">
                <div className="flex justify-between items-center text-slate-900 font-bold">
                  <span>TELEMETRY ONLINE</span>
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                </div>
                <div className="flex justify-between">
                  <span>Neon DB:</span>
                  <span className="text-emerald-600 font-bold">Synced</span>
                </div>
                <div className="flex justify-between">
                  <span>RLS:</span>
                  <span className="text-blue-600 font-bold">Clause 2.1</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Command Body with Desktop Sidebar Rail */}
      <div className="flex-1 flex w-full min-h-[calc(100dvh-4rem)]">
        {/* Desktop Fixed Left Navigation Rail */}
        {/* Desktop Fixed Left Navigation Rail - Pinned Footer & Smooth Independent Scroll */}
        <aside
          className={`hidden lg:flex flex-col justify-between shrink-0 bg-white border-r border-slate-200 sticky top-16 h-[calc(100dvh-4rem)] overflow-hidden transition-all duration-300 ease-in-out shadow-xs z-20 ${
            isSidebarCollapsed ? 'w-20 p-2.5' : 'w-72 xl:w-76 p-3.5'
          }`}
        >
          {isSidebarCollapsed ? (
            /* Collapsed Icon Rail View */
            <div className="flex flex-col items-center justify-between h-full w-full">
              <div className="flex flex-col items-center space-y-3 w-full">
                <div className="w-8 h-8 rounded-lg bg-blue-50 border border-blue-200 flex items-center justify-center">
                  <Lock className="w-4 h-4 text-blue-600" />
                </div>

                <div className="w-8 h-px bg-slate-200" />

                <div className="space-y-1.5 w-full flex flex-col items-center overflow-y-auto max-h-[calc(100dvh-12rem)] pr-0.5">
                  {navSections.flatMap(sec => sec.items).map(item => {
                    const isSelected = activeTab === item.id;
                    return (
                      <div key={item.id} className="relative group w-full flex justify-center">
                        <button
                          onClick={() => setActiveTab(item.id as any)}
                          className={`w-10 h-10 rounded-xl flex items-center justify-center transition-all cursor-pointer relative ${
                            isSelected
                              ? 'bg-blue-50 text-blue-700 border border-blue-200 shadow-2xs font-bold'
                              : 'text-slate-500 hover:text-slate-900 hover:bg-slate-100 border border-transparent'
                          }`}
                          title={item.label}
                        >
                          <span className="transition-transform group-hover:scale-110">
                            {item.icon}
                          </span>
                          {isSelected && (
                            <span className="absolute left-1 top-2.5 bottom-2.5 w-1 bg-blue-600 rounded-r-md" />
                          )}
                          {item.count !== undefined && item.count > 0 && (
                            <span className="absolute -top-1 -right-1 w-4 h-4 bg-blue-600 text-white rounded-full text-[9px] font-mono font-bold flex items-center justify-center shadow-xs">
                              {item.count}
                            </span>
                          )}
                        </button>

                        {/* Tooltip on hover */}
                        <div className="absolute left-full ml-3 px-3 py-1.5 bg-slate-900 border border-slate-800 text-white text-xs font-semibold rounded-xl whitespace-nowrap shadow-xl opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity z-50 flex items-center gap-2">
                          <span>{item.label}</span>
                          {item.badge && (
                            <span className={`text-[10px] px-1.5 py-0.2 rounded-full font-bold ${item.badgeClass || 'bg-slate-800 text-slate-200'}`}>
                              {item.badge}
                            </span>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Collapsed Bottom Telemetry Indicator */}
              <div className="pt-2 border-t border-slate-100 w-full flex justify-center shrink-0">
                <div
                  className="w-9 h-9 rounded-xl bg-emerald-50 border border-emerald-200 flex items-center justify-center group relative cursor-pointer"
                  title="Telemetry Online"
                >
                  <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                  <div className="absolute left-full ml-3 px-2.5 py-1.5 bg-slate-900 text-emerald-300 text-[10px] font-mono font-bold rounded-xl whitespace-nowrap shadow-xl opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity z-50">
                    Telemetry Synced • Neon DB
                  </div>
                </div>
              </div>
            </div>
          ) : (
            /* Expanded Full Sidebar View - Two-section flex layout with pinned footer */
            <div className="flex flex-col h-full justify-between overflow-hidden">
              {/* Top Quick Module Filter */}
              <div className="relative shrink-0 pb-3 border-b border-slate-100">
                <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="Filter navigation..."
                  value={sidebarFilter}
                  onChange={e => setSidebarFilter(e.target.value)}
                  className="w-full pl-8 pr-7 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 focus:bg-white transition-all"
                />
                {sidebarFilter && (
                  <button
                    onClick={() => setSidebarFilter('')}
                    className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 text-xs cursor-pointer"
                  >
                    ✕
                  </button>
                )}
              </div>

              {/* Navigation Groups - Smooth Independent Scroll Area */}
              <div className="flex-1 overflow-y-auto py-2.5 space-y-3.5 pr-1">
                {navSections.map((sec, secIdx) => {
                  const filteredItems = sec.items.filter(item =>
                    item.label.toLowerCase().includes(sidebarFilter.toLowerCase())
                  );
                  if (filteredItems.length === 0) return null;

                  return (
                    <div key={secIdx} className="space-y-1">
                      <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider px-2.5 mb-1 flex items-center justify-between">
                        <span>{sec.title}</span>
                      </div>

                      <div className="space-y-0.5">
                        {filteredItems.map(item => {
                          const isSelected = activeTab === item.id;
                          return (
                            <button
                              key={item.id}
                              onClick={() => setActiveTab(item.id as any)}
                              className={`w-full px-2.5 py-2 text-xs font-medium rounded-xl transition-all duration-150 flex items-center justify-between text-left group cursor-pointer relative ${
                                isSelected
                                  ? 'bg-blue-50 text-blue-700 border border-blue-200/80 font-bold shadow-2xs before:absolute before:left-0 before:top-2 before:bottom-2 before:w-1 before:bg-blue-600 before:rounded-r-md'
                                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100/70 border border-transparent'
                              }`}
                            >
                              <span className="flex items-center gap-2.5 truncate pl-1">
                                <span className={`shrink-0 transition-transform group-hover:scale-110 ${isSelected ? 'text-blue-600' : 'text-slate-400'}`}>
                                  {item.icon}
                                </span>
                                <span className="truncate">{item.label}</span>
                              </span>

                              <div className="flex items-center gap-1.5 shrink-0 ml-2">
                                {item.badge && (
                                  <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${item.badgeClass || 'bg-slate-100 text-slate-600'}`}>
                                    {item.badge}
                                  </span>
                                )}
                                {item.count !== undefined && item.count > 0 && (
                                  <span className={`text-[10px] px-2 py-0.5 rounded-full font-mono font-bold ${item.countClass || 'bg-slate-100 text-slate-600'}`}>
                                    {item.count}
                                  </span>
                                )}
                              </div>
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Sidebar Footer: Real-time Telemetry Health Pod - ALWAYS Pinned to Bottom */}
              <div className="pt-2.5 border-t border-slate-100 shrink-0">
                <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 space-y-1.5 text-[11px] shadow-2xs">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-600 flex items-center gap-1.5">
                      <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                      Command Telemetry
                    </span>
                    <span className="text-[9px] font-mono text-emerald-700 bg-emerald-50 border border-emerald-200 px-1.5 py-0.5 rounded font-bold">
                      ONLINE
                    </span>
                  </div>

                  <div className="space-y-0.5 font-mono text-[10px] text-slate-600">
                    <div className="flex justify-between">
                      <span>Neon PostgreSQL:</span>
                      <span className="text-slate-800 font-semibold">Synced</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Gemini Engine:</span>
                      <span className="text-purple-700 font-semibold">gemini-2.5-flash</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Privacy Tier:</span>
                      <span className="text-blue-700 font-semibold">Clause 2.1 RLAC</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </aside>

        {/* Right Main Content Area */}
        <main className="flex-1 min-w-0 p-4 sm:p-6 lg:p-8 pb-16 bg-slate-50 overflow-y-auto space-y-6">
          {/* Top 4 Telemetry Metrics Cards - ONLY on Operational / Ticket tabs */}
          {['service_requests', 'hostel_requests', 'grievances', 'clubs', 'bookings', 'lost_found', 'kanban'].includes(activeTab) && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 animate-in fade-in-50 duration-200">
              {/* Card 1: Grievances */}
              <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs flex flex-col justify-between hover:border-slate-300 hover:shadow-md transition-all group min-h-[140px]">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Active Grievances</span>
                  <div className="w-8 h-8 rounded-lg bg-rose-50 border border-rose-200 flex items-center justify-center shrink-0">
                    <MessageSquareWarning className="w-4 h-4 text-rose-600" />
                  </div>
                </div>
                <div>
                  <div className="text-3xl font-black text-slate-900 tracking-tight leading-none">{grievances.length}</div>
                  <div className="text-xs text-slate-400 mt-1.5 flex items-center gap-1 font-medium">
                    <span>Formal SGRC student filings</span>
                  </div>
                </div>
              </div>

              {/* Card 2: Club Apps */}
              <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs flex flex-col justify-between hover:border-slate-300 hover:shadow-md transition-all group min-h-[140px]">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Club Applications</span>
                  <div className="w-8 h-8 rounded-lg bg-indigo-50 border border-indigo-200 flex items-center justify-center shrink-0">
                    <Users className="w-4 h-4 text-indigo-600" />
                  </div>
                </div>
                <div>
                  <div className="text-3xl font-black text-slate-900 tracking-tight leading-none">{clubApps.length}</div>
                  <div className="text-xs text-slate-400 mt-1.5 flex items-center gap-1 font-medium">
                    <span>SAC & student council review</span>
                  </div>
                </div>
              </div>

              {/* Card 3: Bookings */}
              <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs flex flex-col justify-between hover:border-slate-300 hover:shadow-md transition-all group min-h-[140px]">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Facility Bookings</span>
                  <div className="w-8 h-8 rounded-lg bg-blue-50 border border-blue-200 flex items-center justify-center shrink-0">
                    <Calendar className="w-4 h-4 text-blue-600" />
                  </div>
                </div>
                <div>
                  <div className="text-3xl font-black text-slate-900 tracking-tight leading-none">{bookings.length}</div>
                  <div className="text-xs text-slate-400 mt-1.5 flex items-center gap-1 font-medium">
                    <span>Halls, labs & sports grounds</span>
                  </div>
                </div>
              </div>

              {/* Card 4: Lost & Found */}
              <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs flex flex-col justify-between hover:border-slate-300 hover:shadow-md transition-all group min-h-[140px]">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Lost & Found Posts</span>
                  <div className="w-8 h-8 rounded-lg bg-amber-50 border border-amber-200 flex items-center justify-center shrink-0">
                    <PackageSearch className="w-4 h-4 text-amber-600" />
                  </div>
                </div>
                <div>
                  <div className="text-3xl font-black text-slate-900 tracking-tight leading-none">{lostAndFound.length}</div>
                  <div className="text-xs text-slate-400 mt-1.5 flex items-center gap-1 font-medium">
                    <span>Campus item registry</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Tab Content Display */}
          <div className="space-y-6">
            {['service_requests', 'hostel_requests', 'grievances', 'clubs', 'bookings', 'lost_found'].includes(activeTab) ? (
              <>
                {/* Search & Header Bar */}
                <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                  <h2 className="text-lg font-bold text-slate-900 capitalize flex items-center gap-2">
                    {activeTab === 'service_requests' ? 'Student Service Requests (Nodal Office)' : activeTab === 'hostel_requests' ? 'Hostel & Mess Requests' : activeTab === 'lost_found' ? 'Lost & Found Registry' : activeTab.replace('_', ' ')}
                  </h2>
                  <div className="relative w-full sm:w-80">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                    <input 
                      type="text" 
                      placeholder="Search by ID, name, or description..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all"
                    />
                  </div>
                </div>

                {/* Data Table */}
                <div className="bg-white border border-slate-200 rounded-2xl shadow-xs overflow-hidden">
                  {loading ? (
                    <div className="p-12 text-center text-slate-400">
                      <div className="animate-spin w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full mx-auto mb-3"></div>
                      Loading data from Neon DB...
                    </div>
                  ) : (
                    <div className="overflow-x-auto min-h-[450px]">
                      <table className="w-full text-left border-collapse">
                        <thead>
                          <tr className="bg-slate-50 border-b border-slate-200 text-xs uppercase tracking-wider text-slate-500 font-semibold">
                            <th className="px-6 py-4">Tracking ID / User</th>
                            <th className="px-6 py-4">Details</th>
                            <th className="px-6 py-4">Date & Time</th>
                            <th className="px-6 py-4">Current Status</th>
                            <th className="px-6 py-4 text-right">Actions</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100 text-xs">
                          {activeTab === 'service_requests' ? (
                            filteredServiceRequests.length > 0 ? filteredServiceRequests.map(s => (
                              <tr key={s.id || s.request_no} className="hover:bg-slate-50/70 transition-colors text-slate-700">
                                <td className="px-6 py-4 align-top">
                                  <span className="font-mono font-semibold text-blue-300 bg-blue-500/10 border border-blue-500/20 px-2 py-0.5 rounded-md text-xs">{s.request_no}</span>
                                  <div className="text-xs text-slate-400 mt-1.5 font-mono">{s.student_id}</div>
                                </td>
                                <td className="px-6 py-4 align-top max-w-md">
                                  <div className="flex items-center gap-2 mb-1">
                                    <span className="px-2 py-0.5 rounded bg-slate-100 border border-slate-200 text-slate-700 text-[10px] font-bold uppercase">{s.category}</span>
                                    <span className="font-semibold text-slate-900 text-sm">{s.title}</span>
                                  </div>
                                  <p className="text-xs text-slate-400 line-clamp-2">{s.description}</p>
                                  {s.assigned_office && (
                                    <div className="text-[11px] text-slate-500 mt-1">Office: {s.assigned_office}</div>
                                  )}
                                </td>
                                <td className="px-6 py-4 align-top text-slate-400 whitespace-nowrap">
                                  <div>{new Date(s.created_at).toLocaleDateString()}</div>
                                  {s.sla_due_date && <div className="text-amber-400 font-medium mt-0.5">SLA: {s.sla_due_date}</div>}
                                </td>
                                <td className="px-6 py-4 align-top whitespace-nowrap">
                                  <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold border ${getStatusBadgeColor(s.status)}`}>
                                    {getStatusIcon(s.status)}
                                    {s.status}
                                  </span>
                                </td>
                                <td className="px-6 py-4 align-top text-right">
                                  <div className="flex items-center justify-end gap-2">
                                    <select 
                                      className="text-xs bg-white border border-slate-300 rounded-lg px-2.5 py-1.5 shadow-2xs text-slate-800 focus:outline-none focus:ring-1 focus:ring-blue-500 font-medium"
                                      value={s.status.toUpperCase()}
                                      onChange={(e) => handleStatusUpdate(s.id || s.request_no, 'service_request', e.target.value)}
                                    >
                                      <option value="SUBMITTED">Submitted</option>
                                      <option value="IN_REVIEW">In Review</option>
                                      <option value="APPROVED">Approved</option>
                                      <option value="REJECTED">Rejected</option>
                                      <option value="RESOLVED">Resolved</option>
                                      <option value="CLOSED">Closed</option>
                                    </select>
                                    <button
                                      onClick={() => handleDeleteTicket(s.id || s.request_no, 'service_request')}
                                      className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors"
                                      title="Delete Service Request Permanently"
                                    >
                                      <Trash2 className="w-4 h-4" />
                                    </button>
                                  </div>
                                </td>
                              </tr>
                            )) : (
                              <tr><td colSpan={5} className="px-6 py-12 text-center text-slate-500">No service requests found.</td></tr>
                            )
                          ) : activeTab === 'hostel_requests' ? (
                            filteredHostelRequests.length > 0 ? filteredHostelRequests.map(h => (
                              <tr key={h.id} className="hover:bg-slate-50/70 transition-colors text-slate-700">
                                <td className="px-6 py-4 align-top">
                                  <div className="font-semibold text-white">{h.student_id}</div>
                                  <div className="text-xs text-slate-400 mt-1 font-mono">Req #{h.id}</div>
                                </td>
                                <td className="px-6 py-4 align-top">
                                  <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-purple-500/10 text-purple-300 font-medium text-xs border border-purple-500/20">
                                    {h.type}
                                  </span>
                                  <div className="mt-2 text-xs text-slate-300">{h.details}</div>
                                </td>
                                <td className="px-6 py-4 align-top text-slate-400 whitespace-nowrap">
                                  {h.created_at ? new Date(h.created_at).toLocaleString() : 'N/A'}
                                </td>
                                <td className="px-6 py-4 align-top whitespace-nowrap">
                                  <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold border ${getStatusBadgeColor(h.status)}`}>
                                    {getStatusIcon(h.status)}
                                    {h.status}
                                  </span>
                                </td>
                                <td className="px-6 py-4 align-top text-right">
                                  <div className="flex items-center justify-end gap-2">
                                    <select 
                                      className="text-xs bg-white border border-slate-300 rounded-lg px-2.5 py-1.5 shadow-2xs text-slate-800 focus:outline-none focus:ring-1 focus:ring-blue-500 font-medium"
                                      value={h.status}
                                      onChange={(e) => handleStatusUpdate(h.id, 'hostel', e.target.value)}
                                    >
                                      <option value="pending">Pending</option>
                                      <option value="in_progress">In Progress</option>
                                      <option value="resolved">Resolved</option>
                                      <option value="rejected">Rejected</option>
                                    </select>
                                    <button
                                      onClick={() => handleDeleteTicket(h.id, 'hostel')}
                                      className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors"
                                      title="Delete Hostel Request Permanently"
                                    >
                                      <Trash2 className="w-4 h-4" />
                                    </button>
                                  </div>
                                </td>
                              </tr>
                            )) : (
                              <tr><td colSpan={5} className="px-6 py-12 text-center text-slate-500">No hostel requests found.</td></tr>
                            )
                          ) : activeTab === 'grievances' ? (
                            filteredGrievances.length > 0 ? filteredGrievances.map(g => (
                              <tr key={g.id} className="hover:bg-slate-50/70 transition-colors text-slate-700">
                                <td className="px-6 py-4 align-top">
                                  <span className="font-mono font-semibold text-slate-700 bg-slate-100 border border-slate-200 px-2 py-0.5 rounded-md text-xs">{g.id}</span>
                                </td>
                                <td className="px-6 py-4 align-top max-w-md">
                                  <p className="text-slate-200 line-clamp-2">{g.description}</p>
                                  {g.withdrawal_reason && (
                                    <div className="mt-2 text-xs bg-rose-500/10 border border-rose-500/20 text-rose-300 px-2.5 py-1.5 rounded-md">
                                      <strong>Withdrawal Reason:</strong> {g.withdrawal_reason}
                                    </div>
                                  )}
                                </td>
                                <td className="px-6 py-4 align-top text-slate-400 whitespace-nowrap">
                                  {new Date(g.timestamp).toLocaleString()}
                                </td>
                                <td className="px-6 py-4 align-top whitespace-nowrap">
                                  <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold border ${getStatusBadgeColor(g.status)}`}>
                                    {getStatusIcon(g.status)}
                                    {g.status}
                                  </span>
                                </td>
                                <td className="px-6 py-4 align-top text-right">
                                  <div className="flex items-center justify-end gap-2">
                                    <select 
                                      disabled={g.status === 'Withdrawn'}
                                      className="text-xs bg-white border border-slate-300 rounded-lg px-2.5 py-1.5 shadow-2xs text-slate-800 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:opacity-50"
                                      value={g.status}
                                      onChange={(e) => handleStatusUpdate(g.id, 'grievance', e.target.value)}
                                    >
                                      <option value="Received & Secured">Received & Secured</option>
                                      <option value="Under Investigation">Under Investigation</option>
                                      <option value="Action Taken">Action Taken</option>
                                      <option value="Resolved">Resolved</option>
                                      <option value="Rejected">Rejected</option>
                                      <option value="Withdrawn" disabled>Withdrawn</option>
                                    </select>
                                    <button
                                      onClick={() => handleDeleteTicket(g.id, 'grievance')}
                                      className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors"
                                      title="Delete Grievance Permanently"
                                    >
                                      <Trash2 className="w-4 h-4" />
                                    </button>
                                  </div>
                                </td>
                              </tr>
                            )) : (
                              <tr><td colSpan={5} className="px-6 py-12 text-center text-slate-500">No grievances found.</td></tr>
                            )
                          ) : activeTab === 'clubs' ? (
                            filteredClubApps.length > 0 ? filteredClubApps.map(c => (
                              <tr key={c.id} className="hover:bg-slate-50/70 transition-colors text-slate-700">
                                <td className="px-6 py-4 align-top">
                                  <div className="font-semibold text-slate-900">{c.student_name}</div>
                                  <div className="text-xs text-slate-400 mt-1 font-mono">App #{c.id}</div>
                                </td>
                                <td className="px-6 py-4 align-top">
                                  <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-indigo-500/10 text-indigo-300 font-medium text-xs border border-indigo-500/20">
                                    {c.club_id}
                                  </span>
                                  {c.withdrawal_reason && (
                                    <div className="mt-2 text-xs bg-rose-500/10 border border-rose-500/20 text-rose-300 px-2.5 py-1.5 rounded-md">
                                      <strong>Withdrawal Reason:</strong> {c.withdrawal_reason}
                                    </div>
                                  )}
                                </td>
                                <td className="px-6 py-4 align-top text-slate-400 whitespace-nowrap">
                                  {new Date(c.timestamp).toLocaleString()}
                                </td>
                                <td className="px-6 py-4 align-top whitespace-nowrap">
                                  <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold border ${getStatusBadgeColor(c.status)}`}>
                                    {getStatusIcon(c.status)}
                                    {c.status}
                                  </span>
                                </td>
                                <td className="px-6 py-4 align-top text-right">
                                  <div className="flex items-center justify-end gap-2">
                                    <select 
                                      disabled={c.status === 'Withdrawn'}
                                      className="text-xs bg-white border border-slate-300 rounded-lg px-2.5 py-1.5 shadow-2xs text-slate-800 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:opacity-50"
                                      value={c.status}
                                      onChange={(e) => handleStatusUpdate(c.id, 'club', e.target.value)}
                                    >
                                      <option value="Application Forwarded">Application Forwarded</option>
                                      <option value="Under Review">Under Review</option>
                                      <option value="Approved">Approved</option>
                                      <option value="Rejected">Rejected</option>
                                      <option value="Waitlisted">Waitlisted</option>
                                      <option value="Withdrawn" disabled>Withdrawn</option>
                                    </select>
                                    <button
                                      onClick={() => handleDeleteTicket(c.id, 'club')}
                                      className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors"
                                      title="Delete Club Application Permanently"
                                    >
                                      <Trash2 className="w-4 h-4" />
                                    </button>
                                  </div>
                                </td>
                              </tr>
                            )) : (
                              <tr><td colSpan={5} className="px-6 py-12 text-center text-slate-500">No club applications found.</td></tr>
                            )
                          ) : activeTab === 'bookings' ? (
                            filteredBookings.length > 0 ? filteredBookings.map(b => (
                              <tr key={b.id} className="hover:bg-slate-50/70 transition-colors text-slate-700">
                                <td className="px-6 py-4 align-top">
                                  <div className="font-semibold text-slate-900">{b.student_id}</div>
                                  <div className="text-xs text-slate-400 mt-1 font-mono">Booking #{b.id}</div>
                                </td>
                                <td className="px-6 py-4 align-top">
                                  <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-amber-500/10 text-amber-300 font-medium text-xs border border-amber-500/20">
                                    Facility #{b.facility_id}
                                  </span>
                                  <div className="mt-2 text-xs text-slate-300">
                                    <strong>Purpose:</strong> {b.purpose}
                                  </div>
                                </td>
                                <td className="px-6 py-4 align-top text-slate-400 whitespace-nowrap">
                                  <div><strong>Date:</strong> {b.date}</div>
                                  <div>{b.start_time} - {b.end_time}</div>
                                </td>
                                <td className="px-6 py-4 align-top whitespace-nowrap">
                                  <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold border ${getStatusBadgeColor(b.status)}`}>
                                    {getStatusIcon(b.status)}
                                    {b.status}
                                  </span>
                                </td>
                                <td className="px-6 py-4 align-top text-right">
                                  <div className="flex items-center justify-end gap-2">
                                    <select 
                                      className="text-xs bg-white border border-slate-300 rounded-lg px-2.5 py-1.5 shadow-2xs text-slate-800 focus:outline-none focus:ring-1 focus:ring-blue-500"
                                      value={b.status}
                                      onChange={(e) => handleStatusUpdate(b.id, 'booking' as any, e.target.value)}
                                    >
                                      <option value="pending">Pending</option>
                                      <option value="confirmed">Confirmed</option>
                                      <option value="cancelled">Cancelled</option>
                                    </select>
                                    <button
                                      onClick={() => handleDeleteTicket(b.id, 'booking')}
                                      className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors"
                                      title="Delete Booking Permanently"
                                    >
                                      <Trash2 className="w-4 h-4" />
                                    </button>
                                  </div>
                                </td>
                              </tr>
                            )) : (
                              <tr><td colSpan={5} className="px-6 py-12 text-center text-slate-500">No bookings found.</td></tr>
                            )
                          ) : (
                            filteredLostAndFound.length > 0 ? filteredLostAndFound.map(l => (
                              <tr key={l.id} className="hover:bg-slate-50/70 transition-colors text-slate-700">
                                <td className="px-6 py-4 align-top">
                                  <div className="font-semibold text-slate-900">{l.student_id}</div>
                                  <div className="text-xs text-slate-400 mt-1 font-mono">Post #{l.id} ({l.type.toUpperCase()})</div>
                                </td>
                                <td className="px-6 py-4 align-top">
                                  <div className="font-semibold text-slate-900 text-sm">{l.title}</div>
                                  <p className="text-xs text-slate-400 line-clamp-2 mt-1">{l.description}</p>
                                </td>
                                <td className="px-6 py-4 align-top text-slate-400 whitespace-nowrap">
                                  {new Date(l.date_posted).toLocaleString()}
                                </td>
                                <td className="px-6 py-4 align-top whitespace-nowrap">
                                  <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold border ${getStatusBadgeColor(l.status)}`}>
                                    {getStatusIcon(l.status)}
                                    {l.status}
                                  </span>
                                </td>
                                <td className="px-6 py-4 align-top text-right">
                                  <div className="flex items-center justify-end gap-2">
                                    <select 
                                      className="text-xs bg-white border border-slate-300 rounded-lg px-2.5 py-1.5 shadow-2xs text-slate-800 focus:outline-none focus:ring-1 focus:ring-blue-500"
                                      value={l.status}
                                      onChange={(e) => handleStatusUpdate(l.id, 'lost_found' as any, e.target.value)}
                                    >
                                      <option value="open">Open</option>
                                      <option value="claimed">Claimed</option>
                                      <option value="resolved">Resolved</option>
                                    </select>
                                    <button
                                      onClick={() => handleDeleteTicket(l.id, 'lost_found')}
                                      className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors"
                                      title="Delete Lost & Found Post Permanently"
                                    >
                                      <Trash2 className="w-4 h-4" />
                                    </button>
                                  </div>
                                </td>
                              </tr>
                            )) : (
                              <tr><td colSpan={5} className="px-6 py-12 text-center text-slate-500">No lost and found items.</td></tr>
                            )
                          )}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              </>
            ) : (
              <div className="w-full">
                {activeTab === 'remediation' && <CognitiveRemediationTab />}
                {activeTab === 'compliance' && <ComplianceTab />}
                {activeTab === 'live_sessions' && <LiveSessionsTab />}
                {activeTab === 'verifications' && <VerificationsTab />}
                {activeTab === 'broadcasts' && <BroadcastsTab />}
                {activeTab === 'distress' && <DistressTab />}
                {activeTab === 'health' && <AgentHealthTab />}
                {activeTab === 'kanban' && <KanbanTab grievances={grievances} handleStatusUpdate={handleStatusUpdate} />}
                {activeTab === 'audit' && <AuditTab />}
                {activeTab === 'knowledge' && <KnowledgeTab />}
                {activeTab === 'analytics' && <AnalyticsTab analytics={analytics} />}
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}

// ==========================================
// FORMAL COMMAND CENTER TAB COMPONENTS (DARK SLATE THEME)
// ==========================================

function DistressTab() {
  const [mockAlerts, setMockAlerts] = useState([
    { id: 'AL-9021', student: 'Rajesh K. (22BCE)', trigger: 'Mentioned severe anxiety about fee deadline', sentiment: 'Critical', time: '2 mins ago', status: 'Unassigned', transcript: "I just can't take this anymore. The fees are due tomorrow and my loan didn't come through. I feel completely helpless and overwhelmed." },
    { id: 'AL-9020', student: 'Priya M. (21BEE)', trigger: 'Repeated phrases indicating depression', sentiment: 'High', time: '14 mins ago', status: 'Unassigned', transcript: "I haven't been able to sleep or study for weeks. Everything feels pointless right now. I don't know who to talk to." },
    { id: 'AL-9018', student: 'Anonymous', trigger: 'Keywords related to self-harm', sentiment: 'Severe', time: '45 mins ago', status: 'Routed to Counselor', transcript: "[Redacted by Safety Filter]" },
  ]);

  const handleRoute = (id: string) => {
    setMockAlerts(alerts => alerts.map(a => a.id === id ? { ...a, status: 'Routed to Counselor' } : a));
  };

  const sentimentData = [
    { name: 'Mon', stress: 12 },
    { name: 'Tue', stress: 19 },
    { name: 'Wed', stress: 15 },
    { name: 'Thu', stress: 35 },
    { name: 'Fri', stress: 42 },
    { name: 'Sat', stress: 28 },
    { name: 'Sun', stress: 18 },
  ];

  return (
    <div className="space-y-6">
      {/* Top row: Alerts & Sentiment */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Real-time Distress Alerts */}
        <div className="lg:col-span-3 bg-white rounded-2xl p-5 border border-slate-200 shadow-xs flex flex-col h-[480px]">
          <div className="flex justify-between items-center mb-4 pb-3 border-b border-slate-100">
            <h3 className="font-bold text-slate-900 flex items-center gap-2">
              <AlertOctagon className="w-5 h-5 text-rose-500 animate-pulse" /> Real-time Distress Surveillance
            </h3>
            <span className="text-xs bg-rose-500/20 text-rose-300 border border-rose-500/30 px-2.5 py-0.5 rounded-full font-bold">
              {mockAlerts.filter(a => a.status === 'Unassigned').length} Unassigned
            </span>
          </div>

          <div className="space-y-3.5 flex-1 overflow-y-auto pr-1">
            {mockAlerts.map(alert => (
              <div key={alert.id} className={`p-4 border rounded-xl transition-all ${alert.status === 'Unassigned' ? 'border-rose-200 bg-rose-50/40' : 'border-slate-200 bg-slate-50/60'}`}>
                <div className="flex justify-between items-start mb-2">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-slate-900 text-sm">{alert.student}</span>
                    <span className={`text-[10px] uppercase px-2 py-0.5 rounded-md font-bold ${
                      alert.sentiment === 'Severe' ? 'bg-rose-600 text-white shadow-xs' : 
                      alert.sentiment === 'Critical' ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' : 
                      'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                    }`}>
                      {alert.sentiment}
                    </span>
                  </div>
                  <span className="text-xs text-slate-500 font-mono">{alert.time}</span>
                </div>
                <p className="text-xs text-slate-300 font-medium mb-1">
                  Trigger: <span className="text-slate-400 font-normal">{alert.trigger}</span>
                </p>
                <div className="mt-2.5 bg-white p-3 rounded-xl border border-slate-200 text-xs italic text-slate-700 border-l-4 border-l-rose-500 shadow-2xs">
                  "{alert.transcript}"
                </div>
                
                <div className="mt-3.5 pt-3 border-t border-slate-800/80 flex justify-between items-center text-xs">
                  <span className="font-medium text-slate-400">Status: <span className="text-slate-200">{alert.status}</span></span>
                  {alert.status === 'Unassigned' && (
                    <button 
                      onClick={() => handleRoute(alert.id)}
                      className="px-3.5 py-1.5 bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold rounded-xl transition-all shadow-sm flex items-center gap-1.5 cursor-pointer"
                    >
                      <UserPlus className="w-3.5 h-3.5" /> Route to Counselor
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Sentiment Analytics */}
        <div className="lg:col-span-2 bg-white rounded-2xl p-5 border border-slate-200 shadow-xs flex flex-col h-[480px]">
          <h3 className="font-bold text-white flex items-center gap-2 mb-1">
            <Activity className="w-5 h-5 text-indigo-400" /> Campus Stress Index
          </h3>
          <p className="text-xs text-slate-400 mb-4">Sentiment telemetry aggregated from AI interactions.</p>
          
          <div className="flex-1 min-h-[220px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={sentimentData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorStressDark" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.7}/>
                    <stop offset="95%" stopColor="#f43f5e" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#64748b' }} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#64748b' }} />
                <RechartsTooltip 
                  contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', borderRadius: '12px', color: '#0f172a' }}
                />
                <Area type="monotone" dataKey="stress" stroke="#f43f5e" strokeWidth={2.5} fillOpacity={1} fill="url(#colorStressDark)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
          
          <div className="mt-4 p-3 bg-amber-500/10 rounded-xl border border-amber-500/20 flex items-start gap-2.5">
            <Bell className="w-4 h-4 text-amber-400 mt-0.5 shrink-0" />
            <p className="text-xs text-amber-200">
              <span className="font-semibold block mb-0.5">High Stress Spike Detected</span>
              Mid-semester CIE exam week accounts for a 45% increase in negative valence triggers.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

function AnalyticsTab({ analytics }: { analytics: any }) {
  if (!analytics) return null;
  return (
    <div className="bg-white border border-slate-200 rounded-2xl shadow-xs p-6 space-y-6">
      <div className="border-b border-slate-100 pb-4">
        <h2 className="text-lg font-bold text-slate-900">Institutional Service Analytics</h2>
        <p className="text-xs text-slate-400">Telemetry aggregations across student submissions & bookings</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-slate-50 p-5 rounded-2xl border border-slate-200">
          <h3 className="text-sm font-bold text-slate-700 uppercase tracking-wider mb-4">Grievance Status Distribution</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={analytics.grievances}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  label
                >
                  {analytics.grievances.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={['#3b82f6', '#10b981', '#f59e0b', '#f43f5e', '#a855f7'][index % 5]} />
                  ))}
                </Pie>
                <RechartsTooltip contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', borderRadius: '12px' }} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        <div className="bg-slate-50 p-5 rounded-2xl border border-slate-200">
          <h3 className="text-sm font-bold text-slate-700 uppercase tracking-wider mb-4">Facility Bookings Volume</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={analytics.bookings}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#64748b' }} />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} />
                <RechartsTooltip contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', borderRadius: '12px' }} />
                <Bar dataKey="value" fill="#3b82f6" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}

function ComplianceTab() {
  const [tickets] = React.useState([
    { id: 'TKT-8901', type: 'Anti-Ragging', student: 'Anonymous', sla: '2 Hrs', status: 'Breach Risk', assignee: 'Nodal Officer 1' },
    { id: 'TKT-8905', type: 'Harassment', student: 'Confidential', sla: '14 Hrs', status: 'Warning', assignee: 'Nodal Officer 2' },
    { id: 'TKT-8890', type: 'General Grievance', student: '24CSE001', sla: '12 Days', status: 'On Track', assignee: 'Dept Head CSE' }
  ]);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2 bg-white rounded-2xl p-5 border border-slate-200 shadow-xs flex flex-col h-[500px]">
        <div className="flex justify-between items-center mb-4 pb-3 border-b border-slate-100">
          <h3 className="font-bold text-slate-900 flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-rose-500" /> SLA Breach Warning Matrix
          </h3>
          <span className="text-xs bg-rose-500/20 text-rose-300 border border-rose-500/30 px-2.5 py-0.5 rounded-full font-bold">2 Critical</span>
        </div>
        <div className="overflow-x-auto flex-1">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="text-slate-500 uppercase bg-slate-50 border-b border-slate-200 sticky top-0">
              <tr>
                <th className="px-4 py-3 font-semibold">Ticket / Type</th>
                <th className="px-4 py-3 font-semibold">SLA Countdown</th>
                <th className="px-4 py-3 font-semibold">Status</th>
                <th className="px-4 py-3 font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80">
              {tickets.map(t => (
                <tr key={t.id} className="hover:bg-slate-50/70 transition-colors text-slate-700">
                  <td className="px-4 py-3">
                    <div className="font-semibold text-white">{t.id}</div>
                    <div className="text-[11px] text-slate-400">{t.type}</div>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`font-mono font-bold ${t.sla.includes('Hrs') ? 'text-rose-400' : 'text-slate-300'}`}>
                      {t.sla}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded text-[11px] font-semibold border ${
                      t.status === 'Breach Risk' ? 'bg-rose-500/20 text-rose-300 border-rose-500/30' :
                      t.status === 'Warning' ? 'bg-amber-500/20 text-amber-300 border-amber-500/30' : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30'
                    }`}>
                      {t.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button className="text-blue-400 hover:text-blue-300 text-xs font-semibold border border-blue-500/30 hover:bg-blue-500/10 px-3 py-1.5 rounded-xl transition-colors flex items-center gap-1 ml-auto">
                      <Gavel className="w-3.5 h-3.5" /> Fwd to SGRC
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs flex flex-col justify-between h-[500px]">
        <div>
          <h3 className="font-bold text-white flex items-center gap-2 mb-2">
            <FileText className="w-5 h-5 text-indigo-400" /> Statutory ATR Generator
          </h3>
          <p className="text-xs text-slate-400 mb-6">Generate standardized Action Taken Reports for UGC, NAAC, or statutory bodies.</p>
          
          <div className="space-y-4">
            <div>
              <label className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">Report Period</label>
              <select className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-xs text-slate-800 focus:outline-none focus:ring-1 focus:ring-indigo-500">
                <option>Q3 2026 (Jul - Sep)</option>
                <option>Q2 2026 (Apr - Jun)</option>
                <option>Annual 2025-26</option>
              </select>
            </div>
            <div>
              <label className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">Target Authority</label>
              <select className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-xs text-slate-800 focus:outline-none focus:ring-1 focus:ring-indigo-500">
                <option>University Grants Commission (UGC)</option>
                <option>National Assessment (NAAC)</option>
                <option>Internal Management (Registrar)</option>
              </select>
            </div>
          </div>
        </div>
        
        <button className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs py-2.5 rounded-xl flex items-center justify-center gap-2 transition-colors cursor-pointer shadow-md">
          <Download className="w-4 h-4" /> Export Digitally Signed ATR PDF
        </button>
      </div>
    </div>
  );
}

function LiveSessionsTab() {
  const [activeSession, setActiveSession] = React.useState<string | null>('SESS-102');
  
  const sessions = [
    { id: 'SESS-102', student: '24CSE001', topic: 'Fee Payment Issue', status: 'High Friction', agent: 'VIGNAN-AI' },
    { id: 'SESS-105', student: '22BME014', topic: 'Attendance Exemption', status: 'Normal', agent: 'VIGNAN-AI' },
    { id: 'SESS-109', student: 'Anonymous', topic: 'Hostel Complaint', status: 'Escalating', agent: 'VIGNAN-AI' },
  ];

  const transcript = [
    { role: 'user', content: 'I tried paying my fees but the portal crashed and money was deducted!', time: '10:42 AM' },
    { role: 'agent', content: 'I understand you are facing a fee payment issue. Please check your bank statement in 3-5 working days.', time: '10:42 AM' },
    { role: 'user', content: 'I cant wait 5 days! The deadline is tomorrow and my hall ticket is blocked. Help me NOW.', time: '10:43 AM' },
    { role: 'agent', content: 'According to regulation 4.2, late fee of Rs.500 applies after the deadline.', time: '10:43 AM' },
  ];

  return (
    <div className="flex flex-col lg:flex-row h-[600px] bg-white border border-slate-200 rounded-2xl shadow-xs overflow-hidden">
      <div className="w-full lg:w-1/3 border-b lg:border-b-0 lg:border-r border-slate-200 bg-slate-50 flex flex-col">
        <div className="p-4 border-b border-slate-100 flex justify-between items-center">
          <h3 className="font-bold text-white text-sm">Active AI Sessions (12)</h3>
          <span className="flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-2.5 w-2.5 rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
          </span>
        </div>
        <div className="overflow-y-auto flex-1 p-3 space-y-2">
          {sessions.map(s => (
            <div 
              key={s.id} 
              onClick={() => setActiveSession(s.id)}
              className={`p-3 rounded-xl cursor-pointer border transition-all ${
                activeSession === s.id 
                  ? 'bg-blue-50 border-blue-200 text-blue-800 shadow-2xs font-semibold' 
                  : 'bg-white border-slate-200 hover:border-slate-300 text-slate-700'
              }`}
            >
              <div className="flex justify-between items-start mb-1">
                <span className="font-semibold text-xs text-white">{s.student}</span>
                <span className={`text-[9px] uppercase px-1.5 py-0.5 rounded font-bold ${
                  s.status === 'High Friction' ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' :
                  s.status === 'Escalating' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' :
                  'bg-slate-100 text-slate-600'
                }`}>{s.status}</span>
              </div>
              <div className="text-[11px] text-slate-400 truncate">{s.topic}</div>
            </div>
          ))}
        </div>
      </div>
      
      <div className="flex-1 flex flex-col bg-white">
        {activeSession ? (
          <>
            <div className="p-4 border-b border-slate-200 flex justify-between items-center bg-slate-50">
              <div>
                <h3 className="font-bold text-white text-sm">Shadowing Session {activeSession}</h3>
                <div className="text-xs text-slate-400">Live inspection of autonomous NLU inference</div>
              </div>
              <button className="px-3 py-1.5 bg-slate-100 border border-slate-200 rounded-lg text-xs font-semibold text-slate-700 hover:bg-slate-200 flex items-center gap-1.5 transition-colors">
                <UserX className="w-3.5 h-3.5 text-slate-400" /> End Shadow
              </button>
            </div>
            
            <div className="flex-1 p-6 overflow-y-auto space-y-4 bg-slate-50/50">
              {transcript.map((msg, i) => (
                <div key={i} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                  <div className="flex items-baseline gap-2 mb-1">
                    <span className="text-xs font-medium text-slate-400">{msg.role === 'user' ? 'Student' : 'VIGNAN-AI'}</span>
                    <span className="text-[10px] text-slate-500 font-mono">{msg.time}</span>
                  </div>
                  <div className={`p-3.5 rounded-2xl text-xs max-w-[80%] leading-relaxed ${
                    msg.role === 'user' 
                      ? 'bg-blue-600 text-white rounded-tr-none shadow-md shadow-blue-600/20' 
                      : 'bg-white border border-slate-200 text-slate-800 rounded-tl-none shadow-2xs'
                  }`}>
                    {msg.content}
                  </div>
                </div>
              ))}
            </div>
            
            <div className="p-4 border-t border-slate-200 bg-white">
              <div className="flex gap-3">
                <button className="flex-1 bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30 rounded-xl py-2 text-xs font-semibold flex items-center justify-center gap-2 transition-colors">
                  <Ear className="w-4 h-4" /> Whisper Direct Guidance to VIGNAN-AI
                </button>
                <button className="flex-1 bg-rose-600 hover:bg-rose-500 text-white rounded-xl py-2 text-xs font-semibold flex items-center justify-center gap-2 transition-colors shadow-md">
                  <MessageSquareOff className="w-4 h-4" /> Takeover Conversation
                </button>
              </div>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-slate-500 text-xs">
            Select a live session to begin shadowing
          </div>
        )}
      </div>
    </div>
  );
}

function VerificationsTab() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div className="md:col-span-2 space-y-4">
        <div className="bg-white rounded-2xl border border-slate-200 shadow-xs p-5">
          <h3 className="font-bold text-white mb-4 flex items-center gap-2 text-sm">
            <CheckCircle2 className="w-5 h-5 text-emerald-600" /> Pending Exemptions & Statutory Waivers
          </h3>
          <div className="space-y-3">
            <div className="p-4 border border-slate-200 rounded-xl bg-slate-50 flex flex-col sm:flex-row justify-between sm:items-center gap-4">
              <div>
                <div className="font-semibold text-white text-xs">Medical Attendance Condonation</div>
                <div className="text-[11px] text-slate-400 mt-0.5">Student: 23MEC045 • Requested 75% threshold relaxation (medical condonation)</div>
              </div>
              <div className="flex gap-2 shrink-0">
                <button className="px-3 py-1.5 text-xs font-medium bg-white border border-rose-200 text-rose-600 rounded-lg hover:bg-rose-50 transition-colors">Reject</button>
                <button className="px-3 py-1.5 text-xs font-semibold bg-emerald-600 text-white rounded-lg hover:bg-emerald-500 transition-colors shadow-sm">Approve Override</button>
              </div>
            </div>

            <div className="p-4 border border-slate-200 rounded-xl bg-slate-50 flex flex-col sm:flex-row justify-between sm:items-center gap-4">
              <div>
                <div className="font-semibold text-white text-xs">Fee Hold Exam Hall Ticket Release</div>
                <div className="text-[11px] text-slate-400 mt-0.5">Student: 21BEE092 • Unlock hall ticket generation temporarily under undertaking</div>
              </div>
              <div className="flex gap-2 shrink-0">
                <button className="px-3 py-1.5 text-xs font-medium bg-white border border-rose-200 text-rose-600 rounded-lg hover:bg-rose-50 transition-colors">Reject</button>
                <button className="px-3 py-1.5 text-xs font-semibold bg-emerald-600 text-white rounded-lg hover:bg-emerald-500 transition-colors shadow-sm">Approve Override</button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs p-5">
        <h3 className="font-bold text-white mb-2 flex items-center gap-2 text-sm">
          <ShieldCheck className="w-5 h-5 text-blue-600" /> Cryptographic Verification
        </h3>
        <p className="text-xs text-slate-400 mb-4">Cryptographically verify authentic uploaded medical certificates or payment receipts.</p>
        
        <div className="space-y-4">
          <div>
            <label className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">Document SHA-256 Hash</label>
            <input type="text" placeholder="e.g. 8f92a3b04c8..." className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-xs font-mono text-slate-800 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:bg-white" />
          </div>
          <button className="w-full bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold py-2.5 rounded-xl transition-colors cursor-pointer shadow-md">
            Verify Digital Certificate
          </button>
        </div>
      </div>
    </div>
  );
}

function BroadcastsTab() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs p-5 space-y-4">
        <h3 className="font-bold text-white flex items-center gap-2 text-sm">
          <Radio className="w-5 h-5 text-cyan-400" /> Broadcast Campus Alert
        </h3>
        <div className="space-y-4">
          <div>
            <label className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">Banner Message</label>
            <textarea rows={3} placeholder="e.g. Fee payment gateway scheduled maintenance from 2 PM to 4 PM today." className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-xs text-slate-800 focus:outline-none focus:ring-1 focus:ring-cyan-500 focus:bg-white resize-none"></textarea>
          </div>
          <div>
            <label className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">Target Cohort</label>
            <select className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-xs text-slate-800 focus:outline-none focus:ring-1 focus:ring-cyan-500 focus:bg-white">
              <option>All University Students</option>
              <option>B.Tech CSE & AIML Cohorts</option>
              <option>Hostel Residents Only</option>
            </select>
          </div>
          <button className="w-full bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold py-2.5 rounded-xl transition-colors flex items-center justify-center gap-2 cursor-pointer shadow-md">
            <Send className="w-4 h-4" /> Broadcast Live to Portals
          </button>
        </div>
      </div>
      
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs p-5 border-l-4 border-l-amber-500 space-y-4">
        <h3 className="font-bold text-white flex items-center gap-2 text-sm">
          <ShieldAlert className="w-5 h-5 text-amber-600" /> Situational Guardrail Override
        </h3>
        <p className="text-xs text-slate-400">Inject situational administrative directives directly into the AI system prompt.</p>
        <div className="space-y-4">
          <div>
            <label className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">Direct NLU System Directive</label>
            <textarea rows={3} placeholder="e.g. If asked about tomorrow's internal examination, state that it is rescheduled to Monday due to rain." className="w-full bg-amber-50/50 border border-amber-200 rounded-xl px-3 py-2 text-xs text-amber-900 focus:outline-none focus:ring-1 focus:ring-amber-500 focus:bg-white resize-none"></textarea>
          </div>
          <div className="flex gap-4">
            <div className="flex-1">
              <label className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">Expiry Time</label>
              <select className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-xs text-slate-800 focus:outline-none focus:ring-1 focus:ring-amber-500 focus:bg-white">
                <option>1 Hour</option>
                <option>24 Hours</option>
                <option>Until Revoked</option>
              </select>
            </div>
            <div className="flex items-end flex-1">
              <button className="w-full bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/30 text-xs font-bold py-2 rounded-xl transition-colors cursor-pointer">
                Inject Guardrail
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function AgentHealthTab() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs">
          <div className="text-xs text-slate-400 font-medium mb-1 uppercase tracking-wider">System Uptime</div>
          <div className="text-2xl font-black text-emerald-600">99.98%</div>
        </div>
        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs">
          <div className="text-xs text-slate-400 font-medium mb-1 uppercase tracking-wider">Avg Latency</div>
          <div className="text-2xl font-black text-slate-900">840ms</div>
        </div>
        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs">
          <div className="text-xs text-slate-400 font-medium mb-1 uppercase tracking-wider">Hallucination Rate</div>
          <div className="text-2xl font-black text-emerald-600">&lt; 0.1%</div>
        </div>
        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs">
          <div className="text-xs text-slate-400 font-medium mb-1 uppercase tracking-wider">Audit Free Calls Left</div>
          <div className="text-2xl font-black text-purple-300">1,492 / 1,500</div>
        </div>
      </div>

      <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs p-5">
        <h3 className="font-bold text-white mb-4 text-sm">Live University Sub-Agent Status</h3>
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-slate-100 text-slate-400 uppercase">
              <th className="pb-3 font-semibold">Agent Core</th>
              <th className="pb-3 font-semibold">Role</th>
              <th className="pb-3 font-semibold">Status</th>
              <th className="pb-3 font-semibold">Last Sync</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-slate-700">
            <tr>
              <td className="py-3 font-medium text-slate-900">Support_VIGNAN_AI</td>
              <td className="py-3 text-slate-400">Frontline Cognitive Triage</td>
              <td className="py-3"><span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 rounded text-[10px] font-bold">ONLINE</span></td>
              <td className="py-3 text-slate-500">Just now</td>
            </tr>
            <tr>
              <td className="py-3 font-medium text-slate-900">Nav_Agent_Omega</td>
              <td className="py-3 text-slate-400">Campus Maps & Dijkstra Routing</td>
              <td className="py-3"><span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 rounded text-[10px] font-bold">ONLINE</span></td>
              <td className="py-3 text-slate-500">2m ago</td>
            </tr>
            <tr>
              <td className="py-3 font-medium text-slate-900">Policy_Validator_9</td>
              <td className="py-3 text-slate-400">RLS Privacy & Statutory Guardrail</td>
              <td className="py-3"><span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 rounded text-[10px] font-bold">ONLINE</span></td>
              <td className="py-3 text-slate-500">1m ago</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}

function KanbanTab({ grievances, handleStatusUpdate }: any) {
  const statuses = ['Pending', 'In Progress', 'Resolved'];
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold text-slate-900 mb-2">Grievance Resolution Board</h2>
      <div className="flex gap-4 overflow-x-auto pb-4">
        {statuses.map(status => (
          <div key={status} className="flex-1 min-w-[300px] bg-slate-100/70 border border-slate-200 rounded-2xl p-4 flex flex-col shadow-xs">
            <h3 className="font-bold text-white text-xs uppercase tracking-wider mb-4 flex items-center justify-between pb-2 border-b border-slate-100">
              {status}
              <span className="bg-slate-200 text-slate-700 px-2 py-0.5 rounded text-[10px] font-mono">
                {grievances.filter((g: any) => g.status === status).length}
              </span>
            </h3>
            <div className="flex flex-col gap-3 overflow-y-auto">
              {grievances.filter((g: any) => g.status === status).map((g: any) => (
                <div key={g.id} className="bg-white p-4 rounded-xl shadow-2xs border border-slate-200 hover:border-slate-300 transition-all">
                  <div className="text-[10px] font-bold text-blue-400 uppercase mb-1">{g.category}</div>
                  <div className="font-medium text-slate-800 text-xs mb-2 leading-relaxed">{g.description}</div>
                  <div className="text-[11px] text-slate-400 flex justify-between items-center mt-3 pt-2 border-t border-slate-100">
                    <span className="font-mono">{g.student_id}</span>
                    {status !== 'Resolved' && (
                      <button 
                        onClick={() => handleStatusUpdate(g.id, 'grievance', status === 'Pending' ? 'In Progress' : 'Resolved')}
                        className="text-blue-400 hover:text-blue-300 text-xs font-semibold cursor-pointer"
                      >
                        Advance →
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function AuditTab() {
  const auditLogs = [
    { id: 1, time: '10:42 AM', action: 'Distress Protocol Triggered', user: 'VIGNAN-AI', detail: 'Flagged chat #892 for manual review due to negative sentiment.' },
    { id: 2, time: '10:15 AM', action: 'Knowledge Base Queried', user: 'VIGNAN-AI', detail: 'Fetched policy: Hostel Leave Guidelines 2024.' },
    { id: 3, time: '09:30 AM', action: 'Automated Email Sent', user: 'System', detail: 'Sent resolution receipt to 21BEE092@student.edu.' },
    { id: 4, time: '08:00 AM', action: 'Database Backup', user: 'System', detail: 'Nightly automated backup completed successfully.' },
  ];
  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
      <div className="p-4 border-b border-slate-100 flex justify-between items-center">
        <h2 className="text-base font-bold text-slate-900">System Audit Trail</h2>
        <span className="text-xs text-slate-500 font-mono">Immutable Log Ledger</span>
      </div>
      <table className="w-full text-left text-xs">
        <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase">
          <tr>
            <th className="px-6 py-4 font-semibold">Timestamp</th>
            <th className="px-6 py-4 font-semibold">Actor</th>
            <th className="px-6 py-4 font-semibold">Action</th>
            <th className="px-6 py-4 font-semibold">Details</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 text-slate-700">
          {auditLogs.map(log => (
            <tr key={log.id} className="hover:bg-slate-50/70 transition-colors text-slate-700">
              <td className="px-6 py-3.5 text-slate-400 font-mono whitespace-nowrap">{log.time}</td>
              <td className="px-6 py-3.5 font-semibold text-slate-900">{log.user}</td>
              <td className="px-6 py-3.5 text-blue-700 font-medium">{log.action}</td>
              <td className="px-6 py-3.5 text-slate-400">{log.detail}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function KnowledgeTab() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs md:col-span-2 space-y-4">
        <div className="flex justify-between items-center border-b border-slate-100 pb-3">
          <h3 className="font-bold text-slate-900 text-sm">Indexed Academic Regulations (RAG)</h3>
          <button className="bg-blue-600 hover:bg-blue-500 text-white px-3 py-1.5 rounded-xl text-xs font-semibold transition-colors cursor-pointer shadow-sm">
            + Index Document
          </button>
        </div>
        <div className="space-y-2.5">
          {[
            { name: 'Student Code of Conduct 2024.pdf', tokens: '45k', status: 'Indexed' },
            { name: 'Hostel Rules & Regulations.pdf', tokens: '12k', status: 'Indexed' },
            { name: 'Fee Structure AY2024-25.xlsx', tokens: '8k', status: 'Indexed' },
            { name: 'Exam Rescheduling Policy.pdf', tokens: '15k', status: 'Indexing...' },
          ].map(doc => (
            <div key={doc.name} className="flex justify-between items-center p-3 hover:bg-slate-50 rounded-xl border border-slate-200 transition-colors">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-blue-500/10 border border-blue-500/20 text-blue-400 rounded-lg flex items-center justify-center text-xs">📄</div>
                <div>
                  <div className="text-xs font-semibold text-slate-900">{doc.name}</div>
                  <div className="text-[10px] text-slate-400">{doc.tokens} tokens indexed</div>
                </div>
              </div>
              <span className={`text-[10px] font-bold px-2 py-0.5 rounded-md ${doc.status === 'Indexed' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'bg-amber-500/20 text-amber-300 border border-amber-500/30'}`}>
                {doc.status}
              </span>
            </div>
          ))}
        </div>
      </div>
      
      <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs space-y-4">
        <h3 className="font-bold text-white text-sm border-b border-slate-100 pb-3">Vector Embedding Metrics</h3>
        <div className="space-y-3 text-xs">
          <div className="flex justify-between border-b border-slate-100 pb-2">
            <span className="text-slate-400">Total Vectors:</span>
            <span className="font-mono font-bold text-slate-900">12,405</span>
          </div>
          <div className="flex justify-between border-b border-slate-100 pb-2">
            <span className="text-slate-400">Model:</span>
            <span className="font-mono font-semibold text-purple-300">text-embedding-3-small</span>
          </div>
          <div className="flex justify-between border-b border-slate-100 pb-2">
            <span className="text-slate-400">Dimensions:</span>
            <span className="font-mono font-bold text-slate-900">1536</span>
          </div>
          <div className="flex justify-between pb-1">
            <span className="text-slate-400">Last Synced:</span>
            <span className="font-mono text-emerald-600">Today, 02:00 AM</span>
          </div>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// COGNITIVE REMEDIATION & GEMINI GOVERNANCE TAB (NODAL OFFICER SURVEILLANCE)
// ============================================================================

function CognitiveRemediationTab() {
  const [remediations, setRemediations] = useState<any[]>([]);
  const [summary, setSummary] = useState({
    total_audited: 0,
    active_rules: 0,
    policy_protected: 0,
    inactive_rules: 0,
    raw_feedback_count: 0
  });
  const [recentFeedback, setRecentFeedback] = useState<any[]>([]);
  const [geminiStatus, setGeminiStatus] = useState<any>({
    enable_gemini: false,
    masked_api_key: '',
    has_key: false,
    active_model: 'gemini-2.5-flash',
    available_models: ['gemini-2.5-flash', 'gemini-2.5-pro', 'gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-3.5-flash'],
    quota: {
      daily_requests_used: 0,
      daily_requests_limit: 1500,
      daily_requests_remaining: 1500,
      minute_requests_used: 0,
      minute_requests_limit: 15,
      minute_requests_remaining: 15,
      total_requests_all_time: 0,
      recent_calls: []
    }
  });

  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'ALL' | 'ACTIVE' | 'POLICY_PROTECTED' | 'INACTIVE'>('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  // Key Switcher & Config State
  const [showConfigBox, setShowConfigBox] = useState(false);
  const [newApiKey, setNewApiKey] = useState('');
  const [showKeyText, setShowKeyText] = useState(false);
  const [selectedModel, setSelectedModel] = useState('gemini-2.5-flash');
  const [enableGeminiToggle, setEnableGeminiToggle] = useState(false);
  const [updatingConfig, setUpdatingConfig] = useState(false);
  const [configMessage, setConfigMessage] = useState<{ text: string; type: 'success' | 'error' } | null>(null);

  // Ping State
  const [pinging, setPinging] = useState(false);
  const [pingResult, setPingResult] = useState<{ success: boolean; latency_ms?: number; message?: string; error?: string } | null>(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const [remRes, gemRes] = await Promise.all([
        fetchCognitiveRemediations(),
        fetchGeminiStatus()
      ]);

      if (remRes.success) {
        setRemediations(remRes.remediations || []);
        if (remRes.summary) setSummary(remRes.summary);
        if (remRes.recentFeedback) setRecentFeedback(remRes.recentFeedback);
      }

      if (gemRes.success) {
        setGeminiStatus(gemRes);
        setSelectedModel(gemRes.active_model || 'gemini-2.5-flash');
        setEnableGeminiToggle(Boolean(gemRes.enable_gemini));
      }
    } catch (e) {
      console.error('Failed to load cognitive remediation data:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleToggleStatus = async (remId: string, currentStatus: string) => {
    const nextStatus = currentStatus === 'ACTIVE' ? 'INACTIVE' : 'ACTIVE';
    const res = await updateRemediationStatus(remId, nextStatus);
    if (res.success) {
      setRemediations(prev =>
        prev.map(r => (r.remediation_id === remId ? { ...r, status: nextStatus } : r))
      );
      setSummary(prev => ({
        ...prev,
        active_rules: nextStatus === 'ACTIVE' ? prev.active_rules + 1 : Math.max(0, prev.active_rules - 1),
        inactive_rules: nextStatus === 'INACTIVE' ? prev.inactive_rules + 1 : Math.max(0, prev.inactive_rules - 1)
      }));
    } else {
      alert(res.error || 'Failed to update rule status.');
    }
  };

  const handleDeleteRule = async (remId: string) => {
    if (!window.confirm(`Permanently delete remediation rule ${remId}? The bot will revert to default routing for these queries.`)) {
      return;
    }
    const res = await deleteRemediationRule(remId);
    if (res.success) {
      setRemediations(prev => prev.filter(r => r.remediation_id !== remId));
      loadData();
    } else {
      alert(res.error || 'Failed to delete remediation rule.');
    }
  };

  const handleSaveGeminiConfig = async (e: React.FormEvent) => {
    e.preventDefault();
    setUpdatingConfig(true);
    setConfigMessage(null);

    const payload: { apiKey?: string; enableGemini: boolean; model: string } = {
      enableGemini: enableGeminiToggle,
      model: selectedModel
    };
    if (newApiKey.trim()) {
      payload.apiKey = newApiKey.trim();
    }

    const res = await updateGeminiConfig(payload);
    setUpdatingConfig(false);

    if (res.success) {
      setConfigMessage({ text: res.message || 'Gemini configuration successfully verified and saved!', type: 'success' });
      setNewApiKey('');
      loadData();
    } else {
      setConfigMessage({ text: res.error || 'Failed to update Gemini configuration.', type: 'error' });
    }
  };

  const handlePingGemini = async () => {
    setPinging(true);
    setPingResult(null);
    const res = await pingGeminiConnection();
    setPinging(false);
    setPingResult(res);
  };

  const filteredRemediations = remediations.filter(rem => {
    if (filter === 'ACTIVE' && rem.status !== 'ACTIVE') return false;
    if (filter === 'POLICY_PROTECTED' && rem.status !== 'POLICY_PROTECTED') return false;
    if (filter === 'INACTIVE' && rem.status !== 'INACTIVE') return false;

    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    return (
      (rem.user_query && rem.user_query.toLowerCase().includes(q)) ||
      (rem.mismatch_reason && rem.mismatch_reason.toLowerCase().includes(q)) ||
      (rem.target_entity && rem.target_entity.toLowerCase().includes(q)) ||
      (rem.intended_intent && rem.intended_intent.toLowerCase().includes(q)) ||
      (rem.student_comment && rem.student_comment.toLowerCase().includes(q))
    );
  });

  const quota = geminiStatus.quota || {};
  const dailyUsed = quota.daily_requests_used ?? 0;
  const dailyLimit = quota.daily_requests_limit ?? 1500;
  const dailyRemaining = quota.daily_requests_remaining ?? 1500;
  const usedPct = Math.min(100, Math.round((dailyUsed / dailyLimit) * 100));

  return (
    <div className="space-y-6">
      {/* Top Banner Header - Perfectly Balanced Size, Clean Spacing & Responsive Actions */}
      <div className="p-5 sm:p-6 rounded-2xl bg-white text-slate-900 shadow-xs border border-slate-200 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-80 h-80 bg-blue-50/60 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div className="space-y-1.5 max-w-3xl">
            <div className="flex flex-wrap items-center gap-2 mb-1">
              <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold tracking-wide uppercase bg-blue-50 text-blue-700 border border-blue-200 flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-blue-600 animate-pulse" /> Cognitive Remediation Hub
              </span>
              <span className="text-[11px] font-mono text-slate-500 bg-slate-50 border border-slate-200 px-2 py-0.5 rounded">
                Neon PostgreSQL Synced
              </span>
            </div>
            <h2 className="text-xl sm:text-2xl font-bold tracking-tight text-slate-900 leading-tight">
              AI Feedback Surveillance & Gemini Governance
            </h2>
            <p className="text-xs text-slate-500 leading-relaxed">
              Surveil queries disliked by students, inspect Gemini intent-audit diagnoses, review self-learned Dijkstra routing rules pushed to Neon, and manage Google Gemini API quotas & credentials.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2.5 shrink-0 self-start lg:self-center">
            <button
              onClick={handlePingGemini}
              disabled={pinging}
              className="h-9 inline-flex items-center gap-1.5 px-3.5 rounded-xl text-xs font-semibold bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 shadow-2xs transition-all cursor-pointer disabled:opacity-50"
              title="Send lightweight diagnostic ping to Google Gemini API"
            >
              <Zap className={`w-3.5 h-3.5 text-amber-500 ${pinging ? 'animate-spin' : ''}`} />
              {pinging ? 'Pinging Gemini...' : 'Ping Gemini API'}
            </button>

            <button
              onClick={() => setShowConfigBox(!showConfigBox)}
              className="h-9 inline-flex items-center gap-1.5 px-4 rounded-xl text-xs font-bold bg-blue-600 hover:bg-blue-700 text-white shadow-xs transition-all cursor-pointer"
            >
              <KeyRound className="w-3.5 h-3.5" />
              {showConfigBox ? 'Hide Manager' : 'Switch Gemini API Key'}
            </button>

            <button
              onClick={loadData}
              disabled={loading}
              className="h-9 w-9 inline-flex items-center justify-center rounded-xl text-slate-600 hover:text-slate-900 bg-white hover:bg-slate-50 border border-slate-200 shadow-2xs transition-all cursor-pointer"
              title="Refresh live data from Neon DB"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>

        {/* Live Ping Notification Banner */}
        {pingResult && (
          <div className={`mt-4 p-3 rounded-xl text-xs flex items-center justify-between border ${
            pingResult.success ? 'bg-emerald-500/15 border-emerald-500/30 text-emerald-200' : 'bg-rose-500/15 border-rose-500/30 text-rose-200'
          }`}>
            <div className="flex items-center gap-2">
              {pingResult.success ? <CheckCircle className="w-4 h-4 text-emerald-600" /> : <AlertCircle className="w-4 h-4 text-rose-600" />}
              <span>{pingResult.message || pingResult.error}</span>
            </div>
            {pingResult.latency_ms !== undefined && (
              <span className="font-mono font-bold bg-black/40 px-2 py-0.5 rounded text-[10px] text-emerald-300">
                {pingResult.latency_ms} ms roundtrip
              </span>
            )}
          </div>
        )}
      </div>

      {/* Top 4 Telemetry Metrics Cards - Crisp White matching Screenshot 2 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Gemini Free Tier Quota */}
        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs space-y-3 hover:shadow-md transition-all">
          <div className="flex items-center justify-between">
            <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">Daily API Quota</div>
            <div className="p-1.5 bg-blue-50 text-blue-600 border border-blue-200 rounded-lg">
              <Activity className="w-4 h-4" />
            </div>
          </div>
          <div>
            <div className="text-2xl font-black text-slate-900 tracking-tight flex items-baseline gap-1">
              <span>{dailyRemaining.toLocaleString()}</span>
              <span className="text-xs font-semibold text-slate-500 font-sans">/ {dailyLimit.toLocaleString()} RPD</span>
            </div>
            <div className="text-[11px] text-slate-500 font-medium mt-0.5">Remaining Google Gemini Free Calls</div>
          </div>
          {/* Visual Progress Bar */}
          <div className="space-y-1">
            <div className="w-full bg-slate-100 border border-slate-200 h-2 rounded-full overflow-hidden">
              <div
                className={`h-full transition-all duration-500 ${
                  usedPct > 80 ? 'bg-rose-500' : usedPct > 50 ? 'bg-amber-500' : 'bg-emerald-500'
                }`}
                style={{ width: `${Math.max(5, usedPct)}%` }}
              />
            </div>
            <div className="flex justify-between text-[10px] text-slate-500 font-medium font-mono">
              <span>{dailyUsed} calls used today</span>
              <span>15 RPM Limit</span>
            </div>
          </div>
        </div>

        {/* Card 2: Engine Status & Active Key */}
        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs space-y-3 hover:shadow-md transition-all">
          <div className="flex items-center justify-between">
            <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">Gemini Engine Status</div>
            <div className="flex items-center gap-1.5">
              <span className={`h-2.5 w-2.5 rounded-full ${geminiStatus.enable_gemini ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'}`} />
              <span className={`text-xs font-bold ${geminiStatus.enable_gemini ? 'text-emerald-700' : 'text-amber-700'}`}>
                {geminiStatus.enable_gemini ? 'ENABLED' : 'PAUSED'}
              </span>
            </div>
          </div>
          <div>
            <div className="text-xs font-bold text-slate-800 font-mono truncate">
              {geminiStatus.masked_api_key || 'No Key Configured'}
            </div>
            <div className="text-[11px] text-slate-500 font-medium mt-0.5">Active Credential (Masked)</div>
          </div>
          <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px]">
            <span className="text-slate-500 font-medium">Active Model:</span>
            <span className="font-bold font-mono text-purple-700 bg-purple-50 px-2 py-0.5 rounded border border-purple-200 text-[10px]">
              {geminiStatus.active_model || 'gemini-2.5-flash'}
            </span>
          </div>
        </div>

        {/* Card 3: Active Remediations in Neon */}
        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs space-y-3 hover:shadow-md transition-all">
          <div className="flex items-center justify-between">
            <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">Active Rules in Neon</div>
            <div className="p-1.5 bg-purple-50 text-purple-600 border border-purple-200 rounded-lg">
              <Bot className="w-4 h-4" />
            </div>
          </div>
          <div>
            <div className="text-2xl font-black text-purple-700 tracking-tight">
              {summary.active_rules} <span className="text-xs font-bold text-slate-500 font-sans">Rules</span>
            </div>
            <div className="text-[11px] text-slate-500 font-medium mt-0.5">Self-Learned Query Interceptors</div>
          </div>
          <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px]">
            <span className="text-slate-500 font-medium">Runtime Routing:</span>
            <span className="font-bold text-emerald-600">Tier 0 Intercept</span>
          </div>
        </div>

        {/* Card 4: Policy Defense Guardrails */}
        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs space-y-3 hover:shadow-md transition-all">
          <div className="flex items-center justify-between">
            <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">Policy Guardrails Upheld</div>
            <div className="p-1.5 bg-emerald-50 text-emerald-600 border border-emerald-200 rounded-lg">
              <Shield className="w-4 h-4" />
            </div>
          </div>
          <div>
            <div className="text-2xl font-black text-emerald-600 tracking-tight">
              {summary.policy_protected} <span className="text-xs font-bold text-slate-500 font-sans">Protected</span>
            </div>
            <div className="text-[11px] text-slate-500 font-medium mt-0.5">Clause 2.1 RLAC & Rules Upheld</div>
          </div>
          <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px]">
            <span className="text-slate-500 font-medium">Integrity Check:</span>
            <span className="font-bold text-blue-600">100% Zero-Leak</span>
          </div>
        </div>
      </div>

      {/* API Key Switcher & Configuration Drawer */}
      {showConfigBox && (
        <div className="bg-white rounded-2xl border-2 border-blue-300 p-6 shadow-xl space-y-5 animate-in fade-in-50 duration-200">
          <div className="flex items-center justify-between border-b border-slate-100 pb-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-500/10 border border-purple-500/20 text-purple-300 rounded-xl">
                <KeyRound className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-slate-900">Switch Google Gemini API Key & Engine Config</h3>
                <p className="text-xs text-slate-400">
                  Validated live with Google before persisting to Neon DB <code className="font-mono text-purple-300">system_settings</code>. Survives Render reboots.
                </p>
              </div>
            </div>
            <button
              onClick={() => setShowConfigBox(false)}
              className="p-1 text-slate-400 hover:text-white rounded-lg cursor-pointer"
            >
              <XCircle className="w-5 h-5" />
            </button>
          </div>

          <form onSubmit={handleSaveGeminiConfig} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Input New API Key */}
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-300 flex items-center justify-between">
                  <span>Google Gemini API Key</span>
                  <button
                    type="button"
                    onClick={() => setShowKeyText(!showKeyText)}
                    className="text-[11px] text-purple-300 hover:underline cursor-pointer"
                  >
                    {showKeyText ? 'Hide Key' : 'Reveal Key'}
                  </button>
                </label>
                <div className="relative">
                  <input
                    type={showKeyText ? 'text' : 'password'}
                    placeholder="Paste new API Key (e.g. AIzaSy... or AQ.Ab8RN6...)"
                    value={newApiKey}
                    onChange={e => setNewApiKey(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-slate-300 text-slate-900 placeholder-slate-400 focus:bg-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 text-xs font-mono transition-all"
                  />
                </div>
                <p className="text-[11px] text-slate-400">Leave blank if only updating model or enablement status.</p>
              </div>

              {/* Model Selection */}
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-300">Target Gemini Model</label>
                <select
                  value={selectedModel}
                  onChange={e => setSelectedModel(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-slate-300 text-slate-900 focus:bg-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 text-xs font-mono cursor-pointer"
                >
                  {(geminiStatus.available_models || ['gemini-2.5-flash', 'gemini-2.5-pro', 'gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-3.5-flash']).map((m: string) => (
                    <option key={m} value={m}>
                      {m}
                    </option>
                  ))}
                </select>
                <p className="text-[11px] text-slate-400">gemini-2.5-flash recommended for fastest sub-second cognitive audits.</p>
              </div>
            </div>

            {/* Enable Gemini Toggle */}
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between">
              <div className="space-y-0.5">
                <div className="text-xs font-bold text-slate-900">Enable Autonomous Gemini Feedback Loop</div>
                <div className="text-[11px] text-slate-400">
                  When active, student downvotes automatically trigger the Gemini cognitive audit in the background and persist verified remediations to Neon.
                </div>
              </div>
              <button
                type="button"
                onClick={() => setEnableGeminiToggle(!enableGeminiToggle)}
                className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                  enableGeminiToggle ? 'bg-purple-600' : 'bg-slate-700'
                }`}
              >
                <span
                  className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                    enableGeminiToggle ? 'translate-x-5' : 'translate-x-0'
                  }`}
                />
              </button>
            </div>

            {/* Status Toast */}
            {configMessage && (
              <div className={`p-3 rounded-xl text-xs flex items-center gap-2 ${
                configMessage.type === 'success' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
              }`}>
                {configMessage.type === 'success' ? <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0" /> : <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />}
                <span>{configMessage.text}</span>
              </div>
            )}

            <div className="flex justify-end gap-3 pt-2">
              <button
                type="button"
                onClick={() => setShowConfigBox(false)}
                className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition-colors cursor-pointer"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={updatingConfig}
                className="px-5 py-2 rounded-xl text-xs font-bold text-white bg-purple-600 hover:bg-purple-500 shadow-md shadow-purple-600/30 transition-all disabled:opacity-50 flex items-center gap-1.5 cursor-pointer"
              >
                {updatingConfig ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Check className="w-3.5 h-3.5" />}
                {updatingConfig ? 'Validating with Google...' : 'Verify & Switch API Key'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Filter and Search Bar - Crisp White matching Screenshot 2 */}
      <div className="bg-white rounded-2xl p-3.5 sm:p-4 border border-slate-200 shadow-xs flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-2 w-full sm:w-auto">
          <button
            onClick={() => setFilter('ALL')}
            className={`h-9 px-3.5 rounded-xl text-xs font-semibold transition-all cursor-pointer flex items-center gap-1.5 ${
              filter === 'ALL'
                ? 'bg-blue-600 text-white shadow-xs border border-blue-600'
                : 'bg-slate-50 hover:bg-slate-100 text-slate-600 border border-slate-200'
            }`}
          >
            All Audited ({summary.total_audited})
          </button>
          <button
            onClick={() => setFilter('ACTIVE')}
            className={`h-9 px-3.5 rounded-xl text-xs font-semibold transition-all flex items-center gap-1.5 cursor-pointer ${
              filter === 'ACTIVE'
                ? 'bg-emerald-600 text-white shadow-xs border border-emerald-600'
                : 'bg-slate-50 hover:bg-slate-100 text-slate-600 border border-slate-200'
            }`}
          >
            <CheckCircle className="w-3.5 h-3.5" /> Active in Neon ({summary.active_rules})
          </button>
          <button
            onClick={() => setFilter('POLICY_PROTECTED')}
            className={`h-9 px-3.5 rounded-xl text-xs font-semibold transition-all flex items-center gap-1.5 cursor-pointer ${
              filter === 'POLICY_PROTECTED'
                ? 'bg-purple-600 text-white shadow-xs border border-purple-600'
                : 'bg-slate-50 hover:bg-slate-100 text-slate-600 border border-slate-200'
            }`}
          >
            <Shield className="w-3.5 h-3.5" /> Policy Upheld ({summary.policy_protected})
          </button>
          <button
            onClick={() => setFilter('INACTIVE')}
            className={`h-9 px-3.5 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
              filter === 'INACTIVE'
                ? 'bg-slate-700 text-white shadow-xs border border-slate-700'
                : 'bg-slate-50 hover:bg-slate-100 text-slate-600 border border-slate-200'
            }`}
          >
            Inactive ({summary.inactive_rules})
          </button>
        </div>

        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search query, landmark, reason..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            className="w-full h-9 pl-9 pr-3 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 focus:bg-white transition-all"
          />
        </div>
      </div>

      {/* Disliked Queries & Remediations List */}
      <div className="space-y-4">
        {loading ? (
          <div className="bg-white rounded-2xl p-12 text-center border border-slate-200 shadow-xs space-y-3">
            <RefreshCw className="w-8 h-8 text-purple-400 animate-spin mx-auto" />
            <div className="text-sm font-semibold text-slate-300">Loading live audit trail from Neon PostgreSQL...</div>
          </div>
        ) : filteredRemediations.length === 0 ? (
          <div className="bg-white rounded-2xl p-10 sm:p-14 text-center border border-slate-200 shadow-xs space-y-3">
            <div className="w-12 h-12 bg-slate-50 border border-slate-200 rounded-2xl flex items-center justify-center mx-auto text-slate-400 shadow-2xs">
              <Bot className="w-6 h-6 text-slate-400" />
            </div>
            <div className="text-base font-bold text-slate-900">No Audited Queries Found</div>
            <p className="text-xs text-slate-500 max-w-md mx-auto leading-relaxed">
              No disliked queries matching the active filter. When a student downvotes a query in the chat, the autonomous Gemini loop audits it here.
            </p>
          </div>
        ) : (
          filteredRemediations.map((rem: any) => {
            const isActive = rem.status === 'ACTIVE';
            const isPolicy = rem.status === 'POLICY_PROTECTED';
            const triggers: string[] = Array.isArray(rem.trigger_patterns) ? rem.trigger_patterns : [];

            return (
              <div
                key={rem.remediation_id}
                className="bg-white rounded-2xl border border-slate-200 transition-all shadow-xs hover:shadow-md overflow-hidden"
              >
                {/* Header Strip matching Screenshot 2 */}
                <div className="p-4 sm:px-6 bg-slate-50/70 border-b border-slate-100 flex flex-wrap items-center justify-between gap-2 text-xs">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold ${
                      isActive ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' :
                      isPolicy ? 'bg-purple-50 text-purple-700 border border-purple-200' :
                      'bg-slate-100 text-slate-600 border border-slate-200'
                    }`}>
                      {isActive && <CheckCircle className="w-3 h-3 text-emerald-600" />}
                      {isPolicy && <Shield className="w-3 h-3 text-purple-600" />}
                      {rem.status || 'UNKNOWN'}
                    </span>

                    <span className="font-bold font-mono text-[10px] text-slate-600 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                      {rem.intended_intent || 'GENERAL'}
                    </span>

                    <span className="font-mono text-[11px] text-slate-400">
                      ID: {rem.remediation_id}
                    </span>
                  </div>

                  <div className="flex items-center gap-3 text-slate-400 text-[11px]">
                    <span className="font-mono">{rem.created_at ? new Date(rem.created_at).toLocaleString() : ''}</span>
                    
                    <button
                      onClick={() => handleToggleStatus(rem.remediation_id, rem.status)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-semibold cursor-pointer transition-colors border ${
                        isActive ? 'bg-amber-50 text-amber-700 border-amber-200 hover:bg-amber-100' :
                        'bg-emerald-50 text-emerald-700 border-emerald-200 hover:bg-emerald-100'
                      }`}
                      title={isActive ? 'Pause rule from intercepting' : 'Activate rule for NLU interception'}
                    >
                      {isActive ? 'Pause Rule' : 'Activate Rule'}
                    </button>

                    <button
                      onClick={() => handleDeleteRule(rem.remediation_id)}
                      className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors cursor-pointer"
                      title="Delete rule permanently"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {/* Main Card Content matching Screenshot 2 */}
                <div className="p-5 sm:p-6 space-y-4">
                  {/* Student Disliked Query Section matching Screenshot 2 */}
                  <div className="space-y-1.5">
                    <div className="flex items-center gap-1.5 text-xs font-bold text-rose-600 uppercase tracking-wider">
                      <ThumbsDown className="w-3.5 h-3.5 text-rose-500" />
                      <span>STUDENT DISLIKED QUERY</span>
                    </div>
                    <div className="text-base font-bold text-slate-900 bg-rose-50/50 p-3.5 rounded-xl border border-rose-100 font-sans tracking-tight">
                      "{rem.user_query}"
                    </div>
                    {rem.student_comment && (
                      <div className="text-xs text-rose-800 bg-rose-100/70 px-3 py-2 rounded-lg font-medium flex items-center gap-1.5 border border-rose-200/80">
                        <span className="font-bold uppercase text-[10px] tracking-wide">STUDENT FEEDBACK:</span>
                        <span>"{rem.student_comment}"</span>
                      </div>
                    )}
                  </div>

                  {/* Side-by-Side: Delivered vs Gemini Audit matching Screenshot 2 */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    {/* Left: Bot Output Delivered */}
                    <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
                      <div className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center justify-between">
                        <span>DELIVERED BOT OUTPUT (DISLIKED)</span>
                        <span className="text-[10px] font-mono text-slate-400">CONVERSATION TURN</span>
                      </div>
                      <div className="text-xs text-slate-700 font-sans line-clamp-4 leading-relaxed whitespace-pre-wrap">
                        {rem.bot_output || 'No output recorded'}
                      </div>
                    </div>

                    {/* Right: Gemini Audit Diagnosis */}
                    <div className={`p-4 rounded-xl border space-y-2 ${
                      rem.mismatch_detected ? 'bg-purple-50/60 border-purple-200/70' : 'bg-emerald-50/60 border-emerald-200/70'
                    }`}>
                      <div className="text-xs font-bold uppercase tracking-wider flex items-center justify-between">
                        <span className={rem.mismatch_detected ? 'text-purple-700' : 'text-emerald-700'}>
                          GEMINI AUTONOMOUS AUDIT DIAGNOSIS
                        </span>
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                          rem.mismatch_detected ? 'bg-purple-100 text-purple-700 border border-purple-200' : 'bg-emerald-100 text-emerald-700 border border-emerald-200'
                        }`}>
                          {rem.mismatch_detected ? 'MISMATCH DETECTED' : 'POLICY UPHELD'}
                        </span>
                      </div>
                      <p className="text-xs text-slate-700 font-medium leading-relaxed">
                        {rem.mismatch_reason || 'No audit explanation provided.'}
                      </p>
                    </div>
                  </div>

                  {/* What Gemini Instructed & Pushed to Neon matching Screenshot 2 */}
                  {rem.mismatch_detected && (
                    <div className="p-4 rounded-xl bg-slate-50/80 border border-slate-200 space-y-3">
                      <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
                        <span className="font-bold text-indigo-900 uppercase tracking-wider flex items-center gap-1.5">
                          <Database className="w-3.5 h-3.5 text-indigo-600" />
                          GEMINI REMEDIATION PUSHED TO NEON
                        </span>
                        <div className="flex items-center gap-2 text-xs">
                          <span className="text-slate-500 font-medium">Routing Action:</span>
                          <span className="bg-white px-2.5 py-1 rounded border border-slate-200 font-mono font-semibold text-slate-700 shadow-2xs">
                            {rem.routing_action || 'TOOL:get_campus_location_and_navigation'}
                          </span>
                        </div>
                      </div>

                      {rem.target_entity && (
                        <div className="text-xs text-slate-600 flex items-center gap-2">
                          <span className="font-semibold text-slate-500">Target Entity:</span>
                          <span className="font-mono font-bold bg-white px-2 py-0.5 rounded border border-slate-200 text-purple-700">
                            {rem.target_entity}
                          </span>
                        </div>
                      )}

                      {triggers.length > 0 && (
                        <div className="space-y-1.5">
                          <div className="text-[11px] font-semibold text-slate-500">Learned Trigger Variations:</div>
                          <div className="flex flex-wrap gap-1.5">
                            {triggers.map((t, idx) => (
                              <span
                                key={idx}
                                className="px-2.5 py-1 rounded-full text-xs font-mono font-medium bg-white text-slate-700 border border-slate-200 shadow-2xs"
                              >
                                "{t}"
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
