export interface SecurityLogItem {
  id: string;
  time: string;
  event: string;
  agent: string;
  status: "SUCCESS" | "FORWARDED" | "BLOCKED" | "VERIFIED";
  scope: string;
  details: string;
}

export const INITIAL_SECURITY_LOGS: SecurityLogItem[] = [
  {
    id: "SEC-LOG-01",
    time: "10:24 AM",
    event: "Student identity authenticated",
    agent: "Student Profile",
    status: "SUCCESS",
    scope: "UID: 251FA04E13",
    details: "Biometric SSO token validated. Row-Level Security policy enforced.",
  },
  {
    id: "SEC-LOG-02",
    time: "10:22 AM",
    event: "Attendance records queried",
    agent: "Attendance Engine",
    status: "SUCCESS",
    scope: "UID: 251FA04E13 (Own Record Only)",
    details: "Queried 4 subjects. Authorization check passed. Cross-tenant reads rejected.",
  },
  {
    id: "SEC-LOG-03",
    time: "10:20 AM",
    event: "Examination schedule retrieved",
    agent: "Examination Hub",
    status: "SUCCESS",
    scope: "UID: 251FA04E13",
    details: "Seating roll #42 in Hall A2 retrieved securely.",
  },
  {
    id: "SEC-LOG-04",
    time: "10:18 AM",
    event: "Student fee ledger retrieved",
    agent: "Fee Status Engine",
    status: "SUCCESS",
    scope: "UID: 251FA04E13",
    details: "Outstanding balance ₹28,000 fetched over encrypted mTLS channel.",
  },
  {
    id: "SEC-LOG-05",
    time: "10:15 AM",
    event: "Service request routed",
    agent: "Service Requests",
    status: "FORWARDED",
    scope: "UID: 251FA04E13",
    details: "Ticket #SR-8921 generated and enqueued with priority Medium.",
  },
  {
    id: "SEC-LOG-06",
    time: "10:02 AM",
    event: "Cross-student access attempt test",
    agent: "VIGBOT (Guardrail)",
    status: "BLOCKED",
    scope: "Foreign UID query attempt",
    details: "Row-Level Security rule dropped unauthorized foreign parameter. Only 251FA04E13 permissible.",
  },
];
