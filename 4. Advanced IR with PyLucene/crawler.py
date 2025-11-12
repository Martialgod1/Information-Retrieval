import argparse
import collections
import re
import time
from urllib.parse import urljoin, urldefrag, urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except Exception:
    requests = None
    BeautifulSoup = None


def normalize_url(base: str, link: str) -> str:
    try:
        href = urljoin(base, link)
        href, _ = urldefrag(href)
        return href
    except Exception:
        return ""


def crawl(seeds, max_pages=50, same_host=True, delay=0.0):
    if requests is None or BeautifulSoup is None:
        print("requests/bs4 not available. Install or use Docker with network enabled.")
        return {}
    seen = set()
    q = collections.deque(seeds)
    graph = collections.defaultdict(set)
    seed_hosts = {urlparse(u).netloc for u in seeds}
    while q and len(seen) < max_pages:
        url = q.popleft()
        if url in seen:
            continue
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code != 200 or "text/html" not in resp.headers.get("Content-Type", ""):
                continue
            seen.add(url)
            soup = BeautifulSoup(resp.text, "html.parser")
            links = []
            for a in soup.find_all("a", href=True):
                href = normalize_url(url, a["href"])
                if not href.startswith("http"):
                    continue
                if same_host and urlparse(href).netloc not in seed_hosts:
                    continue
                links.append(href)
            for v in links:
                graph[url].add(v)
                if v not in seen:
                    q.append(v)
            if delay > 0:
                time.sleep(delay)
        except Exception:
            continue
    return graph


def main():
    parser = argparse.ArgumentParser(description="Simple crawler (demo). Network may be restricted in some environments.")
    parser.add_argument("--seeds", nargs="+", help="Seed URLs")
    parser.add_argument("--max-pages", type=int, default=50, help="Maximum pages to fetch")
    parser.add_argument("--allow-offsite", action="store_true", help="Allow leaving seed hosts")
    parser.add_argument("--delay", type=float, default=0.0, help="Politeness delay (seconds)")
    args = parser.parse_args()

    if not args.seeds:
        print("Provide --seeds. Example: --seeds https://example.com")
        return
    graph = crawl(args.seeds, max_pages=args.max_pages, same_host=not args.allow_offsite, delay=args.delay)
    print(f"Crawled pages: {len(graph)}")
    edges = sum(len(v) for v in graph.values())
    print(f"Edges: {edges}")
    for u, vs in list(graph.items())[:10]:
        print(u)
        for v in list(vs)[:5]:
            print("  ->", v)


if __name__ == "__main__":
    main()


