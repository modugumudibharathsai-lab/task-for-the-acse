"use client";

import { useState, useEffect } from "react";
import { Bus, MapPin, Clock } from "lucide-react";
import { getTransportRoutes } from "@/actions/transport";
import { getBackendUrl } from "@/lib/backend-url";
import { HostelBusTimetable } from "./HostelBusTimetable";

const FALLBACK_ROUTES = [
  { id: 1, route_name: "Route A - Campus Link", driver_name: "Ramesh Kumar", current_location: "Near Guntur Bus Stand", eta_minutes: 15 },
  { id: 2, route_name: "Route B - Tenali Express", driver_name: "Suresh Babu", current_location: "Tenali Flyover", eta_minutes: 25 },
  { id: 3, route_name: "Route C - Vijayawada Metro Connect", driver_name: "Venkatesh Rao", current_location: "Benz Circle", eta_minutes: 40 },
  { id: 4, route_name: "Route D - Hostel Shuttle", driver_name: "Krishna Reddy", current_location: "Boys Hostel Block C", eta_minutes: 5 }
];

export function TransportView() {
  const [routes, setRoutes] = useState<any[]>(FALLBACK_ROUTES);
  const [activeTab, setActiveTab] = useState<"live" | "timetable">("live");

  useEffect(() => {
    const loadRoutes = async () => {
      let loaded = false;
      try {
        const data = await getTransportRoutes();
        if (Array.isArray(data) && data.length > 0) {
          setRoutes(data);
          loaded = true;
        }
      } catch (e) {
        console.warn("Server action failed, trying direct API:", e);
      }

      if (!loaded) {
        try {
          const backendUrl = getBackendUrl();
          const res = await fetch(`${backendUrl}/community/transport`);
          if (res.ok) {
            const json = await res.json();
            if (json?.success && Array.isArray(json?.routes) && json.routes.length > 0) {
              setRoutes(json.routes);
              loaded = true;
            }
          }
        } catch (e) {
          console.warn("Direct fetch error:", e);
        }
      }
    };

    loadRoutes();
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Smart Transportation</h2>
        <p className="text-muted-foreground">Live university bus tracking and ETAs.</p>
      </div>

      <div className="inline-flex w-fit items-center justify-center rounded-lg bg-muted p-[3px] text-muted-foreground">
        <button
          type="button"
          onClick={() => setActiveTab("live")}
          className={`relative inline-flex h-8 items-center justify-center gap-1.5 rounded-md px-3 text-sm font-medium transition-all ${
            activeTab === "live"
              ? "bg-background text-foreground shadow-sm font-semibold"
              : "hover:text-foreground text-foreground/60"
          }`}
        >
          <Bus className="h-4 w-4" />
          Live Tracking
        </button>
        <button
          type="button"
          onClick={() => setActiveTab("timetable")}
          className={`relative inline-flex h-8 items-center justify-center gap-1.5 rounded-md px-3 text-sm font-medium transition-all ${
            activeTab === "timetable"
              ? "bg-background text-foreground shadow-sm font-semibold"
              : "hover:text-foreground text-foreground/60"
          }`}
        >
          <Clock className="h-4 w-4" />
          Hostel Timetable
        </button>
      </div>

      {activeTab === "live" && (
        <div className="grid gap-4 md:grid-cols-2">
          {routes.map((route) => (
            <div key={route.id} className="rounded-xl border bg-card text-card-foreground shadow-sm p-5 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-full bg-emerald-100 flex items-center justify-center">
                    <Bus className="h-5 w-5 text-emerald-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold">{route.route_name}</h3>
                    <p className="text-xs text-muted-foreground">Driver: {route.driver_name}</p>
                  </div>
                </div>
                <div className="text-right">
                  <div className="flex items-center justify-end gap-1 text-emerald-600 font-bold">
                    <Clock className="h-4 w-4" />
                    <span>{route.eta_minutes} min</span>
                  </div>
                  <p className="text-xs text-muted-foreground">ETA to campus</p>
                </div>
              </div>
              <div className="flex items-center gap-2 text-sm bg-muted/50 p-2 rounded-lg">
                <MapPin className="h-4 w-4 text-muted-foreground" />
                <span>Currently at: <span className="font-medium">{route.current_location}</span></span>
              </div>
            </div>
          ))}
        </div>
      )}

      {activeTab === "timetable" && (
        <HostelBusTimetable />
      )}
    </div>
  );
}
