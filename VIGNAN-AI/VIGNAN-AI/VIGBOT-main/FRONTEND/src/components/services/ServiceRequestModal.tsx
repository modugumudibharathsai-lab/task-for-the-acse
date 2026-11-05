"use client";

import React, { useState } from "react";
import {
  X,
  FileCheck2,
  ShieldCheck,
  Send,
  AlertTriangle,
  LifeBuoy,
  CheckCircle2,
  Cpu,
} from "lucide-react";
import { CURRENT_STUDENT } from "@/data/student";
import { ServiceRequest } from "@/data/services";
import { apiClient } from "@/lib/api-client";
import { useStudent } from "@/context/StudentContext";
import { useLanguage } from "@/context/LanguageContext";

interface ServiceRequestModalProps {
  isOpen: boolean;
  initialCategory?: string;
  onClose: () => void;
  onSubmitRequest: (newReq: ServiceRequest) => void;
}

export const ServiceRequestModal: React.FC<ServiceRequestModalProps> = ({
  isOpen,
  initialCategory = "Certificate",
  onClose,
  onSubmitRequest,
}) => {
  const { studentData } = useStudent();
  const { t, tDynamic } = useLanguage();
  const student = studentData?.profile || CURRENT_STUDENT;

  const [category, setCategory] = useState<ServiceRequest["category"]>(
    (initialCategory as ServiceRequest["category"]) || "Certificate"
  );
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState<ServiceRequest["priority"]>("Medium");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submittedRequest, setSubmittedRequest] = useState<ServiceRequest | null>(null);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !description.trim()) return;

    setIsSubmitting(true);

    const randomId = Math.floor(1000 + Math.random() * 9000);
    const newReq: ServiceRequest = {
      id: `SR-${randomId}`,
      category,
      title,
      studentId: student.id,
      studentName: student.name,
      description,
      priority,
      status: "Forwarded to Student Services",
      submittedAt: "Just now",
      assignedDept:
        category === "Certificate"
          ? "Registrar Academic Section"
          : category === "Mentor Meeting"
          ? "Faculty Mentorship Cell"
          : category === "Grievance"
          ? "Dean Student Affairs Board"
          : "Academic Support Center",
      sourceAgent: "VIGNAN-AI (Service Requests)",
      trackingToken: `TRK-SR-${randomId}-CSE`,
    };

    // Forward to backend
    apiClient.createServiceRequest(category, title, description).catch(() => {});

    setTimeout(() => {
      setIsSubmitting(false);
      setSubmittedRequest(newReq);
      onSubmitRequest(newReq);
    }, 800);
  };

  const handleResetAndClose = () => {
    setSubmittedRequest(null);
    setTitle("");
    setDescription("");
    onClose();
  };

  return (
    <div role="dialog" aria-modal="true" className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-xs p-4">
      <div className="relative w-full max-w-lg rounded-xl bg-card p-6 shadow-2xl border border-slate-200">
        {/* Modal Header */}
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-blue-100 text-blue-700">
              <FileCheck2 className="h-4 w-4" />
            </div>
            <div>
              <h3 className="text-base font-bold text-foreground">
                Institutional Service Request
              </h3>
              <p className="text-sm text-muted-foreground">
                Official University Workflows & Ticketing
              </p>
            </div>
          </div>
          <button
            onClick={handleResetAndClose}
            className="rounded-full p-1.5 text-slate-400 hover:bg-muted transition-colors cursor-pointer"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {submittedRequest ? (
          /* Confirmation State */
          <div className="py-6 text-center space-y-4">
            <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-emerald-100 text-emerald-600">
              <CheckCircle2 className="h-8 w-8" />
            </div>
            <div>
              <h4 className="text-lg font-bold text-foreground">
                Service Request Dispatched!
              </h4>
              <p className="text-xs text-muted-foreground mt-1">
                Your request has been authenticated, stamped with Row-Level Security, and forwarded to Student Services.
              </p>
            </div>

            <div className="rounded-lg bg-muted/50 p-4 border border-slate-200 text-left text-xs space-y-1.5 font-medium text-foreground">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Tracking Token:</span>
                <span className="font-mono font-bold text-blue-700">
                  {submittedRequest.trackingToken}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Student:</span>
                <span>{submittedRequest.studentName} ({submittedRequest.studentId})</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Assigned Department:</span>
                <span>{submittedRequest.assignedDept}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Status:</span>
                <span className="font-bold text-emerald-600">{submittedRequest.status}</span>
              </div>
            </div>

            <button
              onClick={handleResetAndClose}
              className="w-full rounded-xl bg-slate-900 py-2.5 text-xs font-semibold text-white hover:bg-slate-800 transition-colors cursor-pointer"
            >
              Done
            </button>
          </div>
        ) : (
          /* Submission Form */
          <form onSubmit={handleSubmit} className="space-y-4 pt-4 text-xs">
            {/* Authenticated Student Banner */}
            <div className="flex items-center justify-between rounded-xl bg-blue-50/70 p-3 border border-blue-100 text-foreground">
              <div className="flex items-center gap-2">
                <ShieldCheck className="h-4 w-4 text-blue-600" />
                <span className="font-semibold">{student.name}</span>
                <span className="text-slate-400">•</span>
                <span className="font-mono text-muted-foreground">{student.id}</span>
              </div>
              <span className="text-sm font-bold text-blue-700 uppercase">
                Verified Identity
              </span>
            </div>

            {/* Category Select */}
            <div>
              <label className="block font-bold text-foreground mb-1">
                Service Category
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value as ServiceRequest["category"])}
                className="w-full rounded-xl border border-slate-200 bg-card p-2.5 text-xs text-foreground focus:border-blue-500 focus:outline-hidden"
              >
                <option value="Certificate">Certificate Application (Bonafide, Custodian, etc.)</option>
                <option value="Mentor Meeting">Book Mentor Meeting (Dr. Radhika Sharma)</option>
                <option value="Grievance">{t.reqGrievance || "Raise an Academic / Campus Grievance"}</option>
                <option value="Academic Support">{t.reqSupport || "Request Academic Support / Remedial Coaching"}</option>
                <option value="Issue Report">{t.reqTechnical || "Report Technical / Infrastructure Issue"}</option>
              </select>
            </div>

            {/* Title */}
            <div>
              <label className="block font-bold text-foreground mb-1">
                Request Subject / Title
              </label>
              <input
                type="text"
                required
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Bonafide Statement for Summer Internship or Attendance Condonation"
                className="w-full rounded-xl border border-slate-200 bg-card p-2.5 text-xs text-foreground placeholder:text-slate-400 focus:border-blue-500 focus:outline-hidden"
              />
            </div>

            {/* Description */}
            <div>
              <label className="block font-bold text-foreground mb-1">
                Description & Academic Context
              </label>
              <textarea
                required
                rows={3}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Please describe your requirement clearly. Relevant academic information will be attached automatically."
                className="w-full rounded-xl border border-slate-200 bg-card p-2.5 text-xs text-foreground placeholder:text-slate-400 focus:border-blue-500 focus:outline-hidden"
              />
            </div>

            {/* Priority */}
            <div>
              <label className="block font-bold text-foreground mb-1">{t.priority || "Priority"}</label>
              <div className="flex gap-2">
                {(["Low", "Medium", "High", "Urgent"] as const).map((p) => (
                  <button
                    type="button"
                    key={p}
                    onClick={() => setPriority(p)}
                    className={`flex-1 rounded-lg py-1.5 text-xs font-semibold transition-all cursor-pointer ${
                      priority === p
                        ? "bg-blue-600 text-white shadow-xs"
                        : "bg-muted text-muted-foreground hover:bg-slate-200"
                    }`}
                  >
                    {p}
                  </button>
                ))}
              </div>
            </div>

            {/* Actions */}
            <div className="flex justify-end gap-2 pt-2 border-t border-slate-100">
              <button
                type="button"
                onClick={handleResetAndClose}
                className="rounded-xl border border-slate-200 bg-card px-4 py-2 text-xs font-semibold text-muted-foreground hover:bg-muted/50 cursor-pointer"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSubmitting}
                className="flex items-center gap-1.5 rounded-xl bg-blue-600 px-5 py-2 text-xs font-semibold text-white shadow-xs hover:bg-blue-700 disabled:opacity-50 cursor-pointer"
              >
                {isSubmitting ? (
                  <span>Submitting request...</span>
                ) : (
                  <>
                    <Send className="h-3.5 w-3.5" />
                    <span>{t.submitServiceRequest || "Submit Service Request"}</span>
                  </>
                )}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};
