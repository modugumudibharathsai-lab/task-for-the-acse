"use client";

import { useState, useEffect } from "react";
import { HeartPulse, Headphones, BookOpen, CalendarHeart } from "lucide-react";
import { getWellnessResources } from "@/actions/wellness";

export function WellnessView() {
  const [resources, setResources] = useState<any[]>([]);

  useEffect(() => {
    getWellnessResources().then(setResources);
  }, []);

  const getIcon = (category: string) => {
    switch (category) {
      case "Audio": return <Headphones className="h-6 w-6 text-indigo-500" />;
      case "Reading": return <BookOpen className="h-6 w-6 text-emerald-500" />;
      case "Action": return <CalendarHeart className="h-6 w-6 text-rose-500" />;
      default: return <HeartPulse className="h-6 w-6 text-slate-500" />;
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Wellness & Mental Health</h2>
        <p className="text-muted-foreground">Resources to help you stay balanced and healthy.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {resources.map((resource) => (
          <div key={resource.id} className="rounded-xl border bg-card text-card-foreground shadow-sm p-6 hover:shadow-md transition-shadow cursor-pointer flex flex-col h-full">
            <div className="h-12 w-12 rounded-full bg-slate-50 flex items-center justify-center mb-4">
              {getIcon(resource.category)}
            </div>
            <h3 className="font-semibold text-lg mb-2">{resource.title}</h3>
            <p className="text-sm text-muted-foreground flex-grow">{resource.description}</p>
            <div className="mt-4 pt-4 border-t">
              <span className="text-xs font-medium uppercase tracking-wider text-muted-foreground">{resource.category}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
