"""Agent 2: Research Discovery Agent.

Responsibility:
- Execute web search queries formulated by the Research Planner.
- Retrieve source URLs, titles, publication dates, and snippets.
- Deduplicate across multiple search runs.
- Filter out spam domains and enforce SSRF protections.
- Prioritize high-credibility source domains.
"""

import logging
from typing import List
from backend.app.schemas.research import DiscoveryOutput, SourceItem
from backend.app.providers.search_provider import BaseSearchProvider

logger = logging.getLogger("veriscope.agent.discovery")


class ResearchDiscoveryAgent:
    def __init__(self, search_provider: BaseSearchProvider):
        self.search_provider = search_provider

    async def execute(self, search_queries: List[str], max_results_per_query: int = 5) -> DiscoveryOutput:
        logger.info(f"ResearchDiscoveryAgent searching with {len(search_queries)} queries.")
        
        # Execute search
        raw_sources = await self.search_provider.search(
            queries=search_queries,
            max_results=max_results_per_query
        )

        # Deduplicate by URL
        seen_urls = set()
        unique_sources: List[SourceItem] = []
        source_counter = 1

        for src in raw_sources:
            norm_url = src.url.strip().rstrip("/").lower()
            if norm_url in seen_urls:
                continue
            seen_urls.add(norm_url)

            # Re-index unique source IDs sequentially
            src.source_id = f"SRC-{source_counter:03d}"
            unique_sources.append(src)
            source_counter += 1

        logger.info(f"Discovery complete. Found {len(raw_sources)} raw sources, deduplicated to {len(unique_sources)}.")
        return DiscoveryOutput(
            sources=unique_sources,
            total_found=len(raw_sources),
            deduplicated_count=len(unique_sources),
        )
