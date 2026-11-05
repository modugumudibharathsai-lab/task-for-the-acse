"use server";

import { getDb } from "../lib/db-provider";

export async function getAcademicRecords(studentId: string) {
  try {
    const db = getDb();
    if (!db) {
      return { success: true, data: [] };
    }
    const records = db.prepare("SELECT * FROM academic_records WHERE student_id = ? ORDER BY semester ASC").all(studentId);
    db.close();
    return { success: true, data: records };
  } catch (error: any) {
    console.error("Error fetching academic records:", error);
    return { success: false, error: error.message };
  }
}
