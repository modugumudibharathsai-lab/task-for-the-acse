import React, { useEffect, useState } from "react";
import { Ticket, QrCode, Calendar, MapPin } from "lucide-react";
import { getEventRegistrations, registerForEvent } from "@/actions/events";
import { useStudent } from "@/context/StudentContext";
import { CURRENT_STUDENT } from "@/data/student";

export const EventRegistrationView = () => {
  const { studentData } = useStudent();
  const student = studentData?.profile || CURRENT_STUDENT;
  const [registrations, setRegistrations] = useState<any[]>([]);

  useEffect(() => {
    const fetchRegs = async () => {
      const res = await getEventRegistrations(student.id);
      if (res.success) {
        setRegistrations((res.data as any[]) || []);
      }
    };
    fetchRegs();
  }, [student.id]);

  const handleRegister = async (eventName: string) => {
    const res = await registerForEvent(student.id, eventName);
    if (res.success) {
      setRegistrations([...registrations, { id: res.id, student_id: student.id, event_name: eventName, qr_code: res.qrCode, status: 'Registered' }]);
    }
  };

  const isRegistered = (name: string) => registrations.some(r => r.event_name === name);

  const upcomingEvents = [
    { name: "Annual Tech Symposium", date: "Oct 15, 2026", location: "Main Auditorium", type: "Technical" },
    { name: "AI Ethics Workshop", date: "Oct 20, 2026", location: "AI Lab, T-105", type: "Workshop" },
    { name: "Winter Cultural Fest", date: "Dec 05, 2026", location: "Open Air Theatre", type: "Cultural" },
  ];

  return (
    <div className="space-y-6 animate-in fade-in zoom-in-95 duration-300">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Event Registrations</h2>
          <p className="text-sm text-muted-foreground">Browse upcoming events and get your digital QR tickets.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upcoming Events List */}
        <div className="space-y-4">
          <h3 className="font-semibold flex items-center gap-2">
            <Calendar className="h-5 w-5 text-blue-600" /> Upcoming Events
          </h3>
          <div className="space-y-3">
            {upcomingEvents.map((ev, i) => (
              <div key={i} className="rounded-xl border border-border bg-card p-4 shadow-sm flex flex-col sm:flex-row justify-between gap-4">
                <div>
                  <span className="text-[10px] uppercase tracking-wider font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full">{ev.type}</span>
                  <h4 className="font-bold text-foreground mt-1">{ev.name}</h4>
                  <div className="flex flex-wrap items-center gap-3 text-xs text-muted-foreground mt-2">
                    <span className="flex items-center gap-1"><Calendar className="h-3 w-3" /> {ev.date}</span>
                    <span className="flex items-center gap-1"><MapPin className="h-3 w-3" /> {ev.location}</span>
                  </div>
                </div>
                <div className="flex items-center">
                  {isRegistered(ev.name) ? (
                    <span className="text-emerald-600 font-semibold text-sm flex items-center gap-1 bg-emerald-50 px-3 py-1.5 rounded-lg border border-emerald-200">
                      <Ticket className="h-4 w-4" /> Registered
                    </span>
                  ) : (
                    <button 
                      onClick={() => handleRegister(ev.name)}
                      className="bg-blue-600 hover:bg-blue-700 text-white font-medium text-sm px-4 py-2 rounded-lg transition-colors shadow-sm"
                    >
                      Get Ticket
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* My Tickets */}
        <div className="space-y-4">
          <h3 className="font-semibold flex items-center gap-2">
            <QrCode className="h-5 w-5 text-indigo-600" /> My Tickets
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {registrations.length > 0 ? (
              registrations.map(r => (
                <div key={r.id} className="rounded-xl border border-border bg-card shadow-sm overflow-hidden flex flex-col">
                  <div className="bg-indigo-600 text-white p-3 text-center">
                    <span className="text-[10px] uppercase tracking-widest font-bold opacity-80">Admit One</span>
                    <h4 className="font-bold text-sm line-clamp-1">{r.event_name}</h4>
                  </div>
                  <div className="p-4 flex-1 flex flex-col items-center justify-center space-y-3 bg-[url('https://www.transparenttextures.com/patterns/cream-pixels.png')]">
                    <div className="bg-white p-2 rounded-lg shadow-xs border border-slate-200">
                       <QrCode className="h-20 w-20 text-slate-800" />
                    </div>
                    <span className="text-xs font-mono text-slate-500">{r.qr_code}</span>
                  </div>
                </div>
              ))
            ) : (
              <div className="col-span-full rounded-xl border border-dashed border-border bg-muted/30 p-8 text-center">
                <Ticket className="h-8 w-8 text-muted-foreground mx-auto mb-2 opacity-50" />
                <p className="text-sm font-medium text-slate-600">No active tickets</p>
                <p className="text-xs text-muted-foreground mt-1">Register for an event to get your QR pass.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
