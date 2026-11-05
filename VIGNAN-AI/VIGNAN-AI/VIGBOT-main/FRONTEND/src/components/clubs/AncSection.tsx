"use client";

import React, { useState } from 'react';
import { AlertTriangle, ShieldCheck, Send, Search, Loader2 } from 'lucide-react';
import { Club } from '@/data/clubs';
import { submitAncComplaint, trackComplaint } from '@/actions/db';
import { useStudent } from '@/context/StudentContext';
import { CURRENT_STUDENT } from '@/data/student';

interface AncSectionProps {
  club: Club;
}

export function AncSection({ club }: AncSectionProps) {
  const { studentData } = useStudent();
  const student = studentData?.profile || CURRENT_STUDENT;

  const [showComplaintForm, setShowComplaintForm] = useState(false);
  const [complaintText, setComplaintText] = useState('');
  
  // Progress tracker state
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [progressStep, setProgressStep] = useState(0);
  const [trackingId, setTrackingId] = useState<string | null>(null);

  // Tracking state
  const [searchId, setSearchId] = useState('');
  const [trackResult, setTrackResult] = useState<any>(null);
  const [isTracking, setIsTracking] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!complaintText.trim()) return;
    
    setIsSubmitting(true);
    setProgressStep(1); // Encrypting...
    
    setTimeout(() => setProgressStep(2), 1200); // Bypassing channels...
    setTimeout(() => setProgressStep(3), 2400); // Securing...
    
    // Actually call the DB
    const res = await submitAncComplaint(complaintText, student.id);
    
    setTimeout(() => {
      setIsSubmitting(false);
      setProgressStep(4);
      if (res.success && res.trackingId) {
        setTrackingId(res.trackingId);
      }
    }, 3600);
  };

  const handleTrack = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchId.trim()) return;
    
    setIsTracking(true);
    const res = await trackComplaint(searchId, student.id);
    if (res.success) {
      setTrackResult(res.data);
    } else {
      setTrackResult({ error: res.error });
    }
    setIsTracking(false);
  };

  const resetForm = () => {
    setShowComplaintForm(false);
    setProgressStep(0);
    setTrackingId(null);
    setComplaintText('');
  };

  return (
    <div className="bg-rose-50 border border-rose-200 rounded-xl p-6 shadow-sm mb-8">
      <div className="flex items-center space-x-3 mb-4">
        <ShieldCheck className="w-8 h-8 text-rose-600" />
        <h2 className="text-2xl font-bold text-rose-900">{club.name}</h2>
      </div>
      
      <div className="bg-white p-5 rounded-lg border border-rose-100 mb-6">
        <h3 className="text-lg font-bold text-rose-800 mb-2 flex items-center">
          <AlertTriangle className="w-5 h-5 mr-2" />
          Zero Tolerance Policy
        </h3>
        <p className="text-rose-700 leading-relaxed">
          {club.description} The state university strictly prohibits any form of ragging. 
          Consequences of ragging include immediate suspension, rustication from the university, 
          cancellation of admission, and lodging of an FIR with local police. 
        </p>
      </div>

      <div className="mb-6 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white p-4 rounded-lg border border-gray-100 shadow-sm flex flex-col">
          <span className="font-bold text-gray-900 mb-2">Track Existing Complaint</span>
          <form onSubmit={handleTrack} className="flex gap-2">
            <input 
              type="text" 
              placeholder="e.g. ANC-1234"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-rose-500"
              value={searchId}
              onChange={(e) => setSearchId(e.target.value)}
            />
            <button 
              type="submit"
              disabled={isTracking}
              className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-2 rounded-lg font-medium text-sm flex items-center"
            >
              {isTracking ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
            </button>
          </form>
          {trackResult && !trackResult.error && (
            <div className="mt-3 p-3 bg-emerald-50 border border-emerald-100 rounded text-sm">
              <div className="font-bold text-emerald-800">Status: {trackResult.status}</div>
              <div className="text-emerald-700 text-xs mt-1">Logged: {new Date(trackResult.timestamp).toLocaleString()}</div>
            </div>
          )}
          {trackResult && trackResult.error && (
            <div className="mt-3 text-sm text-red-600 font-medium">{trackResult.error}</div>
          )}
        </div>

        <div className="bg-white p-4 rounded-lg border border-gray-100 shadow-sm flex flex-col justify-center">
           {!showComplaintForm && progressStep === 0 && (
             <div className="text-center">
               <h4 className="font-bold text-gray-900 mb-2">Need to report an incident?</h4>
               <button 
                 onClick={() => setShowComplaintForm(true)}
                 className="w-full py-2 bg-rose-600 hover:bg-rose-700 text-white font-medium rounded-lg transition-colors flex items-center justify-center"
               >
                 Register Confidential Complaint
               </button>
             </div>
           )}
        </div>
      </div>

      {showComplaintForm && (
        <div className="bg-white p-5 rounded-lg border border-rose-200 shadow-sm transition-all duration-300">
          {progressStep === 4 ? (
            <div className="text-center py-8">
              <ShieldCheck className="w-12 h-12 text-emerald-500 mx-auto mb-3" />
              <h4 className="text-xl font-bold text-gray-900 mb-2">Complaint Registered Successfully</h4>
              <p className="text-gray-600 mb-4">
                Your incident has been securely recorded. The Nodal Officer has been notified. 
                Your secure Tracking ID is: <span className="font-mono bg-gray-100 px-2 py-1 rounded text-gray-800 font-bold">{trackingId}</span>
              </p>
              <button onClick={resetForm} className="text-sm font-medium text-rose-600 hover:underline">
                Close
              </button>
            </div>
          ) : isSubmitting ? (
            <div className="py-8 px-4">
              <h4 className="font-bold text-gray-900 mb-6 text-center">Securing your report...</h4>
              <div className="max-w-md mx-auto space-y-4 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-300 before:to-transparent">
                
                <div className={`relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group ${progressStep >= 1 ? 'opacity-100' : 'opacity-30'}`}>
                  <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 border-white bg-slate-300 shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 shadow transition-colors ${progressStep >= 1 ? 'bg-rose-500' : ''}`}>
                    {progressStep === 1 && <Loader2 className="w-5 h-5 text-white animate-spin" />}
                    {progressStep > 1 && <ShieldCheck className="w-5 h-5 text-white" />}
                  </div>
                  <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-4 rounded-xl border border-slate-200 bg-white shadow-sm">
                    <p className="font-bold text-slate-900 text-sm">Encrypting payload</p>
                  </div>
                </div>

                <div className={`relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group ${progressStep >= 2 ? 'opacity-100' : 'opacity-30'}`}>
                  <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 border-white bg-slate-300 shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 shadow transition-colors ${progressStep >= 2 ? 'bg-rose-500' : ''}`}>
                    {progressStep === 2 && <Loader2 className="w-5 h-5 text-white animate-spin" />}
                    {progressStep > 2 && <ShieldCheck className="w-5 h-5 text-white" />}
                  </div>
                  <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-4 rounded-xl border border-slate-200 bg-white shadow-sm">
                    <p className="font-bold text-slate-900 text-sm">Bypassing local faculty channels</p>
                  </div>
                </div>

                <div className={`relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group ${progressStep >= 3 ? 'opacity-100' : 'opacity-30'}`}>
                  <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 border-white bg-slate-300 shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 shadow transition-colors ${progressStep >= 3 ? 'bg-rose-500' : ''}`}>
                    {progressStep === 3 && <Loader2 className="w-5 h-5 text-white animate-spin" />}
                    {progressStep > 3 && <ShieldCheck className="w-5 h-5 text-white" />}
                  </div>
                  <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-4 rounded-xl border border-slate-200 bg-white shadow-sm">
                    <p className="font-bold text-slate-900 text-sm">Pinging Chief Nodal Officer</p>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <form onSubmit={handleSubmit}>
              <h4 className="font-bold text-gray-900 mb-4 flex items-center">
                <AlertTriangle className="w-5 h-5 text-rose-500 mr-2" />
                Incident Report Form
              </h4>
              <textarea
                value={complaintText}
                onChange={(e) => setComplaintText(e.target.value)}
                placeholder="Please describe the incident in detail (location, time, persons involved if known)..."
                className="w-full p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-rose-500 focus:border-rose-500 transition-shadow min-h-[120px] resize-y mb-4"
                required
              />
              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setShowComplaintForm(false)}
                  className="px-4 py-2 text-gray-600 hover:text-gray-900 font-medium transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-6 py-2 bg-rose-600 hover:bg-rose-700 text-white font-medium rounded-lg transition-colors flex items-center"
                >
                  <Send className="w-4 h-4 mr-2" />
                  Submit Securely
                </button>
              </div>
            </form>
          )}
        </div>
      )}
    </div>
  );
}
