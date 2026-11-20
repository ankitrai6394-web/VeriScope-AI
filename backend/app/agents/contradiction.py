"""Agent 6: Contradiction Detection Agent.

Responsibility:
- Compare verified claims, extracted statements, and source findings across independent sources.
- Detect direct or subtle contradictions (e.g. diverging metrics or opposing conclusions).
- Diagnose root causes for divergences:
  * Temporal differences (reporting across different years).
  * Population/sample variations (tier-1 universities vs. general population).
  * Metric definition nuances (mass IT hiring vs. total digital economy roles).
  * Differing survey methodologies.
- Provide reasoned synthesis rather than arbitrarily discarding one source.
"""

import json
import logging
from typing import List
from backend.app.schemas.research import ContradictionOutput, ClaimItem, VerificationItem, SourceItem
from backend.app.providers.llm_provider import BaseLLMProvider

logger = logging.getLogger("veriscope.agent.contradiction")

CONTRADICTION_SYSTEM_PROMPT = """You are the Senior Contradiction Detection Agent for VeriScope AI.
Your objective is to identify disagreements, contrasting statistics, and conflicting conclusions among research evidence.

Guidelines:
1. Thoroughly compare extracted statements across sources.
2. If two sources assert conflicting claims or disparate metrics, pinpoint the contradiction.
3. Diagnose the underlying cause of discrepancy:
   - "date": Differences in reporting timeframe or publication year.
   - "population": Differences in target population, industry sector, or geography.
   - "definition": Differing definitions (e.g., "tech services" vs "entire digital economy").
   - "methodology": Survey extrapolation vs. statutory payroll census.
4. Do NOT simply brand one source false; explain why both may hold true in their respective contexts.
5. If no contradictions exist, return "has_contradictions": false with an empty list.

Output ONLY a JSON object with this exact structure:
{
  "has_contradictions": true,
  "contradictions": [
    {
      "claim_ids": ["CLM-001", "CLM-002"],
      "conflicting_sources": ["SRC-001", "SRC-002"],
      "statement_a": "First statement or metric",
      "statement_b": "Contrasting statement or metric",
      "divergence_reason": "definition",
      "analysis": "In-depth explanation reconciling the apparent contradiction"
    }
  ]
}"""


class ContradictionDetectionAgent:
    def __init__(self, llm_provider: BaseLLMProvider):
        self.llm = llm_provider

    async def execute(
        self,
        claims: List[ClaimItem],
        verifications: List[VerificationItem],
        sources: List[SourceItem],
    ) -> ContradictionOutput:
        logger.info(f"ContradictionDetectionAgent comparing {len(claims)} claims across {len(sources)} sources.")

        context_payload = {
            "claims": [c.model_dump() for c in claims],
            "verifications": [v.model_dump() for v in verifications],
            "sources": [
                {"source_id": s.source_id, "title": s.title, "date": s.publication_date, "snippet": s.snippet[:400]}
                for s in sources
            ],
        }

        user_prompt = (
            f"Analyze the research evidence below and identify any contradictions, metric divergences, or conflicting conclusions:\n\n"
            f"{json.dumps(context_payload, indent=2)}"
        )

        result = await self.llm.generate_structured(
            system_prompt=CONTRADICTION_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            schema_cls=ContradictionOutput,
        )
        return result
