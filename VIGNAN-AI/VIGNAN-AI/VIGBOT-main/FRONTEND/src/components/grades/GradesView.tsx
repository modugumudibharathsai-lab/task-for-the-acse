import React, { useEffect, useState } from "react";
import { GraduationCap, TrendingUp, BookOpen, AlertCircle } from "lucide-react";
import { getAcademicRecords } from "@/actions/academic";
import { useStudent } from "@/context/StudentContext";
import { CURRENT_STUDENT } from "@/data/student";

export const GradesView = () => {
  const { studentData } = useStudent();
  const student = studentData?.profile || CURRENT_STUDENT;
  const [records, setRecords] = useState<any[]>([]);

  useEffect(() => {
    const fetchRecords = async () => {
      const res = await getAcademicRecords(student.id);
      if (res.success) {
        setRecords((res.data as any[]) || []);
      }
    };
    fetchRecords();
  }, [student.id]);

  const latestCgpa = records.length > 0 ? records[records.length - 1].cgpa : 0.0;
  const totalCredits = records.length > 0 ? records[records.length - 1].credits_completed : 0;

  return (
    <div className="space-y-6 animate-in fade-in zoom-in-95 duration-300">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Academic Progress</h2>
          <p className="text-sm text-muted-foreground">Track your CGPA, credits, and semester results.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="rounded-xl border border-border bg-card p-6 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-emerald-100 p-2 text-emerald-600">
              <GraduationCap className="h-5 w-5" />
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Current CGPA</p>
              <h3 className="text-2xl font-bold">{latestCgpa.toFixed(2)}</h3>
            </div>
          </div>
        </div>
        <div className="rounded-xl border border-border bg-card p-6 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-blue-100 p-2 text-blue-600">
              <BookOpen className="h-5 w-5" />
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Credits Completed</p>
              <h3 className="text-2xl font-bold">{totalCredits} / 160</h3>
            </div>
          </div>
        </div>
        <div className="rounded-xl border border-border bg-card p-6 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-violet-100 p-2 text-violet-600">
              <TrendingUp className="h-5 w-5" />
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Academic Standing</p>
              <h3 className="text-xl font-bold text-emerald-600">Excellent</h3>
            </div>
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-border bg-card shadow-sm overflow-hidden">
        <div className="border-b border-border bg-muted/30 px-6 py-4">
          <h3 className="font-semibold text-foreground">Semester Breakdown</h3>
        </div>
        <div className="p-0">
          <table className="w-full text-left text-sm">
            <thead className="bg-muted/50 text-muted-foreground">
              <tr>
                <th className="px-6 py-3 font-medium">Semester</th>
                <th className="px-6 py-3 font-medium">Credits Earned</th>
                <th className="px-6 py-3 font-medium">CGPA</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {records.length > 0 ? (
                records.map((r, i) => (
                  <tr key={r.id} className="hover:bg-muted/30 transition-colors">
                    <td className="px-6 py-4 font-medium">Semester {r.semester}</td>
                    <td className="px-6 py-4">{r.credits_completed}</td>
                    <td className="px-6 py-4 font-semibold">{r.cgpa.toFixed(2)}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={3} className="px-6 py-8 text-center text-muted-foreground">
                    No academic records found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
