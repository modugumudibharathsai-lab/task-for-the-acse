"use server";

import { getDb } from "../lib/db-provider";

import { getBackendUrl } from "../lib/backend-url";
const BACKEND_BASE_URL = getBackendUrl();

export async function getMarketplaceListings() {
  try {
    const res = await fetch(`${BACKEND_BASE_URL}/community/marketplace`, {
      cache: 'no-store'
    });
    if (res.ok) {
      const json = await res.json();
      if (json.success && Array.isArray(json.data)) {
        return { success: true, data: json.data };
      }
    }
  } catch (backendError) {
    console.warn("Backend fetch failed for marketplace, attempting local fallback:", backendError);
  }

  try {
    const db = getDb();
    if (!db) return { success: true, data: [] };
    const records = db.prepare("SELECT * FROM marketplace_listings ORDER BY created_at DESC").all();
    db.close();
    return { success: true, data: records };
  } catch (error: any) {
    console.error("Error fetching marketplace listings:", error);
    return { success: false, error: error.message };
  }
}

export async function createMarketplaceListing(studentId: string, title: string, category: string, price: number) {
  try {
    const res = await fetch(`${BACKEND_BASE_URL}/community/marketplace`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        student_id: studentId,
        title,
        category,
        price
      })
    });
    if (res.ok) {
      const json = await res.json();
      if (json.success) {
        return { success: true, id: json.id };
      }
    }
  } catch (backendError) {
    console.warn("Backend create failed for marketplace, attempting local fallback:", backendError);
  }

  try {
    const db = getDb();
    if (!db) return { success: false, error: "Database unavailable" };
    const info = db.prepare("INSERT INTO marketplace_listings (student_id, title, category, price) VALUES (?, ?, ?, ?)")
                   .run(studentId, title, category, price);
    db.close();
    return { success: true, id: info.lastInsertRowid };
  } catch (error: any) {
    console.error("Error creating marketplace listing:", error);
    return { success: false, error: error.message };
  }
}
