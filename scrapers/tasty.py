import json
import logging
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from .helpers import safe_request

logger = logging.getLogger("scrapers")


def _ddg_fallback(query):
    """Use DuckDuckGo as fallback when direct scraping is blocked."""
    try:
        try:
            from ddgs import DDGS
        except ImportError:
            from duckduckgo_search import DDGS
        results = []
        ddg_results = DDGS().text(f"site:tasty.co {query} recipe", max_results=10)
        for r in ddg_results:
            title = r.get("title", "")
            href = r.get("href", "")
            if title and href and len(title) > 3:
                for sep in [" | ", " - ", " | Tasty"]:
                    if sep in title:
                        title = title.split(sep)[0]
                title = title.strip()
                if len(title) >= 3:
                    results.append({
                        "title": title,
                        "source": "Tasty",
                        "url": href,
                        "prep_time": "",
                    })
        return results
    except Exception as e:
        logger.warning(f"DDG fallback failed for Tasty: {e}")
        return []


def search_tasty(query, proxy_manager=None, rotate_ua=True):
    results = []
    try:
        url = f"https://tasty.co/search?q={quote_plus(query)}"
        resp = safe_request(url, proxy_manager, rotate_ua)
        if not resp:
            logger.info(f"Tasty direct scrape failed, using DDG fallback for '{query}'")
            return _ddg_fallback(query)
        soup = BeautifulSoup(resp.text, "html.parser")

        script = soup.select_one("script#__NEXT_DATA__")
        if script and script.string:
            data = json.loads(script.string)
            items = (
                data.get("props", {})
                .get("pageProps", {})
                .get("initialFeed", {})
                .get("items", [])
            )
            for item in items:
                if item.get("type") != "recipe":
                    continue
                name = item.get("name", "")
                slug = item.get("slug", "")
                link = f"https://tasty.co/recipe/{slug}" if slug else ""
                prep_time = ""
                times = item.get("times", {})
                if times.get("total_time", {}).get("display"):
                    prep_time = times["total_time"]["display"]
                if name and link:
                    results.append({
                        "title": name,
                        "source": "Tasty",
                        "url": link,
                        "prep_time": prep_time,
                    })
        if not results:
            for a in soup.select("a[href*='/recipe/']"):
                title = a.get_text(strip=True)
                href = a.get("href", "")
                if title and len(title) > 3 and href:
                    if not href.startswith("http"):
                        href = "https://tasty.co" + href
                    results.append({
                        "title": title,
                        "source": "Tasty",
                        "url": href,
                        "prep_time": "",
                    })

        if not results:
            logger.info(f"Tasty returned 0 results directly, using DDG fallback for '{query}'")
            results = _ddg_fallback(query)

    except Exception as e:
        logger.error(f"Tasty scraper error: {type(e).__name__}: {e}")
        results = _ddg_fallback(query)
    return results[:15]
