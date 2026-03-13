import os
import json
import csv
from datetime import datetime
from urllib.parse import urlparse
from rich.console import Console

console = Console()
EXPORT_DIR = os.path.join("data", "exports")


def _get_default_path():
    """Returns the default export directory, creating it if needed."""
    os.makedirs(EXPORT_DIR, exist_ok=True)
    return EXPORT_DIR


def export_json(all_results, file_name=None, full_path=None):
    """Export results to JSON.

    By default the file is written to data/exports and includes a timestamp.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = file_name or f"results_{timestamp}.json"
    full_path = full_path or _get_default_path()

    export_path = os.path.join(full_path, file_name)
    with open(export_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=4)

    console.print(f"[green]Results exported to {export_path}[/green]")


def export_csv(all_results, file_name=None, full_path=None):
    """Export results to CSV.

    By default the file is written to data/exports and includes a timestamp.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = file_name or f"results_{timestamp}.csv"
    full_path = full_path or _get_default_path()

    export_path = os.path.join(full_path, file_name)
    with open(export_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "link", "domain", "snippet"])
        writer.writeheader()
        for r in all_results:
            link = r.get("link", "")
            domain = r.get("domain") or urlparse(link).netloc
            writer.writerow({
                "title": r.get("title", ""),
                "link": link,
                "domain": domain,
                "snippet": r.get("snippet", "")
            })

    console.print(f"[green]Results exported to {export_path}[/green]")
