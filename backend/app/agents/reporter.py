"""Agent 7: Report Generation Agent.

Responsibility:
- Synthesize all findings from prior agents into a comprehensive research report.
- Adhere strictly to the required 11-section report architecture:
  1. Research Overview
  2. Executive Summary
  3. Research Methodology
  4. Key Findings
  5. Verified Claims
  6. Contradicted Claims
  7. Conflicting Evidence
  8. Source Reliability Analysis
  9. Research Limitations
  10. Final Conclusion
  11. References
- Anchor every assertion to its verified claim ID (CLM-xxx) and source citation (SRC-xxx).
"""

import json
import logging
from typing import List, Dict, Any
from backend.app.schemas.research import (
    ReportGenerationOutput,
    PlannerOutput,
    SourceItem,
    ClaimItem,
    VerificationItem,
    SourceReliabilityOutput,
    ContradictionOutput,
)
from backend.app.providers.llm_provider import BaseLLMProvider

logger = logging.getLogger("veriscope.agent.reporter")

REPORTER_SYSTEM_PROMPT = """You are the Lead Research Report Generation Agent for VeriScope AI.
Your objective is to generate an authoritative, citation-backed investigative research report.

Report Structure Requirements:
1. Title and Executive Summary (high-level synthesis).
2. Research Methodology (triangulation and verification approach).
3. Key Findings (bulleted highlights).
4. Verified Claims (claims confirmed by empirical evidence).
5. Contradicted Claims (claims refuted by data).
6. Conflicting Evidence (subtle divergences explained by date/definition).
7. Source Reliability Analysis (assessment of institutional authority).
8. Research Limitations (data gaps, sample limits).
9. Final Conclusion.
10. Explicit markdown rendering containing all the above sections formatted professionally.

Every key assertion MUST cite the relevant Claim ID (e.g. [CLM-001]) and Source ID (e.g. [SRC-001]).
Do not invent any facts not present in the research evidence.

Output ONLY a JSON object with this exact structure:
{
  "report_title": "Comprehensive Report Title",
  "executive_summary": "Thorough executive summary of findings",
  "methodology": "Detailed description of research methodology",
  "key_findings": ["Finding 1", "Finding 2", ...],
  "limitations": "Explicit discussion of data constraints",
  "conclusion": "Final actionable conclusion",
  "markdown_content": "# Comprehensive Markdown Dossier..."
}"""


class ReportGenerationAgent:
    def __init__(self, llm_provider: BaseLLMProvider):
        self.llm = llm_provider

    async def execute(
        self,
        query: str,
        plan: PlannerOutput,
        sources: List[SourceItem],
        claims: List[ClaimItem],
        verifications: List[VerificationItem],
        reliability: SourceReliabilityOutput,
        contradictions: ContradictionOutput,
    ) -> ReportGenerationOutput:
        logger.info(f"ReportGenerationAgent compiling report for: '{query}'")

        payload = {
            "query": query,
            "topic": plan.topic,
            "objective": plan.research_objective,
            "sub_questions": plan.sub_questions,
            "sources": [
                {
                    "source_id": s.source_id,
                    "title": s.title,
                    "domain": s.domain,
                    "date": s.publication_date,
                    "type": s.source_type,
                }
                for s in sources
            ],
            "claims": [c.model_dump() for c in claims],
            "verifications": [v.model_dump() for v in verifications],
            "reliability": [r.model_dump() for r in reliability.assessments],
            "contradictions": [c.model_dump() for c in contradictions.contradictions],
        }

        user_prompt = (
            f"Generate a comprehensive, 11-section research report from the assembled multi-agent evidence below:\n\n"
            f"{json.dumps(payload, indent=2)}"
        )

        result = await self.llm.generate_structured(
            system_prompt=REPORTER_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            schema_cls=ReportGenerationOutput,
        )
        return result
