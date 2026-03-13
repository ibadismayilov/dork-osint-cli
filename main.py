import argparse
import sys
from controller import run_search

def main():
    parser = argparse.ArgumentParser(description="Pro Terminal Search & Recon System")
    
    # Keyword is optional
    parser.add_argument("keyword", nargs="?", help="Search keyword")
    
    # OSINT / Recon Mode
    parser.add_argument("--subdomain", "--subdomain_search", dest="subdomain_search", 
                        help="Target domain for subdomain discovery (e.g., apple.com)")
    
    # --- YENİ ƏLAVƏ: ACTIVE SCAN FLAG ---
    parser.add_argument("--active", action="store_true", help="Enable Active Wordlist Brute-force (Deep Recon)")
    
    # SMART DORKING MODES 
    parser.add_argument("--mode", choices=["recon", "leaks", "admin", "vuln", "deep_recon"], 
                        help="Pre-defined smart dorking templates")
    
    # Filters
    parser.add_argument("--pdf", action="store_true", help="Filter by PDF files")
    parser.add_argument("--login", action="store_true", help="Search for login pages")
    parser.add_argument("--site", help="Filter by specific site")
    parser.add_argument("--intitle", help="Filter by page title")
    parser.add_argument("--inurl", help="Filter by URL content")
    parser.add_argument("--intext", help="Filter by page text body")
    parser.add_argument("--filetype", help="Filter by file extension")
    parser.add_argument("--date", dest="date", help="Filter by date (e.g., 2024-01-01)")
    
    # System Actions
    parser.add_argument("--history", action="store_true", help="View search history")
    parser.add_argument("--clear-cache", action="store_true", help="Clear cached results")
    parser.add_argument("--page-size", type=int, default=10, help="Number of results per page")
    
    # Export Options 
    parser.add_argument("--export-csv", action="store_true", help="Export results to CSV")
    parser.add_argument("--export-json", action="store_true", help="Export results to JSON")
    parser.add_argument("--export-html", action="store_true", help="Export results to HTML Dashboard")
    parser.add_argument("--export-path", help="Custom export directory (default: data/exports)")
    
    # UI Options
    parser.add_argument("--no-interactive", action="store_true", help="Run in non-interactive mode (auto-export and quit)")
    
    args = parser.parse_args()

    if len(sys.argv) <= 1:
        parser.print_help()
        sys.exit(1)
        
    run_search(args)

if __name__ == "__main__":
    main()