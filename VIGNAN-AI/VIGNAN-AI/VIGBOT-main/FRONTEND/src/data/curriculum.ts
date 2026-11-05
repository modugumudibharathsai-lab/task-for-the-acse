export interface CourseCategory {
  name: string;
  completedCredits: number;
  totalRequiredCredits: number;
  description: string;
  coursesDone: string[];
  pendingCourses: string[];
}

export const CURRICULUM_DATA: {
  programme: string;
  totalDegreeCredits: number;
  completedCredits: number;
  currentSemesterCredits: number;
  remainingCredits: number;
  sourceAgent: string;
  categories: CourseCategory[];
} = {
  programme: "B.Tech Computer Science & Engineering (Section 7)",
  totalDegreeCredits: 160,
  completedCredits: 78,
  currentSemesterCredits: 23,
  remainingCredits: 59,
  sourceAgent: "Curriculum Engine - Section 7",
  categories: [
    {
      name: "Core Engineering",
      completedCredits: 48,
      totalRequiredCredits: 72,
      description: "Fundamental Computer Science theory, algorithms, and systems",
      coursesDone: [
        "Data Structures (DS-25CS201, 4 credits)",
        "Discrete Mathematical Structures (DMS-25MT202, 3 credits)",
        "Database Management System (DBMS-25CS203, 4 credits)",
        "Object Oriented Programming Through Java (OOPS-25CS204, 4 credits)",
        "Digital Logic design (DLD-25CS205, 3 credits)",
        "Theory of Computation (4 credits)",
      ],
      pendingCourses: [
        "Compiler Design (4 credits, Sem 5)",
        "Computer Networks (4 credits, Sem 5)",
        "Distributed Systems & Cloud (4 credits, Sem 6)",
      ],
    },
    {
      name: "Professional & Advanced Electives",
      completedCredits: 14,
      totalRequiredCredits: 30,
      description: "Specialized tracks in AI/ML, Data Engineering, and Systems",
      coursesDone: [
        "Artificial Intelligence (AI-24CS302, 3 credits)",
        "Data Wrangling and Visualization (DW-25CS202, 2 credits)",
        "Cloud Fundamentals (3 credits)",
        "Full-Stack Web Architectures (3 credits)",
      ],
      pendingCourses: [
        "Deep Learning & Generative AI (3 credits, Sem 5)",
        "Natural Language Processing (3 credits, Sem 6)",
        "Big Data Analytics (3 credits, Sem 6)",
      ],
    },
    {
      name: "Laboratory & Practical Implementation",
      completedCredits: 10,
      totalRequiredCredits: 18,
      description: "Hands-on implementation and system software laboratories",
      coursesDone: [
        "Data Structures Lab (DS-25CS201-P, 1.5 credits)",
        "Java & OOP Lab (OOPS-25CS204-P, 1.5 credits)",
        "DBMS Practical Lab (DBMS-25CS203-P, 1.5 credits)",
        "Digital Logic Simulation Lab (1.5 credits)",
      ],
      pendingCourses: [
        "Computer Networks Lab (2 credits, Sem 5)",
        "AI Innovation & Capstone Lab (2 credits, Sem 6)",
      ],
    },
    {
      name: "Humanities & Management",
      completedCredits: 6,
      totalRequiredCredits: 12,
      description: "Ethics, professional communication, and entrepreneurship",
      coursesDone: [
        "Technical English & Communication (2 credits)",
        "Universal Human Values & Professional Ethics (2 credits)",
        "Constitution of India (2 credits)",
      ],
      pendingCourses: [
        "Technology Economics & Startups (2 credits, Sem 5)",
        "Intellectual Property Rights (2 credits, Sem 6)",
      ],
    },
    {
      name: "Internship & Capstone Project",
      completedCredits: 0,
      totalRequiredCredits: 28,
      description: "Industrial summer internship and senior year capstone project",
      coursesDone: [],
      pendingCourses: [
        "Industrial Summer Internship (4 credits, Sem 6)",
        "Capstone Project Phase I (6 credits, Sem 7)",
        "Capstone Project Phase II & Defense (10 credits, Sem 8)",
      ],
    },
  ],
};
