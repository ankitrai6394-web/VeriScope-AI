"""Pydantic Schemas for VeriScope AI Request/Response and Agent Data Contracts."""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl


class VerificationStatus(str, Enum):
    SUPPORTED = "SUPPORTED"
    CONTRADICTED = "CONTRADICTED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    CONFLICTING_EVIDENCE = "CONFLICTING_EVIDENCE"


class AgentStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class ResearchMode(str, Enum):
    LIVE = "live"
    DEMO = "demo"


# ==========================================
# Client API Request / Response Schemas
# ==========================================

class ResearchCreateRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="The research question or topic to investigate.",
        examples=["Is artificial intelligence improving employment opportunities for fresh graduates in India?"]
    )
    mode: Optional[ResearchMode] = Field(
        default=ResearchMode.LIVE,
        description="Execution mode: 'live' uses search API & LLM; 'demo' uses verified deterministic data."
    )


class AgentExecutionResponse(BaseModel):
    id: str
    session_id: str
    agent_name: str
    status: AgentStatus
    task_description: str
    execution_time_ms: int
    output_summary: Optional[str] = None
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ResearchSourceResponse(BaseModel):
    id: str
    session_id: str
    source_id: str
    title: str
    url: str
    domain: str
    publication_date: Optional[str] = None
    snippet: str
    source_type: str
    reliability_score: float
    reliability_rationale: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ExtractedClaimResponse(BaseModel):
    id: str
    session_id: str
    claim_id: str
    claim_text: str
    evidence_type: str
    confidence: float
    source_ids: List[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ClaimVerificationResponse(BaseModel):
    id: str
    session_id: str
    claim_id: str
    verification_status: VerificationStatus
    explanation: str
    supporting_sources: List[str]
    contradicting_sources: List[str]
    limitations: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ResearchReportResponse(BaseModel):
    id: str
    session_id: str
    report_title: str
    executive_summary: str
    methodology: str
    key_findings: List[str]
    limitations: str
    conclusion: str
    markdown_content: str
    references: List[Dict[str, Any]]
    contradiction_analysis: Optional[List[Dict[str, Any]]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ResearchSessionResponse(BaseModel):
    id: str
    query: str
    mode: str
    status: str
    error_message: Optional[str] = None
    total_sources: int
    total_claims: int
    verified_claims: int
    contradicted_claims: int
    partially_supported_claims: int
    insufficient_claims: int
    conflicting_claims: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ResearchSessionDetailResponse(ResearchSessionResponse):
    agent_executions: List[AgentExecutionResponse] = []
    sources: List[ResearchSourceResponse] = []
    claims: List[ExtractedClaimResponse] = []
    verifications: List[ClaimVerificationResponse] = []
    report: Optional[ResearchReportResponse] = None


# ==========================================
# Agent Structured Input / Output Contracts
# ==========================================

class PlannerOutput(BaseModel):
    topic: str
    research_objective: str
    sub_questions: List[str]
    search_queries: List[str]
    required_source_types: List[str]
    research_strategy: str


class SourceItem(BaseModel):
    source_id: str
    title: str
    url: str
    domain: str
    publication_date: Optional[str] = None
    snippet: str
    source_type: str = "web"


class DiscoveryOutput(BaseModel):
    sources: List[SourceItem]
    total_found: int
    deduplicated_count: int


class ClaimItem(BaseModel):
    claim_id: str
    claim: str
    source_ids: List[str]
    evidence_type: str = "empirical"
    confidence: float = 0.75


class EvidenceExtractionOutput(BaseModel):
    claims: List[ClaimItem]


class VerificationItem(BaseModel):
    claim_id: str
    verification_status: VerificationStatus
    explanation: str
    supporting_source_ids: List[str]
    contradicting_source_ids: List[str]
    limitations: Optional[str] = None


class VerificationOutput(BaseModel):
    verifications: List[VerificationItem]


class ReliabilityItem(BaseModel):
    source_id: str
    domain: str
    source_type: str
    reliability_score: float
    rationale: str
    is_primary_source: bool


class SourceReliabilityOutput(BaseModel):
    assessments: List[ReliabilityItem]


class ContradictionItem(BaseModel):
    claim_ids: List[str]
    conflicting_sources: List[str]
    statement_a: str
    statement_b: str
    divergence_reason: str  # "date", "population", "methodology", "definition", etc.
    analysis: str


class ContradictionOutput(BaseModel):
    has_contradictions: bool
    contradictions: List[ContradictionItem]


class ReportGenerationOutput(BaseModel):
    report_title: str
    executive_summary: str
    methodology: str
    key_findings: List[str]
    limitations: str
    conclusion: str
    markdown_content: str
