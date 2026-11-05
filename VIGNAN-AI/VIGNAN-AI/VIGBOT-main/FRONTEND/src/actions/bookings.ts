"use server";

import { getDb } from "../lib/db-provider";
import { revalidatePath } from "next/cache";

import { getBackendUrl } from "../lib/backend-url";
const BACKEND_BASE_URL = getBackendUrl();

export interface Facility {
  id: number;
  name: string;
  type: string;
  description: string;
  capacity: number;
  image_url: string;
}

export interface Booking {
  id: number;
  facility_id: number;
  student_id: string;
  date: string;
  start_time: string;
  end_time: string;
  purpose: string;
  status: string;
}

export async function getFacilities(): Promise<Facility[]> {
  try {
    const res = await fetch(`${BACKEND_BASE_URL}/community/facilities`, { cache: 'no-store' });
    if (res.ok) {
      const data = await res.json();
      if (data.success && Array.isArray(data.facilities)) {
        return data.facilities;
      }
    }
  } catch (backendError) {
    console.warn("Backend fetch failed for facilities, attempting local fallback:", backendError);
  }

  try {
    const db = getDb();
    if (!db) return [];
    const stmt = db.prepare("SELECT * FROM facilities");
    const records = stmt.all() as Facility[];
    db.close();
    return records;
  } catch (error) {
    console.error("Failed to fetch facilities:", error);
    return [];
  }
}

export async function getBookingsForFacility(facilityId: number, date: string): Promise<Booking[]> {
  try {
    const res = await fetch(`${BACKEND_BASE_URL}/community/bookings?facility_id=${facilityId}&date=${date}`, { cache: 'no-store' });
    if (res.ok) {
      const data = await res.json();
      if (data.success && Array.isArray(data.bookings)) {
        return data.bookings;
      }
    }
  } catch (backendError) {
    console.warn("Backend fetch failed for bookings, attempting local fallback:", backendError);
  }

  try {
    const db = getDb();
    if (!db) return [];
    const stmt = db.prepare("SELECT * FROM bookings WHERE facility_id = ? AND date = ? AND status = 'confirmed'");
    const records = stmt.all(facilityId, date) as Booking[];
    db.close();
    return records;
  } catch (error) {
    console.error("Failed to fetch bookings:", error);
    return [];
  }
}

export async function createBooking(data: {
  facility_id: number;
  student_id: string;
  date: string;
  start_time: string;
  end_time: string;
  purpose: string;
}): Promise<{ success: boolean; message: string }> {
  try {
    const res = await fetch(`${BACKEND_BASE_URL}/community/bookings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (res.ok) {
      const json = await res.json();
      if (json.success) {
        revalidatePath("/");
        return { success: true, message: "Booking confirmed!" };
      }
    }
  } catch (backendError) {
    console.warn("Backend create failed for booking, attempting local fallback:", backendError);
  }

  try {
    const db = getDb();
    if (!db) return { success: false, message: "Database unavailable" };
    // Check for double booking
    const checkStmt = db.prepare(`
      SELECT * FROM bookings 
      WHERE facility_id = ? 
      AND date = ? 
      AND status = 'confirmed'
      AND (
        (start_time <= ? AND end_time > ?) OR
        (start_time < ? AND end_time >= ?) OR
        (start_time >= ? AND end_time <= ?)
      )
    `);
    
    const existing = checkStmt.get(
      data.facility_id, 
      data.date, 
      data.start_time, data.start_time,
      data.end_time, data.end_time,
      data.start_time, data.end_time
    );

    if (existing) {
      db.close();
      return { success: false, message: "Time slot is already booked." };
    }

    const insertStmt = db.prepare(`
      INSERT INTO bookings (facility_id, student_id, date, start_time, end_time, purpose, status)
      VALUES (?, ?, ?, ?, ?, ?, 'confirmed')
    `);

    insertStmt.run(
      data.facility_id,
      data.student_id,
      data.date,
      data.start_time,
      data.end_time,
      data.purpose
    );
    db.close();

    revalidatePath("/");
    return { success: true, message: "Booking confirmed!" };
  } catch (error) {
    console.error("Failed to create booking:", error);
    return { success: false, message: "Failed to create booking. Please try again." };
  }
}
