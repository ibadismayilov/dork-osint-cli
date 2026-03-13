import os
from rich.console import Console
from datetime import datetime

console = Console()

# Qovluq iyerarxiyasını qururuq: data/histories
HISTORY_DIR = os.path.join("data", "histories")
if not os.path.exists(HISTORY_DIR):
    os.makedirs(HISTORY_DIR)

HISTORY_FILE = os.path.join(HISTORY_DIR, "history.txt")

def show_history(file_path=HISTORY_FILE):
    try:
        if not os.path.exists(file_path):
            console.print("[red]No history found.[/red]")
            return

        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        if not lines:
            console.print("[yellow]No history found.[/yellow]")
            return
            
        from rich.table import Table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Date", style="dim")
        table.add_column("Query", style="cyan")
        table.add_column("Link", style="green")
        
        for line in lines:
            parts = line.strip().split(" | ")
            if len(parts) == 3:
                table.add_row(parts[0], parts[1], parts[2])
        
        console.print(table)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

def save_history(file_path, query, link):
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))
        
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {query} | {link}\n")