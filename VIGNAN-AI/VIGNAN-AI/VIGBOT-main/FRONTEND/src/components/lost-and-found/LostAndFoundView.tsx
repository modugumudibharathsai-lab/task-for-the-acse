"use client";

import { getBackendUrl } from "@/lib/backend-url";


import React, { useState, useEffect } from "react";
import { Search, MapPin, Tag, Plus, CheckCircle2, User, Loader2, AlertTriangle, AlertCircle } from "lucide-react";
import { fetchLostAndFoundItems, claimLostAndFoundItem, reportLostAndFoundItem } from "@/actions/lostAndFound";
import { useStudent } from "@/context/StudentContext";
import { ReportItemModal } from "./ReportItemModal";
import { formatDistanceToNow } from "date-fns";

interface LostAndFoundItem {
  id: number;
  student_id: string;
  type: 'lost' | 'found';
  title: string;
  description: string;
  tags: string;
  contact_info: string;
  status: string;
  date_posted: string;
  image_url: string;
}

export const LostAndFoundView = () => {
  const { studentData } = useStudent();
  const student = studentData?.profile;
  
  const [items, setItems] = useState<LostAndFoundItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterType, setFilterType] = useState<'all' | 'lost' | 'found'>('all');
  const [searchQuery, setSearchQuery] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [actionLoading, setActionLoading] = useState<number | null>(null); // item ID being claimed

  const loadItems = async () => {
    setLoading(true);
    let loaded = false;
    try {
      const res = await fetchLostAndFoundItems(filterType);
      if (res?.success && Array.isArray(res?.items) && res.items.length > 0) {
        setItems(res.items as LostAndFoundItem[]);
        loaded = true;
      }
    } catch (e) {
      console.warn("Server action fetch failed:", e);
    }

    if (!loaded) {
      try {
        const backendUrl = getBackendUrl();
        const res = await fetch(`${backendUrl}/community/lost-and-found?filter_type=${filterType}`);
        if (res.ok) {
          const data = await res.json();
          if (data?.success && Array.isArray(data?.items)) {
            setItems(data.items as LostAndFoundItem[]);
            loaded = true;
          }
        }
      } catch (e) {
        console.warn("Direct fetch error:", e);
      }
    }
    setLoading(false);
  };

  useEffect(() => {
    loadItems();
  }, [filterType]);

  const handleClaim = async (id: number) => {
    const studentId = student?.id || "251FA04E13";
    setActionLoading(id);
    let claimed = false;
    try {
      const res = await claimLostAndFoundItem(id, studentId);
      if (res?.success) claimed = true;
    } catch (e) {
      console.warn("Action claim failed, trying direct API:", e);
    }

    if (!claimed) {
      try {
        const backendUrl = getBackendUrl();
        const res = await fetch(`${backendUrl}/community/lost-and-found/${id}/claim`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ student_id: studentId })
        });
        if (res.ok) {
          const json = await res.json();
          if (json?.success) claimed = true;
        }
      } catch (e) {
        console.error("Direct claim error:", e);
      }
    }

    if (claimed) {
      setItems((prev) => prev.filter(item => item.id !== id));
      alert("Item claimed! A notification has been sent to the reporter.");
    }
    setActionLoading(null);
  };

  const handleReportItem = async (data: any) => {
    const studentId = student?.id || "251FA04E13";
    let reported = false;
    try {
      const res = await reportLostAndFoundItem(studentId, data.type, data.title, data.description, data.tags, data.contactInfo, data.imageUrl);
      if (res?.success) {
        reported = true;
      }
    } catch (e) {
      console.warn("Server action report failed:", e);
    }

    if (!reported) {
      try {
        const backendUrl = getBackendUrl();
        const res = await fetch(`${backendUrl}/community/lost-and-found`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            student_id: studentId,
            type: data.type,
            title: data.title,
            description: data.description,
            tags: data.tags || "",
            contact_info: data.contactInfo,
            image_url: data.imageUrl || null
          })
        });
        if (res.ok) {
          const resData = await res.json();
          if (resData?.success) reported = true;
        }
      } catch (e) {
        console.error("Direct report error:", e);
      }
    }

    if (reported) {
      alert("Item reported successfully!");
      setIsModalOpen(false);
      loadItems();
    } else {
      alert("Failed to report item.");
    }
  };

  const filteredItems = items.filter(item => 
    item.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
    item.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.tags?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="@container space-y-6 animate-in fade-in duration-500">
      {/* Header */}
      <div className="flex flex-col @2xl:flex-row @2xl:items-center justify-between gap-4 border-b border-slate-200/80 pb-4">
        <div>
          <h2 className="text-xl font-bold text-foreground">Lost & Found Community Board</h2>
          <p className="text-xs text-muted-foreground mt-1">
            Help your fellow students by reporting found items or posting what you've lost.
          </p>
        </div>
        
        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 text-xs font-bold text-white shadow-xs hover:bg-blue-700 transition-colors cursor-pointer"
        >
          <Plus className="h-4 w-4" />
          Report an Item
        </button>
      </div>

      {/* Filters and Search */}
      <div className="flex flex-col sm:flex-row gap-4 justify-between">
        <div className="flex gap-2 p-1 bg-slate-200/50 rounded-xl overflow-x-auto">
          {(['all', 'lost', 'found'] as const).map((type) => (
            <button
              key={type}
              onClick={() => setFilterType(type)}
              className={`px-4 py-1.5 rounded-lg text-xs font-bold capitalize whitespace-nowrap transition-all ${
                filterType === type 
                  ? "bg-white text-slate-800 shadow-sm" 
                  : "text-slate-500 hover:text-slate-700 hover:bg-slate-200"
              }`}
            >
              {type === 'all' ? 'All Items' : (type === 'lost' ? 'Lost Items' : 'Found Items')}
            </button>
          ))}
        </div>

        <div className="relative max-w-sm w-full">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search items, tags..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full rounded-xl border border-slate-200 bg-white py-2 pl-9 pr-4 text-xs outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all"
          />
        </div>
      </div>

      {/* Grid */}
      {loading ? (
        <div className="flex justify-center items-center h-64">
           <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
        </div>
      ) : filteredItems.length === 0 ? (
        <div className="flex flex-col items-center justify-center p-12 text-center rounded-2xl border border-dashed border-slate-300 bg-slate-50">
          <AlertCircle className="h-10 w-10 text-slate-400 mb-3" />
          <h3 className="font-bold text-slate-700">No items found</h3>
          <p className="text-sm text-slate-500 mt-1 max-w-xs">Try adjusting your filters or search query, or be the first to report an item.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredItems.map(item => (
            <div key={item.id} className="group relative flex flex-col overflow-hidden rounded-2xl bg-white border border-slate-200 shadow-sm hover:shadow-md hover:border-slate-300 transition-all">
              
              {/* Type Badge */}
              <div className="absolute top-3 left-3 z-10">
                <span className={`px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider rounded-full backdrop-blur-md shadow-sm ${
                  item.type === 'lost' 
                    ? 'bg-rose-500/90 text-white' 
                    : 'bg-emerald-500/90 text-white'
                }`}>
                  {item.type}
                </span>
              </div>

              {/* Image */}
              {item.image_url && (
                <div className="relative h-48 w-full bg-slate-100 overflow-hidden">
                  <img src={item.image_url} alt={item.title} className="object-cover w-full h-full group-hover:scale-105 transition-transform duration-500" />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-80" />
                  <div className="absolute bottom-3 left-3 right-3 text-white">
                    <h3 className="font-bold text-sm truncate">{item.title}</h3>
                    <p className="text-[10px] opacity-90 mt-0.5">
                      Posted {formatDistanceToNow(new Date(item.date_posted), { addSuffix: true })}
                    </p>
                  </div>
                </div>
              )}

              {/* Content */}
              <div className={`flex flex-col flex-1 p-4 ${!item.image_url ? 'pt-10' : ''}`}>
                {!item.image_url && (
                  <div className="mb-3">
                    <h3 className="font-bold text-sm text-slate-800 line-clamp-1">{item.title}</h3>
                    <p className="text-[10px] text-slate-500 mt-0.5">
                      Posted {formatDistanceToNow(new Date(item.date_posted), { addSuffix: true })}
                    </p>
                  </div>
                )}
                <p className="text-xs text-slate-600 line-clamp-2 mb-3">
                  {item.description}
                </p>

                <div className="flex flex-wrap gap-1 mb-4">
                  {item.tags?.split(',').map((tag, idx) => (
                    <span key={idx} className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-slate-100 text-slate-500 text-[10px] font-medium border border-slate-200">
                      <Tag className="h-3 w-3" />
                      {tag.trim()}
                    </span>
                  ))}
                </div>

                <div className="mt-auto space-y-3 pt-3 border-t border-slate-100">
                  <div className="flex items-center gap-2 text-xs text-slate-500">
                    <User className="h-3.5 w-3.5" />
                    <span className="truncate">{item.contact_info}</span>
                  </div>
                  
                  <button
                    onClick={() => handleClaim(item.id)}
                    disabled={actionLoading === item.id || item.student_id === student?.id}
                    className={`w-full flex items-center justify-center gap-2 py-2 rounded-xl text-xs font-bold transition-colors ${
                      item.student_id === student?.id
                        ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
                        : 'bg-slate-900 text-white hover:bg-slate-800'
                    }`}
                  >
                    {actionLoading === item.id ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : item.student_id === student?.id ? (
                      "Your Post"
                    ) : (
                      <>
                        <CheckCircle2 className="h-4 w-4" />
                        {item.type === 'lost' ? "I Found This!" : "This is Mine!"}
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <ReportItemModal 
        isOpen={isModalOpen} 
        onClose={() => setIsModalOpen(false)} 
        onSubmit={handleReportItem} 
      />
    </div>
  );
};
