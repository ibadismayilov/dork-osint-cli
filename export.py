# export.py
import os
import json
import csv
from rich.console import Console

console = Console()
EXPORT_DIR = "exports"

def export_json(all_results):
    file_name = input("Please enter file name for JSON (without extension, default: results): ").strip() or "results"
    file_name += ".json"
    full_path = input(f"Please enter full path to save JSON (default: {EXPORT_DIR}): ").strip() or EXPORT_DIR
    os.makedirs(full_path, exist_ok=True)
    export_path = os.path.join(full_path, file_name)
    with open(export_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=4)
    console.print(f"[green]Results exported to {export_path}[/green]")

def export_csv(all_results):
    file_name = input("Please enter file name for CSV (without extension, default: results): ").strip() or "results"
    file_name += ".csv"
    full_path = input(f"Please enter full path to save CSV (default: {EXPORT_DIR}): ").strip() or EXPORT_DIR
    os.makedirs(full_path, exist_ok=True)
    export_path = os.path.join(full_path, file_name)
    with open(export_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "link", "domain", "snippet"])
        writer.writeheader()
        for r in all_results:
            writer.writerow({
                "title": r.get("title", ""),
                "link": r.get("link", ""),
                "domain": r.get("domain", ""),
                "snippet": r.get("snippet", "")
            })
    console.print(f"[green]Results exported to {export_path}[/green]")