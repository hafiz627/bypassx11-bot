from bs4 import BeautifulSoup
import httpx

async def head_probe(client: httpx.AsyncClient, url: str):
    r = await client.head(url, follow_redirects=True)
    return r.url, r.headers.get("content-type"), r.headers.get("content-length")

async def recursive_trace(client: httpx.AsyncClient, url: str, max_depth: int = 8):
    current = url
    trace = [url]
    for _ in range(max_depth):
        r = await client.get(current, follow_redirects=False)
        if r.status_code in {301,302,303,307,308} and r.headers.get("location"):
            current = str(r.headers["location"])
            trace.append(current)
            continue
        soup = BeautifulSoup(r.text, "html.parser")
        canonical = soup.find("link", rel="canonical")
        if canonical and canonical.get("href") and canonical["href"] != current:
            current = canonical["href"]
            trace.append(current)
        break
    return current, trace
