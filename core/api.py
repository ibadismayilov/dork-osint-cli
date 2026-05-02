import os
import json
import socket
import requests
import concurrent.futures
import time
from urllib.parse import urlparse
from dotenv import load_dotenv
from tqdm import tqdm
from random import choice

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
            "source": "Active (DNS)",
            "status_code": None,
            "http_title": None,
            "server": None,
            "ports": []
        }
    return None

# -------- HTTP PROBING & SERVICE DETECTION --------

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
]

def probe_subdomain_http(domain, timeout=5):
    """Probe HTTP/HTTPS on a subdomain and grab title & server info."""
    results = {}
    
    for protocol in ["https", "http"]:
        url = f"{protocol}://{domain}"
        try:
            headers = {"User-Agent": choice(USER_AGENTS)}
            response = requests.head(url, timeout=timeout, headers=headers, allow_redirects=True, verify=False)
            results[protocol] = {
                "status": response.status_code,
                "title": None,
                "server": response.headers.get("Server", "Unknown")
            }
            
            # Get title only for successful responses
            if response.status_code in [200, 301, 302, 403]:
                try:
                    get_resp = requests.get(url, timeout=timeout, headers=headers, verify=False)
                    if "text/html" in get_resp.headers.get("Content-Type", ""):
                        from html.parser import HTMLParser
                        class TitleParser(HTMLParser):
                            def __init__(self):
                                super().__init__()
                                self.title = None
                            def handle_starttag(self, tag, attrs):
                                if tag == "title" and not self.title:
                                    self.title_parsing = True
                            def handle_endtag(self, tag):
                                if tag == "title":
                                    self.title_parsing = False
                            def handle_data(self, data):
                                if hasattr(self, 'title_parsing') and self.title_parsing:
                                    self.title = data.strip()[:100]
                        
                        parser = TitleParser()
                        parser.feed(get_resp.text[:5000])
                        if parser.title:
                            results[protocol]["title"] = parser.title
                except:
                    pass
        except requests.exceptions.Timeout:
            pass
        except Exception:
            pass
        
        time.sleep(0.1)  # Rate limiting
    
    return results

def check_subdomain_ports(domain, ports=[80, 443, 8080, 8443, 22, 3306, 5432, 25, 587, 21], timeout=2):
    """Check common ports on a subdomain."""
    open_ports = []
    
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((domain, port))
            sock.close()
            
            if result == 0:
                open_ports.append(port)
            time.sleep(0.05)
        except:
            pass
    
    return open_ports

# -------- CERTIFICATE TRANSPARENCY LOGS --------

def get_ct_subdomains(domain, limit=100):
    """Fetch subdomains from Certificate Transparency logs (crt.sh)."""
    try:
        url = f"https://crt.sh/?q=%.{domain}&output=json"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            return []
        
        data = response.json()
        subdomains = set()
        
        for entry in data[:limit]:
            names = entry.get("name_value", "").split("\n")
            for name in names:
                name = name.strip()
                if name and name != domain and domain in name:
                    # Remove wildcard
                    if name.startswith("*."):
                        name = name[2:]
                    subdomains.add(name)
        
        return list(subdomains)
    except Exception:
        return []

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

def run_active_scan_extended(domain, threads=100, enable_http_probe=True, enable_port_scan=True, enable_ct_logs=True):
    """
    Extended Active Subdomain Enumeration with HTTP Probing, Port Scanning, and CT Logs.
    Keeps DNS results but enriches with additional data.
    """
    all_subdomains = set()
    results = []
    
    print("\n[*] Phase 1: Certificate Transparency Logs (crt.sh)...")
    ct_subs = get_ct_subdomains(domain)
    if ct_subs:
        print(f"[+] Found {len(ct_subs)} subdomains from CT logs")
        all_subdomains.update(ct_subs)
    
    print("\n[*] Phase 2: DNS Brute-Force (Wordlist)...")
    if not os.path.exists(WORDLIST_PATH):
        print(f"[!] Error: Wordlist not found at {WORDLIST_PATH}")
        return results

    if is_wildcard(domain):
        print(f"[!] Warning: Wildcard DNS detected for {domain}. Skipping brute-force.")
    else:
        with open(WORDLIST_PATH, "r", encoding="utf-8", errors="ignore") as f:
            subs = [line.strip() for line in f if line.strip()]

        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            future_to_sub = {executor.submit(check_subdomain_dns, sub, domain): sub for sub in subs}
            
            for future in tqdm(concurrent.futures.as_completed(future_to_sub), total=len(subs), desc="DNS Brute", unit="sub"):
                res = future.result()
                if res:
                    # Extract just the subdomain name
                    sub_name = res["domain"].replace(f".{domain}", "")
                    all_subdomains.add(sub_name)
    
    print(f"\n[*] Total unique subdomains found: {len(all_subdomains)}")
    
    # Phase 3: Enrich with HTTP Probing and Port Scanning
    if enable_http_probe or enable_port_scan:
        print("\n[*] Phase 3: HTTP Probing & Port Scanning...")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads // 2) as executor:
            futures = {}
            
            for sub in all_subdomains:
                full_domain = f"{sub}.{domain}" if sub else domain
                
                # Submit HTTP probe task
                if enable_http_probe:
                    futures[executor.submit(probe_subdomain_http, full_domain)] = ("http", full_domain)
                
                # Submit port scan task
                if enable_port_scan:
                    futures[executor.submit(check_subdomain_ports, full_domain)] = ("ports", full_domain)
            
            enriched_data = {}
            
            for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Enrich", unit="task"):
                task_type, target = futures[future]
                try:
                    result = future.result()
                    if target not in enriched_data:
                        enriched_data[target] = {"http_probe": None, "ports": []}
                    
                    if task_type == "http":
                        enriched_data[target]["http_probe"] = result
                    elif task_type == "ports":
                        enriched_data[target]["ports"] = result
                except:
                    pass
    
    # Build final results
    print("\n[*] Building final report...")
    for sub in all_subdomains:
        full_domain = f"{sub}.{domain}" if sub else domain
        ip = get_ip_address(full_domain)
        
        if ip == "N/A":
            continue
        
        result = {
            "title": "Subdomain Discovered",
            "link": f"http://{full_domain}",
            "domain": full_domain,
            "ip": ip,
            "country_code": get_country_code(ip),
            "snippet": "Active Enumeration",
            "source": "Active (Extended)",
            "status_code": None,
            "http_title": None,
            "server": None,
            "ports": []
        }
        
        # Add enriched data
        if full_domain in enriched_data:
            enriched = enriched_data[full_domain]
            
            # HTTP probe data (prefer HTTPS over HTTP)
            if enriched["http_probe"]:
                http_data = enriched["http_probe"].get("https") or enriched["http_probe"].get("http")
                if http_data:
                    result["status_code"] = http_data.get("status")
                    result["http_title"] = http_data.get("title")
                    result["server"] = http_data.get("server")
            
            # Port data
            if enriched["ports"]:
                result["ports"] = enriched["ports"]
        
        results.append(result)
    
    print(f"\n[+] Extended scan complete. Total results: {len(results)}")
    return results