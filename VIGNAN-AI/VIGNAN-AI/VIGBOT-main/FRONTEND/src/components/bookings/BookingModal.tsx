"use client";

import { getBackendUrl } from "@/lib/backend-url";


import { useState, useEffect } from "react";
import { X, Calendar as CalendarIcon, Clock, AlertCircle } from "lucide-react";
import { Facility, Booking, getBookingsForFacility, createBooking } from "@/actions/bookings";

interface BookingModalProps {
  facility: Facility;
  isOpen: boolean;
  onClose: () => void;
}

const TIME_SLOTS = [
  "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"
];

export function BookingModal({ facility, isOpen, onClose }: BookingModalProps) {
  const [selectedDate, setSelectedDate] = useState<string>("");
  const [selectedTime, setSelectedTime] = useState<string>("");
  const [purpose, setPurpose] = useState<string>("");
  const [existingBookings, setExistingBookings] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ text: string, type: 'error' | 'success' } | null>(null);

  // When date changes, fetch bookings to find available slots
  useEffect(() => {
    if (selectedDate && facility.id) {
      setLoading(true);
      getBookingsForFacility(facility.id, selectedDate).then(bookings => {
        setExistingBookings(bookings);
        setLoading(false);
        // Reset selected time if it's now booked
        if (selectedTime) {
          const isBooked = bookings.some(b => b.start_time === selectedTime);
          if (isBooked) setSelectedTime("");
        }
      });
    } else {
      setExistingBookings([]);
    }
  }, [selectedDate, facility.id]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDate || !selectedTime || !purpose) {
      setMessage({ text: "Please fill in all fields", type: 'error' });
      return;
    }

    setLoading(true);
    
    // Calculate end time (1 hour later)
    const hour = parseInt(selectedTime.split(':')[0]);
    const endTime = `${(hour + 1).toString().padStart(2, '0')}:00`;

    let res: { success: boolean; message: string } = { success: false, message: "Failed to create booking." };
    try {
      res = await createBooking({
        facility_id: facility.id,
        student_id: "251FA04E13",
        date: selectedDate,
        start_time: selectedTime,
        end_time: endTime,
        purpose
      });
    } catch (e) {
      console.warn("createBooking server action failed:", e);
    }

    if (!res?.success) {
      try {
        const backendUrl = getBackendUrl();
        const postRes = await fetch(`${backendUrl}/community/bookings`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            facility_id: facility.id,
            student_id: "251FA04E13",
            date: selectedDate,
            start_time: selectedTime,
            end_time: endTime,
            purpose
          })
        });
        if (postRes.ok) {
          const json = await postRes.json();
          if (json?.success) {
            res = { success: true, message: "Booking confirmed!" };
          }
        }
      } catch (e) {
        console.error("Direct booking error:", e);
      }
    }

    if (res.success) {
      setMessage({ text: res.message, type: 'success' });
      setTimeout(() => {
        onClose();
        setMessage(null);
        setSelectedDate("");
        setSelectedTime("");
        setPurpose("");
      }, 1500);
    } else {
      setMessage({ text: res.message, type: 'error' });
    }
    setLoading(false);
  };

  const getTodayString = () => {
    const today = new Date();
    return today.toISOString().split('T')[0];
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="bg-white rounded-2xl w-full max-w-md overflow-hidden shadow-2xl">
        <div className="flex justify-between items-center p-6 border-b border-slate-100">
          <div>
            <h2 className="text-xl font-semibold text-slate-800">Book Facility</h2>
            <p className="text-sm text-slate-500">{facility.name}</p>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-slate-100 rounded-full transition-colors">
            <X className="w-5 h-5 text-slate-500" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          {message && (
            <div className={`p-3 rounded-lg flex items-start gap-3 text-sm ${
              message.type === 'error' ? 'bg-red-50 text-red-700' : 'bg-emerald-50 text-emerald-700'
            }`}>
              <AlertCircle className="w-5 h-5 flex-shrink-0" />
              <p>{message.text}</p>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Select Date</label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <CalendarIcon className="w-5 h-5 text-slate-400" />
              </div>
              <input
                type="date"
                min={getTodayString()}
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Select Time (1 Hour Slot)</label>
            {!selectedDate ? (
              <p className="text-sm text-slate-500 italic">Please select a date first to view availability.</p>
            ) : (
              <div className="grid grid-cols-3 gap-2">
                {TIME_SLOTS.map(slot => {
                  const isBooked = existingBookings.some(b => b.start_time === slot);
                  const isSelected = selectedTime === slot;
                  
                  return (
                    <button
                      key={slot}
                      type="button"
                      disabled={isBooked}
                      onClick={() => setSelectedTime(slot)}
                      className={`py-2 text-sm rounded-lg border transition-all flex items-center justify-center gap-1 ${
                        isBooked 
                          ? "bg-slate-50 border-slate-200 text-slate-400 cursor-not-allowed opacity-60" 
                          : isSelected 
                            ? "bg-blue-600 border-blue-600 text-white shadow-md shadow-blue-500/20" 
                            : "bg-white border-slate-200 text-slate-700 hover:border-blue-500 hover:text-blue-600"
                      }`}
                    >
                      <Clock className="w-3 h-3" /> {slot}
                    </button>
                  );
                })}
              </div>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Purpose</label>
            <textarea
              value={purpose}
              onChange={(e) => setPurpose(e.target.value)}
              placeholder="E.g., Club meeting, Group study..."
              className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none h-24"
              required
            />
          </div>

          <div className="pt-2">
            <button
              type="submit"
              disabled={loading || !selectedDate || !selectedTime || !purpose}
              className="w-full bg-blue-600 text-white font-medium py-2.5 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2 shadow-sm shadow-blue-500/30"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                "Confirm Booking"
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
