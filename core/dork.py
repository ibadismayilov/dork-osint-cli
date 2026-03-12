def build_query(keyword=None, subdomain_search=None, pdf=False, login=False, site=None, intitle=None, inurl=None, intext=None, filetype=None, date_filter=None):
    """
    Builds an advanced Google search query with support for Recon and Filter modes.
    """
    
    # Priority 1: Subdomain Discovery Mode
    if subdomain_search:
        return f"site:*.{subdomain_search} -www"

    # Priority 2: Standard Search with Advanced Filters
    query = keyword if keyword else ""

    if site:
        query += f" site:{site}"
    
    if pdf:
        query += " filetype:pdf"
    
    if filetype and not pdf:
        query += f" filetype:{filetype}"
        
    if login:
        query += " inurl:login"

    # Handle intitle (string or list)
    if intitle:
        if isinstance(intitle, list):
            query += " " + " ".join([f'intitle:{t}' for t in intitle])
        else:
            query += f" intitle:{intitle}"

    # Handle inurl (string or list)
    if inurl:
        if isinstance(inurl, list):
            query += " " + " ".join([f'inurl:{t}' for t in inurl])
        else:
            query += f" inurl:{inurl}"

    # Handle intext (string or list) - YENİ ƏLAVƏ OLUNDU
    if intext:
        if isinstance(intext, list):
            query += " " + " ".join([f'intext:{t}' for t in intext])
        else:
            query += f" intext:{intext}"

    if date_filter:
        query += f" after:{date_filter}"

    return query.strip()