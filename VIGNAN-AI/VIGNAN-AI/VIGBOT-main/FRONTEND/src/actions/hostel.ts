"use server";

import { getDb } from "../lib/db-provider";

import { getBackendUrl } from "../lib/backend-url";
const BACKEND_BASE_URL = getBackendUrl();

export async function getHostelRequests(studentId: string) {
  try {
    const res = await fetch(`${BACKEND_BASE_URL}/community/hostel?student_id=${studentId}`, { cache: 'no-store' });
    if (res.ok) {
      const data = await res.json();
      if (data.success && Array.isArray(data.requests)) {
        return { success: true, data: data.requests };
      }
    }
  } catch (backendError) {
    console.warn("Backend fetch failed for hostel requests:", backendError);
  }

  try {
    const db = getDb();
    if (!db) return { success: true, data: [] };
    const records = db.prepare("SELECT * FROM hostel_requests WHERE student_id = ? ORDER BY created_at DESC").all(studentId);
    db.close();
    return { success: true, data: records };
  } catch (error: any) {
    console.error("Error fetching hostel requests:", error);
    return { success: false, error: error.message };
  }
}

export async function createHostelRequest(studentId: string, type: string, details: string) {
  try {
    const res = await fetch(`${BACKEND_BASE_URL}/community/hostel`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ student_id: studentId, type, details })
    });
    if (res.ok) {
      const data = await res.json();
      if (data.success) {
        return { success: true, id: data.id };
      }
    }
  } catch (backendError) {
    console.warn("Backend create failed for hostel request:", backendError);
  }

  try {
    const db = getDb();
    if (!db) return { success: false, error: "Database unavailable" };
    const info = db.prepare("INSERT INTO hostel_requests (student_id, type, details) VALUES (?, ?, ?)")
      .run(studentId, type, details);
    db.close();
    return { success: true, id: info.lastInsertRowid };
  } catch (error: any) {
    console.error("Error creating hostel request:", error);
    return { success: false, error: error.message };
  }
}
