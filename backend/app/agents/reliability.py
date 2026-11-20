"""Agent 5: Source Reliability Agent.

Responsibility:
- Evaluate the credibility and methodological rigor of every discovered source.
- Analyze top-level domains (.gov, .edu, .org, commercial outlets).
- Distinguish between primary empirical sources and secondary reporting.
- Evaluate publication date and detect potentially outdated data.
- Provide a clear reliability score (0.0 to 1.0) and justification.
"""

import json
import logging
from typing import List
from backend.app.schemas.research import SourceReliabilityOutput, SourceItem
from backend.app.providers.llm_provider import BaseLLMProvider

logger = logging.getLogger("veriscope.agent.reliability")

RELIABILITY_SYSTEM_PROMPT = """You are the Senior Source Reliability Agent for VeriScope AI.
Your task is to analyze the quality, bias, and credibility of sources gathered during research.

Evaluation Criteria:
1. Domain Reputation & Governance: Government (.gov) and accredited academic institutions (.edu/.ac.in) possess high authority for statutory and peer-reviewed data.
2. Primary vs Secondary: Primary censuses/filings outrank secondary aggregations or opinion blogs.
3. Publication Date: Note whether findings from prior years may be superseded by subsequent tech shifts.
4. Methodological Transparency: Check if sources quote specific sample sizes, surveys, or regulatory records.
5. Provide a reliability score from 0.0 to 1.0.

Output ONLY a JSON object with this exact structure:
{
  "assessments": [
    {
      "source_id": "SRC-001",
      "domain": "example.org",
      "source_type": "industry",
      "reliability_score": 0.88,
      "rationale": "Clear transparent explanation of source credibility and limitations",
      "is_primary_source": true
    }
  ]
}"""


class SourceReliabilityAgent:
    def __init__(self, llm_provider: BaseLLMProvider):
        self.llm = llm_provider

    async def execute(self, sources: List[SourceItem]) -> SourceReliabilityOutput:
        logger.info(f"SourceReliabilityAgent evaluating {len(sources)} sources.")

        sources_data = [
            {
                "source_id": s.source_id,
                "title": s.title,
                "domain": s.domain,
                "date": s.publication_date,
                "source_type": s.source_type,
                "snippet": s.snippet[:500],
            }
            for s in sources
        ]

        user_prompt = (
            f"Assess the credibility, source type, and reliability of these {len(sources)} sources:\n\n"
            f"{json.dumps(sources_data, indent=2)}"
        )

        result = await self.llm.generate_structured(
            system_prompt=RELIABILITY_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            schema_cls=SourceReliabilityOutput,
        )
        return result
