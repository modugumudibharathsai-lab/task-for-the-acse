import { getBackendUrl } from "@/lib/backend-url";
import React, { useEffect, useState } from "react";
import { Store, Tag, Plus, IndianRupee } from "lucide-react";
import { getMarketplaceListings, createMarketplaceListing } from "@/actions/marketplace";
import { useStudent } from "@/context/StudentContext";
import { CURRENT_STUDENT } from "@/data/student";

export const MarketplaceView = () => {
  const { studentData } = useStudent();
  const student = studentData?.profile || CURRENT_STUDENT;
  const [listings, setListings] = useState<any[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newCategory, setNewCategory] = useState("Books");
  const [newPrice, setNewPrice] = useState(0);

  useEffect(() => {
    fetchListings();
  }, []);

  const fetchListings = async () => {
    let loaded = false;
    try {
      const res = await getMarketplaceListings();
      if (res?.success && Array.isArray(res?.data) && res.data.length > 0) {
        setListings(res.data as any[]);
        loaded = true;
      }
    } catch (e) {
      console.warn("Server action failed:", e);
    }

    if (!loaded) {
      try {
        const backendUrl = getBackendUrl();
        const res = await fetch(`${backendUrl}/community/marketplace`);
        if (res.ok) {
          const json = await res.json();
          if (json?.success && Array.isArray(json?.data) && json.data.length > 0) {
            setListings(json.data);
            loaded = true;
          }
        }
      } catch (e) {
        console.warn("Direct fetch error:", e);
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;
    const studentId = student?.id || "251FA04E13";
    let created = false;
    try {
      const res = await createMarketplaceListing(studentId, newTitle, newCategory, newPrice);
      if (res?.success) created = true;
    } catch (e) {
      console.warn("Server action failed:", e);
    }

    if (!created) {
      try {
        const backendUrl = getBackendUrl();
        const res = await fetch(`${backendUrl}/community/marketplace`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            student_id: studentId,
            title: newTitle,
            category: newCategory,
            price: newPrice
          })
        });
        if (res.ok) {
          const json = await res.json();
          if (json?.success) created = true;
        }
      } catch (e) {
        console.error("Direct create listing error:", e);
      }
    }

    if (created) {
      setIsModalOpen(false);
      setNewTitle("");
      setNewPrice(0);
      fetchListings();
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in zoom-in-95 duration-300">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Student Marketplace</h2>
          <p className="text-sm text-muted-foreground">Buy, sell, or carpool securely with other students.</p>
        </div>
        <button 
          onClick={() => setIsModalOpen(true)}
          className="flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white font-medium text-sm px-4 py-2 rounded-lg transition-colors shadow-sm"
        >
          <Plus className="h-4 w-4" /> Create Listing
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {listings.length > 0 ? (
          listings.map((l) => (
            <div key={l.id} className="rounded-xl border border-border bg-card overflow-hidden shadow-sm hover:shadow-md transition-shadow group flex flex-col">
              <div className="h-32 bg-slate-100 flex items-center justify-center border-b border-border text-slate-300 group-hover:bg-slate-200 transition-colors">
                 <Store className="h-10 w-10" />
              </div>
              <div className="p-4 flex-1 flex flex-col justify-between space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-[10px] uppercase tracking-wider font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full flex items-center gap-1">
                      <Tag className="h-3 w-3" /> {l.category}
                    </span>
                    <span className="text-xs text-muted-foreground">{new Date(l.created_at).toLocaleDateString()}</span>
                  </div>
                  <h3 className="font-bold text-foreground line-clamp-2">{l.title}</h3>
                  <p className="text-xs text-muted-foreground mt-1">Seller: {l.student_id}</p>
                </div>
                <div className="flex items-center justify-between pt-3 border-t border-border">
                  <span className="font-bold flex items-center text-lg">
                    {l.price > 0 ? <><IndianRupee className="h-4 w-4" />{l.price}</> : <span className="text-emerald-600 text-sm">FREE / SPLIT</span>}
                  </span>
                  <button className="text-sm font-medium text-blue-600 hover:text-blue-800">
                    Contact
                  </button>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="col-span-full rounded-xl border border-dashed border-border bg-muted/30 p-12 text-center">
            <Store className="h-12 w-12 text-muted-foreground mx-auto mb-3 opacity-50" />
            <p className="font-medium text-slate-600">No active listings</p>
            <p className="text-sm text-muted-foreground mt-1">Be the first to list an item for sale or carpool.</p>
          </div>
        )}
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4 animate-in fade-in duration-200">
          <div className="bg-card w-full max-w-md rounded-xl shadow-2xl overflow-hidden animate-in zoom-in-95 duration-200">
            <div className="bg-muted/30 border-b border-border p-4">
              <h3 className="font-bold text-lg">Create New Listing</h3>
            </div>
            <form onSubmit={handleSubmit} className="p-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Title</label>
                <input 
                  type="text" 
                  required
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  placeholder="E.g., Engineering Drawing Kit"
                  className="w-full rounded-md border border-input px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Category</label>
                  <select 
                    value={newCategory}
                    onChange={(e) => setNewCategory(e.target.value)}
                    className="w-full rounded-md border border-input px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  >
                    <option value="Books">Books</option>
                    <option value="Electronics">Electronics</option>
                    <option value="Carpool">Carpool</option>
                    <option value="Other">Other</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Price (₹)</label>
                  <input 
                    type="number" 
                    min="0"
                    value={newPrice}
                    onChange={(e) => setNewPrice(Number(e.target.value))}
                    className="w-full rounded-md border border-input px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  />
                </div>
              </div>
              <div className="flex justify-end gap-2 pt-4">
                <button 
                  type="button" 
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-medium text-sm rounded-lg transition-colors"
                >
                  Post Listing
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
