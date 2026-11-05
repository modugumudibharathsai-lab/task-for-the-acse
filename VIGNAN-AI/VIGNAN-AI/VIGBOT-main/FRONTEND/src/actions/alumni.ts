"use server";

import { getDb } from "../lib/db-provider";

import { getBackendUrl } from "../lib/backend-url";
const BACKEND_BASE_URL = getBackendUrl();

export async function getAlumniMentors() {
  try {
    const res = await fetch(`${BACKEND_BASE_URL}/community/alumni`, { cache: 'no-store' });
    if (res.ok) {
      const data = await res.json();
      if (data.success && Array.isArray(data.mentors)) {
        return data.mentors;
      }
    }
  } catch (backendError) {
    console.warn("Backend fetch failed for alumni mentors:", backendError);
  }

  try {
    const db = getDb();
    if (!db) return [];
    const rows = db.prepare("SELECT * FROM alumni_mentors").all();
    db.close();
    return rows;
  } catch (error) {
    console.error("Error fetching alumni mentors:", error);
    return [];
  }
}
