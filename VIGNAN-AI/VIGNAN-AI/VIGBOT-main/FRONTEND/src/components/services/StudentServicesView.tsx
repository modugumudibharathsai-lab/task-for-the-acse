"use client";

import React, { useEffect, useState } from "react";
import {
  LifeBuoy,
  FileCheck2,
  AlertTriangle,
  Users,
  GraduationCap,
  Plus,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  Clock,
  ChevronDown,
  ChevronUp,
  XCircle,
  Loader2,
} from "lucide-react";
import { ServiceRequest } from "@/data/services";
import { CURRENT_STUDENT } from "@/data/student";
import { useStudent } from "@/context/StudentContext";
import { useLanguage } from "@/context/LanguageContext";
import { fetchStudentDbActivity, withdrawTicket } from "@/actions/db";

interface StudentServicesViewProps {
  services: ServiceRequest[];
  onOpenNewServiceModal: (category?: string) => void;
  onAskHelpdesk: (query: string) => void;
}

export const StudentServicesView: React.FC<StudentServicesViewProps> = ({
  services,
  onOpenNewServiceModal,
  onAskHelpdesk,
}) => {
  const { studentData } = useStudent();
  const { t, tDynamic } = useLanguage();
  const student = studentData?.profile || CURRENT_STUDENT;
  
  const [dbComplaints, setDbComplaints] = useState<any[]>([]);
  const [dbClubApps, setDbClubApps] = useState<any[]>([]);
  
  const [expandedReq, setExpandedReq] = useState<string | null>(null);
  const [withdrawingId, setWithdrawingId] = useState<string | null>(null);
  const [withdrawReason, setWithdrawReason] = useState("");
  const [isSubmittingWithdraw, setIsSubmittingWithdraw] = useState(false);

  const loadDbActivity = async () => {
    const res = await fetchStudentDbActivity(student.id);
    if (res.success) {
      setDbComplaints(res.complaints || []);
      setDbClubApps(res.clubApps || []);
    }
  };

  useEffect(() => {
    loadDbActivity();
  }, [student.id]);

  const handleWithdraw = async (id: string, type: 'club' | 'grievance') => {
    if (!withdrawReason.trim()) return;
    setIsSubmittingWithdraw(true);
    const res = await withdrawTicket(id, type, withdrawReason, student.id);
    setIsSubmittingWithdraw(false);
    if (res.success) {
      setWithdrawingId(null);
      setWithdrawReason("");
      loadDbActivity(); // refresh to show withdrawn status and reason
    } else {
      alert("Failed to withdraw: " + res.error);
    }
  };

  const serviceCards = [
    {
      category: "Certificate",
      title: t.bonafideCert || "Apply for a Certificate",
      desc: "Instant verification for Bonafide, Custodian, Medium of Instruction, or Course Completion statement.",
      icon: FileCheck2,
      color: "text-blue-600 bg-blue-50 border-blue-200",
    },
    {
      category: "Mentor Meeting",
      title: t.chipBookMentor || "Book Mentor Meeting",
      desc: "Schedule a one-on-one advisory session with Dr. Radhika Sharma (Cabin C-402).",
      icon: Users,
      color: "text-indigo-600 bg-indigo-50 border-indigo-200",
    },
    {
      category: "Grievance",
      title: t.grievanceRedressal || "Raise an Academic Grievance",
      desc: "Submit formal appeals on internal marks evaluations, attendance condonation, or hostel amenities.",
      icon: AlertTriangle,
      color: "text-amber-600 bg-amber-50 border-amber-200",
    },
    {
      category: "Academic Support",
      title: "Request Academic Support",
      desc: "Enroll in peer tutoring cohorts, remedial programming clinics, or library study groups.",
      icon: GraduationCap,
      color: "text-emerald-600 bg-emerald-50 border-emerald-200",
    },
  ];

  const toggleExpand = (id: string) => {
    // Only toggle if we are not actively withdrawing
    if (withdrawingId === id) return;
    setExpandedReq(expandedReq === id ? null : id);
    setWithdrawingId(null);
    setWithdrawReason("");
  };

  return (
    <div className="@container space-y-6">
      {/* Header */}
      <div className="flex flex-col @lg:flex-row @lg:items-center justify-between gap-3 border-b border-slate-200/80 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-foreground">{t.servicesTitle || "Student Services & Applications"}</h2>
            
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            {t.servicesSubtitle || "Convert conversational requests into verified institutional tickets."}
          </p>
        </div>

        <button
          onClick={() => onOpenNewServiceModal("Certificate")}
          className="flex items-center gap-1.5 rounded-xl bg-blue-600 px-3.5 py-2 text-xs font-semibold text-white shadow-xs hover:bg-blue-700 transition-colors cursor-pointer"
        >
          <Plus className="h-4 w-4" />
          <span>{t.newServiceRequest || "New Service Request"}</span>
        </button>
      </div>

      {/* 4 Action Cards */}
      <div className="grid grid-cols-1 @xl:grid-cols-2 @5xl:grid-cols-4 gap-4">
        {serviceCards.map((card) => {
          const Icon = card.icon;
          return (
            <div
              key={card.category}
              onClick={() => onOpenNewServiceModal(card.category)}
              className="rounded-lg border border-slate-200 bg-card p-5 shadow-2xs hover:shadow-sm hover:border-blue-300 transition-all cursor-pointer flex flex-col justify-between group"
            >
              <div>
                <div className={`flex h-10 w-10 items-center justify-center rounded-xl ${card.color} mb-3`}>
                  <Icon className="h-5 w-5" />
                </div>
                <h3 className="font-bold text-foreground text-sm mb-1">{card.title}</h3>
                <p className="text-xs text-muted-foreground leading-relaxed">{card.desc}</p>
              </div>

              <div className="mt-4 pt-2 border-t border-slate-100 flex items-center justify-between text-xs font-semibold text-blue-600 group-hover:text-blue-800">
                <span>{t.createServiceRequest}</span>
                <ArrowRight className="h-3.5 w-3.5 transition-transform group-hover:translate-x-1" />
              </div>
            </div>
          );
        })}
      </div>

      {/* Active Service Requests List */}
      <div className="rounded-lg border border-slate-200 bg-card overflow-hidden shadow-2xs">
        <div className="bg-muted/50/80 px-5 py-3 border-b border-slate-200 flex items-center justify-between">
          <h3 className="text-xs font-bold uppercase tracking-wider text-foreground">
            Active Requests & Tickets for {student.id}
          </h3>
          <span className="text-xs text-muted-foreground font-medium">
            {services.length + dbComplaints.length + dbClubApps.length} Submitted Tickets
          </span>
        </div>

        <div className="divide-y divide-slate-100">
          {/* DB Club Applications */}
          {dbClubApps.map((app) => {
            const isWithdrawn = app.status === 'Withdrawn';
            const expId = `club-${app.id}`;
            return (
            <div 
              key={expId} 
              className={`p-4 hover:bg-muted/50/60 transition-colors cursor-pointer ${isWithdrawn ? 'opacity-75' : ''}`}
              onClick={() => toggleExpand(expId)}
            >
              <div className="flex flex-col @lg:flex-row @lg:items-center justify-between gap-2">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-purple-600">CLUB-{app.id}</span>
                    <span className="rounded-md bg-muted px-2 py-0.5 text-sm font-bold text-foreground">
                      Club Enrollment
                    </span>
                    <span className="text-xs font-bold text-foreground">Application to {app.club_id}</span>
                  </div>
                  <p className="text-xs text-muted-foreground leading-relaxed">Student: {student.name} ({student.id})</p>
                  <div className="flex items-center gap-3 text-sm text-muted-foreground pt-0.5">
                    <span>Submitted: {new Date(app.timestamp).toLocaleString()}</span>
                    <span>•</span>
                    <span>Department: <strong>Student Life</strong></span>
                  </div>
                </div>

                <div className="flex items-center @lg:flex-col @lg:items-end gap-2 shrink-0">
                  <span className={`rounded-full px-2.5 py-0.5 text-sm font-bold border flex items-center gap-1 ${
                    isWithdrawn ? 'bg-slate-50 text-slate-500 border-slate-200' : 'bg-emerald-50 text-emerald-800 border-emerald-200'
                  }`}>
                    {isWithdrawn ? <XCircle className="h-3 w-3" /> : <CheckCircle2 className="h-3 w-3 text-emerald-600" />}
                    <span>{app.status}</span>
                  </span>
                  <span className="text-sm font-medium text-slate-400">Priority: Normal</span>
                </div>
              </div>
              
              {/* Expanded Status View */}
              {expandedReq === expId && (
                <div className="mt-4 pt-4 border-t border-slate-100 animate-fade-in pl-2">
                  <h4 className="text-sm font-bold text-foreground mb-3">Live Tracking Status</h4>
                  <div className="flex items-center text-sm">
                    <div className="flex flex-col items-center">
                      <div className={`w-6 h-6 rounded-full flex items-center justify-center text-white ${isWithdrawn ? 'bg-slate-400' : 'bg-emerald-500'}`}><CheckCircle2 className="w-4 h-4"/></div>
                      <div className={`h-6 w-0.5 my-1 ${isWithdrawn ? 'bg-slate-400' : 'bg-emerald-500'}`}></div>
                      <div className={`w-6 h-6 rounded-full flex items-center justify-center text-white ${isWithdrawn ? 'bg-slate-400' : 'bg-emerald-500'}`}><CheckCircle2 className="w-4 h-4"/></div>
                      <div className={`h-6 w-0.5 my-1 ${isWithdrawn ? 'bg-slate-400' : 'bg-slate-200'}`}></div>
                      {isWithdrawn ? (
                        <div className="w-6 h-6 rounded-full bg-slate-500 flex items-center justify-center text-white"><XCircle className="w-4 h-4"/></div>
                      ) : (
                        <div className="w-6 h-6 rounded-full bg-slate-200 border-2 border-slate-300"></div>
                      )}
                    </div>
                    <div className="ml-4 flex flex-col justify-between h-32 py-0.5 text-slate-600 font-medium">
                      <div><span className="text-slate-900">Application Submitted</span> <span className="text-xs font-normal ml-2">({new Date(app.timestamp).toLocaleString()})</span></div>
                      <div><span className="text-slate-900">Forwarded via WhatsApp</span> <span className="text-xs font-normal ml-2">Notification sent to Club Head</span></div>
                      <div>{isWithdrawn ? 'Withdrawn by Student' : 'Pending Review'}</div>
                    </div>
                  </div>

                  {!isWithdrawn && withdrawingId !== expId && (
                    <button 
                      onClick={(e) => { e.stopPropagation(); setWithdrawingId(expId); }} 
                      className="mt-4 text-xs font-semibold text-rose-600 hover:text-rose-700 bg-rose-50 px-3 py-1.5 rounded-lg border border-rose-100 inline-flex items-center gap-1 transition-colors"
                    >
                      Withdraw Request
                    </button>
                  )}

                  {withdrawingId === expId && (
                    <div className="mt-4 p-4 bg-rose-50 rounded-xl border border-rose-200 shadow-sm" onClick={(e) => e.stopPropagation()}>
                      <p className="text-sm font-bold text-rose-900 mb-2">Why are you withdrawing this application?</p>
                      <input 
                        type="text" 
                        value={withdrawReason} 
                        onChange={(e) => setWithdrawReason(e.target.value)} 
                        className="w-full text-sm p-2.5 rounded-lg border border-rose-200 mb-3 focus:outline-none focus:ring-2 focus:ring-rose-500 bg-white" 
                        placeholder="Reason for withdrawal..." 
                        autoFocus
                      />
                      <div className="flex gap-2">
                        <button 
                          onClick={() => handleWithdraw(app.id, 'club')} 
                          disabled={isSubmittingWithdraw || !withdrawReason.trim()} 
                          className="bg-rose-600 text-white text-xs font-semibold px-4 py-2 rounded-lg hover:bg-rose-700 disabled:opacity-50 transition-colors flex items-center"
                        >
                          {isSubmittingWithdraw ? <Loader2 className="w-3 h-3 animate-spin mr-1"/> : null}
                          Confirm Withdrawal
                        </button>
                        <button 
                          onClick={() => { setWithdrawingId(null); setWithdrawReason(''); }} 
                          className="text-slate-700 text-xs font-semibold px-4 py-2 rounded-lg hover:bg-slate-100 border border-slate-300 bg-white transition-colors"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  )}

                  {isWithdrawn && app.withdrawal_reason && (
                    <div className="mt-4 p-3 bg-slate-50 rounded-lg border border-slate-200 inline-block">
                      <p className="text-xs font-semibold text-slate-700">Withdrawal Reason:</p>
                      <p className="text-xs text-slate-600 italic mt-0.5">"{app.withdrawal_reason}"</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          )})}

          {/* DB Complaints */}
          {dbComplaints.map((comp) => {
            const isWithdrawn = comp.status === 'Withdrawn';
            const expId = comp.id;
            return (
            <div 
              key={expId} 
              className={`p-4 hover:bg-muted/50/60 transition-colors cursor-pointer ${isWithdrawn ? 'opacity-75' : ''}`}
              onClick={() => toggleExpand(expId)}
            >
              <div className="flex flex-col @lg:flex-row @lg:items-center justify-between gap-2">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-rose-600">{comp.id}</span>
                    <span className="rounded-md bg-muted px-2 py-0.5 text-sm font-bold text-foreground">
                      ANC Grievance
                    </span>
                    <span className="text-xs font-bold text-foreground">Confidential Report</span>
                  </div>
                  <p className="text-xs text-muted-foreground leading-relaxed">Student: {student.name} ({student.id})</p>
                  <p className="text-xs text-muted-foreground leading-relaxed italic border-l-2 border-rose-200 pl-2 mt-1">"{comp.description}"</p>
                  <div className="flex items-center gap-3 text-sm text-muted-foreground pt-0.5">
                    <span>Submitted: {new Date(comp.timestamp).toLocaleString()}</span>
                    <span>•</span>
                    <span>Department: <strong>Nodal Officer</strong></span>
                  </div>
                </div>

                <div className="flex items-center @lg:flex-col @lg:items-end gap-2 shrink-0">
                  <span className={`rounded-full px-2.5 py-0.5 text-sm font-bold border flex items-center gap-1 ${
                    isWithdrawn ? 'bg-slate-50 text-slate-500 border-slate-200' : 'bg-rose-50 text-rose-800 border-rose-200'
                  }`}>
                    {isWithdrawn ? <XCircle className="h-3 w-3" /> : <ShieldCheck className="h-3 w-3 text-rose-600" />}
                    <span>{comp.status}</span>
                  </span>
                  <span className="text-sm font-medium text-rose-500">Priority: High</span>
                </div>
              </div>
              
              {/* Expanded Status View */}
              {expandedReq === expId && (
                <div className="mt-4 pt-4 border-t border-slate-100 animate-fade-in pl-2">
                  <h4 className="text-sm font-bold text-foreground mb-3">Live Tracking Status</h4>
                  <div className="flex items-center text-sm">
                    <div className="flex flex-col items-center">
                      <div className={`w-6 h-6 rounded-full flex items-center justify-center text-white ${isWithdrawn ? 'bg-slate-400' : 'bg-emerald-500'}`}><CheckCircle2 className="w-4 h-4"/></div>
                      <div className={`h-6 w-0.5 my-1 ${isWithdrawn ? 'bg-slate-400' : 'bg-emerald-500'}`}></div>
                      <div className={`w-6 h-6 rounded-full flex items-center justify-center text-white ${isWithdrawn ? 'bg-slate-400' : 'bg-emerald-500'}`}><CheckCircle2 className="w-4 h-4"/></div>
                      <div className={`h-6 w-0.5 my-1 ${isWithdrawn ? 'bg-slate-400' : 'bg-slate-200'}`}></div>
                      {isWithdrawn ? (
                        <div className="w-6 h-6 rounded-full bg-slate-500 flex items-center justify-center text-white"><XCircle className="w-4 h-4"/></div>
                      ) : (
                        <div className="w-6 h-6 rounded-full bg-slate-200 border-2 border-slate-300"></div>
                      )}
                    </div>
                    <div className="ml-4 flex flex-col justify-between h-32 py-0.5 text-slate-600 font-medium">
                      <div><span className="text-slate-900">Incident Reported</span> <span className="text-xs font-normal ml-2">({new Date(comp.timestamp).toLocaleString()})</span></div>
                      <div><span className="text-slate-900">Received & Secured</span> <span className="text-xs font-normal ml-2">Assigned to Nodal Officer</span></div>
                      <div>{isWithdrawn ? 'Withdrawn by Student' : 'Under Investigation'}</div>
                    </div>
                  </div>

                  {!isWithdrawn && withdrawingId !== expId && (
                    <button 
                      onClick={(e) => { e.stopPropagation(); setWithdrawingId(expId); }} 
                      className="mt-4 text-xs font-semibold text-rose-600 hover:text-rose-700 bg-rose-50 px-3 py-1.5 rounded-lg border border-rose-100 inline-flex items-center gap-1 transition-colors"
                    >
                      Withdraw Request
                    </button>
                  )}

                  {withdrawingId === expId && (
                    <div className="mt-4 p-4 bg-rose-50 rounded-xl border border-rose-200 shadow-sm" onClick={(e) => e.stopPropagation()}>
                      <p className="text-sm font-bold text-rose-900 mb-2">Why are you withdrawing this grievance?</p>
                      <input 
                        type="text" 
                        value={withdrawReason} 
                        onChange={(e) => setWithdrawReason(e.target.value)} 
                        className="w-full text-sm p-2.5 rounded-lg border border-rose-200 mb-3 focus:outline-none focus:ring-2 focus:ring-rose-500 bg-white" 
                        placeholder="Reason for withdrawal..." 
                        autoFocus
                      />
                      <div className="flex gap-2">
                        <button 
                          onClick={() => handleWithdraw(comp.id, 'grievance')} 
                          disabled={isSubmittingWithdraw || !withdrawReason.trim()} 
                          className="bg-rose-600 text-white text-xs font-semibold px-4 py-2 rounded-lg hover:bg-rose-700 disabled:opacity-50 transition-colors flex items-center"
                        >
                          {isSubmittingWithdraw ? <Loader2 className="w-3 h-3 animate-spin mr-1"/> : null}
                          Confirm Withdrawal
                        </button>
                        <button 
                          onClick={() => { setWithdrawingId(null); setWithdrawReason(''); }} 
                          className="text-slate-700 text-xs font-semibold px-4 py-2 rounded-lg hover:bg-slate-100 border border-slate-300 bg-white transition-colors"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  )}

                  {isWithdrawn && comp.withdrawal_reason && (
                    <div className="mt-4 p-3 bg-slate-50 rounded-lg border border-slate-200 inline-block">
                      <p className="text-xs font-semibold text-slate-700">Withdrawal Reason:</p>
                      <p className="text-xs text-slate-600 italic mt-0.5">"{comp.withdrawal_reason}"</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          )})}

          {/* Static Mock Services */}
          {services.map((req) => (
            <div 
              key={req.id} 
              className="p-4 hover:bg-muted/50/60 transition-colors cursor-pointer"
              onClick={() => toggleExpand(req.id)}
            >
              <div className="flex flex-col @lg:flex-row @lg:items-center justify-between gap-2">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-blue-600">{req.id}</span>
                    <span className="rounded-md bg-muted px-2 py-0.5 text-sm font-bold text-foreground">
                      {req.category}
                    </span>
                    <span className="text-xs font-bold text-foreground">{req.title}</span>
                  </div>
                  <p className="text-xs text-muted-foreground leading-relaxed">{req.description}</p>
                  <div className="flex items-center gap-3 text-sm text-muted-foreground pt-0.5">
                    <span>Submitted: {req.submittedAt}</span>
                    <span>•</span>
                    <span>Department: <strong>{req.assignedDept}</strong></span>
                    <span>•</span>
                    <span className="font-mono text-blue-700">{req.trackingToken}</span>
                  </div>
                </div>

                <div className="flex items-center @lg:flex-col @lg:items-end gap-2 shrink-0">
                  <span className="rounded-full bg-emerald-50 px-2.5 py-0.5 text-sm font-bold text-emerald-800 border border-emerald-200 flex items-center gap-1">
                    <CheckCircle2 className="h-3 w-3 text-emerald-600" />
                    <span>{tDynamic(req.status)}</span>
                  </span>
                  <span className="text-sm font-medium text-slate-400">
                    {t.priority}: {tDynamic(req.priority)}
                  </span>
                </div>
              </div>
              
              {/* Expanded Status View */}
              {expandedReq === req.id && (
                <div className="mt-4 pt-4 border-t border-slate-100 animate-fade-in pl-2">
                  <h4 className="text-sm font-bold text-foreground mb-3">Tracking History</h4>
                  <div className="flex items-center text-sm">
                    <div className="flex flex-col items-center">
                      <div className="w-6 h-6 rounded-full bg-emerald-500 flex items-center justify-center text-white"><CheckCircle2 className="w-4 h-4"/></div>
                      <div className="h-6 w-0.5 bg-emerald-500 my-1"></div>
                      <div className="w-6 h-6 rounded-full bg-emerald-500 flex items-center justify-center text-white"><CheckCircle2 className="w-4 h-4"/></div>
                      <div className="h-6 w-0.5 bg-emerald-500 my-1"></div>
                      <div className="w-6 h-6 rounded-full bg-blue-500 flex items-center justify-center text-white"><Clock className="w-3 h-3"/></div>
                    </div>
                    <div className="ml-4 flex flex-col justify-between h-32 py-0.5 text-slate-600 font-medium">
                      <div><span className="text-slate-900">Request Submitted</span></div>
                      <div><span className="text-slate-900">Forwarded to Department</span></div>
                      <div><span className="text-slate-900">{tDynamic(req.status)}</span> <span className="text-xs font-normal ml-2">Expected Completion: 3 Days</span></div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
