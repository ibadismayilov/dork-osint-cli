from urllib.parse import urlparse
from rich.console import Console
from rich.table import Table
from rich.text import Text
# Importing the separated logic from utils folder
from utils.resolver import get_ip_address 

console = Console()

def display_results(results, start_index=0):
    """
    Renders search results in a professional, structured CLI table.
    Uses vibrant colors for Domain and IP, keeping the Title layout slim.
    """
    # Initialize the table with magenta headers
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("No", width=4, justify="center")
    table.add_column("Title", width=40)
    table.add_column("IP Address", style="bold green", width=15)
    table.add_column("Domain", style="bold bright_green", width=25)
    table.add_column("Link", style="blue underline")
    
    # Snippet column is currently disabled to keep the UI clean
    # table.add_column("Snippet", style="yellow")

    title_limit = 40

    # Display status spinner while resolving IPs for all results
    with console.status("[bold green]Resolving target hosts...") as status:
        for i, r in enumerate(results, start=1):
            num = start_index + i
            
            # Truncate title if it exceeds the limit
            title = r.get("title", "No Title")
            title_display = title if len(title) <= title_limit else title[:title_limit-3] + "..."
            
            link = r.get("link", "")
            domain = urlparse(link).netloc if link else "N/A"
            
            # Call the separated IP resolution function
            ip_addr = get_ip_address(link)
            
            # Formatting and adding the row to the table
            table.add_row(
                str(num),
                Text(title_display, style="bold cyan"), 
                Text(ip_addr, style="bold green"),
                Text(domain, style="bold bright_green"),
                Text(link, style="blue")
            )
    
    # Print the final table to the terminal
    console.print(table)

def show_full_snippet(result):
    """
    Displays the full content and metadata of a single result for detailed inspection.
    """
    snippet = result.get("snippet", "")
    title = result.get("title", "No Title")
    link = result.get("link", "")
    
    console.print(f"\n[bold cyan]{title}[/bold cyan]")
    console.print(f"[blue underline]{link}[/blue underline]")
    console.print(f"[yellow]{snippet}[/yellow]\n")