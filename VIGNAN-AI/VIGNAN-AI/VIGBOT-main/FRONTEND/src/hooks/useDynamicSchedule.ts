import { useState, useEffect } from 'react';
import { WEEKLY_TIMETABLE } from '@/data/timetable';

export const useDynamicSchedule = () => {
  const [currentTime, setCurrentTime] = useState<Date | null>(null);

  useEffect(() => {
    setCurrentTime(new Date());
    const interval = setInterval(() => setCurrentTime(new Date()), 60000);
    return () => clearInterval(interval);
  }, []);

  const d = currentTime || new Date();
  const realToday = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"][d.getDay()];
  const todaySlots = WEEKLY_TIMETABLE[realToday === "Sunday" ? "Monday" : realToday] || [];
  
  const parseToMinutes = (timeStr: string) => {
    const m = timeStr.match(/^(\d{1,2}):(\d{2})\s*(AM|PM)?$/i);
    if (!m) return 0;
    let hours = parseInt(m[1], 10);
    const mins = parseInt(m[2], 10);
    const ampm = m[3] ? m[3].toUpperCase() : null;
    if (ampm === "PM" && hours < 12) hours += 12;
    if (ampm === "AM" && hours === 12) hours = 0;
    return hours * 60 + mins;
  };

  const currentMinutes = d.getHours() * 60 + d.getMinutes();
  
  let nextClassSlot = todaySlots[0];
  if (currentTime) {
    const upcoming = todaySlots.filter(s => {
      const times = s.time.split(/[-–]/).map(t => t.trim());
      if (times.length < 2) return false;
      return parseToMinutes(times[0]) > currentMinutes || (parseToMinutes(times[0]) <= currentMinutes && parseToMinutes(times[1]) > currentMinutes);
    });
    if (upcoming.length > 0) nextClassSlot = upcoming[0];
  }

  // Dynamic next exam date (mocked to 2 days from current time for realism instead of fixed 06 Oct in past)
  const nextExamDate = new Date(d);
  nextExamDate.setDate(nextExamDate.getDate() + 2);
  const formattedNextExamDate = nextExamDate.toLocaleDateString('en-GB', { day: '2-digit', month: 'short' });

  return {
    nextClassSlot,
    formattedNextExamDate,
    currentTime: d,
  };
};
