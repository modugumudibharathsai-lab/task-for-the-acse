# Frontend Integration Guide: Connecting to VIGBOT Backend

This document details how any frontend (such as the Next.js application in `FRONTEND/` or a frontend running on another laptop) connects to the **VIGBOT Backend API**.

---

## 1. Backend Service Details

- **Base API URL:** `http://localhost:8000/api/v1` (or `http://<BACKEND-LAPTOP-IP>:8000/api/v1` when calling across LAN)
- **Interactive Swagger Docs:** `http://localhost:8000/docs`
- **OpenAPI Contract:** `http://localhost:8000/api/v1/openapi.json`
- **Authentication:** Bearer JWT Token (`Authorization: Bearer <token>`)

---

## 2. Test Accounts for Frontend Testing

| Field | Student 1 (Default Test Account) | Student 2 (Boundary Isolation Test) |
| :--- | :--- | :--- |
| **Username** | `24cse001` | `24cse002` |
| **Password** | `student123` | `student123` |
| **Full Name** | Asha Reddy | Rahul Verma |
| **Roll Number** | `24CSE001` | `24CSE002` |
| **Attendance State** | Digital Electronics: 68.0% (Needs 14 classes for 75%) | Data Structures: 70.0% (Needs 8 classes for 75%) |

---

## 3. Core API Endpoints

### A. Authentication
`POST /api/v1/auth/login`
```json
// Request:
{
  "username": "24cse001",
  "password": "student123"
}

// Response:
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer",
  "expires_in": 86400,
  "student_id": "cccccccc-0000-0000-0000-000000000001",
  "roll_no": "24CSE001",
  "full_name": "Asha Reddy",
  "programme_code": "BTCSE"
}
```

### B. Student Profile
`GET /api/v1/me`
*Headers: `Authorization: Bearer <token>`*
Returns current authenticated student's profile, GPA, and branch.

### C. Create Conversation
`POST /api/v1/conversations`
*Headers: `Authorization: Bearer <token>`*
```json
{ "title": "Academic Assistance" }
```

### D. Send Message & Receive VIGBOT Response
`POST /api/v1/conversations/{conversation_id}/messages`
*Headers: `Authorization: Bearer <token>`*
```json
// Request:
{
  "content": "What is my attendance in Digital Electronics?",
  "language": "en"
}

// Response:
{
  "message_id": "msg-8f921a",
  "conversation_id": "conv-3a10b4",
  "sender_role": "VIGBOT",
  "content": "Your attendance in **Digital Electronics (CS302)** is **68.0%** (34 out of 50 classes attended).\n\n⚠️ **Status: Below Mandatory 75% Threshold**\n• Classes needed: You must attend the **next 14 consecutive classes** without absence to reach 75%.\n• Deadline: Condonation cut-off date is **2026-11-15**.\n• Feasibility: Recovery is mathematically feasible before term instruction ends.",
  "category": "PERSONAL_DATA",
  "source_agent": "Attendance System",
  "citations": [],
  "structured_card": {
    "type": "attendance",
    "title": "Digital Electronics (CS302)",
    "subtitle": "Faculty: Prof. K. Raman",
    "badge": "68.0% Attendance",
    "badgeVariant": "amber",
    "data": {
      "courseCode": "CS302",
      "courseTitle": "Digital Electronics",
      "currentPct": 68.0,
      "classesHeld": 50,
      "classesAttended": 34,
      "classesNeeded": 14,
      "deadline": "2026-11-15",
      "isAtRisk": true
    },
    "actionLabel": "Apply for Medical Condonation",
    "actionIntent": "service:condonation"
  },
  "is_distress": false,
  "suggested_follow_ups": [
    "When is the next Digital Electronics lecture?",
    "When is the second formative assessment?",
    "What is the policy for medical condonation?"
  ],
  "routed_by": "rules",
  "created_at": "2026-09-11T19:35:00Z"
}
```
*(Note: `routed_by` indicates which routing layer handled the request: `"rules"` for Tier 1 deterministic guardrails, `"classifier"` for Tier 2 local ML intent model, `"gemini"` for Tier 3 cloud fallback, or `"classifier_pipeline_test"` during dry-run testing).*


### E. Service Requests (Ticketing)
`POST /api/v1/service-requests`
*Headers: `Authorization: Bearer <token>`*
```json
{
  "category": "BONAFIDE_CERTIFICATE",
  "title": "Bonafide Certificate for Bus Pass",
  "description": "Requesting certificate for annual state transit pass concession."
}
```

---

## 4. Distress Signal Protocol (Crisis Handover)

When a student types distress phrases (e.g. *"I can't handle this anymore, I want to give up"*):
1. The backend response returns:
   - `is_distress: true`
   - `category: "DISTRESS_SUPPORT"`
   - `source_agent: "Distress Escalation & Counseling"`
   - `structured_card.type: "distress"`
2. The frontend should trigger the red **Distress Support Overlay** with emergency counseling hotline numbers (+91-98765-43210 and 14416).
