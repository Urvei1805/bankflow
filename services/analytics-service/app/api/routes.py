"""
BankFlow Analytics Service — API Routes
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.analytics_service import (
    get_analytics_summary,
    get_fraud_distribution,
    get_spend_by_category,
)

router = APIRouter(prefix="/v1/analytics", tags=["Analytics"])


@router.get("/summary")
async def analytics_summary(db: AsyncSession = Depends(get_db)):
    """
    Get analytics summary: total transactions, volume, averages, fraud counts.
    Results are cached in Redis for 60 seconds.
    """
    data = await get_analytics_summary(db)
    return {
        "data": {
            "type": "analytics-summary",
            "id": "current",
            "attributes": data,
        }
    }


@router.get("/fraud-distribution")
async def fraud_distribution(db: AsyncSession = Depends(get_db)):
    """
    Get fraud risk distribution breakdown.
    Results are cached in Redis for 60 seconds.
    """
    data = await get_fraud_distribution(db)
    return {
        "data": {
            "type": "fraud-distribution",
            "id": "current",
            "attributes": data,
        }
    }


@router.get("/spend-by-category")
async def spend_by_category(db: AsyncSession = Depends(get_db)):
    """
    Get total spend grouped by merchant category.
    Results are cached in Redis for 60 seconds.
    """
    data = await get_spend_by_category(db)
    return {
        "data": {
            "type": "spend-by-category",
            "id": "current",
            "attributes": data,
        }
    }
