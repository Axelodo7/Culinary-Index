import json
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from .helpers import safe_request


def search_tasty(query, proxy_manager=None, rotate_ua=True):
    results = []
    try:
        url = f"https://tasty.co/search?q={quote_plus(query)}"
        resp = safe_request(url, proxy_manager, rotate_ua)
        if not resp:
            return results
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
    except Exception:
        pass
    return results[:15]
