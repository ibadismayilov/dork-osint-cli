import os
import json
import socket
import requests
import concurrent.futures
from urllib.parse import urlparse
from dotenv import load_dotenv
from tqdm import tqdm

try:
    from serpapi import GoogleSearch
except ImportError:
    GoogleSearch = None

# Load environment variables from .env file
load_dotenv()
API_KEY = os.getenv("API_KEY")

# Define directory structure for data storage
CACHE_DIR = os.path.join("data", "cache")
CACHE_FILE = os.path.join(CACHE_DIR, "cache.json")
WORDLIST_PATH = os.path.join("data", "wordlists", "all.txt")

# ---------------- UTILS: IP & GEO RESOLVER ----------------

def get_ip_address(url):
    """
    Extracts the domain from a URL and resolves its IP address.
    """
    try:
        if url.startswith(("http://", "https://")):
            domain = urlparse(url).netloc
        else:
            domain = url
            
        if ":" in domain:
            domain = domain.split(":")[0]
        if not domain:
            return "N/A"
        return socket.gethostbyname(domain)
    except Exception:
        return "N/A"

def get_country_code(ip):
    """Retrieves the ISO country code (e.g., az, us, tr) for a given IP address."""
    if not ip or ip == "N/A" or ip.startswith("127.") or ip.startswith("10."):
        return ""
    try:
        response = requests.get(f"https://ipapi.co/{ip}/country/", timeout=3)
        if response.status_code == 200:
            code = response.text.strip().lower()
            return code if len(code) == 2 else ""
    except Exception:
        pass
    return ""

# ---------------- CACHE OPERATIONS ----------------

def load_cache():
    """
    Loads cached search results from the local JSON file.
    """
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def save_cache(cache):
    """
    Saves current search results to the cache directory.
    """
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=4)

# ---------------- GOOGLE SEARCH (PASSIVE) ----------------

def search_google(query, page=1, page_size=10):
    """
    Executes a Google search via SerpApi and enriches results with IP and Geo data.
    """
    start = (page - 1) * page_size
    cache_key = f"{query}_page_{page}_{page_size}"
    cache = load_cache()

    if cache_key in cache:
        return cache[cache_key]

    if not API_KEY:
        print("[!] SerpApi API_KEY is not set. Please set API_KEY in your .env file.")
        return {"results": [], "total": 0}

    if GoogleSearch is None:
        print("[!] Missing dependency: serpapi. Install with 'pip install google-search-results'.")
        return {"results": [], "total": 0}

    params = {
        "engine": "google",
        "q": query,
        "api_key": API_KEY,
        "start": start,
        "num": page_size
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
    except Exception as e:
        print(f"Error connecting to SerpApi: {e}")
        return {"results": [], "total": 0}

    organic_results = results.get("organic_results", [])
    total_results = results.get("search_information", {}).get("total_results", 0)

    formatted_results = []
    for item in organic_results:
        link = item.get("link")
        ip_addr = get_ip_address(link)
        
        formatted_results.append({
            "title": item.get("title", "No Title"),
            "link": link,
            "domain": item.get("display_link") or urlparse(link).netloc,
            "ip": ip_addr,
            "country_code": get_country_code(ip_addr),
            "snippet": item.get("snippet", ""),
            "source": "Passive (Google)"
        })

    formatted_data = {"results": formatted_results, "total": total_results}
    cache[cache_key] = formatted_data
    save_cache(cache)

    return formatted_data

# ---------------- RECON: ACTIVE SCAN & WILDCARD ----------------

def is_wildcard(domain):
    """Checks if the domain has a Wildcard DNS record."""
    random_sub = f"detect-wildcard-{os.urandom(4).hex()}"
    try:
        socket.gethostbyname(f"{random_sub}.{domain}")
        return True
    except socket.gaierror:
        return False

def check_subdomain_dns(sub, domain):
    """Helper for Active Scan to verify DNS records."""
    target = f"{sub}.{domain}"
    ip = get_ip_address(target)
    if ip != "N/A":
        return {
            "title": "Subdomain Discovered",
            "link": f"http://{target}",
            "domain": target,
            "ip": ip,
            "country_code": get_country_code(ip),
            "snippet": "Discovered via Active Wordlist Enumeration",
            "source": "Active (Wordlist)"
        }
    return None

def run_active_scan(domain, threads=100):
    """Performs Active Subdomain Enumeration using a wordlist."""
    if not os.path.exists(WORDLIST_PATH):
        print(f"[!] Error: Wordlist not found at {WORDLIST_PATH}")
        return []

    if is_wildcard(domain):
        print(f"[!] Warning: Wildcard DNS detected for {domain}. Skipping active scan.")
        return []

    with open(WORDLIST_PATH, "r", encoding="utf-8", errors="ignore") as f:
        subs = [line.strip() for line in f if line.strip()]

    print(f"[*] Starting Active Scan on {domain} ({len(subs)} entries)...")
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        future_to_sub = {executor.submit(check_subdomain_dns, sub, domain): sub for sub in subs}
        
        for future in tqdm(concurrent.futures.as_completed(future_to_sub), total=len(subs), desc="Scanning", unit="sub"):
            res = future.result()
            if res:
                results.append(res)
                
    return results