from rich.console import Console
from rich.table import Table
from rich.text import Text

console = Console()

def display_results(results, start_index=0, snippet_len=80):
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("No", width=6)
    table.add_column("Title")
    table.add_column("Link")
    table.add_column("Domain")
    table.add_column("Snippet")

    for i, r in enumerate(results, start=1):
        num = start_index + i
        title = r.get("title", "No Title")
        title_display = title if len(title) <= 80 else title[:77] + "..."
        link = r.get("link", "")
        domain = link.split("/")[2] if "/" in link else ""
        snippet = r.get("snippet", "")
        snippet_display = snippet if len(snippet) <= snippet_len else snippet[:snippet_len-3]+"..."
        table.add_row(str(num),
                      Text(title_display, style="bold cyan"),
                      Text(link, style="blue underline"),
                      Text(domain, style="green"),
                      Text(snippet_display, style="yellow"))
    console.print(table)


def show_full_snippet(result):
    snippet = result.get("snippet", "")
    title = result.get("title", "No Title")
    link = result.get("link", "")
    console.print(f"\n[bold cyan]{title}[/bold cyan]")
    console.print(f"[blue underline]{link}[/blue underline]")
    console.print(f"[yellow]{snippet}[/yellow]\n")