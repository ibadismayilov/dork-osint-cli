# history.py
from rich.console import Console

console = Console()

def show_history(file_path):
    try:
        with open(file_path, "r") as f:
            lines = f.readlines()
        if not lines:
            console.print("[yellow]No history found.[/yellow]")
            return
        from rich.table import Table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Date")
        table.add_column("Query")
        table.add_column("Link")
        for line in lines:
            date, query, link = line.strip().split(" | ")
            table.add_row(date, query, link)
        console.print(table)
    except FileNotFoundError:
        console.print("[red]No history found.[/red]")

def save_history(file_path, query, link):
    with open(file_path, "a") as f:
        from datetime import datetime
        f.write(f"{datetime.now()} | {query} | {link}\n")