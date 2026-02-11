"""
Web search integration for executing X-ray queries.

Supports multiple backends:
- httpx-based Google search (default, no API key needed)
- SerpAPI (optional, for production use)
- Google Custom Search API (optional)
"""

from __future__ import annotations

import asyncio
import re
import urllib.parse
from dataclasses import dataclass, field
from typing import Optional

import httpx
from bs4 import BeautifulSoup

from .xray_engine import SearchQuery


@dataclass
class SearchResult:
    """A single search result."""

    title: str
    url: str
    snippet: str
    source_platform: str = ""
    posted_date: Optional[str] = None
    is_contract: bool = False
    is_c2c: bool = False
    relevance_score: float = 0.0


@dataclass
class SearchResultSet:
    """Collection of results from a single query execution."""

    query: SearchQuery
    results: list[SearchResult] = field(default_factory=list)
    total_found: int = 0
    error: Optional[str] = None


class WebSearchClient:
    """Executes search queries and parses results."""

    USER_AGENT = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    CONTRACT_SIGNALS = {
        "c2c", "corp to corp", "corp-to-corp", "corp 2 corp",
        "contract", "1099", "contract to hire", "c2h", "contingent",
        "6 month", "12 month", "long term contract", "short term contract",
    }

    C2C_SIGNALS = {
        "c2c", "corp to corp", "corp-to-corp", "corp 2 corp",
    }

    def __init__(
        self,
        serpapi_key: Optional[str] = None,
        google_api_key: Optional[str] = None,
        google_cse_id: Optional[str] = None,
        rate_limit_delay: float = 2.0,
    ):
        self._serpapi_key = serpapi_key
        self._google_api_key = google_api_key
        self._google_cse_id = google_cse_id
        self._rate_limit_delay = rate_limit_delay
        self._client = httpx.AsyncClient(
            headers={"User-Agent": self.USER_AGENT},
            timeout=30.0,
            follow_redirects=True,
        )

    async def execute_query(self, query: SearchQuery) -> SearchResultSet:
        """Execute a single search query and return parsed results."""
        if self._serpapi_key:
            return await self._search_serpapi(query)
        elif self._google_api_key and self._google_cse_id:
            return await self._search_google_api(query)
        else:
            return await self._search_google_scrape(query)

    async def execute_batch(
        self,
        queries: list[SearchQuery],
        max_concurrent: int = 3,
    ) -> list[SearchResultSet]:
        """Execute multiple queries with rate limiting."""
        results = []
        semaphore = asyncio.Semaphore(max_concurrent)

        async def _limited_search(q: SearchQuery) -> SearchResultSet:
            async with semaphore:
                result = await self.execute_query(q)
                await asyncio.sleep(self._rate_limit_delay)
                return result

        tasks = [_limited_search(q) for q in queries]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        return [
            r if isinstance(r, SearchResultSet)
            else SearchResultSet(query=queries[i], error=str(r))
            for i, r in enumerate(results)
        ]

    async def _search_serpapi(self, query: SearchQuery) -> SearchResultSet:
        """Search using SerpAPI (most reliable)."""
        params = {
            "q": query.query,
            "api_key": self._serpapi_key,
            "engine": "google",
            "num": 20,
            "gl": "us",
            "hl": "en",
        }
        try:
            resp = await self._client.get(
                "https://serpapi.com/search", params=params
            )
            resp.raise_for_status()
            data = resp.json()

            results = []
            for item in data.get("organic_results", []):
                result = SearchResult(
                    title=item.get("title", ""),
                    url=item.get("link", ""),
                    snippet=item.get("snippet", ""),
                    source_platform=query.platform.value,
                )
                self._classify_result(result)
                results.append(result)

            return SearchResultSet(
                query=query,
                results=results,
                total_found=len(results),
            )
        except Exception as e:
            return SearchResultSet(query=query, error=str(e))

    async def _search_google_api(self, query: SearchQuery) -> SearchResultSet:
        """Search using Google Custom Search API."""
        params = {
            "q": query.query,
            "key": self._google_api_key,
            "cx": self._google_cse_id,
            "num": 10,
            "gl": "us",
        }
        try:
            resp = await self._client.get(
                "https://www.googleapis.com/customsearch/v1", params=params
            )
            resp.raise_for_status()
            data = resp.json()

            results = []
            for item in data.get("items", []):
                result = SearchResult(
                    title=item.get("title", ""),
                    url=item.get("link", ""),
                    snippet=item.get("snippet", ""),
                    source_platform=query.platform.value,
                )
                self._classify_result(result)
                results.append(result)

            return SearchResultSet(
                query=query,
                results=results,
                total_found=int(data.get("searchInformation", {}).get("totalResults", 0)),
            )
        except Exception as e:
            return SearchResultSet(query=query, error=str(e))

    async def _search_google_scrape(self, query: SearchQuery) -> SearchResultSet:
        """Fallback: scrape Google search results (for development/testing)."""
        encoded = urllib.parse.quote_plus(query.query)
        url = f"https://www.google.com/search?q={encoded}&num=20&gl=us&hl=en"

        try:
            resp = await self._client.get(url)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            results = []
            for g in soup.select("div.g"):
                title_el = g.select_one("h3")
                link_el = g.select_one("a[href]")
                snippet_el = g.select_one("div.VwiC3b") or g.select_one("span.aCOpRe")

                if title_el and link_el:
                    href = link_el["href"]
                    if href.startswith("/url?q="):
                        href = href.split("/url?q=")[1].split("&")[0]
                        href = urllib.parse.unquote(href)

                    result = SearchResult(
                        title=title_el.get_text(),
                        url=href,
                        snippet=snippet_el.get_text() if snippet_el else "",
                        source_platform=query.platform.value,
                    )
                    self._classify_result(result)
                    results.append(result)

            return SearchResultSet(
                query=query,
                results=results,
                total_found=len(results),
            )
        except Exception as e:
            return SearchResultSet(query=query, error=str(e))

    def _classify_result(self, result: SearchResult):
        """Classify a result as contract/C2C based on content signals."""
        text = f"{result.title} {result.snippet}".lower()
        result.is_contract = any(term in text for term in self.CONTRACT_SIGNALS)
        result.is_c2c = any(term in text for term in self.C2C_SIGNALS)

        # Relevance scoring
        score = 0.0
        if result.is_contract:
            score += 3.0
        if result.is_c2c:
            score += 2.0
        if any(w in text for w in ["urgent", "immediate", "hot", "asap"]):
            score += 2.0
        if any(w in text for w in ["remote", "hybrid"]):
            score += 1.0
        if re.search(r"\$\d+", text):
            score += 1.0
        result.relevance_score = score

    async def close(self):
        await self._client.aclose()
