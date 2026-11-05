"use server";

import { getDb } from "../lib/db-provider";



export async function getGamificationData(studentId: string) {
  try {
    const db = getDb();
    const row = db.prepare("SELECT * FROM gamification WHERE student_id = ?").get(studentId) as any;
    db.close();
    if (row) {
      return {
        points: row.points,
        badges: JSON.parse(row.badges_json || "[]")
      };
    }
    return { points: 0, badges: [] };
  } catch (error) {
    console.error("Error fetching gamification data:", error);
    return { points: 0, badges: [] };
  }
}

