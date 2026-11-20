"""Health and Status Endpoints."""

from fastapi import APIRouter
from backend.app.core.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """Health check endpoint confirming API availability and operational mode."""
    has_llm = bool(settings.LLM_API_KEY)
    has_search = bool(settings.SEARCH_API_KEY)

    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "providers": {
            "llm": {
                "configured": has_llm,
                "provider": settings.LLM_PROVIDER if has_llm else "mock (demo mode)",
                "model": settings.LLM_MODEL,
            },
            "search": {
                "configured": has_search,
                "provider": settings.SEARCH_PROVIDER if has_search else "mock (demo mode)",
            },
        },
        "live_mode_available": has_llm and has_search,
        "demo_mode_available": True,
    }
