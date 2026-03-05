import socket
from urllib.parse import urlparse
from rich.console import Console
from rich.table import Table
from rich.text import Text

console = Console()

def get_ip_address(url):
    """
    Extracts the domain from the URL and resolves it to an IP address.
    """
    try:
        domain = urlparse(url).netloc
        if not domain:
            return "N/A"
        return socket.gethostbyname(domain)
    except Exception:
        return "Unknown"

def display_results(results, start_index=0):
    """
    Displays the search results in a structured table. 
    Title is kept slim and Domain is made more vibrant.
    """
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("No", width=4, justify="center")
    # Using a larger width for Title but keeping font style 'normal' for a smaller look
    table.add_column("Title", width=40)
    table.add_column("IP Address", style="bold green", width=15)
    # Bright green makes the domain stand out more
    table.add_column("Domain", style="bold bright_green", width=25)
    table.add_column("Link", style="blue underline")
    
    # Snippet column is commented out as requested
    # table.add_column("Snippet", style="yellow")

    title_limit = 40

    with console.status("[bold green]Resolving target hosts...") as status:
        for i, r in enumerate(results, start=1):
            num = start_index + i
            
            title = r.get("title", "No Title")
            title_display = title if len(title) <= title_limit else title[:title_limit-3] + "..."
            
            link = r.get("link", "")
            domain = urlparse(link).netloc if link else "N/A"
            ip_addr = get_ip_address(link)
            
            # Snippet processing remains commented out
            # snippet = r.get("snippet", "")
            # snippet_display = snippet if len(snippet) <= 50 else snippet[:47] + "..."
            
            table.add_row(
                str(num),
                # Removed 'bold' from Title to make it look smaller/slimmer
                Text(title_display, style="bold cyan"), 
                Text(ip_addr, style="bold green"),
                Text(domain, style="bold bright_green"),
                Text(link, style="blue")
            )
    
    console.print(table)

def show_full_snippet(result):
    """
    Prints the full details of a single search result.
    """
    snippet = result.get("snippet", "")
    title = result.get("title", "No Title")
    link = result.get("link", "")
    console.print(f"\n[bold cyan]{title}[/bold cyan]")
    console.print(f"[blue underline]{link}[/blue underline]")
    console.print(f"[yellow]{snippet}[/yellow]\n")