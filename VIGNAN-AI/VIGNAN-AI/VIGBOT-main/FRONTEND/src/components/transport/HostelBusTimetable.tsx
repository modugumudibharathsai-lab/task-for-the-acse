import { MapPin, Clock } from "lucide-react";

export function HostelBusTimetable() {
  const timetables = [
    {
      hostel: "KM HOSTEL",
      morning: ["7:50 AM", "8:05 AM", "8:40 AM", "9:30 AM", "10:30 AM", "11:35 AM"],
      evening: ["1:45 PM", "3:30 PM", "4:10 PM", "4:40 PM", "5:15 PM", "6:15 PM", "7:00 PM", "8:00 PM", "9:00 PM"],
    },
    {
      hostel: "VILLAS SP RESIDENCY",
      morning: ["7:45 AM", "8:00 AM", "8:40 AM", "9:00 AM", "9:50 AM", "11:30 AM"],
      evening: ["2:00 PM", "3:30 PM", "4:10 PM", "4:40 PM", "5:15 PM", "6:00 PM", "7:00 PM", "8:00 PM", "9:00 PM"],
    },
    {
      hostel: "AP, AR, AA, AO HOSTELS",
      morning: ["7:45 AM", "7:55 AM", "8:00 AM", "8:40 AM", "9:00 AM", "9:50 AM", "11:30 AM / 11:35 AM"],
      evening: ["2:00 PM", "3:30 PM", "4:10 PM", "4:40 PM", "5:15 PM", "6:00 PM", "7:00 PM", "8:00 PM", "9:00 PM"],
    }
  ];

  return (
    <div className="space-y-6">
      <div className="rounded-lg bg-amber-50 p-4 border border-amber-200 dark:bg-amber-950/50 dark:border-amber-900">
        <p className="text-sm text-amber-800 dark:text-amber-200 font-medium">
          Note: This is the current bus schedule w.e.f 01.10.2026. If there are any changes in the future, the revised timetable will be updated.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
        {timetables.map((schedule) => (
          <div key={schedule.hostel} className="rounded-xl border bg-card text-card-foreground shadow-sm overflow-hidden">
            <div className="bg-muted px-4 py-3 border-b">
              <h3 className="font-semibold text-lg">{schedule.hostel}</h3>
            </div>
            
            <div className="p-4 space-y-6">
              <div>
                <div className="flex items-center gap-2 mb-3 text-emerald-600 dark:text-emerald-500 font-medium">
                  <MapPin className="h-4 w-4" />
                  <h4>Morning Trip (Hostel to University)</h4>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  {schedule.morning.map((time, i) => (
                    <div key={i} className="flex items-center gap-2 text-sm bg-muted/50 p-2 rounded-md">
                      <Clock className="h-3 w-3 text-muted-foreground" />
                      <span>{time}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="border-t pt-4">
                <div className="flex items-center gap-2 mb-3 text-blue-600 dark:text-blue-500 font-medium">
                  <MapPin className="h-4 w-4" />
                  <h4>Evening Trip (University to Hostel)</h4>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  {schedule.evening.map((time, i) => (
                    <div key={i} className="flex items-center gap-2 text-sm bg-muted/50 p-2 rounded-md">
                      <Clock className="h-3 w-3 text-muted-foreground" />
                      <span>{time}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
