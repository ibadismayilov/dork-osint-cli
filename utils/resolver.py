import socket
from urllib.parse import urlparse

try:
    import whois
except ImportError:
    whois = None

try:
    import builtwith
except ImportError:
    builtwith = None

def get_ip_address(url):
    try:
        domain = urlparse(url).netloc
        if not domain: return "N/A"
        return socket.gethostbyname(domain)
    except Exception:
        return "Unknown"

def get_whois_info(url):
    """Fetches registration details of the domain."""
    if whois is None:
        return None

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
    if builtwith is None:
        return {}

    try:
        # We use builtwith to identify CMS, Web Servers, etc.
        return builtwith.builtwith(url)
    except Exception:
        return {}