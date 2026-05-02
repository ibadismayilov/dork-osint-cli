"""
Professional OSINT Module: DNS Enumeration, Reverse Lookup, Email Enumeration, Web Archive
Supports comprehensive reconnaissance for security audits and research.
"""

import socket
import re
import requests
from urllib.parse import urljoin, urlparse
from datetime import datetime
import json

try:
    import dns.resolver
    import dns.reversename
    import dns.zone
    HAS_DNSPYTHON = True
except ImportError:
    HAS_DNSPYTHON = False

# ====== DNS ENUMERATION ======

def enumerate_dns_records(domain, record_types=["A", "AAAA", "MX", "NS", "TXT", "SOA", "CNAME"]):
    """
    Enumerate all DNS records for a domain.
    Returns dict with record type as key and list of records as value.
    """
    results = {rtype: [] for rtype in record_types}
    
    if not HAS_DNSPYTHON:
        return {"error": "dnspython not installed. Install: pip install dnspython"}
    
    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = 5
        resolver.lifetime = 10
        
        for rtype in record_types:
            try:
                answers = resolver.resolve(domain, rtype)
                for rdata in answers:
                    results[rtype].append({
                        "value": str(rdata),
                        "ttl": answers.rrset.ttl if hasattr(answers, 'rrset') else None
                    })
            except dns.resolver.NXDOMAIN:
                results[rtype] = [{"error": "Domain does not exist"}]
                break
            except dns.resolver.NoAnswer:
                results[rtype] = []
            except Exception as e:
                results[rtype] = [{"error": str(e)}]
    except Exception as e:
        return {"error": f"DNS resolution failed: {str(e)}"}
    
    return results

def extract_nameservers(dns_records):
    """Extract nameserver information from DNS records."""
    ns_list = dns_records.get("NS", [])
    return [ns["value"] for ns in ns_list if "value" in ns]

def extract_mx_records(dns_records):
    """Extract mail server information from DNS records."""
    mx_list = dns_records.get("MX", [])
    return [mx["value"] for mx in mx_list if "value" in mx]

def extract_txt_records(dns_records):
    """Extract TXT records (SPF, DKIM, DMARC, etc.)."""
    txt_list = dns_records.get("TXT", [])
    records = {}
    for txt in txt_list:
        if "value" in txt:
            value = txt["value"].strip('"')
            if value.startswith("v=spf1"):
                records["SPF"] = value
            elif value.startswith("v=DMARC1"):
                records["DMARC"] = value
            elif "dkim" in value.lower():
                records["DKIM"] = value
            else:
                if "TXT" not in records:
                    records["TXT"] = []
                records["TXT"].append(value)
    return records

# ====== REVERSE DNS & ASN ======

def reverse_dns_lookup(ip_address):
    """Perform reverse DNS lookup on an IP address."""
    try:
        hostname = socket.gethostbyaddr(ip_address)
        return {
            "hostname": hostname[0],
            "aliases": hostname[1],
            "ips": hostname[2]
        }
    except socket.herror:
        return {"error": "Reverse DNS lookup failed"}
    except Exception as e:
        return {"error": str(e)}

def get_asn_info(ip_address):
    """Get ASN and network info from IP address using WHOIS data (via public APIs)."""
    try:
        # Using whois.cymru.com for ASN lookup
        response = requests.get(f"https://whois.cymru.com/cgi-bin/whois.cgi?ip={ip_address}&format=json", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                return data[0]
        return None
    except Exception:
        return None

def get_ip_geolocation(ip_address):
    """Get geolocation data for an IP address."""
    try:
        response = requests.get(f"https://ipapi.co/{ip_address}/json/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                "country": data.get("country_name"),
                "country_code": data.get("country_code"),
                "city": data.get("city"),
                "latitude": data.get("latitude"),
                "longitude": data.get("longitude"),
                "organization": data.get("org"),
                "isp": data.get("org")
            }
    except Exception:
        pass
    return None

# ====== EMAIL ENUMERATION ======

def extract_emails_from_domain(domain):
    """
    Extract potential email addresses from DNS records and common patterns.
    Useful for social engineering reconnaissance.
    """
    emails = set()
    
    # Get MX records
    try:
        if HAS_DNSPYTHON:
            resolver = dns.resolver.Resolver()
            answers = resolver.resolve(domain, "MX")
            for rdata in answers:
                mail_server = str(rdata.exchange).rstrip('.')
                emails.add(f"admin@{domain}")
                emails.add(f"info@{domain}")
                emails.add(f"contact@{domain}")
                emails.add(f"support@{domain}")
                emails.add(f"security@{domain}")
                emails.add(f"abuse@{domain}")
                emails.add(f"postmaster@{domain}")
    except:
        pass
    
    return list(emails)

def verify_email_existence(email, timeout=10):
    """
    Attempt to verify if an email exists (without sending).
    Uses SMTP server connection to check mailbox existence.
    Note: Many servers block this for security reasons.
    """
    try:
        domain = email.split("@")[1]
        
        # Get MX records
        if not HAS_DNSPYTHON:
            return {"status": "unknown", "reason": "dnspython not installed"}
        
        resolver = dns.resolver.Resolver()
        mx_records = resolver.resolve(domain, "MX")
        
        if not mx_records:
            return {"status": "no_mx", "reason": "No MX records found"}
        
        mx_host = str(mx_records[0].exchange).rstrip('.')
        
        # Try SMTP connection
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((mx_host, 25))
            
            if result == 0:
                # Could connect, but most servers don't allow VRFY anymore
                sock.close()
                return {"status": "likely_exists", "reason": "MX server is responding"}
            else:
                sock.close()
                return {"status": "unknown", "reason": "Could not connect to MX server"}
        except socket.timeout:
            return {"status": "unknown", "reason": "Timeout connecting to MX server"}
        except Exception as e:
            return {"status": "unknown", "reason": str(e)}
    except Exception as e:
        return {"status": "error", "reason": str(e)}

# ====== WEB ARCHIVE ======

def get_wayback_snapshots(domain, limit=10):
    """
    Get historical snapshots from Wayback Machine (archive.org).
    Useful for finding old pages, subdomains, and exposed information.
    """
    try:
        url = f"https://archive.org/wayback/available?url={domain}&output=json"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("archived_snapshots"):
                snapshots = data["archived_snapshots"].get("closest", {})
                if snapshots:
                    return {
                        "available": True,
                        "first_capture": data.get("archived_snapshots", {}).get("closest", {}).get("timestamp"),
                        "url": snapshots.get("url"),
                        "status": snapshots.get("status")
                    }
            return {"available": False}
        return {"error": "Failed to query Wayback Machine"}
    except Exception as e:
        return {"error": str(e)}

def get_wayback_calendar(domain):
    """Get list of all snapshots available on Wayback Machine for a domain."""
    try:
        url = f"https://archive.org/wayback/available?url={domain}&output=json"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            snapshots = data.get("archived_snapshots", {}).get("snapshots", [])
            return {
                "total_snapshots": len(snapshots),
                "snapshots": snapshots[:limit] if len(snapshots) > 0 else []
            }
    except:
        pass
    
    return {"total_snapshots": 0, "snapshots": []}

# ====== SUBDOMAIN EXTRACTION FROM WEB ARCHIVE ======

def extract_subdomains_from_archive(domain, limit=100):
    """
    Extract subdomains from Wayback Machine CDX records.
    Finds historical subdomains that may no longer be active.
    """
    subdomains = set()
    
    try:
        # Query CDX API for all URLs
        url = f"https://cdx.api.archive.org/v1/search?url=*.{domain}/*&matchType=domain&output=json&limit={limit}"
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            # Skip header row
            for row in data[1:]:
                if len(row) > 2:
                    original_url = row[2]
                    # Extract subdomain from URL
                    parsed = urlparse(original_url)
                    hostname = parsed.netloc
                    if hostname.endswith(f".{domain}"):
                        subdomains.add(hostname)
    except Exception:
        pass
    
    return list(subdomains)

# ====== COMPREHENSIVE RECON ======

def run_full_recon(domain, include_email_enum=True, include_wayback=True, include_asn=False):
    """
    Comprehensive OSINT recon on a domain.
    Returns consolidated report with all available information.
    """
    report = {
        "domain": domain,
        "timestamp": datetime.now().isoformat(),
        "dns": {},
        "nameservers": [],
        "mx_records": [],
        "txt_records": {},
        "emails": [],
        "wayback": {},
        "archive_subdomains": [],
        "asn_info": {}
    }
    
    # Phase 1: DNS Enumeration
    print("[*] Phase 1: DNS Enumeration...")
    dns_records = enumerate_dns_records(domain)
    report["dns"] = dns_records
    report["nameservers"] = extract_nameservers(dns_records)
    report["mx_records"] = extract_mx_records(dns_records)
    report["txt_records"] = extract_txt_records(dns_records)
    
    # Phase 2: Email Enumeration
    if include_email_enum:
        print("[*] Phase 2: Email Enumeration...")
        emails = extract_emails_from_domain(domain)
        report["emails"] = emails
    
    # Phase 3: Wayback Machine
    if include_wayback:
        print("[*] Phase 3: Web Archive Lookup...")
        report["wayback"] = get_wayback_snapshots(domain)
        report["archive_subdomains"] = extract_subdomains_from_archive(domain)
    
    # Phase 4: ASN Information (for primary IP)
    if include_asn and "A" in dns_records and dns_records["A"]:
        print("[*] Phase 4: ASN Lookup...")
        try:
            primary_ip = dns_records["A"][0]["value"]
            report["asn_info"] = get_asn_info(primary_ip) or {}
            geo_info = get_ip_geolocation(primary_ip)
            if geo_info:
                report["geolocation"] = geo_info
        except:
            pass
    
    return report

def format_recon_report(report):
    """Format recon report for terminal display."""
    output = []
    output.append(f"\n{'='*60}")
    output.append(f"OSINT RECONNAISSANCE REPORT: {report['domain']}")
    output.append(f"Generated: {report['timestamp']}")
    output.append(f"{'='*60}\n")
    
    # DNS Records
    if report.get("dns"):
        output.append("[DNS RECORDS]")
        for rtype, records in report["dns"].items():
            if records and not any("error" in str(r) for r in records):
                output.append(f"  {rtype}:")
                for record in records:
                    if "value" in record:
                        output.append(f"    - {record['value']}")
        output.append("")
    
    # Nameservers
    if report.get("nameservers"):
        output.append("[NAMESERVERS]")
        for ns in report["nameservers"]:
            output.append(f"  - {ns}")
        output.append("")
    
    # MX Records
    if report.get("mx_records"):
        output.append("[MAIL SERVERS]")
        for mx in report["mx_records"]:
            output.append(f"  - {mx}")
        output.append("")
    
    # TXT Records (SPF, DMARC, DKIM)
    if report.get("txt_records"):
        output.append("[SECURITY RECORDS]")
        for key, value in report["txt_records"].items():
            if isinstance(value, list):
                for v in value:
                    output.append(f"  {key}: {v}")
            else:
                output.append(f"  {key}: {value}")
        output.append("")
    
    # Emails
    if report.get("emails"):
        output.append("[POTENTIAL EMAIL ADDRESSES]")
        for email in report["emails"][:5]:
            output.append(f"  - {email}")
        if len(report["emails"]) > 5:
            output.append(f"  ... and {len(report['emails'])-5} more")
        output.append("")
    
    # Wayback
    if report.get("wayback") and report["wayback"].get("available"):
        output.append("[WEB ARCHIVE]")
        output.append(f"  First Capture: {report['wayback'].get('first_capture')}")
        if report.get("archive_subdomains"):
            output.append(f"  Historical Subdomains: {len(report['archive_subdomains'])}")
            for sub in report["archive_subdomains"][:5]:
                output.append(f"    - {sub}")
        output.append("")
    
    # ASN
    if report.get("asn_info"):
        output.append("[ASN INFORMATION]")
        for key, value in report["asn_info"].items():
            output.append(f"  {key}: {value}")
        output.append("")
    
    # Geolocation
    if report.get("geolocation"):
        output.append("[GEOLOCATION]")
        geo = report["geolocation"]
        output.append(f"  Country: {geo.get('country')} ({geo.get('country_code')})")
        output.append(f"  City: {geo.get('city')}")
        output.append(f"  Organization: {geo.get('organization')}")
        output.append("")
    
    return "\n".join(output)
