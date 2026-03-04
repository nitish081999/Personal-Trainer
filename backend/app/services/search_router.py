import logging
from datetime import date
from typing import Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class SearchUsageTracker:
    """Track daily search API usage."""

    def __init__(self):
        self._usage: dict[str, int] = {}
        self._current_date: str = ""
        self._reset_if_new_day()

    def _reset_if_new_day(self):
        today = date.today().isoformat()
        if today != self._current_date:
            self._current_date = today
            self._usage = {"tavily": 0, "serper": 0, "duckduckgo": 0}

    def record(self, provider: str):
        self._reset_if_new_day()
        self._usage[provider] = self._usage.get(provider, 0) + 1

    def can_use(self, provider: str) -> bool:
        self._reset_if_new_day()
        if provider == "tavily":
            return self._usage.get("tavily", 0) < settings.TAVILY_DAILY_LIMIT
        elif provider == "serper":
            return self._usage.get("serper", 0) < settings.SERPER_DAILY_LIMIT
        elif provider == "duckduckgo":
            return True  # No hard limit for DuckDuckGo
        return False

    def get_usage(self) -> dict:
        self._reset_if_new_day()
        return {
            "tavily_calls_used": self._usage.get("tavily", 0),
            "tavily_daily_limit": settings.TAVILY_DAILY_LIMIT,
            "serper_calls_used": self._usage.get("serper", 0),
            "serper_daily_limit": settings.SERPER_DAILY_LIMIT,
        }


search_usage = SearchUsageTracker()


async def _search_tavily(query: str, max_results: int = 10) -> Optional[list[dict]]:
    """Search using Tavily API."""
    if not settings.TAVILY_API_KEY or not search_usage.can_use("tavily"):
        return None

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": settings.TAVILY_API_KEY,
                    "query": query,
                    "max_results": max_results,
                    "include_raw_content": True,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            search_usage.record("tavily")
            results = []
            for r in data.get("results", []):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "content": r.get("raw_content", r.get("content", "")),
                    "source": "tavily",
                })
            return results
    except Exception as e:
        logger.error(f"Tavily search error: {e}")
        return None


async def _search_serper(query: str, max_results: int = 10) -> Optional[list[dict]]:
    """Search using Serper API (Google Search)."""
    if not settings.SERPER_API_KEY or not search_usage.can_use("serper"):
        return None

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                "https://google.serper.dev/search",
                headers={
                    "X-API-KEY": settings.SERPER_API_KEY,
                    "Content-Type": "application/json",
                },
                json={"q": query, "num": max_results},
            )
            resp.raise_for_status()
            data = resp.json()
            search_usage.record("serper")
            results = []
            for r in data.get("organic", []):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("link", ""),
                    "content": r.get("snippet", ""),
                    "source": "serper",
                })
            return results
    except Exception as e:
        logger.error(f"Serper search error: {e}")
        return None


async def _search_duckduckgo(query: str, max_results: int = 10) -> Optional[list[dict]]:
    """Search using DuckDuckGo (no API key needed)."""
    if not search_usage.can_use("duckduckgo"):
        return None

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                "https://api.duckduckgo.com/",
                params={"q": query, "format": "json", "no_html": 1},
            )
            resp.raise_for_status()
            data = resp.json()
            search_usage.record("duckduckgo")
            results = []

            # Abstract
            if data.get("Abstract"):
                results.append({
                    "title": data.get("Heading", ""),
                    "url": data.get("AbstractURL", ""),
                    "content": data["Abstract"],
                    "source": "duckduckgo",
                })

            # Related topics
            for topic in data.get("RelatedTopics", [])[:max_results]:
                if "Text" in topic:
                    results.append({
                        "title": topic.get("Text", "")[:100],
                        "url": topic.get("FirstURL", ""),
                        "content": topic.get("Text", ""),
                        "source": "duckduckgo",
                    })

            return results if results else None
    except Exception as e:
        logger.error(f"DuckDuckGo search error: {e}")
        return None


class SearchRouter:
    """Route search queries with failover."""

    @staticmethod
    async def search(query: str, max_results: int = 10) -> tuple[list[dict], str]:
        """
        Search with failover: Tavily -> Serper -> DuckDuckGo.
        Returns (results, api_used).
        """
        # Try Tavily
        results = await _search_tavily(query, max_results)
        if results:
            return results, "tavily"

        # Try Serper
        results = await _search_serper(query, max_results)
        if results:
            return results, "serper"

        # Try DuckDuckGo
        results = await _search_duckduckgo(query, max_results)
        if results:
            return results, "duckduckgo"

        return [], "none"

    @staticmethod
    def all_apis_exhausted() -> bool:
        """Check if all search APIs are exhausted."""
        return (
            not search_usage.can_use("tavily")
            and not search_usage.can_use("serper")
            and not search_usage.can_use("duckduckgo")
        )


search_router = SearchRouter()
