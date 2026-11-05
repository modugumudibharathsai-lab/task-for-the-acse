"use client";

import React, { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMap, LayersControl, Polyline, LayerGroup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

// Fix Leaflet's default icon path issues with Next.js/Webpack
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png",
  iconUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
});

const RecenterAutomatically = ({ lat, lng }: { lat: number; lng: number }) => {
  const map = useMap();
  useEffect(() => {
    map.flyTo([lat, lng], map.getZoom(), { animate: true, duration: 1.5 });
  }, [lat, lng, map]);
  return null;
};

const BaseLayerTracker = ({ onLayerChange }: { onLayerChange: (name: string) => void }) => {
  const map = useMap();
  useEffect(() => {
    const handleLayerChange = (e: any) => {
      onLayerChange(e.name);
    };
    map.on('baselayerchange', handleLayerChange);
    return () => {
      map.off('baselayerchange', handleLayerChange);
    };
  }, [map, onLayerChange]);
  return null;
};

interface LocationData {
  id: string;
  name: string;
  building: string;
  floor: string;
  type: string;
  latitude?: number;
  longitude?: number;
}

interface DynamicMapProps {
  locations: LocationData[];
  selectedLocation?: LocationData | null;
  userCharacter?: string;
  userLocation?: [number, number] | null;
  routeTo?: LocationData | null;
  onLocationSelect?: (location: LocationData) => void;
}

// Pseudo-random number generator for deterministic placement based on string
const hashString = (str: string) => {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  return hash;
};



export default function DynamicMap({ 
  locations, 
  selectedLocation, 
  userCharacter = "dot", 
  userLocation,
  routeTo,
  onLocationSelect 
}: DynamicMapProps) {
  const [activeBaseLayer, setActiveBaseLayer] = useState("OpenStreetMap");
  
  // Center of Vignan University Campus
  const defaultCenter: [number, number] = [16.232820, 80.550347];
  const actualUserLocation = userLocation || defaultCenter;
  
  const mapCenter = selectedLocation
    ? [
        selectedLocation.latitude || defaultCenter[0] + (hashString(selectedLocation.id) % 100) * 0.00002, 
        selectedLocation.longitude || defaultCenter[1] + (hashString(selectedLocation.id + "1") % 100) * 0.00002
      ] as [number, number]
    : userLocation ? userLocation : defaultCenter;

  const getUserMarkerHtml = () => {
    let emoji = "📍";
    switch(userCharacter) {
      case "student": emoji = "👨‍🎓"; break;
      case "happy": emoji = "😁"; break;
      case "teacher": emoji = "🧑‍🏫"; break;
      case "dot": emoji = "📍"; break;
    }

    return `<div class="relative flex h-8 w-8 items-center justify-center bg-white rounded-full border-2 border-blue-500 shadow-md text-lg z-20">
              ${emoji}
            </div>`;
  };

  const getRouteCoordinates = (): [number, number][] => {
    if (!routeTo || !actualUserLocation) return [];
    
    const destLat = routeTo.latitude || (defaultCenter[0] + (hashString(routeTo.id) % 100) * 0.00002);
    const destLng = routeTo.longitude || (defaultCenter[1] + (hashString(routeTo.id + "1") % 100) * 0.00002);
    
    // Simulate a path by adding a midpoint to make it look like a route rather than a direct line
    const midLat = (actualUserLocation[0] + destLat) / 2 + 0.0005;
    const midLng = (actualUserLocation[1] + destLng) / 2;
    
    return [actualUserLocation, [midLat, midLng], [destLat, destLng]];
  };

  return (
    <MapContainer 
      center={mapCenter} 
      zoom={17} 
      style={{ height: "100%", width: "100%", zIndex: 0 }}
      scrollWheelZoom={true}
    >
      <LayersControl position="topright">
        <BaseLayerTracker onLayerChange={setActiveBaseLayer} />
        <LayersControl.BaseLayer checked name="OpenStreetMap">
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
        </LayersControl.BaseLayer>
        
        <LayersControl.BaseLayer name="Satellite Imagery">
          <LayerGroup>
            <TileLayer
              attribution='Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
              url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
            />
          </LayerGroup>
        </LayersControl.BaseLayer>

        <LayersControl.BaseLayer name="Topographic">
          <TileLayer
            attribution='Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)'
            url="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png"
          />
        </LayersControl.BaseLayer>
      </LayersControl>

      {(selectedLocation || userLocation) && (
        <RecenterAutomatically lat={mapCenter[0]} lng={mapCenter[1]} />
      )}

      {/* "You are here" Marker */}
      <Marker 
        position={actualUserLocation}
        icon={L.divIcon({
          className: "bg-transparent",
          html: getUserMarkerHtml(),
          iconSize: userCharacter === "dot" ? [20, 20] : [32, 32],
          iconAnchor: userCharacter === "dot" ? [10, 10] : [16, 16],
          popupAnchor: [0, -10]
        })}
        zIndexOffset={1000}
      >
        <Popup>
          <div className="font-bold text-blue-600">You are here</div>
          <div className="text-xs text-slate-500">Current Location</div>
        </Popup>
      </Marker>
      
      {/* Draw Simulated Route */}
      {routeTo && (
        <Polyline 
          positions={getRouteCoordinates()} 
          color="#3b82f6" 
          weight={4} 
          dashArray="10, 10" 
          className="animate-pulse"
        />
      )}
      
      {/* No location labels rendered on the map per user request */}

      {/* Render only the popup for the selected location without any markers */}
      {selectedLocation && (() => {
        const latOffset = (hashString(selectedLocation.id) % 100) * 0.00002;
        const lngOffset = (hashString(selectedLocation.id + "1") % 100) * 0.00002;
        const lat = selectedLocation.latitude || (defaultCenter[0] + latOffset);
        const lng = selectedLocation.longitude || (defaultCenter[1] + lngOffset);
        
        return (
          <Popup position={[lat, lng]} autoPan={true}>
            <div className="text-sm min-w-[150px]">
              <p className="font-bold">{selectedLocation.name}</p>
              <p className="text-xs text-slate-600">{selectedLocation.building}, Floor {selectedLocation.floor}</p>
              <p className="text-[10px] font-bold text-muted-foreground uppercase mt-1 px-1.5 py-0.5 bg-slate-100 rounded inline-block">{selectedLocation.type}</p>
            </div>
          </Popup>
        );
      })()}
    </MapContainer>
  );
}
