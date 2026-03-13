import os
from rich.console import Console
from core.dork import build_query
from core.api import search_google, CACHE_FILE, run_active_scan
from ui.ui_display import display_results
from core.history import show_history, HISTORY_FILE
from utils.export import export_csv, export_json
from ui.pagination import paginate_results
from core.reporter import generate_html_report

console = Console()

def parse_comma_list(arg):
    if not arg:
        return None
    return [s.strip() for s in arg.split(",")] if "," in arg else arg


def run_search(args):
    """Main controller function to manage the search flow and OSINT operations."""

    if args.history:
        show_history(HISTORY_FILE)
        return

    if args.clear_cache:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                f.write("{}")
            console.print("[bold green]✔ Cache cleared successfully.[/bold green]")
        return

    query = build_query(
        keyword=args.keyword,
        subdomain_search=args.subdomain_search,
        mode=getattr(args, "mode", None),
        pdf=args.pdf,
        login=args.login,
        site=args.site,
        intitle=parse_comma_list(args.intitle),
        inurl=parse_comma_list(args.inurl),
        intext=parse_comma_list(args.intext),
        filetype=args.filetype,
        date_filter=getattr(args, "date", None),
    )

    if args.subdomain_search:
        console.print(f"[bold magenta]🔍 Recon Mode:[/bold magenta] Target: [cyan]{args.subdomain_search}[/cyan]")
    elif getattr(args, "mode", None):
        console.print(
            f"[bold yellow]🤖 Smart Mode ({args.mode}):[/bold yellow] Target: [cyan]{args.site if args.site else 'Global'}[/cyan]"
        )
    else:
        console.print(f"[bold green]🔎 Search Query:[/bold green] [white]{query}[/white]")

    final_results = []

    # 1) Passive results via SerpApi
    if query:
        passive_data = search_google(query, page=1, page_size=args.page_size)
        if passive_data and passive_data.get("results"):
            final_results.extend(passive_data["results"])

    # 2) Optional active subdomain brute-force (wordlist-based)
    if args.subdomain_search and getattr(args, "active", False):
        console.print(f"\n[bold yellow]🚀 Deep Recon Enabled:[/bold yellow] Starting active brute-force for [cyan]{args.subdomain_search}[/cyan]")
        active_results = run_active_scan(args.subdomain_search)

        if active_results:
            existing_domains = {res.get("domain") for res in final_results if res.get("domain")}
            for res in active_results:
                if res.get("domain") not in existing_domains:
                    final_results.append(res)

            console.print(f"[bold green]✔ Active scan finished. Total targets now: {len(final_results)}[/bold green]")

    # 3) Pagination & interactive display
    if final_results:
        final_results = paginate_results(
            query=query,
            all_results=final_results,
            display_func=display_results,
            page_size=args.page_size,
            history_file=HISTORY_FILE,
            args=args,
        )

        # 4) Exports
        if final_results:
            if args.export_json:
                export_json(final_results, full_path=args.export_path)

            if args.export_csv:
                export_csv(final_results, full_path=args.export_path)

            if args.export_html:
                target_name = args.site or args.subdomain_search or args.keyword or "General_Search"
                with console.status("[bold blue]Generating HTML Dashboard..."):
                    report_file = generate_html_report(final_results, target_name, output_path=args.export_path)
                console.print(f"[bold green]✔ HTML Report generated:[/bold green] [underline]{report_file}[/underline]")
    else:
        console.print("[yellow]⚠ No results found.[/yellow]")

    console.print("\n[bold cyan]Session completed. Happy Hunting![/bold cyan]")
