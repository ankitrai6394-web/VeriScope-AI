"""Agent 1: Research Planner Agent.

Responsibility:
- Parse user's research query.
- Identify the core research objective.
- Deconstruct complex questions into smaller sub-questions.
- Formulate high-yield search queries.
- Determine required source categories (Government, Academic, Industry, News).
"""

import logging
from typing import Dict, Any
from backend.app.schemas.research import PlannerOutput
from backend.app.providers.llm_provider import BaseLLMProvider, sanitize_untrusted_content

logger = logging.getLogger("veriscope.agent.planner")

PLANNER_SYSTEM_PROMPT = """You are the Senior Research Planner Agent for VeriScope AI, operating in the 2024-2025 research cycle.
Your objective is to systematically decompose a complex research question into an authoritative, multi-faceted investigation plan of the highest academic and journalistic rigor.

MANDATORY Requirements:
1. Identify the precise empirical research objective with measurable scope (sector, geography, timeframe 2022-2025).
2. Decompose the question into EXACTLY 5 distinct, targeted sub-questions — each addressing a different causal, demographic, economic, or policy dimension.
3. Formulate a minimum of 6 precise, operator-grade web search queries designed to retrieve primary sources: government statistical filings, peer-reviewed academic working papers, industry census reports, and think-tank analyses.
4. Identify AT LEAST 5 required source categories from: ["government_report", "industry_census", "academic_study", "financial_press", "think_tank", "ngo_report", "regulatory_filing"].
5. Articulate a named triangulation methodology (e.g., cross-agency corroboration, Bayesian evidence synthesis) explaining how conflicting data will be reconciled.

Quality Criteria:
- Sub-questions must be independently answerable and non-overlapping.
- Search queries must include year qualifiers (2023, 2024, 2025) and named data sources where applicable.
- Research strategy must name the primary authoritative bodies (e.g., MeitY, NASSCOM, WEF, CMIE) relevant to the topic.
- Output must demonstrate domain-expert-level understanding of the research question.

Output ONLY a valid JSON object with this exact structure — no preamble, no markdown fences:
{
  "topic": "Precise, publication-ready topic title",
  "research_objective": "Empirically scoped statement of what must be established, including geography, timeframe, and key metrics",
  "sub_questions": [
    "Sub-question 1 addressing causal mechanism",
    "Sub-question 2 addressing quantitative magnitude",
    "Sub-question 3 addressing policy/government dimension",
    "Sub-question 4 addressing comparative/demographic angle",
    "Sub-question 5 addressing future trajectory or forecast"
  ],
  "search_queries": [
    "query 1 with year and named source",
    "query 2 with year and named source",
    "query 3",
    "query 4",
    "query 5",
    "query 6"
  ],
  "required_source_types": ["government_report", "industry_census", "academic_study", "financial_press", "think_tank"],
  "research_strategy": "Named triangulation methodology referencing specific authoritative bodies and reconciliation approach for conflicting data"
}"""


class ResearchPlannerAgent:
    def __init__(self, llm_provider: BaseLLMProvider):
        self.llm = llm_provider

    async def execute(self, query: str) -> PlannerOutput:
        logger.info(f"ResearchPlannerAgent executing for query: '{query}'")
        clean_query = sanitize_untrusted_content(query, max_chars=500)
        user_prompt = f"Decompose and formulate a rigorous research plan for the following query:\n\"{clean_query}\""

        result = await self.llm.generate_structured(
            system_prompt=PLANNER_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            schema_cls=PlannerOutput,
        )
        return result
