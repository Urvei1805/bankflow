"""
BankFlow Auth Service — FastAPI Application Entry Point
──────────────────────────────────────────────────────────
Provides OAuth2/JWT authentication, user/TPP registration,
API key management, and role-based access control.
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

from app.api.routes import router as auth_router
from app.core.config import get_settings
from app.db.session import init_db

settings = get_settings()

# ── Structured Logging ────────────────────────────────────────
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# ── Rate Limiting ─────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)


# ── Lifespan ──────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("auth_service_starting", environment=settings.ENVIRONMENT)
    await init_db()
    logger.info("database_initialized")
    yield
    logger.info("auth_service_shutting_down")


# ── Application Factory ──────────────────────────────────────
app = FastAPI(
    title="BankFlow Auth Service",
    description="OAuth2/JWT authentication and API key management for BankFlow",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── Middleware ────────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(GZipMiddleware, minimum_size=500)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    """Add security headers to all responses."""
    start = time.time()
    response: Response = await call_next(request)
    process_time = time.time() - start

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Process-Time"] = str(round(process_time, 4))
    return response


# ── Routes ────────────────────────────────────────────────────
app.include_router(auth_router)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for load balancers and Docker."""
    return {
        "status": "healthy",
        "service": "auth-service",
        "version": "1.0.0",
    }
