import os
from pathlib import Path
from rich.console import Console
from core.dork import build_query
from core.api import search_google, CACHE_FILE, run_active_scan, run_active_scan_extended
from ui.ui_display import display_results
from core.history import show_history, HISTORY_FILE
from utils.export import export_csv, export_json, export_txt, export_yaml
from ui.pagination import paginate_results
from core.reporter import generate_html_report
from core.osint import (
    enumerate_dns_records, extract_nameservers, extract_mx_records, 
    extract_txt_records, extract_emails_from_domain, get_wayback_snapshots,
    extract_subdomains_from_archive, run_full_recon, format_recon_report,
    reverse_dns_lookup, get_asn_info, get_ip_geolocation
)

console = Console()

def parse_comma_list(arg):
    if not arg:
        return None
    return [s.strip() for s in arg.split(",")] if "," in arg else arg


def run_search(args):
    """Main controller function to manage the search flow and OSINT operations."""

    if args.history:
        show_history(HISTORY_FILE)
        return

    if args.clear_cache:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                f.write("{}")
            console.print("[bold green]✔ Cache cleared successfully.[/bold green]")
        return

    # ====== OSINT OPERATIONS ======
    
    # Reverse DNS lookup
    if getattr(args, "reverse_dns", None):
        console.print(f"[bold cyan]🔍 Reverse DNS Lookup:[/bold cyan] {args.reverse_dns}")
        result = reverse_dns_lookup(args.reverse_dns)
        if "error" not in result:
            console.print(f"  Hostname: {result.get('hostname')}")
            if result.get('aliases'):
                console.print(f"  Aliases: {', '.join(result['aliases'])}")
        else:
            console.print(f"  [red]{result['error']}[/red]")
        
        # Also get ASN and geolocation
        asn_data = get_asn_info(args.reverse_dns)
        if asn_data:
            console.print(f"  ASN: {asn_data.get('AS', 'N/A')}")
            console.print(f"  Organization: {asn_data.get('Organization', 'N/A')}")
        
        geo_data = get_ip_geolocation(args.reverse_dns)
        if geo_data:
            console.print(f"  Location: {geo_data.get('city')}, {geo_data.get('country')} ({geo_data.get('country_code')})")
        return
    
    # Full OSINT reconnaissance
    if getattr(args, "recon", False):
        if not args.subdomain_search:
            console.print("[red]Error: --recon requires --subdomain to be specified[/red]")
            return
        
        console.print(f"[bold magenta]🔎 Full OSINT Reconnaissance:[/bold magenta] [cyan]{args.subdomain_search}[/cyan]")
        recon_report = run_full_recon(args.subdomain_search, include_email_enum=True, include_wayback=True, include_asn=True)
        console.print(format_recon_report(recon_report))
        
        # Export recon report
        if getattr(args, "export_json", False):
            export_json([recon_report], target_name=args.subdomain_search, full_path=args.export_path, silent=args.silent)
        return
    
    # DNS Enumeration
    if getattr(args, "dns_enum", False) or getattr(args, "dns_records", None):
        if not args.subdomain_search:
            console.print("[red]Error: --dns-enum requires --subdomain to be specified[/red]")
            return
        
        record_types = ["A", "AAAA", "MX", "NS", "TXT", "SOA", "CNAME"]
        if getattr(args, "dns_records", None):
            record_types = [rt.strip().upper() for rt in args.dns_records.split(",")]
        
        console.print(f"[bold cyan]📋 DNS Enumeration:[/bold cyan] {args.subdomain_search}")
        console.print(f"[dim]Record types: {', '.join(record_types)}[/dim]\n")
        
        dns_data = enumerate_dns_records(args.subdomain_search, record_types)
        
        if "error" in dns_data:
            console.print(f"[red]{dns_data['error']}[/red]")
        else:
            from rich.table import Table
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Type", width=10)
            table.add_column("Value", width=50)
            table.add_column("TTL", width=10)
            
            for rtype, records in dns_data.items():
                if records:
                    for record in records:
                        if "value" in record:
                            table.add_row(rtype, record["value"], str(record.get("ttl", "-")))
            
            console.print(table)
        
        if getattr(args, "export_json", False):
            export_json([dns_data], target_name=f"{args.subdomain_search}_dns", full_path=args.export_path, silent=args.silent)
        return
    
    # Email enumeration
    if getattr(args, "emails", False):
        if not args.subdomain_search:
            console.print("[red]Error: --emails requires --subdomain to be specified[/red]")
            return
        
        console.print(f"[bold yellow]✉️  Email Enumeration:[/bold yellow] {args.subdomain_search}\n")
        emails = extract_emails_from_domain(args.subdomain_search)
        
        from rich.table import Table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Email Address", width=40)
        
        for email in emails:
            table.add_row(email)
        
        console.print(table)
        
        if getattr(args, "export_txt", False):
            export_txt(emails, target_name=f"{args.subdomain_search}_emails", full_path=args.export_path, silent=args.silent)
        return
    
    # Web Archive lookup
    if getattr(args, "archive", False):
        if not args.subdomain_search:
            console.print("[red]Error: --archive requires --subdomain to be specified[/red]")
            return
        
        console.print(f"[bold blue]📦 Web Archive Lookup:[/bold blue] {args.subdomain_search}\n")
        archive_data = get_wayback_snapshots(args.subdomain_search)
        
        if archive_data.get("available"):
            console.print(f"[green]✔ Archive available[/green]")
            console.print(f"  First capture: {archive_data.get('first_capture')}")
            console.print(f"  Archive URL: {archive_data.get('url')}\n")
            
            subdomains = extract_subdomains_from_archive(args.subdomain_search)
            console.print(f"[bold]Historical Subdomains: {len(subdomains)}[/bold]")
            
            from rich.table import Table
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Subdomain", width=50)
            
            for sub in subdomains[:20]:
                table.add_row(sub)
            
            if len(subdomains) > 20:
                table.add_row(f"[dim]... and {len(subdomains)-20} more[/dim]")
            
            console.print(table)
        else:
            console.print("[yellow]No archive data available[/yellow]")
        
        return

    query = build_query(
        keyword=args.keyword,
        subdomain_search=args.subdomain_search,
        mode=getattr(args, "mode", None),
        pdf=args.pdf,
        login=args.login,
        site=args.site,
        intitle=parse_comma_list(args.intitle),
        inurl=parse_comma_list(args.inurl),
        intext=parse_comma_list(args.intext),
        filetype=args.filetype,
        date_filter=getattr(args, "date", None),
    )

    if args.subdomain_search:
        console.print(f"[bold magenta]🔍 Recon Mode:[/bold magenta] Target: [cyan]{args.subdomain_search}[/cyan]")
    elif getattr(args, "mode", None):
        console.print(
            f"[bold yellow]🤖 Smart Mode ({args.mode}):[/bold yellow] Target: [cyan]{args.site if args.site else 'Global'}[/cyan]"
        )
    else:
        console.print(f"[bold green]🔎 Search Query:[/bold green] [white]{query}[/white]")

    final_results = []

    # 1) Passive results via SerpApi
    if query:
        passive_data = search_google(query, page=1, page_size=args.page_size)
        if passive_data and passive_data.get("results"):
            final_results.extend(passive_data["results"])

    # 2) Optional active subdomain brute-force (wordlist-based)
    if args.subdomain_search and getattr(args, "active", False):
        console.print(f"\n[bold yellow]🚀 Active Scan Enabled:[/bold yellow] Starting brute-force for [cyan]{args.subdomain_search}[/cyan]")
        
        # Determine which scanning mode to use
        use_extended = getattr(args, "extended", False) or getattr(args, "http_probe", False) or getattr(args, "port_scan", False) or getattr(args, "ct_logs", False)
        
        if use_extended:
            from core.api import run_active_scan_extended
            http_probe = getattr(args, "extended", False) or getattr(args, "http_probe", False)
            port_scan = getattr(args, "extended", False) or getattr(args, "port_scan", False)
            ct_logs = getattr(args, "extended", False) or getattr(args, "ct_logs", False)
            active_results = run_active_scan_extended(args.subdomain_search, enable_http_probe=http_probe, enable_port_scan=port_scan, enable_ct_logs=ct_logs)
        else:
            active_results = run_active_scan(args.subdomain_search)

        if active_results:
            existing_domains = {res.get("domain") for res in final_results if res.get("domain")}
            for res in active_results:
                if res.get("domain") not in existing_domains:
                    final_results.append(res)

            console.print(f"[bold green]✔ Active scan finished. Total targets now: {len(final_results)}[/bold green]")

    # 3) Pagination & interactive display
    if final_results:
        final_results = paginate_results(
            query=query,
            all_results=final_results,
            display_func=display_results,
            page_size=args.page_size,
            history_file=HISTORY_FILE,
            args=args,
        )

        # 4) Exports
        if final_results:
            if args.export_json:
                export_json(final_results, target_name=args.site or args.subdomain_search or args.keyword,
                            full_path=args.export_path, silent=args.silent, compress=getattr(args, 'compress', False))

            if args.export_csv:
                export_csv(final_results, target_name=args.site or args.subdomain_search or args.keyword,
                           full_path=args.export_path, silent=args.silent)

            if args.export_txt:
                export_txt(final_results, target_name=args.site or args.subdomain_search or args.keyword,
                           full_path=args.export_path, silent=args.silent)

            if args.export_yaml:
                export_yaml(final_results, target_name=args.site or args.subdomain_search or args.keyword,
                            full_path=args.export_path, silent=args.silent, compress=getattr(args, 'compress', False))

            if args.export_html:
                target_name = args.site or args.subdomain_search or args.keyword or "General_Search"
                html_subdir = Path("data") / "exports" / "html"
                with console.status("[bold blue]Generating HTML Dashboard..."):
                    report_file = generate_html_report(final_results, target_name, output_path=str(html_subdir))
                console.print(f"[bold green]✔ HTML Report generated:[/bold green] [underline]{report_file}[/underline]")
                try:
                    import webbrowser
                    browser_url = Path(report_file).resolve().as_uri()
                    webbrowser.open(browser_url)
                    console.print("[dim cyan]ℹ Opening dashboard in your browser...[/dim cyan]")
                except Exception as e:
                    console.print(f"[red]Could not open browser automatically: {e}[/red]")
    else:
        console.print("[yellow]⚠ No results found.[/yellow]")

    console.print("\n[bold cyan]Session completed. Happy Hunting![/bold cyan]")
