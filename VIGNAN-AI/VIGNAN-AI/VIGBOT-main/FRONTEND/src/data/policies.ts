export interface PolicyItem {
  id: string;
  title: string;
  category: "Academic" | "Examination" | "Attendance" | "Registration" | "Conduct";
  shortDescription: string;
  effectiveDate: string;
  sourceAgent: string;
  keyPoints: string[];
  fullText: string;
}

export const POLICIES_DATA: PolicyItem[] = [
  {
    id: "POL-01",
    title: "Institutional Attendance Policy",
    category: "Attendance",
    shortDescription: "Mandatory 75% threshold rule, medical condonation criteria, and detention rules.",
    effectiveDate: "01 July 2026",
    sourceAgent: "University Policies",
    keyPoints: [
      "Minimum Attendance: Every student must maintain at least 75% attendance in each registered theory and laboratory course.",
      "Condonation Window: Attendance between 65% and 74.9% can be condoned by the Dean (Academics) upon presentation of a valid Government Medical Certificate within 5 working days of recovery.",
      "Severe Detention: Students falling below 65% are strictly debarred from appearing in the End-Semester Examination and must re-register for the course.",
      "Institutional Duty Leave: Official representation in inter-collegiate sports, hackathons, or academic competitions grants duty-leave credits upon prior HoD approval.",
    ],
    fullText: `1. Purpose & Scope: This policy sets the academic attendance obligations across all undergraduate and postgraduate engineering programs. Regular attendance is an essential component of the instructional framework.\n\n2. Minimum Threshold: A student is expected to attain 100% attendance. However, taking into account unpreventable contingencies such as illness, a minimum aggregate attendance of 75% is mandatory in each individual course.\n\n3. Condonation Provisions: In exceptional circumstances (hospitalization, contagious illness, family bereavement), students with attendance between 65% and 74.9% may apply for attendance condonation accompanied by an authorized physician certificate.\n\n4. Debarment & Consequence: Any student with attendance lower than 65% is awarded an 'F-Detained' grade and must repeat the course during summer terms or supplementary sessions.`,
  },
  {
    id: "POL-02",
    title: "University Examination & Evaluation Policy",
    category: "Examination",
    shortDescription: "End-semester rules, hall ticket eligibility, biometric entry, and re-evaluation procedures.",
    effectiveDate: "15 June 2026",
    sourceAgent: "University Policies",
    keyPoints: [
      "Admit Card & Identification: Digital hall tickets with verified QR codes are mandatory; physical university identity card must be carried.",
      "Reporting Window: Examination gates open 30 minutes prior to scheduled start. No entry permitted beyond 15 minutes after paper commencement.",
      "Passing Threshold: 40% aggregate required in theory examinations and 50% in continuous laboratory assessments.",
      "Re-evaluation & Transparency: Students may request answer script photocopy inspection within 7 days of result declaration upon payment of standard scrutiny fees.",
    ],
    fullText: `1. General Rules: All university end-semester examinations are conducted under centralized Controller of Examinations (CoE) supervision.\n\n2. Malpractice Policy: Possessing smart watches, mobile devices, unauthorized formula sheets, or communication devices results in immediate confiscation and referral to the Unfair Means Committee (UMC).\n\n3. Supplementary Opportunities: Students failing to secure the minimum passing grade (P) may register for the Make-Up examination session held in January and July.`,
  },
  {
    id: "POL-03",
    title: "Continuous Assessment & Grading Policy",
    category: "Academic",
    shortDescription: "Weightage breakdown between Formative Assessments (FA), Mid-Semester, and Final Exams.",
    effectiveDate: "01 August 2026",
    sourceAgent: "University Policies",
    keyPoints: [
      "Internal Assessment (40%): Comprises 2 Formative Assessments (15% each) and Continuous Laboratory/Assignment evaluation (10%).",
      "Mid-Semester Exam (20%): Centralized mid-term evaluation covering first 2.5 modules.",
      "End-Semester Examination (40%): Comprehensive summative assessment covering all 5 syllabus modules.",
      "Relative & Absolute Grading: Core engineering disciplines adhere to a 10-point Letter Grade scale ranging from O (Outstanding, 10.0) to F (Fail, 0.0).",
    ],
    fullText: `Assessment Framework: The university follows Choice Based Credit System (CBCS) guidelines. Internal evaluation is formative and diagnostic, ensuring timely feedback before summative semester assessments.`,
  },
  {
    id: "POL-04",
    title: "Course Registration & Credit Policy",
    category: "Registration",
    shortDescription: "Add/drop semester deadlines, minimum credit loading (18) and maximum credit cap (28).",
    effectiveDate: "20 July 2026",
    sourceAgent: "University Policies",
    keyPoints: [
      "Semester Registration: All students must complete pre-registration through the student portal 14 days before semester commencement.",
      "Credit Limits: Normal semester load is 22–24 credits; minimum permissible load is 18 credits; academic probation caps registration at 20 credits.",
      "Add/Drop Grace Period: Course substitutions or drop requests are accepted during the first 10 days of instructional commencement without academic record penalty.",
    ],
    fullText: `Registration Guidelines: Prerequisite compliance is verified automatically by the enrollment subsystem. Faculty advisors must electronically sign off on elective choices prior to timetable locking.`,
  },
  {
    id: "POL-05",
    title: "Academic Progress & Promotion Policy",
    category: "Academic",
    shortDescription: "Degree completion timeline, standing requirements, and CGPA minimums.",
    effectiveDate: "01 May 2026",
    sourceAgent: "University Policies",
    keyPoints: [
      "Degree Duration: Normal B.Tech span is 4 years (8 semesters); maximum permissible completion window is 6 consecutive academic years.",
      "Promotion Criteria to Year 3: Must earn at least 40 credits from First Year and have no more than 3 active backlogs.",
      "Dean's Honor List: Awarded to students achieving semester SGPA >= 9.25 with zero backlogs and 85%+ overall attendance.",
    ],
    fullText: `Academic standing is reviewed after each semester examination cycle. Remedial mentoring is mandated for students whose CGPA falls below 6.0.`,
  },
];
