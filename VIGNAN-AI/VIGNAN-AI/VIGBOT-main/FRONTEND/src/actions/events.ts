"use server";

import { getDb } from "../lib/db-provider";

import { getBackendUrl } from "../lib/backend-url";
const BACKEND_BASE_URL = getBackendUrl();

export async function getEventRegistrations(studentId: string) {
  try {
    const res = await fetch(`${BACKEND_BASE_URL}/community/events?student_id=${studentId}`, { cache: 'no-store' });
    if (res.ok) {
      const data = await res.json();
      if (data.success && Array.isArray(data.events)) {
        return { success: true, data: data.events };
      }
    }
  } catch (backendError) {
    console.warn("Backend fetch failed for events:", backendError);
  }

  try {
    const db = getDb();
    if (!db) return { success: true, data: [] };
    const records = db.prepare("SELECT * FROM event_registrations WHERE student_id = ?").all(studentId);
    db.close();
    return { success: true, data: records };
  } catch (error: any) {
    console.error("Error fetching event registrations:", error);
    return { success: false, error: error.message };
  }
}

export async function registerForEvent(studentId: string, eventName: string) {
  try {
    const res = await fetch(`${BACKEND_BASE_URL}/community/events/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ student_id: studentId, event_name: eventName })
    });
    if (res.ok) {
      const data = await res.json();
      if (data.success) {
        return { success: true, id: data.id, qrCode: `QR_${studentId}_${Date.now()}` };
      }
    }
  } catch (backendError) {
    console.warn("Backend register failed for event:", backendError);
  }

  try {
    const db = getDb();
    if (!db) return { success: false, error: "Database unavailable" };
    const qrCode = `QR_${studentId}_${Date.now()}`;
    const info = db.prepare("INSERT INTO event_registrations (student_id, event_name, qr_code) VALUES (?, ?, ?)")
                   .run(studentId, eventName, qrCode);
    db.close();
    return { success: true, id: info.lastInsertRowid, qrCode };
  } catch (error: any) {
    console.error("Error registering for event:", error);
    return { success: false, error: error.message };
  }
}
