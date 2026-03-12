class DorkManager:
    """
    Manages pre-defined Google Dorking templates for security audits and OSINT.
    """
    def __init__(self):
        self.modes = {
            "recon": [
                'inurl:admin', 'inurl:login', 'intitle:"index of"', 
                'inurl:config', 'filetype:php intitle:phpinfo'
            ],
            "leaks": [
                'filetype:env "DB_PASSWORD"', 
                'filetype:log "password"', 
                'filetype:sql "INSERT INTO"', 
                'inurl:backup filetype:sql',
                'intitle:"index of" "config.php"'
            ],
            "admin": [
                'inurl:admin', 'inurl:login', 'intitle:login', 
                'inurl:wp-admin', 'inurl:dashboard', 'inurl:controlpanel'
            ],
            "vuln": [
                'inurl:".php?id="', 'inurl:".php?cat="', 
                'intext:"sql syntax error"', 'inurl:".php?search="'
            ]
        }

    def get_queries(self, site, mode):
        """
        Applies the selected mode templates to the target site.
        """
        if mode in self.modes:
            return [f"site:{site} {dork}" for dork in self.modes[mode]]
        return []

def build_query(keyword=None, subdomain_search=None, mode=None, pdf=False, login=False, 
                site=None, intitle=None, inurl=None, intext=None, filetype=None, date_filter=None):
    """
    Main logic to construct a valid Google search query based on user arguments.
    """
    
    # Priority 1: Subdomain Discovery
    if subdomain_search:
        return f"site:*.{subdomain_search} -www"

    # Priority 2: Smart Dorking Modes
    smart_dorks = ""
    if mode and site:
        dm = DorkManager()
        queries = dm.get_queries(site, mode)
        if queries:
            # Group dorks with OR in parentheses to separate from other filters
            smart_dorks = "(" + " OR ".join(queries) + ")"

    # Priority 3: Component Assembly
    query_parts = []

    if keyword:
        query_parts.append(keyword)

    # Add site filter only if Smart Mode is not active (since site is already in dorks)
    if site and not smart_dorks:
        query_parts.append(f"site:{site}")
    
    if smart_dorks:
        query_parts.append(smart_dorks)

    # Filetype priority
    if pdf:
        query_parts.append("filetype:pdf")
    elif filetype:
        query_parts.append(f"filetype:{filetype}")
        
    if login:
        query_parts.append("inurl:login")

    # Advanced Search Operators
    operators = {"intitle": intitle, "inurl": inurl, "intext": intext}
    for op, value in operators.items():
        if value:
            if isinstance(value, list):
                query_parts.append(" ".join([f'{op}:{t}' for t in value]))
            else:
                query_parts.append(f"{op}:{value}")

    if date_filter:
        query_parts.append(f"after:{date_filter}")

    return " ".join(query_parts).strip()