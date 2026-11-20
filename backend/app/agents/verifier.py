"""Agent 4: Fact Verification Agent.

Responsibility:
- Cross-examine every extracted claim against the complete evidence base.
- Assign an epistemic status:
  * SUPPORTED: Directly confirmed by credible source(s) without significant counter-evidence.
  * CONTRADICTED: Disproven by empirical data or authoritative contradictory sources.
  * PARTIALLY_SUPPORTED: Evidence supports aspects of the claim, but key details remain unverified.
  * INSUFFICIENT_EVIDENCE: Sources do not contain enough empirical data to confirm or deny.
  * CONFLICTING_EVIDENCE: Reputable sources present fundamentally opposing data.
- Detail supporting and contradicting source IDs.
- Highlight specific research limitations.
"""

import json
import logging
from typing import List
from backend.app.schemas.research import VerificationOutput, ClaimItem, SourceItem
from backend.app.providers.llm_provider import BaseLLMProvider, sanitize_untrusted_content

logger = logging.getLogger("veriscope.agent.verifier")

VERIFIER_SYSTEM_PROMPT = """You are the Senior Fact Verification Agent for VeriScope AI.
Your task is to independently evaluate factual claims against collected source snippets.

Verification Rules:
1. NEVER assume a claim is true merely because an LLM or author stated it. Look for empirical corroboration.
2. Select EXACTLY one verification status for each claim from:
   - SUPPORTED: Corroborated by explicit data in sources.
   - CONTRADICTED: Refuted by empirical facts or opposing authoritative measurements.
   - PARTIALLY_SUPPORTED: Some aspects true, but scope or magnitude is unproven.
   - INSUFFICIENT_EVIDENCE: Not enough data in the snippets to make an empirical determination.
   - CONFLICTING_EVIDENCE: Two or more reputable sources directly conflict on this point.
3. List all supporting source IDs and contradicting source IDs explicitly.
4. Provide a succinct, objective explanation outlining the empirical basis.
5. Mention any limitations (e.g. sample size, temporal gap).

Output ONLY a JSON object with this exact structure:
{
  "verifications": [
    {
      "claim_id": "CLM-001",
      "verification_status": "SUPPORTED",
      "explanation": "Specific rationale with evidence references",
      "supporting_source_ids": ["SRC-001"],
      "contradicting_source_ids": [],
      "limitations": "Description of any data gaps or caveats"
    }
  ]
}"""


class FactVerificationAgent:
    def __init__(self, llm_provider: BaseLLMProvider):
        self.llm = llm_provider

    async def execute(self, claims: List[ClaimItem], sources: List[SourceItem]) -> VerificationOutput:
        logger.info(f"FactVerificationAgent verifying {len(claims)} claims against {len(sources)} sources.")

        claims_data = [
            {"claim_id": c.claim_id, "claim": c.claim, "originating_sources": c.source_ids}
            for c in claims
        ]
        sources_data = [
            {
                "source_id": s.source_id,
                "title": s.title,
                "domain": s.domain,
                "date": s.publication_date,
                "snippet": sanitize_untrusted_content(s.snippet, max_chars=600),
            }
            for s in sources
        ]

        user_prompt = (
            f"EVIDENCE BASE (Sources):\n{json.dumps(sources_data, indent=2)}\n\n"
            f"CLAIMS TO VERIFY:\n{json.dumps(claims_data, indent=2)}\n\n"
            f"Evaluate every single claim strictly against the evidence base."
        )

        result = await self.llm.generate_structured(
            system_prompt=VERIFIER_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            schema_cls=VerificationOutput,
        )
        return result
