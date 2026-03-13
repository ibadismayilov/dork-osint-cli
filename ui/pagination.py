import webbrowser
import time
from rich.console import Console
from rich.panel import Panel
from core.history import save_history
from core.api import search_google
from ui.ui_display import display_results, show_full_snippet
from utils.export import export_json, export_csv
from core.reporter import generate_html_report

console = Console()

def paginate_results(query, all_results, display_func, page_size, history_file, args=None):
    """
    Handles pagination, user interaction, and final export options.
    """
    page = 1
    global_index = 0
    total_results = None

    while True:
        end_index = global_index + page_size

        # API fetch logic with loading spinner
        if end_index > len(all_results) or total_results is None:
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

    # --- FINAL EXPORT MENU ---
    if all_results:
        console.print("\n" + "="*50)
        console.print("[bold yellow]SEARCH SESSION FINISHED[/bold yellow]")
        console.print(f"Total results collected: [bold green]{len(all_results)}[/bold green]")
        console.print("="*50)
        
        console.print("\n[bold white]Would you like to export your findings?[/bold white]")
        console.print("1. Export to [bold cyan]JSON[/bold cyan]")
        console.print("2. Export to [bold green]CSV[/bold green]")
        console.print("3. Export to [bold magenta]HTML Dashboard[/bold magenta]")
        console.print("4. Exit without exporting")
        
        choice = input("\nSelect an option (1-4): ").strip()
        
        if choice == "1":
            export_json(all_results)
        elif choice == "2":
            export_csv(all_results)
        elif choice == "3":
            target_name = "Search_Report"
            if args:
                target_name = getattr(args, 'site', None) or getattr(args, 'keyword', None) or "Search_Report"
            
            with console.status("[bold blue]Generating HTML Dashboard..."):
                report_file = generate_html_report(all_results, target_name)
            
            console.print(f"[bold green]✔ HTML Report created:[/bold green] [underline]{report_file}[/underline]")
            
            try:
                import os
                report_path = os.path.abspath(report_file)
                
                webbrowser.open(f"file://{report_path}")
                console.print(f"[dim cyan]ℹ Opening dashboard in your browser...[/dim cyan]")
            except Exception as e:
                console.print(f"[red]Could not open browser automatically: {e}[/red]")
        else:
            console.print("[italic white]Exiting... Goodbye![/italic white]")

    return all_results