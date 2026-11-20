"""Unit Tests for All 7 Specialized Agents."""

import pytest
from backend.app.providers.llm_provider import MockLLMProvider
from backend.app.providers.search_provider import MockSearchProvider
from backend.app.agents.planner import ResearchPlannerAgent
from backend.app.agents.discovery import ResearchDiscoveryAgent
from backend.app.agents.extractor import EvidenceExtractionAgent
from backend.app.agents.verifier import FactVerificationAgent
from backend.app.agents.reliability import SourceReliabilityAgent
from backend.app.agents.contradiction import ContradictionDetectionAgent
from backend.app.agents.reporter import ReportGenerationAgent
from backend.app.schemas.research import VerificationStatus


@pytest.mark.asyncio
async def test_agent_1_planner():
    llm = MockLLMProvider()
    agent = ResearchPlannerAgent(llm)
    output = await agent.execute("Is artificial intelligence improving employment in India?")
    assert output.topic != ""
    assert len(output.sub_questions) >= 3
    assert len(output.search_queries) >= 2


@pytest.mark.asyncio
async def test_agent_2_discovery():
    search_provider = MockSearchProvider()
    agent = ResearchDiscoveryAgent(search_provider)
    output = await agent.execute(search_queries=["AI jobs India", "tech fresher employment"])
    assert len(output.sources) > 0
    assert output.sources[0].source_id == "SRC-001"
    assert output.sources[0].domain != ""


@pytest.mark.asyncio
async def test_agent_3_extractor():
    llm = MockLLMProvider()
    search_provider = MockSearchProvider()
    discovery_agent = ResearchDiscoveryAgent(search_provider)
    discovery_output = await discovery_agent.execute(["AI jobs"])

    agent = EvidenceExtractionAgent(llm)
    output = await agent.execute(discovery_output.sources)
    assert len(output.claims) > 0
    assert output.claims[0].claim_id.startswith("CLM-")
    assert len(output.claims[0].source_ids) > 0


@pytest.mark.asyncio
async def test_agent_4_verifier():
    llm = MockLLMProvider()
    search_provider = MockSearchProvider()
    discovery_agent = ResearchDiscoveryAgent(search_provider)
    discovery_output = await discovery_agent.execute(["AI jobs"])

    extractor = EvidenceExtractionAgent(llm)
    claims_output = await extractor.execute(discovery_output.sources)

    agent = FactVerificationAgent(llm)
    output = await agent.execute(claims=claims_output.claims, sources=discovery_output.sources)
    assert len(output.verifications) > 0
    statuses = [v.verification_status for v in output.verifications]
    assert VerificationStatus.SUPPORTED in statuses
    assert VerificationStatus.CONTRADICTED in statuses


@pytest.mark.asyncio
async def test_agent_5_source_reliability():
    llm = MockLLMProvider()
    search_provider = MockSearchProvider()
    discovery_agent = ResearchDiscoveryAgent(search_provider)
    discovery_output = await discovery_agent.execute(["AI jobs"])

    agent = SourceReliabilityAgent(llm)
    output = await agent.execute(discovery_output.sources)
    assert len(output.assessments) > 0
    assert 0.0 <= output.assessments[0].reliability_score <= 1.0


@pytest.mark.asyncio
async def test_agent_6_contradiction_detection():
    llm = MockLLMProvider()
    search_provider = MockSearchProvider()
    discovery_agent = ResearchDiscoveryAgent(search_provider)
    discovery_output = await discovery_agent.execute(["AI jobs"])

    extractor = EvidenceExtractionAgent(llm)
    claims_output = await extractor.execute(discovery_output.sources)

    verifier = FactVerificationAgent(llm)
    verifications_output = await verifier.execute(claims_output.claims, discovery_output.sources)

    agent = ContradictionDetectionAgent(llm)
    output = await agent.execute(
        claims=claims_output.claims,
        verifications=verifications_output.verifications,
        sources=discovery_output.sources,
    )
    assert output.has_contradictions is True
    assert len(output.contradictions) > 0
    assert output.contradictions[0].divergence_reason != ""


@pytest.mark.asyncio
async def test_agent_7_report_generation():
    llm = MockLLMProvider()
    search_provider = MockSearchProvider()

    planner = ResearchPlannerAgent(llm)
    plan = await planner.execute("AI employment India")

    discovery = ResearchDiscoveryAgent(search_provider)
    disc_output = await discovery.execute(plan.search_queries)

    extractor = EvidenceExtractionAgent(llm)
    claims_output = await extractor.execute(disc_output.sources)

    verifier = FactVerificationAgent(llm)
    verifications_output = await verifier.execute(claims_output.claims, disc_output.sources)

    reliability = SourceReliabilityAgent(llm)
    reliability_output = await reliability.execute(disc_output.sources)

    contradiction = ContradictionDetectionAgent(llm)
    contradictions_output = await contradiction.execute(
        claims_output.claims, verifications_output.verifications, disc_output.sources
    )

    reporter = ReportGenerationAgent(llm)
    report = await reporter.execute(
        query="AI employment India",
        plan=plan,
        sources=disc_output.sources,
        claims=claims_output.claims,
        verifications=verifications_output.verifications,
        reliability=reliability_output,
        contradictions=contradictions_output,
    )
    assert report.report_title != ""
    assert report.executive_summary != ""
    assert len(report.key_findings) > 0
    assert len(report.markdown_content) > 50
