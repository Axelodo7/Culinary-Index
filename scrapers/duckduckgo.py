from urllib.parse import urlparse


def search_web(query, proxy_manager=None, rotate_ua=True):
    results = []
    try:
        try:
            from ddgs import DDGS
        except ImportError:
            from duckduckgo_search import DDGS
        search_query = f"{query} recipe"
        ddg_results = DDGS().text(search_query, max_results=15)
        for r in ddg_results:
            title = r.get("title", "")
            href = r.get("href", "")
            if title and href:
                source_name = ""
                try:
                    parsed = urlparse(href)
                    source_name = parsed.netloc.replace("www.", "")
                except Exception:
                    source_name = "Web"
                results.append({
                    "title": title,
                    "source": f"Web: {source_name}",
                    "url": href,
                    "prep_time": "",
                })
    except Exception:
        pass
    return results
