export interface StudentAdvisorContact {
  name: string;
  email: string;
  cabin: string;
  phone: string;
}

export interface StudentProfile {
  id: string;
  name: string;
  programme: string;
  department: string;
  academicYear: string;
  semester: number;
  admissionYear: number;
  email: string;
  phone: string;
  cgpa: number;
  mentor: StudentAdvisorContact;
  classTeacher?: StudentAdvisorContact;
  counsellor?: StudentAdvisorContact;
  hod?: StudentAdvisorContact;
  authStatus: "Authenticated";
  securityLabel: string;
  securityToken: string;
  sourceAgent: string;
}

export const CURRENT_STUDENT: StudentProfile = {
  id: "251FA04E13",
  name: "Aman Kumar",
  programme: "B.Tech CSE (Section 7, Room N-312)",
  department: "Computer Science & Engineering",
  academicYear: "2025–26",
  semester: 3,
  admissionYear: 2024,
  email: "251fa04e13@vignan.ac.in",
  phone: "+91 98765 43210",
  cgpa: 8.09,
  mentor: {
    name: "Mr. T. Latesh Babu",
    email: "latesh.babu@vignan.ac.in",
    cabin: "N-312 Faculty Staff Room / CSE Department, VFSTR",
    phone: "+91 94901 23456",
  },
  classTeacher: {
    name: "Mr. T. Latesh Babu",
    email: "latesh.babu@vignan.ac.in",
    cabin: "N-312 Faculty Staff Room / CSE Department, VFSTR",
    phone: "+91 94901 23456",
  },
  counsellor: {
    name: "Dr. Radhika Sharma",
    email: "radhika.sharma@vignan.ac.in",
    cabin: "Student Welfare Block, Room SW-104",
    phone: "+91 98480 12345",
  },
  hod: {
    name: "Dr. S V Phani Kumar",
    email: "hod_cse@vignan.ac.in",
    cabin: "CSE Department HOD Suite, Room H-201",
    phone: "+91 94401 23456",
  },
  authStatus: "Authenticated",
  securityLabel: "Viewing your verified Section-7 student record",
  securityToken: "RLS-VFSTR-251FA04E13-VERIFIED",
  sourceAgent: "Student Profile - Section 7",
};
