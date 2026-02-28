"""
FocusFlow 3D - Person 3: Web Scraper Agent (minimal for short time)
Uses DuckDuckGo - no API key. Replace with Tavily/SerpAPI later if needed.
"""
from duckduckgo_search import DDGS
from typing import List
import re

# Simple in-memory cache so demo doesn't hit rate limits
_cache: dict = {}
CACHE_MAX = 200


def _safe_str(s: str) -> str:
    """Strip problematic chars for Windows/JSON (e.g. emoji)."""
    if not s:
        return ""
    return re.sub(r"[^\x00-\x7F]+", " ", s).strip()[:500]


def search_topic(topic: str, max_results: int = 5) -> List[dict]:
    """Search web for a topic. Returns list of {title, url, snippet}."""
    key = (topic.strip().lower(), max_results)
    if key in _cache:
        return _cache[key]
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(topic, max_results=max_results))
        out = [
            {
                "title": _safe_str(r.get("title", "")),
                "url": r.get("href", r.get("link", "")),
                "snippet": _safe_str(r.get("body", "")),
            }
            for r in results
        ]
        if len(_cache) < CACHE_MAX:
            _cache[key] = out
        return out
    except Exception as e:
        return [{"title": "Error", "url": "", "snippet": str(e)}]


def get_bookshelf_resources(topics: List[str], per_topic: int = 3) -> List[dict]:
    """For each topic, fetch resources and tag with topic. Frontend can show on bookshelf."""
    resources = []
    for topic in topics:
        if not topic or not topic.strip():
            continue
        topic = topic.strip()
        for item in search_topic(topic, max_results=per_topic):
            item["topic"] = topic
            resources.append(item)
    return resources
