export interface FeeItem {
  head: string;
  demand: number;
  paid: number;
  outstanding: number;
  dueDate: string;
  status: "Paid" | "Partial" | "Overdue";
}

export const FEES_DATA: {
  totalDemand: number;
  totalPaid: number;
  outstanding: number;
  dueDate: string;
  sourceAgent: string;
  breakdown: FeeItem[];
  recentReceipts: {
    receiptNo: string;
    date: string;
    amount: number;
    mode: string;
    status: string;
  }[];
} = {
  totalDemand: 120000,
  totalPaid: 92000,
  outstanding: 28000,
  dueDate: "30 September 2026",
  sourceAgent: "Fee Status",
  breakdown: [
    {
      head: "Tuition Fee",
      demand: 90000,
      paid: 70000,
      outstanding: 20000,
      dueDate: "30 Sep 2026",
      status: "Partial",
    },
    {
      head: "Examination Fee",
      demand: 5000,
      paid: 5000,
      outstanding: 0,
      dueDate: "15 Aug 2026",
      status: "Paid",
    },
    {
      head: "Hostel & Amenities",
      demand: 20000,
      paid: 12000,
      outstanding: 8000,
      dueDate: "30 Sep 2026",
      status: "Partial",
    },
    {
      head: "Library & Digital Resources",
      demand: 5000,
      paid: 5000,
      outstanding: 0,
      dueDate: "15 Aug 2026",
      status: "Paid",
    },
  ],
  recentReceipts: [
    {
      receiptNo: "REC-2026-08149",
      date: "14 Jul 2026",
      amount: 70000,
      mode: "UPI / NetBanking",
      status: "Verified & Cleared",
    },
    {
      receiptNo: "REC-2026-09221",
      date: "12 Aug 2026",
      amount: 22000,
      mode: "HDFC Payment Gateway",
      status: "Verified & Cleared",
    },
  ],
};
