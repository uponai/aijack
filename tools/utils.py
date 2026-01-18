from urllib.parse import urlparse, urlencode, parse_qsl, urlunparse

def append_ref_param(url, ref="aijack.info"):
    """
    Appends a ref query parameter to a URL.
    Handles existing query parameters and fragments.
    """
    if not url:
        return url
        
    try:
        parsed = urlparse(url)
        query_params = dict(parse_qsl(parsed.query))
        
        # Add or update ref
        query_params['ref'] = ref
        
        new_query = urlencode(query_params)
        
        return urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment
        ))
    except Exception:
        # Fallback if parsing fails
        return url
