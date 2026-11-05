import React, { useEffect, useState } from "react";
import { MapPin, Search, Compass, Navigation, LocateFixed, Layers, Maximize, Minimize } from "lucide-react";
import { getCampusLocations } from "@/actions/campus";
import dynamic from "next/dynamic";

const DynamicMap = dynamic(() => import("./DynamicMap"), { 
  ssr: false,
  loading: () => (
    <div className="flex-1 bg-slate-100 flex items-center justify-center relative overflow-hidden h-full min-h-[400px]">
      <div className="text-center space-y-2 z-10 bg-white/80 p-6 rounded-xl shadow-sm border border-slate-200">
        <MapPin className="h-8 w-8 text-blue-600 mx-auto animate-pulse" />
        <p className="font-medium text-slate-700">Loading Interactive Map...</p>
      </div>
    </div>
  )
});

export const CampusMapView = () => {
  const [locations, setLocations] = useState<any[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedLocation, setSelectedLocation] = useState<any | null>(null);
  const [userCharacter, setUserCharacter] = useState("dot"); // Default dot
  
  // New Map States
  const [userLocation, setUserLocation] = useState<[number, number] | null>(null);
  const [isLocating, setIsLocating] = useState(false);
  const [routeTo, setRouteTo] = useState<any | null>(null);
  const [activeCategory, setActiveCategory] = useState<string>("All");
  const [isFullScreen, setIsFullScreen] = useState(false);

  const characterOptions = [
    { id: "dot", label: "Dot", emoji: "📍" },
    { id: "student", label: "Student", emoji: "👨‍🎓" },
    { id: "happy", label: "Happy", emoji: "😁" },
    { id: "teacher", label: "Teacher", emoji: "🧑‍🏫" }
  ];
  
  const categories = ["All", "Academic", "Administrative", "Facility", "Hostel", "Food"];

  const mapContainerRef = React.useRef<HTMLDivElement>(null);

  useEffect(() => {
    const fetchLocations = async () => {
      const res = await getCampusLocations();
      if (res.success) {
        setLocations((res.data as any[]) || []);
      }
    };
    fetchLocations();
  }, []);

  // Listen for native fullscreen changes
  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullScreen(!!document.fullscreenElement);
    };
    document.addEventListener("fullscreenchange", handleFullscreenChange);
    return () => document.removeEventListener("fullscreenchange", handleFullscreenChange);
  }, []);

  // Reset route when selecting a new location
  useEffect(() => {
    if (selectedLocation?.id !== routeTo?.id) {
      setRouteTo(null);
    }
  }, [selectedLocation, routeTo]);

  const toggleFullScreen = () => {
    if (!document.fullscreenElement) {
      mapContainerRef.current?.requestFullscreen().catch(err => {
        console.error("Error attempting to enable fullscreen:", err);
      });
    } else {
      document.exitFullscreen();
    }
  };

  const handleLocateMe = () => {
    setIsLocating(true);
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setUserLocation([position.coords.latitude, position.coords.longitude]);
          setSelectedLocation(null); // Clear selected location so map flies to user
          setIsLocating(false);
        },
        (error) => {
          console.error("Error getting location:", error);
          alert("Could not get your location. Please ensure location permissions are granted.");
          setIsLocating(false);
        },
        { enableHighAccuracy: true, maximumAge: 0 }
      );
    } else {
      alert("Geolocation is not supported by your browser");
      setIsLocating(false);
    }
  };

  const handleGetDirections = () => {
    if (!userLocation) {
      // If no user location yet, try to get it first
      handleLocateMe();
      // Use campus center as fallback for demo purposes
      setUserLocation([16.232820, 80.550347]);
    }
    setRouteTo(selectedLocation);
  };

  const normalizedSearch = searchTerm.toLowerCase().replace(/[\s-]/g, '');
  const filteredLocations = locations.filter(l => {
    const matchesSearch = l.name.toLowerCase().replace(/[\s-]/g, '').includes(normalizedSearch) || 
      l.building.toLowerCase().replace(/[\s-]/g, '').includes(normalizedSearch) ||
      (l.description && l.description.toLowerCase().replace(/[\s-]/g, '').includes(normalizedSearch)) ||
      (l.type && l.type.toLowerCase().replace(/[\s-]/g, '').includes(normalizedSearch));

    if (activeCategory === "All") return matchesSearch;
    
    const typeLower = (l.type || "").toLowerCase();
    let matchesCategory = false;
    
    switch(activeCategory) {
      case "Food": matchesCategory = typeLower.includes("food") || typeLower.includes("canteen") || typeLower.includes("cafeteria"); break;
      case "Academic": matchesCategory = typeLower.includes("academic") || typeLower.includes("lab") || typeLower.includes("classroom") || typeLower.includes("office"); break;
      case "Hostel": matchesCategory = typeLower.includes("hostel") || typeLower.includes("dorm"); break;
      case "Administrative": matchesCategory = typeLower.includes("admin"); break;
      case "Facility": matchesCategory = typeLower.includes("facility") || typeLower.includes("bank") || typeLower.includes("atm") || typeLower.includes("library"); break;
      default: matchesCategory = true;
    }
    
    return matchesSearch && matchesCategory;
  });

  const wrapperClass = isFullScreen 
    ? "fixed inset-0 z-[9999] bg-card p-4 flex flex-col" 
    : "space-y-6 animate-in fade-in zoom-in-95 duration-300 flex flex-col h-auto lg:h-[calc(100vh-12rem)] lg:min-h-[500px]";

  return (
    <div ref={mapContainerRef} className={wrapperClass}>
      {!isFullScreen && (
        <>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 shrink-0">
            <div>
              <h2 className="text-2xl font-bold tracking-tight">Campus Directory & Map</h2>
              <p className="text-sm text-muted-foreground">Find cabins, labs, and facilities across the campus.</p>
            </div>
            <div className="relative max-w-sm w-full">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search 'HOD', 'Library'..."
                className="w-full pl-9 pr-4 py-2 bg-card border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>

          {/* Category Filter Chips */}
          <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-hide shrink-0">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setActiveCategory(cat)}
                className={`px-4 py-1.5 rounded-full text-sm font-medium whitespace-nowrap transition-colors ${
                  activeCategory === cat 
                    ? 'bg-blue-600 text-white shadow-sm' 
                    : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </>
      )}

      <div className={`grid grid-cols-1 ${isFullScreen ? 'lg:grid-cols-1' : 'lg:grid-cols-3'} gap-6 lg:flex-1 lg:min-h-0`}>
        {/* Interactive Map */}
        <div className={`${isFullScreen ? 'col-span-1' : 'lg:col-span-2'} rounded-xl border border-border bg-card overflow-hidden shadow-sm flex flex-col relative h-[400px] lg:h-full lg:min-h-0`}>
          <div className="bg-muted/30 border-b border-border p-4 flex flex-wrap items-center justify-between gap-2 shrink-0">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <Compass className="h-5 w-5 text-blue-600" />
                <h3 className="font-semibold text-sm hidden sm:inline-block">Interactive Map</h3>
              </div>
              <button 
                onClick={handleLocateMe}
                disabled={isLocating}
                className="flex items-center gap-1.5 text-xs font-medium bg-white border border-slate-200 px-3 py-1.5 rounded-lg hover:bg-slate-50 text-slate-700 transition-colors disabled:opacity-50"
              >
                <LocateFixed className={`h-4 w-4 text-blue-600 ${isLocating ? 'animate-spin' : ''}`} />
                {isLocating ? 'Locating...' : 'Locate Me'}
              </button>
              <button 
                onClick={toggleFullScreen}
                className="flex items-center gap-1.5 text-xs font-medium bg-white border border-slate-200 px-3 py-1.5 rounded-lg hover:bg-slate-50 text-slate-700 transition-colors"
                title="Toggle Full Screen"
              >
                {isFullScreen ? <Minimize className="h-4 w-4" /> : <Maximize className="h-4 w-4" />}
                <span className="hidden sm:inline">{isFullScreen ? 'Exit' : 'Full Screen'}</span>
              </button>
            </div>
            
            <div className="flex items-center gap-2">
              <div className="flex items-center bg-white border border-border rounded-lg px-2 py-1 gap-1 hidden sm:flex">
                <span className="text-xs text-muted-foreground mr-1">You:</span>
                {characterOptions.map(char => (
                  <button
                    key={char.id}
                    onClick={() => setUserCharacter(char.id)}
                    className={`h-6 w-6 rounded flex items-center justify-center text-sm ${userCharacter === char.id ? 'bg-blue-100 ring-1 ring-blue-400' : 'hover:bg-slate-100'}`}
                    title={char.label}
                  >
                    {char.emoji}
                  </button>
                ))}
              </div>
              {selectedLocation && (
                <button 
                  onClick={() => setSelectedLocation(null)}
                  className="text-xs bg-white border border-border px-2 py-1.5 rounded-lg hover:bg-slate-50 transition-colors"
                >
                  Reset View
                </button>
              )}
            </div>
          </div>
          <div className="flex-1 relative z-0 min-h-0">
            <DynamicMap 
              locations={filteredLocations} 
              selectedLocation={selectedLocation} 
              userCharacter={userCharacter} 
              userLocation={userLocation}
              routeTo={routeTo}
              onLocationSelect={setSelectedLocation}
            />
          </div>
        </div>

        {/* Directory List / Details Panel */}
        {!isFullScreen && (
          <div className="rounded-xl border border-border bg-card flex flex-col h-full shadow-sm overflow-hidden min-h-0">
          {selectedLocation ? (
            // Location Details Panel
            <div className="flex flex-col h-full animate-in slide-in-from-right-4 duration-300">
              <div className="bg-blue-600 text-white p-4 shrink-0 flex justify-between items-start">
                <div>
                  <h3 className="font-bold text-lg">{selectedLocation.name}</h3>
                  <p className="text-blue-100 text-sm">{selectedLocation.building}, Floor {selectedLocation.floor}</p>
                </div>
                <button 
                  onClick={() => setSelectedLocation(null)}
                  className="bg-blue-700/50 hover:bg-blue-700 rounded-full p-1.5 transition-colors"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                </button>
              </div>
              <div className="p-4 flex-1 overflow-y-auto space-y-4">
                
                {/* Directions Button - NEW */}
                <button 
                  onClick={handleGetDirections}
                  className="w-full flex items-center justify-center gap-2 bg-blue-50 text-blue-700 hover:bg-blue-100 py-3 px-4 rounded-lg text-sm font-semibold transition-colors border border-blue-200"
                >
                  <Navigation className="h-4 w-4" />
                  {routeTo?.id === selectedLocation.id ? 'Route Displayed' : 'Get Directions'}
                </button>

                <div>
                  <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">Description</h4>
                  <p className="text-sm">{selectedLocation.description || "No description available for this location."}</p>
                </div>
                
                <div className="space-y-2 pt-4 border-t border-border">
                  {selectedLocation.features && selectedLocation.features.length > 0 ? (
                    selectedLocation.features.map((feature: string, idx: number) => {
                      let btnClass = "w-full flex items-center justify-center gap-2 py-2 px-4 rounded-lg text-sm font-medium transition-colors ";
                      let icon = null;
                      
                      if (feature.includes('Directions')) {
                        btnClass += "bg-blue-600 hover:bg-blue-700 text-white shadow-sm";
                        icon = <Navigation className="h-4 w-4" />;
                      } else if (feature.includes('Schedule') || feature.includes('Books') || feature.includes('Menu')) {
                        btnClass += "bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-200";
                        icon = <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>;
                      } else {
                        btnClass += "bg-white hover:bg-slate-50 text-blue-600 border border-blue-200";
                        icon = <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>;
                      }

                      return (
                        <button key={idx} className={btnClass}>
                          {icon}
                          {feature}
                        </button>
                      );
                    })
                  ) : (
                    <p className="text-xs text-muted-foreground italic text-center py-2">No special features available</p>
                  )}
                </div>
              </div>
            </div>
          ) : (
            // Directory List View
            <>
              <div className="bg-muted/30 border-b border-border p-4 shrink-0 flex justify-between items-center">
                <h3 className="font-semibold text-sm">Directory ({filteredLocations.length})</h3>
              </div>
              <div className="flex-1 overflow-y-auto p-2 space-y-2 scrollbar-thin min-h-0">
                {filteredLocations.length > 0 ? (
                  filteredLocations.map((loc) => (
                    <div 
                      key={loc.id} 
                      onClick={() => setSelectedLocation(loc)}
                      className={`p-3 rounded-lg border transition-colors cursor-pointer group ${
                        selectedLocation?.id === loc.id 
                          ? 'border-blue-500 bg-blue-50/80 shadow-sm' 
                          : 'border-slate-100 hover:border-blue-200 hover:bg-blue-50/50'
                      }`}
                    >
                      <div className="flex justify-between items-start">
                        <div>
                          <h4 className={`font-semibold text-sm ${selectedLocation?.id === loc.id ? 'text-blue-700' : 'group-hover:text-blue-700'}`}>
                            {loc.name}
                          </h4>
                          <p className="text-xs text-muted-foreground mt-0.5">{loc.building}, Floor {loc.floor}</p>
                        </div>
                        <span className="bg-slate-100 text-slate-600 text-[10px] uppercase tracking-wider font-bold px-2 py-0.5 rounded-full">
                          {loc.type}
                        </span>
                      </div>
                      <div className={`mt-3 flex items-center text-xs font-medium transition-opacity ${
                        selectedLocation?.id === loc.id ? 'text-blue-700 opacity-100' : 'text-blue-600 opacity-0 group-hover:opacity-100'
                      }`}>
                        <Navigation className="h-3 w-3 mr-1" /> View Details
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="p-4 text-center text-sm text-muted-foreground">
                    No locations found matching "{searchTerm}".
                  </div>
                )}
              </div>
            </>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
