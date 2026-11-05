import React, { useEffect, useState } from "react";
import { BedDouble, Wrench, Utensils, CheckCircle2 } from "lucide-react";
import { getHostelRequests, createHostelRequest } from "@/actions/hostel";
import { useStudent } from "@/context/StudentContext";
import { CURRENT_STUDENT } from "@/data/student";

export const HostelManagementView = () => {
  const { studentData } = useStudent();
  const student = studentData?.profile || CURRENT_STUDENT;
  const [requests, setRequests] = useState<any[]>([]);
  const [newType, setNewType] = useState("Maintenance");
  const [newDetails, setNewDetails] = useState("");

  useEffect(() => {
    fetchReqs();
  }, [student.id]);

  const fetchReqs = async () => {
    const res = await getHostelRequests(student.id);
    if (res.success) {
      setRequests((res.data as any[]) || []);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newDetails.trim()) return;
    const res = await createHostelRequest(student.id, newType, newDetails);
    if (res.success) {
      setNewDetails("");
      fetchReqs();
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in zoom-in-95 duration-300">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Hostel & Mess Services</h2>
          <p className="text-sm text-muted-foreground">Manage your stay, request maintenance, and view the mess menu.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Actions / Forms */}
        <div className="lg:col-span-1 space-y-6">
          <div className="rounded-xl border border-border bg-card p-5 shadow-sm">
            <h3 className="font-semibold flex items-center gap-2 mb-4">
              <BedDouble className="h-5 w-5 text-blue-600" /> New Request
            </h3>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Request Type</label>
                <select 
                  value={newType} 
                  onChange={(e) => setNewType(e.target.value)}
                  className="w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="Maintenance">Room Maintenance</option>
                  <option value="GatePass">Weekend Gate Pass</option>
                  <option value="Cleaning">Room Cleaning</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Details</label>
                <textarea 
                  value={newDetails}
                  onChange={(e) => setNewDetails(e.target.value)}
                  rows={3}
                  placeholder="E.g., Fan regulator is broken in Room 204..."
                  className="w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                />
              </div>
              <button 
                type="submit" 
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium text-sm px-4 py-2 rounded-lg transition-colors shadow-sm"
              >
                Submit Request
              </button>
            </form>
          </div>

          <div className="rounded-xl border border-border bg-card p-5 shadow-sm">
             <h3 className="font-semibold flex items-center gap-2 mb-4">
              <Utensils className="h-5 w-5 text-orange-500" /> Today's Mess Menu
            </h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between pb-2 border-b border-border">
                <span className="font-medium">Breakfast (7:30 AM)</span>
                <span className="text-muted-foreground">Idli, Vada, Chutney</span>
              </div>
              <div className="flex justify-between pb-2 border-b border-border">
                <span className="font-medium">Lunch (12:30 PM)</span>
                <span className="text-muted-foreground">Rice, Dal, Paneer Curry</span>
              </div>
              <div className="flex justify-between">
                <span className="font-medium">Dinner (7:30 PM)</span>
                <span className="text-muted-foreground">Chapati, Veg Korma</span>
              </div>
            </div>
          </div>
        </div>

        {/* Requests List */}
        <div className="lg:col-span-2 rounded-xl border border-border bg-card shadow-sm flex flex-col h-[500px]">
          <div className="bg-muted/30 border-b border-border p-4 flex items-center gap-2">
            <Wrench className="h-5 w-5 text-slate-600" />
            <h3 className="font-semibold text-sm">My Requests History</h3>
          </div>
          <div className="flex-1 overflow-y-auto p-4 space-y-3 scrollbar-thin bg-slate-50/50">
            {requests.length > 0 ? (
              requests.map((r) => (
                <div key={r.id} className="p-4 rounded-xl border border-border bg-white shadow-xs flex justify-between items-start gap-4">
                  <div className="space-y-1 flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold uppercase tracking-wider text-slate-500">{r.type}</span>
                      <span className="text-xs text-muted-foreground">
                        • {new Date(r.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    <p className="text-sm text-foreground">{r.details}</p>
                  </div>
                  <div>
                    {r.status === 'Open' || r.status === 'Pending' ? (
                      <span className="inline-flex items-center rounded-full bg-amber-50 px-2.5 py-0.5 text-xs font-semibold text-amber-700 border border-amber-200">
                        {r.status}
                      </span>
                    ) : (
                      <span className="inline-flex items-center rounded-full bg-emerald-50 px-2.5 py-0.5 text-xs font-semibold text-emerald-700 border border-emerald-200 gap-1">
                        <CheckCircle2 className="h-3 w-3" /> {r.status}
                      </span>
                    )}
                  </div>
                </div>
              ))
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-muted-foreground">
                 <CheckCircle2 className="h-10 w-10 text-emerald-200 mb-2" />
                 <p>No active requests. Everything looks good!</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
