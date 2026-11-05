"use server";

import { getDb } from "../lib/db-provider";

import { getBackendUrl } from "../lib/backend-url";
const BACKEND_BASE_URL = getBackendUrl();

export async function getCampusPolls() {
  try {
    const res = await fetch(`${BACKEND_BASE_URL}/community/polls`, { cache: 'no-store' });
    if (res.ok) {
      const data = await res.json();
      if (data.success && Array.isArray(data.polls)) {
        return data.polls.map((row: any) => ({
          ...row,
          options: typeof row.options_json === "string" ? JSON.parse(row.options_json || "[]") : (row.options_json || [])
        }));
      }
    }
  } catch (backendError) {
    console.warn("Backend fetch failed for polls, attempting local fallback:", backendError);
  }

  try {
    const db = getDb();
    if (!db) return [];
    const rows = db.prepare("SELECT * FROM campus_polls WHERE is_active = 1").all();
    db.close();
    return rows.map((row: any) => ({
      ...row,
      options: JSON.parse(row.options_json || "[]")
    }));
  } catch (error) {
    console.error("Error fetching campus polls:", error);
    return [];
  }
}
