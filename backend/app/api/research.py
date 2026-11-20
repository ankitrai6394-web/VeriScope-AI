"""Research Session REST API Endpoints."""

import asyncio
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from backend.app.database.session import get_db, async_session_factory
from backend.app.models.research import (
    ResearchSession,
    AgentExecution,
    ResearchSource,
    ExtractedClaim,
    ClaimVerification,
    ResearchReport,
)
from backend.app.schemas.research import (
    ResearchCreateRequest,
    ResearchSessionResponse,
    ResearchSessionDetailResponse,
    AgentExecutionResponse,
    ResearchSourceResponse,
    ExtractedClaimResponse,
    ClaimVerificationResponse,
    ResearchReportResponse,
)
from backend.app.services.orchestrator import MultiAgentOrchestrator

router = APIRouter(prefix="/research", tags=["Research"])


async def run_orchestrator_background(session_id: str, mode: str):
    """Background runner with its own dedicated session to prevent connection leak."""
    async with async_session_factory() as db:
        orchestrator = MultiAgentOrchestrator(session_id=session_id, db=db, mode=mode)
        await orchestrator.run_pipeline()


@router.post("", response_model=ResearchSessionResponse, status_code=status.HTTP_201_CREATED)
async def start_research_session(
    request: ResearchCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Start a new research investigation session. Returns immediately while agents run in the background."""
    mode_val = request.mode.value if request.mode else "live"

    session_obj = ResearchSession(
        query=request.query.strip(),
        mode=mode_val,
        status="PENDING",
    )
    db.add(session_obj)
    await db.commit()
    await db.refresh(session_obj)

    # Launch asynchronous background multi-agent orchestrator pipeline
    asyncio.create_task(run_orchestrator_background(session_id=session_obj.id, mode=mode_val))

    return session_obj


@router.get("/history", response_model=List[ResearchSessionResponse])
async def get_research_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve historical research sessions ordered by latest creation time."""
    stmt = (
        select(ResearchSession)
        .order_by(desc(ResearchSession.created_at))
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{research_id}", response_model=ResearchSessionDetailResponse)
async def get_research_session_detail(
    research_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve full details of a specific research session including agents, claims, sources, and report."""
    stmt = (
        select(ResearchSession)
        .where(ResearchSession.id == research_id)
        .options(
            selectinload(ResearchSession.agent_executions),
            selectinload(ResearchSession.sources),
            selectinload(ResearchSession.claims),
            selectinload(ResearchSession.verifications),
            selectinload(ResearchSession.report),
        )
    )
    result = await db.execute(stmt)
    session_obj = result.scalars().first()

    if not session_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Research session with ID '{research_id}' was not found.",
        )

    return session_obj


@router.get("/{research_id}/status")
async def get_research_status(
    research_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve lightweight status progress and agent execution stages for polling."""
    stmt = (
        select(ResearchSession)
        .where(ResearchSession.id == research_id)
        .options(selectinload(ResearchSession.agent_executions))
    )
    result = await db.execute(stmt)
    session_obj = result.scalars().first()

    if not session_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Research session with ID '{research_id}' was not found.",
        )

    agents_status = [
        {
            "agent_name": a.agent_name,
            "status": a.status,
            "task_description": a.task_description,
            "execution_time_ms": a.execution_time_ms,
            "output_summary": a.output_summary,
            "error_message": a.error_message,
        }
        for a in session_obj.agent_executions
    ]

    return {
        "id": session_obj.id,
        "query": session_obj.query,
        "mode": session_obj.mode,
        "status": session_obj.status,
        "error_message": session_obj.error_message,
        "total_sources": session_obj.total_sources,
        "total_claims": session_obj.total_claims,
        "verified_claims": session_obj.verified_claims,
        "contradicted_claims": session_obj.contradicted_claims,
        "agents": agents_status,
        "updated_at": session_obj.updated_at,
    }


@router.get("/{research_id}/agents", response_model=List[AgentExecutionResponse])
async def get_research_agents(
    research_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve detailed agent execution logs and outputs for a session."""
    stmt = (
        select(AgentExecution)
        .where(AgentExecution.session_id == research_id)
        .order_by(AgentExecution.created_at)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{research_id}/sources", response_model=List[ResearchSourceResponse])
async def get_research_sources(
    research_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve all collected and evaluated sources for a research session."""
    stmt = (
        select(ResearchSource)
        .where(ResearchSource.session_id == research_id)
        .order_by(ResearchSource.source_id)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{research_id}/claims")
async def get_research_claims(
    research_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve all extracted claims joined with their verification outcomes."""
    claims_stmt = (
        select(ExtractedClaim)
        .where(ExtractedClaim.session_id == research_id)
        .order_by(ExtractedClaim.claim_id)
    )
    verifications_stmt = (
        select(ClaimVerification)
        .where(ClaimVerification.session_id == research_id)
    )

    claims_res = await db.execute(claims_stmt)
    ver_res = await db.execute(verifications_stmt)

    claims = claims_res.scalars().all()
    verifications = {v.claim_id: v for v in ver_res.scalars().all()}

    combined = []
    for c in claims:
        v = verifications.get(c.claim_id)
        combined.append({
            "claim_id": c.claim_id,
            "claim_text": c.claim_text,
            "evidence_type": c.evidence_type,
            "confidence": c.confidence,
            "source_ids": c.source_ids,
            "verification": {
                "verification_status": v.verification_status,
                "explanation": v.explanation,
                "supporting_sources": v.supporting_sources,
                "contradicting_sources": v.contradicting_sources,
                "limitations": v.limitations,
            } if v else None,
        })

    return combined


@router.get("/{research_id}/report", response_model=ResearchReportResponse)
async def get_research_report(
    research_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve the synthesized final research report."""
    stmt = select(ResearchReport).where(ResearchReport.session_id == research_id)
    result = await db.execute(stmt)
    report = result.scalars().first()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report for research session '{research_id}' is not yet available or session failed.",
        )

    return report


@router.delete("/{research_id}", status_code=status.HTTP_200_OK)
async def delete_research_session(
    research_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a research session and all associated agent records, claims, sources, and report."""
    stmt = select(ResearchSession).where(ResearchSession.id == research_id)
    result = await db.execute(stmt)
    session_obj = result.scalars().first()

    if not session_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Research session with ID '{research_id}' was not found.",
        )

    await db.delete(session_obj)
    await db.commit()

    return {"message": f"Research session '{research_id}' deleted successfully.", "deleted_id": research_id}
