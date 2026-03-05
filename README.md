# 🔍 Terminal-Based Advanced Search System

A professional command-line interface (CLI) tool designed for advanced
OSINT and Google Dorking. This tool leverages the **SerpApi** to fetch
real-time search results, providing a structured, paginated, and
interactive terminal experience.

------------------------------------------------------------------------

## ✨ Features

-   **Advanced Dorking:** Supports `intitle`, `inurl`, `filetype`,
    `site`, and more.\
-   **Interactive UI:** Built with `Rich` for beautiful tables, panels,
    and status indicators.\
-   **Smart Caching:** Saves search results locally in `cache.json` to
    reduce API usage and improve speed.\
-   **Session History:** Automatically logs your search queries and
    visited links.\
-   **Export Options:** Export your findings directly to `CSV` or `JSON`
    for further analysis.\
-   **Smart Pagination:** Navigate through hundreds of results with
    ease.\
-   **Automated Setup:** Includes a `run.sh` script to handle virtual
    environments and dependencies automatically.

------------------------------------------------------------------------

# 🚀 Quick Start

## Prerequisites

-   Python 3.8+
-   A [SerpApi](https://serpapi.com/) API Key.

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
chmod +x setup.sh && ./setup.sh"
```
# Usage
Once installed, you can use the search command from any folder on your system:

``` bash
search "admin panel login" --filetype php --site example.com
```
------------------------------------------------------------------------

# 🛠 Command Line Arguments

  ----------------------------------------------------------------------------
  Argument            Description                     Example
  ------------------- ------------------------------- ------------------------
  `keyword`           Main search term                `search "admin panel"`

  `--site`            Limit results to a specific     `--site github.com`
                      domain                          

  `--filetype`        Search for specific file        `--filetype log`
                      extensions                      

  `--pdf`             Shortcut for `filetype:pdf`     `--pdf`

  `--login`           Shortcut for `inurl:login`      `--login`

  `--export-csv`      Save results to a CSV file      `--export-csv`

  `--clear-cache`     Wipe local search cache         `--clear-cache`

  `--date`            Filter by date                  `--date 2023-01-01`
                      (`after:YYYY-MM-DD`)            
  ----------------------------------------------------------------------------

------------------------------------------------------------------------

# 📂 Project Structure

    terminal-search-system
    │
    ├── api.py           # SerpApi integration & caching logic
    ├── controller.py    # Main logic flow and argument parsing
    ├── dork.py          # Advanced query builder
    ├── ui_display.py    # Rich-based UI components
    ├── pagination.py    # Interactive results navigation
    ├── history.py       # History logging system
    ├── export.py        # CSV/JSON export functions
    │
    ├── run.sh           # Automated environment handler
    ├── setup.sh         # Global alias setup script
    └── .env.example     # Template for environment variables

------------------------------------------------------------------------

# 🛡 Disclaimer

This tool is intended for legal OSINT and security research purposes
only. Users are responsible for complying with the terms of service of
the search engines and APIs used.

------------------------------------------------------------------------

## 👨‍💻 Developed by

**Ibad Ismayilov**
