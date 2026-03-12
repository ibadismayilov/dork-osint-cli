import os
from rich.console import Console
from core.dork import build_query
from core.api import search_google, CACHE_FILE
from ui.ui_display import display_results
from core.history import show_history
from utils.export import export_csv, export_json
from ui.pagination import paginate_results

console = Console()
DATA_DIR = "data"
HISTORY_FILE = os.path.join(DATA_DIR, "history.txt")

def parse_comma_list(arg):
    """
    Parses a comma-separated string into a list of strings.
    Example: "admin,login" -> ["admin", "login"]
    """
    if not arg:
        return None
    return [s.strip() for s in arg.split(",")] if "," in arg else arg

def run_search(args):
    """
    Main controller function to manage the search flow and OSINT operations.
    """
    
    # 1. HISTORY: Display search history if requested
    if args.history:
        show_history(HISTORY_FILE)
        return

    # 2. CLEAR CACHE: Reset the local API cache file
    if args.clear_cache:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "w") as f:
                f.write("{}")
            console.print("[bold green]✔ Cache cleared successfully.[/bold green]")
        return

    # 3. BUILD QUERY: Generate the search string based on filters or Recon mode
    query = build_query(
        keyword=args.keyword,
        subdomain_search=args.subdomain,
        pdf=args.pdf,
        login=args.login,
        site=args.site,
        intitle=parse_comma_list(args.intitle),
        inurl=parse_comma_list(args.inurl),
        intext=parse_comma_list(args.intext),
        filetype=args.filetype,
        date_filter=args.date
    )

    # Inform the user about the current operation mode
    if args.subdomain:
        console.print(f"[bold magenta]🔍 Recon Mode:[/bold magenta] Finding subdomains for [cyan]{args.subdomain}[/cyan]")
    else:
        console.print(f"[bold green]🔎 Search Query:[/bold green] [white]{query}[/white]")

    # 4. EXECUTION & PAGINATION:
    # Handles fetching results, resolving IPs, performing OSINT, and CLI navigation.
    # The 'paginate_results' function internally calls search_google.
    final_results = paginate_results(
        query=query,
        all_results=[], # Start with an empty list for the session
        display_func=display_results,
        page_size=args.page_size,
        history_file=HISTORY_FILE
    )

    # 5. MANUAL EXPORT (If arguments are explicitly provided):
    # Though pagination provides an export menu, these flags handle direct commands.
    if args.export_json and final_results:
        export_json(final_results)

    if args.export_csv and final_results:
        export_csv(final_results)

    console.print("\n[bold cyan]Session completed. Happy Hunting![/bold cyan]")