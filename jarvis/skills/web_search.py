"""Web Search Skill for JARVIS using DuckDuckGo (free, no API key needed).

Falls back to SerpAPI if SERPAPI_KEY is set in .env.
Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5
"""

import os
import time
import logging
import requests
from urllib.parse import quote_plus

from jarvis.skills.base import Skill, SkillResult

logger = logging.getLogger(__name__)


class WebSearchSkill(Skill):
    """Web search using DuckDuckGo (free) or SerpAPI (optional)."""

    def __init__(self):
        super().__init__()
        self._name = "web_search"
        self._description = "Search the web for current information. Returns top 5 results."
        self._parameters = {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query"}
            },
            "required": ["query"],
        }
        self._serpapi_key = os.getenv("SERPAPI_KEY")  # optional
        self._timeout = 5

    def execute(self, **kwargs) -> SkillResult:
        start = time.time()

        is_valid, error_msg = self.validate_parameters(**kwargs)
        if not is_valid:
            return SkillResult(success=False, result=None, error_message=error_msg,
                               execution_time_ms=int((time.time() - start) * 1000))

        query = kwargs["query"]

        # Try SerpAPI first if key is available
        if self._serpapi_key and "your_" not in self._serpapi_key:
            return self._search_serpapi(query, start)

        # Default: DuckDuckGo Instant Answer API (free, no key)
        return self._search_duckduckgo(query, start)

    def _search_duckduckgo(self, query: str, start: float) -> SkillResult:
        """Use DuckDuckGo Instant Answer API — completely free."""
        try:
            resp = requests.get(
                "https://api.duckduckgo.com/",
                params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1},
                timeout=self._timeout,
                headers={"User-Agent": "JARVIS/1.0"},
            )
            resp.raise_for_status()
            data = resp.json()

            results = []
            # Abstract (main answer)
            if data.get("AbstractText"):
                results.append({
                    "position": 1,
                    "title": data.get("Heading", query),
                    "url": data.get("AbstractURL", ""),
                    "description": data["AbstractText"],
                })

            # Related topics
            for i, topic in enumerate(data.get("RelatedTopics", [])[:4], len(results) + 1):
                if isinstance(topic, dict) and topic.get("Text"):
                    results.append({
                        "position": i,
                        "title": topic.get("Text", "")[:60],
                        "url": topic.get("FirstURL", ""),
                        "description": topic.get("Text", ""),
                    })

            if not results:
                # DuckDuckGo had no instant answer — return a helpful message
                return SkillResult(
                    success=True,
                    result={
                        "query": query,
                        "results": [{
                            "position": 1,
                            "title": f"Search: {query}",
                            "url": f"https://duckduckgo.com/?q={quote_plus(query)}",
                            "description": f"No instant answer found. Search DuckDuckGo for '{query}'.",
                        }],
                        "total_results": 1,
                        "source": "duckduckgo",
                    },
                    execution_time_ms=int((time.time() - start) * 1000),
                )

            elapsed = int((time.time() - start) * 1000)
            logger.info(f"DuckDuckGo search '{query}' completed in {elapsed}ms")
            return SkillResult(
                success=True,
                result={"query": query, "results": results[:5],
                        "total_results": len(results), "source": "duckduckgo"},
                execution_time_ms=elapsed,
            )

        except Exception as e:
            elapsed = int((time.time() - start) * 1000)
            logger.error(f"DuckDuckGo search failed: {e}")
            return SkillResult(success=False, result=None,
                               error_message=f"Web search failed: {e}",
                               execution_time_ms=elapsed)

    def _search_serpapi(self, query: str, start: float) -> SkillResult:
        """Use SerpAPI (100 free searches/month)."""
        try:
            resp = requests.get(
                "https://serpapi.com/search",
                params={"q": query, "api_key": self._serpapi_key, "num": 5},
                timeout=self._timeout,
            )
            resp.raise_for_status()
            data = resp.json()
            organic = data.get("organic_results", [])
            results = [
                {"position": i + 1, "title": r.get("title", ""),
                 "url": r.get("link", ""), "description": r.get("snippet", "")}
                for i, r in enumerate(organic[:5])
            ]
            elapsed = int((time.time() - start) * 1000)
            logger.info(f"SerpAPI search '{query}' completed in {elapsed}ms")
            return SkillResult(
                success=True,
                result={"query": query, "results": results,
                        "total_results": len(results), "source": "serpapi"},
                execution_time_ms=elapsed,
            )
        except Exception as e:
            elapsed = int((time.time() - start) * 1000)
            logger.error(f"SerpAPI search failed: {e}")
            return self._search_duckduckgo(query, start)
