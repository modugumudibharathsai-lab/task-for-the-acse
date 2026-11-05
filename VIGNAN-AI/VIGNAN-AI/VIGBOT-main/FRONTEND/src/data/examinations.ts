export interface ExamScheduleItem {
  id: string;
  code: string;
  subject: string;
  examType: string;
  date: string;
  rawDate: string;
  time: string;
  venue: string;
  seatRange: string;
  daysRemaining: number;
  syllabusOverview: string;
  reportingTime: string;
}

/**
 * Official Examination Schedule - 2026-27 Semester I
 * Grounded in VFSTR B.Tech Academic Calendar (Dated: 6/1/2026)
 * Includes upcoming Formative Assessments (M-2 FA-1) and End-Semester Summative Assessments.
 */
export const EXAMINATIONS_DATA: {
  nearestExamDays: number;
  sourceAgent: string;
  exams: ExamScheduleItem[];
} = {
  nearestExamDays: 24,
  sourceAgent: "Examination Cell & Evaluation",
  exams: [
    {
      id: "EX-01",
      code: "M2-FA1",
      subject: "Module-2 Formative Assessment 1 (M-2 FA-1)",
      examType: "Continuous Internal Evaluation (Formative)",
      date: "06 October 2026",
      rawDate: "2026-10-06T10:00:00",
      time: "10:00 AM – 12:00 PM",
      venue: "Instructional Classrooms, Department of CSE",
      seatRange: "Section 7 Designated Desks",
      daysRemaining: 24,
      syllabusOverview: "Module-2 Syllabus: Advanced topics in Data Structures, Digital Logic Design, Discrete Math, OOP Java & DBMS",
      reportingTime: "09:45 AM",
    },
    {
      id: "EX-02",
      code: "M2-FA2",
      subject: "Module-2 Formative Assessment 2 (M-2 FA-2)",
      examType: "Continuous Internal Evaluation (Formative)",
      date: "11 November 2026",
      rawDate: "2026-11-11T10:00:00",
      time: "10:00 AM – 12:00 PM",
      venue: "Department of CSE, VFSTR",
      seatRange: "Section 7 Designated Desks",
      daysRemaining: 60,
      syllabusOverview: "Complete Module-2 Syllabus and revision across all enrolled B.Tech theory subjects",
      reportingTime: "09:45 AM",
    },
    {
      id: "EX-03",
      code: "DW-25CS202",
      subject: "Data Wrangling & Visualization (Practical Summative)",
      examType: "Preparation & Summative Assessment (Practical-Based)",
      date: "17 November 2026",
      rawDate: "2026-11-17T14:00:00",
      time: "02:00 PM – 05:00 PM",
      venue: "Computing Lab N-314A, VFSTR",
      seatRange: "Workstation 14",
      daysRemaining: 66,
      syllabusOverview: "Pandas, NumPy, Data Cleaning, ETL pipelines, Matplotlib, Seaborn, Interactive Dashboards, Live Coding Demo",
      reportingTime: "01:30 PM",
    },
    {
      id: "EX-04",
      code: "DLD-25CS205",
      subject: "Digital Logic Design (Summative Theory)",
      examType: "Summative Assessment (Lecture-Based End Semester)",
      date: "26 November 2026",
      rawDate: "2026-11-26T09:30:00",
      time: "09:30 AM – 12:30 PM",
      venue: "Examination Hall A2, VFSTR",
      seatRange: "Row D, Desk 42 (Hall Ticket #251FA04E13)",
      daysRemaining: 70,
      syllabusOverview: "Full Syllabus: Number Systems, Boolean Algebra, Karnaugh Maps, Combinational & Sequential Circuits, Counters, Registers",
      reportingTime: "09:00 AM",
    },
    {
      id: "EX-05",
      code: "DS-25CS201",
      subject: "Data Structures (Summative Theory)",
      examType: "Summative Assessment (Lecture-Based End Semester)",
      date: "21 November 2026",
      rawDate: "2026-11-21T09:30:00",
      time: "09:30 AM – 12:30 PM",
      venue: "Examination Hall B1, VFSTR",
      seatRange: "Row B, Desk 18",
      daysRemaining: 73,
      syllabusOverview: "Stacks, Queues, Linked Lists, Trees, AVL/Red-Black Trees, Heaps, Graph Traversals, Shortest Paths",
      reportingTime: "09:00 AM",
    },
    {
      id: "EX-06",
      code: "DMS-25MT202",
      subject: "Discrete Mathematical Structures (Summative Theory)",
      examType: "Summative Assessment (Lecture-Based End Semester)",
      date: "28 November 2026",
      rawDate: "2026-11-28T09:30:00",
      time: "09:30 AM – 12:30 PM",
      venue: "Examination Hall A2, VFSTR",
      seatRange: "Row E, Desk 31",
      daysRemaining: 75,
      syllabusOverview: "Mathematical Logic, Predicates, Set Theory, Relations, Functions, Recurrence Relations, Graph Theory",
      reportingTime: "09:00 AM",
    },
    {
      id: "EX-07",
      code: "OOPS-25CS204",
      subject: "Object Oriented Programming Java (Summative Theory)",
      examType: "Summative Assessment (Lecture-Based End Semester)",
      date: "04 December 2026",
      rawDate: "2026-12-04T09:30:00",
      time: "09:30 AM – 12:30 PM",
      venue: "Examination Hall A1, VFSTR",
      seatRange: "Row F, Desk 12",
      daysRemaining: 77,
      syllabusOverview: "OOP Principles, Inheritance, Polymorphism, Interfaces, Packages, Multithreading, Exception Handling, Collections Framework",
      reportingTime: "09:00 AM",
    },
    {
      id: "EX-08",
      code: "DBMS-25CS203",
      subject: "Database Management System (Summative Theory)",
      examType: "Summative Assessment (Lecture-Based End Semester)",
      date: "01 December 2026",
      rawDate: "2026-12-01T09:30:00",
      time: "09:30 AM – 12:30 PM",
      venue: "Examination Hall B3, VFSTR",
      seatRange: "Row C, Desk 27",
      daysRemaining: 80,
      syllabusOverview: "Relational Data Model, ER Modeling, SQL, Normalization (1NF to BCNF), Transaction Processing, Concurrency Control, Indexing",
      reportingTime: "09:00 AM",
    },
    {
      id: "EX-09",
      code: "AI-24CS302",
      subject: "Artificial Intelligence (Summative Theory)",
      examType: "Summative Assessment (Lecture-Based End Semester)",
      date: "24 November 2026",
      rawDate: "2026-11-24T09:30:00",
      time: "09:30 AM – 12:30 PM",
      venue: "Examination Hall A1, VFSTR",
      seatRange: "Row A, Desk 09",
      daysRemaining: 82,
      syllabusOverview: "Search Strategies (BFS, DFS, A*), Knowledge Representation, Propositional Logic, Probabilistic Reasoning, Machine Learning Basics",
      reportingTime: "09:00 AM",
    },
  ],
};
