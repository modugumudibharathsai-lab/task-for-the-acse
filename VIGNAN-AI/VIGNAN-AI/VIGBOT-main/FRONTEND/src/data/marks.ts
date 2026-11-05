export interface AssessmentRecord {
  id: string;
  subjectCode: string;
  subjectName: string;
  assessmentType: string;
  marksObtained: number;
  maxMarks: number;
  percentage: number;
  date: string;
  weightagePct: number;
  classAveragePct: number;
  grade: string;
  feedback: string;
}

export const MARKS_DATA: {
  overallPercentage: number;
  gpa: number;
  sourceAgent: string;
  recentAssessments: AssessmentRecord[];
  upcomingAssessments: {
    title: string;
    subject: string;
    date: string;
    maxMarks: number;
    syllabus: string;
  }[];
} = {
  overallPercentage: 82,
  gpa: 8.42,
  sourceAgent: "Agents 33 & 34 (Marks & Assessments - Section 7)",
  recentAssessments: [
    {
      id: "AS-01",
      subjectCode: "DLD-25CS205",
      subjectName: "Digital Logic design",
      assessmentType: "Formative Assessment 1 (FA-1)",
      marksObtained: 19,
      maxMarks: 25,
      percentage: 76,
      date: "14 Aug 2026",
      weightagePct: 15,
      classAveragePct: 70,
      grade: "A",
      feedback: "Good grasp of logic minimization and Karnaugh maps; review synchronous counters.",
    },
    {
      id: "AS-02",
      subjectCode: "DS-25CS201",
      subjectName: "Data Structures",
      assessmentType: "Mid-Semester Assessment",
      marksObtained: 44,
      maxMarks: 50,
      percentage: 88,
      date: "22 Aug 2026",
      weightagePct: 30,
      classAveragePct: 76,
      grade: "A+",
      feedback: "Strong algorithmic complexity analysis; clean balanced tree implementations.",
    },
    {
      id: "AS-03",
      subjectCode: "OOPS-25CS204",
      subjectName: "Object Oriented Programming Through Java",
      assessmentType: "Lab Practical Assessment",
      marksObtained: 20,
      maxMarks: 20,
      percentage: 100,
      date: "28 Aug 2026",
      weightagePct: 10,
      classAveragePct: 82,
      grade: "O",
      feedback: "Exemplary implementation of Java multithreading, custom exceptions, and stream APIs.",
    },
    {
      id: "AS-04",
      subjectCode: "DBMS-25CS203",
      subjectName: "Database Management System",
      assessmentType: "Quiz 2 (SQL & Schema Normalization)",
      marksObtained: 23,
      maxMarks: 25,
      percentage: 92,
      date: "04 Sep 2026",
      weightagePct: 15,
      classAveragePct: 74,
      grade: "A+",
      feedback: "Excellent 3NF decomposition proofs and relational calculus queries.",
    },
  ],
  upcomingAssessments: [
    {
      title: "Second Formative Assessment (FA-2)",
      subject: "Digital Logic design",
      date: "15 Oct 2026",
      maxMarks: 25,
      syllabus: "Modules 3 & 4: Registers, Synchronous Counters, Memory Architecture",
    },
    {
      title: "Lab Practical Mid-Evaluation",
      subject: "Data Structures",
      date: "20 Oct 2026",
      maxMarks: 50,
      syllabus: "Graph algorithms (Dijkstra, Prim's) & Heap sort benchmarks",
    },
  ],
};
