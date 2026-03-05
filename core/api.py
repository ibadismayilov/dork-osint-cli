import os
import json
from serpapi import GoogleSearch
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")
CACHE_FILE = "cache.json"

# ---------------- CACHE ----------------
def load_cache():
    if not os.path.exists(CACHE_FILE):
        return {}
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=4)

# ---------------- GOOGLE SEARCH ----------------
def search_google(query, page=1, page_size=10):
    start = (page - 1) * page_size
    cache_key = f"{query}_page_{page}_{page_size}"
    cache = load_cache()

    if cache_key in cache:
        return cache[cache_key]

    params = {
        "engine": "google",
        "q": query,
        "api_key": API_KEY,
        "start": start,
        "num": page_size
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    organic = results.get("organic_results", [])
    total = results.get("search_information", {}).get("total_results", "Unknown")

    formatted = {"results": organic, "total": total}
    cache[cache_key] = formatted
    save_cache(cache)

    return formatted