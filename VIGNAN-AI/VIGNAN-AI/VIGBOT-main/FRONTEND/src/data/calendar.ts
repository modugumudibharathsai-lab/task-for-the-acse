export interface CalendarEvent {
  id: string;
  title: string;
  category: "Exams" | "Academic" | "Deadlines" | "Holidays" | "Assessments";
  startDate: string;
  endDate?: string;
  description: string;
  status: "Completed" | "Current" | "Upcoming";
  actionLabel?: string;
  actionHref?: string;
  sourceAgent: string;
}

/**
 * Official Academic Calendar (2026-27)
 * Vignan's Foundation for Science, Technology and Research (VFSTR) :: Vadlamudi
 * Bachelor of Technology (B.Tech) 2nd (R25), 3rd (R22C24) & 4th (R22) Year
 * Notification Dated: 6/1/2026 | Semester - I
 */
export const ACADEMIC_CALENDAR_DATA: CalendarEvent[] = [
  {
    id: "CAL-01",
    title: "Commencement of Module-1 (I-Sem)",
    category: "Academic",
    startDate: "10 Jul 2026",
    description: "Official commencement of instructional coursework and laboratory sessions for Module-1 of Semester-I.",
    status: "Completed",
    sourceAgent: "Academic Calendar",
  },
  {
    id: "CAL-02",
    title: "Module-1 Formative Assessment 1 (M-1 FA-1)",
    category: "Assessments",
    startDate: "05 Aug 2026",
    endDate: "06 Aug 2026",
    description: "First formative assessment (FA-1) for Module-1 courses across 2nd, 3rd & 4th year B.Tech.",
    status: "Completed",
    sourceAgent: "Assessments",
  },
  {
    id: "CAL-03",
    title: "Independence Day Holiday",
    category: "Holidays",
    startDate: "15 Aug 2026",
    description: "National holiday on account of Independence Day. Flag hoisting and celebrations at VFSTR campus.",
    status: "Completed",
    sourceAgent: "Academic Calendar",
  },
  {
    id: "CAL-04",
    title: "Milad-un-Nabi Holiday",
    category: "Holidays",
    startDate: "25 Aug 2026",
    description: "Institutional holiday on account of Milad-un-Nabi.",
    status: "Completed",
    sourceAgent: "Academic Calendar",
  },
  {
    id: "CAL-05",
    title: "Module-1 Formative Assessment 2 (M-1 FA-2)",
    category: "Assessments",
    startDate: "03 Sep 2026",
    endDate: "07 Sep 2026",
    description: "Second formative assessment for Module-1 (held on 03, 05 & 07 Sep) across 2nd, 3rd & 4th year.",
    status: "Completed",
    sourceAgent: "Assessments",
  },
  {
    id: "CAL-06",
    title: "Krishnashtami Holiday",
    category: "Holidays",
    startDate: "04 Sep 2026",
    description: "Institutional holiday on account of Sri Krishnashtami.",
    status: "Completed",
    sourceAgent: "Academic Calendar",
  },
  {
    id: "CAL-07",
    title: "Commencement of Module-2",
    category: "Academic",
    startDate: "08 Sep 2026",
    description: "Commencement of instructional lectures, project work and advanced laboratories for Module-2 (Semester-I).",
    status: "Current",
    actionLabel: "View Module-2 Courses",
    sourceAgent: "Academic Calendar",
  },
  {
    id: "CAL-08",
    title: "Vinayaka Chavithi Holiday",
    category: "Holidays",
    startDate: "14 Sep 2026",
    description: "Institutional holiday on account of Vinayaka Chavithi (Ganesh Chaturthi).",
    status: "Upcoming",
    sourceAgent: "Academic Calendar",
  },
  {
    id: "CAL-09",
    title: "Gandhi Jayanthi Holiday",
    category: "Holidays",
    startDate: "02 Oct 2026",
    description: "National holiday on account of Mahatma Gandhi Jayanthi.",
    status: "Upcoming",
    sourceAgent: "Academic Calendar",
  },
  {
    id: "CAL-10",
    title: "Module-2 Formative Assessment 1 (M-2 FA-1)",
    category: "Assessments",
    startDate: "06 Oct 2026",
    endDate: "08 Oct 2026",
    description: "Continuous internal assessment 1 for Module-2 subjects (06 & 07 Oct for 2nd, 3rd, 4th; 08 Oct for 2nd year).",
    status: "Upcoming",
    actionLabel: "View Assessment Card",
    sourceAgent: "Assessments",
  },
  {
    id: "CAL-11",
    title: "Dasara Holidays & Vijaya Dasami",
    category: "Holidays",
    startDate: "18 Oct 2026",
    endDate: "21 Oct 2026",
    description: "Dasara vacation period including Durgashtami (18 Oct), Dasara holidays (19 & 21 Oct) and Vijaya Dasami (20 Oct).",
    status: "Upcoming",
    sourceAgent: "Academic Calendar",
  },
  {
    id: "CAL-12",
    title: "Deepavali Holiday",
    category: "Holidays",
    startDate: "08 Nov 2026",
    description: "Institutional festival holiday on account of Deepavali.",
    status: "Upcoming",
    sourceAgent: "Academic Calendar",
  },
  {
    id: "CAL-13",
    title: "Module-2 Formative Assessment 2 (M-2 FA-2)",
    category: "Assessments",
    startDate: "11 Nov 2026",
    endDate: "13 Nov 2026",
    description: "Final formative internal assessment for Module-2 (2nd, 3rd & 4th year B.Tech).",
    status: "Upcoming",
    actionLabel: "View Assessment Card",
    sourceAgent: "Assessments",
  },
  {
    id: "CAL-14",
    title: "Preparation & Summative Assessment (Practical-Based)",
    category: "Exams",
    startDate: "14 Nov 2026",
    endDate: "20 Nov 2026",
    description: "Laboratory external evaluations, project demos and hands-on practical summative exams (2nd, 3rd & 4th Year).",
    status: "Upcoming",
    actionLabel: "View Practical Schedule",
    sourceAgent: "Examinations",
  },
  {
    id: "CAL-15",
    title: "Summative Assessment (Theory / Lecture-Based - End Sem)",
    category: "Exams",
    startDate: "21 Nov 2026",
    endDate: "04 Dec 2026",
    description: "Centralized end-semester theory examinations conducted by Examination Cell (Weeks 20, 21 & 22).",
    status: "Upcoming",
    actionLabel: "View Exam Schedule",
    sourceAgent: "Examinations",
  },
  {
    id: "CAL-16",
    title: "Commencement of II Semester",
    category: "Academic",
    startDate: "14 Dec 2026",
    description: "Official re-opening of university and commencement of instructional classes for B.Tech Semester-II (2026-27).",
    status: "Upcoming",
    sourceAgent: "Academic Calendar",
  },
];
