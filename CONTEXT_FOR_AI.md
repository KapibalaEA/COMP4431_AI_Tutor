# FocusFlow 3D – Person 3 Web Scraper (FastAPI)

## What this is
- **Role:** Person 3 = AI Agent / Web Scraper for a hackathon project (FocusFlow 3D).
- **Stack:** FastAPI, DuckDuckGo search, in-memory cache. Serves bookshelf resources to the frontend.

## Endpoints (all work when URL is correct)
- `GET /search?topic=...&max_results=5` – single-topic search
- `GET /bookshelf?topics=topic1,topic2&per_topic=3` – resources for bookshelf
- `POST /bookshelf` – body: `{"topics": ["merge sort", "binary search"], "per_topic": 3}`

**Important:** API base is `http://127.0.0.1:8000`. Use `/search` and `/bookshelf` — NOT `/docs/search` or `/docs/bookshelf` (those 404).

## How to run
```bash
cd FastAPI
.\venv\Scripts\activate   # Windows
uvicorn app.main:app --reload
```

## Known issues to fix (if possible)
1. **RuntimeWarning:** `duckduckgo_search` has been renamed to `ddgs`. Use `pip install ddgs` and `from ddgs import DDGS` in `app/search.py` to remove the warning.
2. **Venv issues (Windows):** We had to reinstall pydantic, pydantic-core, psycopg2-binary in the venv due to missing native modules (`_pydantic_core`, `_psycopg`). If the app won’t start, try: `pip install pydantic pydantic-core psycopg2-binary --no-cache-dir --force-reinstall`
3. **Database:** `main.py` connects to PostgreSQL at startup (for other routes like /posts). Person 3 only needs `/search` and `/bookshelf`; those work without DB. If you want the app to start without PostgreSQL, the DB connection block would need to be optional or moved.

## Folder structure
- `FastAPI/app/main.py` – FastAPI app, CORS, /search, /bookshelf, other routes
- `FastAPI/app/search.py` – `search_topic()`, `get_bookshelf_resources()`, DuckDuckGo + cache
- `FastAPI/requirements.txt` – dependencies
- `FastAPI/test_scraper_api.py` – quick test script (run with server up: `python test_scraper_api.py`)

## Optional next steps (from PRD)
- Quality scoring (relevance, recency, authority) and sort by score
- Content type per resource (article / video / paper / documentation)
- Pre-cache or demo cache for stable demo
