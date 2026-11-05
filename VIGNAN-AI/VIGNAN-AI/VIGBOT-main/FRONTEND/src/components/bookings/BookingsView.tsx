"use client";

import { getBackendUrl } from "@/lib/backend-url";


import { useState, useEffect } from "react";
import { Facility, getFacilities } from "@/actions/bookings";
import { Search, MapPin, Users, Activity, Filter, CalendarPlus } from "lucide-react";
import { BookingModal } from "./BookingModal";
import Image from "next/image";

const FACILITY_TYPES = ["All", "Sports", "Academic", "Tech", "Event"];

export function BookingsView() {
  const [facilities, setFacilities] = useState<Facility[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [activeType, setActiveType] = useState("All");
  const [selectedFacility, setSelectedFacility] = useState<Facility | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadFacilities = async () => {
      setLoading(true);
      let loaded = false;
      try {
        const data = await getFacilities();
        if (Array.isArray(data) && data.length > 0) {
          setFacilities(data);
          loaded = true;
        }
      } catch (e) {
        console.warn("Action getFacilities failed:", e);
      }

      if (!loaded) {
        try {
          const backendUrl = getBackendUrl();
          const res = await fetch(`${backendUrl}/community/facilities`);
          if (res.ok) {
            const json = await res.json();
            if (json?.success && Array.isArray(json?.facilities) && json.facilities.length > 0) {
              setFacilities(json.facilities);
              loaded = true;
            }
          }
        } catch (e) {
          console.warn("Direct fetch facilities failed:", e);
        }
      }
      setLoading(false);
    };

    loadFacilities();
  }, []);

  const filteredFacilities = facilities.filter(facility => {
    const matchesSearch = facility.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
                          facility.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = activeType === "All" || facility.type === activeType;
    return matchesSearch && matchesType;
  });

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      
      {/* Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-end justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-800">Facility & Resource Booking</h1>
          <p className="text-sm text-slate-500 mt-1">Book campus resources like study rooms, courts, and labs.</p>
        </div>
      </div>

      {/* Controls: Search and Filters */}
      <div className="flex flex-col md:flex-row gap-4 justify-between items-start md:items-center">
        {/* Pills */}
        <div className="flex items-center gap-2 overflow-x-auto pb-2 md:pb-0 hide-scrollbar w-full md:w-auto">
          {FACILITY_TYPES.map(type => (
            <button
              key={type}
              onClick={() => setActiveType(type)}
              className={`whitespace-nowrap px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${
                activeType === type 
                ? "bg-slate-800 text-white shadow-sm" 
                : "bg-white text-slate-600 hover:bg-slate-100 border border-slate-200"
              }`}
            >
              {type}
            </button>
          ))}
        </div>

        {/* Search */}
        <div className="relative w-full md:w-64 flex-shrink-0">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search className="w-4 h-4 text-slate-400" />
          </div>
          <input
            type="text"
            placeholder="Search facilities..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50 bg-white"
          />
        </div>
      </div>

      {/* Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map(i => (
            <div key={i} className="bg-white rounded-2xl h-80 animate-pulse border border-slate-100 shadow-sm"></div>
          ))}
        </div>
      ) : filteredFacilities.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredFacilities.map(facility => (
            <div key={facility.id} className="bg-white rounded-2xl overflow-hidden border border-slate-200 shadow-sm hover:shadow-md transition-shadow group flex flex-col">
              <div className="h-48 bg-slate-100 relative overflow-hidden">
                {facility.image_url ? (
                  <img src={facility.image_url} alt={facility.name} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-slate-400">
                    <MapPin className="w-8 h-8" />
                  </div>
                )}
                <div className="absolute top-3 left-3">
                  <span className="px-2.5 py-1 text-xs font-semibold rounded-md shadow-sm bg-white/90 text-slate-800 backdrop-blur-sm">
                    {facility.type}
                  </span>
                </div>
              </div>
              <div className="p-5 flex-1 flex flex-col">
                <h3 className="text-lg font-semibold text-slate-800 line-clamp-1">{facility.name}</h3>
                <p className="text-sm text-slate-500 mt-1 line-clamp-2 flex-1">{facility.description}</p>
                
                <div className="mt-4 flex items-center gap-4 text-sm text-slate-600">
                  <div className="flex items-center gap-1.5">
                    <Users className="w-4 h-4 text-slate-400" />
                    <span>Up to {facility.capacity}</span>
                  </div>
                </div>

                <button 
                  onClick={() => setSelectedFacility(facility)}
                  className="mt-5 w-full bg-slate-50 hover:bg-blue-50 text-blue-600 font-medium py-2 rounded-lg transition-colors border border-slate-200 hover:border-blue-200 flex items-center justify-center gap-2"
                >
                  <CalendarPlus className="w-4 h-4" />
                  Book Slot
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center shadow-sm">
          <Activity className="w-12 h-12 text-slate-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-slate-800">No facilities found</h3>
          <p className="text-slate-500 mt-1 max-w-sm mx-auto">We couldn't find any facilities matching your current filters.</p>
          <button 
            onClick={() => {setSearchQuery(""); setActiveType("All");}}
            className="mt-6 px-4 py-2 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 transition-colors text-sm font-medium"
          >
            Clear Filters
          </button>
        </div>
      )}

      {/* Modal */}
      {selectedFacility && (
        <BookingModal 
          facility={selectedFacility} 
          isOpen={true} 
          onClose={() => setSelectedFacility(null)} 
        />
      )}
    </div>
  );
}
