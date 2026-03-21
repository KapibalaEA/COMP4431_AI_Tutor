"""
Quick tests for Person 3: Web Scraper / Bookshelf API.
Run with: python test_scraper_api.py
(Start uvicorn first: uvicorn app.main:app --reload)
"""
import requests

BASE = "http://localhost:8000"

def test_search():
    r = requests.get(f"{BASE}/search", params={"topic": "binary search", "max_results": 2})
    assert r.status_code == 200, r.text
    data = r.json()
    assert "topic" in data and "results" in data
    assert isinstance(data["results"], list)
    print("GET /search OK:", len(data["results"]), "results")

def test_bookshelf_get():
    r = requests.get(f"{BASE}/bookshelf", params={"topics": "merge sort,binary search", "per_topic": 2})
    assert r.status_code == 200, r.text
    data = r.json()
    assert "resources" in data
    assert isinstance(data["resources"], list)
    print("GET /bookshelf OK:", len(data["resources"]), "resources")

def test_bookshelf_post():
    r = requests.post(f"{BASE}/bookshelf", json={"topics": ["merge sort", "divide and conquer"], "per_topic": 2})
    assert r.status_code == 200, r.text
    data = r.json()
    assert "resources" in data
    assert isinstance(data["resources"], list)
    print("POST /bookshelf OK:", len(data["resources"]), "resources")

if __name__ == "__main__":
    for name, fn in [("search", test_search), ("bookshelf GET", test_bookshelf_get), ("bookshelf POST", test_bookshelf_post)]:
        try:
            fn()
        except Exception as e:
            print(f"FAIL {name}:", e)
            raise
    print("All Person 3 API checks passed.")
