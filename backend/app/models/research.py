"""Database Models for VeriScope AI Research Platform."""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Text,
    Float,
    Integer,
    DateTime,
    ForeignKey,
    JSON,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship
from backend.app.database.base import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class ResearchSession(Base):
    __tablename__ = "research_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    query = Column(String(500), nullable=False, index=True)
    mode = Column(String(20), default="live", nullable=False)  # "live" or "demo"
    status = Column(String(30), default="PENDING", nullable=False, index=True)  # PENDING, RUNNING, COMPLETED, FAILED
    error_message = Column(Text, nullable=True)
    
    # Quantitative summary counters
    total_sources = Column(Integer, default=0)
    total_claims = Column(Integer, default=0)
    verified_claims = Column(Integer, default=0)
    contradicted_claims = Column(Integer, default=0)
    partially_supported_claims = Column(Integer, default=0)
    insufficient_claims = Column(Integer, default=0)
    conflicting_claims = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    agent_executions = relationship("AgentExecution", back_populates="session", cascade="all, delete-orphan")
    sources = relationship("ResearchSource", back_populates="session", cascade="all, delete-orphan")
    claims = relationship("ExtractedClaim", back_populates="session", cascade="all, delete-orphan")
    verifications = relationship("ClaimVerification", back_populates="session", cascade="all, delete-orphan")
    report = relationship("ResearchReport", back_populates="session", uselist=False, cascade="all, delete-orphan")


class AgentExecution(Base):
    __tablename__ = "agent_executions"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    session_id = Column(String(36), ForeignKey("research_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_name = Column(String(50), nullable=False)  # e.g., "Research Planner", "Fact Verification"
    status = Column(String(20), default="PENDING", nullable=False)  # PENDING, RUNNING, COMPLETED, FAILED, SKIPPED
    task_description = Column(Text, nullable=False)
    execution_time_ms = Column(Integer, default=0)
    output_summary = Column(Text, nullable=True)
    output_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    session = relationship("ResearchSession", back_populates="agent_executions")


class ResearchSource(Base):
    __tablename__ = "research_sources"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    session_id = Column(String(36), ForeignKey("research_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    source_id = Column(String(20), nullable=False, index=True)  # SRC-001
    title = Column(String(500), nullable=False)
    url = Column(String(1000), nullable=False)
    domain = Column(String(255), nullable=False, index=True)
    publication_date = Column(String(50), nullable=True)
    snippet = Column(Text, nullable=False)
    source_type = Column(String(50), default="web")  # academic, government, industry, news, web
    reliability_score = Column(Float, default=0.5)
    reliability_rationale = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    session = relationship("ResearchSession", back_populates="sources")


class ExtractedClaim(Base):
    __tablename__ = "extracted_claims"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    session_id = Column(String(36), ForeignKey("research_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    claim_id = Column(String(20), nullable=False, index=True)  # CLM-001
    claim_text = Column(Text, nullable=False)
    evidence_type = Column(String(50), default="empirical")  # statistical, empirical, observational, definitional
    confidence = Column(Float, default=0.7)
    source_ids = Column(JSON, nullable=False, default=list)  # ["SRC-001", "SRC-002"]
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    session = relationship("ResearchSession", back_populates="claims")


class ClaimVerification(Base):
    __tablename__ = "claim_verifications"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    session_id = Column(String(36), ForeignKey("research_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    claim_id = Column(String(20), nullable=False, index=True)  # CLM-001
    verification_status = Column(String(30), nullable=False)  # SUPPORTED, CONTRADICTED, PARTIALLY_SUPPORTED, INSUFFICIENT_EVIDENCE, CONFLICTING_EVIDENCE
    explanation = Column(Text, nullable=False)
    supporting_sources = Column(JSON, nullable=False, default=list)  # ["SRC-001"]
    contradicting_sources = Column(JSON, nullable=False, default=list)  # ["SRC-002"]
    limitations = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    session = relationship("ResearchSession", back_populates="verifications")


class ResearchReport(Base):
    __tablename__ = "research_reports"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    session_id = Column(String(36), ForeignKey("research_sessions.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    report_title = Column(String(500), nullable=False)
    executive_summary = Column(Text, nullable=False)
    methodology = Column(Text, nullable=False)
    key_findings = Column(JSON, nullable=False, default=list)
    limitations = Column(Text, nullable=False)
    conclusion = Column(Text, nullable=False)
    markdown_content = Column(Text, nullable=False)
    references = Column(JSON, nullable=False, default=list)
    contradiction_analysis = Column(JSON, nullable=True, default=list)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    session = relationship("ResearchSession", back_populates="report")
