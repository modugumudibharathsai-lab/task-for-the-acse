"use client";

import React from "react";
import {
  Bell,
  X,
  AlertTriangle,
  Clock,
  FileText,
  Calendar,
  CheckCheck,
  ChevronRight,
} from "lucide-react";
import { NotificationItem } from "@/data/notifications";
import { useLanguage } from "@/context/LanguageContext";

interface NotificationsDrawerProps {
  isOpen: boolean;
  notifications: NotificationItem[];
  onClose: () => void;
  onMarkAllRead: () => void;
  onSelectNotification: (item: NotificationItem) => void;
}

export const NotificationsDrawer: React.FC<NotificationsDrawerProps> = ({
  isOpen,
  notifications,
  onClose,
  onMarkAllRead,
  onSelectNotification,
}) => {
  const { t, tDynamic } = useLanguage();
  if (!isOpen) return null;

  return (
    <div role="dialog" aria-modal="true" className="fixed inset-0 z-50 flex justify-end bg-slate-900/40 backdrop-blur-xs">
      <div className="relative w-full max-w-md h-full bg-card shadow-2xl border-l border-slate-200 flex flex-col animate-in slide-in-from-right duration-300">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-200 bg-gradient-to-r from-blue-50 to-white p-5">
          <div className="flex items-center gap-2">
            <Bell className="h-5 w-5 text-blue-600" />
            <h3 className="text-base font-bold text-foreground">{t.notificationsTitle || "Notifications"}</h3>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={onMarkAllRead}
              className="text-xs text-blue-600 hover:text-blue-700 font-medium flex items-center gap-1 cursor-pointer"
            >
              <CheckCheck className="h-3.5 w-3.5" />
              <span>{t.markAllRead || "Mark all read"}</span>
            </button>
            <button
              onClick={onClose}
              className="rounded-full p-1.5 text-slate-400 hover:bg-muted hover:text-foreground transition-colors cursor-pointer"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* List */}
        <div className="flex-1 overflow-y-auto overscroll-contain p-4 space-y-2.5 text-xs text-foreground">
          {notifications.map((item) => {
            const isUrgent = item.priority === "urgent";
            const isHigh = item.priority === "high";

            return (
              <div
                key={item.id}
                onClick={() => {
                  onSelectNotification(item);
                  onClose();
                }}
                className={`rounded-lg border p-4 transition-all cursor-pointer ${
                  !item.read
                    ? "bg-blue-50/40 border-blue-200/80 shadow-2xs font-medium"
                    : "bg-card border-slate-200 text-muted-foreground"
                }`}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <div className="flex items-center gap-1.5">
                    {!item.read && (
                      <span className="h-2 w-2 rounded-full bg-blue-600 shrink-0" />
                    )}
                    <span
                      className={`font-bold uppercase tracking-wider text-sm ${
                        isUrgent
                          ? "text-rose-700"
                          : isHigh
                          ? "text-amber-700"
                          : "text-blue-700"
                      }`}
                    >
                      {item.title}
                    </span>
                  </div>
                  <span className="text-sm text-slate-400 font-normal">
                    {item.timestamp}
                  </span>
                </div>

                <p className="text-xs text-foreground leading-relaxed mb-2">{item.message}</p>

                <div className="flex items-center justify-between pt-1 border-t border-slate-100/80 text-sm text-slate-400">
                  <span>From: {item.sourceAgent}</span>
                  <span className="text-blue-600 font-semibold flex items-center gap-0.5">
                    <span>{t.viewDetails}</span>
                    <ChevronRight className="h-3 w-3" />
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
