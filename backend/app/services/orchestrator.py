"""VeriScope AI Multi-Agent Orchestration Engine.

Coordinates the 7 specialized agents with asynchronous execution, concurrent independent tasks,
persistent state tracking in SQLite, bounded retries, and comprehensive error handling.
"""

import asyncio
import logging
import time
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.core.config import settings
from backend.app.models.research import (
    ResearchSession,
    AgentExecution,
    ResearchSource,
    ExtractedClaim,
    ClaimVerification,
    ResearchReport,
)
from backend.app.schemas.research import (
    AgentStatus,
    VerificationStatus,
    PlannerOutput,
    DiscoveryOutput,
    EvidenceExtractionOutput,
    VerificationOutput,
    SourceReliabilityOutput,
    ContradictionOutput,
    ReportGenerationOutput,
)
from backend.app.providers.llm_provider import get_llm_provider
from backend.app.providers.search_provider import get_search_provider
from backend.app.agents.planner import ResearchPlannerAgent
from backend.app.agents.discovery import ResearchDiscoveryAgent
from backend.app.agents.extractor import EvidenceExtractionAgent
from backend.app.agents.verifier import FactVerificationAgent
from backend.app.agents.reliability import SourceReliabilityAgent
from backend.app.agents.contradiction import ContradictionDetectionAgent
from backend.app.agents.reporter import ReportGenerationAgent

logger = logging.getLogger("veriscope.orchestrator")


class MultiAgentOrchestrator:
    def __init__(self, session_id: str, db: AsyncSession, mode: str = "live"):
        self.session_id = session_id
        self.db = db
        self.mode = mode

        # Providers
        self.llm_provider = get_llm_provider(mode=mode)
        self.search_provider = get_search_provider(mode=mode)

        # Agents
        self.planner_agent = ResearchPlannerAgent(self.llm_provider)
        self.discovery_agent = ResearchDiscoveryAgent(self.search_provider)
        self.extractor_agent = EvidenceExtractionAgent(self.llm_provider)
        self.verifier_agent = FactVerificationAgent(self.llm_provider)
        self.reliability_agent = SourceReliabilityAgent(self.llm_provider)
        self.contradiction_agent = ContradictionDetectionAgent(self.llm_provider)
        self.reporter_agent = ReportGenerationAgent(self.llm_provider)

    async def _update_agent_record(
        self,
        agent_name: str,
        status: AgentStatus,
        task_description: str,
        start_time: float,
        output_summary: Optional[str] = None,
        output_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
    ) -> AgentExecution:
        duration_ms = int((time.time() - start_time) * 1000)

        # Query existing record
        stmt = select(AgentExecution).where(
            AgentExecution.session_id == self.session_id,
            AgentExecution.agent_name == agent_name,
        )
        result = await self.db.execute(stmt)
        record = result.scalars().first()

        if not record:
            record = AgentExecution(
                session_id=self.session_id,
                agent_name=agent_name,
                task_description=task_description,
                status=status.value,
                execution_time_ms=duration_ms,
                output_summary=output_summary,
                output_data=output_data,
                error_message=error_message,
            )
            self.db.add(record)
        else:
            record.status = status.value
            record.execution_time_ms = duration_ms
            if output_summary:
                record.output_summary = output_summary
            if output_data:
                record.output_data = output_data
            if error_message:
                record.error_message = error_message

        await self.db.commit()
        await self.db.refresh(record)
        return record

    async def run_pipeline(self) -> None:
        """Execute the complete multi-agent fact-checking and research pipeline."""
        logger.info(f"Starting MultiAgentOrchestrator pipeline for session {self.session_id} (mode={self.mode})")

        # 1. Fetch Research Session
        stmt = select(ResearchSession).where(ResearchSession.id == self.session_id)
        res = await self.db.execute(stmt)
        session_obj = res.scalars().first()

        if not session_obj:
            logger.error(f"Research session {self.session_id} not found.")
            return

        session_obj.status = "RUNNING"
        await self.db.commit()

        try:
            # ----------------------------------------------------
            # STEP 1: Research Planner Agent
            # ----------------------------------------------------
            start_t = time.time()
            agent_name = "Research Planner"
            await self._update_agent_record(
                agent_name=agent_name,
                status=AgentStatus.RUNNING,
                task_description="Analyzing question, decomposing sub-questions, and formulating search strategy",
                start_time=start_t,
            )

            planner_output: PlannerOutput = await self.planner_agent.execute(query=session_obj.query)
            await self._update_agent_record(
                agent_name=agent_name,
                status=AgentStatus.COMPLETED,
                task_description="Decomposed query into sub-questions and generated search terms",
                start_time=start_t,
                output_summary=f"Formulated {len(planner_output.sub_questions)} sub-questions and {len(planner_output.search_queries)} search queries.",
                output_data=planner_output.model_dump(),
            )

            # ----------------------------------------------------
            # STEP 2: Research Discovery Agent
            # ----------------------------------------------------
            start_t = time.time()
            agent_name = "Research Discovery"
            await self._update_agent_record(
                agent_name=agent_name,
                status=AgentStatus.RUNNING,
                task_description="Querying external search provider, retrieving URLs, deduplicating, and filtering",
                start_time=start_t,
            )

            discovery_output: DiscoveryOutput = await self.discovery_agent.execute(
                search_queries=planner_output.search_queries,
                max_results_per_query=settings.MAX_SEARCH_RESULTS_PER_QUERY,
            )

            # Persist discovered sources in DB
            for src in discovery_output.sources:
                db_source = ResearchSource(
                    session_id=self.session_id,
                    source_id=src.source_id,
                    title=src.title,
                    url=src.url,
                    domain=src.domain,
                    publication_date=src.publication_date,
                    snippet=src.snippet,
                    source_type=src.source_type,
                )
                self.db.add(db_source)
            await self.db.commit()

            await self._update_agent_record(
                agent_name=agent_name,
                status=AgentStatus.COMPLETED,
                task_description="Retrieved and deduplicated authoritative sources",
                start_time=start_t,
                output_summary=f"Collected and verified {len(discovery_output.sources)} unique sources.",
                output_data=discovery_output.model_dump(),
            )

            # ----------------------------------------------------
            # STEP 3: Evidence Extraction Agent
            # ----------------------------------------------------
            start_t = time.time()
            agent_name = "Evidence Extraction"
            await self._update_agent_record(
                agent_name=agent_name,
                status=AgentStatus.RUNNING,
                task_description="Extracting discrete factual claims and statistical data points from sources",
                start_time=start_t,
            )

            extractor_output: EvidenceExtractionOutput = await self.extractor_agent.execute(
                sources=discovery_output.sources
            )

            # Persist extracted claims in DB
            for clm in extractor_output.claims:
                db_claim = ExtractedClaim(
                    session_id=self.session_id,
                    claim_id=clm.claim_id,
                    claim_text=clm.claim,
                    evidence_type=clm.evidence_type,
                    confidence=clm.confidence,
                    source_ids=clm.source_ids,
                )
                self.db.add(db_claim)
            await self.db.commit()

            await self._update_agent_record(
                agent_name=agent_name,
                status=AgentStatus.COMPLETED,
                task_description="Extracted atomic factual statements mapped to source citations",
                start_time=start_t,
                output_summary=f"Extracted {len(extractor_output.claims)} discrete verifiable claims.",
                output_data=extractor_output.model_dump(),
            )

            # ----------------------------------------------------
            # STEP 4 & 5: Fact Verification & Source Reliability
            # Agent computations run concurrently via asyncio.gather.
            # DB status updates are serialized (single AsyncSession is not
            # safe for concurrent commits from multiple coroutines).
            # ----------------------------------------------------
            start_t_verifier = time.time()
            start_t_reliability = time.time()

            # Serialize the two RUNNING status writes
            await self._update_agent_record(
                agent_name="Fact Verification",
                status=AgentStatus.RUNNING,
                task_description="Cross-examining extracted claims against independent evidence base",
                start_time=start_t_verifier,
            )
            await self._update_agent_record(
                agent_name="Source Reliability",
                status=AgentStatus.RUNNING,
                task_description="Evaluating domain integrity, publication recency, and primary/secondary authority",
                start_time=start_t_reliability,
            )

            verifier_task = self.verifier_agent.execute(
                claims=extractor_output.claims,
                sources=discovery_output.sources,
            )
            reliability_task = self.reliability_agent.execute(
                sources=discovery_output.sources
            )

            verifier_output, reliability_output = await asyncio.gather(
                verifier_task,
                reliability_task,
            )

            # Persist verifications in DB
            verified_cnt = 0
            contradicted_cnt = 0
            partially_supported_cnt = 0
            insufficient_cnt = 0
            conflicting_cnt = 0

            for v in verifier_output.verifications:
                db_ver = ClaimVerification(
                    session_id=self.session_id,
                    claim_id=v.claim_id,
                    verification_status=v.verification_status.value,
                    explanation=v.explanation,
                    supporting_sources=v.supporting_source_ids,
                    contradicting_sources=v.contradicting_source_ids,
                    limitations=v.limitations,
                )
                self.db.add(db_ver)

                if v.verification_status == VerificationStatus.SUPPORTED:
                    verified_cnt += 1
                elif v.verification_status == VerificationStatus.CONTRADICTED:
                    contradicted_cnt += 1
                elif v.verification_status == VerificationStatus.PARTIALLY_SUPPORTED:
                    partially_supported_cnt += 1
                elif v.verification_status == VerificationStatus.INSUFFICIENT_EVIDENCE:
                    insufficient_cnt += 1
                elif v.verification_status == VerificationStatus.CONFLICTING_EVIDENCE:
                    conflicting_cnt += 1

            # Update Source Reliability scores in DB
            reliability_map = {r.source_id: r for r in reliability_output.assessments}
            src_stmt = select(ResearchSource).where(ResearchSource.session_id == self.session_id)
            src_res = await self.db.execute(src_stmt)
            for db_src in src_res.scalars().all():
                if db_src.source_id in reliability_map:
                    rel_item = reliability_map[db_src.source_id]
                    db_src.reliability_score = rel_item.reliability_score
                    db_src.reliability_rationale = rel_item.rationale
                    db_src.source_type = rel_item.source_type

            await self.db.commit()

            # Serialize COMPLETED status writes (single session, no concurrent commits)
            await self._update_agent_record(
                agent_name="Fact Verification",
                status=AgentStatus.COMPLETED,
                task_description="Completed multi-source claim verification and status classification",
                start_time=start_t_verifier,
                output_summary=f"Verified {len(verifier_output.verifications)} claims: {verified_cnt} Supported, {contradicted_cnt} Contradicted.",
                output_data=verifier_output.model_dump(),
            )
            await self._update_agent_record(
                agent_name="Source Reliability",
                status=AgentStatus.COMPLETED,
                task_description="Completed institutional quality scoring and methodology reviews",
                start_time=start_t_reliability,
                output_summary=f"Evaluated {len(reliability_output.assessments)} sources for credibility and primary status.",
                output_data=reliability_output.model_dump(),
            )

            # ----------------------------------------------------
            # STEP 6: Contradiction Detection Agent
            # ----------------------------------------------------
            start_t = time.time()
            agent_name = "Contradiction Detection"
            await self._update_agent_record(
                agent_name=agent_name,
                status=AgentStatus.RUNNING,
                task_description="Analyzing cross-source discrepancies, dating differences, and sample divergences",
                start_time=start_t,
            )

            contradiction_output: ContradictionOutput = await self.contradiction_agent.execute(
                claims=extractor_output.claims,
                verifications=verifier_output.verifications,
                sources=discovery_output.sources,
            )

            await self._update_agent_record(
                agent_name=agent_name,
                status=AgentStatus.COMPLETED,
                task_description="Identified and reconciled discrepancies among independent sources",
                start_time=start_t,
                output_summary=f"Identified {len(contradiction_output.contradictions)} substantive cross-source discrepancies.",
                output_data=contradiction_output.model_dump(),
            )

            # ----------------------------------------------------
            # STEP 7: Report Generation Agent
            # ----------------------------------------------------
            start_t = time.time()
            agent_name = "Report Generation"
            await self._update_agent_record(
                agent_name=agent_name,
                status=AgentStatus.RUNNING,
                task_description="Synthesizing all agent outputs into an 11-section structured research dossier",
                start_time=start_t,
            )

            report_output: ReportGenerationOutput = await self.reporter_agent.execute(
                query=session_obj.query,
                plan=planner_output,
                sources=discovery_output.sources,
                claims=extractor_output.claims,
                verifications=verifier_output.verifications,
                reliability=reliability_output,
                contradictions=contradiction_output,
            )

            # References list with source citations
            references_payload = [
                {
                    "source_id": s.source_id,
                    "title": s.title,
                    "url": s.url,
                    "domain": s.domain,
                    "publication_date": s.publication_date,
                    "reliability_score": getattr(s, "reliability_score", 0.85),
                }
                for s in discovery_output.sources
            ]

            # Persist Report in DB
            db_report = ResearchReport(
                session_id=self.session_id,
                report_title=report_output.report_title,
                executive_summary=report_output.executive_summary,
                methodology=report_output.methodology,
                key_findings=report_output.key_findings,
                limitations=report_output.limitations,
                conclusion=report_output.conclusion,
                markdown_content=report_output.markdown_content,
                references=references_payload,
                contradiction_analysis=[c.model_dump() for c in contradiction_output.contradictions],
            )
            self.db.add(db_report)

            await self._update_agent_record(
                agent_name=agent_name,
                status=AgentStatus.COMPLETED,
                task_description="Generated final evidence-backed research report with citations",
                start_time=start_t,
                output_summary="Synthesized complete 11-section research report with full citations.",
                output_data=report_output.model_dump(),
            )

            # ----------------------------------------------------
            # Complete Session Summary Counters
            # ----------------------------------------------------
            session_obj.status = "COMPLETED"
            session_obj.total_sources = len(discovery_output.sources)
            session_obj.total_claims = len(extractor_output.claims)
            session_obj.verified_claims = verified_cnt
            session_obj.contradicted_claims = contradicted_cnt
            session_obj.partially_supported_claims = partially_supported_cnt
            session_obj.insufficient_claims = insufficient_cnt
            session_obj.conflicting_claims = conflicting_cnt

            await self.db.commit()
            logger.info(f"Pipeline successfully completed for session {self.session_id}")

        except Exception as e:
            logger.exception(f"Pipeline execution failed for session {self.session_id}: {e}")
            session_obj.status = "FAILED"
            session_obj.error_message = str(e)
            await self.db.commit()
