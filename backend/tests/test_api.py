"""Integration Tests for Research REST APIs and Full Pipeline."""

import pytest
import pytest_asyncio
import httpx
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool
from backend.app.main import app
from backend.app.database.session import get_db
from backend.app.database.base import Base

# Dedicated in-memory SQLite for tests — avoids all file-lock contention
TEST_DATABASE_URL = "sqlite+aiosqlite://"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False},
)

TestSessionFactory = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def override_get_db():
    async with TestSessionFactory() as session:
        try:
            yield session
        finally:
            await session.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_test_db():
    """Create all tables in test DB and override the DI dependency."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_full_research_workflow():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # 1. Start a demo research session
        create_res = await client.post(
            "/api/research",
            json={
                "query": "Is artificial intelligence improving employment opportunities for fresh graduates in India?",
                "mode": "demo",
            },
        )
        assert create_res.status_code == 201
        data = create_res.json()
        research_id = data["id"]
        assert research_id != ""
        assert data["mode"] == "demo"

        # 2. Poll status (immediately after creation it should be PENDING/RUNNING)
        status_res = await client.get(f"/api/research/{research_id}/status")
        assert status_res.status_code == 200
        status_data = status_res.json()
        assert status_data["id"] == research_id

        # 3. Retrieve history
        history_res = await client.get("/api/research/history")
        assert history_res.status_code == 200
        history_items = history_res.json()
        assert any(item["id"] == research_id for item in history_items)

        # 4. Input validation: query too short
        invalid_res = await client.post(
            "/api/research",
            json={"query": "AI", "mode": "demo"},
        )
        assert invalid_res.status_code == 422

        # 5. Delete the session
        del_res = await client.delete(f"/api/research/{research_id}")
        assert del_res.status_code == 200
        del_data = del_res.json()
        assert del_data["deleted_id"] == research_id


@pytest.mark.asyncio
async def test_session_not_found():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/api/research/non-existent-id-12345")
        assert res.status_code == 404
