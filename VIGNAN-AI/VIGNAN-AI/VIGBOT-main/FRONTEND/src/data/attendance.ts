import { calculateConsecutiveClassesNeeded } from "@/lib/utils";

export interface AttendanceSubject {
  code: string;
  name: string;
  faculty: string;
  attended: number;
  total: number;
  percentage: number;
  status: "Attention" | "Healthy" | "Critical";
  minRequiredPct: number;
  classesNeeded70: number;
  classesNeeded75: number;
  canBunkBefore70: number;
  scheduleDays: string[];
}

export const ATTENDANCE_DATA: {
  overallPercentage: number;
  totalAttended: number;
  totalConducted: number;
  status: "Attention required" | "Healthy";
  sourceAgent: string;
  subjects: AttendanceSubject[];
} = {
  overallPercentage: 84, // Healthy average across Section-7
  totalAttended: 351,
  totalConducted: 419,
  status: "Healthy",
  sourceAgent: "Attendance Engine - Section 7",
  subjects: [
    {
      code: "DS-25CS201",
      name: "Data Structures",
      faculty: "Dr. R. Prathap Kumar (7569888963)",
      attended: 42,
      total: 50,
      percentage: 84,
      status: "Healthy",
      minRequiredPct: 75,
      classesNeeded70: 0,
      classesNeeded75: 0,
      canBunkBefore70: 8,
      scheduleDays: ["Mon 02:20", "Tue 12:30", "Wed 02:20", "Fri 09:05", "Sat 01:20"],
    },
    {
      code: "DMS-25MT202",
      name: "Discrete Mathematical Structures",
      faculty: "DR. N. SANTHOSHO",
      attended: 41,
      total: 44,
      percentage: 93,
      status: "Healthy",
      minRequiredPct: 75,
      classesNeeded70: 0,
      classesNeeded75: 0,
      canBunkBefore70: 4,
      scheduleDays: ["Tue 08:15", "Wed 09:05", "Thu 02:20", "Fri 12:30"],
    },
    {
      code: "DBMS-25CS203",
      name: "Database Management System",
      faculty: "Ms. Y. Sai Eswari (8074131669)",
      attended: 41,
      total: 50,
      percentage: 82,
      status: "Healthy",
      minRequiredPct: 75,
      classesNeeded70: 0,
      classesNeeded75: 0,
      canBunkBefore70: 5,
      scheduleDays: ["Mon 03:10", "Tue 01:20", "Wed 01:20", "Thu 09:05", "Fri 02:20"],
    },
    {
      code: "OOPS-25CS204",
      name: "Object Oriented Programming Through Java",
      faculty: "Mr. T. Latesh Babu (Class Teacher)",
      attended: 28,
      total: 38,
      percentage: 74,
      status: "Attention",
      minRequiredPct: 75,
      classesNeeded70: 0,
      classesNeeded75: 0,
      canBunkBefore70: 7,
      scheduleDays: ["Mon 09:05", "Tue 03:10", "Thu 03:10", "Sat 12:30"],
    },
    {
      code: "DLD-25CS205",
      name: "Digital Logic design",
      faculty: "Mrs Archana (8985716984)",
      attended: 46,
      total: 54,
      percentage: 85,
      status: "Healthy",
      minRequiredPct: 75,
      classesNeeded70: calculateConsecutiveClassesNeeded(27, 40, 70), // 4
      classesNeeded75: calculateConsecutiveClassesNeeded(27, 40, 75), // 12
      canBunkBefore70: 0,
      scheduleDays: ["Mon 12:30", "Tue 02:20", "Wed 08:15", "Sat 02:20"],
    },
    {
      code: "AI-24CS302",
      name: "Artificial Intelligence",
      faculty: "Dr. M. Sunil Babu (8333001991)",
      attended: 43,
      total: 47,
      percentage: 91,
      status: "Healthy",
      minRequiredPct: 75,
      classesNeeded70: 0,
      classesNeeded75: 0,
      canBunkBefore70: 10,
      scheduleDays: ["Wed 12:30", "Thu 12:30", "Fri 01:20", "Sat 08:15"],
    },
    {
      code: "DW-25CS202",
      name: "Data Wrangling and Visualization",
      faculty: "Dr. M. Raja Rao (8979803148)",
      attended: 32,
      total: 41,
      percentage: 78,
      status: "Healthy",
      minRequiredPct: 75,
      classesNeeded70: 0,
      classesNeeded75: 0,
      canBunkBefore70: 9,
      scheduleDays: ["Tue 09:05", "Sat 09:05"],
    },
  ],
};
