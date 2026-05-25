"""
BankFlow Analytics Service — Analytics Business Logic
Reads from the shared PostgreSQL database (transactions table)
and provides cached analytics results via Redis.
"""
import json
from typing import Optional

import redis.asyncio as aioredis
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings

settings = get_settings()


async def _get_redis():
    """Get async Redis connection."""
    return aioredis.from_url(settings.redis_url, decode_responses=True)


async def _get_cached(key: str) -> Optional[dict]:
    """Get cached result from Redis."""
    try:
        r = await _get_redis()
        cached = await r.get(key)
        await r.aclose()
        if cached:
            return json.loads(cached)
    except Exception:
        pass
    return None


async def _set_cached(key: str, data: dict, ttl: int = None):
    """Set cached result in Redis."""
    try:
        r = await _get_redis()
        await r.setex(
            key,
            ttl or settings.ANALYTICS_CACHE_TTL,
            json.dumps(data, default=str),
        )
        await r.aclose()
    except Exception:
        pass


async def get_analytics_summary(db: AsyncSession) -> dict:
    """
    Get overall analytics summary:
    - Total transactions
    - Total volume
    - Average transaction
    - Fraud counts by risk level
    """
    cache_key = "analytics:summary"
    cached = await _get_cached(cache_key)
    if cached:
        return cached

    # Query transaction stats
    result = await db.execute(
        text("""
            SELECT
                COUNT(*) as total_transactions,
                COALESCE(SUM(amount), 0) as total_volume,
                COALESCE(AVG(amount), 0) as avg_transaction,
                COUNT(CASE WHEN fraud_risk_level = 'HIGH' THEN 1 END) as high_risk_count,
                COUNT(CASE WHEN fraud_risk_level = 'MEDIUM' THEN 1 END) as medium_risk_count,
                COUNT(CASE WHEN fraud_risk_level = 'LOW' THEN 1 END) as low_risk_count
            FROM transactions
        """)
    )
    row = result.one_or_none()

    if not row:
        data = {
            "total_transactions": 0,
            "total_volume": 0,
            "avg_transaction": 0,
            "fraud_distribution": {"HIGH": 0, "MEDIUM": 0, "LOW": 0},
        }
    else:
        data = {
            "total_transactions": row[0],
            "total_volume": round(float(row[1]), 2),
            "avg_transaction": round(float(row[2]), 2),
            "fraud_distribution": {
                "HIGH": row[3],
                "MEDIUM": row[4],
                "LOW": row[5],
            },
        }

    await _set_cached(cache_key, data)
    return data


async def get_fraud_distribution(db: AsyncSession) -> dict:
    """Get fraud risk distribution breakdown."""
    cache_key = "analytics:fraud_distribution"
    cached = await _get_cached(cache_key)
    if cached:
        return cached

    result = await db.execute(
        text("""
            SELECT
                fraud_risk_level,
                COUNT(*) as count,
                COALESCE(SUM(amount), 0) as total_amount
            FROM transactions
            GROUP BY fraud_risk_level
            ORDER BY fraud_risk_level
        """)
    )
    rows = result.all()

    data = {
        "distribution": [
            {
                "risk_level": row[0] or "LOW",
                "count": row[1],
                "total_amount": round(float(row[2]), 2),
            }
            for row in rows
        ]
    }

    await _set_cached(cache_key, data)
    return data


async def get_spend_by_category(db: AsyncSession) -> dict:
    """Get total spend grouped by merchant category."""
    cache_key = "analytics:spend_by_category"
    cached = await _get_cached(cache_key)
    if cached:
        return cached

    result = await db.execute(
        text("""
            SELECT
                COALESCE(merchant_category, 'unknown') as category,
                COUNT(*) as transaction_count,
                COALESCE(SUM(amount), 0) as total_spend,
                COALESCE(AVG(amount), 0) as avg_spend
            FROM transactions
            WHERE transaction_type = 'debit'
            GROUP BY merchant_category
            ORDER BY total_spend DESC
        """)
    )
    rows = result.all()

    data = {
        "categories": [
            {
                "category": row[0],
                "transaction_count": row[1],
                "total_spend": round(float(row[2]), 2),
                "avg_spend": round(float(row[3]), 2),
            }
            for row in rows
        ]
    }

    await _set_cached(cache_key, data)
    return data
