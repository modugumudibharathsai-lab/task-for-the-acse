"use client";

import { useState, useEffect } from "react";
import { Users, Briefcase, Building, MessageCircle } from "lucide-react";
import { getAlumniMentors } from "@/actions/alumni";

export function AlumniView() {
  const [mentors, setMentors] = useState<any[]>([]);

  useEffect(() => {
    getAlumniMentors().then(setMentors);
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Alumni Mentorship Network</h2>
        <p className="text-muted-foreground">Connect with graduates for career guidance.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {mentors.map((mentor) => (
          <div key={mentor.id} className="rounded-xl border bg-card text-card-foreground shadow-sm p-6 flex flex-col items-center text-center space-y-4">
            <div className="h-16 w-16 rounded-full bg-slate-100 flex items-center justify-center">
              <Users className="h-8 w-8 text-slate-400" />
            </div>
            <div>
              <h3 className="font-semibold text-lg">{mentor.name}</h3>
              <div className="flex items-center justify-center gap-1 text-sm text-muted-foreground mt-1">
                <Briefcase className="h-4 w-4" />
                <span>{mentor.role}</span>
              </div>
              <div className="flex items-center justify-center gap-1 text-sm text-muted-foreground">
                <Building className="h-4 w-4" />
                <span>{mentor.company}</span>
              </div>
            </div>
            <button 
              disabled={!mentor.available_for_chat}
              className={`w-full flex items-center justify-center gap-2 py-2 rounded-lg text-sm font-medium transition-colors ${
                mentor.available_for_chat 
                ? "bg-primary text-primary-foreground hover:bg-primary/90" 
                : "bg-muted text-muted-foreground cursor-not-allowed"
              }`}
            >
              <MessageCircle className="h-4 w-4" />
              {mentor.available_for_chat ? "Request Chat" : "Currently Unavailable"}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
