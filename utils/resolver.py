import socket
import whois
import builtwith
from urllib.parse import urlparse

def get_ip_address(url):
    try:
        domain = urlparse(url).netloc
        if not domain: return "N/A"
        return socket.gethostbyname(domain)
    except Exception:
        return "Unknown"

def get_whois_info(url):
    """Fetches registration details of the domain."""
    try:
        domain = urlparse(url).netloc
        w = whois.whois(domain)
        return {
            "registrar": w.registrar,
            "creation_date": w.creation_date[0] if isinstance(w.creation_date, list) else w.creation_date,
            "expiration_date": w.expiration_date[0] if isinstance(w.expiration_date, list) else w.expiration_date,
            "country": w.country
        }
    except Exception:
        return None

def detect_technology(url):
    """Detects technologies used on the target website."""
    try:
        # We use builtwith to identify CMS, Web Servers, etc.
        results = builtwith.builtwith(url)
        return results
    except Exception:
        return {}