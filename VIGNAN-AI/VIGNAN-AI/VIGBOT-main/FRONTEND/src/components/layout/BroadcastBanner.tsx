"use client";

import { useState, useEffect } from 'react';
import { getActiveBroadcasts } from '@/actions/broadcasts';
import { AlertCircle, X, Info, AlertTriangle } from 'lucide-react';

export function BroadcastBanner() {
  const [broadcasts, setBroadcasts] = useState<any[]>([]);
  const [dismissedIds, setDismissedIds] = useState<number[]>([]);

  useEffect(() => {
    const fetchBroadcasts = async () => {
      const result = await getActiveBroadcasts();
      if (result.success && result.broadcasts) {
        setBroadcasts(result.broadcasts);
      }
    };
    
    fetchBroadcasts();
    // Poll every 30 seconds
    const interval = setInterval(fetchBroadcasts, 30000);
    return () => clearInterval(interval);
  }, []);

  const dismiss = (id: number) => {
    setDismissedIds(prev => [...prev, id]);
  };

  const activeBroadcasts = broadcasts.filter(b => !dismissedIds.includes(b.id));

  if (activeBroadcasts.length === 0) return null;

  return (
    <div className="w-full flex flex-col z-50 sticky top-0">
      {activeBroadcasts.map((broadcast) => (
        <div 
          key={broadcast.id} 
          className={`w-full flex items-center justify-between px-4 py-3 text-sm font-medium
            ${broadcast.type === 'emergency' ? 'bg-red-500 text-white' : 
              broadcast.type === 'warning' ? 'bg-yellow-500 text-white' : 
              'bg-blue-600 text-white'}
          `}
        >
          <div className="flex items-center gap-2 max-w-[90%]">
            {broadcast.type === 'emergency' && <AlertCircle className="h-5 w-5 flex-shrink-0" />}
            {broadcast.type === 'warning' && <AlertTriangle className="h-5 w-5 flex-shrink-0" />}
            {broadcast.type === 'info' && <Info className="h-5 w-5 flex-shrink-0" />}
            
            <p className="truncate">{broadcast.message}</p>
          </div>
          <button 
            onClick={() => dismiss(broadcast.id)}
            className="p-1 hover:bg-white/20 rounded-full transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      ))}
    </div>
  );
}
