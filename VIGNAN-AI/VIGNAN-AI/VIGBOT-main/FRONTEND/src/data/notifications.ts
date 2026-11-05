export interface NotificationItem {
  id: string;
  type: "EXAM_REMINDER" | "ATTENDANCE_ALERT" | "NEW_CIRCULAR" | "ACADEMIC_NOTICE" | "SERVICE_UPDATE";
  title: string;
  message: string;
  timestamp: string;
  priority: "urgent" | "high" | "normal";
  read: boolean;
  actionHref?: string;
  sourceAgent: string;
}

export const INITIAL_NOTIFICATIONS: NotificationItem[] = [
  {
    id: "NOTIF-01",
    type: "ATTENDANCE_ALERT",
    title: "ATTENDANCE ALERT",
    message: "Your Digital Electronics attendance (68%) requires attention to avoid end-term debarment.",
    timestamp: "15 mins ago",
    priority: "urgent",
    read: false,
    actionHref: "#attendance",
    sourceAgent: "Attendance System",
  },
  {
    id: "NOTIF-02",
    type: "EXAM_REMINDER",
    title: "EXAM REMINDER",
    message: "Digital Electronics End-Semester examination is scheduled for 18 Sep at 10:00 AM in Hall A2 (7 days remaining).",
    timestamp: "1 hour ago",
    priority: "high",
    read: false,
    actionHref: "#examinations",
    sourceAgent: "Examination Hub",
  },
  {
    id: "NOTIF-03",
    type: "SERVICE_UPDATE",
    title: "SERVICE UPDATE",
    message: "Your Bonafide Certificate request (#SR-8921) has been forwarded to Academic Registrar.",
    timestamp: "3 hours ago",
    priority: "normal",
    read: false,
    actionHref: "#services",
    sourceAgent: "Student Services",
  },
  {
    id: "NOTIF-04",
    type: "NEW_CIRCULAR",
    title: "NEW CIRCULAR",
    message: "University examination policy and hall ticket guidelines have been updated for Autumn 2026.",
    timestamp: "Yesterday",
    priority: "normal",
    read: true,
    actionHref: "#circulars",
    sourceAgent: "Circulars",
  },
  {
    id: "NOTIF-05",
    type: "ACADEMIC_NOTICE",
    title: "ACADEMIC NOTICE",
    message: "Pre-registration for Semester 6 open and professional electives closes on 25 September 2026.",
    timestamp: "2 days ago",
    priority: "normal",
    read: true,
    actionHref: "#circulars",
    sourceAgent: "Circulars",
  },
];
