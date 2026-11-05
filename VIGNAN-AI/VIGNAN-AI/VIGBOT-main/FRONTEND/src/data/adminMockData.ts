export const mockGrievances = [
  { id: "GRV-1002", description: "Water cooler on 3rd floor N block is dispensing hot water", status: "Pending", timestamp: "2026-09-18T11:20:00.052421", withdrawal_reason: null },
  { id: "GRV-1001", description: "Wi-Fi extremely slow in Block B library section", status: "In Progress", timestamp: "2026-09-16T16:20:00.052421", withdrawal_reason: null },
  { id: "GRV-1003", description: "Stray dogs near the boys hostel entrance at night", status: "Resolved", timestamp: "2026-09-03T16:20:00.052421", withdrawal_reason: "Animal control team handled it." }
];

export const mockClubApps = [
  { id: 6, club_id: "CLUB_MUSIC", student_name: "VIGBOT", status: "Approved", timestamp: "2026-09-17T16:20:00.052421", withdrawal_reason: null },
  { id: 7, club_id: "CLUB_DRAMA", student_name: "Other Student", status: "Approved", timestamp: "2026-09-16T16:20:00.052421", withdrawal_reason: null }
];

export const mockBookings = [
  { id: 12, facility_id: 2, student_id: "251FA04E13", date: "2026-09-20", start_time: "14:00", end_time: "16:00", purpose: "Group study for mid-terms", status: "confirmed" },
  { id: 11, facility_id: 1, student_id: "251FA04E13", date: "2026-09-19", start_time: "17:00", end_time: "18:00", purpose: "Practice match", status: "confirmed" },
  { id: 13, facility_id: 4, student_id: "OTHER_STU", date: "2026-09-19", start_time: "16:00", end_time: "17:00", purpose: "Band practice", status: "confirmed" }
];

export const mockLostAndFound = [
  { id: 18, student_id: "251FA04E13", type: "found", title: "Apple AirPods Pro", description: "Found in AI Lab near the window seats", tags: "airpods, apple", contact_info: "251fa04e13@vignan.ac.in", status: "open", date_posted: "2026-09-18T14:20:00.052421", image_url: null },
  { id: 17, student_id: "OTHER_STU", type: "lost", title: "Hostel Keys with Marvel keychain", description: "Lost somewhere near the canteen", tags: "keys, marvel", contact_info: "other@vignan.ac.in", status: "open", date_posted: "2026-09-18T04:20:00.052421", image_url: "/captain_america_key.jpg" },
  { id: 15, student_id: "251FA04E13", type: "lost", title: "Blue Milton Water Bottle", description: "Lost near the central library seating area.", tags: "bottle, blue", contact_info: "251fa04e13@vignan.ac.in", status: "open", date_posted: "2026-09-16T16:20:00.052421", image_url: "/milton_bottle.png" },
  { id: 16, student_id: "OTHER_STU", type: "found", title: "Scientific Calculator", description: "Found Casio calculator in N-312", tags: "calculator", contact_info: "admin@vignan.ac.in", status: "claimed", date_posted: "2026-09-08T16:20:00.052421", image_url: null }
];

export const mockBroadcasts = [
  { id: 19, message: "Emergency: Campus power maintenance from 1 AM to 3 AM tonight.", type: "emergency", is_active: 1, timestamp: "2026-09-18T15:20:00.052421" },
  { id: 15, message: "Heavy rain expected tomorrow. Transport schedules may be delayed. Plan accordingly.", type: "warning", is_active: 1, timestamp: "2026-09-18T14:20:00.052421" },
  { id: 18, message: "Fire drill scheduled for tomorrow 3 PM at N-Block.", type: "warning", is_active: 1, timestamp: "2026-09-18T04:20:00.052421" },
  { id: 16, message: "TechFest 2026 registration is now open! Early bird discounts available.", type: "info", is_active: 1, timestamp: "2026-09-17T16:20:00.052421" },
  { id: 17, message: "Semester fee payment deadline extended to 15th October.", type: "info", is_active: 1, timestamp: "2026-09-16T16:20:00.052421" }
];

export const mockAnalyticsData = {
  grievances: { received: 3, investigation: 1, resolved: 1 },
  clubs: { approved: 2, pending: 0, rejected: 0 },
  bookings: { confirmed: 3, pending: 0, rejected: 0 }
};
