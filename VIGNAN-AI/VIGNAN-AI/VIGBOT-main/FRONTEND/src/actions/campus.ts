"use server";

import { getDb } from "../lib/db-provider";

import { getBackendUrl } from "../lib/backend-url";
const BACKEND_BASE_URL = getBackendUrl();

export async function getCampusLocations() {
  try {
    const res = await fetch(`${BACKEND_BASE_URL}/community/locations`, { cache: 'no-store' });
    if (res.ok) {
      const data = await res.json();
      if (data.success && Array.isArray(data.locations)) {
        return {
          success: true,
          data: data.locations.map((record: any) => ({
            id: record.location_id,
            name: record.room_number,
            building: record.block,
            floor: record.floor,
            type: record.type,
            description: record.description,
            latitude: record.latitude,
            longitude: record.longitude,
            features: typeof record.features === "string" ? JSON.parse(record.features || "[]") : (record.features || [])
          }))
        };
      }
    }
  } catch (backendError) {
    console.warn("Backend fetch failed for campus locations:", backendError);
  }

  try {
    const db = getDb();
    if (!db) throw new Error("No local database");
    const records = db.prepare("SELECT location_id as id, room_number as name, block as building, floor, type, description, latitude, longitude, features FROM campus_locations ORDER BY room_number ASC").all();
    db.close();

    const parsedRecords = records.map((record: any) => ({
      ...record,
      features: record.features ? JSON.parse(record.features) : []
    }));

    return { success: true, data: parsedRecords };
  } catch (error: any) {
    const fallbackData = [
      { id: 'LOC_MAIN', name: 'N-Block', building: 'Main Block', floor: 'G to 4', type: 'Administrative', description: 'Main administrative and CSE department block', latitude: null, longitude: null, features: [] },
      { id: 'LOC_LIB', name: 'Central Library', building: 'Library', floor: 'G to 2', type: 'Facility', description: '24/7 AC Library with thousands of books', latitude: null, longitude: null, features: [] },
      { id: 'LOC_HOSTEL_A', name: 'Boys Hostel A', building: 'Hostel A', floor: 'G to 5', type: 'Hostel', description: 'First year boys accommodation', latitude: null, longitude: null, features: [] },
      { id: 'LOC_LAB_1', name: 'AI/ML Lab', building: 'N-Block', floor: '3rd Floor', type: 'Academic', description: 'High-performance computing lab equipped with GPUs', latitude: null, longitude: null, features: [] },
      { id: 'LOC_CAFE', name: 'Main Canteen', building: 'Cafeteria', floor: 'Ground', type: 'Food', description: 'Multicuisine food court open till 9 PM', latitude: null, longitude: null, features: [] }
    ];
    return { success: true, data: fallbackData };
  }
}
