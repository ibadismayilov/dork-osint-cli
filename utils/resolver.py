import socket
from urllib.parse import urlparse

def get_ip_address(url):
    """
    Extracts the domain from a given URL and resolves it to an IPv4 address.
    Returns 'N/A' if the domain is missing, or 'Unknown' if resolution fails.
    """
    try:
        # Extract netloc (domain) from the URL
        domain = urlparse(url).netloc
        if not domain:
            return "N/A"
        # Perform DNS lookup to get the IP address
        return socket.gethostbyname(domain)
    except Exception:
        # Return Unknown if DNS resolution fails or network error occurs
        return "Unknown"