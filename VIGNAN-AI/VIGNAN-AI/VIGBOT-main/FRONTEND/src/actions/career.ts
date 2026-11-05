"use server";

import { getDb } from "../lib/db-provider";



export async function getResumeData(studentId: string) {
  try {
    const db = getDb();
    const record = db.prepare("SELECT * FROM resumes WHERE student_id = ? ORDER BY created_at DESC LIMIT 1").get(studentId);
    db.close();
    return { success: true, data: record || null };
  } catch (error: any) {
    console.error("Error fetching resume data:", error);
    return { success: false, error: error.message };
  }
}

export async function saveResumeData(studentId: string, skills: string, projects: string) {
  try {
    const db = getDb();
    
    // Check if exists
    const existing = db.prepare("SELECT id FROM resumes WHERE student_id = ?").get(studentId);
    let info;
    if (existing) {
      info = db.prepare("UPDATE resumes SET skills = ?, projects = ? WHERE student_id = ?")
               .run(skills, projects, studentId);
    } else {
      info = db.prepare("INSERT INTO resumes (student_id, skills, projects) VALUES (?, ?, ?)")
               .run(studentId, skills, projects);
    }
    db.close();
    return { success: true };
  } catch (error: any) {
    console.error("Error saving resume data:", error);
    return { success: false, error: error.message };
  }
}
