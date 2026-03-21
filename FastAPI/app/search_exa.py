"""
FocusFlow 3D - Person 3: Web Scraper Agent (Exa API).
Uses Exa for web search. Set EXA_API_KEY in env or .env.
Same interface as search.py: search_topic(), get_bookshelf_resources().
"""
import os
import re
from typing import List

# Optional: load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# In-memory cache for demo and rate limits
_cache: dict = {}
CACHE_MAX = 200


def _safe_str(s: str) -> str:
    """Strip problematic chars for Windows/JSON (e.g. emoji)."""
    if not s:
        return ""
    return re.sub(r"[^\x00-\x7F]+", " ", s).strip()[:500]


def _get_exa_client():
    """Lazy init Exa client (requires exa-py and EXA_API_KEY)."""
    from exa_py import Exa
    api_key = os.environ.get("EXA_API_KEY")
    if not api_key:
        raise ValueError("EXA_API_KEY is not set. Add it to .env or environment.")
    return Exa(api_key=api_key)


def get_cache_stats() -> dict:
    """Return cache stats for /vibe."""
    return {"cached_queries": len(_cache), "max": CACHE_MAX}


def search_topic(topic: str, max_results: int = 5, skip_cache: bool = False) -> List[dict]:
    """
    Search web for a topic using Exa.
    Returns list of {title, url, snippet} for bookshelf display.
    """
    key = (topic.strip().lower(), max_results)
    if not skip_cache and key in _cache:
        return _cache[key]
    try:
        exa = _get_exa_client()
        results = exa.search(
            query=topic,
            type="auto",
            num_results=max_results,
            contents={"text": {"max_characters": 20000}},
        )
        out = []
        for i, r in enumerate(results.results):
            url = getattr(r, "url", "") or ""
            text = getattr(r, "text", None) or getattr(r, "content", None) or ""
            if isinstance(text, list):
                text = " ".join(str(x) for x in text)[:500]
            else:
                text = _safe_str(str(text)[:500])
            out.append({
                "title": _safe_str(getattr(r, "title", "") or ""),
                "url": url,
                "snippet": text or _safe_str(getattr(r, "description", "") or ""),
                "score": 1.0 - (i * 0.1),
                "type": "video" if "youtube.com" in url or "youtu.be" in url else "article",
            })
        if not skip_cache and len(_cache) < CACHE_MAX:
            _cache[key] = out
        return out
    except Exception as e:
        return [{"title": "Error", "url": "", "snippet": str(e), "score": 0, "type": "article"}]


def search_youtube(topic: str, max_results: int = 5) -> List[dict]:
    """Search YouTube only (Exa restricted to youtube.com)."""
    try:
        exa = _get_exa_client()
        results = exa.search(
            query=topic,
            type="auto",
            num_results=max_results,
            include_domains=["youtube.com", "www.youtube.com"],
            contents={"text": {"max_characters": 20000}},
        )
        out = []
        for i, r in enumerate(results.results):
            url = getattr(r, "url", "") or ""
            text = getattr(r, "text", None) or getattr(r, "content", None) or ""
            if isinstance(text, list):
                text = " ".join(str(x) for x in text)[:500]
            else:
                text = _safe_str(str(text)[:500])
            out.append({
                "title": _safe_str(getattr(r, "title", "") or ""),
                "url": url,
                "snippet": text or _safe_str(getattr(r, "description", "") or ""),
                "score": 1.0 - (i * 0.1),
                "type": "video",
            })
        return out
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
