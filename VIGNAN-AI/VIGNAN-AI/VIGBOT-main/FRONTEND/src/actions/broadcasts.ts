"use server";

import { getDb } from "../lib/db-provider";
import { mockBroadcasts } from '../data/adminMockData';

import { getBackendUrl } from "../lib/backend-url";
const BACKEND_BASE_URL = getBackendUrl();

export async function getActiveBroadcasts() {
  try {
    const res = await fetch(`${BACKEND_BASE_URL}/community/broadcasts`, { cache: 'no-store' });
    if (res.ok) {
      const data = await res.json();
      if (data.success && Array.isArray(data.broadcasts)) {
        return { success: true, broadcasts: data.broadcasts };
      }
    }
  } catch (backendError) {
    console.warn("Backend fetch failed for broadcasts, attempting local fallback:", backendError);
  }

  try {
    const db = getDb();
    if (!db) return { success: true, broadcasts: mockBroadcasts.filter(b => b.is_active === 1) };
    const broadcasts = db.prepare('SELECT * FROM broadcast_alerts WHERE is_active = 1 ORDER BY timestamp DESC').all();
    db.close();
    return { success: true, broadcasts };
  } catch (error: any) {
    console.error("Broadcast Fetch Error:", error);
    console.log("Falling back to static mock data");
    return { success: true, broadcasts: mockBroadcasts.filter(b => b.is_active === 1) };
  }
}

export async function getAllBroadcasts() {
  try {
    const res = await fetch(`${BACKEND_BASE_URL}/community/broadcasts`, { cache: 'no-store' });
    if (res.ok) {
      const data = await res.json();
      if (data.success && Array.isArray(data.broadcasts)) {
        return { success: true, broadcasts: data.broadcasts };
      }
    }
  } catch (backendError) {
    console.warn("Backend fetch failed for broadcasts:", backendError);
  }

  try {
    const db = getDb();
    if (!db) return { success: true, broadcasts: mockBroadcasts };
    const broadcasts = db.prepare('SELECT * FROM broadcast_alerts ORDER BY timestamp DESC').all();
    db.close();
    return { success: true, broadcasts };
  } catch (error: any) {
    return { success: true, broadcasts: mockBroadcasts };
  }
}

export async function toggleBroadcastStatus(id: number, isActive: boolean) {
  try {
    const db = getDb();
    if (!db) return { success: false, error: "Database unavailable" };
    db.prepare('UPDATE broadcast_alerts SET is_active = ? WHERE id = ?').run(isActive ? 1 : 0, id);
    db.close();
    return { success: true };
  } catch (error: any) {
    return { success: false, error: error.message };
  }
}

export async function deleteBroadcast(id: number) {
  try {
    const db = getDb();
    if (!db) return { success: false, error: "Database unavailable" };
    db.prepare('DELETE FROM broadcast_alerts WHERE id = ?').run(id);
    db.close();
    return { success: true };
  } catch (error: any) {
    return { success: false, error: error.message };
  }
}

export async function createBroadcast(message: string, type: string) {
  try {
    const db = getDb();
    if (!db) return { success: false, error: "Database unavailable" };
    db.prepare('INSERT INTO broadcast_alerts (message, type, is_active) VALUES (?, ?, 1)').run(message, type);
    db.close();
    return { success: true };
  } catch (error: any) {
    return { success: false, error: error.message };
  }
}
