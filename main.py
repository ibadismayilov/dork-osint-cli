import argparse
from controller import run_search

def main():
    parser = argparse.ArgumentParser(description="Pro Terminal Search & Recon System")
    parser.add_argument("keyword", nargs="?", help="Search keyword")
    
    # OSINT / Recon Mode
    parser.add_argument("--subdomain", help="Target domain for subdomain discovery (e.g., apple.com)")
    
    # Filters
    parser.add_argument("--pdf", action="store_true")
    parser.add_argument("--login", action="store_true")
    parser.add_argument("--site")
    parser.add_argument("--intitle")
    parser.add_argument("--inurl")
    parser.add_argument("--intext")
    parser.add_argument("--filetype")
    
    # System Actions
    parser.add_argument("--history", action="store_true")
    parser.add_argument("--clear-cache", action="store_true")
    parser.add_argument("--page-size", type=int, default=10)
    parser.add_argument("--export-csv", action="store_true")
    parser.add_argument("--export-json", action="store_true")
    parser.add_argument("--date")
    
    args = parser.parse_args()
    
    run_search(args)

if __name__ == "__main__":
    main()