import webbrowser
import time
from pathlib import Path
from urllib.parse import urlparse
from rich.console import Console
from rich.panel import Panel
from core.history import save_history
from core.api import search_google
from ui.ui_display import display_results, show_full_snippet
from utils.export import export_json, export_csv, export_txt, export_yaml
from core.reporter import generate_html_report

console = Console()


def _get_result_domain(result):
    domain = result.get("domain")
    if domain:
        return domain
    link = result.get("link", "")
    return urlparse(link).netloc


def _unique_domains(results):
    return sorted({_get_result_domain(item) for item in results if _get_result_domain(item)})


def _filter_subdomain_results(results, target_domain):
    return [item for item in results if target_domain in _get_result_domain(item)]


def _get_export_formats(args, default_formats=None):
    formats = []
    if args is None:
        return default_formats or ["json"]

    if getattr(args, "export_json", False):
        formats.append("json")
    if getattr(args, "export_csv", False):
        formats.append("csv")
    if getattr(args, "export_txt", False):
        formats.append("txt")
    if getattr(args, "export_yaml", False):
        formats.append("yaml")
    if getattr(args, "export_html", False):
        formats.append("html")

    if formats:
        return formats

    if getattr(args, "no_interactive", False):
        return default_formats or ["json"]

    console.print("\n[bold white]Which export format do you want?[/bold white]")
    console.print("1. JSON")
    console.print("2. CSV")
    console.print("3. TXT (domain list only)")
    console.print("4. YAML")
    console.print("5. HTML")
    console.print("6. All formats")
    console.print("7. Skip export")

    choice = input("\nSelect an option (1-7): ").strip()
    if choice == "1":
        return ["json"]
    if choice == "2":
        return ["csv"]
    if choice == "3":
        return ["txt"]
    if choice == "4":
        return ["yaml"]
    if choice == "5":
        return ["html"]
    if choice == "6":
        return ["json", "csv", "txt", "yaml", "html"]
    return []


def _export_data(payload, target_name, formats, args):
    if not formats:
        return

    compress = getattr(args, "compress", False)
    silent = getattr(args, "silent", False)

    if "json" in formats:
        export_json(payload, target_name=target_name, full_path=getattr(args, "export_path", None), silent=silent, compress=compress)
    if "csv" in formats:
        export_csv(payload, target_name=target_name, full_path=getattr(args, "export_path", None), silent=silent)
    if "txt" in formats:
        export_txt(payload, target_name=target_name, full_path=getattr(args, "export_path", None), silent=silent)
    if "yaml" in formats:
        export_yaml(payload, target_name=target_name, full_path=getattr(args, "export_path", None), silent=silent, compress=compress)
    if "html" in formats and isinstance(payload, (list, dict)):
        report_target = target_name or "Search_Report"
        export_path = getattr(args, "export_path", None)
        if export_path:
            html_subdir = Path(export_path) / "html"
        else:
            html_subdir = Path("data") / "exports" / "html"
        with console.status("[bold blue]Generating HTML Dashboard...[/bold blue]"):
            if isinstance(payload, dict) and "subdomains" in payload:
                # Convert subdomain list to list of dicts for template
                html_payload = [{"domain": d} for d in payload["subdomains"]]
            else:
                html_payload = payload if isinstance(payload, list) else [payload]
            report_file = generate_html_report(html_payload, report_target, output_path=str(html_subdir))
        if not silent:
            console.print(f"[green]HTML report generated to {report_file}[/green]")
        try:
            import webbrowser
            browser_url = Path(report_file).resolve().as_uri()
            webbrowser.open(browser_url)
            if not silent:
                console.print("[dim cyan]ℹ Opening dashboard in your browser...[/dim cyan]")
        except Exception as e:
            if not silent:
                console.print(f"[red]Could not open browser automatically: {e}[/red]")


def paginate_results(query, all_results, display_func, page_size, history_file, args=None):
    """
    Handles pagination, user interaction, and final export options.
    """
    page = 1
    global_index = 0
    total_results = None
    analyzed_target = None

    while True:
        end_index = global_index + page_size

        # API fetch logic with loading spinner
        if end_index > len(all_results) and not (page == 1 and len(all_results) > 0):
            with console.status(f"[cyan]Loading page {page}...[/cyan]", spinner="dots"):
                retries = 3
                while retries > 0:
                    try:
                        data = search_google(query, page=page, page_size=page_size)
                        if data and data.get("results"):
                            all_results.extend(data["results"])
                            if total_results is None:
                                total_results = data.get("total", "Unknown")
                        break
                    except Exception as e:
                        retries -= 1
                        console.print(f"[red]Error fetching results: {e}. Retries left: {retries}[/red]")
                    time.sleep(0.2)

            if global_index >= len(all_results):
                console.print("[yellow]No more results found.[/yellow]")
                break

        current_page_results = all_results[global_index:end_index]

        if not current_page_results:
            console.print("[yellow]No results to display.[/yellow]")
            break

        # Header panel for the current page
        panel_text = f"[bold green]Page {page}[/bold green] | Results {global_index+1}-{global_index+len(current_page_results)}"
        if total_results != "Unknown":
            panel_text += f" of {total_results}"
        console.print(Panel(panel_text))

        # Render the table for the current page
        display_func(current_page_results, start_index=global_index)

        # User Actions Menu
        console.print("\n[bold white]Actions:[/bold white]")
        console.print("[cyan][ID][/cyan] Open Link & Info | [cyan]n[/cyan] Next | [cyan]p[/cyan] Previous | [cyan]q[/cyan] Quit & Export")
        
        if args and getattr(args, 'no_interactive', False):
            action = "q"  # Auto-quit in non-interactive mode
            console.print("\n[italic cyan]Non-interactive mode: Auto-quitting and exporting...[/italic cyan]")
        else:
            action = input("\nChoose an action: ").strip().lower()

        if action.isdigit():
            sel = int(action)
            if 0 < sel <= len(all_results):
                target = all_results[sel - 1]
                analyzed_target = target
                webbrowser.open(target.get("link", ""))
                save_history(history_file, query, target.get("link", ""))
                show_full_snippet(target)
            else:
                console.print("[red]Invalid ID. Please choose a number from the table.[/red]")

        elif action == "n":
            page += 1
            global_index += page_size

        elif action == "p":
            if page > 1:
                page -= 1
                global_index -= page_size
            else:
                console.print("[yellow]You are already on the first page.[/yellow]")

        elif action == "q":
            break
        else:
            console.print("[red]Unknown action. Please try again.[/red]")

    # --- FINAL EXPORT WORKFLOW ---
    if all_results:
        console.print("\n" + "="*50)
        console.print("[bold yellow]SEARCH SESSION FINISHED[/bold yellow]")
        console.print(f"Total results collected: [bold green]{len(all_results)}[/bold green]")
        console.print("="*50)

        if args and getattr(args, "subdomain_search", None):
            subdomains = _unique_domains(all_results)
            export_formats = _get_export_formats(args, default_formats=["json", "txt"])
            payload = {"subdomains": subdomains}
            _export_data(payload, args.subdomain_search, export_formats, args)
            return all_results

        if analyzed_target is not None:
            target_domain = _get_result_domain(analyzed_target)
            console.print(f"\n[bold white]Do you want to export only the subdomains for [bold cyan]{target_domain}[/bold cyan], or the full search results table?[/bold white]")
            console.print("1. Subdomains only")
            console.print("2. Full results")
            choice = input("\nSelect an option (1-2): ").strip()

            if choice == "1":
                subdomains = _unique_domains(_filter_subdomain_results(all_results, target_domain))
                if not subdomains:
                    subdomains = [target_domain]
                export_formats = _get_export_formats(args)
                payload = {"subdomains": subdomains}
                _export_data(payload, target_domain, export_formats, args)
                return all_results

        export_formats = _get_export_formats(args)
        target_name = None
        if args:
            target_name = getattr(args, "site", None) or getattr(args, "keyword", None) or "search_results"
        _export_data(all_results, target_name, export_formats, args)

    return all_results