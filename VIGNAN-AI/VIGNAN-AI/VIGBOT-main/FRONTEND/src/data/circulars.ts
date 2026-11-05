export interface CircularItem {
  id: string;
  refNo: string;
  title: string;
  category: "Examinations" | "Academics" | "Administration" | "Holidays" | "Events";
  date: string;
  priority: "Urgent" | "High" | "Normal";
  shortDescription: string;
  issuedBy: string;
  sourceAgent: string;
  actionRequired?: string;
  downloadUrl?: string;
}

export const CIRCULARS_DATA: CircularItem[] = [
  {
    id: "CIR-2026-114",
    refNo: "COE/NOT/2026/09-18",
    title: "Semester Examination Schedule Released (Autumn 2026)",
    category: "Examinations",
    date: "08 Sep 2026",
    priority: "Urgent",
    shortDescription: "The official timetable for End-Semester Theory & Practical examinations is officially published. Hall ticket distribution begins 12 Sep.",
    issuedBy: "Office of the Controller of Examinations",
    sourceAgent: "Circulars",
    actionRequired: "Download hall ticket from Exams tab by 14 Sep.",
  },
  {
    id: "CIR-2026-109",
    refNo: "REG/CIR/2026/09-02",
    title: "Course Registration Deadline Announced for Semester 6 Electives",
    category: "Academics",
    date: "04 Sep 2026",
    priority: "High",
    shortDescription: "Pre-registration for upcoming Semester 6 open and professional electives closes on 25 September 2026. Late fee applies thereafter.",
    issuedBy: "Dean of Academic Affairs",
    sourceAgent: "Circulars",
    actionRequired: "Finalize elective choices with your Faculty Mentor.",
  },
  {
    id: "CIR-2026-105",
    refNo: "DSA/ATTN/2026/08-28",
    title: "Mandatory Attendance Review Notice — Autumn 2026",
    category: "Academics",
    date: "28 Aug 2026",
    priority: "Urgent",
    shortDescription: "Mid-term attendance records verified. Students falling below 75% threshold are instructed to meet respective course instructors immediately.",
    issuedBy: "Dean of Student Affairs",
    sourceAgent: "Circulars",
    actionRequired: "Check Attendance view for targeted consecutive class recovery.",
  },
  {
    id: "CIR-2026-098",
    refNo: "ACAD/POL/2026/08-15",
    title: "Academic Policy Update: AI Tooling Usage in Assignments",
    category: "Administration",
    date: "15 Aug 2026",
    priority: "Normal",
    shortDescription: "New institutional guidelines on ethical artificial intelligence citation standards for computer science laboratory deliverables.",
    issuedBy: "Academic Senate Board",
    sourceAgent: "Circulars",
  },
  {
    id: "CIR-2026-092",
    refNo: "EST/HOL/2026/08-10",
    title: "University Holiday Notification — Gandhi Jayanti & Dussehra Break",
    category: "Holidays",
    date: "10 Aug 2026",
    priority: "Normal",
    shortDescription: "The university administrative offices and academic departments will remain closed from 02 Oct to 06 Oct 2026.",
    issuedBy: "Registrar Secretariat",
    sourceAgent: "Circulars",
  },
];
