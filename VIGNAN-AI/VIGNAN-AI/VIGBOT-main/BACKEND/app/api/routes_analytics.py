from fastapi import APIRouter
from typing import List
from app.models.schemas import DailyAnalyticsItem
from app.database import DataRepository

router = APIRouter(prefix="/analytics", tags=["Query Pattern Analytics (Step 10)"])

@router.get("/daily", response_model=List[DailyAnalyticsItem])
async def get_daily_analytics():
    """
    Returns aggregated daily query patterns by topic and intent.
    Strict privacy rule: Contains ZERO student names, roll numbers, or raw messages.
    """
    summary = DataRepository.get_analytics_summary()
    return [DailyAnalyticsItem(**item) for item in summary]
