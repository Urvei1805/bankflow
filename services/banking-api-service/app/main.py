"""
BankFlow Banking API Service — FastAPI Application Entry Point
──────────────────────────────────────────────────────────────
Provides payments, accounts, transactions, consent management,
and real-time WebSocket transaction feed.
"""
import time
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api.routes import router as banking_router
from app.api.websocket import router as ws_router
from app.core.config import get_settings
from app.db.session import init_db

settings = get_settings()

logger = structlog.get_logger()

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"],
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("banking_service_starting", environment=settings.ENVIRONMENT)
    await init_db()
    logger.info("database_initialized")
    yield
    logger.info("banking_service_shutting_down")


app = FastAPI(
    title="BankFlow Banking API Service",
    description="Open Banking payments, accounts, transactions, and consent management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(GZipMiddleware, minimum_size=500)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    start = time.time()
    response: Response = await call_next(request)
    process_time = time.time() - start
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Process-Time"] = str(round(process_time, 4))
    return response


app.include_router(banking_router)
app.include_router(ws_router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "banking-api-service",
        "version": "1.0.0",
    }
