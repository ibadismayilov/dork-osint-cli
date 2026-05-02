from urllib.parse import urlparse
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.panel import Panel
from utils.resolver import get_ip_address, get_whois_info, detect_technology

console = Console()

def display_results(results, start_index=0):
    """
    Renders search results in a professional, structured CLI table.
    Uses vibrant colors for Domain and IP, keeping the Title layout slim.
    """
    # Initialize the table with magenta headers
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("No", width=4, justify="center")
    table.add_column("Title", width=35)
    table.add_column("IP Address", style="bold green", width=15)
    table.add_column("Domain", style="bold bright_green", width=20)
    table.add_column("Status", style="yellow", width=8)
    table.add_column("Ports", style="red", width=12)
    
    # Snippet column is currently disabled to keep the UI clean
    # table.add_column("Snippet", style="yellow")

    title_limit = 35

    # Display status spinner while resolving IPs for all results
    with console.status("[bold green]Processing results...") as status:
        for i, r in enumerate(results, start=1):
            num = start_index + i
            
            # Truncate title if it exceeds the limit
            title = r.get("http_title") or r.get("title", "No Title")
            title_display = title if len(title) <= title_limit else title[:title_limit-3] + "..."
            
            link = r.get("link", "")
            domain = r.get("domain", "N/A")
            
            # Prefer precomputed IP from the search results (cache), otherwise resolve it
            ip_addr = r.get("ip") or "N/A"
            
            # Status code (HTTP probe result)
            status_code = r.get("status_code")
            status_display = str(status_code) if status_code else "—"
            
            # Ports (port scan result)
            ports = r.get("ports", [])
            ports_display = ",".join(map(str, ports[:3])) if ports else "—"
            if len(ports) > 3:
                ports_display += f"+{len(ports)-3}"
            
            # Formatting and adding the row to the table
            table.add_row(
                str(num),
                Text(title_display, style="bold cyan"), 
                Text(ip_addr, style="bold green"),
                Text(domain, style="bold bright_green"),
                Text(status_display, style="yellow"),
                Text(ports_display, style="red" if ports else "dim")
            )
    
    # Print the final table to the terminal
    console.print(table)

def show_full_snippet(result):
    """
    Displays the full result with deep OSINT analysis (Whois & Tech).
    """
    link = result.get("link", "")
    title = result.get("http_title") or result.get("title", "No Title")
    snippet = result.get("snippet", "No description available.")
    status_code = result.get("status_code")
    server = result.get("server")
    ports = result.get("ports", [])

    console.print(Panel(f"[bold cyan]{title}[/bold cyan]\n[blue underline]{link}[/blue underline]", title="Target Details"))
    
    # HTTP Info
    if status_code or server:
        http_info = []
        if status_code:
            http_info.append(f"[yellow]HTTP Status:[/yellow] {status_code}")
        if server:
            http_info.append(f"[yellow]Server:[/yellow] {server}")
        if http_info:
            console.print(" • ".join(http_info))
    
    # Ports Info
    if ports:
        console.print(f"[yellow]Open Ports:[/yellow] {', '.join(map(str, ports))}")
    
    console.print(f"[yellow]Snippet:[/yellow] {snippet}\n")

    # --- Deep OSINT Analysis Section ---
    with console.status("[bold magenta]Performing Deep OSINT Analysis...") as status:
        whois_data = get_whois_info(link)
        tech_data = detect_technology(link)

    # 1. Whois Info Table
    if whois_data:
        w_table = Table(title="WHOIS Information", show_header=False, border_style="magenta")
        w_table.add_row("Registrar", str(whois_data['registrar']))
        w_table.add_row("Created", str(whois_data['creation_date']))
        w_table.add_row("Expires", str(whois_data['expiration_date']))
        w_table.add_row("Country", str(whois_data['country']))
        console.print(w_table)

    # 2. Technology Stack
    if tech_data:
        t_table = Table(title="Technology Stack", border_style="green")
        t_table.add_column("Category", style="bold cyan")
        t_table.add_column("Detected Tech", style="green")
        for category, apps in tech_data.items():
            t_table.add_row(category.capitalize(), ", ".join(apps))
        console.print(t_table)
    else:
        console.print("[red]Could not detect technology stack.[/red]")