"""VeriScope AI Backend Application Entrypoint.

PS03 - Multi-Agent Research & Fact-Checking Platform.
Hack2skill PromptWars x Agent X 2.0.
"""

import logging
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware

from backend.app.core.config import settings
from backend.app.database.session import init_db
from backend.app.api.health import router as health_router
from backend.app.api.research import router as research_router

# Setup logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("veriscope.main")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add defense-in-depth security headers to every HTTP response."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["Cache-Control"] = "no-store, max-age=0"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https:;"
        )
        response.headers["X-Request-ID"] = request.headers.get(
            "X-Request-ID", str(uuid.uuid4())
        )
        return response


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Reject requests with body larger than 64KB to prevent DoS or abuse."""

    MAX_BODY_SIZE = 65536  # 64 KB

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.MAX_BODY_SIZE:
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={
                    "error": "Payload Too Large",
                    "message": f"Request body must not exceed {self.MAX_BODY_SIZE} bytes.",
                },
            )
        return await call_next(request)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager initializing database tables on startup."""
    logger.info("Initializing VeriScope AI database schema...")
    await init_db()
    logger.info("VeriScope AI database tables initialized successfully.")
    yield
    logger.info("VeriScope AI application shutdown.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "VeriScope AI is a multi-agent autonomous research and fact-checking platform. "
        "Engineered for Hack2skill PromptWars x Agent X 2.0 (Problem Statement PS03)."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Middleware stack (applied in reverse order — last added runs first)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestSizeLimitMiddleware)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=(
        r"https://.*\.onrender\.com|"
        r"https://.*\.vercel\.app|"
        r"https://.*\.netlify\.app|"
        r"http://localhost:\d+|"
        r"http://127\.0\.0\.1:\d+"
    ),
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Request-ID", "Accept"],
)

# Register API Routers
app.include_router(health_router, prefix="/api")
app.include_router(research_router, prefix="/api")


# Global Exception Sanitizers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Sanitize validation errors to prevent internal schema leak."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "message": "Invalid research query or request format.",
            "details": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Sanitize internal errors to prevent stack trace or secret exposure."""
    logger.exception(f"Unhandled error processing {request.method} {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An error occurred while processing the multi-agent research pipeline.",
        },
    )


@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "docs": "/docs",
        "api_health": "/api/health",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG,
    )
