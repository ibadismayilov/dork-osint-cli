# controller.py
from rich.console import Console
from dork import build_query
from api import search_google, CACHE_FILE
from ui_display import display_results
from history import show_history
from export import export_csv, export_json
from pagination import paginate_results

console = Console()
HISTORY_FILE = "history.txt"

def parse_comma_list(arg):
    if not arg:
        return None
    return [s.strip() for s in arg.split(",")] if "," in arg else arg

def run_search(args):
    # ---------------- HISTORY ----------------
    if args.history:
        show_history(HISTORY_FILE)
        return

    # ---------------- CLEAR CACHE ----------------
    if args.clear_cache:
        open(CACHE_FILE, "w").write("{}")
        console.print("[green]Cache cleared.[/green]")
        return

    # ---------------- BUILD QUERY ----------------
    query = build_query(
        keyword=args.keyword,
        pdf=args.pdf,
        login=args.login,
        site=args.site,
        intitle=parse_comma_list(args.intitle),
        inurl=parse_comma_list(args.inurl),
        intext=parse_comma_list(args.intext),
        filetype=args.filetype,
        date_filter=args.date
    )

    # ---------------- FETCH DATA ----------------
    retries = 3
    all_results = []
    while retries > 0:
        try:
            data = search_google(query, page=1, page_size=args.page_size)
            if data and data.get("results"):
                all_results.extend(data["results"])
            break
        except Exception as e:
            retries -= 1
            console.print(f"[red]Error fetching results: {e}. Retries left: {retries}[/red]")

    if not all_results:
        console.print("[red]No results found.[/red]")
        return

    # ---------------- PAGINATION ----------------
    all_results = paginate_results(
        query=query,
        all_results=[],
        display_func=display_results,
        page_size=args.page_size,
        history_file=HISTORY_FILE
    )

    # ---------------- EXPORT ----------------
    if args.export_json:
        console.print("\n[bold cyan]JSON export requested[/bold cyan]")
        export_json(all_results)

    if args.export_csv:
        console.print("\n[bold cyan]CSV export requested[/bold cyan]")
        export_csv(all_results)