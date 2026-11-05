export interface ServiceRequest {
  id: string;
  category: "Certificate" | "Grievance" | "Mentor Meeting" | "Academic Support" | "Issue Report";
  title: string;
  studentId: string;
  studentName: string;
  description: string;
  priority: "Low" | "Medium" | "High" | "Urgent";
  status: "Submitted" | "Preparing request" | "Forwarded to Student Services" | "Human review required" | "Resolved";
  submittedAt: string;
  assignedDept: string;
  sourceAgent: string;
  trackingToken: string;
}

export const INITIAL_SERVICES: ServiceRequest[] = [
  {
    id: "SR-8921",
    category: "Certificate",
    title: "Bonafide Certificate for Visa / Internship Application",
    studentId: "251FA04E13",
    studentName: "Aman Kumar",
    description: "Requesting an official bonafide statement indicating enrollment in 5th Semester B.Tech CSE for summer internship verification.",
    priority: "Medium",
    status: "Forwarded to Student Services",
    submittedAt: "08 Sep 2026, 11:20 AM",
    assignedDept: "Academic Registrar Division",
    sourceAgent: "Service Requests",
    trackingToken: "TRK-SR-8921-CSE",
  },
  {
    id: "SR-8742",
    category: "Mentor Meeting",
    title: "Semester 5 Mid-Term Academic & Attendance Review",
    studentId: "251FA04E13",
    studentName: "Aman Kumar",
    description: "Discussion regarding consecutive attendance strategy for Digital Electronics and elective selection for Semester 6.",
    priority: "High",
    status: "Forwarded to Student Services",
    submittedAt: "05 Sep 2026, 03:15 PM",
    assignedDept: "Faculty Mentorship Cell",
    sourceAgent: "Service Requests",
    trackingToken: "TRK-SR-8742-MEN",
  },
];
