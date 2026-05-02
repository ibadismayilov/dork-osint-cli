# 🔍 Terminal-Based Advanced Search System

A professional command-line interface (CLI) tool designed for advanced
OSINT and Google Dorking. This tool leverages the **SerpApi** to fetch
real-time search results, providing a structured, paginated, and
interactive terminal experience. Includes subdomain enumeration with
passive and active scanning capabilities.

------------------------------------------------------------------------

## ✨ Features

-   **Advanced Dorking:** Supports `intitle`, `inurl`, `filetype`,
    `site`, and more.\
-   **Subdomain Discovery:** Passive enumeration via Google Dorks and
    optional active brute-force using wordlists.\
-   **Extended Active Scanning:** HTTP probing, port scanning, and Certificate Transparency logs for real-world reconnaissance.\
-   **Full OSINT Suite:**
    - DNS Records Enumeration (A, AAAA, MX, NS, TXT, SOA, CNAME)
    - Reverse DNS Lookup & Hostname Resolution
    - Email Address Enumeration from DNS records
    - Web Archive (Wayback Machine) Integration
    - ASN & Geolocation Lookup
    - Historical Subdomain Discovery from archives
-   **Smart Dorking Modes:** Pre-defined templates for `recon`, `leaks`,
    `admin`, `vuln`, and `deep_recon`.\
-   **Interactive UI:** Built with `Rich` for beautiful tables, panels,
    and status indicators.\
-   **Smart Caching:** Saves search results locally in `cache.json` to
    reduce API usage and improve speed.\
-   **Session History:** Automatically logs your search queries and
    visited links.\
-   **Export Options:** Export your findings directly to `CSV`, `JSON`, `YAML`, `TXT`, or `HTML Dashboard` with automatic timestamps.\
-   **Export subfolders:** Exports are organized into dedicated format folders under `data/exports/`.\
-   **Silent mode:** Suppress export messages with `--silent`.\
-   **Compressed exports:** Create gzipped JSON/YAML exports with `--compress`.\
-   **Smart Pagination:** Navigate through hundreds of results with
    ease.\
-   **Automated Setup:** Includes a `run.sh` script to handle virtual
    environments and dependencies automatically.\
-   **Robust Dependencies:** Gracefully handles missing optional
    libraries (e.g., `builtwith`, `whois`, `dnspython`).

------------------------------------------------------------------------

# 🚀 Quick Start

## Prerequisites

-   Python 3.8+
-   A [SerpApi](https://serpapi.com/) API Key (required for searches).
-   Optional: `builtwith` and `whois` for enhanced OSINT analysis (install via `pip install builtwith python-whois`).

------------------------------------------------------------------------

## Installation & Usage

### 1. Clone the repository

``` bash
git clone https://github.com/yourusername/terminal-search-system.git
cd terminal-search-system
```

### 2. Setup Environment Variables

Create a `.env` file in the root directory (or use the example):

``` bash
cp .env.example .env
```

Add your SerpApi key to the `.env` file:

    API_KEY=your_serpapi_key_here

### 3. Run the Tool

This command installs all dependencies, sets up the virtual environment, 
and activates the search command globally. You don't need to manually install requirements. 
Just run the automated script:

``` bash
chmod +x setup.sh && ./setup.sh
```

# 🔍 Usage

Once installed, you can use the search command from any folder on your system:

``` bash
search "admin panel login" --filetype php --site example.com
```

### Advanced Examples

- **Subdomain Discovery (Passive):**
  ``` bash
  search --subdomain example.com
  ```

- **Subdomain Discovery (Active Brute-Force):**
  ``` bash
  search --subdomain example.com --active
  ```

- **Extended Active Scan (HTTP Probe + Port Scan + CT Logs):**
  ``` bash
  search --subdomain example.com --extended
  ```

- **Selective Extended Scanning:**
  ``` bash
  search --subdomain example.com --active --http-probe --port-scan --ct-logs
  ```

- **HTTP Probing Only:**
  ``` bash
  search --subdomain example.com --active --http-probe
  ```

- **Port Scanning Only:**
  ``` bash
  search --subdomain example.com --active --port-scan
  ```

- **Certificate Transparency Lookup Only:**
  ``` bash
  search --subdomain example.com --active --ct-logs
  ```

- **Smart Dorking Mode:**
  ``` bash
  search --mode deep_recon --site example.com
  ```

- **Export Results:**
  ``` bash
  search "test query" --export-json --export-csv --export-html
  ```
- **Export YAML results:**
  ``` bash
  search "test query" --export-yaml
  ```
- **Export compressed JSON:**
  ``` bash
  search "test query" --export-json --compress
  ```
- **Export a domain list TXT file:**
  ``` bash
  search --subdomain example.com --export-txt
  ```

### 🔬 OSINT & Reconnaissance Examples

- **Full OSINT Reconnaissance:**
  ``` bash
  search --subdomain example.com --recon
  ```
  Performs comprehensive reconnaissance including DNS enumeration, email discovery, web archive lookup, and ASN analysis.

- **DNS Enumeration (All Records):**
  ``` bash
  search --subdomain example.com --dns-enum
  ```
  Query all DNS record types: A, AAAA, MX, NS, TXT, SOA, CNAME

- **Custom DNS Records:**
  ``` bash
  search --subdomain example.com --dns-records MX,NS,TXT
  ```
  Query specific DNS record types (comma-separated)

- **Email Enumeration:**
  ``` bash
  search --subdomain example.com --emails
  ```
  Generate potential email addresses from domain

- **Web Archive Analysis:**
  ``` bash
  search --subdomain example.com --archive
  ```
  Find historical snapshots and old subdomains from Wayback Machine

- **ASN & Geolocation Lookup:**
  ``` bash
  search --subdomain example.com --asn
  ```
  Perform ASN lookup and geolocation analysis on resolved IPs

- **Reverse DNS Lookup:**
  ``` bash
  search --reverse-dns 8.8.8.8
  ```
  Perform reverse DNS lookup and find hostname from IP address

- **Combined OSINT + Active Scan:**
  ``` bash
  search --subdomain example.com --dns-enum --emails --extended --http-probe --port-scan
  ```
  Comprehensive recon with DNS enumeration, emails, extended scanning with HTTP probes and port scanning

------------------------------------------------------------------------

# 🛠 Command Line Arguments

  ------------------------------------------------------------------------------------------------
  Argument              Description                                Example
  ----------------------- ------------------------------- ----------------------------------------
  `keyword`             Main search term                `search "admin panel"`

  `--site`              Limit results to a specific     `--site github.com`
                        domain                          

  `--subdomain`         Target domain for subdomain     `--subdomain example.com`
                        discovery                       

  `--active`            Enable active wordlist          `--subdomain example.com --active`
                        brute-force for subdomains      

  `--extended`          Enable extended active scan     `--subdomain example.com --extended`
                        (HTTP probe + port scan + CT)   

  `--http-probe`        Enable HTTP/HTTPS probing       `--subdomain example.com --active --http-probe`
                        on discovered subdomains        

  `--port-scan`         Enable port scanning on         `--subdomain example.com --active --port-scan`
                        discovered subdomains           

  `--ct-logs`           Enable Certificate             `--subdomain example.com --active --ct-logs`
                        Transparency logs lookup        

  `--recon`             Full OSINT reconnaissance       `--subdomain example.com --recon`
                        (DNS, emails, archive, ASN)     

  `--dns-enum`          Enumerate all DNS records       `--subdomain example.com --dns-enum`
                        (A, AAAA, MX, NS, TXT, SOA,CNAME)

  `--dns-records`       Query specific DNS record       `--subdomain example.com --dns-records MX,NS,TXT`
                        types (comma-separated)         

  `--emails`            Enumerate potential email      `--subdomain example.com --emails`
                        addresses from domain           

  `--archive`           Query Wayback Machine for       `--subdomain example.com --archive`
                        historical data and subdomains  

  `--asn`               Perform ASN and geolocation    `--subdomain example.com --asn`
                        lookup on resolved IPs          

  `--reverse-dns`       Perform reverse DNS lookup     `--reverse-dns 8.8.8.8`
                        on an IP address                

  `--mode`              Pre-defined dorking mode        `--mode recon --site example.com`
                        (recon/leaks/admin/vuln/deep_recon)

  `--filetype`          Search for specific file        `--filetype log`
                        extensions                      

  `--pdf`               Shortcut for `filetype:pdf`     `--pdf`

  `--login`             Shortcut for `inurl:login`      `--login`

  `--intitle`           Filter by page title            `--intitle "login"`

  `--inurl`             Filter by URL content           `--inurl admin`

  `--intext`            Filter by page text body        `--intext "password"`

  `--date`              Filter by date                  `--date 2023-01-01`
                        (`after:YYYY-MM-DD`)            

  `--export-csv`        Save results to CSV file        `--export-csv`

  `--export-json`       Save results to JSON file       `--export-json`

  `--export-yaml`       Save results to YAML file       `--export-yaml`

  `--export-txt`        Save results to TXT domain list `--export-txt`

  `--export-html`       Save results to HTML Dashboard  `--export-html`

  `--compress`          Compress JSON/YAML export       `--compress`

  `--silent`            Suppress export messages        `--silent`

  `--export-path`       Custom export directory         `--export-path /path/to/dir`
                        (default: data/exports)         

  `--no-interactive`    Run in non-interactive mode     `--no-interactive`
                        (auto-export and quit)         

  `--clear-cache`       Wipe local search cache         `--clear-cache`

  `--history`           View search history             `--history`

  `--page-size`         Number of results per page      `--page-size 20`
                        (default: 10)                   
  ------------------------------------------------------------------------------------------------

------------------------------------------------------------------------

# 📂 Project Structure

    terminal-search-system/
    ├── core/                # Core Logic
    │   ├── api.py           # SerpApi integration, caching, & active scanning
    │   ├── dork.py          # Advanced query builder & dorking modes
    │   ├── osint.py         # OSINT module (DNS, reverse DNS, emails, web archive, ASN)
    │   ├── history.py       # History logging system
    │   └── reporter.py      # HTML report generation
    ├── data/                # Local Data Storage
    │   ├── cache/           # Cached search results
    │   │   └── cache.json   # Local search cache
    │   ├── exports/         # Exported search results organized by format
    │   │   ├── csv/
    │   │   ├── json/
    │   │   ├── txt/
    │   │   ├── yaml/
    │   │   └── html/
    │   ├── histories/       # Search query logs
    │   │   └── history.txt  # Search history
    │   └── wordlists/       # Wordlists for active scanning
    │       └── all.txt      # Subdomain wordlist
    ├── templates/           # Jinja2 Templates
    │   └── report_template.html # HTML report template
    ├── tests/               # Unit tests (currently empty)
    ├── ui/                  # User Interface
    │   ├── ui_display.py    # Rich-based table & UI rendering
    │   └── pagination.py    # Interactive results navigation
    ├── utils/               # Helper Utilities
    │   ├── export.py        # Export functions (CSV/JSON)
    │   └── resolver.py      # IP, Whois, & technology detection
    ├── controller.py        # Main logic flow & argument parsing
    ├── main.py              # Application entry point
    ├── run.sh               # Environment & Execution handler
    ├── setup.sh             # Global command installer (Run once)
    ├── requirements.txt     # Python dependencies list
    ├── .env.example         # Template for API credentials
    ├── .gitignore           # Git ignore rules
    └── README.md            # This file

------------------------------------------------------------------------

# 🛡 Disclaimer

This tool is intended for legal OSINT and security research purposes
only. Users are responsible for complying with the terms of service of
the search engines and APIs used.

------------------------------------------------------------------------

## 👨‍💻 Developed by

**Ibad Ismayilov**
