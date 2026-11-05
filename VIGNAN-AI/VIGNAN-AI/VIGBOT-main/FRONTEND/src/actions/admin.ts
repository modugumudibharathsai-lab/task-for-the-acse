"use server";

import { getDb } from "../lib/db-provider";
import { mockGrievances, mockClubApps, mockBookings, mockLostAndFound } from '../data/adminMockData';
import { getBackendUrl } from "../lib/backend-url";

const BACKEND_BASE_URL = getBackendUrl();

export async function adminLogin(username: string, passwordHash: string) {
  try {
    const res = await fetch(`${BACKEND_BASE_URL}/admin/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password: passwordHash })
    });
    if (res.ok) {
      const data = await res.json();
      if (data.success) {
        return { success: true, admin: data.admin, token: data.token };
      }
    }
  } catch (backendError) {
    console.warn("Backend admin login failed, attempting local fallback:", backendError);
  }

  try {
    const db = getDb();
    if (!db) {
      return { success: false, error: "Authentication service unavailable. Please check credentials." };
    }
    const stmt = db.prepare(`SELECT id, username, name, role, password_hash FROM admins WHERE username = ?`);
    const admin = stmt.get(username) as any;
    db.close();

    if (admin) {
      // In local mode, verify password or check hash
      if (admin.password_hash === passwordHash) {
        return {
          success: true,
          admin: { id: admin.id, username: admin.username, name: admin.name, role: admin.role },
          token: `local-token-${admin.id}`
        };
      }
    }
    return { success: false, error: "Invalid administrative credentials." };
  } catch (error) {
    console.error("Admin login error:", error);
    return { success: false, error: "Database error during login." };
  }
}

export async function fetchAllTickets(token?: string) {
  try {
    const headers: Record<string, string> = {};
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    const res = await fetch(`${BACKEND_BASE_URL}/admin/overview`, {
      cache: 'no-store',
      headers
    });
    if (res.ok) {
      const data = await res.json();
      if (data.success) {
        return {
          success: true,
          grievances: data.grievances || [],
          clubApps: data.clubApps || [],
          bookings: data.bookings || [],
          lostAndFound: data.lostAndFound || [],
          serviceRequests: data.service_requests || [],
          hostelRequests: data.hostelRequests || []
        };
      }
    }
  } catch (backendError) {
    console.warn("Backend fetch overview failed, attempting local fallback:", backendError);
  }

  try {
    const db = getDb();
    if (!db) {
      return {
        success: true,
        grievances: mockGrievances,
        clubApps: mockClubApps,
        bookings: mockBookings,
        lostAndFound: mockLostAndFound,
        serviceRequests: [],
        hostelRequests: []
      };
    }
    const grievances = db.prepare(`SELECT tracking_id as id, description, status, timestamp, withdrawal_reason, student_id FROM studentlife_grievance ORDER BY timestamp DESC`).all();
    const clubApps = db.prepare(`SELECT id, club_id, student_name, status, timestamp, withdrawal_reason, student_id FROM studentlife_club_application ORDER BY timestamp DESC`).all();
    const bookings = db.prepare(`SELECT id, facility_id, student_id, date, start_time, end_time, purpose, status FROM bookings ORDER BY date DESC, start_time DESC`).all();
    const lostAndFound = db.prepare(`SELECT id, student_id, type, title, description, tags, contact_info, status, date_posted, image_url FROM lost_and_found ORDER BY date_posted DESC`).all();
    let serviceRequests = [];
    try {
      serviceRequests = db.prepare(`SELECT * FROM service_requests ORDER BY created_at DESC`).all();
    } catch (e) { }

    db.close();
    return { success: true, grievances, clubApps, bookings, lostAndFound, serviceRequests, hostelRequests: [] };
  } catch (error) {
    return {
      success: true,
      grievances: mockGrievances,
      clubApps: mockClubApps,
      bookings: mockBookings,
      lostAndFound: mockLostAndFound,
      serviceRequests: [],
      hostelRequests: []
    };
  }
}

export async function updateTicketStatus(
  ticketId: string | number,
  type: 'club' | 'grievance' | 'booking' | 'lost_found' | 'service_request' | 'hostel',
  newStatus: string,
  token?: string
) {
  try {
    const endpoint = type === 'service_request'
      ? `${BACKEND_BASE_URL}/admin/service-requests/${ticketId}`
      : `${BACKEND_BASE_URL}/admin/tickets/${type}/${ticketId}`;

    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const res = await fetch(endpoint, {
      method: 'PATCH',
      headers,
      body: JSON.stringify({ status: newStatus })
    });
    if (res.ok) {
      const data = await res.json();
      if (data.success) return { success: true };
    }
  } catch (backendError) {
    console.warn("Backend ticket update failed, attempting local fallback:", backendError);
  }

  try {
    const db = getDb();
    if (!db) return { success: true };
    let stmt;

    if (type === 'grievance') {
      stmt = db.prepare(`UPDATE studentlife_grievance SET status = ? WHERE tracking_id = ?`);
    } else if (type === 'club') {
      stmt = db.prepare(`UPDATE studentlife_club_application SET status = ? WHERE id = ?`);
    } else if (type === 'booking') {
      stmt = db.prepare(`UPDATE bookings SET status = ? WHERE id = ?`);
    } else if (type === 'lost_found') {
      stmt = db.prepare(`UPDATE lost_and_found SET status = ? WHERE id = ?`);
    } else if (type === 'service_request') {
      stmt = db.prepare(`UPDATE service_requests SET status = ? WHERE service_request_id = ? OR request_no = ?`);
      const result = stmt.run(newStatus.toUpperCase(), ticketId, ticketId);
      db.close();
      return { success: result.changes > 0 };
    }

    if (stmt) {
      const result = stmt.run(newStatus, ticketId);
      db.close();
      return { success: result.changes > 0 };
    }
    db.close();
    return { success: false, error: "Invalid ticket type." };
  } catch (error) {
    return { success: false, error: "Failed to update ticket" };
  }
}

export async function deleteTicket(
  ticketId: string | number,
  type: 'club' | 'grievance' | 'booking' | 'lost_found' | 'service_request' | 'hostel',
  token?: string
) {
  try {
    const endpoint = type === 'service_request'
      ? `${BACKEND_BASE_URL}/admin/service-requests/${ticketId}`
      : `${BACKEND_BASE_URL}/admin/tickets/${type}/${ticketId}`;

    const headers: Record<string, string> = {};
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const res = await fetch(endpoint, {
      method: 'DELETE',
      headers
    });
    if (res.ok) {
      const data = await res.json();
      if (data.success) return { success: true };
    }
  } catch (backendError) {
    console.warn("Backend ticket deletion failed, attempting local fallback:", backendError);
  }

  try {
    const db = getDb();
    if (!db) return { success: true };
    let stmt;
    if (type === 'grievance') {
      stmt = db.prepare(`DELETE FROM studentlife_grievance WHERE tracking_id = ?`);
    } else if (type === 'club') {
      stmt = db.prepare(`DELETE FROM studentlife_club_application WHERE id = ?`);
    } else if (type === 'booking') {
      stmt = db.prepare(`DELETE FROM bookings WHERE id = ?`);
    } else if (type === 'lost_found') {
      stmt = db.prepare(`DELETE FROM lost_and_found WHERE id = ?`);
    } else if (type === 'service_request') {
      stmt = db.prepare(`DELETE FROM service_requests WHERE service_request_id = ? OR request_no = ?`);
      const result = stmt.run(ticketId, ticketId);
      db.close();
      return { success: result.changes > 0 };
    }
    if (stmt) {
      const result = stmt.run(ticketId);
      db.close();
      return { success: result.changes > 0 };
    }
    db.close();
    return { success: false, error: "Invalid ticket type." };
  } catch (error) {
    return { success: false, error: "Failed to delete ticket" };
  }
}

// -------------------------------------------------------------
// Cognitive Remediations & Gemini Governance Server Actions
// -------------------------------------------------------------
export async function fetchCognitiveRemediations(token?: string) {
  try {
    const headers: Record<string, string> = {};
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    const res = await fetch(`${BACKEND_BASE_URL}/admin/remediations`, {
      cache: 'no-store',
      headers
    });
    if (res.ok) {
      const data = await res.json();
      if (data.success) {
        return {
          success: true,
          summary: data.summary,
          remediations: data.remediations || [],
          recentFeedback: data.recent_feedback || []
        };
      }
    }
  } catch (error) {
    console.warn("fetchCognitiveRemediations failed:", error);
  }
  return {
    success: false,
    summary: { total_audited: 0, active_rules: 0, policy_protected: 0, inactive_rules: 0, raw_feedback_count: 0 },
    remediations: [],
    recentFeedback: []
  };
}

export async function updateRemediationStatus(remediationId: string, status: string, token?: string) {
  try {
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    const res = await fetch(`${BACKEND_BASE_URL}/admin/remediations/${remediationId}/status`, {
      method: 'PATCH',
      headers,
      body: JSON.stringify({ status })
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (error) {
    console.warn("updateRemediationStatus failed:", error);
  }
  return { success: false, error: "Network error updating remediation status." };
}

export async function deleteRemediationRule(remediationId: string, token?: string) {
  try {
    const headers: Record<string, string> = {};
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    const res = await fetch(`${BACKEND_BASE_URL}/admin/remediations/${remediationId}`, {
      method: 'DELETE',
      headers
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (error) {
    console.warn("deleteRemediationRule failed:", error);
  }
  return { success: false, error: "Network error deleting remediation rule." };
}

export async function fetchGeminiStatus(token?: string) {
  try {
    const headers: Record<string, string> = {};
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    const res = await fetch(`${BACKEND_BASE_URL}/admin/gemini/status`, {
      cache: 'no-store',
      headers
    });
    if (res.ok) {
      const data = await res.json();
      if (data.success) {
        return data;
      }
    }
  } catch (error) {
    console.warn("fetchGeminiStatus failed:", error);
  }
  return {
    success: false,
    enable_gemini: false,
    masked_api_key: "",
    has_key: false,
    active_model: "gemini-2.5-flash",
    available_models: ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash", "gemini-1.5-flash"],
    quota: {
      daily_requests_used: 0,
      daily_requests_limit: 1500,
      daily_requests_remaining: 1500,
      minute_requests_used: 0,
      minute_requests_limit: 15,
      minute_requests_remaining: 15,
      total_requests_all_time: 0,
      recent_calls: []
    }
  };
}

export async function updateGeminiConfig(config: { apiKey?: string; enableGemini?: boolean; model?: string }, token?: string) {
  try {
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    const res = await fetch(`${BACKEND_BASE_URL}/admin/gemini/config`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        api_key: config.apiKey,
        enable_gemini: config.enableGemini,
        model: config.model
      })
    });
    return await res.json();
  } catch (error) {
    return { success: false, error: `Failed to update Gemini config: ${String(error)}` };
  }
}

export async function pingGeminiConnection(token?: string) {
  try {
    const headers: Record<string, string> = {};
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    const res = await fetch(`${BACKEND_BASE_URL}/admin/gemini/ping`, {
      method: 'POST',
      headers
    });
    return await res.json();
  } catch (error) {
    return { success: false, error: `Ping failed: ${String(error)}` };
  }
}
