import argparse
import sys
from controller import run_search

def main():
    parser = argparse.ArgumentParser(
        description="Pro Terminal Search & Recon System",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument("keyword", nargs="?", help="Main search term (e.g., 'admin panel')")
    
    discovery = parser.add_argument_group("Discovery Options")
    discovery.add_argument("--subdomain", "--subdomain_search", dest="subdomain_search", metavar="example.com", help="Target domain for subdomain discovery (e.g., apple.com)")
    discovery.add_argument("--active", action="store_true", help="Enable active wordlist brute-force for subdomain enumeration")
    discovery.add_argument("--extended", action="store_true", help="Enable extended active scan: HTTP probing, port scanning, and CT logs (combines all below)")
    discovery.add_argument("--http-probe", action="store_true", help="Check HTTP/HTTPS responses and grab status codes, titles, and server info")
    discovery.add_argument("--port-scan", action="store_true", help="Scan common ports (80, 443, 8080, 22, 3306, etc.) on discovered subdomains")
    discovery.add_argument("--ct-logs", action="store_true", help="Query Certificate Transparency logs (crt.sh) for additional subdomains")
    discovery.add_argument("--recon", action="store_true", help="Full OSINT reconnaissance (DNS records, emails, web archive, ASN/geolocation)")
    discovery.add_argument("--dns-enum", action="store_true", help="Enumerate DNS records (A, AAAA, MX, NS, TXT, SOA, CNAME)")
    discovery.add_argument("--dns-records", metavar="TYPE", help="Specific DNS record types to query (comma-separated: A,MX,NS,TXT,SOA,CNAME,AAAA)")
    discovery.add_argument("--emails", action="store_true", help="Enumerate potential email addresses from domain")
    discovery.add_argument("--archive", action="store_true", help="Query Wayback Machine for historical snapshots and subdomains")
    discovery.add_argument("--asn", action="store_true", help="Perform ASN lookup and geolocation analysis on resolved IPs")
    discovery.add_argument("--reverse-dns", metavar="IP", help="Perform reverse DNS lookup on an IP address")
    discovery.add_argument("--mode", choices=["recon", "leaks", "admin", "vuln", "deep_recon"], help="Pre-defined smart dorking templates")
    
    filters = parser.add_argument_group("Filters")
    filters.add_argument("--site", metavar="SITE", help="Limit results to a specific domain")
    filters.add_argument("--pdf", action="store_true", help="Shortcut for `filetype:pdf")
    filters.add_argument("--login", action="store_true", help="Shortcut for `inurl:login` ")
    filters.add_argument("--intitle", metavar="TITLE", help="Filter by page title")
    filters.add_argument("--inurl", metavar="URL", help="Filter by URL content")
    filters.add_argument("--intext", metavar="TEXT", help="Filter by page text body")
    filters.add_argument("--filetype", metavar="EXT", help="Filter by file extension")
    filters.add_argument("--date", dest="date", help="Filter by date (e.g., 2024-01-01)")
    
    system = parser.add_argument_group("System & UI Options")
    system.add_argument("--history", action="store_true", help="View search history")
    system.add_argument("--clear-cache", action="store_true", help="Clear cached results")
    system.add_argument("--page-size", type=int, default=10, help="Number of results per page")
    system.add_argument("--no-interactive", action="store_true", help="Run non-interactive mode (auto-export and quit)")
    
    exports = parser.add_argument_group("Export Options")
    exports.add_argument("--export-csv", action="store_true", help="Export results to CSV")
    exports.add_argument("--export-json", action="store_true", help="Export results to JSON")
    exports.add_argument("--export-yaml", action="store_true", help="Export results to YAML")
    exports.add_argument("--export-txt", action="store_true", help="Export results to TXT domain list")
    exports.add_argument("--export-html", action="store_true", help="Export results to HTML Dashboard")
    exports.add_argument("--export-path", metavar="PATH", help="Custom export directory (default: data/exports)")
    exports.add_argument("--compress", action="store_true", help="Compress exports with gzip")
    exports.add_argument("--silent", action="store_true", help="Suppress export confirmation messages")
    
    args = parser.parse_args()

    if len(sys.argv) <= 1:
        parser.print_help()
        sys.exit(1)
        
    run_search(args)

if __name__ == "__main__":
    main()