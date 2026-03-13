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
-   **Smart Dorking Modes:** Pre-defined templates for `recon`, `leaks`,
    `admin`, `vuln`, and `deep_recon`.\
-   **Interactive UI:** Built with `Rich` for beautiful tables, panels,
    and status indicators.\
-   **Smart Caching:** Saves search results locally in `cache.json` to
    reduce API usage and improve speed.\
-   **Session History:** Automatically logs your search queries and
    visited links.\
-   **Export Options:** Export your findings directly to `CSV`, `JSON`,
    or `HTML Dashboard` with automatic timestamps.\
-   **Smart Pagination:** Navigate through hundreds of results with
    ease.\
-   **Automated Setup:** Includes a `run.sh` script to handle virtual
    environments and dependencies automatically.\
-   **Robust Dependencies:** Gracefully handles missing optional
    libraries (e.g., `builtwith`, `whois`).

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

- **Smart Dorking Mode:**
  ``` bash
  search --mode deep_recon --site example.com
  ```

- **Export Results:**
  ``` bash
  search "test query" --export-json --export-csv --export-html
  ```

------------------------------------------------------------------------

# 🛠 Command Line Arguments

  ----------------------------------------------------------------------------
  Argument            Description                     Example
  ------------------- ------------------------------- ------------------------
  `keyword`           Main search term                `search "admin panel"`

  `--site`            Limit results to a specific     `--site github.com`
                      domain                          

  `--subdomain`       Target domain for subdomain     `--subdomain apple.com`
                      discovery                       

  `--active`          Enable active wordlist          `--subdomain apple.com --active`
                      brute-force for subdomains      

  `--mode`            Pre-defined dorking mode        `--mode recon --site example.com`
                      (recon/leaks/admin/vuln/deep_recon)

  `--filetype`        Search for specific file        `--filetype log`
                      extensions                      

  `--pdf`             Shortcut for `filetype:pdf`     `--pdf`

  `--login`           Shortcut for `inurl:login`      `--login`

  `--intitle`         Filter by page title            `--intitle "login"`

  `--inurl`           Filter by URL content           `--inurl admin`

  `--intext`          Filter by page text body        `--intext "password"`

  `--date`            Filter by date                  `--date 2023-01-01`
                      (`after:YYYY-MM-DD`)            

  `--export-csv`      Save results to CSV file        `--export-csv`

  `--export-json`     Save results to JSON file       `--export-json`

  `--export-html`     Save results to HTML Dashboard  `--export-html`

  `--export-path`     Custom export directory         `--export-path /path/to/dir`
                      (default: data/exports)         

  `--no-interactive`  Run in non-interactive mode     `--no-interactive`
                      (auto-export and quit)         

  `--clear-cache`     Wipe local search cache         `--clear-cache`

  `--history`         View search history             `--history`

  `--page-size`       Number of results per page      `--page-size 20`
                      (default: 10)                   
  ----------------------------------------------------------------------------

------------------------------------------------------------------------

# 📂 Project Structure

    terminal-search-system/
    ├── core/                # Core Logic
    │   ├── api.py           # SerpApi integration, caching, & active scanning
    │   ├── dork.py          # Advanced query builder & dorking modes
    │   ├── history.py       # History logging system
    │   └── reporter.py      # HTML report generation
    ├── data/                # Local Data Storage
    │   ├── cache/           # Cached search results
    │   │   └── cache.json   # Local search cache
    │   ├── exports/         # Exported search results (CSV/JSON/HTML)
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
