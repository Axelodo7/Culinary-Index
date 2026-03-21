from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from .helpers import safe_request


def search_superchef(query, proxy_manager=None, rotate_ua=True):
    results = []
    try:
        ajax_url = f"https://www.superchef.pk/searchFeature?searchFeature={quote_plus(query)}"
        resp = safe_request(ajax_url, proxy_manager, rotate_ua)
        if resp and resp.text.strip():
            soup = BeautifulSoup(resp.text, "html.parser")
            items = soup.select("li")
            for item in items:
                a = item.select_one("a")
                if a:
                    title = a.get_text(strip=True)
                    href = a.get("href", "")
                    if title and href:
                        if not href.startswith("http"):
                            href = "https://www.superchef.pk" + href
                        results.append({
                            "title": title,
                            "source": "SuperChef",
                            "url": href,
                            "prep_time": "",
                        })
            if results:
                return results[:15]

        search_url = "https://www.superchef.pk/search"
        try:
            resp = safe_request(
                search_url, proxy_manager, rotate_ua,
                method="post",
                data={"search_word": query},
            )
            if resp:
                soup = BeautifulSoup(resp.text, "html.parser")
                for card in soup.select(".recipe-card, .card, .recipe-item, .col-lg-4, .col-md-6"):
                    a = card.select_one("a")
                    if a:
                        title = ""
                        h = card.select_one("h3, h4, h5, h2")
                        if h:
                            title = h.get_text(strip=True)
                        elif a.get_text(strip=True):
                            title = a.get_text(strip=True)
                        href = a.get("href", "")
                        if title and href and len(title) > 3:
                            if not href.startswith("http"):
                                href = "https://www.superchef.pk" + href
                            results.append({
                                "title": title,
                                "source": "SuperChef",
                                "url": href,
                                "prep_time": "",
                            })
                if results:
                    return results[:15]
        except Exception:
            pass

        try:
            from ddgs import DDGS
        except ImportError:
            from duckduckgo_search import DDGS
        ddg_results = DDGS().text(f"site:superchef.pk {query}", max_results=8)
        for r in ddg_results:
            title = r.get("title", "")
            for sep in [" | ", " - ", " by ", " Recipe by"]:
                if sep in title:
                    title = title.split(sep)[0]
            title = title.replace("Recipe", "").replace("recipe", "").strip()
            title = " ".join(title.split())
            if len(title) < 4:
                continue
            href = r.get("href", "")
            if href.rstrip("/").endswith(("-recipes", "/blog")):
                continue
            results.append({
                "title": title,
                "source": "SuperChef",
                "url": href,
                "prep_time": "",
            })
    except Exception:
        pass
    return results[:15]
