from typing import Dict, Any
from app.database import DataRepository, DatabaseSession

def get_fees_summary(session: DatabaseSession) -> Dict[str, Any]:
    fee = DataRepository.get_fees(session)
    if not fee:
        return {
            "text": "All academic dues are settled. No outstanding fee demands found for your account.",
            "structured_card": None
        }

    text = (
        f"Here is your official fee demand and payment status for Academic Year **{fee['academic_year']}**:\n\n"
        f"• Total Demand: **₹{fee['total_demand']:,.2f}**\n"
        f"• Amount Paid: **₹{fee['paid_amount']:,.2f}**\n"
        f"• Outstanding Balance: **₹{fee['outstanding_balance']:,.2f}**\n"
        f"• Next Installment Due Date: **{fee['next_installment_date']}** (Amount: ₹{fee['next_installment_amount']:,.2f})\n\n"
        f"⚠️ **Notice:** {fee['penalty_warning']}"
    )

    card_data = {
        "type": "fee",
        "title": "Bursar Student Fee Status",
        "subtitle": f"Academic Year {fee['academic_year']}",
        "badge": f"₹{fee['outstanding_balance']:,.2f} Due",
        "badgeVariant": "amber" if fee["outstanding_balance"] > 0 else "green",
        "data": fee,
        "actionLabel": "Pay Installment Online",
        "actionIntent": "service:pay_fee"
    }

    return {
        "text": text,
        "structured_card": card_data
    }
