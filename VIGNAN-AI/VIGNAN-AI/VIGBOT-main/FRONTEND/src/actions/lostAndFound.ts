"use server";

import { getDb } from "../lib/db-provider";

import { getBackendUrl } from "../lib/backend-url";
const BACKEND_BASE_URL = getBackendUrl();

export async function fetchLostAndFoundItems(filterType: 'all' | 'lost' | 'found' = 'all') {
  try {
    const res = await fetch(`${BACKEND_BASE_URL}/community/lost-and-found?filter_type=${filterType}`, {
      cache: 'no-store'
    });
    if (res.ok) {
      const data = await res.json();
      if (data.success && Array.isArray(data.items)) {
        return { success: true, items: data.items };
      }
    }
  } catch (backendError) {
    console.warn("Backend fetch failed for lost-and-found, attempting local fallback:", backendError);
  }

  // Local fallback (offline development)
  try {
    const db = getDb();
    if (!db) return { success: true, items: [] };
    let query = `SELECT * FROM lost_and_found WHERE status = 'open'`;
    const params = [];
    
    if (filterType !== 'all') {
      query += ` AND type = ?`;
      params.push(filterType);
    }
    
    query += ` ORDER BY date_posted DESC`;
    
    const items = db.prepare(query).all(...params);
    db.close();
    
    return { success: true, items };
  } catch (error) {
    console.error("Error fetching lost and found items:", error);
    return { success: false, error: "Failed to fetch items" };
  }
}

export async function reportLostAndFoundItem(
  studentId: string, 
  type: 'lost' | 'found', 
  title: string, 
  description: string, 
  tags: string, 
  contactInfo: string,
  imageUrl?: string
) {
  try {
    const res = await fetch(`${BACKEND_BASE_URL}/community/lost-and-found`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        student_id: studentId,
        type,
        title,
        description,
        tags: tags || "",
        contact_info: contactInfo,
        image_url: imageUrl || null
      })
    });
    if (res.ok) {
      const data = await res.json();
      if (data.success) {
        return { success: true, id: data.id };
      }
    }
    const errData = await res.json().catch(() => null);
    if (errData?.error) {
      console.error("Backend error reporting item:", errData.error);
    }
  } catch (backendError) {
    console.warn("Backend report failed, attempting local fallback:", backendError);
  }

  // Local fallback (offline development)
  try {
    const db = getDb();
    if (!db) return { success: false, error: "Database unavailable" };
    const datePosted = new Date().toISOString();
    const result = db.prepare(`
      INSERT INTO lost_and_found (student_id, type, title, description, tags, contact_info, status, date_posted, image_url)
      VALUES (?, ?, ?, ?, ?, ?, 'open', ?, ?)
    `).run(studentId, type, title, description, tags, contactInfo, datePosted, imageUrl || null);
    
    db.close();
    return { success: true, id: result.lastInsertRowid };
  } catch (error) {
    console.error("Error reporting item:", error);
    return { success: false, error: "Failed to report item" };
  }
}

export async function claimLostAndFoundItem(itemId: number, studentId: string) {
  try {
    const res = await fetch(`${BACKEND_BASE_URL}/community/lost-and-found/${itemId}/claim`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ student_id: studentId })
    });
    if (res.ok) {
      const data = await res.json();
      if (data.success) {
        return { success: true };
      }
    }
  } catch (backendError) {
    console.warn("Backend claim failed, attempting local fallback:", backendError);
  }

  // Local fallback
  try {
    const db = getDb();
    if (!db) return { success: false, error: "Database unavailable" };
    const item: any = db.prepare(`SELECT * FROM lost_and_found WHERE id = ?`).get(itemId);
    
    if (!item) {
      db.close();
      return { success: false, error: "Item not found" };
    }

    db.prepare(`
      UPDATE lost_and_found 
      SET status = 'claimed' 
      WHERE id = ?
    `).run(itemId);
    
    db.close();
    return { success: true };
  } catch (error) {
    console.error("Error claiming item:", error);
    return { success: false, error: "Failed to claim item" };
  }
}
