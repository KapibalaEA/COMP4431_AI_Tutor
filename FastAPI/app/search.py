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


def get_cache_stats() -> dict:
    """Return cache stats for /vibe."""
    return {"cached_queries": len(_cache), "max": CACHE_MAX}


def search_topic(topic: str, max_results: int = 5, skip_cache: bool = False) -> List[dict]:
    """Search web for a topic. Returns list of {title, url, snippet, score, type}."""
    key = (topic.strip().lower(), max_results)
    if not skip_cache and key in _cache:
        return _cache[key]
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(topic, max_results=max_results))
        out = []
        for i, r in enumerate(results):
            url = r.get("href", r.get("link", ""))
            out.append({
                "title": _safe_str(r.get("title", "")),
                "url": url,
                "snippet": _safe_str(r.get("body", "")),
                "score": 1.0 - (i * 0.1),
                "type": "video" if "youtube.com" in url or "youtu.be" in url else "article",
            })
        if not skip_cache and len(_cache) < CACHE_MAX:
            _cache[key] = out
        return out
    except Exception as e:
        return [{"title": "Error", "url": "", "snippet": str(e), "score": 0, "type": "article"}]


def search_youtube(topic: str, max_results: int = 5) -> List[dict]:
    """Search YouTube only (DuckDuckGo video search)."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.videos(topic, max_results=max_results))
        return [
            {
                "title": _safe_str(r.get("title", "")),
                "url": r.get("url", r.get("link", "")),
                "snippet": _safe_str(r.get("description", "")),
                "score": 1.0 - (i * 0.1),
                "type": "video",
            }
            for i, r in enumerate(results)
        ]
    except Exception as e:
        return [{"title": "Error", "url": "", "snippet": str(e), "score": 0, "type": "video"}]


def get_bookshelf_resources(topics: List[str], per_topic: int = 3, skip_cache: bool = False) -> List[dict]:
    """For each topic, fetch resources and tag with topic. Frontend can show on bookshelf."""
    resources = []
    for t in topics:
        if not t or not t.strip():
            continue
        t = t.strip()
        for item in search_topic(t, max_results=per_topic, skip_cache=skip_cache):
            item["topic"] = t
            resources.append(item)
    return resources
