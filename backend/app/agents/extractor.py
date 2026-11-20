"""Agent 3: Evidence Extraction Agent.

Responsibility:
- Parse text snippets from discovered sources.
- Identify discrete factual, statistical, and empirical claims.
- Assign unique Claim IDs (CLM-001, CLM-002, etc.).
- Tag claims with their originating source IDs (SRC-001, SRC-002, etc.).
- Classify evidence type (statistical, empirical, observational, definitional).
- Estimate model confidence score without altering author's original intent.
"""

import json
import logging
from typing import List
from backend.app.schemas.research import EvidenceExtractionOutput, SourceItem
from backend.app.providers.llm_provider import BaseLLMProvider, sanitize_untrusted_content

logger = logging.getLogger("veriscope.agent.extractor")

EXTRACTOR_SYSTEM_PROMPT = """You are the Senior Evidence Extraction Agent for VeriScope AI.
Your objective is to read source snippets and extract distinct, atomic factual assertions.

Guidelines:
1. Extract individual factual claims, statistics, rates, and empirical findings.
2. Do not merge separate assertions into compound claims.
3. Every claim MUST be associated with the exact source ID(s) where it was found (e.g. ["SRC-001"]).
4. Assign a unique sequential ID: CLM-001, CLM-002, etc.
5. Identify evidence type: 'statistical', 'empirical', 'observational', or 'definitional'.
6. Assign a model confidence score (0.0 to 1.0) assessing how clearly the evidence is stated.
7. Preserve the precise meaning of the source without exaggeration.

Output ONLY a JSON object with this exact structure:
{
  "claims": [
    {
      "claim_id": "CLM-001",
      "claim": "Specific factual assertion with metrics if present",
      "source_ids": ["SRC-001"],
      "evidence_type": "statistical",
      "confidence": 0.85
    }
  ]
}"""


class EvidenceExtractionAgent:
    def __init__(self, llm_provider: BaseLLMProvider):
        self.llm = llm_provider

    async def execute(self, sources: List[SourceItem]) -> EvidenceExtractionOutput:
        logger.info(f"EvidenceExtractionAgent processing {len(sources)} sources.")

        # Prepare sanitized source snippets representation
        sources_payload = []
        for s in sources:
            sources_payload.append({
                "source_id": s.source_id,
                "title": s.title,
                "domain": s.domain,
                "date": s.publication_date,
                "snippet": sanitize_untrusted_content(s.snippet, max_chars=800),
            })

        user_prompt = (
            f"Extract all key factual and statistical claims from the following {len(sources)} discovered sources:\n\n"
            f"{json.dumps(sources_payload, indent=2)}"
        )

        result = await self.llm.generate_structured(
            system_prompt=EXTRACTOR_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            schema_cls=EvidenceExtractionOutput,
        )
        return result
