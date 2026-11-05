"use client";

import { useState, useEffect } from "react";
import { Trophy, Medal, Star } from "lucide-react";
import { getGamificationData } from "@/actions/gamification";
import { CURRENT_STUDENT } from "@/data/student";

export function GamificationView() {
  const [data, setData] = useState<{points: number; badges: any[]}>({ points: 0, badges: [] });

  useEffect(() => {
    getGamificationData(CURRENT_STUDENT.id).then(setData);
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Gamification & Rewards</h2>
        <p className="text-muted-foreground">Your campus activity points and badges.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-xl border bg-card text-card-foreground shadow-sm p-6 flex flex-col items-center justify-center space-y-2">
          <Trophy className="h-12 w-12 text-yellow-500" />
          <h3 className="text-xl font-semibold">Total Points</h3>
          <p className="text-4xl font-bold text-primary">{data.points}</p>
        </div>

        <div className="rounded-xl border bg-card text-card-foreground shadow-sm p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Medal className="h-5 w-5 text-indigo-500" />
            Earned Badges
          </h3>
          <div className="flex flex-wrap gap-2">
            {data.badges.length > 0 ? (
              data.badges.map((badge, idx) => (
                <div key={idx} className="flex items-center gap-2 bg-indigo-50 text-indigo-700 px-3 py-1.5 rounded-full text-sm font-medium" title={badge.description}>
                  <Star className="h-4 w-4" />
                  {typeof badge === 'string' ? badge : badge.name}
                </div>
              ))
            ) : (
              <p className="text-sm text-muted-foreground">No badges earned yet.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
