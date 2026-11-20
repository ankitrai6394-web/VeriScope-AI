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

PLANNER_SYSTEM_PROMPT = """You are the Senior Research Planner Agent for VeriScope AI.
Your objective is to systematically decompose a complex research question into an actionable, multi-faceted investigation plan.

You must:
1. Identify the core empirical research objective.
2. Break the question down into 3-5 distinct, targeted sub-questions.
3. Formulate 3-4 precise web search queries tailored to retrieve authoritative sources (academic papers, government datasets, trade bodies).
4. Identify which source types are essential (e.g. "government", "academic", "industry", "news").
5. Summarize the overarching research strategy.

Output ONLY a JSON object with this exact structure:
{
  "topic": "Concise topic title",
  "research_objective": "Clear statement of what needs to be verified",
  "sub_questions": ["sub-question 1", "sub-question 2", ...],
  "search_queries": ["query 1", "query 2", ...],
  "required_source_types": ["government", "academic", "industry", "news"],
  "research_strategy": "Description of triangulation methodology"
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
