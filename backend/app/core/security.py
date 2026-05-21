from urllib.parse import urlparse

def sanitize_url(url: str) -> str:
    url = url.strip()
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Only http/https URLs are allowed")
    if not parsed.netloc:
        raise ValueError("Invalid URL")
    return url
