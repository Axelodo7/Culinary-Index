from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from .helpers import safe_request


def search_foodfusion(query, proxy_manager=None, rotate_ua=True):
    results = []
    try:
        url = f"https://www.foodfusion.com/?s={quote_plus(query)}"
        resp = safe_request(url, proxy_manager, rotate_ua)
        if not resp:
            return results
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
    except Exception:
        pass
    return results
