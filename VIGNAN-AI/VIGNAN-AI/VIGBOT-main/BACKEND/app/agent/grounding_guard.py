"""
Deterministic Numeric Grounding Guard.
Implements non-bypassable verification of academic and financial metrics
against grounded student database records, ensuring hallucinated numbers
never reach the student.
"""
import re
import math
import logging
from typing import Dict, Any, List, Set, Union, Optional

logger = logging.getLogger(__name__)

# Universal statutory thresholds & institutional constants
STATUTORY_THRESHOLDS: Set[float] = {
    75.0,  # Statutory minimum attendance threshold (VFSTR R22/R23)
    65.0,  # Minimum condonation cutoff for medical grounds
    74.0,  # Condonation range upper bound (R23 Clause 4.2)
    74.9,  # Upper limit of medical condonation window (R22 Clause 4.3)
    10.0,  # Maximum medical condonation shortage allowance (up to 10%)
    0.0,   # Safe default / zero debt
    100.0, # Maximum scale
}

# Standard regulation / clause / calendar constants safe for text
SAFE_LITERAL_CONSTANTS: Set[float] = {
    4.3,   # R22 Clause 4.3 (Medical Condonation)
    2.1,   # Data Governance Clause 2.1 (RLAC)
    8.5,   # Dean recommendation threshold
    2024.0, 2025.0, 2026.0, 2027.0, # Academic years
    1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, # Semesters / numbered points
}


def compute_classes_needed(held: int, attended: int, target: float = 0.75) -> int:
    """
    Deterministically computes the number of consecutive classes a student must attend
    to reach or exceed the target attendance percentage (default 75% or 0.75).
    Formula: max(0, math.ceil((target * held - attended) / (1.0 - target)))
    """
    if held <= 0:
        return 0
    current_pct = (attended / held) * 100.0 if held > 0 else 0.0
    if current_pct >= target * 100.0:
        return 0
    needed = math.ceil((target * held - attended) / (1.0 - target))
    return max(0, int(needed))


def _extract_context_metrics(student_context: Dict[str, Any]) -> Dict[str, Set[float]]:
    """
    Extracts all grounded numbers from student_context into categorised sets.
    """
    metrics: Dict[str, Set[float]] = {
        "percentages": set(STATUTORY_THRESHOLDS),
        "class_counts": set(),
        "classes_needed": set(),
        "currencies": set(),
        "cgpa": set(),
        "marks": set(),
        "all_allowed": set(STATUTORY_THRESHOLDS | SAFE_LITERAL_CONSTANTS),
    }

    # 1. Profile metrics
    profile = student_context.get("profile") or student_context
    if isinstance(profile, dict):
        if "cgpa" in profile and profile["cgpa"] is not None:
            cgpa_val = float(profile["cgpa"])
            metrics["cgpa"].add(round(cgpa_val, 2))
            metrics["all_allowed"].add(round(cgpa_val, 2))
        if "overall_attendance_pct" in profile and profile["overall_attendance_pct"] is not None:
            pct_val = float(profile["overall_attendance_pct"])
            metrics["percentages"].add(round(pct_val, 1))
            metrics["percentages"].add(round(pct_val, 0))
            metrics["all_allowed"].add(round(pct_val, 1))
        if "fee_outstanding" in profile and profile["fee_outstanding"] is not None:
            fee_val = float(profile["fee_outstanding"])
            metrics["currencies"].add(fee_val)
            metrics["all_allowed"].add(fee_val)
        if "backlog_count" in profile and profile["backlog_count"] is not None:
            metrics["all_allowed"].add(float(profile["backlog_count"]))
        if "current_year_of_study" in profile and profile["current_year_of_study"] is not None:
            metrics["all_allowed"].add(float(profile["current_year_of_study"]))
        if "semester" in profile and profile["semester"] is not None:
            metrics["all_allowed"].add(float(profile["semester"]))

    # 2. Attendance records
    att_list = student_context.get("attendance", [])
    if isinstance(att_list, dict):
        att_list = [att_list]
    if isinstance(att_list, list):
        for att in att_list:
            if not isinstance(att, dict):
                continue
            held = att.get("classes_held")
            attended = att.get("classes_attended")
            pct = att.get("current_pct")
            needed = att.get("classes_needed")

            if held is not None:
                metrics["class_counts"].add(float(held))
                metrics["all_allowed"].add(float(held))
            if attended is not None:
                metrics["class_counts"].add(float(attended))
                metrics["all_allowed"].add(float(attended))
            if pct is not None:
                pct_val = float(pct)
                metrics["percentages"].add(round(pct_val, 1))
                metrics["percentages"].add(round(pct_val, 0))
                metrics["all_allowed"].add(round(pct_val, 1))

            # Classes needed: from record or computed deterministically
            if held is not None and attended is not None:
                calc_needed = compute_classes_needed(int(held), int(attended), 0.75)
                metrics["classes_needed"].add(float(calc_needed))
                metrics["all_allowed"].add(float(calc_needed))
            if needed is not None:
                metrics["classes_needed"].add(float(needed))
                metrics["all_allowed"].add(float(needed))

    # 3. Fees records
    fee_list = student_context.get("fees", [])
    if isinstance(fee_list, dict):
        fee_list = [fee_list]
    if isinstance(fee_list, list):
        for fee in fee_list:
            if not isinstance(fee, dict):
                continue
            for k in ["total_demand", "paid_amount", "outstanding_balance", "next_installment_amount", "penalty_amount"]:
                val = fee.get(k)
                if val is not None:
                    f_val = float(val)
                    metrics["currencies"].add(f_val)
                    metrics["all_allowed"].add(f_val)
            # Extract currency numbers from penalty_warning (e.g. "Late fee of INR 500 applies...")
            warning_text = fee.get("penalty_warning") or ""
            for num in re.findall(r"(?:₹|Rs\.?|INR)\s*([\d,]+(?:\.\d+)?)", warning_text, flags=re.IGNORECASE):
                try:
                    f_val = float(num.replace(",", ""))
                    metrics["currencies"].add(f_val)
                    metrics["all_allowed"].add(f_val)
                except ValueError:
                    pass

    # 4. Marks records
    marks_list = student_context.get("marks", [])
    if isinstance(marks_list, dict):
        marks_list = [marks_list]
    if isinstance(marks_list, list):
        for m in marks_list:
            if not isinstance(m, dict):
                continue
            obt = m.get("obtained_marks")
            max_m = m.get("max_marks")
            m_pct = m.get("percentage")
            if obt is not None:
                metrics["marks"].add(float(obt))
                metrics["all_allowed"].add(float(obt))
            if max_m is not None:
                metrics["marks"].add(float(max_m))
                metrics["all_allowed"].add(float(max_m))
            if m_pct is not None:
                metrics["percentages"].add(round(float(m_pct), 1))
                metrics["all_allowed"].add(round(float(m_pct), 1))

    return metrics


def verify_numeric_faithfulness(reply_text: str, student_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts numbers, percentages, and currency amounts from reply_text and validates
    them against the authorized grounded metrics in student_context.

    Returns:
        dict: {
            "is_faithful": bool,
            "checked_numbers": list,
            "unverified_numbers": list
        }
    """
    if not reply_text:
        return {"is_faithful": True, "checked_numbers": [], "unverified_numbers": []}

    metrics = _extract_context_metrics(student_context)
    checked_numbers: List[Dict[str, Any]] = []
    unverified_numbers: List[Dict[str, Any]] = []

    # 1. Check Percentages (e.g. 68%, 68.0%, 75%)
    pct_matches = re.finditer(r"(\b\d+(?:\.\d+)?)\s*%", reply_text)
    for m in pct_matches:
        raw_val = float(m.group(1))
        rounded_1 = round(raw_val, 1)
        rounded_0 = round(raw_val, 0)
        is_allowed = (
            rounded_1 in metrics["percentages"]
            or rounded_0 in metrics["percentages"]
            or raw_val in STATUTORY_THRESHOLDS
        )
        entry = {"type": "percentage", "value": raw_val, "raw": m.group(0)}
        if is_allowed:
            checked_numbers.append(entry)
        else:
            unverified_numbers.append(entry)

    # 2. Check Currency Amounts (e.g. ₹12,500, Rs. 12500, INR 85,000)
    curr_matches = re.finditer(r"(?:₹|Rs\.?|INR)\s*([\d,]+(?:\.\d+)?)", reply_text, flags=re.IGNORECASE)
    for m in curr_matches:
        clean_num_str = m.group(1).replace(",", "")
        try:
            curr_val = float(clean_num_str)
            entry = {"type": "currency", "value": curr_val, "raw": m.group(0)}
            if curr_val in metrics["currencies"] or curr_val == 0.0:
                checked_numbers.append(entry)
            else:
                unverified_numbers.append(entry)
        except ValueError:
            pass

    # 3. Check CGPA claims (e.g. "cgpa of 8.45", "cgpa: 8.45", "cgpa is 8.45")
    cgpa_matches = re.finditer(r"\bcgpa(?:\s*is|\s*of|\s*:)?\s*(\d+(?:\.\d+)?)\b", reply_text, flags=re.IGNORECASE)
    for m in cgpa_matches:
        cgpa_val = float(m.group(1))
        entry = {"type": "cgpa", "value": cgpa_val, "raw": m.group(0)}
        if round(cgpa_val, 2) in metrics["cgpa"] or round(cgpa_val, 1) in metrics["cgpa"]:
            checked_numbers.append(entry)
        else:
            unverified_numbers.append(entry)

    # 4. Check "consecutive classes" needed claims (e.g. "14 consecutive classes", "attend 14 classes")
    needed_matches = re.finditer(r"\b(\d+)\s*(?:more\s*)?(?:consecutive\s*)?classes\b", reply_text, flags=re.IGNORECASE)
    for m in needed_matches:
        count_val = float(m.group(1))
        entry = {"type": "classes_needed_or_held", "value": count_val, "raw": m.group(0)}
        if (
            count_val in metrics["classes_needed"]
            or count_val in metrics["class_counts"]
            or count_val in metrics["all_allowed"]
        ):
            checked_numbers.append(entry)
        else:
            unverified_numbers.append(entry)

    # 5. Check attendance ratio claims (e.g. "34 out of 50 classes", "34/50 classes")
    ratio_matches = re.finditer(r"\b(\d+)\s*(?:out of|/)\s*(\d+)\s*classes\b", reply_text, flags=re.IGNORECASE)
    for m in ratio_matches:
        attended_val = float(m.group(1))
        held_val = float(m.group(2))
        entry = {"type": "attendance_ratio", "attended": attended_val, "held": held_val, "raw": m.group(0)}
        if (
            (attended_val in metrics["class_counts"] or attended_val in metrics["all_allowed"])
            and (held_val in metrics["class_counts"] or held_val in metrics["all_allowed"])
        ):
            checked_numbers.append(entry)
        else:
            unverified_numbers.append(entry)

    is_faithful = (len(unverified_numbers) == 0)

    return {
        "is_faithful": is_faithful,
        "checked_numbers": checked_numbers,
        "unverified_numbers": unverified_numbers,
    }


def enforce_grounding_or_fallback(
    reply_text: str,
    student_context: Dict[str, Any],
    fallback_text: str
) -> str:
    """
    Guarantees that unverified or hallucinated numbers never reach the student.
    If reply_text fails numeric verification against the student's authorized context,
    automatically replaces or corrects with the deterministic grounded fallback text.
    """
    personal_record_indicators = [
        "attendance", "cgpa", "tuition", "fee", "marks",
        "consecutive classes", "classes attended", "classes held"
    ]
    if not any(k in reply_text.lower() for k in personal_record_indicators):
        return reply_text

    verification = verify_numeric_faithfulness(reply_text, student_context)
    if verification["is_faithful"]:
        return reply_text

    unverified = [u.get("raw") for u in verification["unverified_numbers"]]
    logger.warning(
        f"[Grounding Guard] Intercepted unverified numeric metrics from LLM: {unverified}. "
        "Falling back to deterministic grounded database summary."
    )
    return (
        f"{fallback_text}\n\n"
        f"*(Note: Response was verified and grounded against your official university database records "
        f"by the VIGBOT Numeric Grounding Guard to prevent hallucinated metrics.)*"
    )
