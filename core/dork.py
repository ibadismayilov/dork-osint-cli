def build_query(keyword=None, pdf=False, login=False, site=None, intitle=None, inurl=None, intext=None, filetype=None, date_filter=None):
    """
    Build advanced Google query string with optional filters.
    """
    query = keyword if keyword else ""

    if pdf:
        query += " filetype:pdf"
    if filetype:
        query += f" filetype:{filetype}"
    if login:
        query += " inurl:login"
    if site:
        query += f" site:{site}"
    if intitle:
        if isinstance(intitle, list):
            query += " " + " ".join([f'intitle:{t}' for t in intitle])
        else:
            query += f" intitle:{intitle}"
    if inurl:
        if isinstance(inurl, list):
            query += " " + " ".join([f'inurl:{t}' for t in inurl])
        else:
            query += f" inurl:{inurl}"
    if intext:
        if isinstance(intext, list):
            query += " " + " ".join([f'intext:{t}' for t in intext])
        else:
            query += f" intext:{intext}"
    if date_filter:
        query += f" after:{date_filter}"

    return query.strip()