/**
 * API Client for connecting Frontend to VIGBOT FastAPI Backend.
 * Uses NEXT_PUBLIC_BACKEND_URL or defaults to the deployed VIGBOT API.
 */

import { getBackendUrl } from "./backend-url";

const ACTIVE_BACKEND_BASE_URL = "/api/v1";
// Bypass Vercel's 10s Serverless timeout by calling Render directly from the client.
const BACKEND_BASE_URL = getBackendUrl();

export interface BackendTokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  student_id: string;
  roll_no: string;
  full_name: string;
  programme_code: string;
}

export interface ProfileResponse {
  roll_no: string;
  cgpa?: number;
  fee_outstanding?: number;
  overall_attendance_pct?: number;
}

export interface DashboardResponse {
  profile?: ProfileResponse;
  timetable?: Array<{
    day_of_week: string;
    time_slot?: string;
    course_title: string;
    course_code: string;
    room_no: string;
    faculty_name: string;
    slot_type?: string;
  }>;
}

export interface BackendMessageResponse {
  message_id: string;
  conversation_id: string;
  sender_role: string;
  content: string;
  category?: string;
  source_agent?: string;
  citations: Array<{
    title: string;
    clause: string;
    effective_date: string;
    summary?: string;
  }>;
  structured_card?: unknown;
  is_distress: boolean;
  suggested_follow_ups?: string[];
  llm_provider?: string;
  model_used?: string;
  used_fallback?: boolean;
  routed_by?: "rules" | "classifier" | "gemini" | "classifier_pipeline_test" | string | null;
  redirect_path?: string;
  action?: {
    type: string;
    label: string;
    target: string;
    route?: string;
  };
  created_at: string;
}

class VigbotApiClient {
  private token: string | null = null;
  private activeConversationId: string | null = null;

  constructor() {
    if (typeof window !== "undefined") {
      this.token = (localStorage.getItem("vigbot_token") || localStorage.getItem("agent65_token"));
      this.activeConversationId = (localStorage.getItem("vigbot_conv_id") || localStorage.getItem("agent65_conv_id"));
    }
  }

  setToken(token: string) {
    this.token = token;
    if (typeof window !== "undefined") {
      localStorage.setItem("vigbot_token", token);
    }
  }

  getToken(): string | null {
    if (!this.token && typeof window !== "undefined") {
      this.token = (localStorage.getItem("vigbot_token") || localStorage.getItem("agent65_token"));
    }
    return this.token;
  }

  async login(username: string, password?: string): Promise<BackendTokenResponse> {
    if (!username || !username.trim()) {
      throw new Error("Registration number is required.");
    }
    if (!password) {
      throw new Error("Password is required.");
    }
    const resp = await fetch(`${BACKEND_BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: username.trim().toUpperCase(), password }),
    });
    if (!resp.ok) {
      const errJson = await resp.json().catch(() => null);
      const detail = errJson?.detail || "Invalid registration number or password.";
      throw new Error(detail);
    }
    const data: BackendTokenResponse = await resp.json();
    this.setToken(data.access_token);
    this.activeConversationId = null;
    if (typeof window !== "undefined") {
      localStorage.removeItem("vigbot_conv_id");
      localStorage.removeItem("agent65_conv_id");
      localStorage.setItem("vigbot_active_student", data.roll_no || username.toUpperCase().trim());
    }
    return data;
  }

  async checkStudentStatus(rollNo: string): Promise<{ status: "activated" | "unactivated" | "unknown"; masked_email?: string; message: string }> {
    const resp = await fetch(`${BACKEND_BASE_URL}/auth/check-status`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ roll_no: rollNo.trim().toUpperCase() }),
    });
    if (!resp.ok) {
      return {
        status: "unknown",
        message: "If this registration number belongs to an active VFSTR student, please verify your details or contact the helpdesk."
      };
    }
    return await resp.json();
  }

  async requestActivationOtp(rollNo: string): Promise<{ success: boolean; message: string; masked_email?: string; expires_in_seconds?: number; requires_admin_verification?: boolean }> {
    const resp = await fetch(`${BACKEND_BASE_URL}/auth/activation/request-otp`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ roll_no: rollNo.trim().toUpperCase() }),
    });
    const data = await resp.json().catch(() => ({}));
    if (!resp.ok) {
      throw new Error(data.detail || "Could not dispatch verification code. Please check your registration number.");
    }
    return data;
  }

  async verifyAndActivate(rollNo: string, otp: string, newPassword: string, confirmPassword: string): Promise<BackendTokenResponse> {
    const resp = await fetch(`${BACKEND_BASE_URL}/auth/activation/verify-and-activate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        roll_no: rollNo.trim().toUpperCase(),
        otp: otp.trim(),
        new_password: newPassword,
        confirm_password: confirmPassword,
      }),
    });
    const data = await resp.json().catch(() => ({}));
    if (!resp.ok) {
      throw new Error(data.detail || "Account activation failed. Please check your verification code.");
    }
    this.setToken(data.access_token);
    this.activeConversationId = null;
    if (typeof window !== "undefined") {
      localStorage.removeItem("vigbot_conv_id");
      localStorage.setItem("vigbot_active_student", data.roll_no || rollNo.toUpperCase().trim());
    }
    return data;
  }

  async requestPasswordResetOtp(rollNo: string): Promise<{ success: boolean; message: string; masked_email?: string }> {
    const resp = await fetch(`${BACKEND_BASE_URL}/auth/password-reset/request-otp`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ roll_no: rollNo.trim().toUpperCase() }),
    });
    const data = await resp.json().catch(() => ({}));
    if (!resp.ok) {
      throw new Error(data.detail || "Password reset request failed. Please verify your registration number.");
    }
    return data;
  }

  async verifyAndResetPassword(rollNo: string, otp: string, newPassword: string, confirmPassword: string): Promise<{ success: boolean; message: string }> {
    const resp = await fetch(`${BACKEND_BASE_URL}/auth/password-reset/verify-and-reset`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        roll_no: rollNo.trim().toUpperCase(),
        otp: otp.trim(),
        new_password: newPassword,
        confirm_password: confirmPassword,
      }),
    });
    const data = await resp.json().catch(() => ({}));
    if (!resp.ok) {
      throw new Error(data.detail || "Password reset failed. Please check your verification code.");
    }
    return data;
  }

  logout() {
    this.token = null;
    this.activeConversationId = null;
    if (typeof window !== "undefined") {
      localStorage.removeItem("vigbot_token"); localStorage.removeItem("agent65_token");
      localStorage.removeItem("vigbot_conv_id"); localStorage.removeItem("agent65_conv_id");
      localStorage.removeItem("vigbot_active_student"); localStorage.removeItem("agent65_active_student");
    }
  }

  async ensureAuthenticated(): Promise<string | null> {
    let token = this.getToken();
    if (!token) {
      const savedRoll = typeof window !== "undefined" ? (localStorage.getItem("vigbot_active_student") || localStorage.getItem("agent65_active_student")) : null;
      if (savedRoll) {
        // Use correct password format for the demo
        const defaultPwd = "aman@" + savedRoll;
        const loginData = await this.login(savedRoll, defaultPwd);
        if (loginData) {
          token = loginData.access_token;
        }
      }
    }
    return token;
  }

  async getProfile(): Promise<ProfileResponse | null> {
    let token = await this.ensureAuthenticated();
    if (!token) return null;
    try {
      let resp = await fetch(`${BACKEND_BASE_URL}/me`, {
        headers: { 
          Authorization: `Bearer ${token}` 
        },
      });
      if (resp.status === 401) {
        this.token = null;
        if (typeof window !== "undefined") localStorage.removeItem("vigbot_token"); localStorage.removeItem("agent65_token");
        token = await this.ensureAuthenticated();
        if (token) {
          resp = await fetch(`${BACKEND_BASE_URL}/me`, {
            headers: { 
              Authorization: `Bearer ${token}` 
            },
          });
        }
      }
      if (!resp.ok) return null;
      return await resp.json();
    } catch {
      return null;
    }
  }

  async getDashboard(): Promise<DashboardResponse | null> {
    let token = await this.ensureAuthenticated();
    if (!token) return null;
    try {
      let resp = await fetch(`${BACKEND_BASE_URL}/student/dashboard`, {
        headers: { 
          Authorization: `Bearer ${token}` 
        },
      });
      if (resp.status === 401) {
        this.token = null;
        if (typeof window !== "undefined") localStorage.removeItem("vigbot_token"); localStorage.removeItem("agent65_token");
        token = await this.ensureAuthenticated();
        if (token) {
          resp = await fetch(`${BACKEND_BASE_URL}/student/dashboard`, {
            headers: { 
              Authorization: `Bearer ${token}` 
            },
          });
        }
      }
      if (!resp.ok) return null;
      return await resp.json();
    } catch {
      return null;
    }
  }

  async getOrCreateConversation(forceNew: boolean = false): Promise<string> {
    if (!forceNew && this.activeConversationId) return this.activeConversationId;

    const token = await this.ensureAuthenticated();
    if (token) {
      try {
        const resp = await fetch(`${BACKEND_BASE_URL}/conversations`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`
          },
          body: JSON.stringify({ title: "Helpdesk Session" }),
        });
        if (resp.ok) {
          const conv = await resp.json();
          this.activeConversationId = conv.conversation_id;
          if (typeof window !== "undefined") {
            localStorage.setItem("vigbot_conv_id", conv.conversation_id);
          }
          return conv.conversation_id;
        }
      } catch (e) {
        console.warn("Could not create conversation on backend:", e);
      }
    }
    return "local-conversation-session";
  }

  async sendMessage(
    content: string,
    language: string = "en",
    selectedModel: "3B" | "8B" = "8B"
  ): Promise<BackendMessageResponse | null> {
    let token = await this.ensureAuthenticated();
    let convId = await this.getOrCreateConversation();

    if (!token || convId === "local-conversation-session") {
      const savedRoll = typeof window !== "undefined" ? (localStorage.getItem("vigbot_active_student") || localStorage.getItem("agent65_active_student")) : null;
      if (savedRoll) {
        const defaultPwd = "aman@" + savedRoll;
        token = await this.login(savedRoll, defaultPwd).then((t) => t?.access_token || null);
        convId = await this.getOrCreateConversation(true);
      }
      if (!token || convId === "local-conversation-session") {
        return null;
      }
    }

    try {
      let resp = await fetch(
        `${BACKEND_BASE_URL}/conversations/${convId}/messages`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`
          },
            body: JSON.stringify({ content, language, selected_model: selectedModel }),
        }
      );

      // Self-healing: if session or conversation expired/reset on backend (404/401)
      if (resp.status === 404 || resp.status === 401) {
        console.info("[VIGBOT] Stale conversation or token detected, auto-healing with fresh session...");
        this.activeConversationId = null;
        if (resp.status === 401) this.token = null;
        if (typeof window !== "undefined") {
          localStorage.removeItem("vigbot_conv_id"); localStorage.removeItem("agent65_conv_id");
          if (resp.status === 401) localStorage.removeItem("vigbot_token"); localStorage.removeItem("agent65_token");
        }
        token = await this.ensureAuthenticated();
        convId = await this.getOrCreateConversation(true);

        resp = await fetch(
          `${BACKEND_BASE_URL}/conversations/${convId}/messages`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`
            },
            body: JSON.stringify({ content, language, selected_model: selectedModel }),
          }
        );
      }

      if (!resp.ok) {
        const errorBody = await resp.text().catch(() => "");
        console.error(`[VIGBOT] Backend returned HTTP ${resp.status}`, errorBody);
        return null;
      }
      return await resp.json();
    } catch (e) {
      console.warn("[VIGBOT] Backend call failed:", e);
      return null;
    }
  }

  async createServiceRequest(category: string, title: string, description: string): Promise<unknown | null> {
    let token = await this.ensureAuthenticated();
    if (!token) return null;
    try {
      let resp = await fetch(`${BACKEND_BASE_URL}/service-requests`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ category, title, description }),
      });
      if (resp.status === 401) {
        this.token = null;
        if (typeof window !== "undefined") localStorage.removeItem("vigbot_token"); localStorage.removeItem("agent65_token");
        token = await this.ensureAuthenticated();
        if (token) {
          resp = await fetch(`${BACKEND_BASE_URL}/service-requests`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`
            },
            body: JSON.stringify({ category, title, description }),
          });
        }
      }
      if (resp.ok) return await resp.json();
    } catch (e) {
      console.warn("Could not post service request to backend:", e);
    }
    return null;
  }

  async sendFeedback(
    conversationId: string | null | undefined,
    messageId: string | null | undefined,
    rating: "up" | "down",
    comment?: string,
    messagesContext?: Array<{ role: string; content: string }>,
    responseText?: string
  ): Promise<{ status: string; saved_for_training: boolean; rating: string; message: string } | null> {
    const token = await this.ensureAuthenticated();
    if (!token) return null;
    try {
      const convId = conversationId || this.activeConversationId || "local-conversation-session";
      const msgId = messageId || `msg-${Date.now()}`;
      const resp = await fetch(
        `${BACKEND_BASE_URL}/conversations/${convId}/messages/${msgId}/feedback`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`
          },
          body: JSON.stringify({
            rating,
            comment,
            messages: messagesContext,
            response_text: responseText,
          }),
        }
      );
      if (resp.ok) {
        return await resp.json();
      }
    } catch (e) {
      console.warn("[VIGBOT] Feedback submission failed:", e);
    }
    return null;
  }
}

export const apiClient = new VigbotApiClient();
