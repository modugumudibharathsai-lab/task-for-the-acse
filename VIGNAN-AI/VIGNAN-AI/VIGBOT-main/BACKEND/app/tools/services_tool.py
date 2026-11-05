from typing import Dict, Any, Optional, Tuple
from app.database import DataRepository, DatabaseSession

def handle_service_request(
    session: DatabaseSession,
    category: str,
    title: str,
    description: str,
    priority: str = "NORMAL",
    instructions: Optional[str] = None
) -> Dict[str, Any]:
    record = DataRepository.create_service_request(session, {
        "category": category,
        "title": title,
        "description": description,
        "priority": priority
    })

    text_parts = [
        "✅ **Service Request Created Successfully**\n",
        f"• Request Tracking No: **{record['request_no']}**",
        f"• Category: **{record['category'].replace('_', ' ').title()}**",
        f"• Title: {record['title']}",
        f"• Assigned Office: **{record['assigned_office']}**",
        f"• Status: **{record['status']}**",
        f"• Estimated SLA Resolution: **{record['sla_due_date']}**\n",
    ]
    if instructions:
        text_parts.append(f"{instructions}\n")
    text_parts.append(f"You can track the progress of this request in your Services tab or quote reference `{record['request_no']}` at the Registrar desk.")
    text = "\n".join(text_parts)

    card_data = {
        "type": "service",
        "title": record["title"],
        "subtitle": f"Tracking ID: {record['request_no']}",
        "badge": record["status"],
        "badgeVariant": "green",
        "data": record,
        "actionLabel": "View Request Details",
        "actionIntent": f"service:{record['request_no']}"
    }

    return {
        "text": text,
        "record": record,
        "structured_card": card_data
    }

def handle_human_handover(
    session: DatabaseSession,
    target_office: str,
    reason: str,
    summary: str,
    urgency: str = "NORMAL"
) -> Dict[str, Any]:
    handover_no = f"HO-2026-{uuid_snip()}"
    text = (
        f"🤝 **Handover to Human Administrative Office Created**\n\n"
        f"Your query requires discretionary evaluation or human administrative review.\n"
        f"• Handover Reference: **{handover_no}**\n"
        f"• Target Office: **{target_office.replace('_', ' ').title()}**\n"
        f"• Reason: {reason}\n"
        f"• Urgency: **{urgency}**\n\n"
        f"The relevant academic officer has been notified with the context of your inquiry. You will receive an update in your notification feed."
    )

    card_data = {
        "type": "service",
        "title": f"Escalated to {target_office.replace('_', ' ').title()}",
        "subtitle": f"Reference: {handover_no}",
        "badge": f"{urgency} Escalation",
        "badgeVariant": "purple",
        "data": {
            "handoverNo": handover_no,
            "targetOffice": target_office,
            "reason": reason,
            "summary": summary
        }
    }

    return {
        "text": text,
        "handover_no": handover_no,
        "structured_card": card_data
    }

def uuid_snip() -> str:
    import uuid
    return uuid.uuid4().hex[:6].upper()


def resolve_service_subtype(query: str) -> Tuple[str, str, str, str]:
    """
    Resolves (category, title, description, instructions) for student service requests.
    Detects ID card, bonafide, transcript, NOC, fee receipt, concession, mentor, grievance, etc.
    """
    q_lower = query.lower()

    # 1. ID Card Replacement
    if any(k in q_lower for k in ["id card", "identity card", "lost card", "replacement card", "duplicate id", "duplicate card"]):
        return (
            "ID_CARD_REPLACEMENT",
            "Student ID Card Replacement",
            f"Request for duplicate/replacement student ID card: '{query}'",
            "📋 **Step-by-Step Procedure for ID Card Replacement:**\n"
            "1. Pay the ID card replacement fee of Rs. 150 at the University Cash Counter (Admin Block, Ground Floor).\n"
            "2. Note down your tracking ticket reference number above.\n"
            "3. Submit the payment counterfoil along with a passport photograph to the Registrar Student Affairs desk (Room G-04).\n"
            "4. Your duplicate biometric RFID identity card will be printed and issued within 3 working days."
        )

    # 2. Bonafide Certificate
    elif any(k in q_lower for k in ["bonafide", "study certificate", "bonafied"]):
        return (
            "BONAFIDE_CERTIFICATE",
            "Bonafide Certificate Application",
            f"Application for official bonafide study certificate: '{query}'",
            "📋 **Step-by-Step Procedure for Bonafide Certificate:**\n"
            "1. Your current semester registration and academic standing will be verified automatically.\n"
            "2. Academic Cell will generate the digitally signed certificate with official seal.\n"
            "3. Download the certificate from the student portal or collect the physical signed copy from Academic Cell within 24–48 hours."
        )

    # 3. Transcript / Grade Card
    elif any(k in q_lower for k in ["transcript", "transcripts", "grade card", "marksheet", "duplicate memo", "marks memo"]):
        return (
            "TRANSCRIPT_REQUEST",
            "Official Transcript / Grade Card Application",
            f"Request for official transcripts/grade memo: '{query}'",
            "📋 **Step-by-Step Procedure for Official Transcript / Grade Card:**\n"
            "1. Specify the academic semesters required and purpose (higher studies/visa).\n"
            "2. Pay the transcript processing fee (Rs. 200 per official sealed set) via the Finance Portal or Cash Desk.\n"
            "3. Examination Section (Controller of Examinations Office, Room 106) processes and issues the verified transcript within 5 working days."
        )

    # 4. No Objection Certificate (NOC)
    elif any(k in q_lower for k in ["noc", "no objection", "no-objection"]):
        return (
            "NOC_REQUEST",
            "No Objection Certificate (NOC) Application",
            f"Application for No Objection Certificate (NOC): '{query}'",
            "📋 **Step-by-Step Procedure for NOC:**\n"
            "1. Specify the purpose (Off-campus Internship, Passport Application, Research Project, Higher Education).\n"
            "2. Department HOD and Class Teacher will endorse the attendance clearance.\n"
            "3. Dean of Student Affairs will issue the signed NOC within 2 working days."
        )

    # 5. Fee Receipt
    elif any(k in q_lower for k in ["fee receipt", "payment receipt", "fee voucher", "tuition receipt", "receipt for fee", "challan"]):
        return (
            "FEE_RECEIPT",
            "Tuition Fee Receipt Generation",
            f"Request for official tuition fee receipt: '{query}'",
            "📋 **Step-by-Step Procedure for Fee Receipt:**\n"
            "1. Quote your semester fee transaction reference or UTR number.\n"
            "2. Finance & Accounts Section validates the bank settlement ledger.\n"
            "3. Official stamped fee voucher will be generated and available for download in your Student Portal within 24 hours."
        )

    # 6. Railway / Bus Transit Concession
    elif any(k in q_lower for k in ["railway", "transit", "bus pass", "concession"]):
        return (
            "RAILWAY_CONCESSION",
            "Transit / Railway Concession Application",
            f"Application for student transit/railway travel concession: '{query}'",
            "📋 **Step-by-Step Procedure for Travel Concession:**\n"
            "1. Verify hometown / traveling railway station in student records.\n"
            "2. Transport & Student Affairs Desk prepares authorized concession voucher.\n"
            "3. Collect the endorsed concession form with university seal from Admin Block Room G-08."
        )

    # 7. Faculty Mentor Appointment
    elif "mentor" in q_lower:
        return (
            "MENTOR_APPOINTMENT",
            "Faculty Mentor 1-on-1 Appointment",
            f"Student requested mentor consultation: '{query}'",
            "📋 **Step-by-Step Procedure for Mentor Consultation:**\n"
            "1. Your assigned mentor has been notified with your discussion topics.\n"
            "2. Check notification feed for the confirmed time slot during official faculty counselling hours (Monday–Friday 3:30–4:30 PM).\n"
            "3. Meet mentor in their department staff room or faculty cabin."
        )

    # 8. Grievance / Complaint
    elif any(k in q_lower for k in ["grievance", "complaint"]):
        return (
            "GRIEVANCE_LODGED",
            "Student Grievance Lodged",
            f"Grievance details: '{query}'",
            "📋 **Step-by-Step Procedure for Grievance Redressal:**\n"
            "1. Statutory Ombudsman & Grievance Cell (Clause 2.1) reviews the logged concern.\n"
            "2. Initial triage status will be shared within 48 hours.\n"
            "3. Formal hearing or resolution report delivered within 7 working days."
        )

    # 9. General Request fallback
    return (
        "OTHER",
        "General Administrative Request",
        query,
        "📋 **Step-by-Step Procedure:**\n"
        "1. Your request has been logged and assigned to Registrar Student Affairs.\n"
        "2. The administrative officer will review and update the status within the estimated SLA.\n"
        "3. You can track this ticket anytime using your tracking ID in the Services tab."
    )

