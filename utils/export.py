from pathlib import Path
import json
import csv
import gzip
from datetime import datetime
from typing import Dict, List, Optional, Union
from urllib.parse import urlparse
from rich.console import Console

try:
    import yaml
except ImportError:
    yaml = None

console = Console()
EXPORT_DIR = Path("data") / "exports"


def _ensure_dir(path: Path) -> Path:
    """Ensure the target directory exists."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def _sanitize_name(name: str) -> str:
    """Convert a target name or title into a safe file prefix."""
    cleaned = name.strip().lower().replace(" ", "_").replace(".", "_").replace("-", "_")
    allowed = [c for c in cleaned if c.isalnum() or c == "_"]
    sanitized = "".join(allowed).strip("_")
    return sanitized or "export"


def _build_export_name(target_name: Optional[str], extension: str) -> str:
    """Build a target-based filename with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prefix = _sanitize_name(target_name) if target_name else "results"
    return f"{prefix}_{timestamp}{extension}"


def _resolve_export_path(file_name: Optional[str], full_path: Optional[Union[str, Path]], extension: str) -> Path:
    """Resolve the final export file path from a directory or file path."""
    if full_path is None:
        subfolder = extension.lstrip('.')
        export_dir = _ensure_dir(EXPORT_DIR / subfolder)
        return export_dir / file_name

    resolved_path = Path(full_path)
    if resolved_path.suffix:
        export_file = resolved_path.with_suffix(extension)
        _ensure_dir(export_file.parent)
        return export_file

    export_dir = _ensure_dir(resolved_path)
    return export_dir / file_name


def _extract_domains(all_results: List[Union[Dict, str]]) -> List[str]:
    """Extract a list of domains from exported result objects or strings."""
    domains = []
    for item in all_results:
        if isinstance(item, str):
            domains.append(item)
            continue

        if not isinstance(item, dict):
            continue

        domain = item.get("domain")
        if not domain:
            link = item.get("link", "")
            domain = urlparse(link).netloc
        if domain:
            domains.append(domain)
    return domains


def _validate_payload(all_results: Union[List, Dict]) -> bool:
    """Basic validation for export payload."""
    if not all_results:
        return False
    if isinstance(all_results, dict):
        return bool(all_results)
    if isinstance(all_results, list):
        return len(all_results) > 0
    return False


def _build_metadata(target_name: Optional[str] = None) -> Dict:
    """Build export metadata."""
    return {
        "exported_at": datetime.now().isoformat(),
        "tool": "Terminal-Based Search System",
        "target": target_name or "unknown",
        "version": "1.0"
    }


def export_json(all_results: List[Union[Dict, str]], target_name: Optional[str] = None,
                file_name: Optional[str] = None, full_path: Optional[Union[str, Path]] = None,
                silent: bool = False, compress: bool = False, include_metadata: bool = True) -> Optional[Path]:
    """Export results to JSON and return the saved file path."""
    if not _validate_payload(all_results):
        if not silent:
            console.print("[yellow]No data to export.[/yellow]")
        return None

    file_name = file_name or _build_export_name(target_name, ".json.gz" if compress else ".json")
    export_path = _resolve_export_path(file_name, full_path, ".json.gz" if compress else ".json")

    data_to_export = all_results
    if include_metadata:
        metadata = _build_metadata(target_name)
        data_to_export = {"metadata": metadata, "data": all_results}

    try:
        opener = gzip.open if compress else open
        mode = "wt" if compress else "w"
        with opener(export_path, mode, encoding="utf-8") as f:
            json.dump(data_to_export, f, indent=4, ensure_ascii=False)

        if not silent:
            console.print(f"[green]Results exported to {export_path}[/green]")
        return export_path
    except OSError as exc:
        if not silent:
            console.print(f"[red]Failed to write JSON export: {exc}[/red]")
        return None


def export_yaml(all_results: List[Union[Dict, str]], target_name: Optional[str] = None,
                file_name: Optional[str] = None, full_path: Optional[Union[str, Path]] = None,
                silent: bool = False, compress: bool = False, include_metadata: bool = True) -> Optional[Path]:
    """Export results to YAML and return the saved file path."""
    if yaml is None:
        if not silent:
            console.print("[red]PyYAML not installed. Install with 'pip install PyYAML'.[/red]")
        return None

    if not _validate_payload(all_results):
        if not silent:
            console.print("[yellow]No data to export.[/yellow]")
        return None

    file_name = file_name or _build_export_name(target_name, ".yaml.gz" if compress else ".yaml")
    export_path = _resolve_export_path(file_name, full_path, ".yaml.gz" if compress else ".yaml")

    data_to_export = all_results
    if include_metadata:
        metadata = _build_metadata(target_name)
        data_to_export = {"metadata": metadata, "data": all_results}

    try:
        opener = gzip.open if compress else open
        mode = "wt" if compress else "w"
        with opener(export_path, mode, encoding="utf-8") as f:
            yaml.dump(data_to_export, f, default_flow_style=False, allow_unicode=True)

        if not silent:
            console.print(f"[green]Results exported to {export_path}[/green]")
        return export_path
    except OSError as exc:
        if not silent:
            console.print(f"[red]Failed to write YAML export: {exc}[/red]")
        return None


def export_csv(all_results: List[Union[Dict, str]], target_name: Optional[str] = None,
               file_name: Optional[str] = None, full_path: Optional[Union[str, Path]] = None,
               silent: bool = False) -> Optional[Path]:
    """Export results to CSV and return the saved file path."""
    file_name = file_name or _build_export_name(target_name, ".csv")
    export_path = _resolve_export_path(file_name, full_path, ".csv")

    # Handle subdomain payload
    if isinstance(all_results, dict) and "subdomains" in all_results:
        all_results = all_results["subdomains"]
        fieldnames = ["subdomain"]
    elif all_results and isinstance(all_results, list) and isinstance(all_results[0], dict):
        fieldnames = list(all_results[0].keys())
    else:
        fieldnames = ["domain"]

    try:
        with export_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for item in all_results:
                if isinstance(item, dict):
                    row = {key: item.get(key, "") for key in fieldnames}
                else:
                    row = {fieldnames[0]: item}
                writer.writerow(row)

        if not silent:
            console.print(f"[green]Results exported to {export_path}[/green]")
        return export_path
    except OSError as exc:
        if not silent:
            console.print(f"[red]Failed to write CSV export: {exc}[/red]")
        return None


def export_txt(all_results: List[Union[Dict, str]], target_name: Optional[str] = None,
               file_name: Optional[str] = None, full_path: Optional[Union[str, Path]] = None,
               silent: bool = False) -> Optional[Path]:
    """Export a plain TXT list of domains and return the saved file path."""
    file_name = file_name or _build_export_name(target_name, ".txt")
    export_path = _resolve_export_path(file_name, full_path, ".txt")

    # Handle subdomain payload
    if isinstance(all_results, dict) and "subdomains" in all_results:
        domains = all_results["subdomains"]
    else:
        domains = _extract_domains(all_results)

    try:
        with export_path.open("w", encoding="utf-8") as f:
            for domain in domains:
                f.write(f"{domain}\n")

        if not silent:
            console.print(f"[green]Results exported to {export_path}[/green]")
        return export_path
    except OSError as exc:
        if not silent:
            console.print(f"[red]Failed to write TXT export: {exc}[/red]")
        return None


def export_batch(all_results: List[Union[Dict, str]], target_name: Optional[str] = None,
                 formats: List[str] = None, full_path: Optional[Union[str, Path]] = None,
                 silent: bool = False, compress: bool = False, include_metadata: bool = True) -> Dict[str, Optional[Path]]:
    """Export to multiple formats and return a dict of file paths."""
    if formats is None:
        formats = ["json"]

    results = {}
    for fmt in formats:
        if fmt == "json":
            results["json"] = export_json(all_results, target_name, full_path=full_path, silent=silent, compress=compress, include_metadata=include_metadata)
        elif fmt == "csv":
            results["csv"] = export_csv(all_results, target_name, full_path=full_path, silent=silent)
        elif fmt == "txt":
            results["txt"] = export_txt(all_results, target_name, full_path=full_path, silent=silent)
        elif fmt == "yaml":
            results["yaml"] = export_yaml(all_results, target_name, full_path=full_path, silent=silent, compress=compress, include_metadata=include_metadata)
        # HTML not included in batch as it has special handling
    return results
