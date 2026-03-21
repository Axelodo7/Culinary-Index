import logging
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from .helpers import safe_request

logger = logging.getLogger("scrapers")


def _ddg_fallback(query, domain="foodfusion.com"):
    """Use DuckDuckGo as fallback when direct scraping is blocked."""
    try:
        try:
            from ddgs import DDGS
        except ImportError:
            from duckduckgo_search import DDGS
        results = []
        ddg_results = DDGS().text(f"site:{domain} {query}", max_results=10)
        for r in ddg_results:
            title = r.get("title", "")
            href = r.get("href", "")
            if title and href and len(title) > 3:
                for sep in [" | ", " - ", " by "]:
                    if sep in title:
                        title = title.split(sep)[0]
                title = title.strip()
                if len(title) >= 3:
                    results.append({
                        "title": title,
                        "source": "Food Fusion",
                        "url": href,
                        "prep_time": "",
                    })
        return results
    except Exception as e:
        logger.warning(f"DDG fallback failed for Food Fusion: {e}")
        return []


def search_foodfusion(query, proxy_manager=None, rotate_ua=True):
    results = []
    try:
        url = f"https://www.foodfusion.com/?s={quote_plus(query)}"
        resp = safe_request(url, proxy_manager, rotate_ua)
        if not resp:
            logger.info(f"Food Fusion direct scrape failed, using DDG fallback for '{query}'")
            return _ddg_fallback(query)
        soup = BeautifulSoup(resp.text, "html.parser")

        articles = soup.select("article.uk-article")
        for article in articles:
            title_el = article.select_one("h1.uk-article-title a")
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            link_el = article.select_one("a.uk-button.uk-button-text")
            link = ""
            if link_el and link_el.get("href"):
                href = link_el["href"]
                if href.startswith("/"):
                    link = "https://www.foodfusion.com" + href
                elif href.startswith("http"):
                    link = href
            if not link:
                link = url
            if title:
                results.append({
                    "title": title,
                    "source": "Food Fusion",
                    "url": link,
                    "prep_time": "",
                })

        # If direct scrape returned 0 results, try DDG fallback
        if not results:
            logger.info(f"Food Fusion returned 0 results directly, using DDG fallback for '{query}'")
            results = _ddg_fallback(query)

    except Exception as e:
        logger.error(f"Food Fusion scraper error: {type(e).__name__}: {e}")
        results = _ddg_fallback(query)
    return results
