from rich.console import Console
from rich.panel import Panel
from core.history import save_history
from core.api import search_google
import webbrowser
import time
from ui.ui_display import display_results, show_full_snippet

console = Console()

def paginate_results(query, all_results, display_func, page_size, history_file):
    page = 1
    global_index = 0
    total_results = None

    while True:
        end_index = global_index + page_size

        # API fetch (loading spinner)
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
                console.print("[yellow]No more results to fetch.[/yellow]")
                break

        current_page_results = all_results[global_index:end_index]

        if not current_page_results:
            console.print("[yellow]No results to display.[/yellow]")
            break

        # Panel with total results
        panel_text = f"[bold green]Page {page}[/bold green] | Showing results {global_index+1}-{global_index+len(current_page_results)}"
        if total_results != "Unknown":
            panel_text += f" of {total_results}"
        console.print(Panel(panel_text))

        # Display results **only once per page**
        display_func(current_page_results, start_index=global_index)

        # USER ACTION
        action = input("\n[number] Open link & show full snippet | n Next | p Previous | q Quit : ").strip().lower()

        if action.isdigit():
            sel = int(action)
            if 0 < sel <= len(all_results):
                # **Yalnız seçilmiş item üçün toggle**
                webbrowser.open(all_results[sel - 1].get("link", ""))
                save_history(history_file, query, all_results[sel - 1].get("link", ""))
                show_full_snippet(all_results[sel - 1])
                # **Əvvəlki cədvəl yenidən göstərilmir**
            else:
                console.print("[red]Invalid selection[/red]")

        elif action == "n":
            page += 1
            global_index += page_size

        elif action == "p":
            if page > 1:
                page -= 1
                global_index -= page_size
                if global_index < 0:
                    global_index = 0
            else:
                console.print("[yellow]Already at first page[/yellow]")

        elif action == "q":
            break
        else:
            console.print("[red]Unknown action[/red]")

    return all_results